import React, {createRef} from 'react'
import {gettext} from 'system/l10n'
import {RequestApiPath} from 'system/routing'
import {api} from 'system/api'
import {CommonKey, ManagedScreenProps, UuidKey} from 'system/types'
import {
  Box,
} from 'system/components'


type ScreenState = {
  entityKey?: CommonKey
}


export default class EntityScreen extends React.Component<ManagedScreenProps, ScreenState> {
  render() {
    console.dir(this.props)
    return (
      <Box>
        HELLO
      </Box>
    )
  }
}
