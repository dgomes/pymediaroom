import logging

import time
import socket
import logging

import socket
import struct

_LOGGER = logging.getLogger(__name__)

version = '0.3'

Commands = {
            'Number0': 48,
            'Number1': 49,
            'Number2': 50,
            'Number3': 51,
            'Number4': 52,
            'Number5': 53,
            'Number6': 54,
            'Number7': 55,
            'Number8': 56,
            'Number9': 57,
            'Back': 8,
            'OK': 13,
            'Menu': 36,
            'Left': 37,
            'Right': 39,
            'Up': 38,
            'Down': 40,
            'ProgUp': 33,
            'ProgDown': 34,
            'VolUp': 175,
            'VolDown': 174,
            'Mute': 173,
            'Exit': 27,
            'Guide': 112,
            'Switch': 156,
            'Rec': 225,
            'PlayPause': 119,
            'Forward': 121,
            'Rewind': 118,
            'Power': 233,
            'Info': 159,
            'Search': 106,
            'Enter': 43,
            'VoD': 114,
            'Stop': 123,
            'Red': 140,
            'Green': 141,
            'Yellow': 142,
            'Blue': 143,
            'Delete': 46,
            'Options': 111,
            'Rose': 237,
            'Open': 115,
            'AV': 0,
            'Prev': 117,
            'Next': 122,
            'Options': 157,
            'Favourite': 113}

class Remote():
    """This class represents a MediaRoom Set-up-Box Remote Control."""

    def __init__(self, ip=None, port=8082, timeout=60):

        self.s = None #postpone multicast socket creation
        self.timeout = timeout
        if ip is None:
            self.stb_ip = self.discover()
        else:
            self.stb_ip = ip
        self.stb_port = port

        self.stbCmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stbCmd.connect((self.stb_ip, self.stb_port))
        self.stbCmd.recv(6)
        _LOGGER.info("Connected to %s:%s" % (self.stb_ip, self.stb_port))

    def send_cmd(self, cmd):
        if cmd not in Commands and cmd not in range(0,999):
            _LOGGER.error("Unknown command")
            return None

        keys = []
        if cmd in range(0,999):
            for c in str(cmd):
                keys.append(Commands["Number"+str(c)])
        else:
            keys = [Commands[cmd]]

        for key in keys:
            _LOGGER.debug("{} key={}".format(cmd, key))
            self.stbCmd.send("key={}\n".format(key).encode('UTF-8'))
            self.stbCmd.recv(3)
            time.sleep(0.300)

    def turn_off(self):
        """Turn off media player."""
        self.send_cmd('Power')

    def __del__(self):
        self.stbCmd.close()
        self.s.close()
        _LOGGER.info("Disconnected")

    def create_socket(self, PORT=8082, GROUP='239.255.255.250'):
        addrinfo = socket.getaddrinfo(GROUP, None)[0]

        self.s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.s.settimeout(self.timeout)
        self.s.bind(('', PORT))

        group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
        mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
        self.s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def get_notify(self):
        if self.s == None:
            self.create_socket()
        data, sender = self.s.recvfrom(2500)
        while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
        
        _LOGGER.debug(data)
        _LOGGER.debug(sender)
        return data, sender[0]

    def discover(self):
        data, src = self.get_notify()
        return src

    def get_standby(self):
        src = None
        while src != self.stb_ip:
            data, src = self.get_notify()
        if b'<tune' in data:
            return False
        return True
