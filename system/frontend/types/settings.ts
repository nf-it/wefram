import {FormCommonFieldItem} from 'system/types'


export type SettingsProperties = FormCommonFieldItem[]

export type SettingsEntity = {
  appName: string
  name: string
  caption?: string
  properties: SettingsProperties
}

export type SettingsEntities = SettingsEntity[]

export type SettingsTabSchema = {
  tabName: string
  tabCaption: string
  entities: SettingsEntities
}

export type SettingsSchema = SettingsTabSchema[]

export type SettingsPropsValuesUpdate = Record<string, any>
