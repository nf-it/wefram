import React from 'react'
import {
  Box,
  Button,
  Checkbox,
  CircularBusy,
  IconButton,
  ImageList,
  ImageListItem,
  ImageListItemBar,
  MaterialIcon,
  Tooltip,
  Typography
} from 'system/components'
import {StoredImagesModel, StoredImageModel} from 'system/types'
import {RequestApiPath} from 'system/routing'
import {api} from 'system/api'
import {gettext} from 'system/l10n'
import {notifications} from 'system/notification'
import {runtime} from 'system/runtime'
import {storage} from 'system/storage'
import {dialog} from 'system/dialog'


export type StoredImagesListProps = {
  apiEntity: string
  storageEntity: string
  columns?: number
  rowHeight?: 'auto' | number
  gap?: number
  permitDelete?: boolean
  permitEdit?: boolean
  permitUpload?: boolean
  permitRearrange?: boolean
  showCaption?: boolean
  showControls?: boolean
}

type StoredImagesListState = {
  loading: boolean,
  items: StoredImagesModel,
  selected: number[]
  rearrangeMode: boolean
}


type RearrangeSortData = Record<number, number>


export class StoredImagesList extends React.Component<StoredImagesListProps, StoredImagesListState> {
  state: StoredImagesListState = {
    loading: true,
    items: [],
    selected: [],
    rearrangeMode: false
  }

  replacingId: number | null

  constructor(props: StoredImagesListProps, state: StoredImagesListState) {
    super(props, state);
    this.replacingId = null
  }

  private fileinput: React.RefObject<HTMLInputElement> = React.createRef()

  componentDidMount() {
    this.load()
  }
  
  public load = (): void => {
    const path: RequestApiPath = this.requestPath()
    api.get(path).then(res => {
      const items: StoredImagesModel = res.data
      const ids: number[] = items.map((el: StoredImageModel) => el.id)
      const selected: number[] = this.state.selected.filter((el: number) => ids.includes(el))
      this.setState({
        items,
        selected,
        loading: false
      })
    }).catch(err => {
      notifications.showRequestError(err)
      this.setState({loading: false})
    })
  }

  private requestPath = (id?: number | null, suffix?: string): RequestApiPath => {
    let app: string
    let path: string
    [app, path] = this.props.apiEntity.split('.', 2)
    return {
      app,
      path: (id ? `${path}/${id}` : path) + (suffix ? suffix : '')
    }
  }

  public postRearragement = (): void => {
    runtime.setBusy()
    const data: RearrangeSortData = {}
    this.state.items.forEach(el => data[el.id] = el.sort)
    api.put(this.requestPath(null, '/reorder'), data).then(res => {
      runtime.dropBusy()
      notifications.showRequestSuccess(res)
    }).catch(err => {
      runtime.dropBusy()
      notifications.showRequestError(err)
    })
  }

  public removeFile = (id: number): void => {
    dialog.showConfirm({
      okCallback: () => {
        dialog.hide()
        runtime.setBusy()
        api.delete(this.requestPath(id)).then(() => {
          runtime.dropBusy()
          notifications.showSuccess()
          this.load()
        }).catch(err => {
          runtime.dropBusy()
          notifications.showRequestError(err)
        })
      }
    })
  }

  public removeFiles = (): void => {
    if (!this.state.selected.length)
      return
    const keys: number[] = this.state.selected
    dialog.showConfirm({
      okCallback: () => {
        dialog.hide()
        runtime.setBusy()
        api.delete(this.requestPath(), {params: {keys}}).then(() => {
          runtime.dropBusy()
          notifications.showSuccess()
          this.load()
        }).catch(err => {
          runtime.dropBusy()
          notifications.showRequestError(err)
        })
      }
    })
  }

  private upload = (data: any): void => {
    const form: FormData = new FormData()
    if (data.target.files.length > 1) {
      data.target.files.forEach((file: any, index: number) => {
        form.append(`file${index}`, file)
      })
    } else {
      form.append('file', data.target.files[0])
    }
    runtime.setBusy()

    const requestPath: RequestApiPath = this.requestPath(this.replacingId)
    if (this.replacingId !== null) {
      api.put(requestPath, form).then(() => {
        runtime.dropBusy()
        notifications.showSuccess()
        this.load()
      }).catch(err => {
        runtime.dropBusy()
        notifications.showRequestError(err)
      })
    } else {
      api.post(requestPath, form).then(() => {
        runtime.dropBusy()
        notifications.showSuccess()
        this.load()
      }).catch(err => {
        runtime.dropBusy()
        notifications.showRequestError(err)
      })
    }
  }

  public renameFile = (id: number, caption: string): void => {
    runtime.setBusy()
    api.put(this.requestPath(id), {caption}).then(() => {
      runtime.dropBusy()
      notifications.showSuccess()
      this.load()
    }).catch(err => {
      runtime.dropBusy()
      notifications.showRequestError(err)
    })
  }

  private selectFileForUpload = (id?: number): void => {
    this.replacingId = id || null
    this.fileinput.current?.click()
  }

  render() {
    if (this.state.loading)
      return (
        <Box display={'flex'} justifyContent={'center'}>
          <CircularBusy />
        </Box>
      )

    if (!this.state.items.length)
      return (
        <Box pt={3} pb={3} borderTop={'1px solid #aaa'} borderBottom={'1px solid #aaa'}>
          <Typography>{gettext("There are no files uploaded yet.", 'system.ui')}</Typography>
        </Box>
      )

    return (
      <Box>
        {((this.props.permitUpload ?? true) || (this.props.permitEdit ?? true)) && (
          <input
            type={'file'}
            ref={this.fileinput}
            style={{display: 'none'}}
            onChange={this.upload}
          />
        )}

        {((this.props.permitUpload ?? true)
            || (this.props.permitDelete ?? true)
            || (this.props.permitRearrange ?? true)
        ) && (
          <Box display={'flex'} justifyContent={'flex-end'} alignItems={'center'}>
            {(this.props.permitDelete ?? true) && (!this.state.rearrangeMode) && (
              <Tooltip title={gettext("Delete selected files")}>
                <IconButton
                  color={'secondary'}
                  disabled={!this.state.selected.length}
                  onClick={() => {
                    this.removeFiles()
                  }}
                >
                  <MaterialIcon icon={'delete_outline'} />
                </IconButton>
              </Tooltip>
            )}
            {(this.props.permitUpload ?? true) && (!this.state.rearrangeMode) && (
              <Tooltip title={gettext("Delete selected files")}>
                <Button
                  color={'primary'}
                  variant={'outlined'}
                  startIcon={<MaterialIcon icon={'publish'} />}
                  style={{
                    marginLeft: '8px'
                  }}
                  onClick={() => this.selectFileForUpload()}
                >
                  {gettext("Upload", 'system.ui')}
                </Button>
              </Tooltip>
            )}
            {(this.props.permitRearrange ?? true) && (
              <React.Fragment>
                {this.state.rearrangeMode && (
                  <Typography>{gettext("Rearrange files and click the button again", 'system.ui')}</Typography>
                )}
                <Tooltip title={gettext("Rearrange files", 'system.ui')}>
                  <IconButton
                    color={this.state.rearrangeMode ? 'secondary' : 'default'}
                    onClick={() => this.setState(
                      {rearrangeMode: !this.state.rearrangeMode},
                      () => {
                        (!this.state.rearrangeMode) && this.postRearragement()
                      }
                    )}
                    style={{
                      marginLeft: '24px'
                    }}
                  >
                    <MaterialIcon icon={'swap_horiz'} />
                  </IconButton>
                </Tooltip>
              </React.Fragment>
            )}
          </Box>
        )}

        <ImageList cols={this.props.columns} gap={this.props.gap ?? 4} rowHeight={this.props.rowHeight} variant={'quilted'}>
          {this.state.items.map((item: StoredImageModel, index: number, arr: any[]) => {
            const showControls: boolean = this.state.rearrangeMode || (this.props.showControls !== undefined
                ? Boolean(this.props.showControls)
                : (this.props.permitDelete ?? true)
            )

            return (
              <ImageListItem>
                <img src={storage.urlFor(this.props.storageEntity, item.file)} alt={item.caption} />
                {(this.props.showCaption ?? true) && item.caption !== undefined && item.caption !== '' && (
                  <ImageListItemBar
                    position={'bottom'}
                    title={item.caption}
                  />
                )}
                {showControls && (
                  <ImageListItemBar
                    position={'top'}
                    actionIcon={
                      <React.Fragment>
                        {(!this.state.rearrangeMode) && (
                          <Tooltip title={gettext("Open file", 'system.ui')}>
                            <IconButton
                              style={{
                                color: '#eee'
                              }}
                              onClick={() => {
                                window.open(storage.urlFor(this.props.storageEntity, item.file), '_blank')
                              }}
                            >
                              <MaterialIcon icon={'open_in_new'} />
                            </IconButton>
                          </Tooltip>
                        )}

                        {(this.props.permitEdit ?? true) && (!this.state.rearrangeMode) && (
                          <React.Fragment>
                          <Tooltip title={gettext("Rename file", 'system.ui')}>
                            <IconButton
                              style={{
                                color: '#eee'
                              }}
                              onClick={() => {
                                dialog.prompt({
                                  defaultValue: item.caption,
                                  okCallback: (value: string) => {
                                    dialog.hide()
                                    if (!value)
                                      return
                                    this.renameFile(item.id, value)
                                  }
                                })
                              }}
                            >
                              <MaterialIcon icon={'edit'} />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title={gettext("Replace file", 'system.ui')}>
                            <IconButton
                              style={{
                                color: '#eee'
                              }}
                              onClick={() => {
                                this.selectFileForUpload(item.id)
                              }}
                            >
                              <MaterialIcon icon={'publish'} />
                            </IconButton>
                          </Tooltip>
                          </React.Fragment>
                        )}

                        {(this.props.permitDelete ?? true) && (!this.state.rearrangeMode) && (
                          <Tooltip title={gettext("Delete file", 'system.ui')}>
                            <IconButton
                              style={{
                                color: '#eee'
                              }}
                              onClick={() => {
                                this.removeFile(item.id)
                              }}
                            >
                              <MaterialIcon icon={'delete_outline'} />
                            </IconButton>
                          </Tooltip>
                        )}

                        {(this.state.rearrangeMode) && ([
                          <Tooltip key={`file-rearr-up-${item.id}`} title={gettext("Move before", 'system.ui')}>
                            <IconButton
                              style={{
                                color: index === 0 ? '#eee3' : '#eee'
                              }}
                              onClick={() => {
                                const items = this.state.items
                                items.splice(index, 1)
                                items.splice(index - 1, 0, item)
                                items.forEach((el: StoredImageModel, inx: number) => el.sort = inx)
                                this.setState({items})
                              }}
                              disabled={index === 0}
                            >
                              <MaterialIcon icon={'arrow_back'} />
                            </IconButton>
                          </Tooltip>,
                          <Tooltip key={`file-rearr-dn-${item.id}`} title={gettext("Move after", 'system.ui')}>
                            <IconButton
                              style={{
                                color: index === arr.length - 1 ? '#eee3' : '#eee'
                              }}
                              onClick={() => {
                                const items = this.state.items
                                items.splice(index, 1)
                                items.splice(index + 1, 0, item)
                                items.forEach((el: StoredImageModel, inx: number) => el.sort = inx)
                                this.setState({items})
                              }}
                              disabled={index === arr.length - 1}
                            >
                              <MaterialIcon icon={'arrow_forward'} />
                            </IconButton>
                          </Tooltip>
                        ])}

                        {(!this.state.rearrangeMode) && (this.props.permitDelete ?? true) && (
                          <Checkbox
                            style={{
                              color: '#fa0'
                            }}
                            checked={this.state.selected.includes(item.id)}
                            onChange={(ev: React.ChangeEvent<HTMLInputElement>) => {
                              let selected: number[] = this.state.selected
                              if (ev.target.checked) {
                                selected.push(item.id)
                              } else {
                                selected = selected.filter((el: number) => el != item.id)
                              }
                              this.setState({selected})
                            }}
                          />
                        )}
                      </React.Fragment>
                    }
                  />
                )}
              </ImageListItem>
            )
          })}
        </ImageList>

      </Box>
    )
  }
}

