import React from 'react'
import {Box, BoxProps, Divider} from 'system/components'
import './index.css'


export interface StaticTextProps extends BoxProps {
  bordered?: boolean
  caption?: string
  captionPadding?: number
  captionComponent?: React.ElementType
  captionStyle?: React.CSSProperties
  contentComponent?: React.ElementType
  contentStyle?: React.CSSProperties
  divided?: boolean
}


export class StaticText extends React.Component<StaticTextProps> {
  render() {
    return (
      <Box
          className={this.props.bordered ? 'SystemUI-StaticText-containerBordered' : 'SystemUI-StaticText-container'}
          {...this.props}
      >
        {this.props.caption !== undefined && this.props.caption.trim() !== '' && (
          <Box
              className={'SystemUI-StaticText-caption'}
              component={this.props.captionComponent}
              pb={this.props.captionPadding}
              style={this.props.captionStyle}
          >
            {this.props.caption}
          </Box>
        )}
        {this.props.divided === true && (
          <Divider />
        )}
        <Box
          className={'SystemUI-StaticText-content'}
          component={this.props.contentComponent}
          style={this.props.contentStyle}
        >
          {this.props.children}
        </Box>
      </Box>
    )
  }
}
