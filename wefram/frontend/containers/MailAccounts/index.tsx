import React, {createRef} from 'react'
import {
  Box,
  Dialog,
  EntityList,
  Typography
} from 'system/components'
import {ScreenProps} from 'system/types'
import {gettext} from 'system/l10n'
import {api} from 'system/api'
import {RequestApiPath} from 'system/routing'
import MailAccount from 'system/containers/MailAccount'


const objectsPath: RequestApiPath = api.entityPath('system', 'MailAccount')


type ScreenState = {
  entityKey?: string | null
}


export default class Screen extends React.Component<ScreenProps, ScreenState> {
  state: ScreenState = {
    entityKey: undefined
  }

  private listRef = createRef<EntityList>()

  render() {
    return (
      <React.Fragment>
        <Box mt={1}>
          <Typography variant={'h4'} paddingBottom={2}>
            {gettext('Mail accounts', 'system.mail')}
          </Typography>
          <EntityList
            ref={this.listRef}
            requestPath={objectsPath}

            search
            textTotalCount
            selectable
            addButtonAction={() => this.setState({entityKey: null})}
            deleteButton={true}
            entityCaption={gettext("Mail accounts", 'system.mail')}
            primaryField={'name'}
            secondaryField={'username'}
            onItemClick={(item: any) => {
              this.setState({entityKey: item.id})
            }}
          />
        </Box>

        <Dialog open={this.state.entityKey !== undefined} maxWidth={'md'}>
          {this.state.entityKey !== undefined && (
            <MailAccount
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
