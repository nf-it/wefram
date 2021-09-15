import React, {createRef} from 'react'
import {Link} from 'react-router-dom'
import {
  Avatar,
  Box,
  Checkbox,
  Divider,
  List,
  ListItem,
  ListItemAvatar,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction
} from 'system/components'
import {
  ListsSelection,
  ProvListProps,
} from './types'
import {ProvListsHoc} from './ProvListsHoc'
import {FieldItemData} from './FieldItemData'
import {CommonKey} from 'system/types'


type ProvListState = {
  loading: boolean
  items?: any[]
  selected?: ListsSelection
}


export class ProvList extends React.Component<ProvListProps, ProvListState> {
  state: ProvListState = {
    loading: true,
  }

  private hocRef = createRef<ProvListsHoc>()

  private handleCheckboxChange = (key: CommonKey): void => {
    const selected = (this.props.selected ?? this.state.selected ?? []) as any
    const checked = selected.includes(key)
    if (checked) {
      selected.splice(selected.indexOf(key), 1)
    } else {
      selected.push(key)
    }
    this.props.onSelection !== undefined
      ? this.props.onSelection(selected)
      : this.setState({selected})
  }

  public invertSelection = (): void => {
    const items = this.props.items ?? this.state.items ?? []
    const currentSelected = (this.props.selected ?? this.state.selected ?? []) as any
    const updatedSelected: any[] = []
    items.forEach(item => {
      const key: number | string | undefined =
        this.props.itemKeyField
          ? item[this.props.itemKeyField]
          : (item.key ?? item.id)
      if (key === undefined)
        return
      const selected: boolean = currentSelected.includes(key)
      if (!selected) {
        updatedSelected.push(key)
      }
    })
    this.props.onSelection !== undefined
      ? this.props.onSelection(updatedSelected)
      : this.setState({selected: updatedSelected})
  }

  private getItemAlt = (item: any): string | undefined => {
    if (typeof this.props.primaryField == 'string')
      return item[this.props.primaryField]
    return undefined
  }

  private getItemAvatarUrl = (item: any): string | null => {
    return this.props.avatarField && item[this.props.avatarField] !== undefined
      ? item[this.props.avatarField]
      : null
  }

  public fetch = (): void => {
    this.hocRef.current?.fetch()
  }

  render() {
    const
      items = (this.props.items ?? this.state.items) || []

    return (
      <ProvListsHoc
        ref={this.hocRef}
        onHocFetch={(state) => {
          this.setState({
            items: state.items
          })
        }}
        onHocInvertSelection={this.invertSelection}
        items={items}
        {...this.props}
      >
        <List className={'SystemUI-Lists List'}>
          {items.map((item, index) => {

            const
              keyRe = /{key}/g,
              key: number | string | undefined = this.props.itemKeyField
                ? item[this.props.itemKeyField]
                : (item.key ?? item.id),
              itemsRoute = this.props.itemsRoute,
              routePath: string | null =
                (key && itemsRoute)
                  ? (typeof itemsRoute == 'string'
                    ? String(itemsRoute).replace(keyRe, String(key))
                    : itemsRoute(item)
                  ) : null,
              divider: boolean = index < items.length - 1,
              primaryField: string = this.props.primaryField ?? 'caption',
              itemAltText: string | undefined = this.getItemAlt(item),
              avatarUrl: string | null = this.getItemAvatarUrl(item),
              selection = (this.props.selected ?? this.state.selected ?? []) as any[],
              selected: boolean = (key !== undefined && this.props.selectable && selection.length)
                ? selection.includes(key)
                : false

            const PrimaryFieldComponent = this.props.primaryComponent || FieldItemData
            const SecondaryFieldComponent = this.props.secondaryComponent || FieldItemData

            const ListItemComponent: React.ElementType | undefined = this.props.itemComponent
            const ListItemElement = ListItemComponent !== undefined
              ? (
                <ListItemComponent
                  item={item}
                  index={index}
                />
              ) : (
                <React.Fragment>
                  <ListItem button>
                    {avatarUrl !== null && (
                      <ListItemAvatar>
                        <Avatar alt={itemAltText} src={avatarUrl}/>
                      </ListItemAvatar>
                    )}
                    {key !== undefined && avatarUrl === null && this.props.selectable === true && (
                      <ListItemIcon>
                        <Checkbox
                          edge="start"
                          checked={selected}
                          tabIndex={-1}
                          disableRipple
                          inputProps={{'aria-labelledby': String(key)}}
                          value={key}
                          onClick={e => {
                            e.preventDefault()
                            e.stopPropagation()
                            this.handleCheckboxChange(key)
                          }}
                        />
                      </ListItemIcon>
                    )}

                    <ListItemText
                      primary={<PrimaryFieldComponent item={item} field={primaryField} />}
                      secondary={this.props.secondaryField && (
                        <SecondaryFieldComponent item={item} field={this.props.secondaryField} />
                      )}
                    />

                    {(key !== undefined && this.props.selectable && this.props.avatarField) && (

                      <ListItemSecondaryAction>
                        <Checkbox
                          edge="start"
                          checked={selected}
                          tabIndex={-1}
                          disableRipple
                          inputProps={{'aria-labelledby': String(key)}}
                          onClick={e => {
                            e.stopPropagation()
                          }}
                          onChange={() => this.handleCheckboxChange(key)}
                        />
                      </ListItemSecondaryAction>
                    )}

                  </ListItem>
                  {divider && <Divider />}
                </React.Fragment>
              )

            return routePath
              ? <Link to={routePath} className={'SystemUI-Lists RouteLink'}>{ListItemElement}</Link>
              : this.props.onItemClick !== undefined
                ? <Box onClick={() => this.props.onItemClick && this.props.onItemClick(item)}>{ListItemElement}</Box>
                : <React.Fragment>{ListItemElement}</React.Fragment>
          })}
        </List>
      </ProvListsHoc>
    )
  }
}
