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

        remote2 = Remote("192.168.1.12", loop=loop)
#        await remote.turn_on()
        try:
            while True:
                state = await remote.get_state()
                state2 = await remote2.get_state()
                print("{} = {}".format(remote, state))
                print("{} = {}".format(remote2, state2))
                await asyncio.sleep(10)
                print("WAKE")
        except KeyboardInterrupt as e:
            pass

        print("bye bye")
#        await remote.turn_off()

    else:
        logging.error("No STB Found")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()

