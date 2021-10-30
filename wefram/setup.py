from . import demo


async def setup_demo() -> None:
    await demo.build()
