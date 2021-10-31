import React from 'react'
import {Box, IconButton, MaterialIcon, TextField, Tooltip} from 'system/components'
import {gettext} from 'system/l10n'


export type PasswordSetterProps = {
  clearable?: boolean  // default = false
  dense?: boolean
  disabled?: boolean
  error?: boolean
  labelPassword?: string
  labelConfirmation?: string
  name?: string
  spacing?: number
  unhidable?: boolean  // default = true
  variant?: 'standard' | 'filled' | 'outlined'
  size?: 'small' | 'medium'
  onChange?: ((name: string | undefined, newValue: any) => void)
}

type PasswordSetterState = {
  value1: string
  value2: string
  invalid: boolean
  clear: boolean
  unhide: boolean
}


export class PasswordSetter extends React.Component<PasswordSetterProps, PasswordSetterState> {
  state: PasswordSetterState = {
    value1: '',
    value2: '',
    invalid: false,
    clear: false,
    unhide: false
  }

  handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    this.setState({value1: e.target.value}, () => {
      this.setState({invalid: this.state.value1 !== this.state.value2}, () => {
        const value: string | undefined = this.state.invalid ? undefined : e.target.value
        this.props.onChange && this.props.onChange(e.target.name ?? e.target.id ?? null, value)
      })
    })
  }

  handleConfirmationChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    this.setState({value2: e.target.value}, () => {
      this.setState({invalid: this.state.value1 !== this.state.value2}, () => {
        const value: string | undefined = this.state.invalid ? undefined : e.target.value
        this.props.onChange && this.props.onChange(e.target.name ?? e.target.id ?? null, value)
      })
    })
  }

  handleClear = () => {
    this.setState({clear: !this.state.clear}, () => {
      this.props.onChange && this.props.onChange(
        this.props.name,
        this.state.clear
          ? null
          : this.state.invalid
            ? undefined
            : this.state.value1
      )
    })
  }

  render() {
    const alignItems = (this.props.variant ?? 'outlined') === 'standard' ? 'flex-end' : 'center'
    return (
      <React.Fragment>
        <Box display={'flex'} alignItems={alignItems} justifyContent={'space-between'} width={'100%'}>
          <TextField
            disabled={this.state.clear || this.props.disabled}
            value={this.state.clear ? '' : (this.state.value1 ?? '')}
            type={this.state.unhide ? 'text' : 'password'}
            error={this.state.invalid || this.props.error}
            label={this.state.clear ? gettext("Empty password", 'system.aaa') : this.props.labelPassword}
            name={this.props.name}
            margin={this.props.dense ? 'dense' : undefined}
            size={this.props.size}
            onChange={this.handlePasswordChange}
            fullWidth
            variant={this.props.variant}
          />
          <TextField
            disabled={this.state.clear || this.props.disabled}
            value={this.state.clear ? '' : (this.state.value2 ?? '')}
            type={this.state.unhide ? 'text' : 'password'}
            error={this.state.invalid || this.props.error}
            label={this.state.clear ? gettext("Empty password", 'system.aaa') : this.props.labelConfirmation}
            name={this.props.name}
            margin={this.props.dense ? 'dense' : undefined}
            size={this.props.size}
            onChange={this.handleConfirmationChange}
            fullWidth
            variant={this.props.variant}
            style={{marginLeft: `${(this.props.spacing ?? 1) * 8}px`}}
          />
          {(this.props.clearable ?? false) && (
            <Tooltip title={gettext('Set password to empty', 'system.aaa')}>
              <IconButton
                size={'small'}
                style={{
                  marginLeft: `${(this.props.spacing ?? 1) * 8}px`,
                  marginBottom: '8px',
                  marginTop: '8px',
                  border: this.state.clear ? '1px solid #bd3302' : '1px solid #dddddd'
                }}
                color={this.state.clear ? 'secondary' : 'default'}
                onClick={() => this.setState({clear: !this.state.clear})}
              >
                <MaterialIcon icon={'highlight_off'} size={20} />
              </IconButton>
            </Tooltip>
          )}
          {(this.props.unhidable ?? true) && (!this.state.clear) && (
            <IconButton
              size={'small'}
              style={{
                marginLeft: `${(this.props.spacing ?? 1) * 8}px`,
                marginTop: '8px',
                marginBottom: '8px',
                border: this.state.unhide ? '1px solid #bd3302' : '1px solid #dddddd'
              }}
              color={this.state.unhide ? 'secondary' : 'default'}
              onClick={() => this.setState({unhide: !this.state.unhide})}
            >{
              this.state.unhide
                ? (<MaterialIcon icon={'visibility'} size={20} />)
                : (<MaterialIcon icon={'visibility_off'} size={20} />)
            }</IconButton>
          )}
        </Box>
      </React.Fragment>
    )
  }
}

