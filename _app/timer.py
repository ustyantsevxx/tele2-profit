import time

import inquirer as console
from colorama import Fore

from _app.account import print_balance
from _app.api import Tele2Api
from _app.menu import menu_again_action
from _app.startup import delete_active_lots


def input_auto_resell_interval():
    while True:
        print(Fore.CYAN + 'Tip: As Tele2 API may lag - it is recommended ' +
              'to set interval value to at least 3 seconds.')
        user_input = input(
            Fore.MAGENTA + 'Auto-resell interval (seconds): ')
        try:
            interval = int(user_input)
            return interval
        except ValueError:
            print(Fore.RED + 'Interval value must be integer!')
            continue


async def activate_timer_if_needed(api: Tele2Api):
    if console.confirm('Activate lot auto-selling timer?'):
        interval = input_auto_resell_interval()
        print(Fore.GREEN + f'Timer activated! Your lots will be relisted every '
                           f'{interval} sec.')
        iteration = 1
        while True:
            print(Fore.WHITE + f'\nSleeping for {interval} sec...')
            time.sleep(interval)
            print(Fore.CYAN + f'Relisting (iteration #{iteration})...\n')
            deleted_lots = await delete_active_lots(api)
            if not len(deleted_lots):
                print(Fore.GREEN +
                      'All lots have been sold! Deactivating the timer...')
                await print_balance(api)
                break
            await menu_again_action(api, deleted_lots)
            iteration += 1