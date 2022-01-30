/**
 * Provides the localization facility of the project.
 *
 * The project's applications about to import `gettext` and `ngettext` functions to get a localized text
 * basing on the source, english form.
 *
 * For example:
 *
 * ``
 *    ...
 *    import {gettext} from 'system/l10n'
 *
 *    ...
 *
 *    const localized_text: string = gettext("Welcome", 'myapp.mydomain')
 *    const another_text: string = gettext("How are you?")
 * ``
 */

export * from './types'
export * from './interface'
