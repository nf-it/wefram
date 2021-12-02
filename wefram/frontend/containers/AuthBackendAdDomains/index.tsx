import React, {createRef} from 'react'
import {gettext} from 'system/l10n'
import {RequestApiPath} from 'system/routing'
import {api} from 'system/api'
import {ScreenProps, ActiveDirectoryDomainModel} from 'system/types'
import {
  Box,
  Dialog,
  EntityForm,
  EntityTable,
  FormPaper,
  FormCheckboxField,
  FormDigitsInputField,
  FormTextInputField,
  Typography
} from 'system/components'


const entityPath: RequestApiPath = api.entityPath('system', 'ActiveDirectoryDomain')
const objectPath: RequestApiPath = api.entityObjectPath('system', 'ActiveDirectoryDomain')

type ScreenState = {
  entityKey?: string | null
}

export type CardProps = {
  entityKey: string | null
  onAfterDelete: () => void
  onAfterSubmit: () => void
  onClose: () => void
}

type CardState = {
  data: ActiveDirectoryDomainModel
}

class Card extends React.Component<CardProps, CardState> {
  state: CardState = {
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
        <FormPaper spacingAfter={2}>
          <FormCheckboxField
            formName={'enabled'}
            label={gettext("The domain is in use", 'system.aaa')}
            width={8}
          />
          <FormDigitsInputField
            formName={'sort'}
            label={gettext("Order")}
            required
            width={4}
          />
        </FormPaper>

        <FormPaper spacingBefore={2} spacingAfter={1}>
          <FormTextInputField
            error={this.state.data.name === ''}
            formName={'name'}
            label={gettext("Name")}
            required
            width={12}
          />
          <FormTextInputField
            error={this.state.data.domain === ''}
            formName={'domain'}
            label={gettext("Domain", 'system.aaa')}
            required
            placeholder={'mydomain.ru'}
            width={12}
          />
          <FormTextInputField
            formName={'server'}
            label={gettext("Active Directory server (optional)", 'system.aaa')}
            placeholder={'dc.mydomain.ru'}
            width={12}
          />
        </FormPaper>
      </EntityForm>
    )
  }
}


export default class Screen extends React.Component<ScreenProps, ScreenState> {
  state: ScreenState = {
    entityKey: undefined
  }

  private listRef = createRef<EntityTable>()

  render() {
    return (
      <React.Fragment>
        <Box mt={2}>
          <Typography variant={'h4'} paddingBottom={2}>
            {gettext("Administrate Active Directory domains", 'system.aaa')}
          </Typography>
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
            <Card
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


