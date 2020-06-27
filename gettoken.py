import requests
from json import load, dump

with open('config.json', 'r') as f:
    NUMBER = load(f)['number']

sms_post_url = f'https://tyumen.tele2.ru/api/validation/number/{NUMBER}'
auth_post_url = 'https://my.tele2.ru/auth/realms/tele2-b2c/protocol/openid-connect/token'
requests.post(sms_post_url, json={"sender": "Tele2"})
code = input('sms code: ')
response = requests.post(auth_post_url, {"client_id": "digital-suite-web-app",
                                         "grant_type": "password",
                                         "username": NUMBER,
                                         "password": code,
                                         "password_type": "sms_code"})
TOKEN = response.json()['access_token']

with open('config.json', 'w') as f:
    dump({'number': NUMBER, 'token': TOKEN}, f)
