import asyncio
import logging

import aiohttp
from aiohttp import web

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, logger):
        self._logger = logger
        self._logger.info(f"Creating Server")

    async def hello(self, request):
        return web.Response(text="Hello from command server")

    async def start(
            self,
            host: str,
            port: int,
    ):
        app = web.Application()
        app.router.add_route("GET", "/", lambda request: self.hello(request))

        self._runner = aiohttp.web.AppRunner(app)
        await self._runner.setup()
        self._site = aiohttp.web.TCPSite(self._runner, host, port)
        await self._site.start()

    async def stop(self):
        self._logger.info("Server stopping...")
        await self._site.stop()
        await self._runner.shutdown()
        self._logger.info("Server stopped")


async def main():
    logging.basicConfig(level=logging.DEBUG)
    loc_logger = logging.getLogger(__name__)
    server = Server(loc_logger)
    await server.start("127.0.0.1", 12834)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
