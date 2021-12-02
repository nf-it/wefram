import React from 'react'
import {
  EntityForm,
  FormPaper,
  FormCheckboxField,
  FormPasswordSetterField,
  FormTextInputField
} from 'system/components'
import {gettext} from 'system/l10n'
import {api} from 'system/api'
import {RequestApiPath} from 'system/routing'
import {MailAccountModel} from 'system/types'


const objectPath: RequestApiPath = api.entityObjectPath('system', 'MailAccount')


type CardProps = {
  entityKey: string | null
  onAfterDelete: () => void
  onAfterSubmit: () => void
  onClose: () => void
}

type CardState = {
  data: MailAccountModel
}

export default class Card extends React.Component<CardProps, CardState> {
  state: CardState = {
    data: {
      id: null,
      name: '',
      snd_host: '',
      snd_port: 0,
      rcv_host: '',
      rcv_port: 0,
      use_imap: true,
      use_tls: true,
      username: '',
      password: ''
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
        requiredForSubmit={['name']}
        submitFieldsModel={[
          'name',
          'snd_host',
          'snd_port',
          'rcv_host',
          'rcv_port',
          'use_imap',
          'use_tls',
          'username',
          'password'
        ]}

        submit
        delete={key !== null}
        title={key === null ? gettext("New account", 'system.mail') : this.state.data.name}
        windowed

        onAfterDelete={this.props.onAfterDelete}
        onAfterSubmit={this.props.onAfterSubmit}
        onClose={this.props.onClose}
      >
        <FormPaper>
          <FormTextInputField
            error={this.state.data.name === ''}
            formName={'name'}
            label={gettext("Name")}
            required
            width={6}
          />
          <FormTextInputField
            error={this.state.data.username === ''}
            formName={'username'}
            label={gettext("Username", 'system.mail')}
            required
            width={6}
          />
          <FormPasswordSetterField
            labelPassword={gettext("Password", 'system.mail')}
            labelConfirmation={gettext("Password confirmation", 'system.mail')}
            formName={'password'}
            spacing={12}
          />
          <FormTextInputField
            formName={'snd_host'}
            label={gettext("Server for mail sending (SMTP)", 'system.mail')}
            width={8}
          />
          <FormTextInputField
            formName={'snd_port'}
            label={gettext("Port", 'system.mail')}
            inputType={'number'}
            width={4}
          />
          <FormTextInputField
            formName={'rcp_host'}
            label={gettext("Server for mail receiving (IMAP/POP3)", 'system.mail')}
            width={8}
          />
          <FormTextInputField
            formName={'rcp_port'}
            label={gettext("Port", 'system.mail')}
            inputType={'number'}
            width={4}
          />
          <FormCheckboxField
            formName={'use_imap'}
            label={gettext("Use IMAP protocol", 'system.mail')}
            width={6}
          />
          <FormCheckboxField
            formName={'use_tls'}
            label={gettext("Use TLS encryption", 'system.mail')}
            width={6}
          />
        </FormPaper>
      </EntityForm>
    )
  }
}
