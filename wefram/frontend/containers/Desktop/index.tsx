import React from 'react'
import {ScreenProps} from 'system/types'
import {
  Box,
  Button,
  ButtonLink,
  DividerRuler,
  TranslatedText,
  Typography
} from 'system/components'
import LoginIcon from '@mui/icons-material/LockOpen'
import LogoffIcon from '@mui/icons-material/ExitToApp'
import HelpIcon from '@mui/icons-material/LiveHelpOutlined'
import {runtime} from 'system/runtime'
import {session} from 'system/aaa'
import {gettext} from 'system/l10n'
import './index.css'


type DesktopState = {
  introduction: boolean
}


export default class Desktop extends React.Component<ScreenProps> {
  state: DesktopState = {
    introduction: false
  }

  handleProfileLogout = () => {
    runtime.logoff()
  }

  handleIntroductionClick = () => {
    this.setState({introduction: !this.state.introduction})
  }

  render() {
    return (
      <React.Fragment>
        <Box mt={3} mb={3}>
          <Typography
            variant={'h2'}
            style={{
              borderBottom: '2px solid #1976d2',
              paddingBottom: '8px'
            }}
          >
            {gettext("Welcome")}
            <span className={'SystemUI-Desktop-appTitle'}>
              {runtime.title}
            </span>
          </Typography>
          <Box mt={1} display={'flex'} alignItems={'center'}>
            {session.authenticated ? (
              <React.Fragment>
                <Typography
                  variant={'h4'}
                  color={'primary'}
                  style={{
                    fontWeight: 300
                  }}
                >{session.displayName}</Typography>
                <Button
                  color={'primary'}
                  variant={'outlined'}
                  endIcon={<LogoffIcon />}
                  style={{
                    marginLeft: '24px'
                  }}
                  onClick={this.handleProfileLogout}
                >
                  {gettext('Logout', 'system.aaa')}
                </Button>
              </React.Fragment>
            ) : (
              <React.Fragment>
                <ButtonLink
                  to={runtime.loginScreenUrl}
                  startIcon={<LoginIcon />}
                  variant={'contained'}
                  color={'primary'}
                >{gettext("Sign In", 'system.aaa')}</ButtonLink>
                <Typography style={{marginLeft: '1rem'}}>
                  {gettext("click here to sign in", 'system.aaa')}
                </Typography>
              </React.Fragment>
            )}
            {this.props.params.introTextId !== null && (
              <Button
                color={'primary'}
                // variant={'outlined'}
                endIcon={<HelpIcon />}
                style={{
                  marginLeft: '24px'
                }}
                onClick={this.handleIntroductionClick}
              >
                {gettext('Introduction', 'system.desktop')}
              </Button>
            )}
          </Box>
        </Box>
        {this.props.params.introTextId !== null && (
          <Box mt={3} mb={3} hidden={!this.state.introduction}>
            <DividerRuler vspace={3} />
            <TranslatedText
              appName={this.props.params.introTextId.split('.')[0]}
              textId={this.props.params.introTextId.split('.')[1]}
              fallbackToLazyText
            />
            <DividerRuler vspace={3} />
          </Box>
        )}
      </React.Fragment>
    )
  }
}
