import React, {createRef} from 'react'
import {
  Box,
  EntityList,
  Typography
} from 'system/components'
import {ScreenProps} from 'system/types'
import {gettext} from 'system/l10n'
import {api} from 'system/api'
import {RequestApiPath} from 'system/routing'


const objectsPath: RequestApiPath = api.entityPath('###app###', '###entity###')


type ___ScreenState = {
  entityKey?: string | null
}


export default class ___Screen extends React.Component<ScreenProps> {
  state: ___ScreenState = {
    entityKey: undefined
  }

  private listRef = createRef<EntityList>()

  render() {
    return (
      <React.Fragment>
        <Box mt={1}>
          <Typography variant={'h4'} paddingBottom={2}>{gettext('___')}</Typography>
          <EntityList
            ref={this.listRef}
            requestPath={objectsPath}
          />
        </Box>
      </React.Fragment>
    )
  }
}
