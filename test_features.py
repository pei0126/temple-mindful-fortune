import sys
import json
from fastapi.testclient import TestClient
from datetime import date
from main import app, init_sqlite_db

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure SQLite is initialized
init_sqlite_db()

client = TestClient(app)

def run_tests():
    # 1. Test Static Index HTML: 4 Tabs, 3D Moon Blocks, Language Dropdown, Admin Modal
    res = client.get('/')
    html_content = res.text
    assert 'main-tab-daily' in html_content, 'Main Tab Daily missing'
    assert 'main-tab-prayer' in html_content, 'Main Tab Prayer missing'
    assert 'main-tab-toss' in html_content, 'Main Tab 3D Toss missing'
    assert 'main-tab-library' in html_content, 'Main Tab Library missing'
    assert 'lang-dropdown' in html_content, 'Language Dropdown missing'
    assert 'standalone-block-left' in html_content, '3D Moon Blocks elements missing'
    assert 'admin-modal' in html_content, 'Admin Modal missing'
    print('[PASS] Static HTML: 4 Main Tabs, 3D Moon Blocks, Language Switcher, and Admin Modal are present.')

    # 2. Test /api/models
    res = client.get('/api/models')
    data = res.json()
    assert data['success'] is True
    assert len(data['models']) >= 3
    print(f'[PASS] Models API: {len(data["models"])} models in catalog, default: {data["current_default"]}.')

    # 3. Test Admin Authentication & Protected Set Model API
    res_unauth = client.post('/api/admin/set_model', json={'model': 'gemini-3.1-flash-lite-preview'})
    assert res_unauth.status_code == 401, 'Unauthorized request should be blocked with 401'
    
    res_verify_fail = client.post('/api/admin/verify', json={'password': 'wrong_password_123'})
    assert res_verify_fail.status_code == 401, 'Wrong password must fail'

    res_verify_ok = client.post('/api/admin/verify', json={'password': 'temple888'})
    assert res_verify_ok.status_code == 200, 'Correct password must succeed'

    res = client.post('/api/admin/set_model', json={'model': 'gemini-3.1-flash-lite-preview', 'password': 'temple888'})
    set_data = res.json()
    assert res.status_code == 200
    assert set_data['success'] is True
    assert set_data['active_model'] == 'gemini-3.1-flash-lite-preview'
    print(f'[PASS] Admin Security: Protected endpoint verified.')

    # 4. Test /api/lots for all systems
    for sys_id, expected_count in [('60_jiazi', 60), ('guandi_100', 100), ('guanyin_100', 100)]:
        res = client.get(f'/api/lots?lot_type={sys_id}')
        data = res.json()
        assert data['success'] is True
        assert len(data['lots']) == expected_count
        print(f'[PASS] Lots list API: {sys_id} returns {len(data["lots"])} lots.')

    # 5. Test Daily Lot 1-per-day IP & Device Lock
    test_device = 'dev_test_unique_9988'
    today = date.today().isoformat()
    
    # First call: Initial draw for today
    r1 = client.get(f'/api/daily_lot?lot_type=60_jiazi&date_str={today}&device_id={test_device}&language=zh-TW').json()
    assert r1['success'] is True
    assert r1['is_locked'] is True
    drawn_lot_num = r1['lot_number']

    # Second call with same device: Should return EXACT SAME lot and mark already_drawn_today = True
    r2 = client.get(f'/api/daily_lot?lot_type=60_jiazi&date_str={today}&device_id={test_device}&language=zh-TW').json()
    assert r2['success'] is True
    assert r2['already_drawn_today'] is True
    assert r2['lot_number'] == drawn_lot_num, 'Same device/IP must return the locked lot on subsequent draws'
    print(f'[PASS] Daily Lot Rate Limiting: Device {test_device} correctly locked to lot #{drawn_lot_num} for today.')

    # 6. Test Multi-Language Fallback & AI Interpretation across 4 Languages
    languages = ['zh-TW', 'en', 'ja', 'ko']
    for lang in languages:
        payload = {
            'lot_type': '60_jiazi',
            'lot_number': 1,
            'user_question': 'Is it a good time for a career transition or investment?',
            'language': lang
        }
        res = client.post('/api/interpret', json=payload)
        assert res.status_code == 200, f'Interpret failed for language {lang}'
        d = res.json()
        assert d['success'] is True
        assert 'analysis' in d
        assert 'direct_verdict' in d['analysis']
        assert len(d['analysis']['actions']['dos']) > 0
        assert len(d['analysis']['actions']['donts']) > 0
        assert len(d['analysis']['encouragement']) > 0
        print(f'[PASS] Multi-Language AI Interpretation ({lang}): Verdict received -> {d["analysis"]["direct_verdict"][:35]}...')

    print('\n[SUCCESS] All Comprehensive test suites passed successfully!')

if __name__ == '__main__':
    run_tests()
