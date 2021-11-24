from typing import *
from datetime import datetime
from sqlalchemy import event, inspect
from sqlalchemy.orm import class_mapper, attributes as orm_attributes, state as orm_state
from sqlalchemy.util.concurrency import await_only
from .model import DatabaseModel as Model, History
from .reg import models_by_name
from .types import Column, BigAutoIncrement, String, StringChoice, UUID, JSONB, DateTime, ForeignKey
from .helpers import ModelColumn
from .engine import AsyncSession
from ...tools import CSTYLE, for_jsonify
from ... import logger


__all__ = [
    'DataHistory',
    'start',
    'push_history_record'
]


class DataHistory(Model):
    """ The general ORM history model storing all non-separated changelogs. """

    id = BigAutoIncrement()
    """ The history row primary key (big integer). """

    app = Column(String(255), nullable=False)
    """ The app whose model's object change have to be logged. """

    model = Column(String(255), nullable=False)
    """ The corresponding model name (appnameModelname format). """

    instance_id = Column(UUID(), nullable=True, default=None)
    """ The primary key value of the corresponding model's object instance. """

    ts = Column(DateTime(), nullable=False, default=datetime.now)
    """ The timestamp when the event happened. """

    action = StringChoice(['create', 'update', 'delete'])
    """ The type of the action against the corresponding object: create, modify or delete. """

    data = Column(JSONB())
    """ The JSON dump of the corresponding model's object. """

    attrs = Column(JSONB())
    """ For the ``modify`` action - a list of attributes been changed. """

    before = Column(JSONB())
    """ For the ``modify`` action - the dump of changed attributes prior to update. """

    after = Column(JSONB())
    """ For the ``modify`` action - the dump of changed attributes after the update. """

    performer = Column(UUID(), ForeignKey(ModelColumn('User', 'id'), ondelete='CASCADE'), nullable=True)
    """ The ``id`` of the :class:`~wefram.private.models.aaa.User` which have performed the action, 
    or NULL if there was a guest """


async def start() -> None:
    logger.debug("starting to changelogging the history on declared models")
    for model_name, model in models_by_name.items():
        if not model.Meta.history.enable:
            continue
        history_model: ClassVar = DataHistory
        logger.debug(
            f"setting up changelogging on {CSTYLE['red']}{model_name}{CSTYLE['clear']}"
            f" -> {CSTYLE['green']}{history_model.__name__}{CSTYLE['clear']}",
            'ds.history'
        )
        event.listen(model, 'after_insert', log_instance_after_create)
        event.listen(model, 'after_update', log_instance_after_update)
        event.listen(model, 'after_delete', log_instance_after_delete)


async def push_history_record(
        target: Any,
        action: Literal['create', 'update', 'delete'],
        attrs: Optional[List[str]] = None,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None
) -> None:
    from ... import aaa

    history: History = target.__class__.Meta.history
    dump: dict = for_jsonify(target.dict(
        attributes=[(e.key if isinstance(e, Column) else str(e)) for e in (history.attributes or [])] or None,
        exclude=[(e.key if isinstance(e, Column) else str(e)) for e in (history.exclude or [])] or None,
        deep=False,
        for_jsonify=True
    )) if action in ['create', 'update'] else None
    record: DataHistory = DataHistory(
        app=target.__class__.__app__,
        model=target.__class__.__decl_cls_name__,
        instance_id=target.__pk1__,
        ts=datetime.now(),
        action=action,
        data=dump,
        performer=aaa.get_current_user_id(),
        attrs=attrs,
        before=for_jsonify(before),
        after=for_jsonify(after)
    )

    async with AsyncSession() as db:
        async with db.begin():
            db.add(record)
            await db.commit()

    logger.debug(
        f"logged {CSTYLE['blue']}{action}{CSTYLE['clear']} action for"
        f" {CSTYLE['red']}{target.__class__.__app__}.{target.__class__.__decl_cls_name__}{CSTYLE['clear']}",
        'ds.history'
    )


def log_instance_after_create(mapper, connection, target) -> None:
    await_only(push_history_record(target, 'create'))


def log_instance_after_update(mapper, connection, target) -> None:
    # Collecting the list of changed attributes
    history: History = target.__class__.Meta.history
    inspr: orm_state.InstanceState = inspect(target)
    attrs: list = class_mapper(target.__class__).column_attrs
    modified: List[str] = []
    ignore: List[str] = [(e.key if isinstance(e, Column) else str(e)) for e in (history.ignore or [])]
    before: Dict[str, Any] = {}
    after: Dict[str, Any] = {}
    for attr in attrs:
        k: str = attr.key
        if k in ignore:
            continue
        hist: orm_attributes.History = getattr(inspr.attrs, k).history
        if not hist.has_changes():
            continue
        modified.append(k)
        before[k] = hist.deleted if len(hist.deleted) > 1 else hist.deleted[0]
        after[k] = hist.added if len(hist.added) > 1 else hist.added[0]

    # Exit if there is nothing to log
    if not modified:
        return

    # Logging the action
    await_only(push_history_record(target, 'update', attrs=modified, before=before, after=after))


def log_instance_after_delete(mapper, connection, target) -> None:
    await_only(push_history_record(target, 'delete'))

