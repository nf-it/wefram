from ... import config, ui, urls, l10n


_CONFIG_REQUIRES = config.DESKTOP['requires']


@ui.screens.register(sitemap=-1)
class Desktop(ui.screens.Screen):
    component = 'containers/Desktop'
    icon = urls.media_res_url('icons/workspace.png')
    caption = l10n.lazy_gettext("Desktop")
    route = '//workspace'
    requires = _CONFIG_REQUIRES
    params = {
        'introTextId': config.DESKTOP['intro_text']
    }

