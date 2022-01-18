import React from 'react'
import {
  Button,
  IconButton,
  ListItemIcon,
  ListItemText,
  MaterialIcon,
  MaterialIconVariant,
  MaterialIconColor,
  MaterialIconSize,
  Menu,
  MenuItem,
  Typography,
  RelIcon
} from 'system/components'


export type MenuButtonComponentType = 'button' | 'iconbutton'
export type MenuButtonSize = 'small' | 'medium' | 'large'
export type MenuButtonColor = 'inherit' | 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning'
export type MenuButtonItemColor = MenuButtonColor | string
export type MenuButtonVariant = 'text' | 'outlined' | 'contained'

export type MenuButtonItem = {
  caption: string
  clarification?: string
  color?: MenuButtonItemColor
  closeOnClick?: boolean
  disabled?: boolean
  icon?: string
  iconColor?: MenuButtonItemColor
  onClick?: (item: MenuButtonItem) => void
}
export type MenuButtonItems = MenuButtonItem[]

export type MenuButtonProps = {
  closeOnItemClick?: boolean
  color?: MenuButtonColor
  componentType?: MenuButtonComponentType
  disabled?: boolean
  icon?: string
  iconColor?: MaterialIconColor
  iconVariant?: MaterialIconVariant
  iconSize?: MaterialIconSize
  size?: MenuButtonSize
  items: MenuButtonItems
  itemsIconsSize?: MaterialIconSize
  style?: React.CSSProperties
  variant?: MenuButtonVariant
}

type MenuButtonState = {
  anchor: any
  open: boolean
}


export class MenuButton extends React.Component<MenuButtonProps, MenuButtonState> {
  state: MenuButtonState = {
    anchor: null,
    open: false
  }

  handleOpen = (e: React.MouseEvent): void => {
    this.setState({
      anchor: e.currentTarget,
      open: true
    })
  }

  handleClose = (): void => {
    this.setState({
      anchor: null,
      open: false
    })
  }

  render() {
    const icon: string = this.props.icon ?? 'menu'
    const componentType: MenuButtonComponentType = this.props.componentType ?? 'button'

    const Icon = (
      <MaterialIcon
        icon={icon}
        color={this.props.iconColor ?? this.props.color}
        size={this.props.iconSize ?? this.props.size}
        variant={this.props.iconVariant}
      />
    )

    const ButtonElement = (componentType === 'iconbutton') ? (
      <IconButton
        color={this.props.color}
        disabled={this.props.disabled}
        style={this.props.style}
        size={this.props.size}
        onClick={this.handleOpen}
      >
        {Icon}
      </IconButton>
    ) : (
      <Button
        color={this.props.color}
        disabled={this.props.disabled}
        style={this.props.style}
        variant={this.props.variant}
        size={this.props.size}
        onClick={this.handleOpen}
      >
        {Icon}
      </Button>
    )

    const hasIcons: boolean = this.props.items.filter((item: MenuButtonItem) => item.icon !== undefined).length > 0

    return (
      <React.Fragment>
        {ButtonElement}

        <Menu
          anchorEl={this.state.anchor}
          open={this.state.open}
          onClose={this.handleClose}
        >
          {this.props.items.map((item: MenuButtonItem) => (
            <MenuItem
              onClick={() => {
                if (item.onClick !== undefined) {
                  item.onClick(item)
                }
                if (item.closeOnClick !== false && this.props.closeOnItemClick !== false) {
                  this.handleClose()
                }
              }}
              disabled={item.disabled}
              style={{
                color: item.color
              }}
            >
              {hasIcons && (
                <ListItemIcon>
                  {item.icon !== undefined && (
                    <RelIcon icon={item.icon} size={this.props.itemsIconsSize ?? 24} />
                  )}
                </ListItemIcon>
              )}
              <ListItemText>{item.caption}</ListItemText>
              {item.clarification && (
                <Typography variant={'body2'} color={'text.secondary'}>{item.clarification}</Typography>
              )}
            </MenuItem>
          ))}
        </Menu>
      </React.Fragment>
    )
  }
}

