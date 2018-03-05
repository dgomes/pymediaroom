import struct 
import asyncio
import socket
import logging
import xmltodict

from datetime import datetime
from async_timeout import timeout

_LOGGER = logging.getLogger(__name__)

DISCOVERY_BROADCAST_ADDR = "239.255.255.250" 
DISCOVERY_BROADCAST_PORT = 8082
TIMEOUT = 5

class MRNotify(object):
    def __init__(self, addr, data):
        self.src_ip = addr[0]
        self.src_port = addr[1]
        self._tune = None

        while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
        while data[:6] != b"NOTIFY": data = data[1:] # Strip head garbage

        for line in data.decode().split('\n'):
            _LOGGER.debug(line)
            if line.startswith("x-type"):
                self.type = line.split(":")[1]
            if line.startswith("x-filter"):
                self.filter = line.split(":")[1]
            if line.startswith("x-lastUserActivity"):
                self.lastUserActivity = line.split(":")[1]
            if line.startswith("x-device"):
                self.device = line.split(":")[1]

            if line.startswith("<"):
                self.node = xmltodict.parse(line)['node']

        _LOGGER.debug(self)
        if b"<tune" in data:
            self._tune = True
        self.data = data

    def __str__(self):
        return self.src_ip

    @property
    def tune(self):
        return self.tune

    @property
    def ip_address(self):
        return self.src_ip

async def getNotify(device=None, max_wait=30, loop=None):

    class MediaroomDiscoveryProtocol:
        def __init__(self, max_wait, loop, addr):
            self.loop = loop
            self.transport = None
            self.addr = addr
            self.responses = asyncio.Queue(loop=loop)
            self.start_time = None
            self.max_wait = max_wait

        def connection_made(self, transport):
            self.transport = transport
            
            sock = self.transport.get_extra_info('socket')
            sock.settimeout(TIMEOUT)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # for BSD/Darwin only
            try:
                socket.SO_REUSEPORT
            except AttributeError:
                _LOGGER.debug("No SO_REUSEPORT available, skipping")
            else:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

            sock.bind(('', DISCOVERY_BROADCAST_PORT))

            # IGMP packet
            addrinfo = socket.getaddrinfo(self.addr, None)[0]
            group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
            mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            self.start_time = datetime.utcnow().timestamp() 

        def datagram_received(self, data, addr):
            self.responses.put_nowait(MRNotify(addr, data))

        def error_received(self, exc):
            _LOGGER.error('Error received:', exc)

        def connection_lost(self, exc):
            if exc:
                _LOGGER.error('Connection lost:', exc)

        def close(self):
            self.transport.close()

        def timeout(self):
            return self.remaining <= 0

        @property
        def remaining(self):
            return self.start_time + self.max_wait - datetime.utcnow().timestamp() 

    loop = loop or asyncio.get_event_loop()

    md = MediaroomDiscoveryProtocol(max_wait, loop,DISCOVERY_BROADCAST_ADDR)

    addrinfo = socket.getaddrinfo(DISCOVERY_BROADCAST_ADDR, None)[0]
    sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
    await loop.create_datagram_endpoint(lambda: md, sock=sock)

    try:
        async with timeout(md.remaining, loop=loop):
            while not md.timeout():
                yield await md.responses.get()
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        _LOGGER.error(e)
    finally:
        md.close()

