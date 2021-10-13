""" The applications management toolkit """

from typing import *
import asyncio
from . import project, frontend


COMMANDS = {
    'create': project.create,
    'remove': project.remove,
    'enable': project.enable,
    'disable': project.disable,
    'frontend.create-container': frontend.create_container
}


async def run(params: List[str]) -> None:
    if not params:
        return

    command = params.pop(0)
    if command in COMMANDS:
        func: callable = COMMANDS[command]
        if asyncio.iscoroutinefunction(func):
            await func(params)
        else:
            func(params)
        return

    print(f"Unknown command: `app {command}`")
