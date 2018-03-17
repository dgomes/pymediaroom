import logging
from pymediaroom import (discover, Remote, install_mediaroom_protocol, State)
import asyncio

async def main(loop):
    stbs = await discover(max_wait=5, loop=loop)
    stbs = sorted(list(stbs))

    if stbs:
        logging.info("Found {}".format(stbs))
        remote = Remote(stbs[0])
        #remote = Remote("192.168.1.69", loop=loop)
        await install_mediaroom_protocol(responses_callback=remote.notify_callback)


        while remote.state == State.UNKNOWN:
            await asyncio.sleep(5)

        await remote.turn_on()

        await remote.send_cmd('Rose') 
        await remote.send_cmd('Rose') 

        await asyncio.sleep(10)

    else:
        logging.error("No STB Found")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()

