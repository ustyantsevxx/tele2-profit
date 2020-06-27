import requests
from json import dumps

NUMBER = '79044979272'

base_api = f'https://tyumen.tele2.ru/api/subscribers/{NUMBER}'
market_api = f'{base_api}/exchange/lots/created'
rests_api = f'{base_api}/siteTYUMEN/rests'


def read_token():
    try:
        f = open("token.txt", "r")
        tok = f.readline()
        f.close()
        return tok
    except IOError:
        return False


def create_autorized_session():
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {read_token()}'})
    return session


rs = create_autorized_session()


def return_lot(lot_id):
    return rs.delete(f'{market_api}/{lot_id}').json()


def sell_gb(amount, price):
    return rs.put(market_api, json={
        "trafficType": "data",
        "cost": {"amount": price, "currency": "rub"},
        "volume": {"value": amount, "uom": "gb"}
    }).json()


def sell_minutes(amount, price):
    return rs.put(market_api, json={
        "trafficType": "voice",
        "cost": {"amount": price, "currency": "rub"},
        "volume": {"value": amount, "uom": "min"}
    }).json()


def apply_emojes_and_shit(lot_id, lot_price):
    rs.patch(f'{market_api}/{lot_id}', json={
        "cost": {"amount": lot_price, "currency": "rub"},
        'showSellerName': True,
        "emojis": ["bomb", "devil", "scream"]
    })


def return_all():
    lots = list(rs.get(market_api).json()['data'])
    active_lots = [a['id'] for a in lots if a['status'] == 'active']
    for lot in active_lots:
        return_lot(lot)


def sell_all_minutes_by_50():
    rests = list(rs.get(rests_api).json()['data']['rests'])
    minutes_total = sum([a['remain'] for a in rests if a['type'] == 'tariff'
                         and a['uom'] == 'min'])
    for i in range(int(minutes_total // 50)):
        lot = sell_minutes(50, 40)['data']
        apply_emojes_and_shit(lot['id'], lot['cost']['amount'])


return_all()
sell_all_minutes_by_50()
