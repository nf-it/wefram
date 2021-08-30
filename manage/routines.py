from typing import *


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
