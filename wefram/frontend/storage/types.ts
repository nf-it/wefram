
export type StoredFileModel = {
  id: number
  createdAt: string
  sort: number
  caption: string
  file: string
}

export type StoredFilesModel = StoredFileModel[]

export type StoredImageModel = {
  id: number
  createdAt: string
  sort: number
  caption: string
  file: string
}

export type StoredImagesModel = StoredImageModel[]


export type Storage = {
  urlFor(entity: string, fileId: string): string
}

