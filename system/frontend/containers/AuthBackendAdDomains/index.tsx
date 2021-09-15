import React, {createRef} from 'react'
import {gettext} from 'system/l10n'
import {RequestApiPath} from 'system/routing'
import {api} from 'system/api'
import {ScreenProps, ActiveDirectoryDomainModel} from 'system/types'
import {
  Box,
  Checkbox,
  Dialog,
  DigitsInputField,
  EntityForm,
  EntityTable,
  Grid,
  FormControlLabel,
  TextField,
  Typography
} from 'system/components'


const entityPath: RequestApiPath = api.entityPath('system', 'ActiveDirectoryDomain')
const objectPath: RequestApiPath = api.entityObjectPath('system', 'ActiveDirectoryDomain')

type AuthBackendAdDomainsState = {
  entityKey?: string | null
}

export type DomainCardProps = {
  entityKey: string | null
  onAfterDelete: () => void
  onAfterSubmit: () => void
  onClose: () => void
}

type DomainCardState = {
  data: ActiveDirectoryDomainModel
}

class DomainCard extends React.Component<DomainCardProps, DomainCardState> {
  state: DomainCardState = {
    data: {
      id: null,
      enabled: true,
      sort: 0,
      name: '',
      domain: '',
      server: ''
    }
  }

  render() {
    const key: string | null = this.props.entityKey
    return (
      <EntityForm
        entityKey={key}
        requestPath={objectPath}

        data={this.state.data}
        onUpdateData={(data, cb) => this.setState({data}, cb)}
        requiredForSubmit={[
          'name',
          'domain'
        ]}
        submitFieldsModel={[
          'enabled',
          'sort',
          'name',
          'domain',
          'server'
        ]}

        submit
        delete={key !== null}
        title={key === null ? gettext("New domain", 'system.aaa') : this.state.data.name}
        windowed

        onAfterDelete={this.props.onAfterDelete}
        onAfterSubmit={this.props.onAfterSubmit}
        onClose={this.props.onClose}
      >
        <Box mt={2} mb={2}>
          <Grid container spacing={1}>
            <Grid item xs={8}>
              <FormControlLabel control={
                <Checkbox
                  id={'enabled'}
                  defaultChecked={this.state.data.enabled}
                />
              } label={gettext("The domain is in use", 'system.aaa')} />
            </Grid>
            <Grid item xs={4}>
              <DigitsInputField
                name={'sort'}
                label={gettext("Order")}
                required
                fullWidth
                defaultValue={this.state.data.sort}
              />
            </Grid>
          </Grid>

        </Box>
        <Box mt={2} mb={2}>
          <TextField
            error={this.state.data.name === ''}
            name={'name'}
            label={gettext("Name")}
            required
            fullWidth
            defaultValue={this.state.data.name} />
        </Box>
        <Box mt={2} mb={2}>
          <TextField
            error={this.state.data.domain === ''}
            name={'domain'}
            label={gettext("Domain", 'system.aaa')}
            required
            fullWidth
            placeholder={'mydomain.ru'}
            defaultValue={this.state.data.domain} />
        </Box>
        <Box mt={2} mb={2}>
          <TextField
            name={'server'}
            label={gettext("Active Directory server (optional)", 'system.aaa')}
            required
            fullWidth
            placeholder={'dc.mydomain.ru'}
            defaultValue={this.state.data.server} />
        </Box>
      </EntityForm>
    )
  }
}


export default class AuthBackendAdDomains extends React.Component<ScreenProps, AuthBackendAdDomainsState> {
  state: AuthBackendAdDomainsState = {
    entityKey: undefined
  }

  private listRef = createRef<EntityTable>()

  render() {
    return (
      <React.Fragment>
        <Box mt={2}>
          <Typography variant={'h4'}>{gettext("Administrate Active Directory domains", 'system.aaa')}</Typography>
          <EntityTable
            ref={this.listRef}

            addButtonAction={() => this.setState({entityKey: null})}
            columns={[
              {fieldName: 'enabled', fieldType: 'boolean'},
              {fieldName: 'name', caption: gettext("Name")},
              {fieldName: 'domain', caption: gettext("Domain", 'system.aaa')},
              {fieldName: 'server', caption: gettext("Server", 'system.aaa')}
            ]}
            deleteButton={true}
            entityCaption={gettext("Domains list", 'system.aaa')}
            selectable
            requestPath={entityPath}
            onItemClick={(item: any) => {
              this.setState({entityKey: item.id})
            }}
          />
        </Box>
        <Dialog open={this.state.entityKey !== undefined} maxWidth={'sm'}>
          {this.state.entityKey !== undefined && (
            <DomainCard
              entityKey={this.state.entityKey}
              onClose={() => {
                this.setState({entityKey: undefined})
              }}
              onAfterDelete={() => {
                this.listRef.current?.update()
                this.setState({entityKey: undefined})
              }}
              onAfterSubmit={() => {
                this.listRef.current?.update()
                this.setState({entityKey: undefined})
              }}
            />
          )}
        </Dialog>
      </React.Fragment>
    )
  }
}


