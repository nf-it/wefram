/*
 A set of different TypeScript general tools (functions) used anywhere.

 Author: Denis "reagent" Khodus (c) 2021

 The part of these tools been exported from the outer library called `lodash`,
 lighty modified or optimized.
 The reason to do that is because lodash is a big package while we need only a
 really small set of functionality of it.
 */


type _Internal = {
  lastGeneratedId: number
}

const _internal: _Internal = {
  lastGeneratedId: 0
}

const _compactScreenMaxWidth: number = 650


export function strToDate(src: string): Date | null {
  if (!src.trim())
    return null

  let res = new Date(src)
  if (!isNaN(res.valueOf()))
    return res

  const
    s: string = src.trim().replace(/ /g, 'T'),
    parts: string[] = s.split('T')

  res = new Date()

  parts.forEach(p => {
    if (p.indexOf(':') !== -1) {
      if (p.indexOf('+') !== -1) {
        p = p.split('+')[0]
      }
      const
        times: string[] = p.split(':'),
        h: number = Number(times[0]),
        m: number = Number(times[1]),
        s: number = times.length > 2 ? Number(times[2]) : 0
      res.setHours(h)
      res.setMinutes(m)
      res.setSeconds(s)
    } else {
      const [y, m, d] = p.split('-')
      res.setFullYear(Number(y))
      res.setMonth(Number(m))
      res.setDate(Number(d))
    }
  })

  return res
}


export function uniqueId(prefix?: string): string {
  _internal.lastGeneratedId++
  return String(prefix ? String(prefix).concat('_') : '').concat(String(_internal.lastGeneratedId))
}


export function isObjectLike(value: unknown) {
  return value != null && typeof value == 'object';
}


export function isObject(object: unknown) {
  return object != null && typeof object === 'object';
}

function deepEqual(object1: any, object2: any): boolean {
  const keys1 = Object.keys(object1);
  const keys2 = Object.keys(object2);

  if (keys1.length !== keys2.length) {
    return false;
  }

  for (const key of keys1) {
    const val1 = object1[key];
    const val2 = object2[key];
    const areObjects = isObject(val1) && isObject(val2);
    if (areObjects && !deepEqual(val1, val2) || !areObjects && val1 !== val2) {
      return false;
    }
  }

  return true;
}


export function isEqual(object1: any, object2: any): boolean {
  if (object1 === object2) {
    return true;
  }
  if (object1 == null || object2 == null || (!isObjectLike(object1) && !isObjectLike(object2))) {
    return object1 !== object1 && object2 !== object2;
  }
  return deepEqual(object1, object2)
}


export function isArraysEqual(arr1: any[], arr2: any[]): boolean {
  if (!Array.isArray(arr1) || !Array.isArray(arr2))
    return false
  if (arr1.length !== arr2.length)
    return false
  for (let i = 0; i < arr1.length; i++) {
    const e1: any = arr1[i]
    const e2: any = arr2[i]
    if (Array.isArray(e1) && Array.isArray(e2) && !isArraysEqual(e1, e2))
      return false
    if (typeof e1 !== typeof e2)
      return false
    if (e1 !== e2)
      return false
  }
  return true
}


export function arrayFrom<T>(s: T | T[]): T[] {
  return Array.isArray(s) ? s : [s, ]
}


export function isCompactScreen(): boolean {
  return window.innerWidth <= _compactScreenMaxWidth
}


export function colorByString(s: string | null | undefined): string {
  const DEFAULT_COLOR: string = '#BDBDBD'
  const COLORS: string[] = [
    '#115599',
    '#119955',
    '#995511',
    '#991155',
    '#337766',
    '#336699',
    '#008888',
    '#DD8800',
    '#5544BB',
    '#557788'
  ]
  if (!s)
    return DEFAULT_COLOR
  const letterCode: string = String(String(s[0]).charCodeAt(0))
  const colorCodeN: number = Number(letterCode[letterCode.length-1])
  if (isNaN(colorCodeN))
    return DEFAULT_COLOR
  return COLORS[colorCodeN]
}
