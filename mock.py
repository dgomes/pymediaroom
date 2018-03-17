import socket
import sys
import time
from pymediaroom.notify import (MEDIAROOM_BROADCAST_ADDR, MEDIAROOM_BROADCAST_PORT)

MCAST_GRP = MEDIAROOM_BROADCAST_ADDR 
MCAST_PORT = MEDIAROOM_BROADCAST_PORT

mcsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
mcsock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

fake_notify = b"NOTIFY * HTTP/1.1\r\nx-type: display\r\nx-filter: d5e10bf1-fa37-4da9-be9d-b0b5249eacb9\r\nx-lastUserActivity: 1/1/2003 8:00:27 PM\r\nx-location: http://192.168.1.65:8080/dvrfs/info.xml\r\nx-debug: http://192.168.1.65:8080\r\n\r\n<node count='69255'><activities><p15n stamp='08D40311908F4B802caba4baa909'/><schedver dver='3' ver='0' pendcap='False' /><x/></activities></node>"

fake_notify = b"\x02}\x86[\xe9^\xc9\xf8H\xa5\xc13\x84\x0e\xb9\xfd\xbc\x00!\x00\x10\x001\x01\xe3\xdeDO\xa6V/\xc8D\xaf%a\xae\xf7e\xabT%\x1f\xee\x14J\x02\r\x93NOTIFY * HTTP/1.1\r\nx-type: dvr\r\nx-filter: 17f71ee7-b075-4e0f-b955-8ec9f85b395b\r\nx-lastUserActivity: 3/2/2018 10:33:04 PM\r\nx-location: http://192.168.1.65:8080/dvrfs/info.xml\r\nx-device: 230f1459-606e-4317-a8a8-0130ce57c476\r\nx-debug: http://192.168.1.65:8080\r\n\r\n<node count='35361'><activities><p15n stamp='08D3DE32508D71F0306023F84A39'/><schedver dver='3' ver='0' pendcap='True' /><x/><recordver ver='1' verid='27846' size='477815111680' free='477815111680' /><x/></activities></node>"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind(('', 8082))
sock.settimeout(2.0)
sock.listen(10)

while True:
    mcsock.sendto(fake_notify, (MCAST_GRP, MCAST_PORT))
    try:
        conn = None
        conn, addr = sock.accept()
        print("CONN")
        conn.send(b"HELLO")
        conn.settimeout(10.0)
        r = conn.recv(8)
        print(">", str(r))
        conn.send(b"OK")
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        pass
    finally:
        if conn:
            conn.close()
