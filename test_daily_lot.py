from fastapi.testclient import TestClient
from datetime import date
from main import app

client = TestClient(app)

def test_daily_lot_features():
    today = date.today().isoformat()

    # 1. Test basic daily lot with no user_id
    r1 = client.get(f'/api/daily_lot?lot_type=60_jiazi&date_str={today}')
    d1 = r1.json()
    assert d1['success'] is True, 'Basic daily lot failed'
    print(f'[PASS] Daily Lot (Default): #{d1["lot_number"]} - {d1["lot"]["lot_name"]}')

    # 2. Test user_id personalization: Multiple users should receive different personalized lots
    users = ['user_101', 'user_102', 'user_103', 'user_104', 'user_105', 'user_106']
    lots_obtained = set()
    for u in users:
        res = client.get(f'/api/daily_lot?lot_type=60_jiazi&date_str={today}&user_id={u}')
        data = res.json()
        assert data['success'] is True
        lots_obtained.add(data['lot_number'])
        print(f'[PASS] {u} -> Lot #{data["lot_number"]} ({data["lot"]["lot_name"]})')
    
    # Across 6 users, we expect multiple distinct lots
    assert len(lots_obtained) > 1, 'Personalization should produce distinct lots across users'
    print(f'[PASS] Personalization test: {len(users)} users generated {len(lots_obtained)} distinct lots.')

    # 3. Test user consistency: Same user on same day gets exact same lot
    r_user_again = client.get(f'/api/daily_lot?lot_type=60_jiazi&date_str={today}&user_id=user_101')
    d_user_again = r_user_again.json()
    assert d_user_again['lot_number'] == client.get(f'/api/daily_lot?lot_type=60_jiazi&date_str={today}&user_id=user_101').json()['lot_number']
    print('[PASS] User consistency verified: repeated requests for user_101 yield exact same lot.')

    # 4. Test redraw_index: redraw increments should yield diverse lots
    redraw_lots = []
    for idx in range(5):
        r = client.get(f'/api/daily_lot?lot_type=60_jiazi&date_str={today}&user_id=user_101&redraw_index={idx}')
        d = r.json()
        assert d['success'] is True
        assert d['redraw_index'] == idx
        redraw_lots.append(d['lot_number'])
        print(f'[PASS] Redraw index {idx} -> Lot #{d["lot_number"]} ({d["lot"]["lot_name"]})')
    
    assert len(set(redraw_lots)) > 1, 'Redrawing should change the lot'

    # 5. Test all 3 systems
    for sys_id in ['60_jiazi', 'guandi_100', 'guanyin_100']:
        r = client.get(f'/api/daily_lot?lot_type={sys_id}&date_str={today}&user_id=user_101')
        data = r.json()
        assert data['success'] is True
        print(f'[PASS] System {sys_id}: Lot #{data["lot_number"]} loaded ({data["lot_type_name"]})')

    print('\n>>> ALL DAILY LOT PERSONALIZATION & REDRAW TESTS PASSED! <<<')

if __name__ == '__main__':
    test_daily_lot_features()
