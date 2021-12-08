import React from 'react'
import {observer} from 'mobx-react'
import {IMessages, messages, StoredMessage, MessageAction} from 'system/messages'
import {gettext} from 'system/l10n'
import {Avatar, Backdrop, Box, Button, DateTimeText, MaterialIcon, IconButton, Typography} from 'system/components'


export type MessagesProps = {
  store: IMessages
}

type MessagesState = {
  clearAllConfirm: boolean
  clearAllConfirmTimer: any | null
}

type MessageProps = {
  message: StoredMessage
  closeAllConfirm: boolean
}

const Message = (props: MessageProps): React.ReactElement => {
  const {
    message,
    closeAllConfirm
  } = props

  return (
    <Button
      style={{
        margin: '8px 0',
        borderRadius: '.75vmax',
        backgroundColor: closeAllConfirm ? '#eee7' : '#eeec',
        display: 'block',
        maxWidth: '50vw',
        width: '100%',
        boxSizing: 'border-box',
        WebkitBackdropFilter: 'blur(3px)',
        backdropFilter: 'blur(3px)',
        border: closeAllConfirm ? '1px solid #d00' : '1px solid #0003',
        boxShadow: '0 0 3px #0002',
        padding: '6px',
        color: '#333',
        textTransform: 'none',
        textAlign: 'left'
      }}
      onClick={() => {
        if (message.action === undefined)
          return
        message.action(message)
      }}
    >
      <Box
        display={'flex'}
        alignItems={'flex-start'}
        boxSizing={'border-box'}
        flexGrow={1}
      >
        {message.icon !== undefined && message.icon !== '' && (
          <Box alignSelf={'flex-start'} padding={'8px'} boxSizing={'border-box'}>
            <Avatar src={message.icon.startsWith('/') ? message.icon : undefined}>
              {!message.icon.startsWith('/') && (
                <MaterialIcon icon={message.icon} />
              )}
            </Avatar>
          </Box>
        )}
        <Box padding={'8px'} boxSizing={'border-box'} flexGrow={1} style={{
          opacity: closeAllConfirm ? .2 : 1
        }}>
          {(message.title || message.timestamp) && (
            <Box display={'flex'} justifyContent={'flex-end'} alignItems={'flex-start'}>
              {message.title !== undefined && message.title !== '' && (
                <Typography variant={'body1'} fontWeight={600} flexGrow={1}>{message.title}</Typography>
              )}
              {message.timestamp !== undefined && message.timestamp !== null && (
                <Typography variant={'body2'} color={'#0007'} noWrap>
                  <DateTimeText value={message.timestamp} />
                </Typography>
              )}
            </Box>
          )}
          <Box>
            <Typography variant={'body1'}>{message.text}</Typography>
          </Box>
        </Box>
      </Box>
      {message.actions !== undefined && Array.isArray(message.actions) && message.actions.length > 0 && (
        <Box display={'flex'} justifyContent={'flex-end'} gap={'4px'}>
          {message.actions.map((el: MessageAction) => (
            <Button
              disabled={closeAllConfirm}
              variant={el.highlight ? 'outlined' : 'text'}
              size={'small'}
              style={{
                fontWeight: 400,
                backgroundColor: '#0001',
                fontSize: '.85em'
              }}
              onClick={(ev: React.MouseEvent) => {
                ev.stopPropagation()
                ev.preventDefault()
              }}
            >
              {el.caption}
            </Button>
          ))}
        </Box>
      )}
      <IconButton
        size={'small'}
        style={{
          position: 'absolute',
          left: '-.25vw',
          top: '-.25vw',
          zIndex: 2,
          backgroundColor: closeAllConfirm ? '#fffc' : undefined
        }}
        onClick={(ev: React.MouseEvent) => {
          ev.stopPropagation()
          ev.preventDefault()
          messages.close(message.id)
        }}
      >
        <MaterialIcon
          icon={'cancel'}
          color={closeAllConfirm ? '#d40' : '#0007'}
          size={closeAllConfirm ? 24 : 16}
        />
      </IconButton>
    </Button>
  )
}


class _Messages extends React.Component<MessagesProps, MessagesState> {
  state: MessagesState = {
    clearAllConfirm: false,
    clearAllConfirmTimer: null
  }

  private handleClearAllClick = (): void => {
    if (this.state.clearAllConfirm) {
      if (this.state.clearAllConfirmTimer !== null) {
        clearTimeout(this.state.clearAllConfirmTimer)
      }
      this.setState({
        clearAllConfirm: false,
        clearAllConfirmTimer: null
      })
      messages.closeAll()
    } else {
      this.setState({
        clearAllConfirm: true,
        clearAllConfirmTimer: setTimeout(() => this.setState({
          clearAllConfirm: false,
          clearAllConfirmTimer: null
        }), 3000)
      })
    }
  }

  private handleHideClick = (): void => {
    if (this.state.clearAllConfirmTimer !== null) {
      clearTimeout(this.state.clearAllConfirmTimer)
      this.setState({
        clearAllConfirm: false,
        clearAllConfirmTimer: null
      })
    }
    messages.hideBackdrop()
  }

  render() {
    return (
      <Backdrop
        id={'SystemUI-Messages-Backdrop'}
        open={this.props.store.open}
        onClick={(ev: React.MouseEvent) => {
          if ((ev.target as HTMLDivElement).id !== 'SystemUI-Messages-Backdrop')
            return
          this.handleHideClick()
        }}
        style={{
          zIndex: 9999,
          backgroundColor: '#f4f4f477',
          padding: '0 8px',
          overflowY: 'auto',
          display: 'block',
          WebkitBackdropFilter: 'blur(1px)',
          backdropFilter: 'blur(2px)',
        }}
      >
        {this.props.store.messages.length > 0 ? (
          <Box style={{
            width: '100%',
            maxWidth: '50vw',
            margin: '8px auto',
            boxSizing: 'border-box'
          }}>
            {this.props.store.messages.map((message: StoredMessage) => (
              <Message message={message} closeAllConfirm={this.state.clearAllConfirm} />
            ))}
          </Box>
        ) : (
          <Box style={{
            width: '100%',
            maxWidth: '50vw',
            margin: '8px auto',
            boxSizing: 'border-box',
            borderRadius: '.75vmax',
            backgroundColor: '#fffa',
            display: 'block',
            WebkitBackdropFilter: 'blur(3px)',
            backdropFilter: 'blur(3px)',
            // border: '1px solid #0003',
            // boxShadow: '0 0 3px #0002',
            padding: '32px',
            color: '#333',
            textTransform: 'none',
            textAlign: 'center'
          }}>
            {gettext("You have no messages requiring attention.", 'system')}
          </Box>
        )}
        <Box style={{
          position: 'sticky',
          bottom: 0,
          borderRadius: '.75vmax',
          display: 'flex',
          justifyContent: 'center',
          maxWidth: '50vw',
          width: '100%',
          margin: '0 auto 8px',
          boxSizing: 'border-box'
        }}>
          <Button
            variant={'contained'}
            size={'small'}
            style={{
              WebkitBackdropFilter: 'blur(3px)',
              backdropFilter: 'blur(3px)',
              backgroundColor: '#4685'
            }}
            onClick={this.handleHideClick}
          >
            {gettext('Hide', 'system')}
          </Button>
          {this.props.store.messages.length > 0 && (
            <Button
              color={this.state.clearAllConfirm ? 'error' : 'primary'}
              size={'small'}
              variant={'outlined'}
              style={{
                marginLeft: '4px',
                WebkitBackdropFilter: 'blur(3px)',
                backdropFilter: 'blur(3px)',
                backgroundColor: '#fffc',
                borderColor: this.state.clearAllConfirm ? '#d40b' : '#4685',
                color: this.state.clearAllConfirm ? '#d40' : '#468b'
              }}
              onClick={this.handleClearAllClick}
            >
              {gettext('Close all', 'system')}
            </Button>
          )}
        </Box>
      </Backdrop>
    )
  }
}

export const MessagesBar = observer(_Messages)
