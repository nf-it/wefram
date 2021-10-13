from typing import *
from .. import aaa


def print_help() -> None:
    pass


async def run(params: List[str]) -> None:
    if not params:
        print_help()
        return

    command: str = params.pop(00)

    if command == 'logoff':
        if not params:
            print("Syntax error: expected `manage aaa logoff <login> [login] [...]`")
            return
        [(await aaa.drop_user_sessions_by_login(login)) for login in params]
        return

    print(f"Unsupported command for [aaa]: {command}")
