import React from 'react'
import {ScreensSchema} from '../types'


export const screensSchema: ScreensSchema = {
    "system_SettingsScreen": {
    "name": "system_SettingsScreen",
    "rootComponentPath": "system/containers/SettingsScreen",
    "rootComponent": React.lazy(() => import('system/containers/SettingsScreen')),
    "requires": [
      "system.settingsPropertiesAccess"
    ],
    "routeUrl": "/settings/system/properties",
    "routeParams": [],
    "params": {}
  },
  "system_UsersScreen": {
    "name": "system_UsersScreen",
    "rootComponentPath": "system/containers/UsersScreen",
    "rootComponent": React.lazy(() => import('system/containers/UsersScreen')),
    "requires": [
      "system.adminUsersRoles"
    ],
    "routeUrl": "/settings/system/users",
    "routeParams": [],
    "params": {}
  },
  "system_RolesScreen": {
    "name": "system_RolesScreen",
    "rootComponentPath": "system/containers/RolesScreen",
    "rootComponent": React.lazy(() => import('system/containers/RolesScreen')),
    "requires": [
      "system.adminUsersRoles"
    ],
    "routeUrl": "/settings/system/roles",
    "routeParams": [],
    "params": {}
  },
  "system_RoleScreen": {
    "name": "system_RoleScreen",
    "rootComponentPath": "system/containers/RoleScreen",
    "rootComponent": React.lazy(() => import('system/containers/RoleScreen')),
    "requires": [
      "system.adminUsersRoles"
    ],
    "routeUrl": "/settings/system/roles/:key",
    "routeParams": [
      "key"
    ],
    "params": {}
  },
  "club_Documents": {
    "name": "club_Documents",
    "rootComponentPath": "system/containers/StoredFilesScreen",
    "rootComponent": React.lazy(() => import('system/containers/StoredFilesScreen')),
    "requires": [
      "club.documents"
    ],
    "routeUrl": "/club/documents",
    "routeParams": [],
    "params": {
      "apiEntity": "club.Document",
      "storageEntity": "club.documents",
      "updatable": null
    }
  },
  "reserve_ReservationsList": {
    "name": "reserve_ReservationsList",
    "rootComponentPath": "project/reserve/screens/ReservationsList",
    "rootComponent": React.lazy(() => import('project/reserve/screens/ReservationsList')),
    "requires": [
      "reserve.reservations_actuals"
    ],
    "routeUrl": "/reserve/reservationslist",
    "routeParams": [],
    "params": {}
  },
  "system_Workspace": {
    "name": "system_Workspace",
    "rootComponentPath": "system/containers/DefaultWorkspace",
    "rootComponent": React.lazy(() => import('system/containers/DefaultWorkspace')),
    "requires": [],
    "routeUrl": "/workspace",
    "routeParams": [],
    "params": {}
  }
}
