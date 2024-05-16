import asyncio
import json
import logging
import os.path

import aiohttp
from aiohttp import web
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader('templates'))


class Server:
    def __init__(self, logger):
        self._logger = logger
        self._logger.info(f"Creating Server")

    async def hello(self, request):
        return web.Response(text="Hello from command server")

    async def web(self, request):
        template = env.get_template('panel.html')
        nodes = [0, 1]
        return web.Response(text=template.render(nodes=nodes), content_type="text/html")

    async def get_yagna_log(self, request):
        yagna_no = int(request.match_info.get('no', 0))
        # get from uri:

        self._logger.info(f"Get yagna log for yagna no: {yagna_no}")
        yagna_dir = f"dock_prov_{yagna_no}/yagna"
        if os.path.isdir(yagna_dir):
            with open(f"{yagna_dir}/yagna_rCurrent.log") as f:
                log = f.read()
            return web.Response(text=log)

        return web.Response(text=f"Yagna log for yagna no: {yagna_no}")

    async def check_yanga_up(self, request):
        yagna_no = int(request.match_info.get('no', 0))
        # get from uri:

        self._logger.info(f"Check yagna up for yagna no: {yagna_no}")

        port = 8555 + yagna_no

        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": "Bearer change_me"}

            try:
                async with session.request("get", f"http://localhost:{port}/me", headers=headers) as resp:
                    body = await resp.text()
                    if resp.status == 200:
                        response = json.loads(body)
                    else:
                        response = {"error": body}
            except Exception as e:
                response = {"error": str(e)}

        return web.json_response(response)

    async def compose_down(self, request):
        self._logger.info("Stop dockers")
        os.system("docker compose down")
        return web.Response(text="Dockers stopped")

    async def compose_up(self, request):
        self._logger.info("Stop dockers")
        os.system("docker compose up -d")
        return web.Response(text="Dockers started")

    async def start(
            self,
            host: str,
            port: int,
    ):
        app = web.Application()
        app.router.add_route("GET", "/", lambda request: self.hello(request))
        app.router.add_route("GET", "/web", lambda request: self.web(request))
        app.router.add_route("GET", "/yagna/{no}/log", lambda request: self.get_yagna_log(request))
        app.router.add_route("GET", "/yagna/{no}/isup", lambda request: self.check_yanga_up(request))
        app.router.add_route("GET", "/compose/down", lambda request: self.compose_down(request))
        app.router.add_route("GET", "/compose/up", lambda request: self.compose_up(request))

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
