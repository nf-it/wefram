import {workspaceTheme} from 'build/theme'
import React from 'react'
import {
  MaterialIcon,
  MaterialIconProps
} from 'system/components'


export type RelIconProps = MaterialIconProps & {

}


export const RelIcon = (props: RelIconProps) => {
  const icon: string = props.icon

  // If there is a Material UI icon - return the corresponding
  // MaterialIcon component.
  if (!icon.startsWith('/')) {
    return (
      <MaterialIcon {...props} />
    )
  }

  // If the icon starts with slash - meaning that the icon has
  // have presented by URL - return the IMG element with
  // corresponding properties.
  // Note that not all properties of the MaterialIcon component
  // are applicable to the IMG. For example, there is no option
  // to set the color (due to that is just an image).
  const imageSize: string = props.size === 'small'
    ? `20px`
    : props.size === 'medium'
      ? '24px'
      : props.size === 'large'
        ? '32px'
        : props.size !== undefined
          ? `${props.size ?? 24}px`
          : '24px'
  return (
    <img
      alt={'icon'}
      src={icon}
      style={{
        width: imageSize,
        height: imageSize,
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'contain',
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
    />
  )
}
