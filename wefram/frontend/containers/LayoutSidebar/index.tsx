import React from 'react'
import {observer} from 'mobx-react'
import {
  Box,
  Drawer,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  MaterialIcon,
  Toolbar
} from 'system/components'
import LayoutAppbar from '../LayoutAppbar'
import {Link} from 'react-router-dom'
import {runtime} from 'system/runtime'
import {screensSchema} from 'build/screens'
import {routing} from 'system/routing'
import {dialog} from 'system/dialog'
import {messages, StoredMessage} from 'system/messages'
import {SidebarItemModel} from 'system/types'
import './index.css'


type TSidebarFolderOpen = Record<string, boolean>
type LayoutSidebarProps = { }
type LayoutSidebarState = {
  expandStatus: TSidebarFolderOpen
}


type SidebarItemProps = {
  item: SidebarItemModel
}


const SidebarItemInner = (props: SidebarItemProps) => (
  <ListItem
    button
    key={props.item.name}
    data-key={props.item.name}
    style={{
      backgroundColor: 'inherit'
    }}
    onClick={() => {
      if (props.item.endpoint === null)
        return
      // reserved for the future use with custom endpoint
    }}
  >
    <ListItemIcon>
      {props.item.icon !== null && (
        <img
          className={'SystemUI-LayoutSidebar-icon'}
          src={props.item.icon}
        />
      )}
    </ListItemIcon>
    <ListItemText primary={props.item.caption}/>
  </ListItem>
)


const SidebarItem = (props: SidebarItemProps) => {
  const item: SidebarItemModel = props.item
  if (!item.url)
    return null  // at this moment - endpoint are not supported

  switch (item.urlTarget) {
    case 'screen':
      return (
        <Link to={item.url} className={'SystemUI-LayoutSidebar-item'}>
          <SidebarItemInner item={item} />
        </Link>
      )
    case 'redirect':
      return (
        <a href={item.url} target={'_self'} className={'SystemUI-LayoutSidebar-item'}>
          <SidebarItemInner item={item} />
        </a>
      )
    default:  // blank
      return (
        <a href={item.url} target={'_blank'} className={'SystemUI-LayoutSidebar-item'}>
          <SidebarItemInner item={item} />
        </a>
      )
  }
}


class Sidebar extends React.Component<LayoutSidebarProps, LayoutSidebarState> {
  state: LayoutSidebarState = {
    expandStatus: {}
  }

  componentDidMount() {
    const expandStatus: TSidebarFolderOpen = JSON.parse(localStorage.getItem('sidebarExpandStatus') || '{}')
    this.setState({expandStatus})
  }

  handleSidebarFolderClick = (event: React.MouseEvent<HTMLElement>) => {
    const key: string = String(event.currentTarget.dataset.key)
    const expandStatus: TSidebarFolderOpen = this.state.expandStatus
    if (typeof expandStatus[key] === 'undefined') {
      expandStatus[key] = true
    } else {
      expandStatus[key] = !expandStatus[key]
    }
    this.setState({expandStatus})
    localStorage.setItem('sidebarExpandStatus', JSON.stringify(expandStatus))
  }

  render() {
    return (
      <Drawer
        className={'SystemUI-LayoutSidebar'}
        variant="permanent"
        classes={{
          paper: 'SystemUI-LayoutSidebar-paper',
        }}
      >
        <Toolbar />

        <LayoutAppbar />

        <Box className={'SystemUI-LayoutSidebar-container'}>
          <List>
            {runtime.sidebar.map(item => (
              <Box key={`sidebar-item-${item.name}`}>
                {(item.children !== null && item.children?.length > 0) ? (
                  <React.Fragment>
                    <ListItem
                      button
                      key={item.name}
                      data-key={item.name}
                      onClick={this.handleSidebarFolderClick}
                      className={'SystemUI-LayoutSidebar-item'}
                    >
                      <ListItemIcon>
                        {item.icon !== null && (
                          <img
                            className={'SystemUI-LayoutSidebar-icon'}
                            src={item.icon}
                          />
                        )}
                      </ListItemIcon>
                      <ListItemText primary={item.caption}/>
                      {
                        this.state.expandStatus[item.name]
                          ? <MaterialIcon icon={'expand_less'} />
                          : <MaterialIcon icon={'expand_more'} />
                      }
                    </ListItem>
                    <Collapse
                      in={this.state.expandStatus[item.name]}
                      timeout="auto"
                      unmountOnExit
                      className={'SystemUI-LayoutSidebar-folder'}
                    >
                      <List component="div" disablePadding>
                        {item.children.map(child => (
                          <Link to={screensSchema[child.screen]?.routeUrl} className={'SystemUI-LayoutSidebar-item'}>
                            <ListItem
                                button
                                key={child.name}
                                data-key={child.name}
                                dense
                                style={{
                                  backgroundColor: 'inherit'
                                }}
                            >
                              <ListItemIcon>
                                {child.icon !== null && (
                                  <img
                                    className={'SystemUI-LayoutSidebar-icon'}
                                    src={child.icon}
                                  />
                                )}
                              </ListItemIcon>
                              <ListItemText primary={child.caption}/>
                            </ListItem>
                          </Link>
                        ))}
                      </List>
                    </Collapse>
                  </React.Fragment>
                ) : (
                  <Link to={screensSchema[item.screen]?.routeUrl} className={'SystemUI-LayoutSidebar-item'}>
                    <ListItem
                      button
                      key={item.name}
                      data-key={item.name}
                      style={{
                        backgroundColor: 'inherit'
                      }}
                    >
                      <ListItemIcon>
                        {item.icon !== null && (
                          <img
                            className={'SystemUI-LayoutSidebar-icon'}
                            src={item.icon}
                          />
                        )}
                      </ListItemIcon>
                      <ListItemText primary={item.caption}/>
                    </ListItem>
                  </Link>
                )}
              </Box>
            ))}

            {!runtime.production && (
              <Box key={`sidebar-item-development__menu`}>
                <ListItem
                  button
                  key={'development__menu'}
                  data-key={'development__menu'}
                  onClick={this.handleSidebarFolderClick}
                  className={'SystemUI-LayoutSidebar-item'}
                >
                  <ListItemIcon>
                    <img
                      className={'SystemUI-LayoutSidebar-icon'}
                      src={routing.assetPath('system', 'icons/development.png')}
                    />
                  </ListItemIcon>
                  <ListItemText primary={'Development'}/>
                  {
                    this.state.expandStatus['development__menu']
                      ? <MaterialIcon icon={'expand_less'} />
                      : <MaterialIcon icon={'expand_more'} />
                  }
                </ListItem>
                <Collapse
                  in={this.state.expandStatus['development__menu']}
                  timeout="auto"
                  unmountOnExit
                  className={'SystemUI-LayoutSidebar-folder'}
                >
                  <List component="div" disablePadding>
                    <ListItem
                        button
                        key={'development__test_message'}
                        data-key={'development__test_message'}
                        dense
                        style={{
                          backgroundColor: 'inherit'
                        }}
                        onClick={() => {
                          dialog.prompt({
                            message: 'Enter message text',
                            okCallback: (value: string) => {
                              dialog.hide()
                              messages.append({
                                title: "Test message",
                                text: value,
                                icon: routing.assetPath('system', 'icons/development.png'),
                                action: (message: StoredMessage) => alert(message.id)
                              })
                            }
                          })
                        }}
                    >
                      <ListItemIcon>
                      </ListItemIcon>
                      <ListItemText primary={"Test message"}/>
                    </ListItem>
                  </List>
                </Collapse>
              </Box>
            )}
          </List>
        </Box>
      </Drawer>
    )
  }
}


const LayoutSidebar = observer(Sidebar)
export default LayoutSidebar
