import React from 'react'
import {strToDate} from '../../tools'


export type TimeTextProps = {
  ifNone?: string | boolean
  seconds?: boolean
  value: string | null | undefined
}

export type DateTextProps = {
  ifNone?: string | boolean
  monthRepr?: '2-digit' | 'numeric' | 'short' | 'long'
  value: string | null | undefined
}

export type DateTimeTextProps = {
  ifNone?: string | boolean
  monthRepr?: '2-digit' | 'numeric' | 'short' | 'long'
  seconds?: boolean
  value: string | null | undefined
}


export class TimeText extends React.Component<TimeTextProps> {
  static defaultProps: TimeTextProps = {
    value: undefined,
    ifNone: '-',
    seconds: false
  }

  render() {
    const noneText: string =
      typeof this.props.ifNone == 'boolean'
      ? (this.props.ifNone ? '-' : '')
      : String(this.props.ifNone ?? '')

    const valueText: string =
      this.props.value
      ? strToDate(this.props.value)?.toLocaleTimeString(undefined, {
        hour: 'numeric',
        minute: '2-digit',
        second: this.props.seconds ? '2-digit' : undefined
      }) || noneText
      : noneText

    return valueText
  }
}


export class DateText extends React.Component<DateTextProps> {
  static defaultProps: DateTextProps = {
    value: undefined,
    ifNone: '-',
    monthRepr: '2-digit'
  }

  render() {
    const noneText: string =
      typeof this.props.ifNone == 'boolean'
      ? (this.props.ifNone ? '-' : '')
      : String(this.props.ifNone ?? '')

    const valueText: string =
      this.props.value
      ? strToDate(this.props.value)?.toLocaleDateString(undefined, {
        year: 'numeric',
        month: this.props.monthRepr ?? '2-digit',
        day: (this.props.monthRepr ?? '2-digit') !== 'numeric' ? 'numeric' : '2-digit'
      }) || noneText
      : noneText

    return valueText
  }
}


export class DateTimeText extends React.Component<DateTimeTextProps> {
  static defaultProps: DateTimeTextProps = {
    value: undefined,
    ifNone: '-',
    monthRepr: '2-digit',
    seconds: false
  }

  render() {
    const noneText: string =
      typeof this.props.ifNone == 'boolean'
      ? (this.props.ifNone ? '-' : '')
      : String(this.props.ifNone ?? '')

    const valueText: string =
      this.props.value
      ? strToDate(this.props.value)?.toLocaleString(undefined, {
        year: 'numeric',
        month: this.props.monthRepr ?? '2-digit',
        day: (this.props.monthRepr ?? '2-digit') !== 'numeric' ? 'numeric' : '2-digit',
        hour: 'numeric',
        minute: '2-digit',
        second: this.props.seconds ? '2-digit' : undefined
      }) || noneText
      : noneText

    return valueText
  }
}
