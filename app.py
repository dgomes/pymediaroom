import logging
#import coloredlogs
from pymediaroom import (discover, Remote)
import asyncio

#coloredlogs.install()

async def main(loop):
    stbs = await discover(max_wait=5, loop=loop)
    stbs = list(stbs)
    if stbs:
        logging.info("Found {}".format(stbs))
        remote = Remote(stbs[0], loop=loop)
        #remote = Remote("192.168.1.69", loop=loop)
        await remote.monitor_state()

        await remote.turn_on()

        await asyncio.sleep(10)

        await remote.turn_off()

    else:
        logging.error("No STB Found")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()

