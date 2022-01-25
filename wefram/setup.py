"""
This module uses by the ``manage`` mechanics within the ``setup`` target.
"""


from . import demo


async def setup_demo() -> None:
    await demo.build()
