import asyncio
import json
import logging
import os.path

import aiohttp
from aiohttp import web
from jinja2 import Environment, FileSystemLoader

from gen_compose import generate_compose_file
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
        self._logger.info("docker compose down --remove-orphans")
        os.system("docker compose down")
        return web.Response(text="Dockers stopped")

    async def compose_up(self, request):
        os.system("docker build -t yagna-provider .")
        self._logger.info("docker compose up -d --remove-orphans")
        os.system("docker compose up -d")
        return web.Response(text="Dockers started")

    async def container_stop(self, request):
        yagna_no = int(request.match_info.get('no', 0))
        self._logger.info("Stop container no:")
        await run_process_async_text(f"docker compose stop provider_{yagna_no}")
        return web.Response(text="Docker stopped")

    async def container_kill(self, request):
        yagna_no = int(request.match_info.get('no', 0))
        self._logger.info("Kill container no:")
        await run_process_async_text(f"docker compose kill provider_{yagna_no}")
        return web.Response(text="Docker killed")

    async def container_start(self, request):
        yagna_no = int(request.match_info.get('no', 0))
        self._logger.info("Stop container no:")
        await run_process_async_text(f"docker compose start provider_{yagna_no}")
        return web.Response(text="Docker stopped")

    async def container_restart(self, request):
        yagna_no = int(request.match_info.get('no', 0))
        self._logger.info("Restart container no:")
        await run_process_async_text(f"docker compose restart provider_{yagna_no}")
        return web.Response(text="Docker restarted")

    async def kill_container_process(self, request, force):
        yagna_no = int(request.match_info.get('no', 0))
        proc_id = int(request.match_info.get('proc_id', 0))
        self._logger.info(f"Kill process {proc_id} in container {yagna_no}")
        kill_command = "kill -9" if force else "kill"
        await run_process_async_text(f"docker exec provider-provider_{yagna_no}-1 {kill_command} {proc_id}")
        return web.Response(text=f"Killed process {proc_id}")

    async def get_docker_env(self, request):
        yagna_no = int(request.match_info.get('no', 0))
        self._logger.info(f"Get docker env for yagna no: {yagna_no}")
        text = await run_process_async_text(f"docker exec provider-provider_{yagna_no}-1 env")
        text = text.decode(encoding='utf-8')
        results = {}
        for line in text.split("\n"):
            try: # Ignore invalid lines
                key, value = line.split("=")
                results[key] = value
            except Exception as e:
                logger.error(f"Error parsing line: {line}")
                continue

        return web.json_response(results)

    async def regenerate_compose_file(self, request):
        self._logger.info("Regenerate docker compose file")
        json_data = await request.json()
        number_of_providers = json_data.get("provCount", 2)
        expose_ports = json_data.get("exposePorts", True)
        provider_name_prefix = json_data.get("providerPrefix", "dock-prov")
        subnet = json_data.get("subnet", "change_me")
        new_file = generate_compose_file(
            number_of_providers=number_of_providers,
            expose_ports=expose_ports,
            provider_name_prefix=provider_name_prefix,
            subnet=subnet
        )
        with open("docker-compose.yml", "w") as f:
            f.write(new_file)

        return web.Response(text="Docker compose file regenerated")

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
        app.router.add_route("GET", "/yagna/{no}/env", lambda request: self.get_docker_env(request))
        app.router.add_route("POST", "/yagna/{no}/cli", lambda request: self.run_yanga_cli_command(request))
        app.router.add_route("POST", "/yagna/{no}/start", lambda request: self.container_start(request))
        app.router.add_route("POST", "/yagna/{no}/restart", lambda request: self.container_restart(request))
        app.router.add_route("POST", "/yagna/{no}/stop", lambda request: self.container_stop(request))
        app.router.add_route("POST", "/yagna/{no}/kill", lambda request: self.container_kill(request))
        app.router.add_route("POST", "/yagna/{no}/proc/{proc_id}/stop",
                             lambda request: self.kill_container_process(request, False))
        app.router.add_route("POST", "/yagna/{no}/proc/{proc_id}/kill",
                             lambda request: self.kill_container_process(request, True))
        app.router.add_route("POST", "/compose/down", lambda request: self.compose_down(request))
        app.router.add_route("POST", "/compose/up", lambda request: self.compose_up(request))
        app.router.add_route("POST", "/compose/regenerate", lambda request: self.regenerate_compose_file(request))


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


