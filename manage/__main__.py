import os
import sys
import asyncio
import argparse
import subprocess
from routines import yesno


sys.path.insert(0, os.getcwd())


async def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', metavar='command')
    parser.add_argument('--pre-release', choices=['y', 'n'], default='n', required=False)
    args = parser.parse_args()

    command = args.command

    if command == 'devel':
        exit(0)

    elif command == 'build':
        from manage import build
        await build.execute()
        exit(0)

    elif command == 'update-deps':
        from manage import build
        await build.resolve_deps()
        exit(0)

    elif command == 'make':
        from manage import make
        await make.make()
        exit(0)

    elif command == 'make-statics':
        from manage import make
        make.make_statics_only()
        exit(0)

    elif command == 'fmake':
        subprocess.run(['yarn', 'build-devel'])
        exit(0)

    elif command == 'setup':
        from system import setup
        if not yesno(
            "Setup will rebuild both PostgreSQL & REDIS databases, destroying ALL DATA,"
            "after which will the database with initial data. Are you really sure???"
        ):
            print("Canceled")
            exit(1)
        await setup.rebuild_db()
        await setup.upload_initial_data()
        print("Done!")
        exit(0)

    elif command == 'migrate':
        from system.ds import migrate
        await migrate.migrate()
        print("Done!")
        exit(0)

    elif command == 'dropall':
        from system import setup
        if not yesno(
            "This command will drop all tables in the current PostgreSQL and all"
            " keys in the Redis. It will destroy ALL DATA in the databases. Are"
            " you really sure???"
        ):
            print("Canceled")
            exit(1)
        await setup.dropall()
        print("Done!")
        exit(0)

    elif command == 'build-demo':
        from system import setup, runtime
        if not yesno(
            "WARNING! This procedure will destroy ALL DATA in the PostgreSQL and"
            " Redis databases prior to build demo data. Are you really sure???"
        ):
            print("Canceled")
            exit(1)
        await setup.rebuild_db()
        await setup.upload_initial_data()
        await runtime.within_cli(setup.build_demo)
        print("Done!")
        exit(0)

    elif command == 'create-app':
        from manage import appman
        appman.create_app()
        exit(0)

    elif command == 'upgrade-system':
        from manage import platman
        if not yesno(
            "WARNING! This will download and upgrade the core system (WEFRAM). The new"
            " version will be installed if any exists. If your current version is the"
            " already lastest one - nothing will happend. Proceed with upgrade?",
            True
        ):
            print("Canceled")
            exit(1)
        pre_release: bool = args.pre_release == 'y'
        await platman.upgrade_system(pre_release)
        exit(0)

    print(f"Unknown command: {command}")
    exit(1)


asyncio.run(_main())
