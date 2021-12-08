import React from 'react'
import {observer} from 'mobx-react'
import {Switch, Route, Router} from 'react-router-dom'
import {createTheme, ThemeProvider} from '@mui/material/styles'
import {workspaceTheme} from './theme'
import {notificationsStore, notifications} from './notification'
import {messagesStore} from './messages'
import {dialogsStore} from './dialog'
import {LayoutSidebar} from './containers/LayoutSidebar'
import {LayoutScreens} from './containers/LayoutScreens'
import {NotificationBar} from './containers/GlobalNotify'
import {GlobalDialog} from './containers/GlobalDialog'
import {MessagesBar} from 'system/containers/Messages'
import {Relogin} from 'system/containers/Relogin'
import {LoadingGlobal} from './components'
import {Loading} from './components'
import {runtime} from './runtime'
import {routingHistory} from 'system/routing'
import Login from 'system/containers/Login'
import {aaa} from 'system/aaa'
import './main.css'


const AAA_CHECK_INTERVAL: number = 30000

type AppProps = { }
type AppState = {
  loading: boolean
}

class Main extends React.Component<AppProps, AppState> {
  state: AppState = {
    loading: true,
  }

  componentDidMount() {
    this.initializeProject()

    // setInterval(() => {
    //   aaa.check()
    //     .then(() => { /* really do nother on success */ })
    //     .catch(() => { /* really do nothing on error */ })
    // }, AAA_CHECK_INTERVAL)
  }

  private initializeProject = (): void => {
    runtime.initialize().then(() => {
      document.title = runtime.title
      this.setState({loading: false})
    }).catch(() => {
      notifications.showError('An server error occured: could not load application. Will try again in few seconds.')
      setTimeout(() => this.initializeProject(), 5000)
      return null
    })
  }

  render() {
    if (this.state.loading)
      return (
        <Loading open={this.state.loading}/>
      )

    return (
      <ThemeProvider theme={createTheme(workspaceTheme)}>
        <Router history={routingHistory}>
          <Switch>
            <Route
              exact
              key={'routing-loginscreen'}
              component={Login}
              path={runtime.loginScreenUrl}
            />
            <div className={'SystemUI-Layout-root'}>
              <LayoutSidebar />
              <LayoutScreens />
            </div>
          </Switch>
        </Router>
        <Relogin open={runtime.reloginFormOpen} />
        <LoadingGlobal busy={runtime.busy} />
        <GlobalDialog store={dialogsStore} />
        <NotificationBar store={notificationsStore} />
        <MessagesBar store={messagesStore} />
      </ThemeProvider>
    )
  }
}

export const ProjectApp = observer(Main)
