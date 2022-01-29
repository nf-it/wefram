import React, {createRef} from 'react'
import {
  Box,
  Checkbox,
  Collapse,
  IconButton,
  Hinted,
  MaterialIcon,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip
} from 'system/components'
import {
  EnumsSelection,
  ProvTableProps,
} from './types'
import {ProvEnumsHoc} from './ProvEnumsHoc'
import {FieldItemData} from './FieldItemData'
import {CommonKey} from 'system/types'
import {gettext} from 'system/l10n'


type ProvTableState = {
  /**
   * @property loading - `true` (initially = true) when loading items
   * @property items - the fetched from backend items array
   * @property selected - the array of selected items' keys
   * @property expanded - the dict containing corresponding rows' numbers and their expanded state
   */
  loading: boolean
  items?: any[]
  selected?: EnumsSelection
  expanded: Record<number, boolean>
}


export class ProvTable extends React.Component<ProvTableProps, ProvTableState> {
  state: ProvTableState = {
    loading: true,
    expanded: {}
  }

  private hocRef = createRef<ProvEnumsHoc>()

  /**
   * Called when checkbox has been clicked to modify the list of the selected items.
   *
   * @param key - the corresponding item's key (on which's checkbox has been clicked)
   */
  private handleCheckboxChange = (key: CommonKey): void => {
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
   * Fetch items from the backend, and render them after, using HOC component.
   */
  public fetch = (): void => {
    this.hocRef.current?.fetch()
  }

  render() {
    const
      items = (this.props.items ?? this.state.items) || []

    const
      colSpan: number = this.props.columns.length + 1
        + ((this.props.selectable ?? false) !== false ? 1 : 0)
        + (this.props.renderRowPrefix ? 1 : 0)
        + (this.props.renderRowSuffix ? 1 : 0)


    return (
      <ProvEnumsHoc
        ref={this.hocRef}
        disableSelectInvertButton
        onHocFetch={(state) => {
          this.setState({
            items: state.items
          })
        }}
        onHocInvertSelection={this.invertSelection}
        items={items}
        {...this.props}
      >
        <Table>
          <TableHead>
            {this.props.renderRowExpandedChild && (
              <TableCell padding={'checkbox'} />
            )}
            {(this.props.selectable ?? false) !== false && (
              <TableCell align={'center'} padding={'checkbox'}>
                <Tooltip title={gettext("Invert selection", 'system.ui')}>
                  <IconButton
                    onClick={this.invertSelection}
                  >
                    <MaterialIcon icon={'select_all'} />
                  </IconButton>
                </Tooltip>
              </TableCell>
            )}
            {this.props.renderRowPrefix && (
              <TableCell padding={'checkbox'} />
            )}
            {this.props.columns.filter(column => !column.hidden).map(column => (
              <TableCell align={column.fieldAlign}>
                {column.captionHint !== undefined ? (
                  <Hinted hint={column.captionHint}>{column.caption}</Hinted>
                ) : (
                  column.caption
                )}
              </TableCell>
            ))}
            {this.props.renderRowSuffix && (
              <TableCell padding={'checkbox'} />
            )}
          </TableHead>
          <TableBody>
            {items.map((item, index, arr) => {
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
                // avatarUrl: string | null = this.getItemAvatarUrl(item),
                selection = (this.props.selected ?? this.state.selected ?? []) as any[],
                selected: boolean = (key !== undefined && (this.props.selectable ?? false) !== false && selection.length)
                  ? selection.includes(key)
                  : false

              const
                expandedChild: React.ReactNode | null = this.props.renderRowExpandedChild
                  ? this.props.renderRowExpandedChild(item)
                  : null

              return (
                [
                  <TableRow
                    key={`row-${index}`}
                    hover={this.props.onItemClick !== undefined}
                    style={{
                      cursor: this.props.onItemClick ? 'pointer' : 'default'
                    }}
                    selected={selected}
                    onClick={() => this.props.onItemClick && this.props.onItemClick(item)}
                  >
                    {this.props.renderRowExpandedChild && (
                      <TableCell align={'center'} padding={'checkbox'}>
                        {expandedChild !== null && (
                          <IconButton onClick={() => {
                            const expanded = this.state.expanded
                            expanded[index] = !Boolean(expanded[index])
                            this.setState({expanded})
                          }}>
                            {this.state.expanded[index] ? (
                              <MaterialIcon icon={'keyboard_arrow_up'} />
                            ) : (
                              <MaterialIcon icon={'keyboard_arrow_down'} />
                            )}
                          </IconButton>
                        )}
                      </TableCell>
                    )}
                    {(this.props.selectable ?? false) !== false && (
                      <TableCell align={'center'} padding={'checkbox'}>
                        {key !== undefined && (
                          <Checkbox
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
                        )}
                      </TableCell>
                    )}
                    {this.props.renderRowPrefix && (
                      <TableCell padding={'checkbox'}>
                        {this.props.renderRowPrefix(item, index, arr)}
                      </TableCell>
                    )}
                    {this.props.columns.filter(column => !column.hidden).map(column => (
                      <TableCell
                        align={column.fieldAlign}
                      >
                        <FieldItemData item={item} field={column} disableCaption/>
                      </TableCell>
                    ))}
                    {this.props.renderRowSuffix && (
                      <TableCell padding={'checkbox'}>
                        {this.props.renderRowSuffix(item, index, arr)}
                      </TableCell>
                    )}
                  </TableRow>,
                  (this.props.renderRowExpandedChild ? (
                    <TableRow key={`row-${index}-collapse`}>
                      <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={colSpan}>
                        <Collapse in={Boolean(this.state.expanded[index])} timeout="auto" unmountOnExit>
                          {expandedChild}
                        </Collapse>
                      </TableCell>
                    </TableRow>
                  ) : null)
                ]
              )
            })}
          </TableBody>
        </Table>
      </ProvEnumsHoc>
    )
  }
}
