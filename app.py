import logging
#import coloredlogs
from pymediaroom import (discover, Remote)
import asyncio

#coloredlogs.install()

async def main(loop):
    stbs = await discover(max_wait=5, loop=loop)
    stbs = sorted(list(stbs))


    if stbs:
        logging.info("Found {}".format(stbs))
        remote = Remote(stbs[0])
        #remote = Remote("192.168.1.69", loop=loop)
        await installMediaroomProtocol(responses_callback=remote.notify_callback)
        
        try:
            await remote.turn_on()

            await remote.send_cmd('Rose') 
            await remote.send_cmd('Rose') 
        except:
            print("can't connect to STB")

        await asyncio.sleep(10)

#        await remote.turn_off()

    else:
        logging.error("No STB Found")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()

