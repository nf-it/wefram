import React from 'react'
import {
  AppBar,
  Menu,
  MenuItem,
  IconButton,
  Toolbar,
  Typography,
  Tooltip,
} from '@material-ui/core'
import {AccountCircle} from '@material-ui/icons'
import {appInterface, runtime} from 'system/runtime'
import {ClockTime} from 'system/components'
import {aaa, session} from 'system/aaa'
import {gettext} from 'system/l10n'
import {notifications} from 'system/notification'
import {routingHistory, routing} from 'system/routing'
import './index.css'


type LayoutAppbarProps = { }
type LayoutAppbarState = {
  anchorProfileMenu: HTMLElement | null
}


export class LayoutAppbar extends React.Component<LayoutAppbarProps, LayoutAppbarState> {
  state: LayoutAppbarState = {
    anchorProfileMenu: null
  }

  handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>): void => {
    this.setState({anchorProfileMenu: event.currentTarget})
  }

  handleProfileMenuClose = (): void => {
    this.setState({anchorProfileMenu: null})
  }

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

  handleProfileSignin = () => {
    routingHistory.push(runtime.loginScreenUrl)
  }

  render() {
    return [
      <AppBar
        position="fixed"
        className={'SystemUI-LayoutAppbar'}
      >
        <Toolbar>
          <Typography variant="h6" noWrap className={'SystemUI-LayoutAppbar-title'}>
            {runtime.title}
          </Typography>
          <ClockTime />
          <Tooltip title={session.user?.fullName || gettext('Sign In', 'system.aaa')}>
            <IconButton
              edge="end"
              aria-label={session.user?.fullName || gettext('Sign In', 'system.aaa')}
              aria-controls="profileMenu"
              aria-haspopup="true"
              onClick={this.handleProfileMenuOpen}
              color="inherit"
            >
              <AccountCircle/>
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>,

      <Menu
        anchorEl={this.state.anchorProfileMenu}
        anchorOrigin={{vertical: 'top', horizontal: 'right'}}
        id="profileMenu"
        keepMounted
        transformOrigin={{vertical: 'top', horizontal: 'right'}}
        open={this.state.anchorProfileMenu !== null}
        onClose={this.handleProfileMenuClose}
        style={{
          zIndex: 65535
        }}
      >
        {session.authenticated && ([
          <MenuItem key={'appbar-menu-displayName'}>
            {session.user?.displayName}
          </MenuItem>,
          <MenuItem key={'appbar-menu-logout'} onClick={this.handleProfileLogout}>
            {gettext('Logout', 'system.aaa')}
          </MenuItem>
        ])}
        {!session.authenticated && (
          <MenuItem key={'appbar-menu-login'} onClick={this.handleProfileSignin}>
            {gettext('Sign In', 'system.aaa')}
          </MenuItem>
        )}
      </Menu>
    ]
  }
}