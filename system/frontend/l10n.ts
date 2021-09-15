import {Localization} from '@material-ui/core/locale'
import {Response} from './response'
import {api} from './api'
import {RequestApiPath} from './routing'


export const appName: string = 'l10n'
const apiVersion: number = 1
const translationsPath: RequestApiPath = {
  app: appName,
  path: 'translations',
  version: apiVersion
}


export type Locale = {
  name: string
  weekStartsOn?: 0 | 1 | 2 | 3 | 4 | 5 | 6
  firstWeekContainsDate?: 1 | 2 | 3 | 4 | 5 | 6 | 7
  dateFormat: string
}

export type TLocaleDictDomain = Record<string, string>
export type TLocaleDicrionary = Record<string, TLocaleDictDomain>
let translations: TLocaleDicrionary = { }

export type LocalizationAPI = {
  _tryToTranslate(s: string, domain: string): string | null
  load(): Response<TLocaleDicrionary>
  initializeFromStruct(s: TLocaleDicrionary): void
  initializeFromServer(): Promise<any>
  createMuiLocalization(): Localization
  gettext(s: string, domain?: string | undefined): string
  ngettext(n: number, singular: string, plural: string, domain?: string | undefined): string
}

export const localization: LocalizationAPI = {
  _tryToTranslate(s: string, domain: string): string | null {
    if (!(domain in translations))
      return null
    if (!(s in translations[domain]))
      return null
    return translations[domain][s]
  },

  async load(): Response<TLocaleDicrionary> {
    return await api.get(translationsPath)
  },

  initializeFromStruct(s: TLocaleDicrionary) {
    translations = s
  },

  async initializeFromServer() {
    await localization.load().then(res => {
      localization.initializeFromStruct(res.data)
    })
  },

  createMuiLocalization(): Localization {
    return {
      props: {
        MuiBreadcrumbs: {
          expandText: gettext("Show path", 'system.ui-mui')
        },
        MuiTablePagination: {
          backIconButtonText: gettext("Previous page", 'system.ui-mui'),
          labelRowsPerPage: gettext("Rows on page:", 'system.ui-mui'),
          labelDisplayedRows: function labelDisplayedRows(_ref) {
            const
              from = _ref.from,
              to = _ref.to,
              count = _ref.count
            return ""
              .concat(String(from), "-")
              .concat(String(to), gettext(" of ", 'system.ui-mui'))
              .concat(count !== -1 ? String(count) : gettext("more than ", 'system.ui-mui').concat(String(to)))
          },
          nextIconButtonText: gettext("Next page", 'system.ui-mui')
        },
        MuiRating: {
          getLabelText: function getLabelText(value) {
            return "".concat(String(value), (value !== 1 ? gettext(" stars", 'system.ui-mui') : gettext(" star", 'system.ui-mui')))
          },
          emptyLabelText: gettext("None", 'system.ui-mui')
        },
        MuiAutocomplete: {
          clearText: gettext("Clear", 'system.ui-mui'),
          closeText: gettext("Close", 'system.ui-mui'),
          loadingText: gettext("Loading…", 'system.ui-mui'),
          noOptionsText: gettext("No options available", 'system.ui-mui'),
          openText: gettext("Open", 'system.ui-mui')
        },
        MuiAlert: {
          closeText: gettext("Close", 'system.ui-mui')
        },
        MuiPagination: {
          'aria-label': gettext("Pagination navigation", 'system.ui-mui'),
          getItemAriaLabel: function getItemAriaLabel(type, page, selected) {
            if (type === 'page') {
              return `${selected ? gettext("Page", 'system.ui-mui') : gettext("Go to page", 'system.ui-mui')} ${page}`
            }

            if (type === 'first') {
              return gettext("Go to first page", 'system.ui-mui')
            }

            if (type === 'last') {
              return gettext("Go to last page", 'system.ui-mui')
            }

            if (type === 'next') {
              return gettext("Go to next page", 'system.ui-mui')
            }

            if (type === 'previous') {
              return gettext("Go to previous page", 'system.ui-mui')
            }

            return undefined;
          }
        }
      }
    }
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
  }
}

export const gettext = localization.gettext
export const ngettext = localization.ngettext
