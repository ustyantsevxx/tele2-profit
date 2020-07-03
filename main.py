import asyncio
from aiohttp import ClientSession
from json import load, dumps


with open('config.json', 'r') as f:
    obj = load(f)
    NUMBER, TOKEN = obj['number'], obj['token']

base_api = f'https://tyumen.tele2.ru/api/subscribers/{NUMBER}'
market_api = f'{base_api}/exchange/lots/created'
rests_api = f'{base_api}/siteTYUMEN/rests'


async def return_lot(sess, lot_id):
    print(f'deleting {lot_id}...')
    await sess.delete(f'{market_api}/{lot_id}')
    print(f'{lot_id} deleted')


async def sell_minutes(sess, amount, price):
    print(f'listing {amount} for {price} rub...')
    resp = await sess.put(market_api, json={
        "trafficType": "voice",
        "cost": {"amount": price, "currency": "rub"},
        "volume": {"value": amount, "uom": "min"}
    })
    print('listed')
    lot_id = (await resp.json())['data']['id']
    print(f'patching {lot_id}...')
    resp = await sess.patch(f'{market_api}/{lot_id}', json={
        "cost": {"amount": price, "currency": "rub"},
        'showSellerName': True,
        "emojis": ["bomb", "devil", "scream"]
    })
    print(f'{lot_id} PATCHED!')
    return await resp.json()


async def main():
    tasks = []
    headers = {'Authorization': f'Bearer {TOKEN}'}

    async with ClientSession(headers=headers) as ses:
        async with ses.get(market_api) as resp:
            lots = list((await resp.json())['data'])
        active_lots = [a['id'] for a in lots if a['status'] == 'active']

        for lot_id in active_lots:
            task = asyncio.ensure_future(return_lot(ses, lot_id))
            tasks.append(task)
        await asyncio.gather(*tasks)

        tasks = []

        async with ses.get(rests_api) as resp:
            rests = list((await resp.json())['data']['rests'])
        minutes_total = sum([a['remain'] for a in rests if a['type'] == 'tariff'
                             and a['uom'] == 'min'])

        for i in range(int(minutes_total // 50)):
            task = asyncio.ensure_future(sell_minutes(ses, 50, 40))
            tasks.append(task)
        resp = await asyncio.gather(*tasks)
        print(dumps(resp, indent=2))


future = asyncio.ensure_future(main())
asyncio.get_event_loop().run_until_complete(future)
print('Script terminated.')
