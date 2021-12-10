import React from 'react'
import {
  Box,
  Typography
} from 'system/components'
import {ScreenProps} from 'system/types'
import {gettext} from 'system/l10n'


type ___ScreenState = {

}


export default class ___Screen extends React.Component<ScreenProps> {
  state: ___ScreenState = {

  }

  render() {
    return (
      <React.Fragment>
        <Box mt={1}>
          <Typography variant={'h4'} paddingBottom={2}>{gettext('___')}</Typography>
        </Box>
      </React.Fragment>
    )
  }
}
