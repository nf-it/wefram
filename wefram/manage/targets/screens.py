from ..routines import frontend
from ... import ui
from ...tools import json_encode_custom


def run(*_) -> None:
    schema: dict = ui.screens.as_json()
    items: str = json_encode_custom(schema, indent=2).lstrip('{').rstrip('}').strip('\n')
    frontend.with_template('screens.ts', items=items)
