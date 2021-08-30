import React from 'react'
import Image from 'material-ui-image'
import {
  Backdrop,
  Box,
  Button,
  IconButton,
  Modal
} from '@material-ui/core'
import CloseIcon from '@material-ui/icons/CloseRounded'
import ClearIcon from '@material-ui/icons/DeleteForeverRounded'
import UploadIcon from '@material-ui/icons/CloudUploadRounded'
import {storage} from '../../storage'
import {RequestApiPath, routing} from '../../routing'
import {api} from '../../api'
import {notifications} from '../../notification'
import {runtime} from '../../runtime'
import {gettext} from '../../l10n'
import {dialog} from '../../dialog'
import './index.css'


export type StoredImageProps = {
  entity: string
  fileId?: string | null

  cover?: boolean
  defaultFileId?: string | null
  dirty?: boolean
  emptyUrl?: string | null
  instantUpdate?: boolean
  permitClean?: boolean
  permitUpload?: boolean
  height?: string
  width?: string
  style?: any

  onChange?: (fileId: string | null) => void
}

type S = {
  openViewer: boolean
  openUpload: boolean
  openClear: boolean
  fileId?: string | null
}

export class StoredImage extends React.Component<StoredImageProps, S> {
  state: S = {
    openViewer: false,
    openUpload: false,
    openClear: false
  }

  private imageinput: React.RefObject<HTMLInputElement> = React.createRef()

  private clearImage = (): void => {
    const currentFileId: string | null = this.currentFileId
    const update: boolean = Boolean(this.state.fileId) || ((this.props.instantUpdate ?? false) && currentFileId !== null)
    this.setState({
      openViewer: false,
      fileId: null
    }, () => {
      this.props.onChange !== undefined && this.props.onChange(null)
    })
    if (update) {
      const url: RequestApiPath = {
        app: 'system',
        path: `storage/${this.props.entity}/file/${currentFileId}`
      }
      runtime.busy = true
      api.delete(url).then(() => {
        runtime.busy = false
      }).catch(err => {
        runtime.busy = false
        notifications.showRequestError(err)
      })
    }
  }

  private uploadImage = (data: any): void => {
    const currentFileId: string | null = this.currentFileId
    const update: boolean =
      (Boolean(this.state.fileId) || ((this.props.instantUpdate ?? false) && currentFileId !== null))
      && this.props.dirty === true
    const url: RequestApiPath = update
      ? {app: 'system', path: `storage/${this.props.entity}/file/${currentFileId}`}
      : {app: 'system', path: `storage/${this.props.entity}/file`}
    const form: FormData = new FormData()
    form.append('file', data.target.files[0])

    runtime.busy = true
    this.setState({openViewer: false})

    if (update) {
      api.put(url, form).then(res => {
        const newFileId: string = (res.statusCode !== 204 && res.data)
          ? res.data
          : currentFileId
        runtime.busy = false
        this.setState({
          fileId: newFileId
        }, () => {this.props.onChange !== undefined && this.props.onChange(newFileId)})
      }).catch(err => {
        notifications.showRequestError(err)
      })

    } else {
      api.post(url, form).then(res => {
        const newFileId: string = res.data
        runtime.busy = false
        this.setState({
          fileId: newFileId
        }, () => {this.props.onChange !== undefined && this.props.onChange(newFileId)})
      }).catch(err => {
        notifications.showRequestError(err)
      })
    }
  }

  private selectFile = (): void => {
    this.imageinput.current?.click()
  }

  private get currentFileId(): string | null {
    return (
      this.props.fileId !== undefined
        ? this.props.fileId
        : (this.state.fileId !== undefined ? this.state.fileId : this.props.defaultFileId)
    ) || null
  }

  render() {
    const fileId: string | null = this.currentFileId
    const height: string = this.props.height ?? '10vmax'
    const width: string | undefined = this.props.width
    const emptyUrl: string | null =
      this.props.emptyUrl === null
        ? null
        : this.props.emptyUrl
          ?? (routing.mediaAssetPath('system', this.props.permitUpload ? 'image-upload.svg' : 'image.svg'))
    const style: any = this.props.style ?? {}
    style.height = height
    if (width) {
      style.width = width
    }

    return (
      <React.Fragment>
        {this.props.permitUpload && (
          <input
            type={'file'}
            ref={this.imageinput}
            style={{display: 'none'}}
            onChange={this.uploadImage}
          />
        )}
        {fileId === null && (
          <Box
              className={`SystemUI-StoredImage-Empty ${this.props.permitUpload && 'clickable'}`}
              style={style}
              onClick={this.props.permitUpload ? this.selectFile : undefined}
          >
            <Box style={{
              backgroundImage: `url(${emptyUrl})`
            }} />
          </Box>
        )}
        {fileId !== null && (
          <Box
              className={'SystemUI-StoredImage-Picture'}
              style={style}
              onClick={() => this.setState({openViewer: true})}
          >
            <Image
              src={storage.urlFor(this.props.entity, fileId)}
              style={{
                backgroundColor: 'transparent',
                padding: null,
                paddingTop: null,
                position: 'absolute'
              }}
              imageStyle={{
                width: null,
                height: null,
                position: 'relative',
                overflow: 'hidden',
                maxWidth: '100%',
                maxHeight: '100%',
                borderRadius: '.5vmax'
              }}
              cover={this.props.cover}
            />
          </Box>
        )}
        <Modal
            open={this.state.openViewer && fileId !== null}
            onClose={() => this.setState({openViewer: false})}
        >
          <Backdrop
              open={this.state.openViewer && fileId !== null}
              style={{
                zIndex: 10000
              }}
          >
            {this.state.openViewer && fileId !== null && (
              <Box className={'SystemUI-StoredImage-Viewer'}>
                <Box className={'_controls'}>
                  {this.props.permitUpload && (
                    <Button
                      startIcon={<UploadIcon />}
                      style={{
                        color: '#ea0',
                        marginRight: '1vmax'
                      }}
                      onClick={this.selectFile}
                    >{gettext("Replace", 'system.ui')}</Button>
                  )}
                  {this.props.permitClean && (
                    <Button
                      startIcon={<ClearIcon />}
                      style={{
                        color: '#e66',
                        marginRight: '1vmax'
                      }}
                      onClick={() => {
                        dialog.showConfirm({
                          message: gettext("Are you sure you want to clean up delete this image?", 'system.ui'),
                          captionOK: gettext("Delete"),
                          defaultOK: false,
                          colorOK: 'secondary',
                          highlightOK: true,
                          okCallback: () => {
                            dialog.hide()
                            this.clearImage()
                          }
                        })
                      }}
                    >{gettext("Clear", 'system.ui')}</Button>
                  )}
                  <IconButton
                    onClick={() => this.setState({openViewer: false})}
                    size={'small'}
                    style={{color: '#ddd'}}
                  >
                    <CloseIcon />
                  </IconButton>
                </Box>
                <Box className={'_container'} onClick={() => this.setState({openViewer: false})}>
                  <Image
                    src={storage.urlFor(this.props.entity, fileId)}
                    style={{
                      backgroundColor: 'transparent',
                      padding: null,
                      paddingTop: null,
                      position: 'absolute'
                    }}
                    imageStyle={{
                      width: null,
                      height: null,
                      position: 'relative',
                      overflow: 'hidden',
                      maxWidth: '100%',
                      maxHeight: '100%',
                      borderRadius: '.5vmax'
                    }}
                  />
                </Box>
              </Box>
            )}
          </Backdrop>
        </Modal>
      </React.Fragment>
    )
  }
}
