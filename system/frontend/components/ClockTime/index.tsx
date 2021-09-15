import React from 'react'
import {Tooltip} from '@material-ui/core'

export type ClockTimeProps = {}

type S = {
  clockTimeShort: string,
  clockTimeFull: string
}

export class ClockTime extends React.Component<ClockTimeProps, S> {
  state: S = {
    clockTimeShort: '-',
    clockTimeFull: '-'
  }

  constructor(p: ClockTimeProps, s: S) {
    super(p, s)
    this.state.clockTimeShort = this.getClockTimeShort()
    this.state.clockTimeFull = this.getClockTimeFull()

    setInterval(() => this.updateClockTime(), 5000)
  }

  getClockTimeShort = (): string => {
    const now = new Date()
    return `${now.getHours()}:${now.getMinutes() < 10 ? '0' : ''}${now.getMinutes()}`
  }

  getClockTimeFull = (): string => {
    const now = new Date()
    return `${now.getHours()}:${now.getMinutes()} ${new Intl.DateTimeFormat().format(now)}`
  }

  updateClockTime = (): void => {
    this.setState({
      clockTimeShort: this.getClockTimeShort(),
      clockTimeFull: this.getClockTimeFull()
    })
  }

  render() {
    return (
      <Tooltip title={this.state.clockTimeFull}>
        <div>
          {this.state.clockTimeShort}
        </div>
      </Tooltip>
    )
  }
}

