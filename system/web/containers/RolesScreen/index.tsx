import React from 'react'
import {Box, Typography} from '@material-ui/core'
import {ScreenProps} from '../../types'
import {EntityList} from '../EntityList'
import {gettext} from '../../l10n'
import {runtime} from '../../runtime'
import {api} from '../../api'
import {RequestApiPath} from '../../routing'


const itemScreenPath: string = '/settings/system/roles/{key}'
const addScreenPath: string = '/settings/system/roles/new'
const objectsPath: RequestApiPath = api.entityPath('system', 'Role')


export default class Roles extends React.Component<ScreenProps> {
  restoreScrollPosition = (): void => {
    runtime.restoreScrollPosition()
  }

  render() {
    return (
      <Box mt={2}>
        <Typography variant={'h4'}>{gettext("Administrate roles", 'system.aaa')}</Typography>
        <EntityList
          addScreen={addScreenPath}
          defaultSort={{value: 'name', direction: 'asc'}}
          deleteButton={true}
          entityCaption={gettext("Roles list", 'system.aaa')}
          itemsRoute={itemScreenPath}
          limit={25}
          pagination
          primaryField={'name'}
          requestPath={objectsPath}
          search
          selectable
          textTotalCount
          urlStateOffset
          urlStateSearch
          onFetchDone={this.restoreScrollPosition}
        />
      </Box>
    )
  }
}
