import subprocess
from ... import config


def run(*_) -> None:
    env_mode: str = 'development' if not config.PRODUCTION else 'production'
    command: str = 'build' if env_mode == 'production' else 'build-devel'

    if env_mode == 'development':
        print("***")
        print("WARNING! You are building the frontend in the DEVELOPMENT mode!")
        print("This can be used in development environments only! Please switch to PRODUCTION on the prod server!")
        print("***")

    subprocess.run(['yarn', command])

