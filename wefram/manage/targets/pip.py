import os.path
import subprocess
from ..routines import deps
from ... import config


def run(*_) -> None:
    requirements: dict = deps.get_pip_dependencies()
    requirements_fn: str = os.path.join(config.PRJ_ROOT, 'requirements')
    with open(requirements_fn, 'w') as f:
        f.write('\n'.join([
            pkg_name if pkg_vers == 'latest' else f"{pkg_name}~={pkg_vers}"
            for pkg_name, pkg_vers in requirements.items()
        ]))
    subprocess.run(['pip', 'install', '--upgrade', 'pip'])
    subprocess.run(['pip', 'install', '-r', requirements_fn])
