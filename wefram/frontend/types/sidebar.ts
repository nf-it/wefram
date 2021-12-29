export type SidebarChildItemModel = {
  name: string
  caption: string
  order: number
  url?: string
  urlTarget?: 'screen' | 'blank' | 'redirect' | 'container'
  endpoint?: string
  icon: string | null
}

export type SidebarItemModel = {
  name: string
  caption: string
  order: number
  url?: string
  urlTarget?: 'screen' | 'blank' | 'redirect' | 'container'
  endpoint?: string
  icon: string | null
  children?: SidebarChildItemModel[] | null
}

export type SidebarConfiguration = SidebarItemModel[]
