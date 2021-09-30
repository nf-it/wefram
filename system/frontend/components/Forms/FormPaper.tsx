import React from 'react'
import {Box, Grid, GridSpacing, Typography} from 'system/components'


export type FormPaperProps = {
  title?: string  // default = empty
  titlePadding?: number | boolean  // default = true for 'depadded' or false for others
  spacing?: GridSpacing  // default = 2
  spacingAfter?: number  // default = 2
  spacingBefore?: number  // default = 8 or 4
  variant?: 'standard' | 'outlined' | 'padded'  // default = 'standard'
  padding?: number  // default = 2
}


export class FormPaper extends React.Component<FormPaperProps> {
  render() {
    return (
      <Box
        mt={this.props.spacingBefore ?? (this.props.title !== undefined ? 4 : 2)}
        mb={this.props.spacingAfter ?? 8}
        p={this.props.padding ?? ((this.props.variant ?? 'standard') !== 'standard' ? 2 : 0)}
        boxSizing={'border-box'}
        borderRadius={'.5vmax'}
        border={this.props.variant === 'outlined' ? '1px solid #ddd' : undefined}
      >
        {this.props.title && (
          <Typography
            variant={'h4'}
            color={'primary'}
            // style={{
            //   paddingLeft: this.props.titlePadding === true || (this.props.variant === 'padded' && this.props.titlePadding !== false)
            //     ? '16px'
            //     : undefined
            // }}
            gutterBottom
          >{this.props.title}</Typography>
        )}
        <Grid container spacing={this.props.spacing ?? 2}>
          {this.props.children}
        </Grid>
      </Box>
    )
  }
}
