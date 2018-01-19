import logging
import pymediaroom

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #send command
    stb = pymediaroom.Remote()
    while(not stb.get_standby()):
        print("OK")
    #stb.send_cmd("Info")
