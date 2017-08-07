import logging
import pymediaroom

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    #send command
    stb = mediaroom.Remote()
    stb.send_cmd("Number5")
