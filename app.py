import logging
import pymediaroom

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #send command
    stb = pymediaroom.Remote()
    print(stb.get_standby())
    #stb.send_cmd("Info")
