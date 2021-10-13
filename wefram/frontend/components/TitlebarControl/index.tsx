import React from 'react'
import {Box, Typography, TypographyVariant} from 'system/components'


export type TitlebarControlProps = {
  title: string
  variant?: TypographyVariant
  color?:
    | 'initial'
    | 'inherit'
    | 'primary'
    | 'secondary'
    | 'textPrimary'
    | 'textSecondary'
    | 'error'
  mt?: number
  mb?: number
}


export class TitlebarControl extends React.Component<TitlebarControlProps> {
  render() {
    return (
      <Box
        mt={this.props.mt}
        mb={this.props.mb ?? 3}
        style={{
          display: 'flex',
          alignItems: 'center'
        }}
      >
        <Box>
          <Typography
            variant={this.props.variant ?? 'h4'}
            color={this.props.color}
          >{this.props.title}</Typography>
        </Box>
        <Box
          style={{
            flexGrow: 1,
            display: 'flex',
            justifyContent: 'flex-end'
          }}
        >
          {this.props.children}
        </Box>
      </Box>
    )
  }
}
