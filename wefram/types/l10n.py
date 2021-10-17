from typing import *
from ..tools import get_calling_app


__all__ = [
    'L10nStr'
]


class L10nStr:
    """ The lazy localization string wrapping type. Used to set up localizatable
    string which translated actual value is unknown at a time of defining this
    text. The actual value will be returned to the caller (uses str() type
    conversion, for example) at a moment, depending on the request context and
    corresponding user's preferred language.
    """

    def __init__(
            self,
            untranslated: str,
            domain: Optional[str] = None,
            plural_num: Optional[Union[int, float, callable]] = None
    ):
        super().__init__()
        self.app_name: str = get_calling_app()
        self.untranslated: str = untranslated
        self.domain: Optional[str] = domain
        self.plural_num: Optional[Union[int, float, callable]] = plural_num

    def localize(self) -> str:
        """ Translates this lazy stored localization in runtime to the corresponding
        localized variant, or return an original text if there is no translation.
        """
        from ..l10n.catalog import translate, translate_pluralizable

        return translate(self.untranslated, self.domain, self.app_name) \
            if self.plural_num is None \
            else translate_pluralizable(self.plural_num, self.untranslated, self.domain, self.app_name)

    def __str__(self) -> str:
        return self.localize()

    def __repr__(self) -> str:
        return self.localize()

    def __call__(self):
        return self.localize()
