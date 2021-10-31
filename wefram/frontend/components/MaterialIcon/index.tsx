import React from 'react'


export type MaterialIconProps = {
  color?: string
  size?: number
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
      fontSize: props.size !== undefined ? `${props.size ?? 24}px` : undefined,
      color: props.color
    }}
  >{props.icon}</span>
)
