import asyncio
import json

from colorama import Fore

from app.api import Tele2Api


def try_load_config():
    try:
        with open('config.json', 'r') as f:
            obj = json.load(f)
            phone_number = obj['x-p']
            access_token = obj['x-at']
            refresh_token = obj['x-rt']
        return phone_number, access_token, refresh_token
    except FileNotFoundError or KeyError or json.decoder.JSONDecodeError:
        return False


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
