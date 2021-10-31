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
import {LayoutAppbar} from '../LayoutAppbar'
import {Link} from 'react-router-dom'
import {runtime} from 'system/runtime'
import {screensSchema} from 'build/screens'
import './index.css'


type TSitemapFolderOpen = Record<string, boolean>
type LayoutSitemapProps = { }
type LayoutSitemapState = {
  expandStatus: TSitemapFolderOpen
}


class Sitemap extends React.Component<LayoutSitemapProps, LayoutSitemapState> {
  state: LayoutSitemapState = {
    expandStatus: {}
  }

  componentDidMount() {
    const expandStatus: TSitemapFolderOpen = JSON.parse(localStorage.getItem('sitemapExpandStatus') || '{}')
    this.setState({expandStatus})
  }

  handleSitemapFolderClick = (event: React.MouseEvent<HTMLElement>) => {
    const key: string = String(event.currentTarget.dataset.key)
    const expandStatus: TSitemapFolderOpen = this.state.expandStatus
    if (typeof expandStatus[key] === 'undefined') {
      expandStatus[key] = true
    } else {
      expandStatus[key] = !expandStatus[key]
    }
    this.setState({expandStatus})
    localStorage.setItem('sitemapExpandStatus', JSON.stringify(expandStatus))
  }

  render() {
    return (
      <Drawer
        className={'SystemUI-LayoutSitemap'}
        variant="permanent"
        classes={{
          paper: 'SystemUI-LayoutSitemap-paper',
        }}
        // style={{
        //   backgroundColor: '#253043',
        //   color: '#eee'
        // }}
      >
        <Toolbar />

        <LayoutAppbar />

        <div className={'SystemUI-LayoutSitemap-container'}>
          <List>
            {runtime.sitemap.map(item => (
              <Box key={`sitemap-item-${item.name}`}>
                {item.children !== null && item.children?.length > 0 && (
                  <React.Fragment>
                    <ListItem
                      button
                      key={item.name}
                      data-key={item.name}
                      onClick={this.handleSitemapFolderClick}
                      className={'SystemUI-LayoutSitemap-item'}
                    >
                      <ListItemIcon>
                        {item.icon !== null && (
                          <img
                            className={'SystemUI-LayoutSitemap-icon'}
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
                      className={'SystemUI-LayoutSitemap-folder'}
                    >
                      <List component="div" disablePadding>
                        {item.children.map(child => (
                          <Link to={screensSchema[child.screen]?.routeUrl} className={'SystemUI-LayoutSitemap-item'}>
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
                                    className={'SystemUI-LayoutSitemap-icon'}
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
                )}
                {item.children === null && (
                  <Link to={screensSchema[item.screen]?.routeUrl} className={'SystemUI-LayoutSitemap-item'}>
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
                            className={'SystemUI-LayoutSitemap-icon'}
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
          </List>
        </div>
      </Drawer>
    )
  }
}


export const LayoutSitemap = observer(Sitemap)
