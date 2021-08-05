import React from 'react'
import CheckCircleOutlineOutlinedIcon from '@material-ui/icons/CheckCircleOutlineOutlined'
import RemoveCircleOutlineOutlinedIcon from '@material-ui/icons/RemoveCircleOutlineOutlined';
import {
  ListField,
  FieldType,
  ListFieldType,
  ListFieldStruct, ListFieldValueVisualize
} from './types'
import {gettext} from '../../l10n'


type ItemProps = {
  item: any
  field: ListField
}


type InnerProps = {
  item: any
  field: ListFieldType
  className?: string
}


class ListFieldItemInner extends React.Component<InnerProps> {
  private guessFieldType = (value: any): FieldType => {
    if (typeof value == 'boolean')
      return 'boolean'
    if (typeof value == 'number')
      return 'number'
    return 'string'
  }

  private makeRenderingElement = (itemValue: any, field: ListFieldStruct): JSX.Element | null =>
  {
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
                ? <CheckCircleOutlineOutlinedIcon fontSize={'small'} style={{color: 'green'}} />
                : <RemoveCircleOutlineOutlinedIcon fontSize={'small'} style={{color: 'red'}} />
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
      {field.caption !== undefined && (
        <span style={field.captionStyle} className={captionClassName}>{field.caption}:</span>
      )}
      {value}
    </span>
  }

  render() {
    const field: ListFieldType = this.props.field
    let fieldType: FieldType
    let fieldName: string
    let style: object | undefined
    let className: string | undefined
    let caption: string | undefined
    let captionStyle: object | undefined
    let captionClassName: string | undefined
    let textual: boolean | undefined
    let nullText: string | boolean | undefined
    let itemValue: any
    let valueVisualize: ListFieldValueVisualize | undefined

    if (typeof field == 'string') {
      fieldName = String(field)
      itemValue = this.props.item[fieldName]
      fieldType = this.guessFieldType(itemValue)
      style = undefined
      className = undefined
      caption = undefined
      captionStyle = undefined
      captionClassName = undefined
      textual = undefined
      nullText = false
      valueVisualize = undefined
    } else {
      fieldName = field.fieldName
      itemValue = this.props.item[fieldName]
      fieldType = field.fieldType ?? this.guessFieldType(itemValue)
      style = field.style
      className = field.className
      caption = field.caption
      captionStyle = field.captionStyle
      captionClassName = field.captionClassName
      textual = field.textual
      nullText = field.nullText
      valueVisualize = field.valueVisualize
    }

    const fieldStruct: ListFieldStruct = {
      fieldType,
      fieldName,
      style,
      className,
      caption,
      captionStyle,
      captionClassName,
      textual,
      nullText,
      valueVisualize
    }

    return (
      <div className={this.props.className || 'mr-3'}>
        {this.makeRenderingElement(itemValue, fieldStruct)}
      </div>
    )
  }
}


export class ListFieldItem extends React.Component<ItemProps> {
  render() {
    if (Array.isArray(this.props.field))
      return (
        <React.Fragment>
          {this.props.field.map((f: any) => {
            if (Array.isArray(f))
              return (
                <div className={'d-flex align-items-center'}>
                  {f.map(subf => (
                    <ListFieldItemInner field={subf} item={this.props.item} />
                  ))}
                </div>
              )
            else
              return (
                <ListFieldItemInner field={f} item={this.props.item} />
              )
          })}
        </React.Fragment>
      )

    return <ListFieldItemInner field={this.props.field} item={this.props.item} />
  }
}
