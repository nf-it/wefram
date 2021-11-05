import React from 'react'
import {primaryColor, secondaryColor, disabledColor} from 'system/theme'


export type MaterialIconProps = {
  color?: string | 'primary' | 'secondary' | 'disabled'
  size?: number | 'small' | 'medium' | 'large'
  icon: string
  variant?: 'filled' | 'outlined' | 'rounded' | 'sharp' | 'two-tone'
}


export const MaterialIcon = (props: MaterialIconProps) => (
  <span
    className={
      (props.variant === 'filled' || !props.variant)
        ? 'material-icons'
        : props.variant === 'rounded'
        ? 'material-icons-round'
        : `material-icons-${String(props.variant)}`
    }
    style={{
      fontSize: props.size === 'small'
        ? `20px`
        : props.size === 'medium'
          ? '24px'
          : props.size === 'large'
            ? '32px'
            : props.size !== undefined
              ? `${props.size ?? 24}px`
              : undefined,
      color: props.color === 'primary'
        ? primaryColor
        : props.color === 'secondary'
          ? secondaryColor
          : props.color === 'disabled'
            ? disabledColor
            : props.color
    }}
  >{props.icon}</span>
)
