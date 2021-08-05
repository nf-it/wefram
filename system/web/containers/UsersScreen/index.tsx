import React, {createRef} from 'react'
import {
  Box,
  Dialog,
  DialogContent,
  Typography
} from '@material-ui/core'
import {LockOpen, Lock} from '@material-ui/icons'
import {ScreenProps} from '../../types'
import {EntityList} from '../EntityList'
import {gettext} from '../../l10n'
import {runtime} from '../../runtime'
import {api} from '../../api'
import {RequestApiPath} from '../../routing'
import {UserCard} from '../UserCard'

const objectsPath: RequestApiPath = api.entityPath('system', 'User')


type UsersScreenState = {
  entityKey?: string | null
}


export default class UsersScreen extends React.Component<ScreenProps> {
  state: UsersScreenState = {
    entityKey: undefined
  }

  private listRef = createRef<EntityList>()

  restoreScrollPosition = (): void => {
    runtime.restoreScrollPosition()
  }

  render() {
    return (
      <React.Fragment>
      <Box mt={2}>
        <Typography variant={'h4'}>{gettext("Administrate users", 'system.aaa')}</Typography>
        <EntityList
          ref={this.listRef}

          addButtonAction={() => this.setState({entityKey: null})}
          defaultSort={{value: 'fullName', direction: 'asc'}}
          deleteButton={true}
          deleteConfirmMessage={gettext("Are you sure you want to delete the selected users?", 'system.aaa-messages')}
          entityCaption={gettext("Users list", 'system.aaa')}
          limit={25}
          pagination
          primaryField={'fullName'}
          requestPath={objectsPath}
          sortOptions={[
            {value: 'login', caption: gettext("Login", 'system.aaa-list')},
            {value: 'fullName', caption: gettext("Full name", 'system.aaa-list')}
          ]}
          search
          secondaryField={[
            [
              {
                fieldType: 'boolean',
                fieldName: 'locked',
                valueVisualize: (value: any): any => {
                  return value
                    ? (<Lock fontSize={'small'} style={{color: 'red'}}/>)
                    : (<LockOpen fontSize={'small'} style={{color: 'gray'}}/>)
                }
              },
              'login',
              {
                fieldType: 'dateTimeNice',
                fieldName: 'lastLogin',
                caption: gettext("Last logged on", 'system.aaa-list')
              }
            ],
          ]}
          selectable
          textTotalCount
          urlStateOffset
          urlStateSearch
          onFetchDone={this.restoreScrollPosition}
          onItemClick={(item: any) => {
            this.setState({entityKey: item.id})
          }}
        />
      </Box>
      <Dialog open={this.state.entityKey !== undefined} maxWidth={'sm'}>
        {this.state.entityKey !== undefined && (
          <UserCard
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
