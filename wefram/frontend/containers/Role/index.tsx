import React from 'react'
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Box,
  Checkbox,
  EntityForm,
  FormPaper,
  FormItem,
  FormTextInput,
  FormControlLabel,
  LoadingLinear,
  OptionsList,
  Paper,
  Typography, TranslatedChapter, Chapters, MaterialIcon
} from 'system/components'
import {RoleEditModel, ScreenProps} from 'system/types'
import {gettext} from 'system/l10n'
import {api} from 'system/api'
import {RequestApiPath, routing} from 'system/routing'
import {notifications} from 'system/notification'


const Help = () => (
  <Chapters>
    <TranslatedChapter appName={'system'} caption={gettext("Roles", 'system')} textId={'help_rolecard'} />
  </Chapters>
)

const apiVersion: number = 1
const containerPath: RequestApiPath = {
  app: 'system',
  path: 'container/Role',
  version: apiVersion
}
const objectPath: RequestApiPath = api.entityObjectPath('system', 'Role')


type ScontainerPermission = {
  key: string
  caption: string
}

type ContainerAppPermission = {
  app: string
  caption: string
  permissions: ScontainerPermission[]
}

type ContainerAppPermissions = ContainerAppPermission[]

type Container = {
  permissions: ContainerAppPermissions
}

type ScreenState = {
  loading: boolean
  data: RoleEditModel
  container?: Container
}

export default class Screen extends React.Component<ScreenProps, ScreenState> {
  state: ScreenState = {
    loading: true,
    data: {
      id: null,
      name: '',
      permissions: [],
      users: []
    }
  }

  componentDidMount() {
    this.instantiate()
  }

  private instantiate = (): void => {
    api.get(containerPath).then(res => {
      this.setState({
        container: res.data,
        loading: false
      }, () => console.log(this.state.container))
    }).catch(err => {
      notifications.showRequestError(err)
      routing.back()
    })
  }

  private get entityKey(): string | null {
    const key: string | undefined = (this.props.match.params as Record<string, string>).key
    if (!key)
      return null
    if (key === 'new')
      return null
    return key
  }

  render() {
    if (this.state.loading) {
      return (
        <LoadingLinear/>
      )
    }

    const key: string | null = this.entityKey
    return (
      <EntityForm
        entityKey={key}
        requestPath={objectPath}

        data={this.state.data}
        help={<Help />}
        onUpdateData={(data, cb) => this.setState({data}, cb)}
        requiredForSubmit={['name']}

        submit
        delete={key !== null}
      >
        <Typography variant={'h4'}>
          {key === null ? gettext("New role", 'system.aaa-form') : this.state.data.name}
        </Typography>

        <FormPaper spacing={4}>

          {/* Left (general) side */}
          <FormItem width={7}>
            <Paper elevation={1}>
              <Box p={2}>
                <FormTextInput
                  formName={'name'}
                  label={gettext("Role name", 'system.aaa-form')} />
              </Box>
            </Paper>

            <Box mt={3}>
              <Box pb={1}>
                <Typography variant={'h5'}>{gettext("Permissions for the role", 'system.aaa-form')}</Typography>
              </Box>
              {this.state.container?.permissions.map(app => (
                <Accordion defaultExpanded={false}>
                  <AccordionSummary expandIcon={
                    <MaterialIcon icon={'expand_more'} />
                  }>
                    <Typography>{app.caption}</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box>
                      {app.permissions.map(perm => (
                        <Box>
                          <FormControlLabel
                            control={
                              <Checkbox
                                defaultChecked={Boolean(this.state.data.permissions?.includes(perm.key))}
                                onChange={(ev) => {
                                  const data = this.state.data
                                  const permissions: string[] =
                                    (data.permissions || []).filter((e: string) => e !== perm.key)
                                  const checked: boolean = ev.target.checked
                                  if (checked) {
                                    permissions.push(perm.key)
                                  }
                                  data.permissions = permissions
                                  this.setState({data})
                                }}
                              />
                            }
                            label={perm.caption}/>
                        </Box>
                      ))}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          </FormItem>

          {/* Right (users) side */}
          <FormItem width={5}>
            <Paper elevation={1}>
              <Box p={2}>
                <Box mb={2}>
                  <Typography variant={'h5'}>{gettext("Role's users", 'system.aaa')}</Typography>
                </Box>
                <OptionsList
                  defaultValues={this.state.data.users}
                  resolveItemsPath={api.path('system', 'User/resolve')}
                  searchItemsPath={api.path('system', 'User')}
                  onChange={values => {
                    const data = this.state.data
                    data.users = values
                    this.setState({data})
                  }}
                />
              </Box>
            </Paper>
          </FormItem>
        </FormPaper>
      </EntityForm>
    )
  }
}
