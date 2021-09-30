import React from 'react'
import {Box} from 'system/components'


export type SpacingProps = {
  horizontal?: number
  vertical?: number
}


export class Spacing extends React.Component<SpacingProps> {
  render() {
    return (
      <Box ml={this.props.horizontal} mt={this.props.vertical} />
    )
  }
}
