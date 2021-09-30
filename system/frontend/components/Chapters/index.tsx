import React from 'react'
import {arrayFrom} from 'system/tools'
import {Box, TranslatedText, Tabs, Tab, Typography} from 'system/components'
import {TranslatedTextVariant} from 'system/types'


export type ChapterProps = {
  caption: string
  children: JSX.Element | JSX.Element[]
  title?: boolean | string
}

export type FetchableChapterProps = {
  appName: string
  caption: string
  textId: string
  title?: boolean | string
  variant?: TranslatedTextVariant
}

export type ChaptersProps = {
  children: JSX.Element | JSX.Element[]
}

type ChaptersState = {
  tab: number
}


export const Chapter = (props: ChapterProps) => {
  return (
    <Box>
      {((props.title ?? true) !== false) && (props.caption !== '' || typeof props.title == 'string') && (
        <Typography variant={'h4'} color={'primary'} gutterBottom>
          {(typeof props.title == 'string') ? props.title : props.caption}
        </Typography>
      )}
      {props.children}
    </Box>
  )
}


export const TranslatedChapter = (props: FetchableChapterProps) => {
  return (
    <Chapter caption={props.caption}>
      <TranslatedText appName={props.appName} textId={props.textId} variant={props.variant} />
    </Chapter>
  )
}


export class Chapters extends React.PureComponent<ChaptersProps, ChaptersState> {
  state: ChaptersState = {
    tab: 0
  }

  private _tabCaptionFromElement = (element: any): string => {
    return element?.caption || '...'
  }

  render() {
    const children = arrayFrom(this.props.children)
    return (
      <React.Fragment>
        {children.length > 1 && (
          <Tabs
            indicatorColor="primary"
            textColor="primary"
            onChange={(ev, tab) => this.setState({tab})}
            value={this.state.tab}
          >
            {React.Children.map(children, (element: any, index: number) => (
              <Tab label={this._tabCaptionFromElement(element)} value={index} />
            ))}
          </Tabs>
        )}
        {children.map((chapter: any, index: number) => (
          <Box hidden={this.state.tab !== index}>
            {chapter}
          </Box>
        ))}
      </React.Fragment>
    )
  }
}
