import React from 'react'
import {workspaceTheme} from 'build/theme'
import {Box, IconButton, MaterialIcon, Tooltip} from '..'


export type HintedProps = {
  hint: string
  icon?: string
  color?: string
  children?: React.ReactNode
}


export const Hinted = (props: HintedProps) => (
  <Box display={'flex'} alignItems={'flex-start'} justifyContent={'flex-start'}>
    {props.children}
    <Tooltip title={props.hint}>
      <IconButton style={{
        padding: 0,
        marginLeft: '4px'
      }}>
        <MaterialIcon icon={props.icon ?? 'info'} size={16} color={props.color ?? workspaceTheme.colors.hintColor} />
      </IconButton>
    </Tooltip>
  </Box>
)
