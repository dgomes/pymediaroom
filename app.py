import logging
import pymediaroom

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    #discover STB
    stb_ip = pymediaroom.Remote.discover()
    logging.info("Found {}".format(stb_ip))

    #Create Remote per stb, timeout is relevant for status updates
    stb = pymediaroom.Remote(stb_ip, timeout=10)
    #monitor standby
    while(not stb.get_standby()):
        logging.info("OK")
    #send command
    #stb.send_cmd("Info")
