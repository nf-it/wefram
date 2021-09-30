import React from 'react'
import {observer} from 'mobx-react'
import {Notification} from 'system/components'
import {INotification, notifications} from 'system/notification'


export type GlobalNotifyProps = {
  store: INotification
}

class _NotificationBar extends React.Component<GlobalNotifyProps> {
  render() {
    return (
      <Notification
        open={this.props.store.open}
        variant={this.props.store.variant}
        message={this.props.store.message}
        onClose={() => notifications.hide()}
      />
    )
  }
}

export const NotificationBar = observer(_NotificationBar)
