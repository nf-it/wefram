import React from 'react'
import {
  DateTimeText,
  Divider,
  Grid,
  Box,
  EntityForm,
  Paper,
  PasswordSetter,
  FormControlLabel,
  StaticText,
  Switch,
  TextField
} from 'system/components'
import {gettext} from 'system/l10n'
import {api} from 'system/api'
import {RequestApiPath} from 'system/routing'
import {session} from 'system/aaa'


const objectPath: RequestApiPath = api.entityObjectPath('system', 'User')

export type UserCardProps = {
  entityKey: string | null
  onAfterDelete: () => void
  onAfterSubmit: () => void
  onClose: () => void
}

type UserCardState = {
  data: any
}

export class UserCard extends React.Component<UserCardProps, UserCardState> {
  state: UserCardState = {
    data: {
      id: null,
      login: '',
      secret: null,
      locked: false,
      createdAt: null,
      lastLogin: null,
      firstName: "",
      middleName: "",
      lastName: "",
      timezone: null,
      locale: null,
      fullName: ""
    }
  }

  render() {
    const key: string | null = this.props.entityKey
    const requiredForSubmit: string[] =
      key === null
      ? ['login', 'firstName', 'secret']
      : ['login', 'firstName']

    return (
      <EntityForm
        entityKey={key}
        requestPath={objectPath}

        data={this.state.data}
        onUpdateData={(data, cb) => this.setState({data}, cb)}
        requiredForSubmit={requiredForSubmit}
        submitFieldsModel={[
          'login',
          'secret',
          'locked',
          'firstName',
          'middleName',
          'lastName',
          'timezone',
          'locale'
        ]}

        submit
        delete={key !== null && (String(session.user?.id) !== String(key))}
        title={key === null ? gettext("New user", 'system.aaa-form') : this.state.data.fullName}
        windowed

        onAfterDelete={this.props.onAfterDelete}
        onAfterSubmit={this.props.onAfterSubmit}
        onClose={this.props.onClose}
      >
        {key !== null && (
          <Paper variant={'outlined'} style={{height: '100%'}}>
            <Box p={2}>
              <Grid container>
                <Grid item xs={6}>
                  <StaticText
                    caption={gettext("Last logon time", 'system.aaa-form')}
                  >
                    <DateTimeText value={this.state.data.lastLogin} />
                  </StaticText>
                </Grid>
                <Grid item xs={6}>
                  <StaticText
                    caption={gettext("Created at")}
                  >
                    <DateTimeText value={this.state.data.createdAt} />
                  </StaticText>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        )}

        <Box>
          <Box pt={2} pb={2}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  error={this.state.data.login === ''}
                  name={'login'}
                  label={gettext("Login", 'system.aaa-form')}
                  required
                  fullWidth
                  style={{flexGrow: 5}}
                  defaultValue={this.state.data.login} />
              </Grid>
              <Grid item xs={6}>
                <FormControlLabel
                  control={
                    <Switch
                      id={'locked'}
                      defaultChecked={this.state.data.locked}
                      disabled={String(session.user?.id) === String(key)}
                    />
                  }
                  label={gettext("Is locked", 'system.aaa-form')} />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  name={'lastName'}
                  label={gettext("Last name", 'system.aaa-form')}
                  fullWidth
                  defaultValue={this.state.data.lastName} />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  error={this.state.data.firstName === ''}
                  name={'firstName'}
                  label={gettext("First name", 'system.aaa-form')}
                  required
                  fullWidth
                  defaultValue={this.state.data.firstName} />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  name={'middleName'}
                  label={gettext("Middle name", 'system.aaa-form')}
                  fullWidth
                  defaultValue={this.state.data.middleName} />
              </Grid>
            </Grid>
          </Box>

          <Divider className={'mt-3 mb-2'} />

          <Box pt={2} pb={2}>
            {key !== null && (
              <Box fontSize={'.9rem'}>
                {gettext("Type a new password to change it for the user", 'system.aaa-form')}
              </Box>
            )}
            <Grid container spacing={4}>
              <PasswordSetter
                labelPassword={gettext("Password", 'system.aaa-form')}
                labelConfirmation={gettext("Password confirmation", 'system.aaa-form')}
                name={'secret'}
              />
            </Grid>
            {key === null && (this.state.data.secret === null || this.state.data.secret === '') && (
              <Box mt={2} mb={2} fontSize={'.9rem'} color={'red'}>
                {gettext("Password required to be set for the new user", 'system.aaa-form')}
              </Box>
            )}
          </Box>
        </Box>
      </EntityForm>
    )
  }
}

