import asyncio
import json
import math
import re
import time
from datetime import datetime, timedelta

import inquirer as console
from colorama import init as colorama_init, Fore

from api import Tele2Api
from utils import run_main


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
              'Token invalid or expired. Get new with ' + Fore.YELLOW + 'auth.py')
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


async def print_rests(api: Tele2Api):
    print('Checking your rests...')
    print(Fore.CYAN + 'note: only plan (not market-bought ones nor transferred)'
                      ' rests can be sold')
    rests = await api.get_rests()
    print(Fore.WHITE + 'You have')
    print(Fore.YELLOW + f'\t{rests["voice"]} min')
    print(Fore.GREEN + f'\t{rests["data"]} gb')
    print(Fore.WHITE + '\t\tavailable to sell.')
    return rests


def input_lots(data_left, display_name, min_amount, max_multiplier,
               price_multiplier, lot_type):
    lots_to_sell = []
    index = 1
    while data_left >= min_amount:
        user_input = input(Fore.WHITE + f'\t{display_name}s lot {index} >>> ')

        if user_input == '':
            break

        if not re.match(r'^\s*\d+\s*(\s\d+\s*)?$', user_input):
            print(Fore.MAGENTA + '\tIncorrect input format. Try again')
            continue

        clean = re.sub(r'\s+', ' ', user_input.strip())
        lot_data = list(map(int, clean.split(' ')))

        amount = lot_data[0]
        if amount < min_amount:
            print(Fore.RED +
                  f'\tOops: {display_name.capitalize()} lot amount must be '
                  f'> {min_amount}')
            continue
        elif amount > data_left:
            print(Fore.RED + f'\tOops: You only have {data_left} left')
            continue

        if len(lot_data) == 1:
            price = math.ceil(amount * price_multiplier)
        else:
            price = lot_data[1]
            if price < math.ceil(amount * price_multiplier):
                print(Fore.RED +
                      f'\tOops: {display_name.capitalize()} lot price must be >='
                      f' ({price_multiplier} * amount)')
                continue
            elif price > max_multiplier * amount:
                print(Fore.RED +
                      f'\tOops: {display_name.capitalize()} lot price must be <='
                      f' ({max_multiplier} * amount)')
                continue

        print(Fore.GREEN +
              f'\t\tOk! Lot {index}: {amount} {display_name[:3]}.'
              f' for {price} rub.')
        data_left -= amount
        print(f'\t\t({data_left} {display_name[:3]}. left)')
        lots_to_sell.append({
            'name': display_name[:3],
            'lot_type': lot_type,
            'amount': amount,
            'price': price,
        })

        index += 1
    return lots_to_sell


async def prepare_lots(rests):
    lots_to_sell = []
    if rests['voice'] >= 50:
        print(Fore.YELLOW + '1. Prepare minute lots:')
        lots_to_sell += input_lots(rests['voice'], 'minute', 50, 2, 0.8,
                                   'voice')
    if rests['data'] >= 1:
        print(Fore.GREEN + '2. Prepare gigabyte lots:')
        lots_to_sell += input_lots(rests['data'], 'gigabyte', 1, 50, 15,
                                   'data')
    return lots_to_sell


def print_prepared_lots(prepared_lots):
    count = len(prepared_lots)
    if count:
        print(Fore.LIGHTMAGENTA_EX +
              f'Ok. You have prepared {count} lot{"s" if count > 1 else ""}:')
        for lot in prepared_lots:
            color = Fore.YELLOW if lot['lot_type'] == 'voice' else Fore.GREEN
            print(color + f'\t{lot["amount"]} {lot["name"]} '
                          f'for {lot["price"]} rub')


def prepare_old_lots(old_lots: list):
    lots = []
    for lot in old_lots:
        lots.append({
            'lot_type': lot['trafficType'],
            'amount': lot['volume']['value'],
            'price': lot['cost']['amount'],
        })
    return lots


def print_lot_listing_status(lots: any):
    for lot in lots:
        lot_status = lot['meta']['status']
        if lot_status == 'OK':
            color = Fore.YELLOW if lot['data']['trafficType'] == 'voice' \
                else Fore.GREEN
            amount = lot['data']['volume']['value']
            uom = lot['data']['volume']['uom']
            cost = lot['data']['cost']['amount']
            print(color +
                  f'Successful listing {amount} {uom} for {cost} rub.')
        else:
            print(Fore.RED +
                  f'Error during listing: {lot_status}')


async def sell_prepared_lots(api: Tele2Api, lots: list):
    tasks = []
    for lot in lots:
        task = asyncio.ensure_future(api.sell_lot(lot))
        tasks.append(task)
    print(Fore.WHITE + 'Listing...')
    lots = await asyncio.gather(*tasks)
    print_lot_listing_status(lots)


async def display_menu(have_lots_returned: bool):
    choices = [('Prepare new lots to sell', 'new'), 'Exit']
    if have_lots_returned:
        choices.insert(0, ('Try selling returned lots again', 'again'))
    return console.list_input('Action', choices=choices)


async def menu_new_action(api):
    rests = await print_rests(api)
    prepared_lots = await prepare_lots(rests)
    print(Fore.MAGENTA + '-----')
    if len(prepared_lots):
        print_prepared_lots(prepared_lots)
        if console.confirm('Sell prepared lots?', default=True):
            await sell_prepared_lots(api, prepared_lots)
    else:
        print(Fore.YELLOW + 'You did not prepared any lots.')


async def menu_again_action(api, deleted_lots):
    lots = prepare_old_lots(deleted_lots)
    await sell_prepared_lots(api, lots)


async def print_balance(api):
    balance = await api.get_balance()
    print(Fore.YELLOW + 'Balance: ' + Fore.MAGENTA + f'{balance} rub.')


def input_auto_resell_interval():
    while True:
        user_input = input(
            Fore.MAGENTA + 'Auto-resell interval (seconds): ')
        try:
            interval = int(user_input)
            return interval
        except ValueError:
            print(Fore.RED + 'Interval value must be integer!')
            continue


async def activate_timer_if_needed(api: Tele2Api):
    if console.confirm('Activate lot auto-selling timer?', default=True):
        interval = input_auto_resell_interval()
        print(Fore.GREEN + f'Timer activated! Your lots will be relisted every '
                           f'{interval} sec.')
        iteration = 1
        while True:
            time.sleep(interval)
            print(Fore.CYAN + f'\nRelisting (iteration #{iteration})...\n')
            deleted_lots = await delete_active_lots(api)
            if not len(deleted_lots):
                print(Fore.GREEN +
                      'All lots have been sold! Deactivating the timer...')
                break
            await menu_again_action(api, deleted_lots)


async def main():
    access_token, date, phone_number = load_config()
    async with Tele2Api(phone_number, access_token) as api:
        # script initialization:

        colorama_init(False)

        # logic pipeline:

        await check_auth(api)
        print_token_time(date)
        await print_balance(api)
        deleted_lots = await delete_active_lots(api)

        print(Fore.MAGENTA + '-----')

        option = await display_menu(have_lots_returned=len(deleted_lots) > 0)

        if option == 'new':
            await menu_new_action(api)
        elif option == 'again':
            await menu_again_action(api, deleted_lots)
        elif option == 'Exit':
            pass

        await activate_timer_if_needed(api)


if __name__ == '__main__':
    run_main(main)
