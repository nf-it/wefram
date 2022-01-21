from typing import *
from ...tools import py_to_json


RouteParams = List[str]
CompositeLayout = List[Any]


class Prop:
    """
    The base class used by composite screens' fields to form props.
    """

    props: dict = {}

    def as_json(self) -> dict:
        return {k: v for k, v in py_to_json(self.props) if v is not ...}

