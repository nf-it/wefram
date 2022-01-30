import React, {createRef} from 'react'
import {gettext} from 'system/l10n'
import {RequestApiPath} from 'system/routing'
import {api} from 'system/api'
import {ManagedScreenProps} from 'system/screens'
import {CommonKey} from 'system/types'
import {
  Box,
  EntityList,
  EntityTable,
  Typography,
} from 'system/components'


type ScreenState = {
  entityKey?: CommonKey
}


export type EntityScreenEnumVariant = 'list' | 'table'

export type EntityScreenManagedProps = {
  entityApp: string
  entityName: string
  enumVariant: EntityScreenEnumVariant

  caption?: string
  entityCaption?: string
}


export default class EntityScreen extends React.Component<ManagedScreenProps, ScreenState> {
  state: ScreenState = {
    entityKey: undefined
  }

  private enumRef = createRef<any>()

  render() {
    const managedProps: EntityScreenManagedProps = this.props.managedProps

    const entityPath: RequestApiPath = api.entityPath(managedProps.entityApp, managedProps.entityName)
    const objectPath: RequestApiPath = api.entityObjectPath(managedProps.entityApp, managedProps.entityName)

    return (
      <React.Fragment>
        <Box mt={2}>
          {managedProps.caption !== undefined && (
            <Typography variant={'h4'} paddingBottom={2}>
              {managedProps.caption}
            </Typography>
          )}

          {managedProps.enumVariant === 'list' ? (
            <EntityList
              ref={this.enumRef}
              requestPath={entityPath}
            />
          ) : (
            <EntityTable
              ref={this.enumRef}
              requestPath={entityPath}
              columns={[]}
            />
          )}
        </Box>
      </React.Fragment>
    )
  }
}
