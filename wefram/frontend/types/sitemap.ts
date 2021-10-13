export type ISitemapChild = {
  name: string
  caption: string
  order: number
  screen: string
  icon: string | null
}

export type ISitemap = {
  name: string
  caption: string
  order: number
  screen: string
  icon: string | null
  children: ISitemapChild[] | null
}[]
