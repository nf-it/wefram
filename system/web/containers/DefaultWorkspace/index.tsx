import React from 'react'
import {ScreenProps} from 'system/types'
import {
  Box,
  Button,
  ButtonLink,
  Typography
} from 'system/components'
import LoginIcon from '@material-ui/icons/LockOpen'
import LogoffIcon from '@material-ui/icons/ExitToApp'
import {appInterface, runtime} from 'system/runtime'
import {aaa, session} from 'system/aaa'
import {gettext} from 'system/l10n'
import {notifications} from 'system/notification'
import {routing} from 'system/routing'


export default class Workspace extends React.Component<ScreenProps> {
  handleProfileLogout = () => {
    runtime.busy = true
    aaa.logout()
    this.setState({anchorProfileMenu: null})
    notifications.showSuccess(gettext('You have been logged out. Good bye.', 'system.aaa-messages'))
    appInterface.initializeApp().then(() => {
      runtime.busy = false
      routing.gotoDefault()
    })
  }

  render() {
    return (
      <React.Fragment>
        <Box mt={3} mb={3}>
          <Typography
            variant={'h2'}
            style={{
              borderBottom: '2px solid #1976d2',
              paddingBottom: '8px'
            }}
          >{gettext("Welcome")}</Typography>
          <Box mt={1} display={'flex'} alignItems={'center'}>
            {session.authenticated ? (
              <React.Fragment>
                <Typography
                  variant={'h4'}
                  color={'primary'}
                  style={{
                    fontWeight: 300
                  }}
                >{session.displayName}</Typography>
                <Button
                  color={'primary'}
                  variant={'outlined'}
                  endIcon={<LogoffIcon />}
                  style={{
                    marginLeft: '24px'
                  }}
                  onClick={this.handleProfileLogout}
                >
                  {gettext('Logout', 'system.aaa')}
                </Button>
              </React.Fragment>
            ) : (
              <React.Fragment>
                <ButtonLink
                  to={runtime.loginScreenUrl}
                  startIcon={<LoginIcon />}
                  variant={'contained'}
                  color={'primary'}
                >{gettext("Sign In", 'system.aaa')}</ButtonLink>
                <Typography style={{marginLeft: '1rem'}}>
                  {gettext("click here to sign in", 'system.aaa')}
                </Typography>
              </React.Fragment>
            )}
          </Box>
        </Box>
      </React.Fragment>
    )
  }
}
