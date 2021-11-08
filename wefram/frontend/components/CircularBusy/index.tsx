import React from 'react'
import {Box, CircularProgress, CircularProgressProps} from '@mui/material'


export type CircularBusyProps = CircularProgressProps & {
  padding?: number
}


export const CircularBusy = (props: CircularBusyProps) => (
  <Box
    pt={props.padding ?? 2}
    pb={props.padding ?? 2}
    width={'100%'}
    display={'flex'}
    justifyContent={'center'}
    alignItems={'center'}
  >
    <CircularProgress {...props} />
  </Box>
)
