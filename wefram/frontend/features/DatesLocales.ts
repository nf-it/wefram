import {gettext} from 'system/l10n'
import {runtime} from 'system/runtime'


export type DateFormat = {
  full: string
  long: string
  medium: string
  short: string
}

export type TimeFormats = {
  full: string
  long: string
  medium: string
  short: string
}

export type DateMask = string


export type DateLocale = {
  // code?: string
  // formatDistance?: (...args: Array<any>) => any
  // formatRelative?: (...args: Array<any>) => any
  localize?: {
    ordinalNumber: (...args: Array<any>) => any
    // era: (...args: Array<any>) => any
    // quarter: (...args: Array<any>) => any
    month: (...args: Array<any>) => any
    day: (...args: Array<any>) => any
    // dayPeriod: (...args: Array<any>) => any
  }
  formatLong?: {
    // date: (...args: Array<any>) => any
    // time: (...args: Array<any>) => any
    // dateTime: (...args: Array<any>) => any
  }
  match?: {
  //   ordinalNumber: (...args: Array<any>) => any
  //   era: (...args: Array<any>) => any
  //   quarter: (...args: Array<any>) => any
  //   month: (...args: Array<any>) => any
  //   day: (...args: Array<any>) => any
  //   dayPeriod: (...args: Array<any>) => any
  }
  options?: {
    weekStartsOn?: 0 | 1 | 2 | 3 | 4 | 5 | 6
    firstWeekContainsDate?: 1 | 2 | 3 | 4 | 5 | 6 | 7
  }
}

const monthValues = {
  abbreviated: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  wide: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
}
const dayValues = {
  short: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
  abbreviated: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
  wide: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
}

//
// var dateFormats = {
//   full: "EEEE, d MMMM y 'г.'",
//   long: "d MMMM y 'г.'",
//   medium: "d MMM y 'г.'",
//   short: 'dd.MM.y'
// };
// var timeFormats = {
//   full: 'H:mm:ss zzzz',
//   long: 'H:mm:ss z',
//   medium: 'H:mm:ss',
//   short: 'H:mm'
// };

// const monthValues = {
//   narrow: ['Я', 'Ф', 'М', 'А', 'М', 'И', 'И', 'А', 'С', 'О', 'Н', 'Д'],
//   abbreviated: ['янв.', 'фев.', 'март', 'апр.', 'май', 'июнь', 'июль', 'авг.', 'сент.', 'окт.', 'нояб.', 'дек.'],
//   wide: ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
// };
// const formattingMonthValues = {
//   narrow: ['Я', 'Ф', 'М', 'А', 'М', 'И', 'И', 'А', 'С', 'О', 'Н', 'Д'],
//   abbreviated: ['янв.', 'фев.', 'мар.', 'апр.', 'мая', 'июн.', 'июл.', 'авг.', 'сент.', 'окт.', 'нояб.', 'дек.'],
//   wide: ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
// };
// const dayValues = {
//   narrow: ['В', 'П', 'В', 'С', 'Ч', 'П', 'С'],
//   short: ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'],
//   abbreviated: ['вск', 'пнд', 'втр', 'срд', 'чтв', 'птн', 'суб'],
//   wide: ['воскресенье', 'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']
// };


const localize = (): DateLocale => {
  let firstWeekDay: number = ((runtime.locale.weekStartsOn ?? 0) as number) + 1
  if (firstWeekDay > 6) {
    firstWeekDay -= 7
  }
  const weekStartsOn: 0 | 1 | 2 | 3 | 4 | 5 | 6 = firstWeekDay as any

  return {
    localize: {
      month: (n: number, o?: any) => {
        switch (o['width'] ?? 'abbreviated') {
          case 'narrow':
            return gettext(monthValues.abbreviated[n], 'system.datetime-months')
          case 'wide':
            return gettext(monthValues.wide[n], 'system.datetime-months')
          default:
            return gettext(monthValues.abbreviated[n], 'system.datetime-months')
        }
      },
      day: (n: number, o?: any) => {
        switch (o['width'] ?? 'abbreviated') {
          case 'narrow':
            return gettext(dayValues.abbreviated[n], 'system.datetime-days')
          case 'wide':
            return gettext(dayValues.wide[n], 'system.datetime-days')
          case 'short':
            return gettext(dayValues.short[n], 'system.datetime-days')
          default:
            return gettext(dayValues.abbreviated[n], 'system.datetime-days')
        }
      },
      ordinalNumber: (...args: Array<any>): any => {
        return args[0]
      }
    },
    formatLong: {
      date: (...args: Array<any>): any => {
        return runtime.locale.dateFormat
      }
    },
    options: {
      weekStartsOn,
      firstWeekContainsDate: runtime.locale.firstWeekContainsDate
    },
    match: {

    }
  }
}

export default localize
