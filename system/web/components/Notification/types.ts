export interface NotificationState {
  title: string
  type: NotificationType
  opened: boolean
}

export enum NotificationType {
  Error = 'error',
  Warning = 'warning',
  Success = 'success'
}

export interface NotificationModel {
  title: string
  type: string
}

export interface NotificationPayload {
  payload: NotificationModel
  type: string
}

