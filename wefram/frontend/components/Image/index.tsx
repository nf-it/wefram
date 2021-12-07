/**
 * The original package was 'material-ui-image' which was not updated to use the new version
 * of the Material-UI (mui) v5 in time. So, this component was slightly rewritten and finally
 * integrated into the Wefram platform.
 */

import React from 'react'
import {Box, CircularProgress, MaterialIcon} from 'system/components'


export type ImageVariant = 'rounded' | 'square' | 'circular'

export type ImageProps = {
  animationDuration?: number          /** Duration of the fading animation, in milliseconds. */
  aspectRatio?: number                /** Override aspect ratio. */
  cover?: boolean                     /** Override the object fit to cover. */
  color?: string                      /** Override the background color. */
  disableError?: boolean              /** Disables the error icon if set to true. */
  disableSpinner?: boolean            /** Disables the loading spinner if set to true. */
  disableTransition?: boolean         /** Disables the transition after load if set to true. */
  errorIcon?: JSX.Element             /** Override the error icon. */
  iconContainerStyle?: React.CSSProperties  /** Override the inline-styles of the container that contains the loading spinner and the error icon. */
  imageStyle?: React.CSSProperties    /** Override the inline-styles of the image. */
  loading?: JSX.Element               /** Override the loading component. */
  onClick?: React.MouseEventHandler   /** Fired when the user clicks on the image happened. */
  onError?: React.EventHandler<any>   /** Fired when the image failed to load. */
  onLoad?: React.EventHandler<any>    /** Fired when the image finished loading. */
  src: string                         /** Specifies the URL of an image. */
  style?: React.CSSProperties         /** Override the inline-styles of the root element. */
  variant?: ImageVariant  /** The variant of the displaying image. */
}


type ImageState = {
  imageError: boolean
  imageLoaded: boolean
}


type ImagePropsDefaults = {
  animationDuration: number
  aspectRatio: number
  color: string
  disableError: boolean
  disableSpinner: boolean
  disableTransition: boolean
  errorIcon: JSX.Element | null
  variant: ImageVariant
  loading: JSX.Element
}

const defaults: ImagePropsDefaults = {
  animationDuration: 1000,
  aspectRatio: 1,
  color: '#ffffff',
  disableError: false,
  disableSpinner: false,
  disableTransition: false,
  errorIcon: null,
  variant: 'square',
  loading: <CircularProgress size={48} />
}


export class Image extends React.Component<ImageProps, ImageState> {
  state: ImageState = {
    imageError: false,
    imageLoaded: false
  }

  public static borderRadiusForVariant = (
    variant?: ImageVariant,
    defaultVariant: ImageVariant = 'square'
  ): string => {
    switch (variant) {
      case 'square':
        return '1px'
      case 'rounded':
        return '.5vmax'
      case 'circular':
        return '10000px'
      default:
        return defaultVariant
    }
  }

  private getStyles = (): any => {
    const {
      animationDuration,
      aspectRatio,
      cover,
      color,
      imageStyle,
      disableTransition,
      iconContainerStyle,
      style
    } = this.props

    const imageTransition = !disableTransition && {
      opacity: this.state.imageLoaded ? 1 : 0,
      filterBrightness: this.state.imageLoaded ? 100 : 0,
      filterSaturate: this.state.imageLoaded ? 100 : 20,
      transition: `
        filterBrightness ${(animationDuration ?? defaults.animationDuration) * 0.75}ms cubic-bezier(0.4, 0.0, 0.2, 1),
        filterSaturate ${animationDuration ?? defaults.animationDuration}ms cubic-bezier(0.4, 0.0, 0.2, 1),
        opacity ${(animationDuration ?? defaults.animationDuration) / 2}ms cubic-bezier(0.4, 0.0, 0.2, 1)`
    }

    const borderRadius: string = Image.borderRadiusForVariant(this.props.variant)

    return {
      root: {
        backgroundColor: color,
        paddingTop: `calc(1 / ${aspectRatio} * 100%)`,
        position: 'relative',
        borderRadius,
        ...style
      },
      image: {
        width: '100%',
        height: this.props.cover ? '100%' : undefined,
        position: 'absolute',
        objectFit: cover ? 'cover' : 'inherit',
        top: 0,
        left: 0,
        borderRadius,
        ...imageTransition,
        ...imageStyle
      },
      iconContainer: {
        width: '100%',
        height: '100%',
        position: 'absolute',
        top: 0,
        left: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        pointerEvents: 'none',
        borderRadius,
        ...iconContainerStyle
      }
    }
  }

  handleLoadImage = (e?: React.SyntheticEvent<HTMLImageElement, Event>): void => {
    this.setState({
      imageLoaded: true,
      imageError: false
    })
    if (this.props.onLoad) {
      this.props.onLoad(e)
    }
  }

  handleImageError = (e?: React.SyntheticEvent<HTMLImageElement, Event>): void => {
    if (this.props.src) {
      this.setState({
        imageError: true
      })
      if (this.props.onError) {
        this.props.onError(e)
      }
    }
  }

  render() {
    const styles: any = this.getStyles()

    const {
      animationDuration,
      aspectRatio,
      color,
      cover,
      disableError,
      disableSpinner,
      disableTransition,
      errorIcon,
      iconContainerStyle,
      imageStyle,
      loading,
      onClick,
      style,
      ...imageProps
    } = this.props

    const errorIconElement = errorIcon || <MaterialIcon icon={'broken_image'} size={48} color={'#e0e0e0'} />

    return (
      <Box
        style={styles.root}
        onClick={onClick}
      >
        {imageProps.src && (
          <img
            {...imageProps}
            style={styles.image}
            onLoad={this.handleLoadImage}
            onError={this.handleImageError}
          />
        )}
        <Box style={styles.iconContainer}>
          {!disableSpinner && !this.state.imageLoaded && !this.state.imageError && loading}
          {!disableError && this.state.imageError && errorIconElement}
        </Box>
      </Box>
    )
  }
}
