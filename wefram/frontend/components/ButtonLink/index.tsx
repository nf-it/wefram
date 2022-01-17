import React from 'react'
import {Link} from 'react-router-dom'
import {Button, ButtonProps} from 'system/components'


export interface ButtonLinkProps extends ButtonProps {
  to: string
}

export const ButtonLink = (props: ButtonLinkProps) => {
  let {style, to, children, ...elementProps} = props
  style = style ?? {}
  style.textDecoration = style.textDecoration ?? 'none'

  return (
    <Link
      to={to}
      style={{
        textDecoration: 'none'
      }}
    >
      <Button {...elementProps} style={style}>
        {children}
      </Button>
    </Link>
  )
}
