import React from 'react'
import {
  TextField,
  StandardTextFieldProps,
  OutlinedTextFieldProps,
  FilledTextFieldProps
} from 'system/components'


const defaultTriggerTimeout: number = 1000

export type LazyStandardTextFieldProps = StandardTextFieldProps & {
  onChangeLazy: (e: React.ChangeEvent<HTMLInputElement>) => void
  lazyTimeout?: number
}

export type LazyOutlinedTextFieldProps = OutlinedTextFieldProps & {
  onChangeLazy: (e: React.ChangeEvent<HTMLInputElement>) => void
  lazyTimeout?: number
}

export type LazyFilledTextFieldProps = FilledTextFieldProps & {
  onChangeLazy: (e: React.ChangeEvent<HTMLInputElement>) => void
  lazyTimeout?: number
}

export type LazyTextFieldProps = LazyStandardTextFieldProps | LazyFilledTextFieldProps | LazyOutlinedTextFieldProps


export class LazyTextField extends React.Component<LazyTextFieldProps> {
  timer: any | null
  onChange: any | undefined

  constructor(p: LazyTextFieldProps) {
    super(p);
    this.timer = null
    this.onChange = undefined
  }

  private handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    if (this.timer !== null) {
      clearTimeout(this.timer)
    }
    this.timer = setTimeout(
      () => {
        this.timer = null
        this.props.onChangeLazy(e)
      },
      this.props.lazyTimeout ?? defaultTriggerTimeout
    )
    if (this.props.onChange !== undefined) {
      this.props.onChange(e)
    }
  }

  render() {
    return (
      <TextField
        {...this.props}
        onChange={this.handleChange}
      />
    )
  }
}
