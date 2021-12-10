import {RequestApiPath, routing} from 'system/routing'
import {StoredFileModel, StoredFilesModel} from 'system/types'


export type Storage = {
  urlFor(entity: string, fileId: string): string
}

export const storage: Storage = {
  urlFor(entity, fileId) {
    if (fileId.startsWith('/'))
      return routing.assetAbspath(fileId)
    return `/files/${entity}/${fileId}`
  },

}
