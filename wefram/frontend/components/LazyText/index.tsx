import React from 'react'
import {api} from 'system/api'
import {notifications} from 'system/notification'
import {LazyTextVariant} from 'system/types'
import {Box, CircularProgress, FetchFailedBox, MarkdownText, Typography} from 'system/components'
import {AxiosResponse} from 'axios'


export type LazyTextProps = {
  altBaseUrl?: string
  appName: string
  baseUrl?: string
  textId: string
  variant?: LazyTextVariant
}

type LazyTextState = {
  content?: string | null
  variant?: LazyTextVariant
}

const apiVersion: number = 1


export class LazyText extends React.PureComponent<LazyTextProps, LazyTextState> {
  state: LazyTextState = {
    content: undefined,
    variant: undefined
  }

  componentDidMount() {
    this.fetch()
  }

  private applyResponseContent = (res: AxiosResponse): void => {
    const contentType: string = res.headers['content-type'].split(';')[0].trim().toLowerCase()
    let variant: LazyTextVariant | undefined
    switch (contentType) {
      case 'text/html':
        variant = 'html'
        break
      case 'text/markdown':
        variant = 'md'
        break
      default:
        variant = 'txt'
    }
    const content: string = String(res.data)
    this.setState({content, variant})
  }

  public fetch = (): void => {
    api.get({
      app: 'system',
      path: (this.props.baseUrl ?? '/text').concat('/', this.props.appName, '/', this.props.textId),
      version: apiVersion
    }, {
      params: { variant: this.props.variant }
    }).then(res => {
      this.applyResponseContent(res)
    }).catch(err => {
      if (this.props.altBaseUrl) {
        api.get({
          app: 'system',
          path: (this.props.altBaseUrl ?? '/text').concat('/', this.props.appName, '/', this.props.textId),
          version: apiVersion
        }, {
          params: { variant: this.props.variant }
        }).then(res => {
          this.applyResponseContent(res)
        }).catch(err => {
          this.setState({content: null, variant: undefined})
        })
      } else {
        this.setState({content: null, variant: undefined})
      }
    })
  }

  render() {
    if (this.state.content === undefined)
      return <CircularProgress />

    if (this.state.content === null)
      return <FetchFailedBox />

    if (this.state.variant === 'html') {
      return <Box dangerouslySetInnerHTML={{__html: this.state.content}} />
    } else if (this.state.variant === 'md') {
      return <MarkdownText text={this.state.content} />
    } else {
      return <Typography variant={'body1'}>{this.state.content}</Typography>
    }
  }
}
