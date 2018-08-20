# -*- coding: utf-8 -*
import sys, socket
from struct import *
import str2asc


def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        w = (ord(msg[i]) << 8 ) + ord(msg[i+1])
        s = carry_around_add(s, w)
    return ~s & 0xffff


def raw_udp(src_ip, src_port, dst_ip, dst_port):
    ip_protocol = socket.IPPROTO_UDP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, ip_protocol)
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    ip_source = src_ip
    ip_dest = dst_ip

    udp_sport = src_port
    udp_dport = dst_port

    udp_header_length = 8;

    payload_data = 'hello world'
    udp_length = udp_header_length + len(payload_data)
    udp_checksum = 0

    udp_header = pack('!HHHH', udp_sport, udp_dport, udp_length, udp_checksum)

    # 构建pseudo ip header
    psh_saddr = socket.inet_pton(socket.AF_INET, ip_source)
    psh_daddr = socket.inet_pton(socket.AF_INET, ip_dest)
    psh_reserved = 0
    psh_protocol = ip_protocol
    psh_udp_len = udp_length
    psh = pack('!4s4sBBH', psh_saddr, psh_daddr, psh_reserved, psh_protocol, psh_udp_len)

    # 创建最终用于checksum的内容
    chk = psh + udp_header + payload_data

    # 必要时追加1字节的padding
    if len(chk) % 2 != 0:
        chk += '\0'

    udp_checksum = checksum(chk)
    udp_header = pack('!HHHH', udp_sport, udp_dport, udp_length, udp_checksum)

    packet = udp_header + payload_data
    # 发送出去
    s.sendto(packet, (ip_dest, 0))

    # listener_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, ip_protocol)
    # listener_sock.bind(('', src_port))

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
    src_ip = '192.168.1.165'
    src_port = 1002
    dst_ip = '192.168.1.159'
    dst_port = 6666


    raw_udp(src_ip, src_port, dst_ip, dst_port)