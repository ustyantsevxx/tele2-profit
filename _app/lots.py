import math
import re

from colorama import Fore

from _app.api import Tele2Api


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
        lots_to_sell += input_lots(data_left=rests['voice'],
                                   display_name='minute',
                                   min_amount=50,
                                   max_multiplier=2,
                                   price_multiplier=0.8,
                                   lot_type='voice'
                                   )
    if rests['data'] >= 1:
        print(Fore.GREEN + '2. Prepare gigabyte lots:')
        lots_to_sell += input_lots(data_left=rests['data'],
                                   display_name='gigabyte',
                                   min_amount=1,
                                   max_multiplier=50,
                                   price_multiplier=15,
                                   lot_type='data'
                                   )
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


def print_lot_listing_status(lot: any):
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
    for lot in lots:
        state = await api.sell_lot(lot)
        print_lot_listing_status(state)
