
export type StoredFile = {
  id: number
  createdAt: string
  sort: number
  caption: string
  file: string
}

export type StoredFiles = StoredFile[]

export type StoredImage = {
  id: number
  createdAt: string
  sort: number
  caption: string
  file: string
}

export type StoredImages = StoredImage[]
