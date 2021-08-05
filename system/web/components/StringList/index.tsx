import React from 'react'
import {
  Box,
  IconButton,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  OutlinedInput,
} from '@material-ui/core'
import SubmitIcon from '@material-ui/icons/DoneRounded'
import RemoveItemIcon from '@material-ui/icons/RemoveCircleTwoTone'
import DeleteIcon from '@material-ui/icons/DeleteForever'
import CancelIcon from '@material-ui/icons/Block'
import UpIcon from '@material-ui/icons/ArrowUpward'
import DownIcon from '@material-ui/icons/ArrowDownward'
import {gettext} from '../../l10n'


export type StringListProps = {
  disabled?: boolean
  rearragable?: boolean
  values: string[]
  onChange: (values: string[]) => void
}

type S = {
  controlsInput: string
  deleting: number[]
}


export class StringList extends React.Component<StringListProps, S> {
  state: S = {
    controlsInput: '',
    deleting: []
  }

  render() {
    return (
      <React.Fragment>
        <Box>
          <List style={{
            border: '1px solid #ccc',
            borderRadius: '4px',
            margin: '8px 0',
            padding: '0 4px'
          }}>
            {this.props.values.map((el: string, ix: number) => (
              <ListItem style={{
                borderBottom: ix !== this.props.values.length-1 ? '1px dotted #999' : undefined
              }}>
                <ListItemText primary={<Box style={{marginRight: '70px'}}>{el}</Box>} />
                {!(this.props.disabled ?? false) && (
                  <ListItemSecondaryAction>
                    {(this.props.rearragable ?? true) && (!this.state.deleting.includes(ix)) && ([
                      <IconButton
                        size={'small'}
                        disabled={ix === 0}
                        onClick={() => {
                          const values: string[] = this.props.values
                          const value: string = values[ix]
                          values.splice(ix, 1)
                          values.splice(ix-1, 0, value)
                          this.props.onChange(values)
                        }}
                      >
                        <UpIcon />
                      </IconButton>,
                      <IconButton
                        size={'small'}
                        disabled={ix === this.props.values.length-1}
                        onClick={() => {
                          const values: string[] = this.props.values
                          const value: string = values[ix]
                          values.splice(ix, 1)
                          values.splice(ix+1, 0, value)
                          this.props.onChange(values)
                        }}
                      >
                        <DownIcon />
                      </IconButton>
                    ])}
                    {this.state.deleting.includes(ix) ? (
                      <React.Fragment>
                        <IconButton
                          size={'small'}
                          style={{
                            color: '#f00',
                            marginRight: '8px'
                          }}
                          onClick={() => {
                            const values: string[] = this.props.values
                            values.splice(ix, 1)
                            this.props.onChange(values)
                            this.setState({
                              deleting: this.state.deleting.filter(e => e !== ix)
                            })
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                        <IconButton
                          size={'small'}
                          onClick={() => {
                            this.setState({
                              deleting: this.state.deleting.filter(e => e !== ix)
                            })
                          }}
                        >
                          <CancelIcon />
                        </IconButton>
                      </React.Fragment>
                    ) : (
                      <IconButton
                        size={'small'}
                        onClick={() => {
                          const deleting: number[] = this.state.deleting
                          deleting.push(ix)
                          this.setState({deleting})
                        }}
                      >
                        <RemoveItemIcon />
                      </IconButton>
                    )}
                  </ListItemSecondaryAction>
                )}
              </ListItem>
            ))}
          </List>
        </Box>
        {!(this.props.disabled ?? false) && (
          <Box style={{
            display: 'flex'
          }}>
            <OutlinedInput
              value={this.state.controlsInput}
              placeholder={gettext("Type new element here", 'system.ui')}
              fullWidth
              margin={'dense'}
              onChange={(ev: React.ChangeEvent<HTMLInputElement>) => {
                this.setState({controlsInput: ev.target.value})
              }}
              onKeyPress={(ev: React.KeyboardEvent<HTMLDivElement>) => {
                if (ev.key === 'Enter') {
                  const value: string = this.state.controlsInput.trim()
                  if (!value)
                    return
                  const values: string[] = this.props.values
                  values.push(value)
                  this.props.onChange(values)
                  this.setState({controlsInput: ''})
                }
              }}
              endAdornment={
                <InputAdornment position={'end'}>
                  <IconButton
                    edge={'end'}
                    size={'small'}
                    onClick={() => {
                      const value: string = this.state.controlsInput.trim()
                      if (!value)
                        return
                      const values: string[] = this.props.values
                      values.push(value)
                      this.props.onChange(values)
                      this.setState({controlsInput: ''})
                    }}
                  >
                    <SubmitIcon />
                  </IconButton>
                </InputAdornment>
              }
            />
          </Box>
        )}
      </React.Fragment>
    )
  }
}
