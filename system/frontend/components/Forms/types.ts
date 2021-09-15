import React from 'react'


export type FormFieldCommon = {
  _formData?: any
  _formOnChange?: (name: string, newValue: any) => void
  formName?: string
}
