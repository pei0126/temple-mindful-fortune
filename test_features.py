import json
from fastapi.testclient import TestClient
from datetime import date
from main import app

client = TestClient(app)

def run_tests():
    # 1. Test Static Index HTML: Public header is clean, Admin modal exists, Daily redraw exists
    res = client.get('/')
    html_content = res.text
    assert 'main-tab-daily' in html_content, 'Main Tab Daily missing'
    assert 'main-tab-prayer' in html_content, 'Main Tab Prayer missing'
    assert 'main-tab-library' in html_content, 'Main Tab Library missing'
    assert 'admin-modal' in html_content, 'Admin Modal missing'
    assert 'admin-model-select' in html_content, 'Admin Model Select missing'
    assert 'daily-redraw-btn' in html_content, 'Daily Redraw button missing'
    assert 'global-model-select' not in html_content, 'Public Model Selector should be removed from public header'
    print('[PASS] Static HTML: Public header is clean, Admin Modal and Daily Redraw elements are present.')

    # 2. Test /api/models
    res = client.get('/api/models')
    data = res.json()
    assert data['success'] is True
    assert len(data['models']) >= 3
    print(f'[PASS] Models API: {len(data["models"])} models in catalog, default: {data["current_default"]}.')

    # 3. Test Admin Set Model API: POST /api/admin/set_model
    res = client.post('/api/admin/set_model', json={'model': 'gemini-3.1-flash-lite-preview'})
    set_data = res.json()
    assert set_data['success'] is True
    assert set_data['active_model'] == 'gemini-3.1-flash-lite-preview'
    print(f'[PASS] Admin Set Model API: Successfully updated active model to {set_data["active_model"]}.')

    # 4. Test /api/lots for all systems
    for sys_id, expected_count in [('60_jiazi', 60), ('guandi_100', 100), ('guanyin_100', 100)]:
        res = client.get(f'/api/lots?lot_type={sys_id}')
        data = res.json()
        assert data['success'] is True
        assert len(data['lots']) == expected_count
        print(f'[PASS] Lots list API: {sys_id} returns {len(data["lots"])} lots.')

    # 5. Test Personalized Daily Lot & Redraw
    today = date.today().isoformat()
    users = ['user_alpha', 'user_beta', 'user_gamma', 'user_delta', 'user_epsilon']
    assigned_lots = set()
    for u in users:
        r = client.get(f'/api/daily_lot?lot_type=60_jiazi&date_str={today}&user_id={u}')
        d = r.json()
        assert d['success'] is True
        assigned_lots.add(d['lot_number'])
    assert len(assigned_lots) > 1, 'Personalized seeds should distribute lots'
    print(f'[PASS] Daily Lot Personalization: {len(users)} users generated {len(assigned_lots)} distinct lots.')

    # Test redraw
    r0 = client.get(f'/api/daily_lot?lot_type=60_jiazi&date_str={today}&user_id=user_alpha&redraw_index=0').json()
    r1 = client.get(f'/api/daily_lot?lot_type=60_jiazi&date_str={today}&user_id=user_alpha&redraw_index=1').json()
    assert r0['lot_number'] != r1['lot_number'], 'Redraw should yield new lot'
    print(f'[PASS] Daily Lot Redraw: initial #{r0["lot_number"]} -> redraw #{r1["lot_number"]}.')

    print('\n[SUCCESS] All Comprehensive test suites passed!')

if __name__ == '__main__':
    run_tests()
