import React from 'react'
import {Link} from 'react-router-dom'
import {Button, ButtonProps} from 'system/components'
import './index.css'


export interface ButtonLinkProps extends ButtonProps {
  to: string
}

export const ButtonLink = (props: ButtonLinkProps) => (
  <Link to={props.to} className={'SystemUI-buttonLink'}>
    <Button {...props} className={'SystemUI-buttonLinkButton'}>{props.children}</Button>
  </Link>
)

