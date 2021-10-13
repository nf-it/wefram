import React from 'react'
import MaskedInput, {Mask} from 'react-text-mask'
import {TextField, TextFieldProps} from 'system/components'


export type MaskedTextFieldProps = TextFieldProps & {
  mask: Mask | ((value: string) => Mask)
  guide?: boolean
  keepCharPositions?: boolean
}


interface TextMaskCustomProps {
  // inputRef: (ref: HTMLInputElement | null) => void
  mask: Mask | ((value: string) => Mask)
  guide?: boolean
  keepCharPositions?: boolean
}


function TextMaskCustom(props: TextMaskCustomProps) {
  const { mask, guide, keepCharPositions, ...other } = props;

  return (
    <MaskedInput
      {...other}
      // ref={(ref: any) => {
      //   inputRef(ref ? ref.inputElement : null);
      // }}
      mask={mask}
      guide={guide}
      placeholderChar={'\u2000'}
      keepCharPositions={keepCharPositions}
      showMask
    />
  );
}


export class MaskedTextField extends React.Component<MaskedTextFieldProps> {
  render() {
    let { inputProps, InputProps, ...otherProps } = this.props

    InputProps = InputProps ?? { }
    inputProps = inputProps ?? { }

    InputProps.inputComponent = TextMaskCustom as any
    inputProps.mask = this.props.mask
    inputProps.guide = this.props.guide
    inputProps.keepCharPositions = this.props.keepCharPositions

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
