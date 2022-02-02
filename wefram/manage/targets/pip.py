import subprocess
from ..routines import deps


def run(*_) -> None:
    requirements: dict = deps.get_pip_dependencies()
    subprocess.run(['pip', 'install', '--upgrade', 'pip'])
    subprocess.run(['pip', 'install', '--upgrade', *[
        pkg_name if pkg_vers == 'latest' else f"{pkg_name}~={pkg_vers}"
        for pkg_name, pkg_vers in requirements.items()
    ]])
