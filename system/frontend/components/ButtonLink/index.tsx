import React from 'react'
import {Link} from 'react-router-dom'
import {Button, ButtonProps} from '@material-ui/core'
import './index.css'


export interface ButtonLinkProps extends ButtonProps {
  to: string
}


export class ButtonLink extends React.Component<ButtonLinkProps> {
  render() {
    return (
      <Link to={this.props.to} className={'SystemUI-buttonLink'}>
        <Button {...this.props} className={'SystemUI-buttonLinkButton'}>{this.props.children}</Button>
      </Link>
    )
  }
}
