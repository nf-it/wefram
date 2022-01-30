import {Response} from 'system/response'


export type Locale = {
  name: string
  weekStartsOn?: 0 | 1 | 2 | 3 | 4 | 5 | 6
  firstWeekContainsDate?: 1 | 2 | 3 | 4 | 5 | 6 | 7
  dateFormat: string
}

export type TranslatedTextVariant = 'html' | 'md' | 'txt'
export type LazyTextVariant = 'html' | 'md' | 'txt'

export type LocaleDictDomain = Record<string, string>
export type LocaleDicrionary = Record<string, LocaleDictDomain>

export type TranslatedTextResponse = {
  content: string
  variant: TranslatedTextVariant
}


/**
 * The localization project interface type.
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

  /**
   * Returns the translation text by the given application name (`app`) and the corresponding
   * localization text ID (`textId`).
   * @param app - the name of the text's parent application (where the text is stored at).
   * @param textId - the ID of the text record.
   * @param variant - the required variant (if there are several variants have been stored).
   * @return - the Promise of {TranslatedTextResponse} type or null of there is no text.
   */
  getTranslationText(app: string, textId: string, variant?: TranslatedTextVariant): Promise<TranslatedTextResponse | null>
}
