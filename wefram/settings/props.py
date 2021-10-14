from typing import *
from ..types.l10n import L10nStr
from ..types.settings import PropBase
from ..tools import get_calling_app


__all__ = [
    'ItemKey',
    'ItemValue',
    'KeysValuesDict',
    'KeyValueItem',
    'KeysValuesList',

    'ChoiceProp',
    'BooleanProp',
    'FileProp',
    'ImageProp',
    'NumberProp',
    'NumberMMProp',
    'StringListProp',
    'StringProp',
    'TextProp',
]


ItemKey = Union[str, int, None]
ItemValue = Any
KeysValuesDict = Dict[ItemKey, ItemValue]
KeyValueItem = Tuple[ItemKey, ItemValue]
KeysValuesList = Sequence[KeyValueItem]


class StringProp(PropBase):
    prop_type = 'string'


class NumberProp(PropBase):
    prop_type = 'number'


class NumberMMProp(PropBase):
    prop_type = 'number-min-max'

    def __init__(
            self,
            caption: Union[str, L10nStr],
            min_value: int,
            max_value: int,
            step: int = 1,
            order: Optional[int] = None
    ):
        super().__init__(caption, order)
        self.min_value: int = min_value
        self.max_value: int = max_value
        self.step: int = step

    def schemadef(self) -> dict:
        return {**super().schemadef(), **{
            'minValue': int(self.min_value),
            'maxValue': int(self.max_value),
            'step': int(self.step)
        }}


class TextProp(PropBase):
    prop_type = 'text'


class BooleanProp(PropBase):
    prop_type = 'boolean'

    def __init__(
            self,
            caption: Union[str, L10nStr],
            inline: bool = False,
            order: Optional[int] = None
    ):
        super().__init__(caption, order)
        self.inline: bool = bool(inline)

    def schemadef(self) -> dict:
        return {**super().schemadef(), **{
            'inline': bool(self.inline)
        }}


class ChoiceProp(PropBase):
    prop_type = 'choice'

    def __init__(
            self,
            caption: Union[str, L10nStr],
            options: Union[KeysValuesList, KeysValuesDict],
            order: Optional[int] = None
    ):
        super().__init__(caption, order)
        if not isinstance(options, (list, tuple, dict)):
            raise ValueError(
                f"ChoiceProp.options must be type of (list, tuple or dict), {type(options)} given instead"
            )
        self.options = options

    def schemadef(self) -> dict:
        options: KeysValuesList
        if isinstance(self.options, dict):
            options = [(key, caption) for key, caption in self.options.items()]
        else:
            options = self.options
        return {**super().schemadef(), **{
            'options': [{
                'key': option[0],
                'caption': option[1]
            } for option in options]
        }}


class StringListProp(PropBase):
    prop_type = 'string-list'


class ImageProp(PropBase):
    prop_type = 'image'

    def __init__(
            self,
            caption: Union[str, L10nStr],
            entity: str,
            clearable: bool = True,
            prop_cover: bool = False,
            prop_height: Union[str, int] = '10vmax',
            prop_width: Optional[Union[str, int]] = None,
            prop_inline: bool = False,
            order: Optional[int] = None
    ):
        super().__init__(caption, order)
        self.entity: str = self._entity_from(entity)
        self.clearable: bool = bool(clearable)
        self.prop_cover: bool = prop_cover
        self.prop_height: Union[str, int] = prop_height
        self.prop_width: Optional[Union[str, int]] = prop_width
        self.prop_inline: bool = bool(prop_inline)

    def _entity_from(self, src: str) -> str:
        return '.'.join([get_calling_app(), src]) if '.' not in src else src

    def schemadef(self) -> dict:
        return {**super().schemadef(), **{
            'entity': self.entity,
            'clearable': bool(self.clearable),
            'inline': bool(self.prop_inline),
            'cover': self.prop_cover,
            'height': f'{self.prop_height}px' if isinstance(self.prop_height, int) else self.prop_height,
            'width': f'{self.prop_width}px' if isinstance(self.prop_width, int) else self.prop_width,
        }}


class FileProp(PropBase):
    prop_type = 'file'

    def __init__(
            self,
            caption: Union[str, L10nStr],
            entity: str,
            order: Optional[int] = None
    ):
        super().__init__(caption, order)
        self.entity = self._entity_from(entity)

    def _entity_from(self, src: str) -> str:
        return '.'.join([get_calling_app(), src]) if '.' not in src else src

    def schemadef(self) -> dict:
        return {**super().schemadef(), **{
            'entity': self.entity
        }}

