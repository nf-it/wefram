import React, {createRef} from 'react'
import {
  Box,
  Dialog,
  EntityTable,
  Typography
} from 'system/components'
import {ScreenProps} from 'system/types'
import {gettext} from 'system/l10n'
import {api} from 'system/api'
import {RequestApiPath} from 'system/routing'
import CardContainer from './EntityCard'


const objectsPath: RequestApiPath = api.entityPath('###app###', '###entity###')


type ___ScreenState = {
  entityKey?: string | null
}


export default class ___Screen extends React.Component<ScreenProps> {
  state: ___ScreenState = {
    entityKey: undefined
  }

  private listRef = createRef<EntityTable>()

  render() {
    return (
      <React.Fragment>
        <Box mt={1}>
          <Typography variant={'h4'} paddingBottom={2}>{gettext('___')}</Typography>
          <EntityTable
            ref={this.listRef}
            requestPath={objectsPath}
            columns={[

            ]}
          />
        </Box>

        <Dialog open={this.state.entityKey !== undefined} maxWidth={'md'}>
          {this.state.entityKey !== undefined && (
            <CardContainer
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
