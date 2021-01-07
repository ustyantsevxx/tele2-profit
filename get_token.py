from colorama import init as colorama_init

from _app.api import Tele2Api
from _app.auth import get_phone_number, get_access_token, save_config
from _app.utils import run_main


async def main():
    colorama_init(autoreset=True)
    phone_number = get_phone_number()
    async with Tele2Api(phone_number) as api:
        access_token = await get_access_token(api, phone_number)
    save_config(phone_number, access_token)


if __name__ == '__main__':
    run_main(main)
