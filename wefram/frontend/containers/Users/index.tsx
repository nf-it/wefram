import React, {createRef} from 'react'
import {
  Box,
  Dialog,
  EntityList,
  MaterialIcon,
  MenuButton,
  Typography
} from 'system/components'
import {notifications} from 'system/notification'
import {runtime} from 'system/project'
import {UserModel} from 'system/aaa'
import {ScreenProps} from 'system/screens'
import {UuidKey} from 'system/types'
import {gettext} from 'system/l10n'
import {api} from 'system/api'
import {aaaProvider, session} from 'system/aaa'
import {RequestApiPath} from 'system/routing'
import User from '../User'


const objectsPath: RequestApiPath = api.entityPath('system', 'User')


type ScreenState = {
  entityKey?: string | null
  selected: UuidKey[]
  selectable: UuidKey[]
}


export default class Screen extends React.Component<ScreenProps> {
  state: ScreenState = {
    entityKey: undefined,
    selected: [],
    selectable: []
  }

  private listRef = createRef<EntityList>()

  render() {
    return (
      <React.Fragment>
        <Box mt={1}>
          <Typography variant={'h4'} paddingBottom={2}>
            {gettext("Administrate users", 'system.aaa')}
          </Typography>
          <EntityList
            ref={this.listRef}

            addButtonAction={() => this.setState({entityKey: null})}
            avatarColor
            avatarField={'avatar'}
            controls={[
              <MenuButton
                variant={'outlined'}
                items={[
                  {
                    icon: 'lock',
                    iconColor: 'red',
                    caption: gettext("Lock selected", 'system.aaa'),
                    disabled: this.state.selected.length === 0,
                    onClick: () => {
                      const selected = this.state.selected
                      if (!selected.length)
                        return
                      runtime.busy = true
                      aaaProvider.lockUsers(selected).then(() => {
                        runtime.busy = false
                        notifications.showRequestSuccess()
                        this.listRef.current?.update()
                      }).catch(err => {
                        runtime.busy = false
                        notifications.showRequestError(err)
                      })
                    }
                  },
                  {
                    icon: 'lock_open',
                    caption: gettext("Unlock selected", 'system.aaa'),
                    disabled: this.state.selected.length === 0,
                    onClick: () => {
                      const selected = this.state.selected
                      if (!selected.length)
                        return
                      runtime.busy = true
                      aaaProvider.unlockUsers(selected).then(() => {
                        runtime.busy = false
                        notifications.showRequestSuccess()
                        this.listRef.current?.update()
                      }).catch(err => {
                        runtime.busy = false
                        notifications.showRequestError(err)
                      })
                    }
                  },
                  {
                    icon: 'logout',
                    caption: gettext("Log off selected", 'system.aaa'),
                    disabled: this.state.selected.length === 0,
                    onClick: () => {
                      const selected = this.state.selected
                      if (!selected.length)
                        return
                      runtime.busy = true
                      aaaProvider.logoffUsers(selected).then(() => {
                        runtime.busy = false
                        notifications.showRequestSuccess()
                      }).catch(err => {
                        runtime.busy = false
                        notifications.showRequestError(err)
                      })
                    }
                  }
                ]}
              />
            ]}
            defaultSort={{value: 'fullName', direction: 'asc'}}
            deleteAction={true}
            deleteConfirmMessage={gettext("Are you sure you want to delete the selected users?", 'system.aaa-messages')}
            entityCaption={gettext("Users list", 'system.aaa')}
            limit={30}
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
                  hidden: (value: any): boolean => !Boolean(value),
                  valueVisualize: (value: any): any => {
                    return value
                      ? (<MaterialIcon icon={'lock'} size={20} color={'red'} />)
                      : (<MaterialIcon icon={'lock_open'} size={20} color={'grey'} />)
                  }
                },
                'login',
              ],
              {
                fieldType: 'dateTimeNice',
                fieldName: 'lastLogin',
                caption: gettext("Last logged on", 'system.aaa-list')
              }
            ]}
            selected={this.state.selected}
            selectable={this.state.selectable}
            storageEntity={'system.users'}
            textTotalCount
            variant={'cards'}
            urlStateOffset
            urlStateSearch

            onAfterFetch={(items: UserModel[]) => {
              const loggedUserId = session.user?.id
              const selectable = items.filter(item => item.id !== loggedUserId).map(item => item.id)
              this.setState({selectable})
              return items
            }}
            onItemClick={(item: UserModel) => {
              this.setState({entityKey: item.id})
            }}
            onSelection={selected => {
              this.setState({
                selected
              })
            }}
          />
        </Box>
        <Dialog open={this.state.entityKey !== undefined} maxWidth={'sm'}>
          {this.state.entityKey !== undefined && (
            <User
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
