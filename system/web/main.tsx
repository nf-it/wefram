import React from 'react'
import ReactDOM from 'react-dom'
import {observer} from 'mobx-react'
import {Link, Switch, Route, Router} from 'react-router-dom'
import {createTheme, ThemeProvider} from '@material-ui/core/styles'
import {Box} from '@material-ui/core'
import {defaultTheme} from './theme'
import {notificationsStore} from './notification'
import {dialogsStore} from './dialog'
import {LayoutAppbar} from './containers/LayoutAppbar'
import {LayoutSitemap} from './containers/LayoutSitemap'
import {LayoutScreens} from './containers/LayoutScreens'
import {NotificationBar} from './containers/GlobalNotify'
import {GlobalDialog} from './containers/GlobalDialog'
import {Relogin} from 'system/containers/Relogin'
import {LoadingGlobal} from './components'
import {Loading} from './components'
import {runtime, appInterface} from './runtime'
import {notifications} from './notification'
import {routingHistory} from 'system/routing'
import {LoginScreen} from 'system/containers/LoginScreen'
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
    this.initializeApp()

    setInterval(() => {
      aaa.check().finally()
    }, AAA_CHECK_INTERVAL)
  }

  initializeApp = () => {
    appInterface.initializeApp().then(() => {
      document.title = runtime.title
      this.setState({loading: false})
    }).catch(() => {
      notifications.showError('An server error occured: could not load application. Will try again in few seconds.')
      setTimeout(() => this.initializeApp(), 5000)
      return null
    })
  }

  render() {
    if (this.state.loading)
      return (
        <Loading open={this.state.loading}/>
      )

    return (
      <ThemeProvider theme={createTheme(defaultTheme, runtime.muiLocalization)}>
        <Router history={routingHistory}>
          <Switch>
            <Route
              exact
              key={'routing-loginscreen'}
              component={LoginScreen}
              path={runtime.loginScreenUrl}
            />
            <Box className={'SystemUI-Layout-root'}>
              <LayoutAppbar />
              <LayoutSitemap />
              <LayoutScreens />
            </Box>
          </Switch>
        </Router>
        <Relogin open={runtime.reloginFormOpen} />
        <LoadingGlobal runtime={runtime} />
        <GlobalDialog store={dialogsStore} />
        <NotificationBar store={notificationsStore} />
      </ThemeProvider>
    )
  }
}

const App = observer(Main)

ReactDOM.render(
  <App />,
  document.getElementById('root')
)
