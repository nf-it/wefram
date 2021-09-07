from argparse import Namespace
from system import aaa


async def runcmd(command: str, args: Namespace) -> None:
    if command == 'logoff':
        login: str = args.login
        if not login:
            print("Syntax: aaa.logoff --login=<the_user_login>")
            exit(2)
        await aaa.drop_user_sessions_by_login(login)
        print("OK")
        exit(0)

    print(f"Unknown AAA command: {command}")
    exit(1)
