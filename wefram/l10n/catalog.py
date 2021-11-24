from typing import *
import os.path
import json
from json.decoder import JSONDecodeError
from ..runtime import context
from ..tools import CSTYLE, get_calling_app
from .. import logger
from .locales import Locale
from .config import BUILT_DICTS_PATH
from .resources import *


__all__ = [
    'locate_dictionary_json',
    'Dictionary',
    'translate',
    'translate_pluralizable',
    'pack_dictionary',
    'ui_locale_json'
]


class _Domain:
    messages: Dict[str, str]
    messages_lc: Dict[str, str]

    def __init__(self, messages: Dict[str, str]):
        self.messages = messages
        self.messages_lc = {u.lower(): t for u, t in messages.items()}

    def get(self, untranslated: str) -> Optional[str]:
        return self.messages.get(untranslated, None)

    def getlc(self, untranslated: str) -> Optional[str]:
        return self.messages_lc.get(untranslated, None)

    def add(self, untranslated: str, translated: str) -> None:
        self.messages[untranslated] = translated
        self.messages_lc[untranslated.lower()] = translated

    def merge(self, messages: Dict[str, str]):
        for m_id, m_msg in messages.items():
            self.messages[m_id] = m_msg
            self.messages_lc[m_id.lower()] = m_msg

    def merge_with(self, merging_domain: '_Domain'):
        self.messages.update(merging_domain.messages)
        self.messages_lc.update(merging_domain.messages_lc)

    @property
    def as_dict(self) -> Dict[str, str]:
        return self.messages.copy()


def locate_dictionary_json(locale: Locale) -> Optional[str]:
    fn: str
    language: str = locale.language
    territory: str = locale.territory

    territory = language.upper() if not territory else territory.upper()
    fn = '_'.join([language, territory])
    fn = os.path.join(BUILT_DICTS_PATH, f"{fn}.json")
    if os.path.isfile(fn):
        return fn
    fn = os.path.join(BUILT_DICTS_PATH, f"{language}.json")
    if os.path.isfile(fn):
        return fn

    if not os.path.isdir(BUILT_DICTS_PATH):
        return None

    fns = sorted([f for f in os.listdir(BUILT_DICTS_PATH) if f.startswith(f"{language}_")])
    if fns:
        return os.path.join(BUILT_DICTS_PATH, fns[0])

    return None


class Dictionary:
    def __init__(self, locale_: Locale, autoload: bool = True):
        self.locale: Locale = locale_
        self._domains: Dict[str, _Domain] = (self.load() if autoload else dict()) or dict()

    @classmethod
    def parse_dictionary(
            cls,
            dictionary: dict,
            prefix: Optional[str] = None
    ) -> Dict[str, _Domain]:
        domains: Dict[str, _Domain] = {}

        for domain_id, messages in dictionary.items():
            domain_id: str
            messages: Dict[str, str]

            if domain_id != '**' and prefix and prefix != domain_id:
                domain_id = '.'.join([prefix, domain_id])
            elif domain_id == '**':
                domain_id = '*'

            domains[domain_id]: _Domain = _Domain(messages)

        return domains

    @classmethod
    def from_source(
            cls,
            filename: str,
            prefix: Optional[str] = None
    ) -> Optional[Dict[str, _Domain]]:
        if not os.path.isfile(filename):
            logger.warning(f"translations file not found: {filename}")
            return

        try:
            with open(filename, 'r') as f:
                loaded: dict = json.load(f)
                logger.info(f"loaded translations from file: {filename}")
            domains: Dict[str, _Domain] = cls.parse_dictionary(loaded, prefix)

        except JSONDecodeError:
            return

        return domains

    def load(
            self,
            filename: Optional[str] = None,
            prefix: Optional[str] = None
    ) -> Optional[Dict[str, _Domain]]:
        dictionary_path: Optional[str] = filename or locate_dictionary_json(self.locale)
        if not dictionary_path:
            return
        loaded: Optional[Dict[str, _Domain]] = self.from_source(dictionary_path, prefix)
        if loaded is not None:
            logger.debug(
                f"loaded localization catalog for locale {CSTYLE['bold']}{str(self.locale)}{CSTYLE['clear']}"
            )
        return loaded

    def merge(self, domains: Dict[str, _Domain]) -> None:
        for n, d in domains.items():
            domain = self.ensure_domain(n)
            domain.merge_with(d)

    def add(
            self,
            untranslated: [str, Tuple[str, str]],
            translated: [str, Tuple[str, str]],
            domain: Optional[str] = None,
            app_name: Optional[str] = None
    ) -> None:
        domain: str = domain or "*"
        app_name: str = app_name or get_calling_app()
        domain_name: str = '.'.join([app_name, domain])
        _domain = self.ensure_domain(domain_name)
        _domain.add(untranslated, translated)

    def as_dict(self) -> Dict[str, dict]:
        return {
            name: domain.as_dict for name, domain in self._domains.items()
        }

    def save(self, filename: Optional[str] = None) -> None:
        contents: Dict[str, dict] = self.as_dict()
        filename: str = f"{filename or str(self.locale)}.json"
        if not filename.startswith('/'):
            filename = os.path.join(BUILT_DICTS_PATH, filename)

        if os.path.exists(filename):
            os.unlink(filename)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(contents, f, ensure_ascii=False)

    @property
    def domains(self) -> Dict[str, _Domain]:
        return self._domains

    def get_domain(self, name: str) -> Optional[_Domain]:
        return self._domains.get(name, None)

    def ensure_domain(self, name: str) -> _Domain:
        _domain = self.get_domain(name)
        if _domain is not None:
            return _domain
        self._domains[name] = _Domain({})
        return self._domains[name]

    def translate(
            self,
            untranslated: [str, Tuple[str, str]],
            domain: Optional[str],
            app_name: str,
            get_plural: bool = False
    ) -> str:
        untranslated: List[str] = list(untranslated) \
            if isinstance(untranslated, (list, tuple)) \
            else [untranslated, ]

        if not self._domains:
            return untranslated[-1] if get_plural else untranslated[0]

        domain: str = domain or "*"
        searching_domain: str = ('.'.join([app_name, domain]) if domain else app_name) \
            if not domain or '.' not in domain \
            else domain
        searching_domains: List[str] = [searching_domain, f"{app_name}.*", '*']

        term: str = untranslated[-1] if get_plural else untranslated[0]
        for domain_name in searching_domains:
            _domain: Optional[_Domain] = self.get_domain(domain_name)
            if _domain is None:
                continue
            result: Optional[str] = _domain.get(term)
            if result is not None:
                return result

        lcterm = str(term).lower()
        for domain_name in searching_domains:
            _domain: Optional[_Domain] = self.get_domain(domain_name)
            if _domain is None:
                continue
            result: Optional[str] = _domain.getlc(lcterm)
            if result is not None:
                return result

        return term


_catalogs: Dict[str, Optional[Dictionary]] = {}


def _get_dictionary(locale: Locale) -> Dictionary:
    locale_code: str = str(locale)
    if locale_code not in _catalogs:
        _catalogs[locale_code]: Optional[Dictionary] = Dictionary(locale)
    return _catalogs[locale_code]


def _get_current_dictionary() -> Dictionary:
    if 'locale' not in context:
        raise RuntimeError(EXC_CONTEXT)
    locale: Locale = context['locale']
    return _get_dictionary(locale)


def pack_dictionary(
        locale: Optional[Locale] = None
) -> Dict[str, dict]:
    dictionary: Dictionary = _get_current_dictionary() if locale is None else _get_dictionary(locale)
    return dictionary.as_dict()


def ui_locale_json() -> dict:
    locale: Locale = context['locale']
    date_format: str = str(locale.datetime_skeletons['yMd']) \
        .replace('MM', 'M') \
        .replace('dd', 'd') \
        .replace('yy', 'y') \
        .replace('M', 'MM') \
        .replace('d', 'dd') \
        .replace('y', 'yyyy')
    return {
        'name': str(locale),
        'weekStartsOn': locale.first_week_day,
        'firstWeekContainsDate': 1,
        'dateFormat': date_format
    }


def translate(
        untranslated: [str, Tuple[str, str]],
        domain: Optional[str],
        app_name: str
) -> str:
    return _get_current_dictionary().translate(
        untranslated,
        domain,
        app_name,
        False
    )


def translate_pluralizable(
        num: [int, float, callable],
        untranslated: [str, Tuple[str, str]],
        domain: Optional[str],
        app_name: str
) -> str:
    if callable(num):
        num: [int, float] = num()
    return _get_current_dictionary().translate(
        untranslated,
        domain,
        app_name,
        num > 1 or num < -1 or num == 0
    )

