import React from 'react'
import {Box, MaterialIcon, Typography, TypographyProps} from '..'


export interface TipTypographyProps extends TypographyProps {
  color?: string
  bordered?: boolean
  backgroundColor?: string
  icon?: string
  iconColor?: string
}


export const TipTypography = (props: TipTypographyProps) => {
  const {
    backgroundColor,
    bordered,
    color,
    icon,
    iconColor,
    ...typographyProps
  } = props

  return (
    <Box
      alignItems={'flex-start'}
      border={(bordered ?? true) ? '1px solid #0002' : undefined}
      borderRadius={'8px'}
      display={'flex'}
      padding={'8px'}
      sx={{
        backgroundColor: backgroundColor ?? '#ffc',
        color: color ?? '#333'
      }}
    >
      <Box paddingRight={'8px'} lineHeight={0}>
        <MaterialIcon icon={icon ?? 'info'} color={iconColor ?? '#000b'} />
      </Box>
      <Box>
        <Typography flexGrow={1} fontSize={'.85rem'} {...typographyProps} />
      </Box>
    </Box>
  )
}
