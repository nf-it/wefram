import React from 'react'
import {MuiPickersUtilsProvider, DatePicker as MuiDatePicker, DatePickerProps} from '@material-ui/pickers'
import DateFnsUtils from '@date-io/date-fns'
import {gettext} from 'system/l10n'
import {runtime} from 'system/runtime'
// import CalendarIcon from '@material-ui/icons/EventTwoTone'
import dateLocalization from 'system/features/DatesLocales'


export class DatePicker extends React.Component<DatePickerProps> {
  render() {
    const {...props} = this.props
    props.cancelLabel === undefined && (props.cancelLabel = gettext("Cancel"))
    props.okLabel === undefined && (props.okLabel = gettext("OK"))
    props.invalidDateMessage === undefined && (props.invalidDateMessage = gettext("Invalid Date Format", 'system.ui'))
    props.maxDateMessage === undefined && (props.maxDateMessage = gettext("Date should not be after maximal date", 'system.ui'))
    props.minDateMessage === undefined && (props.minDateMessage = gettext("Date should not be before minimal date", 'system.ui'))
    props.allowKeyboardControl = false
    props.autoOk = true
    props.format = runtime.locale.dateFormat

    return (
      <MuiPickersUtilsProvider utils={DateFnsUtils} locale={dateLocalization()}>
        <MuiDatePicker
          {...props}
        />
      </MuiPickersUtilsProvider>
    )
  }
}
