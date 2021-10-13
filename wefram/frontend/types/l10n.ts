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
