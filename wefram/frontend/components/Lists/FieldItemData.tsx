import React from 'react'
import {MaterialIcon} from 'system/components'
import {
  ListsField,
  FieldType,
  ListsFieldType,
  ListsFieldStruct
} from './types'
import {gettext} from 'system/l10n'


export type FieldItemDataProps = {
  item: any
  field: ListsField
  disableCaption?: boolean
}


type FieldItemDataInnerProps = {
  item: any
  field: ListsFieldType
  className?: string
  disableCaption?: boolean
}


class FieldItemDataInner extends React.Component<FieldItemDataInnerProps> {
  private guessFieldType = (value: any): FieldType => {
    if (typeof value == 'boolean')
      return 'boolean'
    if (typeof value == 'number')
      return 'number'
    return 'string'
  }

  private makeRenderingElement = (itemValue: any, field: ListsFieldStruct): JSX.Element | null =>
  {
    const hidden: boolean = field.hidden === undefined
      ? false
      : typeof field.hidden == 'boolean'
      ? Boolean(field.hidden)
      : field.hidden(itemValue, field)
    if (hidden)
      return null

    if (field.render)
      return field.render(itemValue, this.props.item)

    let value: null | string | JSX.Element

    if (field.valueVisualize !== undefined && typeof field.valueVisualize == 'function') {
      value = field.valueVisualize(itemValue)
    } else if (field.valueVisualize !== undefined && (itemValue in field.valueVisualize)) {
      value = field.valueVisualize[itemValue]
    } else {
      if (itemValue !== undefined && itemValue !== null) {
        switch (field.fieldType) {
          case 'boolean':
            value = field.textual ? (
              itemValue ? gettext("Yes") : gettext("No")
            ) : (
              itemValue
                ? <MaterialIcon icon={'check_circle_outline'} size={20} color={'green'} />
                : <MaterialIcon icon={'remove_circle_outline'} size={20} color={'red'} />
            )
            break
          case 'date':
            try {
              value = String(new Intl.DateTimeFormat(undefined, {
                year: 'numeric',
                month: 'numeric',
                day: 'numeric',
              }).format(new Date(itemValue)))
            } catch {
              value = null
            }
            break
          case 'dateNice':
            try {
              value = String(new Intl.DateTimeFormat(undefined, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
              }).format(new Date(itemValue)))
            } catch {
              value = null
            }
            break
          case 'dateTime':
            try {
              value = String(new Intl.DateTimeFormat(undefined, {
                year: 'numeric',
                month: 'numeric',
                day: 'numeric',
                hour: 'numeric',
                minute: 'numeric'
              }).format(new Date(itemValue)))
            } catch {
              value = null
            }
            break
          case 'dateTimeNice':
            try {
              value = String(new Intl.DateTimeFormat(undefined, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: 'numeric'
              }).format(new Date(itemValue)))
            } catch {
              value = null
            }
            break
          case 'icon':
            value = "-"
            break
          default:
            value = String(itemValue)
        }
      } else {
        value = itemValue
      }
    }

    // If the value is empty (or even undefined) and the 'nullText' is not specified - return
    // nothing meaning the item will not being rendered at all.
    if ((value === undefined || value === null || value === '') && !field.nullText)
      return null

    // If the value is empty and there is nullText set - render the '-' symbol if there not
    // been provided the specific text, or the provided text instead.
    if (value === undefined || value === null) {
      value = field.nullText === true ? '-' : String(field.nullText)
    }

    const captionClassName: string = field.captionClassName || 'SystemUI-Lists ItemCaption'

    return <span style={field.style} className={field.className}>
      {(field.caption !== undefined && !this.props.disableCaption) && (
        <span style={field.captionStyle} className={captionClassName}>{field.caption}:</span>
      )}
      {value}
    </span>
  }

  render() {
    const field: ListsFieldType = typeof this.props.field == 'string'
      ? { fieldName: this.props.field, fieldType: this.guessFieldType(this.props.item[this.props.field]) }
      : this.props.field
    const itemValue: any = field.getter
      ? field.getter(this.props.item)
      : this.props.item[field.fieldName]

    const rendered: JSX.Element | null = this.makeRenderingElement(itemValue, field)
    if (rendered === null)
      return null

    return (
      <div className={this.props.className || 'mr-3'}>

        {rendered}
      </div>
    )
  }
}


export class FieldItemData extends React.Component<FieldItemDataProps> {
  render() {
    if (Array.isArray(this.props.field))
      return (
        <React.Fragment>
          {this.props.field.map((f: any) => {
            if (Array.isArray(f))
              return (
                <div className={'d-flex align-items-center'}>
                  {f.map(subf => (
                    <FieldItemDataInner field={subf} item={this.props.item} disableCaption={this.props.disableCaption} />
                  ))}
                </div>
              )
            else
              return (
                <FieldItemDataInner field={f} item={this.props.item} disableCaption={this.props.disableCaption} />
              )
          })}
        </React.Fragment>
      )

    return <FieldItemDataInner field={this.props.field} item={this.props.item} disableCaption={this.props.disableCaption} />
  }
}
