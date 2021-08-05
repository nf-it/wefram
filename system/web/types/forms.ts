export type FormCommonFieldType =
  | 'string'
  | 'number'
  | 'text'
  | 'boolean'
  | 'choice'
  | 'image'
  | 'number-min-max'
  | 'string-list'

export type FormCommonFieldOption = {
  key: string
  caption: any
}

export type FormCommonFieldOptions = FormCommonFieldOption[]

export type FormCommonFieldItem = {
  fieldType: FormCommonFieldType
  caption: string
  name: string
  value?: any
  entity?: string
  clearable?: boolean
  cover?: boolean
  inline?: boolean
  minValue?: number
  maxValue?: number
  step?: number
  height?: string
  width?: string
  options?: FormCommonFieldOptions
}
