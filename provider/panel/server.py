import asyncio
import json
import logging
import os.path

import aiohttp
from aiohttp import web
from jinja2 import Environment, FileSystemLoader

from panel.proc import run_process_async, run_process_async_text

logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader('panel/templates'))


class PanelServer:
    def __init__(self, logger):
        self._site = None
        self._runner = None
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

        # self._logger.info(f"Get yagna log for yagna no: {yagna_no}")
        yagna_dir = f"dock_prov_{yagna_no}/yagna"
        if os.path.isdir(yagna_dir):
            with open(f"{yagna_dir}/yagna_rCurrent.log") as f:
                log = f.read()
            return web.Response(text=log)

        return web.Response(text=f"Yagna log for yagna no: {yagna_no}")

    async def run_yanga_cli_command(self, request):
        yagna_no = int(request.match_info.get('no', 0))
        text = await request.text()
        safe_text = ""
        for letter in text:
            if letter.isalnum() or letter in [" ", "-", "_"]:
                safe_text += letter
            else:
                raise ValueError(f"Invalid character in command: {letter}")

        self._logger.info(f"Run yagna cli command for yagna no: {yagna_no}, command: {safe_text}")

        text = await run_process_async_text(f"docker exec provider-provider_{yagna_no}-1 yagna {text}")
        text = json.dumps(json.loads(text), indent=4)
        return web.Response(text=text)

    async def list_docker_processes(self, request):
        yagna_no = int(request.match_info.get('no', 0))

        text = await run_process_async_text(f"docker exec provider-provider_{yagna_no}-1"
                                            + " ps aux")
        text = text.decode(encoding='utf-8')
        processes = []
        for line in text.split("\n"):
            if line.startswith("USER"):
                continue
            if "aux" in line:
                continue
            spl = line.split()
            if len(spl) < 11:
                continue
            command = spl[10]
            args = spl[11:]
            command_short = command.split("/")[-1]
            process = {
                "pid": spl[1],
                "cpu": spl[2],
                "mem": spl[3],
                "vsz": spl[4],
                "rss": spl[5],
                "tty": spl[6],
                "stat": spl[7],
                "start": spl[8],
                "time": spl[9],
                "command": command_short,
                "args": " ".join(args),
                "command_path": command
            }
            processes.append(process)

        return web.json_response(processes)

    async def check_yanga_up(self, request):
        yagna_no = int(request.match_info.get('no', 0))
        # get from uri:

        # self._logger.info(f"Check yagna up for yagna no: {yagna_no}")

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
        app.router.add_route("GET", "/yagna/{no}/proc", lambda request: self.list_docker_processes(request))
        app.router.add_route("POST", "/yagna/{no}/cli", lambda request: self.run_yanga_cli_command(request))
        app.router.add_route("POST", "/compose/down", lambda request: self.compose_down(request))
        app.router.add_route("POST", "/compose/up", lambda request: self.compose_up(request))

        self._runner = aiohttp.web.AppRunner(app)
        await self._runner.setup()
        self._site = aiohttp.web.TCPSite(self._runner, host, port)
        await self._site.start()
        logger.info(f"Server started at http://{host}:{port}")

    async def stop(self):
        self._logger.info("Server stopping...")
        await self._site.stop()
        await self._runner.shutdown()
        self._logger.info("Server stopped")


