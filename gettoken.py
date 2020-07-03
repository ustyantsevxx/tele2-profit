import asyncio
from aiohttp import ClientSession
from json import load, dump


async def main():
    with open('config.json', 'r') as f:
        number = load(f)['number']

    sms_post_url = f'https://tyumen.tele2.ru/api/validation/number/{number}'
    auth_post_url = 'https://my.tele2.ru/auth/realms/tele2-b2c/protocol/openid-connect/token'

    async with ClientSession() as sess:
        print('sending SMS...')
        await sess.post(sms_post_url, json={"sender": "Tele2"})
        code = input('SMS code: ')
        print('recieving token...')
        response = await sess.post(auth_post_url,
                                   data={"client_id": "digital-suite-web-app",
                                         "grant_type": "password",
                                         "username": number,
                                         "password": code,
                                         "password_type": "sms_code"})
        token = (await response.json())['access_token']
        print('token recieved')

    with open('config.json', 'w') as f:
        dump({'number': number, 'token': token}, f)
    print('token saved to config.json')


future = asyncio.ensure_future(main())
asyncio.get_event_loop().run_until_complete(future)

print('Script terminated.')
