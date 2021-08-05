import React, {Component} from 'react'
import classNames from 'classnames'
import CheckCircleIcon from '@material-ui/icons/CheckCircle'
import ErrorIcon from '@material-ui/icons/Error'
import InfoIcon from '@material-ui/icons/Info'
import CloseIcon from '@material-ui/icons/Close'
import IconButton from '@material-ui/core/IconButton'
import Snackbar from '@material-ui/core/Snackbar'
import SnackbarContent from '@material-ui/core/SnackbarContent'
import WarningIcon from '@material-ui/icons/Warning'
import {withStyles} from '@material-ui/core/styles'
import {SvgIconProps} from '@material-ui/core'

export * from './types'

export interface VariantIcon {
  success: (props: SvgIconProps) => JSX.Element
  warning: (props: SvgIconProps) => JSX.Element
  error: (props: SvgIconProps) => JSX.Element
  info: (props: SvgIconProps) => JSX.Element
}

export type NotificationProps = {
  open: boolean
  type: keyof VariantIcon
  message: string
  closeCallback: any
}

const variantIcon: VariantIcon = {
  success: CheckCircleIcon,
  warning: WarningIcon,
  error: ErrorIcon,
  info: InfoIcon
}

interface NotificationContentProps {
  classes: any
  className?: any
  message: string
  onClose: any
  variant: keyof VariantIcon
}

const styles = (theme: any) => ({
  success: {backgroundColor: theme.palette.notifications.success},
  error: {backgroundColor: theme.palette.notifications.error},
  info: {backgroundColor: theme.palette.notifications.info},
  warning: {backgroundColor: theme.palette.notifications.warning},
  icon: {fontSize: 20},
  iconVariant: {opacity: 0.9},
  message: {display: 'flex', alignItems: 'center'}
})

function MySnackbarContent(props: NotificationContentProps) {
  const {classes, className, message, onClose, variant, ...other} = props
  const Icon = variantIcon[variant]

  return (
    <SnackbarContent
      className={classNames(classes[variant], className)}
      aria-describedby="client-snackbar"
      message={
        <span
          id="client-snackbar"
          className={classes.message}
          style={{width: '230px'}}
        >
          <Icon
            className={classNames(classes.icon, classes.iconVariant)}
            style={{marginRight: '0.5rem'}}
          />
          {message}
        </span>
      }
      action={[
        <IconButton
          key="close"
          aria-label="Close"
          color="inherit"
          className={classes.close}
          onClick={onClose}
        >
          <CloseIcon className={classes.icon}/>
        </IconButton>
      ]}
      {...other}
    />
  )
}

const MySnackbarContentWrapper = withStyles(styles)(MySnackbarContent)

export class Notification extends Component<NotificationProps> {
  render() {
    const type: keyof VariantIcon = this.props.type

    return (
      <Snackbar
        open={this.props.open}
        autoHideDuration={4000}
        onClose={this.props.closeCallback}
        style={{margin: '0 auto', zIndex: 65536}}
      >
        <MySnackbarContentWrapper
          onClose={this.props.closeCallback}
          variant={type || 'info'}
          message={this.props.message}
        />
      </Snackbar>
    )
  }
}
