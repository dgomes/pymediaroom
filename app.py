import logging
from pymediaroom import (discover, Remote, install_mediaroom_protocol, State)
import asyncio

async def main():
    stbs = await discover(max_wait=5)
    stbs = sorted(list(stbs))

    if stbs:
        logging.info("Found {}".format(stbs))
        remote = Remote(stbs[0])
        #remote = Remote("192.168.1.69")
        await install_mediaroom_protocol(responses_callback=remote.notify_callback)


        while remote.state == State.UNKNOWN:
            await asyncio.sleep(5)

        await remote.turn_on()

        await remote.send_cmd(100) 
        await asyncio.sleep(10)
        await remote.send_cmd(5) 

        await asyncio.sleep(10)

    else:
        logging.error("No STB Found")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

