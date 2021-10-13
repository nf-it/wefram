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

export type LocalizationAPI = {
  _tryToTranslate(s: string, domain: string): string | null
  load(): Response<LocaleDicrionary>
  initializeFromStruct(s: LocaleDicrionary): void
  initializeFromServer(): Promise<any>
  gettext(s: string, domain?: string | undefined): string
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
