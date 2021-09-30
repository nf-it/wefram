import React from 'react'
import {gettext} from 'system/l10n'
import {Box, Typography} from 'system/components'


export type FetchFailedBoxProps = {
  text?: string
}


export const FetchFailedBox = (props: FetchFailedBoxProps) => (
  <Box style={{
    borderRadius: '.25vmax',
    border: '2px solid #d40',
    backgroundColor: '#d402',
    padding: '.5vmax'
  }}>
    <Typography variant={'h4'} color={'#f00'} gutterBottom>
      {gettext("Something went wrong")}
    </Typography>
    <Typography variant={'body1'} color={'#a20'}>
      {props.text ?? gettext("Something went wrong while downloading data from the server for this location. Please try to visit this page again later.")}
    </Typography>
  </Box>
)
