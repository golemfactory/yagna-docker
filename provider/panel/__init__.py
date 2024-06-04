import asyncio
import logging

from panel.server import PanelServer

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    loc_logger = logging.getLogger(__name__)
    server = PanelServer(loc_logger)
    await server.start("0.0.0.0", 12834)

    while True:
        await asyncio.sleep(1)

