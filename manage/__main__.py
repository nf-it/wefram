import os
import sys
import asyncio
import argparse


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

    elif command == 'rebuild-db':
        from manage import make
        from system import setup
        await setup.rebuild_db()
        await setup.upload_initial_data()
        print("Done!")
        exit(0)

    elif command == 'build-demo':
        from system import setup
        await setup.build_demo()
        await setup.upload_initial_data()
        exit(0)

    elif command == 'create-app':
        from manage import appman
        appman.create_app()
        exit(0)

    elif command == 'first-install-prepare':
        from manage import build
        await build.first_install_prepare()
        exit(0)

    elif command == 'upgrade-system':
        from manage import platman
        pre_release: bool = args.pre_release == 'y'
        await platman.upgrade_system(pre_release)
        exit(0)

    print(f"Unknown command: {command}")
    exit(1)


asyncio.run(_main())
