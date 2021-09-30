import React from 'react'
import {TranslatedTextVariant} from 'system/types'
import {LazyText} from 'system/components'


export type TranslatedTextProps = {
  appName: string
  textId: string
  variant?: TranslatedTextVariant
}

export const TranslatedText = (props: TranslatedTextProps) => {
  return (
    <LazyText appName={props.appName} textId={props.textId} variant={props.variant} baseUrl={'/translated_text'} />
  )
}

