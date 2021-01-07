import asyncio
import json
from datetime import datetime, timedelta

from colorama import Fore

from _app.api import Tele2Api


def load_config():
    with open('config.json', 'r') as f:
        obj = json.load(f)
        phone_number = obj['number']
        access_token = obj['token']
        date = obj['date']
    return access_token, date, phone_number


async def check_auth(api: Tele2Api):
    code = await api.check_auth_code()
    if code == 401:
        print(Fore.RED +
              'Token invalid or expired. Get new with '
              + Fore.YELLOW + 'get_token.py')
        exit()
    elif code != 200:
        print(Fore.RED +
              'Tele2 server unavailable. Try running script again later.')
        exit()


def print_token_time(date):
    fmt = '%Y-%m-%d %H:%M:%S'
    d = datetime.strptime(date, fmt) + timedelta(hours=4)
    now = datetime.strptime(datetime.now().strftime(fmt), fmt)
    minutes_left = int((d - now).seconds / 60)
    print(Fore.GREEN + 'Successful auth! '
          + f'Your token expires in {minutes_left} min.')


async def delete_active_lots(api: Tele2Api):
    tasks = []
    print(Fore.WHITE + 'Checking active lots...')
    active_lots = await api.get_active_lots()
    count = len(active_lots)
    if count:
        print(Fore.MAGENTA +
              f'You have {count} active lot{"s" if count > 1 else ""}:')
        for lot in active_lots:
            color = Fore.YELLOW if lot['trafficType'] == 'voice' else Fore.GREEN
            print(color +
                  f'\t{lot["volume"]["value"]} {lot["volume"]["uom"]} '
                  f'for {int(lot["cost"]["amount"])} rub')
        for lot in active_lots:
            task = asyncio.ensure_future(api.return_lot(lot['id']))
            tasks.append(task)
        await asyncio.gather(*tasks)
        print(Fore.GREEN + 'All active lots have been deleted!')
    else:
        print(Fore.MAGENTA + 'You don\'t have any active lots.')
    return active_lots
