"""
Provides types of properties used in the settings entities.
"""

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
    """
    The common, single line string text field. Python representation is ``str``.
    """

    prop_type = 'string'


class NumberProp(PropBase):
    """
    The number property. Represented by ``int`` type.
    """

    prop_type = 'number'


class NumberMMProp(PropBase):
    """
    The property providing the selection of a number from the specified
    range of numbers: the minimum and the maximum ones. The step might
    be set to the necessary value.

    :param min_value:
        The minimum allowed value, the range start.
    :type min_value:
        int

    :param max_value:
        The maximum allowed value, the range end.
    :type max_value:
        int

    :param step:
        The step of the value selection. Is optional and if is omitted,
        then "1" will be used.
    :type step:
        Optional, int
    """

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
    """
    The multiline text field. Represented by ``str`` python type.
    """

    prop_type = 'text'


class BooleanProp(PropBase):
    """
    The boolean (true-false, yes-no) property. Rendered as switch with given
    caption next to it. The additional ``inline`` argument might be set to
    rearrange the caption from the left column to the one line, with caption
    right next to the switch on the right side.

    :param inline:
        If set to ``True``, then the switch will be rendered on the begining of
        the property row, with the caption right next to the switch; else,
        if set to ``False`` (default) - the default layout with caption on
        the left side and the switch on the right side.
    :type inline:
        bool, default = False
    """

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
    """
    The choice property which provides the selection the one option
    from the list of available. Options are declared using the ``options``
    argument.

    :param options:
        The set of available options to select from. There two variants
        of options declaration are provided:

        #. Using the list, each element of which is a tuple, containing
            the corresponding item key (value) at the first place, and
            the caption of that item at the second. For example:

            ``
            ChoiceProp(caption="The first variant", options=[
                ('value1', "The first option"),
                ('value2', "The second option")
            ])
            ``
        #. Using the dict, in which keys representing corresponding items'
            values, and dict's values represents items' captions. In
            this case items will be ordered by their captions. For
            example:

            ``
            ChoiceProp(caption="The second variant", options={
                'value1': "The first option",
                'value2': "The second option"
            })
            ``
    :type options:
        list, dict
    """

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
    """
    The modificable list of strings. This property provides the posibility
    to render and modify the list of strings, by adding and removing them.
    The python representation is ``list`` or, in ``typing`` terms,
    the ``List[str]``.
    """

    prop_type = 'string-list'


class ImageProp(PropBase):
    """
    Provides the uploadable image property. Requires the corresponding
    storage entity to be specified.

    :param entity:
        The corresponding storage entity name to which the image uploads to.
    :type entity:
        str

    :param clearable:
        If set to ``True`` - the uploaded image might be removed, clearing
        the property's value; otherwise the image is required to be present.
    :type clearable:
        bool, default = True

    :param prop_cover:
        If set to ``True``, the image in the property will be shown covered,
        otherwise - contained.
    :type prop_cover:
        bool, default = False

    :param prop_height:
        The height of the image rendered as the settings property.
    :type prop_height:
        str | int, default = '10vmax'

    :param prop_width:
        The width of the image rendered as the settings property.
    :type prop_width:
        str | int

    :param prop_inline:
        If set to ``True`` - the image property will be rendered full width,
        with caption at the top of the image; otherwise the standard layout
        will be used with caption in the left part, and the image in the
        right part of the property row.
    :type prop_inline:
        bool, default = False
    """

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
    """
    Provides the uploadable file property. Requires the corresponding
    storage entity to be specified.

    :param entity:
        The corresponding storage entity to which the file uploads to.
    """

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

