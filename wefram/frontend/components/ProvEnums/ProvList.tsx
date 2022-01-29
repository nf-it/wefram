import React, {createRef} from 'react'
import {Link} from 'react-router-dom'
import {
  Avatar,
  Box,
  ButtonBase,
  Card,
  CardActions,
  CardHeader,
  CardContent,
  Checkbox,
  Divider,
  Gridbox,
  List,
  ListItem,
  ListItemAvatar,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction
} from 'system/components'
import {
  EnumField,
  EnumsSelection,
  ProvListProps,
} from './types'
import {ProvEnumsHoc} from './ProvEnumsHoc'
import {FieldItemData} from './FieldItemData'
import {CommonKey} from 'system/types'
import {isCompactScreen, colorByString} from 'system/tools'
import {routing} from 'system/routing'
import {storage} from 'system/storage'


type ProvListState = {
  /**
   * @property compactScreen - `true` if the current screen width comforms to the compact,
   *    mobile device dimensions; `false` otherwise.
   * @property loading - `true` (initially = true) when loading items
   * @property items - the fetched from backend items array
   * @property selected - the array of selected items' keys
   */
  compactScreen: boolean
  loading: boolean
  items?: any[]
  selected?: EnumsSelection
}


type ProvListItemPrepared = {
  /**
   * @property key - the item's key (UuidKey or string | number)
   * @property routePath - the item's URL for link element, if the item click routes to the another screen
   * @property divider - do render the divider after this item?
   * @property primaryField - the item's primary field struct or null
   * @property secondaryField - the item's secondary field struct or null
   * @property itemAltText - the item's alternative string
   * @property avatarUrl - the item's avatar image URL, if applicable
   * @property avatarChildren - the item's avatar ready to render JSX element(s)
   * @property avatarColor - the item's avatar color, if applicable & there is no avatar image
   * @property selected - is this item selected and corresponding checkbox must be "checked"?
   * @property actions - the ready to render JSX element(s) containing additional item's actions (optional)
   * @property cardHeaderActions - extension for 'cards' variant of the list, with ability to render
   *    additional actions for the item at the item's header
   */
  key: CommonKey | undefined
  routePath: string | null
  divider: boolean
  primaryField: EnumField | null
  secondaryField: EnumField | null
  itemAltText: string | undefined
  avatarUrl: string | null
  avatarChildren: React.ReactNode | null
  avatarColor?: string
  selected: boolean
  actions: React.ReactNode | null
  cardHeaderActions: React.ReactNode | null
}


export class ProvList extends React.Component<ProvListProps, ProvListState> {
  state: ProvListState = {
    compactScreen: false,
    loading: true,
  }

  private hocRef = createRef<ProvEnumsHoc>()

  componentDidMount() {
    this.updateWindowDimensions();
    window.addEventListener('resize', this.updateWindowDimensions);
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this.updateWindowDimensions);
  }

  updateWindowDimensions() {
    this.setState({compactScreen: isCompactScreen()});
  }

  /**
   * Called when checkbox has been clicked to modify the list of the selected items.
   *
   * @param key - the corresponding item's key (on which's checkbox has been clicked)
   */
  private handleCheckboxChange = (key: CommonKey | undefined): void => {
    const restricted: boolean = Array.isArray(this.props.selectable) && !this.props.selectable.includes(key)
    const selected = (this.props.selected ?? this.state.selected ?? []) as any
    const checked = selected.includes(key)
    if (checked) {
      selected.splice(selected.indexOf(key), 1)
    } else if (!restricted) {
      selected.push(key)
    }
    this.props.onSelection !== undefined
      ? this.props.onSelection(selected)
      : this.setState({selected})
  }

  /**
   * Inverts the selection, taking all items and inverting their corresponding state. If
   * the another item is selected - makes it unselected, and vise versa.
   */
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
      const restricted: boolean = Array.isArray(this.props.selectable) && !this.props.selectable.includes(key)
      if (!selected && !restricted) {
        updatedSelected.push(key)
      }
    })
    this.props.onSelection !== undefined
      ? this.props.onSelection(updatedSelected)
      : this.setState({selected: updatedSelected})
  }

  /**
   * Returns item's alternative string.
   *
   * @param item - the item object
   * @return - the item alternative string or undefined if not applicable.
   */
  private getItemAlt = (item: any): string | undefined => {
    if (typeof this.props.primaryField == 'string')
      return item[this.props.primaryField]
    return undefined
  }

  /**
   * Returns the item corresponding avatar URL (the absolute one). If there is no
   * avatar image - returns null instead.
   *
   * @param item - the item object
   * @return - the URL if applicable, or {null} instead
   */
  private getItemAvatarUrl = (item: any): string | null => {
    return this.props.avatarField && item[this.props.avatarField]
      ? (
        this.props.storageEntity
          ? storage.urlFor(this.props.storageEntity, item[this.props.avatarField])
          : routing.assetAbspath(item[this.props.avatarField])
      ) : null
  }

  /**
   * Returns the rendered JSX element to be included as avatar element, for the item.
   *
   * @param item - the item object.
   * @return - the ready to render JSX element
   */
  private getItemAvatarChildren = (item: any): React.ReactNode | null => {
    if (this.props.avatarField && item[this.props.avatarField])
      return null
    if (this.props.avatarFallback === undefined) {
      const itemAlt = this.getItemAlt(item)
      if (!itemAlt)
        return null
      const itemAltSplitted: string[] = itemAlt.split(' ')
      const avatarLetters: string[] = [itemAltSplitted[0][0]]
      if (itemAltSplitted.length > 1) {
        avatarLetters.push(itemAltSplitted[1][0])
      }
      return avatarLetters.join('')
    } else if (typeof this.props.avatarFallback == 'string') {
      return <img alt={'avatar'} src={routing.assetAbspath(this.props.avatarFallback)} />
    } else {
      return this.props.avatarFallback(item)
    }
  }

  /**
   * Returns the corresponding color for the item avatar, if there is no image applicable as the avatar.
   *
   * @param item - the item object
   * @param itemAlt - the item alternative string
   * @return - the CSS color code or undefined on error
   */
  private getItemAvatarColor = (item: any, itemAlt: string | undefined): string | undefined => {
    if (typeof this.props.avatarColor == 'function')
      return this.props.avatarColor(item)
    if (typeof this.props.avatarColor == 'string') {
      if (this.props.avatarColor in item)
        return item[this.props.avatarColor]
      return this.props.avatarColor
    }
    if (this.props.avatarColor === true && itemAlt)
      return colorByString(itemAlt)
    return undefined
  }

  /**
   * Fetch items from the backend, and render them after, using HOC component.
   */
  public fetch = (): void => {
    this.hocRef.current?.fetch()
  }

  /**
   * Basing on the item object, prepare the required for render item struct and return it.
   *
   * @param item - the item object
   * @param index - the corresponding item index in the entire items array
   * @param items - the entire array of items
   * @return - the prepared for render item struct
   */
  private prepareItem = (item: any, index: number, items: any[]): ProvListItemPrepared => {
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
      primaryField: EnumField | null = this.props.primaryField ?? 'caption',
      secondaryField: EnumField | null = this.props.secondaryField ?? null,
      itemAltText: string | undefined = this.getItemAlt(item),
      avatarUrl: string | null = this.getItemAvatarUrl(item),
      avatarChildren: React.ReactNode | null = this.getItemAvatarChildren(item),
      avatarColor: string | undefined = this.getItemAvatarColor(item, itemAltText),
      selection = (this.props.selected ?? this.state.selected ?? []) as any[],
      selected: boolean = (key !== undefined && ((this.props.selectable ?? false) !== false) && selection.length)
        ? selection.includes(key)
        : false,
      actions: React.ReactNode | null = this.props.renderItemActions === undefined
        ? null
        : this.props.renderItemActions(item, index, items),
      cardHeaderActions: React.ReactNode | null = this.props.renderItemCardHeaderActions === undefined
        ? null
        : this.props.renderItemCardHeaderActions(item, index, items)

    return {
      key,
      routePath,
      divider,
      primaryField,
      secondaryField,
      itemAltText,
      avatarUrl,
      avatarChildren,
      avatarColor,
      selected,
      actions,
      cardHeaderActions
    }
  }

  render() {
    const
      items = (this.props.items ?? this.state.items) || []

    const
      columns = this.state.compactScreen
        ? (this.props.cardsOnRowCompactScreen ?? this.props.cardsOnRow ?? 1)
        : (this.props.cardsOnRowWideScreen ?? this.props.cardsOnRow ?? 3)

    return (
      <ProvEnumsHoc
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
        {(this.props.variant ?? 'list') === 'list' ? (
          <List className={'SystemUI-Lists List'}>
            {items.map((item, index) => {
              const preparedItem: ProvListItemPrepared = this.prepareItem(item, index, items)

              const PrimaryFieldComponent = this.props.renderPrimaryField !== undefined
                ? this.props.renderPrimaryField(item, preparedItem.primaryField)
                : preparedItem.primaryField
                  ? <FieldItemData item={item} field={preparedItem.primaryField} />
                  : undefined
              const SecondaryFieldComponent = this.props.renderSecondaryField !== undefined
                ? this.props.renderSecondaryField(item, preparedItem.secondaryField)
                : preparedItem.secondaryField
                  ? <FieldItemData item={item} field={preparedItem.secondaryField} />
                  : undefined

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
                      {this.props.avatarField !== undefined && (
                        <ListItemAvatar>
                          <Avatar
                            alt={preparedItem.itemAltText}
                            src={preparedItem.avatarUrl ?? undefined}
                            sx={{
                              color: '#FFFFFFDD',
                              bgcolor: preparedItem.avatarColor
                            }}
                          >
                            {preparedItem.avatarChildren}
                          </Avatar>
                        </ListItemAvatar>
                      )}
                      {preparedItem.key !== undefined
                          && this.props.avatarField === undefined
                          && (this.props.selectable ?? false) !== false
                          && (
                        <ListItemIcon>
                          <Checkbox
                            edge="start"
                            checked={preparedItem.selected}
                            tabIndex={-1}
                            disableRipple
                            inputProps={{'aria-labelledby': String(preparedItem.key)}}
                            value={preparedItem.key}
                            onClick={e => {
                              e.preventDefault()
                              e.stopPropagation()
                              this.handleCheckboxChange(preparedItem.key)
                            }}
                            disabled={Array.isArray(this.props.selectable) && !this.props.selectable.includes(preparedItem.key)}
                          />
                        </ListItemIcon>
                      )}

                      <ListItemText
                        primary={PrimaryFieldComponent}
                        secondary={SecondaryFieldComponent}
                      />

                      {(
                        (preparedItem.key !== undefined && (this.props.selectable ?? false) !== false && this.props.avatarField)
                        || (preparedItem.actions !== null)
                      ) && (
                        <ListItemSecondaryAction>
                          {preparedItem.actions}
                          {(preparedItem.key !== undefined && (this.props.selectable ?? false) !== false && this.props.avatarField) && (
                            <Checkbox
                              edge="start"
                              checked={preparedItem.selected}
                              tabIndex={-1}
                              disableRipple
                              inputProps={{'aria-labelledby': String(preparedItem.key)}}
                              onClick={e => {
                                e.stopPropagation()
                              }}
                              onChange={() => this.handleCheckboxChange(preparedItem.key)}
                            />
                          )}
                        </ListItemSecondaryAction>
                      )}

                    </ListItem>
                    {preparedItem.divider && <Divider />}
                  </React.Fragment>
                )

              return preparedItem.routePath
                ? <Link to={preparedItem.routePath} className={'SystemUI-Lists RouteLink'}>{ListItemElement}</Link>
                : this.props.onItemClick !== undefined
                  ? <Box onClick={() => this.props.onItemClick && this.props.onItemClick(item)}>{ListItemElement}</Box>
                  : <React.Fragment>{ListItemElement}</React.Fragment>
            })}
          </List>
        ) : (
          <Gridbox columns={columns} gap={1}>
            {items.map((item, index) => {
              const preparedItem: ProvListItemPrepared = this.prepareItem(item, index, items)

              const PrimaryFieldComponent = this.props.renderPrimaryField !== undefined
                ? this.props.renderPrimaryField(item, preparedItem.primaryField)
                : preparedItem.primaryField
                  ? <FieldItemData item={item} field={preparedItem.primaryField} />
                  : undefined
              const SecondaryFieldComponent = this.props.renderSecondaryField !== undefined
                ? this.props.renderSecondaryField(item, preparedItem.secondaryField)
                : preparedItem.secondaryField
                  ? <FieldItemData item={item} field={preparedItem.secondaryField} />
                  : undefined

              const ListItemComponent: React.ElementType | undefined = this.props.itemComponent
              const ListItemElement = ListItemComponent !== undefined
                ? (
                  <ListItemComponent
                    item={item}
                    index={index}
                  />
                ) : (
                  <React.Fragment>
                    <Card variant={'outlined'} sx={{
                      boxSizing: 'border-box',
                      height: '100%'
                    }}>
                      <CardHeader
                        avatar={this.props.avatarField !== undefined ? (
                          <Avatar
                            alt={preparedItem.itemAltText}
                            src={preparedItem.avatarUrl ?? undefined}
                            sx={{
                              color: '#FFFFFFDD',
                              bgcolor: preparedItem.avatarColor
                            }}
                          >
                            {preparedItem.avatarChildren}
                          </Avatar>
                        ) : (preparedItem.key !== undefined && (this.props.selectable ?? false) !== false) ? (
                          <Checkbox
                            edge="start"
                            checked={preparedItem.selected}
                            tabIndex={-1}
                            disableRipple
                            inputProps={{'aria-labelledby': String(preparedItem.key)}}
                            value={preparedItem.key}
                            onClick={e => {
                              e.preventDefault()
                              e.stopPropagation()
                              this.handleCheckboxChange(preparedItem.key)
                            }}
                          />
                        ) : undefined}
                        action={(
                          (
                            preparedItem.key !== undefined
                            && this.props.avatarField !== undefined
                            && (this.props.selectable ?? false) !== false
                          )
                          || (preparedItem.cardHeaderActions !== null)
                        ) ? (
                          <React.Fragment>
                            {preparedItem.cardHeaderActions}
                            {preparedItem.key !== undefined
                              && this.props.avatarField !== undefined
                              && (this.props.selectable ?? false) !== false
                              && (
                                <Checkbox
                                  edge="start"
                                  checked={preparedItem.selected}
                                  tabIndex={-1}
                                  disableRipple
                                  inputProps={{'aria-labelledby': String(preparedItem.key)}}
                                  value={preparedItem.key}
                                  onClick={e => {
                                    e.preventDefault()
                                    e.stopPropagation()
                                    this.handleCheckboxChange(preparedItem.key)
                                  }}
                                />
                              )
                            }
                          </React.Fragment>
                        ) : undefined}
                        title={PrimaryFieldComponent}
                        titleTypographyProps={{
                          variant: 'h6',
                        }}
                      />
                      {SecondaryFieldComponent !== undefined && SecondaryFieldComponent !== null && (
                        <CardContent sx={{
                          paddingTop: '4px',
                          paddingBottom: '16px'
                        }}>
                          {SecondaryFieldComponent}
                        </CardContent>
                      )}
                      {preparedItem.actions !== null && (
                        <CardActions sx={{
                          paddingTop: 0
                        }}>
                          {preparedItem.actions}
                        </CardActions>
                      )}
                    </Card>
                  </React.Fragment>
                )

              return preparedItem.routePath
                ? <Link to={preparedItem.routePath} className={'SystemUI-Lists RouteLink'}>{ListItemElement}</Link>
                : this.props.onItemClick !== undefined
                  ? <ButtonBase
                      sx={{
                        textAlign: 'left',
                        display: 'block'
                      }}
                      onClick={() => this.props.onItemClick && this.props.onItemClick(item)}
                  >{ListItemElement}</ButtonBase>
                  : <React.Fragment>{ListItemElement}</React.Fragment>
            })}
          </Gridbox>
        )}
      </ProvEnumsHoc>
    )
  }
}
