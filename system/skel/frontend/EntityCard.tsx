import React from 'react'
import {
  Box,
  EntityForm
} from 'system/components'
import {gettext} from 'system/l10n'
import {api} from 'system/api'
import {RequestApiPath} from 'system/routing'


const objectPath: RequestApiPath = api.entityObjectPath('###app###', '###entity###')


export type ___Props = {
  entityKey: string | null
  onAfterDelete: () => void
  onAfterSubmit: () => void
  onClose: () => void
}

type ___State = {
  data: any  /* typed model may be used here */
}

export default class ___ extends React.Component<___Props, ___State> {
  state: ___State = {
    data: {
      id: null,
      /* initial model data here */
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
        requiredForSubmit={[]}
        submitFieldsModel={[]}

        submit
        delete={key !== null}
        title={key === null ? gettext("Create") : this.state.data.name}
        windowed

        onAfterDelete={this.props.onAfterDelete}
        onAfterSubmit={this.props.onAfterSubmit}
        onClose={this.props.onClose}
      >
        <Box>

        {/* the Card contents here */}

        </Box>
      </EntityForm>
    )
  }
}

