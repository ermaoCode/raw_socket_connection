# -*- coding: utf-8 -*
import sys, socket
from struct import *
import str2asc



def raw_udp():
    ip_protocol = socket.IPPROTO_UDP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, ip_protocol)
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    data, addr = s.recvfrom(1024)
    print addr
    print data
    str2asc.printBinary(data)

    for i in range(100):
        data, addr = s.recvfrom(1024)
        print addr
        print data
        str2asc.printBinary(data)

if __name__ == '__main__':
    raw_udp()