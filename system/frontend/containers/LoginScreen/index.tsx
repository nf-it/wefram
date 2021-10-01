import React from 'react'
import {LoginForm} from '../LoginForm'


export const LoginScreen = () => (
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
