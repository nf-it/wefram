import React from 'react'
import {Box, MaterialIcon, Tooltip} from '..'


export type HintedProps = {
  hint: string
  icon?: string
  color?: string
  children?: React.ReactNode
}


export const Hinted = (props: HintedProps) => (
  <Box display={'flex'} alignItems={'center'} justifyContent={'space-between'}>
    {props.children}
    <Tooltip title={props.hint}>
      <MaterialIcon icon={props.icon ?? 'info'} size={'small'} color={props.color ?? '#644'} />
    </Tooltip>
  </Box>
)
