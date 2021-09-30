from typing import *
from datetime import datetime
from sqlalchemy import event, inspect
from sqlalchemy.orm import class_mapper, attributes as orm_attributes, state as orm_state
from sqlalchemy.util.concurrency import await_only
from .model import Model, History, models_by_name
from .types import Column, BigAutoIncrement, String, StringChoice, UUID, JSONB, DateTime, ForeignKey
from .helpers import ModelColumn
from .engine import AsyncSession
from ...tools import CSTYLE, for_jsonify
from ... import logger


__all__ = [
    'DataHistory',
    'start'
]


class DataHistory(Model):
    """ The general ORM history model storing all non-separated changelogs.

    Attributes:
        id:             The history row primary key (big integer)
        model:          The corresponding model name (appnameModelname format)
        instance_id:    The primary key value of the model's instance
        ts:             The timestamp when the event happened
        action:         The type of the action against the corresponding object: create, modify or delete
        data:           The JSON dump of the corresponding model's object
        performer:      The systemUser.id which have performed the action, or NULL if there was a guest

    """
    id = BigAutoIncrement()
    app = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False)
    instance_id = Column(UUID(), nullable=True, default=None)
    ts = Column(DateTime(), nullable=False, default=datetime.now)
    action = StringChoice(['create', 'update', 'delete'])
    data = Column(JSONB())
    attrs = Column(JSONB())
    before = Column(JSONB())
    after = Column(JSONB())
    performer = Column(UUID(), ForeignKey(ModelColumn('User', 'id'), ondelete='CASCADE'), nullable=True)


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
    dump: dict = for_jsonify(target.as_dict(
        attributes=[(e.key if isinstance(e, Column) else str(e)) for e in (history.attributes or [])] or None,
        exclude=[(e.key if isinstance(e, Column) else str(e)) for e in (history.exclude or [])] or None,
        deep=False,
        for_history=True
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

