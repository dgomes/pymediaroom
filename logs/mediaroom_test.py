import logging
import time
import pymediaroom

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    #discover STB
    stb_ip = pymediaroom.Remote.discover(["192.168.1.6"])
    if stb_ip != None:
        
        logging.info("Found {}".format(stb_ip))

        #Create Remote per stb, timeout is relevant for status updates
        stb = pymediaroom.Remote(stb_ip, timeout=10)
        stb.update()

        #detect standby and power on if needed
        if (not stb.get_standby()):
            logging.info("STB is ON")
        else:
            stb.send_cmd("Power")
            logging.info("STB is turning ON")

            while (stb.get_standby()):
                time.sleep(1)
                stb.update()
            logging.info("STB is ON")
        
        #send commands
       
        for cmd in ["Number1", "ProgUp", "Mute", "VolUp", "Power"]:
            stb.send_cmd(cmd)    
       
            time.sleep(4)
            stb.update()
   
        while (not stb.get_standby()):
            time.sleep(1)
        logging.info("Demo completed")
