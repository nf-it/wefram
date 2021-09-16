import React from 'react'
import {observer} from 'mobx-react'
import {
  Avatar,
  Box,
  Button,
  CssBaseline,
  Grid,
  TextField,
  FormControlLabel,
  Checkbox,
  Link,
  Paper,
  Typography
} from 'system/components'
import LockOutlinedIcon from '@material-ui/icons/LockOutlined'
import {gettext} from 'system/l10n'
import {notifications} from 'system/notification'
import {runtime, appInterface} from 'system/runtime'
import {routing} from 'system/routing'
import {aaa} from 'system/aaa/api'
import {session} from 'system/aaa/session'
import {localStorageUsernameRememberKeyname} from 'system/types/aaa'
import './index.css'


function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {'Copyright © '}
      <Link color="inherit" href="https://nf-it.ru/">
        NF-IT
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

type Props = {}

type State = {
  username: string
  password: string
  remember: boolean
}

class _LoginForm extends React.Component<Props, State> {
  state: State = {
    username: runtime.rememberUsername
      ? localStorage.getItem(localStorageUsernameRememberKeyname) || ''
      : '',
    password: '',
    remember: false,
  }
  passwordInput: HTMLInputElement | null

  constructor(props: Props) {
    super(props)
    this.passwordInput = null
  }

  componentDidMount() {
    if (this.state.username !== '') {
      this.passwordInput?.focus()
    }
  }

  private handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (this.state.username === '' || this.state.password === '')
      return

    const remember = runtime.rememberUsername && this.state.remember
    if (remember) {
      localStorage.setItem(localStorageUsernameRememberKeyname, this.state.username)
    }

    runtime.busy = true
    aaa.authenticate(this.state.username, this.state.password).then(() => {
      appInterface.initializeApp().then(() => {
        runtime.busy = false
        notifications.showSuccess(
          `${gettext("Welcome")}, ${session.displayName}`
        )
        if (String(window.location.pathname) === String(runtime.loginScreenUrl)) {
          routing.gotoDefault()
        }
      })
    }).catch((err) => {
      runtime.busy = false
      const statusCode: number = err.response.status
      if (statusCode === 400 || statusCode === 401) {
        notifications.showError(
          gettext('Username (Login) or password is incorrect, please try again!', 'system.aaa-messages')
        )
      } else {
        notifications.showSomeServerError()
      }
    })
  }

  private handleUsernameKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      e.stopPropagation()
      if (this.state.username === '')
        return
      this.passwordInput?.focus()
    }
  }

  render() {
    return (
      <Grid container component="main" className={'UI-LoginForm-root'}>
        <CssBaseline />
        <Grid item xs={false} sm={4} md={7} className={'UI-LoginForm-image'} style={{
          backgroundImage: `url(${routing.mediaAssetPath('system', 'authorization.jpg')})`
        }} />
        <Grid item xs={12} sm={8} md={5} component={Paper} elevation={6} square style={{
          display: 'flex',
          alignItems: 'center'
        }}>
          <div className={'UI-LoginForm-paper'}>
            <Avatar className={'UI-LoginForm-avatar'} color="secondary">
              <LockOutlinedIcon />
            </Avatar>
            <Typography component="h1" variant="h5">
              {gettext("Welcome")}
            </Typography>
            <form className={'UI-LoginForm-form'} noValidate onSubmit={this.handleSubmit}>
              <TextField
                variant="outlined"
                margin="normal"
                required
                fullWidth
                id="username"
                label={gettext("Username (Login)", 'system.aaa')}
                name="username"
                autoComplete="username"
                autoFocus
                onKeyPress={this.handleUsernameKeyPress}
                onChange={(e) => this.setState({username: e.target.value})}
                value={this.state.username}
              />
              <TextField
                variant="outlined"
                margin="normal"
                required
                fullWidth
                name="password"
                label={gettext("Password", 'system.aaa')}
                type="password"
                id="password"
                autoComplete="current-password"
                inputRef={el => this.passwordInput = el}
                onChange={(e) => this.setState({password: e.target.value})}
              />
              {runtime.rememberUsername && (
                <FormControlLabel
                  control={
                    <Checkbox
                      value="remember"
                      color="primary"
                      onChange={(e) => this.setState({remember: e.target.checked})}
                    />
                  }
                  label={gettext("Remember me", 'system.aaa')}
                />
              )}
              <div className={'UI-LoginForm-submit'}>
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  color="primary"
                  className={'css.submitbtn'}
                >
                  {gettext("Sign In", 'system.aaa')}
                </Button>
              </div>
              <Box mt={5}>
                <Copyright />
              </Box>
            </form>
          </div>
        </Grid>
      </Grid>
    );
  }
}

export const LoginForm = observer(_LoginForm)
