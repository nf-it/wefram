from typing import *


__all__ = [
    'CSTYLE',
    'term_choice',
    'term_floatinput',
    'term_intinput',
    'term_input'
]


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

