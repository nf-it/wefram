import React from 'react'
import {Route, Switch, Redirect} from 'react-router-dom'
import {Box} from 'system/components'
import {screensSchema} from 'build/screens'
import {Screen} from 'system/containers/Screen'
import Login from 'system/containers/Login'
import {routing} from 'system/routing'
import {session} from 'system/aaa'


type LayoutScreensProps = { }
type LayoutScreensState = { }


export class LayoutScreens extends React.Component<LayoutScreensProps, LayoutScreensState> {
  state: LayoutScreensState = {

  }

  render() {
    return (
      <Box className={'SystemUI-Layout-content'}>
          <Switch>
            {/*Routes whose not requires any permissions to be */}
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
                    component={Login}
                  />
                )
              }
            )}

            {/* Redirect to the default page if the given URL is not valid for the set routing schema*/}
            <Redirect key={'routing-screen-switch--default'} to={routing.defaultPath()}/>

          </Switch>
      </Box>
    )
  }
}
