from .targets import pip, webpack


async def run(*_) -> None:
    pip.run()
    webpack.run()

