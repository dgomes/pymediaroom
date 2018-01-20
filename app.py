import logging
import pymediaroom

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    #discover STB
    stb_ip = pymediaroom.Remote.discover(["192.168.1.6"])
    if stb_ip != None:
        
        logging.info("Found {}".format(stb_ip))

        #Create Remote per stb, timeout is relevant for status updates
        stb = pymediaroom.Remote(stb_ip, timeout=10)
        #monitor standby
        while(not stb.get_standby()):
            logging.info("OK")
        logging.info("STB is in Standby")
        #send command
        #stb.send_cmd("Info")
