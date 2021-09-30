import React from 'react'
import {
  AppBar,
  Box,
  Collapse,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Toolbar,
  Tooltip,
  Typography
} from 'system/components'
import {
  AccountCircle,
  ExpandLess,
  ExpandMore
} from '@mui/icons-material'
import {Link, Redirect, Route, Switch} from 'react-router-dom'
import {observer} from 'mobx-react'
import {LoginScreen} from '../LoginScreen'
import {aaa, session} from 'system/aaa'
import {gettext} from 'system/l10n'
import {ClockTime} from 'system/components'
import {screensSchema} from 'build/screens'
import {Screen} from '../Screen'
import {notifications} from 'system/notification'
import {routingHistory, routing} from 'system/routing'
import {runtime} from 'system/runtime'
import './index.css'


type TSitemapFolderOpen = Record<string, boolean>

type P = { }
type S = {
  anchorProfileMenu: HTMLElement | null
  sitemapFolderOpen: TSitemapFolderOpen
}

class _BaseLayout extends React.Component<P, S> {
  state: S = {
    anchorProfileMenu: null,
    sitemapFolderOpen: { }
  }

  handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    this.setState({anchorProfileMenu: event.currentTarget})
  }

  handleProfileMenuClose = () => {
    this.setState({anchorProfileMenu: null})
  }

  handleProfileLogout = () => {
    runtime.setBusy()
    aaa.logout()
    this.setState({anchorProfileMenu: null})
    notifications.showSuccess(gettext('You have been logged out. Good bye.', 'system.aaa-messages'))
    runtime.initialize().then(() => {
      runtime.dropBusy()
      routing.gotoDefault()
    })
  }

  handleProfileSignin = () => {
    routingHistory.push(runtime.loginScreenUrl)
  }

  handleSitemapFolderClick = (event: React.MouseEvent<HTMLElement>) => {
    const key: string = String(event.currentTarget.dataset.key)
    const sitemapFolderOpen: TSitemapFolderOpen = this.state.sitemapFolderOpen
    if (typeof sitemapFolderOpen[key] === 'undefined') {
      sitemapFolderOpen[key] = true
    } else {
      sitemapFolderOpen[key] = !sitemapFolderOpen[key]
    }
    this.setState({sitemapFolderOpen})
  }

  render() {
    return (
      <div className={'SystemUI-LayoutSitemap-root'}>
        <AppBar
            position="fixed"
            className={'SystemUI-LayoutSitemap-appbar'}
        >
          <Toolbar>
            <Typography variant="h6" noWrap className={'SystemUI-LayoutSitemap-title'}>
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
        </AppBar>

        <Menu
          anchorEl={this.state.anchorProfileMenu}
          anchorOrigin={{vertical: 'top', horizontal: 'right'}}
          id="profileMenu"
          keepMounted
          transformOrigin={{vertical: 'top', horizontal: 'right'}}
          open={this.state.anchorProfileMenu !== null}
          onClose={this.handleProfileMenuClose}
        >
          {session.authenticated && ([
            <MenuItem key={'appbar-menu-displayName'}>{session.user?.displayName}</MenuItem>,
            <MenuItem key={'appbar-menu-logout'} onClick={this.handleProfileLogout}>{gettext('Logout', 'system.aaa')}</MenuItem>
          ])}
          {!session.authenticated && (
            <MenuItem key={'appbar-menu-login'} onClick={this.handleProfileSignin}>{gettext('Sign In', 'system.aaa')}</MenuItem>
          )}
        </Menu>

        <Drawer
          className={'SystemUI-LayoutSitemap-sitemap'}
          variant="permanent"
          classes={{
            paper: 'SystemUI-LayoutSitemap-sitemap-paper',
          }}
          style={{
            backgroundColor: '#253043',
            color: '#eee'
          }}
        >
          <Toolbar />

          <div className={'SystemUI-LayoutSitemap-sitemap-container'}>
            <Divider/>
            <List>
              {runtime.sitemap.map(item => (
                <Box key={`sitemap-item-${item.name}`}>
                  {item.children !== null && item.children?.length > 0 && (
                    <React.Fragment>
                      <ListItem
                        button
                        key={item.name}
                        data-key={item.name}
                        onClick={this.handleSitemapFolderClick}
                        className={'SystemUI-LayoutSitemap-sitemap-item'}
                      >
                        <ListItemIcon style={{color: '#89a'}}>{item.icon !== null && (<div className={'ICON'} />)}</ListItemIcon>
                        <ListItemText primary={item.caption}/>
                        {this.state.sitemapFolderOpen[item.name] ? <ExpandLess/> : <ExpandMore/>}
                      </ListItem>
                      <Collapse
                        in={this.state.sitemapFolderOpen[item.name]}
                        timeout="auto"
                        unmountOnExit
                        className={'SystemUI-LayoutSitemap-sitemap-folder'}
                      >
                        <List component="div" disablePadding>
                          {item.children.map(child => (
                            <Link to={screensSchema[child.screen]?.routeUrl} className={'SystemUI-LayoutSitemap-sitemap-item'}>
                              <ListItem
                                  button
                                  key={child.name}
                                  data-key={child.name}
                                  dense
                                  style={{
                                    backgroundColor: 'inherit'
                                  }}
                              >
                                <ListItemIcon style={{color: '#789'}}>{child.icon !== null && (<div className={'ICON'} />)}</ListItemIcon>
                                <ListItemText primary={child.caption}/>
                              </ListItem>
                            </Link>
                          ))}
                        </List>
                      </Collapse>
                    </React.Fragment>
                  )}
                  {item.children === null && (
                    <Link to={screensSchema[item.screen]?.routeUrl} className={'SystemUI-LayoutSitemap-sitemap-item'}>
                      <ListItem
                        button
                        key={item.name}
                        data-key={item.name}
                        style={{
                          backgroundColor: 'inherit'
                        }}
                      >
                        <ListItemIcon style={{color: '#89a'}}>{item.icon !== null && (<div className={'ICON'} />)}</ListItemIcon>
                        <ListItemText primary={item.caption}/>
                      </ListItem>
                    </Link>
                  )}
                </Box>
              ))}
            </List>
          </div>
        </Drawer>

        <main className={'SystemUI-LayoutSitemap-content'}>
          <Switch>

            {/* Routes whose not requires any permissions to be */}
            {Object.keys(screensSchema).filter(
              name => !screensSchema[name].requires.length
            ).map(name => {
                const screenSchema = screensSchema[name]
                return (
                  <Route
                    exact
                    key={`routing-screen-switch-${name}`}
                    path={screenSchema.routeUrl}
                    render={
                      (props) => <Screen
                        name={screenSchema.name}
                        rootComponent={screenSchema.rootComponent || undefined}
                        requires={screenSchema.requires}
                        routeUrl={screenSchema.routeUrl}
                        routeParams={screenSchema.routeParams}
                        params={screenSchema.params}
                        {...props}
                      />
                    }
                  />
                )
              }
            )}

            {/* Routes whose requires user to be logged in and have according permissions */}
            {session.authenticated && Object.keys(screensSchema).filter(
              name => screensSchema[name].requires.length && session.permitted(screensSchema[name].requires)
            ).map(name => {
                const screenSchema = screensSchema[name]
                return (
                  <Route
                    exact
                    key={`routing-screen-switch-${name}`}
                    path={screenSchema.routeUrl}
                    render={
                      (props) => <Screen
                        name={screenSchema.name}
                        rootComponent={screenSchema.rootComponent || undefined}
                        requires={screenSchema.requires}
                        routeUrl={screenSchema.routeUrl}
                        routeParams={screenSchema.routeParams}
                        params={screenSchema.params}
                        {...props}
                      />
                    }
                  />
                )
              }
            )}

            {/* Service routes whose displays login screen if the screen requires user to be logged in  */}
            {!session.authenticated && Object.keys(screensSchema).filter(
              name => !session.permitted(screensSchema[name].requires)
            ).map(name => {
                const screenSchema = screensSchema[name]
                return (
                  <Route
                    exact
                    key={`routing-screen-switch-${name}`}
                    path={screenSchema.routeUrl}
                    component={LoginScreen}
                  />
                )
              }
            )}

            {/* Redirect to the default page if the given URL is not valid for the set routing schema*/}
            <Redirect key={'routing-screen-switch--default'} to={routing.defaultPath()}/>

          </Switch>
        </main>
      </div>
    )
  }
}

export const BaseLayout = observer(_BaseLayout)
