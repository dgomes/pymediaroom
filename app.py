import logging
from pymediaroom import (discover, Remote)
import asyncio

async def main(loop):
    stbs = await discover(max_wait=5, loop=loop)
    stbs = list(stbs)
    if stbs:
        logging.info("Found {}".format(stbs[0]))
        remote = Remote(stbs[0], loop=loop)

        await remote.turn_on()

        await asyncio.sleep(10)
        print("bye bye")
        await remote.turn_off()

    else:
        logging.erro("No STB Found")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()

