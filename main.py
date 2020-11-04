import asyncio
import json
import math
import re
from datetime import datetime, timedelta

import inquirer as console
from colorama import init as colorama_init, Fore
from api import Tele2Api


def print_version():
    print('tele2-profit v1.2.0')


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
              'Token invalid or expired. Get new with ' + Fore.BLUE + 'auth.py')
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
    print('Checking active lots...')
    active_lots = await api.get_active_lots()
    count = len(active_lots)
    if count:
        print(Fore.MAGENTA +
              f'You have {count} active lot{"s" if count > 1 else ""}:')
        for lot in active_lots:
            color = Fore.BLUE if lot['trafficType'] == 'voice' else Fore.GREEN
            print(color +
                  f'\t{lot["volume"]["value"]} {lot["volume"]["uom"]} '
                  f'for {int(lot["cost"]["amount"])} rub')
        for lot in active_lots:
            task = asyncio.ensure_future(api.return_lot(lot['id']))
            tasks.append(task)
        await asyncio.gather(*tasks)
        print('All active lots have been deleted!')
    else:
        print(Fore.MAGENTA + 'You don\'t have any active lots.')
    return active_lots


async def print_rests(api: Tele2Api):
    print('Checking your rests...')
    print(Fore.CYAN + 'note: only plan (not market-bought ones nor transferred)'
                      ' rests can be sold')
    rests = await api.get_rests()
    print('You have')
    print(Fore.BLUE + f'\t{rests["voice"]} min')
    print(Fore.GREEN + f'\t{rests["data"]} gb')
    print('\t\tavailable to sell.')
    return rests


def input_lots(data_left, display_name, min_amount, max_multiplier,
               price_multiplier, lot_type):
    lots_to_sell = []
    index = 1

    while data_left >= min_amount:
        user_input = input(f'\t{display_name}s lot {index} >>> ')

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
                  f'\tErr: {display_name.capitalize()} lot amount must be '
                  f'> {min_amount}')
            continue
        elif amount > data_left:
            print(Fore.RED + f'\tErr: You only have {data_left} left')
            continue

        if len(lot_data) == 1:
            price = math.ceil(amount * price_multiplier)
        else:
            price = lot_data[1]
            if price < math.ceil(amount * price_multiplier):
                print(Fore.RED +
                      f'\tErr: {display_name.capitalize()} lot price must be >='
                      f' ({price_multiplier} * amount)')
                continue
            elif price > max_multiplier * amount:
                print(Fore.RED +
                      f'\tErr: {display_name.capitalize()} lot price must be <='
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
        print(Fore.BLUE + '1. Prepare minute lots:')
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
            color = Fore.BLUE if lot['lot_type'] == 'voice' else Fore.GREEN
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


def print_lot_listing_status(lots: list):
    for lot in lots:
        if lot['meta']['status'] == 'OK':
            amount = lot['data']['volume']['value']
            uom = lot['data']['volume']['uom']
            cost = lot['data']['cost']['amount']
            print(Fore.GREEN + f'Successful listing {amount} {uom} for {cost} rub.')
        else:
            print(Fore.RED + 'Error during listing. Try again')


async def sell_prepared_lots(api: Tele2Api, lots: list):
    tasks = []
    for lot in lots:
        task = asyncio.ensure_future(api.sell_lot(lot))
        tasks.append(task)
    print('Listing...')
    lots = await asyncio.gather(*tasks)
    print_lot_listing_status(lots)
    if any(lot['meta']['status'] == 'bp_err_limDay' for lot in lots):
        print(Fore.MAGENTA +
              'Day listing limit (100) reached. Try again tomorrow.')
    else:
        print(Fore.BLUE + 'Lots have been listed to sell.')


async def display_menu(have_lots_returned: bool):
    choices = [('Prepare new lots to sell', 'new'), 'Exit']
    if have_lots_returned:
        choices.insert(0, ('Try selling returned lots again', 'again'))
    return console.list_input('Action', choices=choices)


async def menu_new_action(api):
    rests = await print_rests(api)
    prepared_lots = await prepare_lots(rests)
    print(Fore.YELLOW + '-----')
    if len(prepared_lots):
        print_prepared_lots(prepared_lots)
        if console.confirm('Sell prepared lots?', default=True):
            await sell_prepared_lots(api, prepared_lots)
    else:
        print(Fore.BLUE + 'You did not prepared any lots.')


async def menu_again_action(api, deleted_lots):
    lots = prepare_old_lots(deleted_lots)
    await sell_prepared_lots(api, lots)


async def print_balance(api):
    balance = await api.get_balance()
    print(Fore.BLUE + f'Balance: {balance} rub.')


def init_script():
    colorama_init(False)
    print_version()


async def main():
    access_token, date, phone_number = load_config()
    async with Tele2Api(phone_number, access_token) as api:
        # script initialization  
        
        init_script() 
        
        # logic pipeline:
        
        await check_auth(api)
        print_token_time(date)
        await print_balance(api)
        deleted_lots = await delete_active_lots(api)
        print(Fore.YELLOW + '-----')
        option = await display_menu(len(deleted_lots) > 0)
        if option == 'new':
            await menu_new_action(api)
        elif option == 'again':
            await menu_again_action(api, deleted_lots)
        elif option == 'Exit':
            exit()


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(main())
    event_loop.run_until_complete(future)
    print(Fore.WHITE + 'Complete.')
