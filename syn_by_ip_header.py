# -*- coding: utf-8 -*
'''
	A very simple raw socket implementation in Python
'''

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

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    ip_source = '127.0.0.1'
    ip_dest = '127.0.0.1'	 # 64.4.11.42' 也可以用域名：socket.gethostbyname('www.microsoft.com')

    #填写ip header
    ip_ver = 4			# ipv4
    ip_ihl = 5			# Header Length =5, 表示无options部分
    ip_dscp = 0			# 以前叫tos，现在叫dscp
    ip_total_len = 0		# left for kernel to fill
    ip_id = 22222			# fragment相关，随便写个
    ip_frag_offset = 0x4000		# fragment相关
    ip_ttl = 255			# *nix下TTL一般是255
    ip_protocol = socket.IPPROTO_TCP	# 表示后面接的是tcp数据
    ip_checksum = 0			# left for kernel to fill
    ip_saddr = socket.inet_pton(socket.AF_INET, ip_source)	# 两边的ip地址
    ip_daddr = socket.inet_pton(socket.AF_INET, ip_dest)

    ip_ver_ihl = (ip_ver << 4) + ip_ihl	# 俩4-bit数据合并成一个字节

    # 按上面描述的结构，构建ip header。
    ip_header = pack('!BBHHHBBH4s4s', ip_ver_ihl, ip_dscp, ip_total_len, ip_id, ip_frag_offset, ip_ttl, ip_protocol, ip_checksum, ip_saddr, ip_daddr)


    tcp_sport = 1001	# source port
    tcp_dport = 6666		# destination port
    tcp_seq = 19890602	# 32-bit sequence number，这里随便指定个
    tcp_ack_seq = 0		# 32-bit ACK number。这里不准备构建ack包，故设为0
    tcp_data_offset = 5	# 和ip header一样，没option field
    # 下面是各种tcp flags
    tcp_flag_urg = 0
    tcp_flag_ack = 0
    tcp_flag_psh = 0
    tcp_flag_rst = 0
    tcp_flag_syn = 1
    tcp_flag_fin = 0

    tcp_window_size = 3000
    tcp_checksum = 0
    tcp_urgent_ptr = 0

    # 继续合并small fields
    tcp_offset_reserv = (tcp_data_offset << 4)
    tcp_flags = tcp_flag_fin + (tcp_flag_syn << 1) + (tcp_flag_rst << 2) + (tcp_flag_psh <<3) + (tcp_flag_ack << 4) + (tcp_flag_urg << 5)

    # 按上面描述的结构，构建tcp header。
    tcp_header = pack('!HHLLBBHHH' , tcp_sport, tcp_dport, tcp_seq, tcp_ack_seq, tcp_offset_reserv, tcp_flags, tcp_window_size, tcp_checksum, tcp_urgent_ptr)

    # 写点东西作为data部分(可选)
    payload_data = 'wordpress.youran.me'

    # 构建pseudo ip header
    psh_saddr = ip_saddr
    psh_daddr = ip_daddr
    psh_reserved = 0
    psh_protocol = ip_protocol
    psh_tcp_len = len(tcp_header) + len(payload_data)
    psh = pack('!4s4sBBH', psh_saddr, psh_daddr, psh_reserved, psh_protocol, psh_tcp_len)

    # 创建最终用于checksum的内容
    chk = psh + tcp_header + payload_data

    # 必要时追加1字节的padding
    if len(chk) % 2 != 0:
        chk += '\0'

    print 'data: '
    str2asc.printBinary(chk)
    tcp_checksum = checksum(chk)
    print 'checksum: '
    print '%04x'%(tcp_checksum)

    # 重新构建tcp header，把checksum结果填进去
    tcp_header = pack('!HHLLBBHHH' , tcp_sport, tcp_dport, tcp_seq, tcp_ack_seq, tcp_offset_reserv, tcp_flags, tcp_window_size, tcp_checksum, tcp_urgent_ptr)

    # 最终的tcp/ip packet！
    packet = ip_header + tcp_header + payload_data
    # packet = tcp_header + payload_data
    # 发送出去

    s.sendto(packet, (ip_dest, 0))


if __name__ == '__main__':
    main()