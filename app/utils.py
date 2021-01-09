import asyncio
import os
from _version import __version__


def _print_version():
    print(f'tele2-profit v{__version__} by archie')


def run_main(main):
    try:
        _print_version()
        event_loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(main())
        event_loop.run_until_complete(future)
        if 'system' in dir(os):
            os.system('pause')
    except KeyboardInterrupt:
        pass
