import asyncio
import os

from colorama import Fore


def _print_version():
    print('tele2-profit v1.3.0')


def run_main(main):
    try:
        _print_version()
        event_loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(main())
        event_loop.run_until_complete(future)
        print(Fore.WHITE + 'Script done.')
        if 'system' in dir(os):
            os.system('pause')
    except KeyboardInterrupt:
        pass
