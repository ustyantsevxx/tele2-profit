import asyncio
import json
import re
from datetime import datetime

import inquirer as console
from colorama import init as colorama_init, Fore
from api import Tele2Api


def input_phone_number():
    while True:
        user_input = input(
            Fore.CYAN +
            f'Input your Tele2 phone number (leave empty to cancel): '
        )
        if re.match(r'^7\d{10}?$', user_input):
            return user_input
        elif user_input == '':
            exit()
        else:
            print(Fore.RED + 'Incorrect number format. Correct - 7xxxxxxxxxx')


def get_phone_number():
    try:
        with open('config.json', 'r') as f:
            phone_number = json.load(f)['number']
        correct = console.confirm(
            f'Old config file found. Your number is {phone_number}, correct?',
            default=True
        )
        if correct:
            return phone_number
    except FileNotFoundError:
        print(Fore.RED + 'Config file not found')
    except json.decoder.JSONDecodeError:
        print(Fore.RED + 'Bad config file')
    phone_number = input_phone_number()
    return phone_number


async def get_access_token(api: Tele2Api, phone_number: str):
    await api.send_sms_code()
    while True:
        try:
            sms_code = input(Fore.LIGHTCYAN_EX + 'SMS code: ')
            access_token = await api.get_access_token(phone_number, sms_code)
            return access_token
        except KeyError:
            print(Fore.RED + 'Invalid SMS-сode. Try again')


def save_config(phone_number: str, access_token: str):
    print(Fore.GREEN + 'Successful auth!')
    with open('config.json', 'w') as f:
        json.dump({
            'number': phone_number,
            'token': access_token,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, f, indent=2)
    print(Fore.YELLOW + 'Token saved to ' + Fore.BLUE + 'config.json')


async def main():
    colorama_init(autoreset=True)
    phone_number = get_phone_number()
    async with Tele2Api(phone_number) as api:
        access_token = await get_access_token(api, phone_number)
    save_config(phone_number, access_token)


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(main())
    event_loop.run_until_complete(future)
