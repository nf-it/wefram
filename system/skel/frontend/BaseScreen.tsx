import React from 'react'
import {
  Box,
  Typography
} from 'system/components'
import {ScreenProps} from 'system/types'
import {gettext} from 'system/l10n'


type ___ScreenState = {
  entityKey?: string | null
}


export default class ___Screen extends React.Component<ScreenProps> {
  state: ___ScreenState = {
    entityKey: undefined
  }

  render() {
    return (
      <React.Fragment>
        <Box mt={2}>
          <Typography variant={'h4'}>{gettext('___')}</Typography>
        </Box>
      </React.Fragment>
    )
  }
}
