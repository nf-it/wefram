from typing import *
from types import ModuleType
import uuid
import abc
import sys
import inspect
import json
import datetime
import os
import importlib
import re
from . import config


__all__ = [
    'CSTYLE',
    'ROOT',
    'JSONexactValue',
    'json_encode',
    'json_encode_custom',
    'json_decode',
    'json_from_file',
    'json_to_file',
    'json_encode_to_file',
    'json_decode_from_file',
    'for_jsonify',
    'term_input',
    'term_choice',
    'term_intinput',
    'term_floatinput',
    'isostr_2_date',
    'snakecase_to_lowercamelcase',
    'camelcase_to_snakecase',
    'rerekey_snakecase_to_lowercamelcase',
    'rerekey_camelcase_to_snakecase',
    'py_to_json',
    'json_to_py',
    'remove_from_array',
    'int_or_none',
    'is_int',
    'get_class_of_method',
    'any_in',
    'all_in',
    'str_from',
    'array_from',
    'app_has_module',
    'load_app_module',
    'get_calling_module',
    'get_calling_app',
    'load_resource',
    'has_app',
    'app_dir',
    'app_root',
    'app_path',
    'app_name',
    'app_module_name',
    'module_path'
]

_cached_resources: dict = {}

ROOT: str = config.PRJ_ROOT
CSTYLE: Dict[str, str] = {
    'clear': '\033[0m',
    'underline': '\033[4m',
    'dunderline': '\033[21m',
    'blink': '\033[5m',
    'darker': '\033[2m',
    'italic': '\033[3m',
    'bold': '\033[1m',
    'inverted': '\033[7m',
    'strikeout': '\033[9m',
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'pink': '\033[35m',
    'navy': '\033[36m',
    'white': '\033[37m',
    'Black': '\033[90m',
    'Red': '\033[91m',
    'Green': '\033[92m',
    'Yellow': '\033[93m',
    'Blue': '\033[94m',
    'Pink': '\033[95m',
    'Navy': '\033[96m',
    'White': '\03397m',
    '-black': '\033[40m',
    '-red': '\033[41m',
    '-green': '\033[42m',
    '-yellow': '\033[43m',
    '-blue': '\033[44m',
    '-pink': '\033[45m',
    '-navy': '\033[46m',
    '-white': '\033[47m',
}


class JSONcustom(abc.ABC):
    BOUNDARY: str = f"//<**=={''.join([uuid.uuid4().hex, uuid.uuid4().hex])}==**>//"

    @property
    def packed(self) -> str:
        return ''.join([self.BOUNDARY, str(self.jsonify()), self.BOUNDARY])

    @classmethod
    def extract_all_packed(cls, source: str) -> str:
        return source.\
            replace(f"\"{cls.BOUNDARY}", '').\
            replace(f"{cls.BOUNDARY}\"", '')

    @abc.abstractmethod
    def jsonify(self) -> str:
        raise NotImplementedError


class JSONexactValue(JSONcustom):
    def __init__(self, value: Any) -> None:
        self.value: Any = value

    def jsonify(self) -> str:
        return str(self.value)


class _JsonEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        from wefram.types.l10n import L10nStr
        from .ds import StoredFile, Model

        if isinstance(o, JSONcustom):
            return o.packed
        if o is None:
            return None
        elif isinstance(o, L10nStr):
            return str(o)
        elif isinstance(o, datetime.datetime):
            return o.replace(microsecond=0).isoformat(timespec='seconds')
        elif isinstance(o, datetime.date):
            return str(o.isoformat())
        elif isinstance(o, datetime.time):
            return str(o.replace(microsecond=0).isoformat(timespec='seconds'))
        elif isinstance(o, set):
            o = list(o)
        elif isinstance(o, StoredFile):
            return str(o.file_id)
        elif isinstance(o, Model):
            return o.json(deep=True)
        if isinstance(o, (dict, list, tuple, str, int, float)) or o is True or o is False or o is None:
            return self.encode(o)
        return json.JSONEncoder.default(self, o)


def json_encode(o: Any, **kwargs) -> str:
    kwargs.setdefault('ensure_ascii', False)
    return json.dumps(o, cls=_JsonEncoder, **kwargs)


def json_encode_custom(o: Any, **kwargs) -> str:
    return JSONcustom.extract_all_packed(json_encode(o, **kwargs))


def json_decode(src: str, **kwargs) -> Any:
    return json.loads(src, **kwargs)


def json_encode_to_file(o: Any, filename: str, **kwargs) -> None:
    data: Any = json_encode(o, **kwargs)
    with open(filename, 'w') as f:
        f.write(data)


def json_decode_from_file(filename: str, **kwargs) -> Any:
    with open(filename, 'r') as f:
        data = f.read()
    return json_decode(data, **kwargs)


def json_from_file(filename: str, **kwargs) -> Any:
    with open(filename, 'r') as f:
        return json.load(f, **kwargs)


def json_to_file(o: Any, filename: str, **kwargs) -> None:
    kwargs.setdefault('ensure_ascii', False)
    with open(filename, 'w') as f:
        json.dump(o, f, **kwargs)


def for_jsonify(o: Any, deep: bool = False) -> Any:
    from wefram.types.l10n import L10nStr
    from .ds import StoredFile, Model

    if isinstance(o, JSONcustom):
        return o.packed
    if o is None:
        return None
    elif isinstance(o, dict):
        return {k: for_jsonify(i) for k, i in o.items()}
    elif isinstance(o, (list, tuple, set)):
        return [for_jsonify(e) for e in o]
    elif isinstance(o, L10nStr):
        return str(o)
    elif isinstance(o, datetime.datetime):
        return o.replace(microsecond=0).isoformat(timespec='seconds')
    elif isinstance(o, datetime.date):
        return str(o.isoformat())
    elif isinstance(o, datetime.time):
        return str(o.replace(microsecond=0).isoformat(timespec='seconds'))
    elif isinstance(o, set):
        o = list(o)
    elif isinstance(o, StoredFile):
        return str(o.file_id)
    elif isinstance(o, Model):
        return o.json(deep=deep)

    return o


def term_choice(caption: str, options: dict, default: Optional[str] = None) -> str:
    memos: List[Tuple[str, str]] = sorted([(k, v) for k, v in options.items()], key=lambda x: x[1])
    [print(f"{'{:<15}'.format(k)} : {v}") for k, v in memos]
    answer: Optional[str] = None
    while answer is None:
        answer = term_input(caption, default)
        if answer not in options:
            answer = None
    return answer


def term_input(caption: str, default: Optional[str] = None) -> str:
    placeholder: str = ' '.join([s for s in [
        caption,
        f"[{default}]" if default else None
    ] if s])
    val: Optional[str] = None
    while val is None:
        val = input(f"{placeholder}: " if placeholder else '')
        if val == '':
            val = default
    return val


def term_intinput(caption: str, default: Optional[int] = None) -> int:
    answer: Optional[str, int] = None
    while answer is None:
        answer = term_input(caption, str(default))
        try:
            answer = int(answer)
        except ValueError:
            answer = None
    return answer


def term_floatinput(caption: str, default: Optional[float] = None) -> float:
    answer: Optional[str, float] = None
    while answer is None:
        answer = term_input(caption, str(default))
        try:
            answer = float(answer)
        except ValueError:
            answer = None
    return answer


def isostr_2_date(s: Union[str, datetime.date]) -> Optional[datetime.date]:
    if isinstance(s, datetime.date):
        return s
    if not isinstance(s, str):
        return None
    try:
        return datetime.date.fromisoformat(s)
    except ValueError:
        return None


def snakecase_to_lowercamelcase(text: str) -> str:
    return re.sub('_([a-zA-Z])', lambda m: m.group(1).upper(), text)


def camelcase_to_snakecase(text: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()


def rerekey_snakecase_to_lowercamelcase(d: Union[dict, list, tuple]) -> Union[dict, list]:
    if isinstance(d, (list, tuple)):
        return [rerekey_snakecase_to_lowercamelcase(x) for x in d]
    if not isinstance(d, dict):
        return d
    return {
        snakecase_to_lowercamelcase(k):
            (v if not isinstance(v, (dict, list, tuple)) else rerekey_snakecase_to_lowercamelcase(v))
        for k, v in d.items()
    }


def rerekey_camelcase_to_snakecase(d: Union[dict, list, tuple]) -> Union[dict, list]:
    if isinstance(d, (list, tuple)):
        return [rerekey_camelcase_to_snakecase(x) for x in d]
    if not isinstance(d, dict):
        return d
    return {
        camelcase_to_snakecase(k):
            (v if not isinstance(v, (dict, list, tuple)) else rerekey_camelcase_to_snakecase(v))
        for k, v in d.items()
    }


def py_to_json(d: Union[dict, list, tuple]) -> Union[dict, list]:
    return rerekey_snakecase_to_lowercamelcase(d)


def json_to_py(d: Union[dict, list, tuple]) -> Union[dict, list]:
    return rerekey_camelcase_to_snakecase(d)


def remove_from_array(elements: Sequence[Any], array: [list, set, dict]) -> [list, set, dict]:
    if isinstance(array, set):
        result: set = array.copy()
        [result.discard(e) for e in elements]

    elif isinstance(array, dict):
        result: dict = {k: v for k, v in array.items() if k not in elements}

    else:
        result: list = list(array)
        for e in elements:
            [result.remove(e) for i in range(result.count(e))]

    return result


def int_or_none(val: Any) -> Optional[int]:
    if val is None or val == '':
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def is_int(val: Any) -> bool:
    if val is None:
        return False
    try:
        x: int = int(val)
    except (ValueError, TypeError):
        return False
    return True


def get_class_of_method(method: Any) -> [ClassVar, None]:
    for cls in inspect.getmro(method.im_class):
        if method.__name__ in cls.__dict__: 
            return cls
    return None


def any_in(what: Any, where: Sequence) -> bool:
    if isinstance(what, (str, int)):
        return str(what) in where
    for a in what:
        if a not in where:
            continue
        return True
    return False


def all_in(what: Any, where: Sequence) -> bool:
    if isinstance(what, (str, int)):
        return str(what) in where
    for a in what:
        if a in where:
            continue
        return False
    return True


def str_from(value: Any) -> [None, str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if inspect.isfunction(value) or inspect.ismethod(value):
        return value()
    return str(value)


def array_from(value: Any) -> List:
    if value is None:
        return []
    elif isinstance(value, list):
        return value
    elif isinstance(value, tuple):
        return list(value)
    else:
        return [value, ]


def app_has_module(app: Union[ModuleType, str], module_name: str) -> bool:
    apath: str = module_path(app_module_name(app if isinstance(app, str) else app.__name__))
    mpath: str = os.path.join(*module_name.split('.'))
    fpath: str = os.path.join(apath, mpath)
    if os.path.isdir(fpath):
        return os.path.isfile(os.path.join(fpath, '__init__.py'))
    return os.path.isfile(f"{fpath}.py")


def load_app_module(app: Union[ModuleType, str], module_name: str) -> [None, ModuleType]:
    if not app_has_module(app, module_name):
        return None
    module_name: str = '.'.join([app_module_name(app if isinstance(app, str) else app.__name__), module_name])
    return importlib.import_module(module_name)


def get_calling_module(parent: ModuleType = None) -> str:
    frame = (parent or list(getattr(sys, '_current_frames')().values())[-1]).f_back
    name: str = str(frame.f_globals['__name__'])
    if name.startswith(f"{config.COREPKG}."):
        pname: str = get_calling_module(frame)
        if not pname.startswith('importlib') \
                and not pname == "__main__" \
                and os.path.isdir(os.path.join(ROOT, pname.split('.')[0])):
            name = pname
    return name


def get_calling_app(parent: ModuleType = None) -> str:
    calling_module: List[str] = get_calling_module(parent).split('.')
    return calling_module[0] if calling_module[0] != config.COREPKG else 'system'


def load_resource(filename: str) -> str:
    app: str = get_calling_app()
    resourcepath: str = os.path.join(app_name(app), filename)
    if resourcepath in _cached_resources:
        return _cached_resources[resourcepath]

    filepath: str = os.path.join(module_path(app), filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)

    with open(filepath, 'r') as f:
        content: str = f.read()

    _cached_resources[resourcepath] = content
    return _cached_resources[resourcepath]


def has_app(name: str) -> bool:
    root: Optional[str] = app_root(name)
    if not root:
        return False
    return os.path.isfile(os.path.join(root, 'manifest.json'))


def app_dir(name: str) -> str:
    if name == 'system':
        return 'wefram'
    return name


def app_root(name: str) -> Optional[str]:
    try:
        return module_path(name)
    except ModuleNotFoundError:
        return None


def app_path(name: str) -> str:
    if name == 'system':
        name = config.COREPKG
    return '.'.join(app_dir(name).split(os.path.sep))


def app_name(proposal: str) -> str:
    if proposal == config.COREPKG:
        return 'system'
    return proposal


def app_module_name(proposal: str) -> str:
    if proposal == 'system':
        return config.COREPKG
    return proposal


def module_path(name: str) -> str:
    if name == 'system':
        name = config.COREPKG
    for path in sys.path:
        if path == '':
            path = os.getcwd()
        path = os.path.join(path, name)
        if os.path.isdir(path):
            return path
        if os.path.isfile(f'{path}.py'):
            return path + '.py'
    raise ModuleNotFoundError(name)

