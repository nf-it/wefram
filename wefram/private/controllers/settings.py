from typing import *
from ..const.aaa import PERMISSION_ADMINUSERSROLES
from ..const.settings import PERMISSION_ADMINISTERING
from ...types.settings import SettingsEntity
from ...settings import routines
from ...requests import Request, JSONResponse, NoContentResponse
from ... import aaa, api, settings, apps


@api.handle_get('/settings/properties', version=1)
@aaa.requires(PERMISSION_ADMINISTERING)
async def v1_get_settings_schema(request: Request) -> JSONResponse:
    def _ordered_entities(_tab_id: str) -> List[SettingsEntity]:
        _entities: Dict[Union[str, None], SettingsEntity] = schema[_tab_id]
        _result: List[SettingsEntity] = []
        _default_order: int = max([(_e.order or 0) for _e in _entities.values()]) + 10
        if None in _entities:
            _result.append(_entities[None])
        [_result.append(_entities[_namesub]) for _namesub in sorted(
            [_k for _k in _entities.keys() if _k is not None],
            key=lambda _x: ((_entities[_x].order if _entities[_x].order is not None else _default_order), str(_entities[_x].caption))
        )]
        return _result

    registered = settings.registered
    schema: Dict[str, Dict[Union[str, None], SettingsEntity]] = {}

    entity: SettingsEntity
    tabs: Dict[str, SettingsEntity] = {}
    tabs_captions: Dict[str, str] = {}
    apps_tabs: Dict[str, List[str]] = {}
    for entity in registered.values():
        tab_id: str = '__'.join([entity.app_name, entity.namesub]) \
            if entity.tab is not None \
            else entity.app_name
        tab_caption: str = str(entity.tab) \
            if entity.tab is not None \
            else apps.get_app_caption(entity.app_name)
        tabs_captions[tab_id] = tab_caption
        schema.setdefault(tab_id, {})[entity.namesub] = entity
        apps_tabs.setdefault(entity.app_name, []).append(tab_id)
        tabs[tab_id] = entity

    # Sorting tabs using apps order first, and relative entity order with separate
    # tabs second.
    apps_order: List[Tuple[str, str]] = [
        (name, str(apps.get_app_caption(name)))
        for name in apps.get_apps_sorted()
        if name in schema
    ]
    tabs_order: List[Tuple[str, str]] = []
    for app_name, app_caption in apps_order:
        app_tabs: List[str] = apps_tabs[app_name]
        if app_name in app_tabs:
            tabs_order.append((app_name, app_caption))
        other_tabs: List[str] = [tab_id for tab_id in app_tabs if tab_id != app_name]
        if not other_tabs:
            continue
        default_order: int = max([(tabs[t].order or 0) for t in other_tabs]) + 10
        other_sorted: List[Tuple[str, str]] = sorted(
            [(t, tabs[t].caption) for t in other_tabs],
            key=lambda tx: tabs[tx[0]].order if tabs[tx[0]].order is not None else default_order
        )
        tabs_order.extend(other_sorted)

    values = await routines.getall()

    tabs_schema: List[dict] = []
    for tab in tabs_order:
        tab_entities: List[dict] = []
        for entity in _ordered_entities(tab[0]):
            entity_schema: Optional[dict] = \
                entity.schemadef(**values.get(entity.name, {}))
            if entity_schema is None:
                continue
            tab_entities.append(entity_schema)
        if not tab_entities:
            continue
        tab_schema: dict = {
            'tabName': tab[0],
            'tabCaption': tab[1],
            'entities': tab_entities
        }
        tabs_schema.append(tab_schema)

    return JSONResponse(tabs_schema)


@api.handle_post('/settings/properties', version=1)
@aaa.requires(PERMISSION_ADMINISTERING)
async def v1_update_settings_schema(request: Request) -> NoContentResponse:
    values: Dict[str, Dict[str, Any]] = request.scope['payload']
    await routines.reset(values, verify_permitted=True)
    return NoContentResponse()


@api.handle_get('/container/Role', version=1)
@aaa.requires(PERMISSION_ADMINUSERSROLES)
async def v1_container(request: Request) -> JSONResponse:
    return JSONResponse({
        'permissions': aaa.permissions.get_schema()
    })

