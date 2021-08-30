from typing import *
import babel
from ..runtime import context
from .resources import *


__all__ = [
    'Locale',
    'locale',
]


class Locale(babel.Locale):
    pass


class _LocaleContextWrapper:

    language_name: property = Locale.language_name
    get_territory_name: callable = Locale.get_territory_name
    territory_name: property = Locale.territory_name
    get_script_name: callable = Locale.get_script_name
    script_name: property = Locale.script_name
    english_name: property = Locale.english_name
    languages: property = Locale.languages
    scripts: property = Locale.scripts
    territories: property = Locale.territories
    variants: property = Locale.variants
    currencies: property = Locale.currencies
    currency_symbols: property = Locale.currency_symbols
    number_symbols: property = Locale.number_symbols
    decimal_formats: property = Locale.decimal_formats
    currency_formats: property = Locale.currency_formats
    percent_formats: property = Locale.percent_formats
    scientific_formats: property = Locale.scientific_formats
    periods: property = Locale.periods
    day_periods: property = Locale.day_periods
    day_period_rules: property = Locale.day_period_rules
    days: property = Locale.days
    months: property = Locale.months
    quarters: property = Locale.quarters
    eras: property = Locale.eras
    time_zones: property = Locale.time_zones
    meta_zones: property = Locale.meta_zones
    zone_formats: property = Locale.zone_formats
    first_week_day: property = Locale.first_week_day
    weekend_start: property = Locale.weekend_start
    weekend_end: property = Locale.weekend_end
    min_week_days: property = Locale.min_week_days
    date_formats: property = Locale.date_formats
    time_formats: property = Locale.time_formats
    datetime_formats: property = Locale.datetime_formats
    datetime_skeletons: property = Locale.datetime_skeletons
    interval_formats: property = Locale.interval_formats
    plural_form: property = Locale.plural_form
    list_patterns: property = Locale.list_patterns
    ordinal_form: property = Locale.ordinal_form
    measurement_systems: property = Locale.measurement_systems
    character_order: property = Locale.character_order
    text_direction: property = Locale.text_direction
    unit_display_names: property = Locale.unit_display_names

    def __getattribute__(self, key: str) -> Any:
        if key.startswith('__') and key.endswith('__'):
            return super().__getattribute__(key)
        if key not in self.__annotations__:
            return super().__getattribute__(key)

        if 'locale' not in context:
            raise RuntimeError(EXC_CONTEXT)

        locale_: Locale = context['locale']
        return getattr(locale_, key)


locale = _LocaleContextWrapper()

