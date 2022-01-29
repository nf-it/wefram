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

import {Response} from './response'
import {api} from './api'
import {RequestApiPath} from './routing'
import {TranslatedTextVariant, LocaleDicrionary, TranslatedTextResponse} from './types'


export const appName: string = 'l10n'
const apiVersion: number = 1
const translationsPath: RequestApiPath = {
  app: appName,
  path: 'translations',
  version: apiVersion
}

let translations: LocaleDicrionary = { }

/**
 * The localization project interface.
 */
export type LocalizationAPI = {
  _tryToTranslate(s: string, domain: string): string | null

  /**
   * Loads the localization dictionary from the instantiate request's response data.
   */
  load(): Response<LocaleDicrionary>

  /**
   * Initializes the localization dictionary from the {LocaleDictionary} struct.
   * @param s - the dictionary from which to initialize from.
   */
  initializeFromStruct(s: LocaleDicrionary): void

  /**
   * Initializes the localization dictionary from the backend using request.
   */
  initializeFromServer(): Promise<any>

  /**
   * Used to localize the given text (using given optional context domain).
   * @param s - the source, international english {string} text to localize.
   * @param domain - the optional domain context.
   * @return - localized {string} text.
   */
  gettext(s: string, domain?: string | undefined): string

  /**
   * Used to localize the given numbered text with singular and plural forms of words.
   * @param n - the number for which to localize; if the number is plural - the plural text
   *    form will be used, otherwise the singular text form will be used instead.
   * @param singular - the singular text form, international english {string} text to localize.
   * @param plural - the plural text form, international english {string} text to localize.
   * @param domain - the optional domain context.
   * @return - localized {string} text.
   */
  ngettext(n: number, singular: string, plural: string, domain?: string | undefined): string
  getTranslationText(app: string, textId: string, variant?: TranslatedTextVariant): Promise<TranslatedTextResponse | null>
}

export const localization: LocalizationAPI = {
  _tryToTranslate(s: string, domain: string): string | null {
    if (!(domain in translations))
      return null
    if (!(s in translations[domain]))
      return null
    return translations[domain][s]
  },

  async load(): Response<LocaleDicrionary> {
    return await api.get(translationsPath)
  },

  initializeFromStruct(s: LocaleDicrionary) {
    translations = s
  },

  async initializeFromServer() {
    await localization.load().then(res => {
      localization.initializeFromStruct(res.data)
    })
  },

  gettext(s: string, domainName?: string | undefined): string {
    let domain: string = domainName || '*'
    if (domain.indexOf('.') === -1) {
      domain = `${domain}.*`
    }
    const domains: string[] = [
      domain
    ]

    if (domain.indexOf('.') !== -1) {
      const domainEntities: string[] = domain.split('.')
      for (let i: number = 1, l: number = domainEntities.length; i < l; i++) {
        let sliced: string[] = domainEntities.slice(0, i + 1)
        let merged: string = sliced.join('.')
        domains.push(merged)
        if (String(sliced.slice(-1)) !== '*') {
          domains.push(`${sliced.slice(0, -1).join('.')}.*`)
        }
      }
    }

    if (domains[0] !== '*') {
      domains.push('*')
    }

    for (let i = 0, l = domains.length; i < l; i++) {
      let value: string | null = localization._tryToTranslate(s, domains[i])
      if (value !== null)
        return value
    }
    return s
  },

  ngettext(n: number, singular: string, plural: string, domain?: string | undefined): string {
    return (n > 1 || n < -1 || n === 0) ? localization.gettext(plural, domain) : localization.gettext(singular, domain)
  },

  getTranslationText(app, textId, variant) {
    return api.get({
      app: 'system',
      path: `translations/text/${app}/${textId}`
    }, {
      params: {
        variant
      }
    }).then(res => {
      const variant: TranslatedTextVariant = res.headers['x-text-variant']
      const content: string = String(res.data)
      return {
        content,
        variant
      }
    }).catch(() => {
      return null
    })
  }
}

export const gettext = localization.gettext
export const ngettext = localization.ngettext
