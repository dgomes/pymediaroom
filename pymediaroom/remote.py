"""Remote control agent for Mediaroom Set up Boxes (STB)."""
import logging
import asyncio
from enum import Enum
from async_timeout import timeout

from .commands import COMMANDS
from .notify import (install_mediaroom_protocol, GEN_ID_FORMAT)
from .error import PyMediaroomError

_LOGGER = logging.getLogger(__name__)

REMOTE_CONTROL_PORT = 8082

GET_STATE_TIMEOUT = 10
OPEN_CONTROL_TIMEOUT = 5

class State(Enum):
    """Available States."""
    OFF = 0
    STANDBY = 1 
    PLAYING_LIVE_TV = 2
    PLAYING_RECORDED_TV = 3
    PLAYING_TIMESHIFT_TV = 4
    STOPPED = 5
    UNKNOWN = -1

class Remote():
    """This class represents a MediaRoom Set-up-Box Remote Control."""

    def __init__(self, ip):
        self.stb_ip = ip
        self._state = State.UNKNOWN
        self.lock = asyncio.Lock()
        self.tune_src = None
        self.current_channel = None

    @property
    def device_id(self):
        """Generate pseudo device ID from fixed IP assigned by operator."""
        return GEN_ID_FORMAT.format(self.stb_ip)

    @property
    def state(self):
        return self._state

    def resolv(self, tune_src):
        """Return the channel name. TODO: implement remote webservice to resolv tune_src"""
        self.tune_src = tune_src
        return self.current_channel

    def __repr__(self):
        return self.stb_ip

    async def send_cmd(self, cmd, loop=None):
        """Send remote command to STB."""
        _LOGGER.info("Send cmd = %s", cmd)

        if cmd not in COMMANDS and cmd not in range(0, 999):
            _LOGGER.error("Unknown command")
            raise PyMediaroomError("Unknown commands")

        keys = []
        if cmd in range(0, 999):
            for character in str(cmd):
                keys.append(COMMANDS["Number"+str(character)])
            self.current_channel = cmd
        else:
            keys = [COMMANDS[cmd]]

        try:
            async with timeout(OPEN_CONTROL_TIMEOUT, loop=loop):
                async with self.lock:
                    _LOGGER.debug("Connecting to %s:%s", self.stb_ip, REMOTE_CONTROL_PORT)
                    stb_recv, stb_send = await asyncio.open_connection(self.stb_ip,
                                                                       REMOTE_CONTROL_PORT,
                                                                       loop=loop)
                    await stb_recv.read(6)
                    _LOGGER.info("Connected to %s:%s", self.stb_ip, REMOTE_CONTROL_PORT)

                    for key in keys:
                        _LOGGER.debug("%s key=%s", cmd, key)
                        stb_send.write("key={}\n".format(key).encode('UTF-8'))
                        _ = await stb_recv.read(3)
                        await asyncio.sleep(0.300)

        except asyncio.TimeoutError as error:
            _LOGGER.warning(error)
            raise PyMediaroomError("Timeout connecting to {}".format(self.stb_ip))
        except ConnectionRefusedError as error:
            _LOGGER.warning(error)
            raise PyMediaroomError("Connection refused to {}".format(self.stb_ip))

    async def turn_on(self):
        """Turn off media player."""
        _LOGGER.debug("turn_on while %s", self._state)
        if self._state in [State.STANDBY, State.OFF, State.UNKNOWN]:
            await self.send_cmd('Power')
            self._state = State.PLAYING_LIVE_TV
        return self._state

    async def turn_off(self):
        """Turn off media player."""
        _LOGGER.debug("turn_off while %s", self._state)
        if self._state in [State.PLAYING_LIVE_TV, State.PLAYING_RECORDED_TV,
                          State.PLAYING_TIMESHIFT_TV, State.UNKNOWN]:
            await self.send_cmd('Power')
            self._state = State.OFF
        return self._state

    def notify_callback(self, notify):
        """Process State from NOTIFY message."""
        _LOGGER.debug(notify)
        if notify.ip_address != self.stb_ip:
            return

        if notify.tune:
            self._state = State.PLAYING_LIVE_TV 
            self.tune_src = notify.tune['@src']
            try:
                if notify.stopped:
                    self._state = State.STOPPED
                elif notify.timeshift:
                    self._state = State.PLAYING_TIMESHIFT_TV
                elif notify.recorded:
                    self._state = State.PLAYING_RECORDED_TV
            except PyMediaroomError as e:
                _LOGGER.debug("%s please report at https://github.com/dgomes/pymediaroom/issues", e)
        else:
            self._state = State.STANDBY
        
        _LOGGER.debug("%s is %s", self.stb_ip, self._state)
        return self._state

async def discover(ignore_list=[], max_wait=30, loop=None):
    """List STB in the network."""
    stbs = []
    try:
        async with timeout(max_wait, loop=loop):
            def responses_callback(notify):
                """Queue notify messages."""
                _LOGGER.debug("Found: %s", notify.ip_address)
                stbs.append(notify.ip_address)

            mr_protocol = await install_mediaroom_protocol(responses_callback=responses_callback)
            await asyncio.sleep(max_wait)
    except asyncio.TimeoutError:
        mr_protocol.close()
        _LOGGER.debug("discover() timeout!")

    return list(set([stb for stb in stbs if stb not in ignore_list]))
