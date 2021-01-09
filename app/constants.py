SECURITY_BYPASS_HEADERS = {
    'Connection': 'keep-alive',
    'Tele2-User-Agent': '"mytele2-app/3.17.0"; "unknown"; "Android/9"; "Build/12998710"',
    'X-API-Version': '1',
    'User-Agent': 'okhttp/4.2.0'
}

MAIN_API = 'https://my.tele2.ru/api/subscribers/'
SMS_VALIDATION_API = 'https://my.tele2.ru/api/validation/number/'
TOKEN_API = 'https://my.tele2.ru/auth/realms/tele2-b2c/protocol/openid-connect/token/'
