import inquirer as console
from colorama import Fore

from app.account import print_rests
from app.lots import prepare_lots, sell_prepared_lots, print_prepared_lots, \
    prepare_old_lots


async def display_menu(display_again_action: bool):
    choices = [('Prepare new lots to sell', 'new'), 'Exit']
    if display_again_action:
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
