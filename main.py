from colorama import init as colorama_init, Fore

from _app.account import print_balance
from _app.api import Tele2Api
from _app.utils import run_main
from _app.menu import display_menu, menu_new_action, menu_again_action
from _app.startup import load_config, check_auth, print_token_time, \
    delete_active_lots
from _app.timer import activate_timer_if_needed


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
