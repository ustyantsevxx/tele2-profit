from colorama import Fore

from _app.api import Tele2Api


async def print_balance(api):
    balance = await api.get_balance()
    print(Fore.YELLOW + 'Balance: ' + Fore.MAGENTA + f'{balance} rub.')


async def print_rests(api: Tele2Api):
    print('Checking your rests...')
    print(
        Fore.CYAN + 'note: only plan (not market-bought ones nor transferred)'
                    ' rests can be sold')
    rests = await api.get_rests()
    print(Fore.WHITE + 'You have')
    print(Fore.YELLOW + f'\t{rests["voice"]} min')
    print(Fore.GREEN + f'\t{rests["data"]} gb')
    print(Fore.WHITE + '\t\tavailable to sell.')
    return rests
