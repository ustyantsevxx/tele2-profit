from aiohttp import ClientSession


class Tele2Api:
    session: ClientSession
    access_token: str

    def __init__(self, phone_number: str, access_token: str = ''):
        base_api = f'https://my.tele2.ru/api/subscribers/{phone_number}'
        self.market_api = f'{base_api}/exchange/lots/created'
        self.rests_api = f'{base_api}/rests'
        self.profile_api = f'{base_api}/profile'
        self.balance_api = f'{base_api}/balance'
        self.sms_post_url = f'https://my.tele2.ru/api/validation/number/{phone_number}'
        self.auth_post_url = 'https://my.tele2.ru/auth/realms/tele2-b2c/protocol/openid-connect/token'
        self.access_token = access_token

    async def __aenter__(self):
        self.session = ClientSession(headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def send_sms_code(self):
        await self.session.post(self.sms_post_url, json={'sender': 'Tele2'})

    async def get_access_token(self, phone_number: str, sms_code: str):
        response = await self.session.post(self.auth_post_url, data={
            'client_id': 'digital-suite-web-app',
            'grant_type': 'password',
            'username': phone_number,
            'password': sms_code,
            'password_type': 'sms_code'
        })
        return (await response.json())['access_token']

    async def check_auth_code(self):
        response = await self.session.get(self.profile_api)
        return response.status

    async def get_balance(self):
        response = await self.session.get(self.balance_api)
        return (await response.json())['data']['value']

    async def sell_lot(self, lot):
        response = await self.session.put(self.market_api, json={
            'trafficType': lot['lot_type'],
            'cost': {'amount': lot['price'], 'currency': 'rub'},
            'volume': {'value': lot['amount'],
                       'uom': 'min' if lot['lot_type'] == 'voice' else 'gb'}
        })
        return await response.json()

    async def return_lot(self, lot_id):
        response = await self.session.delete(f'{self.market_api}/{lot_id}')
        return await response.json()

    async def get_active_lots(self):
        response = await self.session.get(self.market_api)
        lots = list((await response.json())['data'])
        active_lots = [a for a in lots if a['status'] == 'active']
        return active_lots

    async def get_rests(self):
        response = await self.session.get(self.rests_api)
        rests = list((await response.json())['data']['rests'])
        sellable = [a for a in rests if a['type'] == 'tariff']
        return {
            'data': int(
                sum(a['remain'] for a in sellable if a['uom'] == 'mb') / 1024),
            'voice': int(
                sum(a['remain'] for a in sellable if a['uom'] == 'min'))
        }
