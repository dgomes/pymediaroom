import logging

import socket
import socket
import struct
import asyncio
from async_timeout import timeout
from enum import Enum

from .commands import Commands
from .notify import * 
from .error import PyMediaroomError

_LOGGER = logging.getLogger(__name__)

GET_STATE_TIMEOUT = 10 
OPEN_CONTROL_TIMEOUT = 5

class State(Enum):
    OFF = 0
    PLAYING = 1
    STANDBY = 2
    UNKNOWN = -1 

class Remote():
    """This class represents a MediaRoom Set-up-Box Remote Control."""

    def __init__(self, ip, port=8082, timeout=60, loop=None):
        self.timeout = timeout
        self.stb_ip = ip
        self.stb_port = port
        self.loop = loop
        self.mr_protocol = None
        self.stb_recv = self.stb_send = None
        self.state = State.UNKNOWN
    
    def __repr__(self):
        return self.stb_ip

    async def open_control(self):
        try:
            async with timeout(OPEN_CONTROL_TIMEOUT, loop=self.loop):
                _LOGGER.debug("Connecting to %s:%s" % (self.stb_ip, self.stb_port))
                self.stb_recv, self.stb_send = await asyncio.open_connection(self.stb_ip, self.stb_port, loop=self.loop) 
                await self.stb_recv.read(6)
                _LOGGER.info("Connected to %s:%s" % (self.stb_ip, self.stb_port))
        except asyncio.TimeoutError as e:
            _LOGGER.error("Timeout connecting to %s", self.stb_ip)
            self.stb_send = self.stb_recv = None
            raise PyMediaroomError("Timeout connecting to {}".format(self.stb_ip))

    async def send_cmd(self, cmd):
        _LOGGER.debug("Send cmd = %s", cmd)
        try:
            if self.stb_recv == self.stb_send: 
                await self.open_control()
        except PyMediaroomError:
            _LOGGER.error("No connection to STB")
            return

        if cmd not in Commands and cmd not in range(0,999):
            _LOGGER.error("Unknown command")
            raise PyMediaroomError("Unknown commands")

        keys = []
        if cmd in range(0,999):
            for c in str(cmd):
                keys.append(Commands["Number"+str(c)])
        else:
            keys = [Commands[cmd]]

        try:
            for key in keys:
                _LOGGER.debug("{} key={}".format(cmd, key))
                self.stb_send.write("key={}\n".format(key).encode('UTF-8'))
                _ = await self.stb_recv.read(3)
                await asyncio.sleep(0.300)
        except asyncio.TimeoutError as e:
            _LOGGER.error(e)
            self.stb_send.close()
            self.stb_send = self.stb_recv = None
            #TODO retry send_cmd

    async def turn_on(self):
        """Turn off media player."""
        _LOGGER.debug("turn_on while %s", self.state)
        if self.state is State.STANDBY:
            await self.send_cmd('Power')

    async def turn_off(self):
        """Turn off media player."""
        _LOGGER.debug("turn_off while %s", self.state)
        if self.state is State.PLAYING:
            await self.send_cmd('Power')

    async def monitor_state(self):
        def responses_callback(notify):
            _LOGGER.debug(notify)
            if notify.tune:
                self.state = State.PLAYING
            else:
                self.state = State.STANDBY
            
        self.mr_protocol = await installMediaroomProtocol(responses_callback=responses_callback, box_ip=self.stb_ip, loop=self.loop)
            

async def discover(ignore_list = [], max_wait=30, loop=None):
    stbs = []
    try:
        async with timeout(max_wait, loop=loop):
            def responses_callback(notify):
                stbs.append(notify.ip_address)
                
            mr_protocol = await installMediaroomProtocol(responses_callback=responses_callback) 
            while True:
                await asyncio.sleep(10)
    except asyncio.TimeoutError as e:
        mr_protocol.close()
        _LOGGER.debug("discover() timeout!")

    return list(set([stb for stb in stbs if stb not in ignore_list]))
