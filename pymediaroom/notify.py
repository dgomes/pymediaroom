"""NOTIFY message utilities."""
import struct
import asyncio
import socket
import logging
import xmltodict
import collections

from .error import PyMediaroomError

_LOGGER = logging.getLogger(__name__)

MEDIAROOM_BROADCAST_ADDR = "239.255.255.250"
MEDIAROOM_BROADCAST_PORT = 8082
TIMEOUT = 5
GEN_ID_FORMAT = "STB{}"

class MediaroomNotify(object):
    """Representation of the Mediaroom NOTIFY message."""
    def __init__(self, addr, data):
        self.src_ip = addr[0]
        self.src_port = addr[1]
        self._device = None
        while data[-1:] == '\0':
            data = data[:-1] # Strip trailing \0's
        while data[:6] != b"NOTIFY":
            data = data[1:] # Strip head garbage
        self.data = data

        for line in data.decode().split('\n'):
            if line.startswith("x-type"):
                self._type = line[line.find(":")+2:]
            elif line.startswith("x-filter"):
                self._filter = line[line.find(":")+2:]
            elif line.startswith("x-lastUserActivity"):
                self._last_user_activity = line[line.find(":")+2:]
            elif line.startswith("x-device"):
                self._device = line[line.find(":")+2:]
            elif line.startswith("x-debug") or\
                line.startswith("x-location") or\
                line.startswith("NOTIFY") or\
                line.startswith("\r"):
                pass
            elif line.startswith("<"):
                self._node = xmltodict.parse(line)['node']
#                import pprint
#                pprint.pprint(self._node)
            else:
                _LOGGER.error("UNKNOWN LINE: %s", line)

    def __str__(self):
#        _LOGGER.debug("x-type: %s", self._type)
#        _LOGGER.debug("x-filter: %s", self._filter)
#        _LOGGER.debug("x-lastUserActivity: %s", self._last_user_activity)
#        _LOGGER.debug("x-device: %s", self._device)

        return "NOTIFY from {} - {}".format(self.src_ip, self.tune)

    @property
    def tune(self):
        """XML node representing tune."""
        if self._node.get('activities'):
            tune = self._node['activities'].get('tune')
            if type(tune) is collections.OrderedDict:
                return tune
            elif type(tune) is list:
                return tune[0]
            return tune
        return None

    @property
    def stopped(self):
        """Return if the stream is stopped."""
        if self.tune and self.tune.get('@stopped'):
            return True if self.tune.get('@stopped') == 'true' else False
        else:
            raise PyMediaroomError("No information in <node> about @stopped")

    @property
    def timeshift(self):
        """Return if the stream is a timeshift."""
        if self.tune and self.tune.get('@src'):
            return True if self.tune.get('@src').startswith('timeshift') else False
        else:
            raise PyMediaroomError("No information in <node> about @src")

    @property
    def recorded(self):
        """Return if the stream is a recording."""
        if self.tune and self.tune.get('@src'):
            return True if self.tune.get('@src').startswith('mbr') else False
        else:
            raise PyMediaroomError("No information in <node> about @src")

    @property
    def ip_address(self):
        """Return IP address of the STB."""
        return self.src_ip

    @property
    def device_uuid(self):
        """Return device UUID."""
        if self._device:
            return self._device
        return GEN_ID_FORMAT.format(self.src_ip)

async def install_mediaroom_protocol(responses_callback, box_ip=None, loop=None):
    """Install an asyncio protocol to process NOTIFY messages."""
    class MediaroomProtocol:
        """Mediaroom asyncio protocol."""
        def __init__(self, loop, responses_callback, addr):
            self.loop = loop
            self.transport = None
            self.addr = addr
            self.responses = responses_callback

        def connection_made(self, transport):
            """Setup multicast socket."""
            self.transport = transport

            sock = self.transport.get_extra_info('socket')
            sock.settimeout(0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # for BSD/Darwin only
            try:
                socket.SO_REUSEPORT
            except AttributeError:
                _LOGGER.debug("No SO_REUSEPORT available, skipping")
            else:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

            # IGMP packet
            addrinfo = socket.getaddrinfo(self.addr, None)[0]
            group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
            mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            sock.bind(('', MEDIAROOM_BROADCAST_PORT))

        def datagram_received(self, data, addr):
            """Datagram received callback."""
            if not box_ip or box_ip == addr[0]:
                self.responses(MediaroomNotify(addr, data))

        def error_received(self, exc):
            """Datagram error callback."""
            _LOGGER.error('Error received: %s', exc)

        def connection_lost(self, exc):
            """Connection lost."""
            _LOGGER.info("Connection lost: %s", exc)

        def close(self):
            """Close socket."""
            _LOGGER.debug("Closing MediaroomProtocol")
            self.transport.close()

    loop = loop or asyncio.get_event_loop()

    mediaroom_protocol = MediaroomProtocol(loop, responses_callback, MEDIAROOM_BROADCAST_ADDR)

    addrinfo = socket.getaddrinfo(MEDIAROOM_BROADCAST_ADDR, None)[0]
    sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
    await loop.create_datagram_endpoint(lambda: mediaroom_protocol, sock=sock)

    return mediaroom_protocol
