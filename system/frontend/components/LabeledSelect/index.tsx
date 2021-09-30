import React from 'react'
import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectProps
} from 'system/components'
import {uniqueId} from 'system/tools'


export type SelectOption = {
  value: string
  caption: string
}

export type SelectOptions = SelectOption[]

export interface LabeledSelectProps extends SelectProps {
  formControlStyle?: any
  formControlClassName?: string
  labelText: string
  options: SelectOptions
}


export class LabeledSelect extends React.Component<LabeledSelectProps> {
  labelId: string

  constructor(p: LabeledSelectProps) {
    super(p);
    this.labelId = uniqueId('reactComponentLabel')
  }

  render() {
    return (
      <FormControl
        style={this.props.formControlStyle}
        className={this.props.formControlClassName}
      >
        <InputLabel id={this.labelId}>{this.props.labelText}</InputLabel>
        <Select
          labelId={this.labelId}
          {...this.props}
        >
          {this.props.options.map(option => (
            <MenuItem value={option.value}>{option.caption}</MenuItem>
          ))}
        </Select>
      </FormControl>
    )
  }
}
