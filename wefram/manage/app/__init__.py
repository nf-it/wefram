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


def print_help() -> None:
    print("Supported [app] project-level commands are:")
    print("")
    print("  create <app_name>")
    print("      Creates the new application in the project")
    print("  remove <app_name> [app_name] [...]")
    print("      Removes the specified application(s) from the project")
    print("  enable <app_name> [app_name] [...]")
    print("      Enables the specified application(s) with adding to the `apps.json`")
    print("  disable <app_name> [app_name] [...]")
    print("      Disabled the specified application(S) with removing from the `apps.json`")
    print("")
    print("Supported [app] frontend-level commands are:")
    print("")
    print("  frontend.create-container <app_name> <container_name>")
    print("      Creates a new container from the selected template type")
    print("")


async def run(params: List[str]) -> None:
    if not params:
        print_help()
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
