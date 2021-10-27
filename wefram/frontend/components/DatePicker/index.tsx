import React from 'react'
import dateLocalization from 'system/features/DatesLocales'
import {TextField} from 'system/components'
import AdapterDateFns from '@mui/lab/AdapterDateFns'
import LocalizationProvider from '@mui/lab/LocalizationProvider'
import {gettext} from 'system/l10n'
import {DatePicker as MuiDatePicker} from '@mui/lab';
import {CalendarPickerView} from '@mui/lab/CalendarPicker/shared'
import {DatePickerView} from '@mui/lab/DatePicker/shared'
import {PopperProps as MuiPopperProps} from '@mui/material/Popper/index'
import {OverrideParseableDateProps} from '@mui/lab/internal/pickers/hooks/date-helpers-hooks'
import {ExportedCalendarPickerProps} from '@mui/lab/CalendarPicker/CalendarPicker'
import {ExportedDateInputProps} from '@mui/lab/internal/pickers/PureDateInput'
import {ParseableDate} from '@mui/lab/internal/pickers/constants/prop-types'
import {ExportedArrowSwitcherProps} from '@mui/lab/internal/pickers/PickersArrowSwitcher'
import {PickersCalendarHeaderComponentsPropsOverides} from '@mui/lab/CalendarPicker/PickersCalendarHeader'
import {DialogProps as MuiDialogProps} from '@mui/material/Dialog/Dialog'
import {InputAdornmentProps} from '@mui/material'
import {PickersDayProps} from '@mui/lab/PickersDay/PickersDay'
import {ToolbarComponentProps} from '@mui/lab/internal/pickers/typings/BasePicker'
import {TransitionProps as MuiTransitionProps} from '@mui/material/transitions/transition'
import IconButton from '@mui/material/IconButton'
import {runtime} from 'system/runtime'


export type DateValue = any

export type DatePickerProps = {
  /** TextField props **/
  defaultValue?: DateValue
  fullWidth?: boolean
  label?: string
  margin?: 'dense' | 'normal' | 'none'
  size?: 'small' | 'medium'
  value?: DateValue
  variant?: 'standard' | 'outlined' | 'filled'

  /** Picker props **/
  allowSameDateSelection?: boolean
  clearable?: boolean
  components?: OverrideParseableDateProps<DateValue, ExportedCalendarPickerProps<DateValue>, 'minDate' | 'maxDate'>['components'] & ExportedDateInputProps<ParseableDate<DateValue>, DateValue | null>['components']
  componentsProps?: ExportedArrowSwitcherProps['componentsProps'] & {
      switchViewButton?: React.ComponentPropsWithRef<typeof IconButton> & PickersCalendarHeaderComponentsPropsOverides;
  }
  DialogProps?: Partial<MuiDialogProps>
  defaultCalendarMonth?: any
  disableCloseOnSelect?: boolean
  disabled?: boolean
  disableHighlightToday?: boolean
  disableMaskedInput?: boolean
  disableOpenPicker?: boolean
  InputAdornmentProps?: Partial<InputAdornmentProps>
  inputFormat?: string
  inputRef?: any
  loading?: boolean
  mask?: string
  maxDate?: any
  minDate?: any
  onAccept?: (date: DateValue) => void
  onChange?: (date: DateValue) => void
  onClose?: () => void
  onError?: (reason: any, value: DateValue) => void
  onMonthChange?: (date: DateValue) => void
  onOpen?: () => void
  onViewChange?: (view: CalendarPickerView) => void
  onYearChange?: (date: DateValue) => void
  open?: boolean
  openTo?: DatePickerView
  orientation?: 'portrait' | 'landscape'
  PopperProps?: Partial<MuiPopperProps>
  readOnly?: boolean
  reduceAnimations?: boolean
  renderDay?: (day: DateValue, selectedDates: Array<DateValue | null>, pickersDayProps: PickersDayProps<DateValue>) => JSX.Element
  renderLoading?: () => React.ReactNode
  rifmFormatter?: (str: string) => string
  shouldDisableDate?: (day: DateValue) => boolean
  shouldDisableYear?: (day: DateValue) => boolean
  showDaysOutsideCurrentMonth?: boolean
  showTodayButton?: boolean
  showToolbar?: boolean
  ToolbarComponent?: React.JSXElementConstructor<ToolbarComponentProps<DateValue | null>>
  toolbarFormat?: string
  toolbarPlaceholder?: React.ReactNode
  toolbarTitle?: React.ReactNode
  TransitionComponent?: React.JSXElementConstructor<MuiTransitionProps>
  views?: readonly DatePickerView[]
}


type DatePickerState = {
  value: DateValue
}


export class DatePicker extends React.Component<DatePickerProps> {
  state: DatePickerState = {
    value: null
  }

  componentDidMount() {
    this.setState({value: this.props.defaultValue ?? null})
  }

  render() {
    const {
      variant,
      margin,
      size,
      defaultValue,
      value,
      label,
      mask,
      fullWidth,
      onChange,
      ...pickerprops
    } = this.props

    const defaultMask: string = runtime.locale.dateFormat.replace(/[a-zA-z]/gi, '_')

    return (
      <LocalizationProvider dateAdapter={AdapterDateFns} locale={dateLocalization()}>
        <MuiDatePicker
          {...pickerprops}
          cancelText={gettext("Cancel")}
          clearText={gettext("Clear")}
          leftArrowButtonText={gettext("Previous month", 'system.datetime')}
          rightArrowButtonText={gettext("Next month", 'system.datetime')}
          okText={gettext("OK")}
          todayText={gettext("Today")}
          value={value ?? this.state.value}
          mask={mask ?? defaultMask}
          renderInput={(params) => (
            <TextField
              margin={margin}
              size={size}
              variant={variant}
              label={label}
              fullWidth={fullWidth}
              {...params}
            />
          )}
          onChange={(date) => {
            this.setState({value: date})
            if (this.props.onChange) {
              this.props.onChange(date)
            }
          }}
        />
      </LocalizationProvider>
    )
  }
}
