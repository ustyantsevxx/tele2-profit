from aiohttp import ClientSession, ContentTypeError, ClientResponse

from app.constants import SECURITY_BYPASS_HEADERS, MAIN_API, SMS_VALIDATION_API, \
    TOKEN_API


async def _try_parse_to_json(response: ClientResponse):
    try:
        response_json = await response.json()
        return response_json
    except ContentTypeError:
        return None


def _is_ok(response: ClientResponse):
    return response.status == 200


class Tele2Api:
    session: ClientSession
    access_token: str

    def __init__(self, phone_number: str, access_token: str = '',
                 refresh_token: str = ''):
        base_api = MAIN_API + phone_number
        self.market_api = f'{base_api}/exchange/lots/created'
        self.rests_api = f'{base_api}/rests'
        self.profile_api = f'{base_api}/profile'
        self.balance_api = f'{base_api}/balance'
        self.sms_post_url = SMS_VALIDATION_API + phone_number
        self.auth_post_url = TOKEN_API
        self.access_token = access_token
        self.refresh_token = refresh_token

    async def __aenter__(self):
        self.session = ClientSession(headers={
            'Authorization': f'Bearer {self.access_token}',
            **SECURITY_BYPASS_HEADERS
        })
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def check_if_authorized(self):
        response = await self.session.get(self.profile_api)
        return _is_ok(response)

    async def send_sms_code(self):
        await self.session.post(self.sms_post_url, json={'sender': 'Tele2'})

    async def auth_with_code(self, phone_number: str, sms_code: str):
        response = await self.session.post(self.auth_post_url, data={
            'client_id': 'digital-suite-web-app',
            'grant_type': 'password',
            'username': phone_number,
            'password': sms_code,
            'password_type': 'sms_code'
        })
        if _is_ok(response):
            response_json = await _try_parse_to_json(response)
            return response_json['access_token'], response_json['refresh_token']

    async def refresh_tokens(self, refresh_token: str):
        response = await self.session.post(self.auth_post_url, data={
            'client_id': 'digital-suite-web-app',
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        })
        if _is_ok(response):
            response_json = await _try_parse_to_json(response)
            return response_json['access_token'], response_json['refresh_token']

    async def get_balance(self):
        response = await self.session.get(self.balance_api)
        if _is_ok(response):
            response_json = await _try_parse_to_json(response)
            return response_json['data']['value']

    async def sell_lot(self, lot):
        response = await self.session.put(self.market_api, json={
            'trafficType': lot['lot_type'],
            'cost': {'amount': lot['price'], 'currency': 'rub'},
            'volume': {'value': lot['amount'],
                       'uom': 'min' if lot['lot_type'] == 'voice' else 'gb'}
        })

        return await _try_parse_to_json(response)

    async def return_lot(self, lot_id):
        response = await self.session.delete(f'{self.market_api}/{lot_id}')
        return await _try_parse_to_json(response)

    async def get_active_lots(self):
        response = await self.session.get(self.market_api)
        if _is_ok(response):
            response_json = await _try_parse_to_json(response)
            lots = list(response_json['data'])
            active_lots = [a for a in lots if a['status'] == 'active']
            return active_lots

    async def get_rests(self):
        response = await self.session.get(self.rests_api)
        response_json = await _try_parse_to_json(response)
        rests = list(response_json['data']['rests'])
        sellable = [a for a in rests if a['type'] == 'tariff']
        return {
            'data': int(
                sum(a['remain'] for a in sellable if a['uom'] == 'mb') / 1024),
            'voice': int(
                sum(a['remain'] for a in sellable if a['uom'] == 'min'))
        }
