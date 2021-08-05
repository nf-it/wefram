import React from 'react'
import {
  Grid,
  TextField,
  GridSize,
  BaseTextFieldProps,
  GridProps
} from '@material-ui/core'


export type PasswordSetterProps = {
  labelPassword?: string
  labelConfirmation?: string
  name?: string
  onChange?: React.ChangeEventHandler<HTMLInputElement>
  textFieldsProps?: BaseTextFieldProps
  gridItemsProps?: GridProps
  xs?: boolean | GridSize
}

type S = {
  value1: string
  value2: string
  invalid: boolean
}


export class PasswordSetter extends React.Component<PasswordSetterProps, S> {
  state: S = {
    value1: '',
    value2: '',
    invalid: false
  }

  handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    this.setState({value1: e.target.value}, () => {
      this.setState({invalid: this.state.value1 !== this.state.value2}, () => {
        if (this.state.invalid) {
          e.type = 'null'
        }
        this.props.onChange && this.props.onChange(e)
      })
    })
  }

  handleConfirmationChange = (e: any): void => {
    this.setState({value2: e.target.value}, () => {
      this.setState({invalid: this.state.value1 !== this.state.value2}, () => {
        if (this.state.invalid) {
          e.type = 'null'
        }
        this.props.onChange && this.props.onChange(e)
      })
    })
  }

  render() {
    return (
      <React.Fragment>
        <Grid item xs={this.props.xs ?? true} {...this.props.gridItemsProps}>
          <TextField
            {...this.props.textFieldsProps}
            type={'password'}
            error={this.state.invalid}
            label={this.props.labelPassword}
            name={this.props.name}
            onChange={this.handlePasswordChange}
            fullWidth
          />
        </Grid>
        <Grid item xs={this.props.xs ?? true} {...this.props.gridItemsProps}>
          <TextField
            {...this.props.textFieldsProps}
            type={'password'}
            error={this.state.invalid}
            label={this.props.labelConfirmation}
            name={this.props.name}
            onChange={this.handleConfirmationChange}
            fullWidth
          />
        </Grid>
      </React.Fragment>
    )
  }
}

