import React from 'react'
import NumberFormat from 'react-number-format'
import {TextField, TextFieldProps} from 'system/components'


export type DigitsInputFieldProps = TextFieldProps & {
  thousandSeparator?: string | boolean
  decimalSeparator?: string
  thousandsGroupStyle?: 'thousand' | 'lakh' | 'wan'
  decimalScale?: number
  fixedDecimalScale?: boolean
  allowNegative?: boolean
  allowEmptyFormatting?: boolean
  allowLeadingZeros?: boolean
  prefix?: string
  suffix?: string
  format?: string
  mask?: string
}


interface NumberFormatCustomProps {
  inputRef: (instance: NumberFormat | null) => void;
  onChange: (event: { target: { name: string; tagName: string; value: number } }) => void;
  name: string;
  thousandSeparator?: string | boolean
  decimalSeparator?: string
  thousandsGroupStyle?: 'thousand' | 'lakh' | 'wan'
  decimalScale?: number
  fixedDecimalScale?: boolean
  allowNegative?: boolean
  allowEmptyFormatting?: boolean
  allowLeadingZeros?: boolean
  prefix?: string
  suffix?: string
  format?: string
  mask?: string
}

function NumberFormatCustom(props: NumberFormatCustomProps) {
  const {
    inputRef,
    onChange,
    ...other
  } = props;

  return (
    <NumberFormat
      {...other}
      getInputRef={inputRef}
      onValueChange={(values) => {
        onChange({
          target: {
            name: props.name,
            tagName: 'INPUT',
            value: values.floatValue ?? 0,
          },
        });
      }}
    />
  );
}



export class DigitsInputField extends React.Component<DigitsInputFieldProps> {
  render() {
    let { inputProps, InputProps, ...otherProps } = this.props

    InputProps = InputProps ?? { }
    inputProps = Object.assign(inputProps ?? { }, {
      thousandSeparator: this.props.thousandSeparator,
      decimalSeparator: this.props.decimalSeparator,
      thousandsGroupStyle: this.props.thousandsGroupStyle,
      decimalScale: this.props.decimalScale,
      fixedDecimalScale: this.props.fixedDecimalScale,
      allowNegative: this.props.allowNegative,
      allowEmptyFormatting: this.props.allowEmptyFormatting,
      allowLeadingZeros: this.props.allowLeadingZeros,
      prefix: this.props.prefix,
      suffix: this.props.suffix,
      format: this.props.format,
      mask: this.props.mask
    })

    InputProps.inputComponent = NumberFormatCustom as any

    return (
      <TextField
        {...otherProps}
        InputLabelProps={{ shrink: true }}
        inputProps={inputProps}
        InputProps={InputProps}
      />
    )
  }
}
