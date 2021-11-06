import React, {createRef} from 'react'
import {
  Checkbox,
  Collapse,
  IconButton,
  Hinted,
  MaterialIcon,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow, Tooltip
} from 'system/components'
import {
  ListsSelection,
  ProvTableProps,
} from './types'
import {ProvListsHoc} from './ProvListsHoc'
import {FieldItemData} from './FieldItemData'
import {CommonKey} from 'system/types'
import {gettext} from 'system/l10n'


type ProvTableState = {
  loading: boolean
  items?: any[]
  selected?: ListsSelection
  expanded: Record<number, boolean>
}


export class ProvTable extends React.Component<ProvTableProps, ProvTableState> {
  state: ProvTableState = {
    loading: true,
    expanded: {}
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

  public fetch = (): void => {
    this.hocRef.current?.fetch()
  }

  render() {
    const
      items = (this.props.items ?? this.state.items) || []

    const
      colSpan: number = this.props.columns.length + 1
        + (this.props.selectable ? 1 : 0)
        + (this.props.renderRowPrefix ? 1 : 0)
        + (this.props.renderRowSuffix ? 1 : 0)


    return (
      <ProvListsHoc
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
            {this.props.selectable && (
              <TableCell align={'center'} padding={'checkbox'}>
                <Tooltip title={gettext("Invert selection", 'system.ui')}>
                  <Checkbox
                    checked={true}
                    tabIndex={-1}
                    disableRipple
                    onClick={this.invertSelection}
                  />
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
                selected: boolean = (key !== undefined && this.props.selectable && selection.length)
                  ? selection.includes(key)
                  : false

              const
                expandedChild: JSX.Element | JSX.Element[] | null = this.props.renderRowExpandedChild
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
                    {this.props.selectable === true && (
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
      </ProvListsHoc>
    )
  }
}
