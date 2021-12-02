import React from 'react'
import {
  Box,
  Button,
  CircularProgress,
  Divider,
  Grid,
  FormCommonField,
  LoadingLinear,
  MaterialIcon,
  Paper,
  Tab,
  Tabs,
  TitlebarControl,
  Typography
} from 'system/components'
import {
  ScreenProps,
  SettingsSchema,
  SettingsPropsValuesUpdate,
  SettingsTabSchema,
  SettingsEntity,
  FormCommonFieldItem
} from 'system/types'
import {gettext} from 'system/l10n'
import {api} from 'system/api'
import {notifications} from 'system/notification'
import {RequestApiPath} from 'system/routing'
import './index.css'


type CtrlState = Record<string, any>

type ScreenState = {
  loading: boolean
  submitting: boolean
  schema: SettingsSchema
  values: SettingsPropsValuesUpdate
  ctrls: CtrlState
  tabInsight: number
}

type PropCaptionProps = {
  caption: string
  pt?: number
  pb?: number
}

type SectionCaptionProps = {
  caption: string
}

const apiUrl: RequestApiPath = api.path('system', '/settings/properties', 1)


class PropCaption extends React.Component<PropCaptionProps> {
  render() {
    return (
      <Box pt={this.props.pt ?? 1} pb={this.props.pb ?? 1}>
        <Typography style={{fontSize: '.8rem', color: '#456'}}>{this.props.caption}</Typography>
      </Box>
    )
  }
}


class SectionCaption extends React.Component<SectionCaptionProps> {
  render() {
    return (
      <Typography
        variant={'h6'}
        color={'primary'}
        style={{
          marginBottom: '16px',
          fontWeight: 400,
          textTransform: 'uppercase',
          padding: '.5vmax',
          backgroundColor: '#0070f0dd',
          borderRadius: '.5vmax',
          color: '#fff'
        }}
      >{this.props.caption}</Typography>
    )
  }
}


export default class Screen extends React.Component<ScreenProps> {
  state: ScreenState = {
    loading: true,
    submitting: false,
    schema: [],
    values: {},
    ctrls: {},
    tabInsight: 0
  }

  componentDidMount() {
    this.load()
  }

  load = (): void => {
    api.get(apiUrl).then(res => {
      this.setState({
        loading: false,
        submitting: false,
        schema: res.data,
        values: {}
      })
    }).catch(err => {
      this.setState({loading: false})
      notifications.showRequestError(err)
    })
  }

  handleTabChange = (event: React.ChangeEvent<{}>, newValue: number): void => {
    this.setState({tabInsight: newValue})
  }

  handleUpdateValue = (entityName: string, propName: string, newValue: any): void => {
    const values: SettingsPropsValuesUpdate = this.state.values
    values[entityName] = values[entityName] ?? {}
    values[entityName][propName] = newValue
    this.setState({values})
  }

  handleSubmit = (): void => {
    this.setState({submitting: true})
    console.dir(this.state.values)
    api.post(apiUrl, this.state.values).then(res => {
      this.load()
      notifications.showRequestSuccess(res)
    }).catch(err => {
      this.setState({submitting: false})
      notifications.showRequestError(err)
    })
  }

  render() {
    if (this.state.loading) {
      return (
        <LoadingLinear/>
      )
    }

    if (!this.state.schema.length)
      return null

    return (
      <Box mt={1}>
        <TitlebarControl title={gettext("Properties and settings", 'system.settings')} mb={3}>
          <Button
            color={'primary'}
            disabled={!Object.keys(this.state.values).length}
            variant={'contained'}
            startIcon={
              this.state.submitting
                ? <CircularProgress size={20} />
                : <MaterialIcon icon={'done'} />
            }
            onClick={this.handleSubmit}
            style={{marginLeft: '8px'}}
          >{gettext("Save")}</Button>
        </TitlebarControl>
        <Grid container style={{alignItems: 'flex-start'}}>
          <Grid item xs={2} className={'SystemUI-Box-GrayPanel'}>
            <Tabs
              orientation={'vertical'}
              variant={'scrollable'}
              value={this.state.tabInsight}
              onChange={this.handleTabChange}
            >
              {this.state.schema.map((appSchema: SettingsTabSchema, index: number) => (
                <Tab
                  id={`system-proptabs-tabsw-${index}`}
                  label={appSchema.tabCaption}
                  value={index}
                  disableFocusRipple
                  wrapped
                  style={{
                    maxWidth: 'none',
                    alignItems: 'flex-start',
                    textAlign: 'left'
                  }}
                />
              ))}
            </Tabs>
          </Grid>
          <Grid item xs={10}>
            {this.state.schema.map((appSchema: SettingsTabSchema, appIndex: number) => (
              <Box hidden={appIndex !== this.state.tabInsight} pl={2}>
                {appIndex === this.state.tabInsight && (
                  <React.Fragment>
                    {appSchema.entities.map((entity: SettingsEntity, entityIndex: number) => (
                      <Paper
                        variant={'outlined'}
                        style={{
                          marginBottom: entityIndex < (appSchema.entities.length - 1) ? '24px' : undefined
                        }}
                      >
                        <Box p={2}>
                          {(entity.caption ?? '') !== '' && (
                            <SectionCaption caption={entity.caption ?? ''} />
                          )}
                          <Box>
                            {entity.properties.map((prop: FormCommonFieldItem, propIndex: number) => {

                              const updatedValue: any = this.state.values[entity.name] !== undefined
                                ? this.state.values[entity.name][prop.name]
                                : undefined
                              const value: any = updatedValue !== undefined ? updatedValue : prop.value
                              return (
                                <React.Fragment>
                                  {propIndex !== 0 && (
                                    <Divider/>
                                  )}
                                  <FormCommonField
                                    field={prop}
                                    value={value}
                                    updatedValue={updatedValue}
                                    onChange={(propName: string, newValue: any) => {
                                      this.handleUpdateValue(entity.name, propName, newValue)
                                    }}
                                  />
                                </React.Fragment>
                              )
                            })}
                          </Box>
                        </Box>
                      </Paper>
                    ))}
                  </React.Fragment>
                )}
              </Box>
            ))}
          </Grid>
        </Grid>
      </Box>
    )
  }
}

