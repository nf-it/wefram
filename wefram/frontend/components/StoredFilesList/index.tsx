import React from 'react'
import {
  Box,
  Button,
  Checkbox,
  CircularBusy,
  IconButton,
  MaterialIcon,
  Tooltip,
  Typography
} from 'system/components'
import {StoredFilesModel, StoredFileModel, StoredImageModel} from 'system/storage'
import {RequestApiPath} from 'system/routing'
import {api} from 'system/api'
import {gettext} from 'system/l10n'
import {notifications} from 'system/notification'
import {runtime} from 'system/project'
import {storage} from 'system/storage'
import {dialog} from 'system/dialog'
import './index.css'


export type StoredFilesListProps = {
  apiEntity: string
  dropAndDropUpload?: boolean
  minHeight?: any               /** Used mainly for drag&drop facility on full page height */
  multipleUpload?: boolean
  storageEntity: string
  permitDelete?: boolean
  permitEdit?: boolean
  permitUpload?: boolean
  permitRearrange?: boolean
}

type StoredFilesListState = {
  loading: boolean,
  items: StoredFilesModel,
  selected: number[]
  rearrangeMode: boolean
}


type RearrangeSortData = Record<number, number>


export class StoredFilesList extends React.Component<StoredFilesListProps, StoredFilesListState> {
  state: StoredFilesListState = {
    loading: true,
    items: [],
    selected: [],
    rearrangeMode: false
  }

  replacingId: number | null

  constructor(props: StoredFilesListProps, state: StoredFilesListState) {
    super(props, state);
    this.replacingId = null
  }

  private uploadFileInput: React.RefObject<HTMLInputElement> = React.createRef()
  private replaceFileInput: React.RefObject<HTMLInputElement> = React.createRef()

  componentDidMount() {
    this.load()
  }
  
  public load = (): void => {
    const path: RequestApiPath = this.requestPath()
    api.get(path).then(res => {
      const items: StoredFilesModel = res.data.filter((item: StoredImageModel) => item.file !== null)
      const ids: number[] = items.map((el: StoredFileModel) => el.id)
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

  public upload = (files: any[]): void => {
    const form: FormData = new FormData()
    if (files.length > 1) {
      form.append('isMultipleFileUpload', 'true')
      Array.from(files).forEach((file: any, index: number) => {
        form.append(`fileUploadData_${index}`, file)
      })
    } else {
      form.append('fileUploadData', files[0])
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

  private uploadFromInput = (fileInputData: any): void => {
    this.upload(Array.from(fileInputData.target.files))
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
    if (this.replacingId === null) {
      this.uploadFileInput.current?.click()
    } else {
      this.replaceFileInput.current?.click()
    }
  }

  private handleSelectAll = (): void => {
    const selected: number[] = []
    this.state.items
      .filter((item: StoredImageModel) => item.file !== null)
      .forEach((item: StoredImageModel) => {
        if (!this.state.selected.includes(item.id)) {
          selected.push(item.id)
        }
      })
    this.setState({selected})
  }

  private handleDragEnter = (ev: React.MouseEvent): void => {
    ev.preventDefault()
    ev.stopPropagation()
  }

  private handleDragOver = (ev: React.MouseEvent): void => {
    ev.preventDefault()
    ev.stopPropagation()
  }

  private handleDragDrop = (ev: React.DragEvent): void => {
    ev.preventDefault()
    ev.stopPropagation()
    if (!(this.props.dropAndDropUpload ?? true))
      return

    let files: any[] = []

    if (ev.dataTransfer.items) {
      for (let i = 0; i < ev.dataTransfer.items.length; i++) {
        if (ev.dataTransfer.items[i].kind !== 'file')
          continue
        files.push(ev.dataTransfer.items[i].getAsFile())
      }
    } else {
      files = Array.from(ev.dataTransfer.files)
    }

    this.upload(files)
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
        <Box
          minHeight={this.props.minHeight}
          onDragEnter={this.handleDragEnter}
          onDragOver={this.handleDragOver}
          onDrop={this.handleDragDrop}
        >
          <Box pt={3} pb={3} mb={2} borderTop={'1px solid #aaa'} borderBottom={'1px solid #aaa'}>
            <Typography>{gettext("There are no files uploaded yet.", 'system.ui')}</Typography>
          </Box>
          {(this.props.permitUpload ?? true) && (
            <Box display={'flex'} justifyContent={'flex-end'} alignItems={'center'}>
              <input
                type={'file'}
                ref={this.uploadFileInput}
                style={{display: 'none'}}
                onChange={this.uploadFromInput}
                multiple={this.props.multipleUpload ?? true}
              />
              <Tooltip title={gettext("Upload new image", 'system.ui')}>
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
            </Box>
          )}
        </Box>
      )

    return (
      <Box
        minHeight={this.props.minHeight}
        onDragEnter={this.handleDragEnter}
        onDragOver={this.handleDragOver}
        onDrop={this.handleDragDrop}
      >
        {((this.props.permitUpload ?? true) || (this.props.permitEdit ?? true)) && (
          <React.Fragment>
            <input
              type={'file'}
              ref={this.uploadFileInput}
              style={{display: 'none'}}
              onChange={this.uploadFromInput}
              multiple={this.props.multipleUpload ?? true}
            />
            <input
              type={'file'}
              ref={this.replaceFileInput}
              style={{display: 'none'}}
              onChange={this.uploadFromInput}
            />
          </React.Fragment>
        )}

        {((this.props.permitUpload ?? true)
            || (this.props.permitDelete ?? true)
            || (this.props.permitRearrange ?? true)
        ) && (
          <Box display={'flex'} justifyContent={'flex-end'} alignItems={'center'} mb={1}>
            {(this.props.permitDelete ?? true) && (!this.state.rearrangeMode) && (
              <React.Fragment>
                <Box flexGrow={1} paddingLeft={'2px'}>
                  <Tooltip title={gettext("Select all")}>
                    <IconButton
                      onClick={this.handleSelectAll}
                    >
                      <MaterialIcon icon={'select_all'} />
                    </IconButton>
                  </Tooltip>
                </Box>
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
              </React.Fragment>
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
                    <MaterialIcon icon={'swap_vert'} />
                  </IconButton>
                </Tooltip>
              </React.Fragment>
            )}
          </Box>
        )}


        {/** === The items enum === */}

        {this.state.items.map((item: StoredFileModel, index: number, arr: any) => (
          <Box borderTop={'1px solid #0001'}>
            <Box
              display={'flex'}
              alignItems={'center'}
              justifyContent={'space-between'}
            >
              {/** Item selection or file icon (depending on delete permission) */}
              {(this.props.permitDelete ?? true) ? (
                <Checkbox
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
              ) : (
                <MaterialIcon icon={'attach_file'} />
              )}

              {/** Filename or caption */}
              <Box flexGrow={1} marginLeft={'4px'} marginRight={'4px'}>
                <a
                  className={'SystemUI-StoredFilesList-Item-Filename'}
                  href={storage.urlFor(this.props.storageEntity, item.file)}
                  target={'_blank'}
                >
                  <Typography>{item.caption || item.file}</Typography>
                </a>
              </Box>

              {/** Item controls */}
              <Box display={'flex'} alignItems={'center'} justifyContent={'flex-end'}>
                {(this.props.permitEdit ?? true) && (!this.state.rearrangeMode) && (
                  <React.Fragment>
                  <Tooltip title={gettext("Rename file", 'system.ui')}>
                    <IconButton
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
                      onClick={() => {
                        this.removeFile(item.id)
                      }}
                    >
                      <MaterialIcon icon={'delete_outline'} />
                    </IconButton>
                  </Tooltip>
                )}
                {(this.state.rearrangeMode) && ([
                  <Tooltip key={`file-rearr-up-${item.id}`} title={gettext("Move up", 'system.ui')}>
                    <IconButton
                      onClick={() => {
                        const items = this.state.items
                        items.splice(index, 1)
                        items.splice(index - 1, 0, item)
                        items.forEach((el: StoredFileModel, inx: number) => el.sort = inx)
                        this.setState({items})
                      }}
                      disabled={index === 0}
                    >
                      <MaterialIcon icon={'keyboard_arrow_up'} />
                    </IconButton>
                  </Tooltip>,
                  <Tooltip key={`file-rearr-dn-${item.id}`} title={gettext("Move down", 'system.ui')}>
                    <IconButton
                      onClick={() => {
                        const items = this.state.items
                        items.splice(index, 1)
                        items.splice(index + 1, 0, item)
                        items.forEach((el: StoredFileModel, inx: number) => el.sort = inx)
                        this.setState({items})
                      }}
                      disabled={index === arr.length - 1}
                    >
                      <MaterialIcon icon={'keyboard_arrow_down'} />
                    </IconButton>
                  </Tooltip>
                ])}
              </Box>

            </Box>
          </Box>
        ))}
      </Box>
    )
  }
}

