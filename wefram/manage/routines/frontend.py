from typing import *
import os.path
from ... import config


__all__ = [
    'with_template'
]


FRONT_TEMPLATES_ROOT: str = os.path.join(config.CORE_ROOT, 'frontend', 'templates')
FRONT_BUILD_ROOT: str = os.path.join(config.BUILD_ROOT, 'frontend')


def with_template(
        template_fn: str,
        prepared_fn: Optional[str] = None,
        **kwargs
) -> None:
    prepared_fn: str = prepared_fn or template_fn
    with open(os.path.join(FRONT_TEMPLATES_ROOT, template_fn), 'r') as template_f:
        content: str = template_f.read()
    for k, v in kwargs.items():
        content = content.replace(f"/* (%%{k}%%) */", v)
    with open(os.path.join(FRONT_BUILD_ROOT, prepared_fn), 'w') as prepared_f:
        prepared_f.write(content)
