import React from 'react'
import {Box} from 'system/components'
import {LoginForm} from '../LoginForm'


const Login = () => (
  <Box style={{
    position: 'fixed',
    left: 0,
    top: 0,
    bottom: 0,
    right: 0,
    zIndex: 20000
  }}>
    <LoginForm />
  </Box>
)

export default Login
