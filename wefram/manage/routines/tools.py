from typing import *


__all__ = [
    'CSTYLE',
    'yesno',
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


def yesno(caption: Optional[str] = None, default_yes: bool = False) -> bool:
    prompt: str = (caption or "Are you sure?") + (
        " [Y|n] " if default_yes else " [y|N] "
    )
    answer: str = input(prompt)
    if not answer:
        return default_yes

    if default_yes and not answer.lower().startswith('n'):
        return True

    return answer.lower().startswith('y')


def term_choice(caption: str, options: dict, default: Optional[str] = None) -> str:
    memos: List[Tuple[str, str]] = sorted([(k, v) for k, v in options.items()], key=lambda x: x[1])
    print(f"{caption}:")
    [print(f"{'{:<4}'.format(str(i+1) + '.')} {'{:<25}'.format(m[0])} : {m[1]}") for i, m in enumerate(memos)]
    answer: Optional[int] = None
    default_answer: Optional[int] = None
    for i, m in enumerate(memos):
        if m[0] != default:
            continue
        default_answer = i
        break
    while answer is None:
        answer = term_intinput("Select an option (type the number)", default_answer)
        if answer < 1 or answer > len(memos):
            answer = None
            continue
        answer: str = memos[answer-1][0]
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

