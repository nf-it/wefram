import React from 'react'
import {Remarkable} from 'remarkable'
import {Box, Typography, TypographyProps} from 'system/components'


export type MarkdownTextProps = TypographyProps & {
  text: string
  html?: boolean
  xhtmlOut?: boolean
  breaks?: boolean
  langPrefix?: string
  linkify?: boolean
  linkTarget?: string
  typographer?: boolean
  quotes?: string
  highlight?: (str: string, lang: string) => string
}

export const MarkdownText = (props: MarkdownTextProps) => {
  const {
    text,
    html,
    xhtmlOut,
    breaks,
    langPrefix,
    linkify,
    linkTarget,
    typographer,
    quotes,
    highlight,
    ...typographyProps
  } = props
  const md = new Remarkable({
    html,
    xhtmlOut,
    breaks,
    langPrefix,
    linkify,
    linkTarget,
    typographer,
    quotes,
    highlight
  })
  return (
    <Typography {...typographyProps}>
      <Box dangerouslySetInnerHTML={{__html: md.render(props.text)}} />
    </Typography>
  )
}
