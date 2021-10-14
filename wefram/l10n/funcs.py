from typing import *
import babel
import babel.numbers
from ..types.l10n import L10nStr
from ..runtime import context
from ..tools import get_calling_app
from .locales import Locale
from .catalog import translate, translate_pluralizable
from .resources import *


__all__ = [
    'current_locale',
    'best_matching_locale',
    'gettext',
    'ngettext',
    'lazy_gettext',
    'lazy_ngettext',
]


def current_locale() -> Locale:
    if 'locale' not in context:
        raise RuntimeError(EXC_CONTEXT)
    return context['locale']


def best_matching_locale(options: List[str]) -> Optional[babel.Locale]:
    """ Returns a best matched locale name for given options list. If there is no any matchings -
    returns None.
    """
    for option in options:
        try:
            locale: babel.Locale = babel.Locale.parse(option.replace('-', '_'))
            return locale
        except babel.UnknownLocaleError:
            continue
    return None


def lazy_gettext(
        untranslated: str,
        domain: Optional[str] = None
) -> L10nStr:
    """ The lazy localization function about to be great used at the moment when the running
    process even does not knows the target locale. For example, it is good to use at
    the moment of application initialization, naming something, because for the very that
    moment there is no actual user who about to read the localized message, and the process
    does not knows which language the user will speak to.
    """
    return L10nStr(untranslated, domain)


def lazy_ngettext(
        num: [int, float, callable],
        untranslated: str,
        domain: Optional[str] = None
) -> L10nStr:
    return L10nStr(untranslated, domain, num)


def gettext(
        untranslated: str,
        domain: Optional[str] = None
) -> str:
    """ Translates the given untranslated message at a time this function being called. This
    means that there must be a running valid request context to make translation succeed.
    """
    app_name: str = get_calling_app()
    return translate(untranslated, domain, app_name)


def ngettext(
        num: [int, float, callable],
        untranslated: str,
        domain: Optional[str] = None
) -> str:
    """ Translates the given untranslated message at a time this function being called. This
    means that there must be a running valid request context to make translation succeed.
    """
    app_name: str = get_calling_app()
    return translate_pluralizable(num, untranslated, domain, app_name)


def format_decimal(number: [int, float], locale_: Optional[Locale] = None) -> str:
    locale_ = locale_ or current_locale()
    return babel.numbers.format_decimal(number, locale_)


_ = gettext

