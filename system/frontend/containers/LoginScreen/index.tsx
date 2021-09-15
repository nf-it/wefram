import React from 'react'
import {LoginForm} from '../LoginForm'


type LoginScreenProps = {
  canCancel: boolean
}


export class LoginScreen extends React.Component<LoginScreenProps> {
  static defaultProps: LoginScreenProps = {
    canCancel: false
  }

  render() {
    return (
      <div style={{
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        right: 0,
        zIndex: 20000
      }}>
        <LoginForm />
      </div>
    )
  }
}

