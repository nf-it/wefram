import {RequestApiPath, routing} from 'system/routing'
import {Storage, StoredFileModel, StoredFilesModel} from './types'


export const storage: Storage = {
  urlFor(entity, fileId) {
    if (fileId.startsWith('/'))
      return routing.assetAbspath(fileId)
    return `/files/${entity}/${fileId}`
  },

}
