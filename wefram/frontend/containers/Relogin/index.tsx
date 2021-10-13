import React from 'react'
import {runInAction} from 'mobx'
import {gettext} from 'system/l10n'
import {aaa, session} from 'system/aaa'
import {runtime} from 'system/runtime'
import {routing} from 'system/routing'
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  TextField
} from 'system/components'
import {notifications} from 'system/notification'


export type ReloginProps = {
  open: boolean
}

type ReloginState = {
  password: string
}


export class Relogin extends React.Component<ReloginProps, ReloginState> {
  state: ReloginState = {
    password: ''
  }

  private submit = (): void => {
    if (this.state.password === '')
      return

    const username: string | undefined = session.user?.login
    if (username === undefined) {
      routing.gotoLogin()
      return
    }

    this.setState({password: ''})

    runtime.setBusy()
    aaa.authenticate(username, this.state.password).then(() => {
      runtime.initialize().then(() => {
        runtime.dropBusy()
        notifications.showSuccess(
          `${gettext("Welcome")}, ${session.displayName}`
        )
        runInAction(() => runtime.reloginFormOpen = false)
      })
    }).catch((err) => {
      runtime.dropBusy()
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

  render() {
    return (
      <Dialog open={this.props.open} maxWidth={'sm'}>
        <DialogTitle>{gettext("Authentication", 'system.aaa')}</DialogTitle>
        <DialogContent>
          <DialogContentText variant={'h4'} color={'primary'} gutterBottom>
            {session.displayName}
          </DialogContentText>
          <DialogContentText gutterBottom variant={'body2'} color={'textPrimary'}>
            {gettext("Your session is over. Please enter your password to continue.", 'system.aaa')}
          </DialogContentText>
          <Box mt={3} mb={3}>
            <TextField
              autoFocus
              variant={'outlined'}
              label={gettext("Password", 'system.aaa')}
              value={this.state.password}
              fullWidth
              type={'password'}
              onKeyDown={(ev: React.KeyboardEvent<HTMLInputElement>) => {
                if (ev.key === 'Enter') {
                  ev.preventDefault()
                  ev.stopPropagation()
                  this.submit()
                }
              }}
              onChange={(ev: React.ChangeEvent<HTMLInputElement>) => this.setState({password: ev.target.value})}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button
            color={'secondary'}
            onClick={() => {
              runInAction(() => runtime.reloginFormOpen = false)
              routing.gotoLogin()
            }}
          >
            {gettext("Another user", 'system.aaa')}
          </Button>
          <Button
            color={'primary'}
            variant={'outlined'}
            onClick={() => this.submit()}
          >
            {gettext("Sign In", 'system.aaa')}
          </Button>
        </DialogActions>
      </Dialog>
    )
  }
}
