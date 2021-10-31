import React from 'react'
import {FormCommonFieldItem} from 'system/types'
import {
  Box,
  FormControlLabel,
  Grid,
  MenuItem,
  Slider,
  StoredImage,
  StringList,
  Switch,
  TextField,
  Typography
} from 'system/components'


export type FormCommonFieldProps = {
  name?: string
  field: FormCommonFieldItem
  caption?: string
  value: any
  updatedValue?: any
  onChange: (name: string, value: any) => void
}

type FormCommonFieldState = {}


type FormCommonFieldCaptionProps = {
  caption: string
  pt?: number
  pb?: number
}


class FormCommonFieldCaption extends React.Component<FormCommonFieldCaptionProps> {
  render() {
    return (
      <Box pt={this.props.pt ?? 1} pb={this.props.pb ?? 1}>
        <Typography style={{fontSize: '.8rem', color: '#456'}}>{this.props.caption}</Typography>
      </Box>
    )
  }
}


export class FormCommonField extends React.Component<FormCommonFieldProps, FormCommonFieldState> {
  render() {
    const name: string = this.props.name ?? this.props.field.name
    const caption: string = (this.props.caption ?? this.props.field.caption) || ''
    const value: any = this.props.value
    const field: FormCommonFieldItem = this.props.field

    switch (field.fieldType) {
      case 'string':
      case 'number':
        return (
          <Grid container>
            <Grid item xs={5} style={{alignSelf: 'center'}}>
              <FormCommonFieldCaption caption={caption}/>
            </Grid>
            <Grid item xs={7}>
              <TextField
                value={String(value ?? '')}
                fullWidth
                variant={'outlined'}
                // margin={'dense'}
                size={'small'}
                type={field.fieldType === 'number' ? 'number' : 'text'}
                style={{
                  marginTop: '4px',
                  marginBottom: '4px'
                }}
                onChange={(ev: React.ChangeEvent<HTMLInputElement>) => {
                  this.props.onChange(
                    name,
                    field.fieldType === 'number' ? (Number(ev.target.value) || 0) : ev.target.value
                  )
                }}
              />
            </Grid>
          </Grid>
        )

      // ------------------------------------------------

      case 'number-min-max':
        return (
          <Grid container pt={1} pb={1}>
            <Grid item xs={5} style={{alignSelf: 'center'}}>
              <FormCommonFieldCaption caption={caption}/>
            </Grid>
            <Grid item xs={7} style={{
              display: 'flex',
              alignItems: 'center',
              paddingRight: '8px'
            }}>
              <Typography style={{
                marginRight: '16px'
              }}>
                {value}
              </Typography>
              <Slider
                value={value || 0}
                step={field.step ?? 1}
                min={field.minValue}
                max={field.maxValue}
                marks
                valueLabelDisplay={'auto'}
                getAriaValueText={(value: any) => {
                  return String(value)
                }}
                onChange={(ev: Event, newValue: number | number[]) => {
                  this.props.onChange(name, Number(newValue))
                }}
              />
            </Grid>
          </Grid>
        )

      // ------------------------------------------------

      case 'text':
        return (
          <Box>
            <FormCommonFieldCaption caption={caption} pt={2}/>
            <Box pb={2}>
              <TextField
                value={String(value ?? '')}
                fullWidth
                multiline
                size={'small'}
                variant={'outlined'}
                onChange={(ev: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
                  this.props.onChange(name, String(ev.target.value))
                }}
              />
            </Box>
          </Box>
        )

      // ------------------------------------------------

      case 'boolean':
        return (field.inline ?? false)
          ? (
            <Box pt={1} pb={1}>
              <Grid container>
                <Grid item xs={5} style={{alignSelf: 'center'}}>
                  <FormCommonFieldCaption caption={caption}/>
                </Grid>
                <Grid item xs={7}>
                  <Switch
                    checked={Boolean(value)}
                    onChange={(ev: React.ChangeEvent<HTMLInputElement>) => {
                      this.props.onChange(
                        name,
                        Boolean(ev.target.checked)
                      )
                    }}
                  />
                </Grid>
              </Grid>
            </Box>
          )
          : (
            <Box pt={1} pb={1}>
              <FormControlLabel
                style={{
                  marginTop: 0,
                  marginBottom: 0
                }}
                control={
                  <Switch
                    checked={Boolean(value)}
                    onChange={(ev: React.ChangeEvent<HTMLInputElement>) => {
                      this.props.onChange(
                        name,
                        Boolean(ev.target.checked)
                      )
                    }}
                  />
                }
                label={<FormCommonFieldCaption caption={caption}/>}
              />
            </Box>
          )

      // ------------------------------------------------

      case 'choice':
        return (
          <Grid container>
            <Grid item xs={5} style={{alignSelf: 'center'}}>
              <FormCommonFieldCaption caption={caption}/>
            </Grid>
            <Grid item xs={7}>
              <TextField
                select
                value={String(value ?? '')}
                fullWidth
                variant={'outlined'}
                // margin={'dense'}
                size={'small'}
                style={{
                  marginTop: '4px',
                  marginBottom: '4px'
                }}
                onChange={(ev: React.ChangeEvent<HTMLInputElement>) => {
                  this.props.onChange(
                    name,
                    ev.target.value
                  )
                }}
              >
                {field.options?.map(el => (
                  <MenuItem value={el.key}>{el.caption}</MenuItem>
                ))}
              </TextField>
            </Grid>
          </Grid>
        )

      // ------------------------------------------------

      case 'string-list':
        return (
          <Grid container>
            <Grid item xs={5} style={{alignSelf: 'center', alignItems: 'flex-start'}}>
              <FormCommonFieldCaption caption={caption}/>
            </Grid>
            <Grid item xs={7}>
              <StringList
                values={value}
                onChange={(values: string[]) => {
                  this.props.onChange(
                    name,
                    values
                  )
                }}
              />
            </Grid>
          </Grid>
        )

      // ------------------------------------------------

      case 'image':
        return (field.inline ?? false)
          ? (
            <Box pt={1} pb={1}>
              <Grid container>
                <Grid item xs={5} style={{alignSelf: 'center'}}>
                  <FormCommonFieldCaption caption={caption}/>
                </Grid>
                <Grid item xs={7}>
                  <Box className={'Prop-image'} pb={1}>
                    <Box style={{
                      display: field.width ? 'inline-block' : undefined
                    }}>
                      <StoredImage
                        fileId={value || null}
                        entity={field.entity ?? ''}
                        cover={field.cover}
                        dirty={this.props.updatedValue !== undefined}
                        imageHeight={field.height}
                        imageWidth={field.width}
                        permitUpload
                        permitClean
                        onChange={(newFileId: string | null) => {
                          this.props.onChange(
                            name,
                            newFileId
                          )
                        }}
                      />
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          )
          : (
            <Box className={'Prop-image'} pb={1}>
              <FormCommonFieldCaption caption={caption} pt={2}/>
              <Box>
                <StoredImage
                  fileId={value || null}
                  entity={field.entity ?? ''}
                  cover={field.cover}
                  dirty={this.props.updatedValue !== undefined}
                  imageHeight={field.height}
                  imageWidth={field.width}
                  permitUpload
                  permitClean
                  onChange={(newFileId: string | null) => {
                    this.props.onChange(
                      name,
                      newFileId
                    )
                  }}
                />
              </Box>
            </Box>
          )

        // ------------------------------------------------

    }
    return null
  }
}

