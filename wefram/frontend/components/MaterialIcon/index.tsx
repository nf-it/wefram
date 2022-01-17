import React from 'react'
import {workspaceTheme} from 'build/theme'


export type MaterialIconSize = number | 'small' | 'medium' | 'large'
export type MaterialIconColor = string | 'primary' | 'secondary' | 'disabled'
export type MaterialIconVariant = 'filled' | 'outlined' | 'rounded' | 'sharp' | 'two-tone'

export type MaterialIconProps = {
  color?: MaterialIconColor
  size?: MaterialIconSize
  icon: string
  variant?: MaterialIconVariant
  ml?: number
  mr?: number
  mt?: number
  mb?: number
  m?: number
  margin?: any
  marginLeft?: any
  marginRight?: any
  marginTop?: any
  marginBottom?: any
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
        ? workspaceTheme.colors.primaryColor
        : props.color === 'secondary'
          ? workspaceTheme.colors.secondaryColor
          : props.color === 'disabled'
            ? workspaceTheme.colors.disabledColor
            : props.color,
      marginLeft: props.ml !== undefined
        ? `${props.ml * 8}px`
        : props.marginLeft !== undefined
          ? props.marginLeft
          : props.m != undefined
            ? `${props.m * 8}px`
            : props.margin,
      marginRight: props.mr !== undefined
        ? `${props.mr * 8}px`
        : props.marginRight !== undefined
          ? props.marginRight
          : props.m != undefined
            ? `${props.m * 8}px`
            : props.margin,
      marginTop: props.mt !== undefined
        ? `${props.mt * 8}px`
        : props.marginTop !== undefined
          ? props.marginTop
          : props.m != undefined
            ? `${props.m * 8}px`
            : props.margin,
      marginBottom: props.mb !== undefined
        ? `${props.mb * 8}px`
        : props.marginBottom !== undefined
          ? props.marginBottom
          : props.m != undefined
            ? `${props.m * 8}px`
            : props.margin
    }}
  >{props.icon}</span>
)
