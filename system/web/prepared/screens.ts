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
  "system_AuthBackendAdDomainsScreen": {
    "name": "system_AuthBackendAdDomainsScreen",
    "rootComponentPath": "system/containers/AuthBackendAdDomains",
    "rootComponent": React.lazy(() => import('system/containers/AuthBackendAdDomains')),
    "requires": [
      "system.adminUsersRoles"
    ],
    "routeUrl": "/settings/system/auth/domains",
    "routeParams": [],
    "params": {}
  },
  "reserve_ReservationsActuals": {
    "name": "reserve_ReservationsActuals",
    "rootComponentPath": "project/reserve/frontend/containers/ReservationsActuals",
    "rootComponent": React.lazy(() => import('project/reserve/frontend/containers/ReservationsActuals')),
    "requires": [
      "reserve.reservations_actuals"
    ],
    "routeUrl": "/reserve/reservationsactuals",
    "routeParams": [],
    "params": {}
  },
  "reserve_ReservationsHistory": {
    "name": "reserve_ReservationsHistory",
    "rootComponentPath": "project/reserve/frontend/containers/ReservationsHistory",
    "rootComponent": React.lazy(() => import('project/reserve/frontend/containers/ReservationsHistory')),
    "requires": [
      "reserve.reservations_history"
    ],
    "routeUrl": "/reserve/reservationshistory",
    "routeParams": [],
    "params": {}
  },
  "services_ReservationsActuals": {
    "name": "services_ReservationsActuals",
    "rootComponentPath": "project/services/frontend/containers/Services",
    "rootComponent": React.lazy(() => import('project/services/frontend/containers/Services')),
    "requires": [
      "services.manage"
    ],
    "routeUrl": "/services/reservationsactuals",
    "routeParams": [],
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
  "club_Gallery": {
    "name": "club_Gallery",
    "rootComponentPath": "system/containers/StoredImagesScreen",
    "rootComponent": React.lazy(() => import('system/containers/StoredImagesScreen')),
    "requires": [
      "club.gallery"
    ],
    "routeUrl": "/club/gallery",
    "routeParams": [],
    "params": {
      "apiEntity": "club.Picture",
      "storageEntity": "club.gallery",
      "updatable": null,
      "columns": 4,
      "rowHeight": 240,
      "gap": 4
    }
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
