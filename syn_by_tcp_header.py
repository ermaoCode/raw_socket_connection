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


def raw_tcp(s, src_ip, src_port, dst_ip, dst_port, seq, ack_seq, syn_flag=0, ack_flag=1, psh_flag=0
            , payload_data=''):

    ip_source = src_ip
    ip_dest = dst_ip
    ip_protocol = socket.IPPROTO_TCP

    #  tcp header
    tcp_sport = src_port	        # source port
    tcp_dport = dst_port		# destination port
    tcp_seq = seq	    # 32-bit sequence number，这里随便指定个
    tcp_ack_seq = ack_seq		    # 32-bit ACK number。这里不准备构建ack包，故设为0
    tcp_data_offset = 5	    # 和ip header一样，没option field
    # 下面是各种tcp flags
    tcp_flag_urg = 0
    tcp_flag_ack = ack_flag
    tcp_flag_psh = psh_flag
    tcp_flag_rst = 0
    tcp_flag_syn = syn_flag
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
    # payload_data = 'wordpress.youran.me'

    # 构建pseudo ip header
    psh_saddr = socket.inet_pton(socket.AF_INET, ip_source)
    psh_daddr = socket.inet_pton(socket.AF_INET, ip_dest)
    psh_reserved = 0
    psh_protocol = ip_protocol
    psh_tcp_len = len(tcp_header) + len(payload_data)
    psh = pack('!4s4sBBH', psh_saddr, psh_daddr, psh_reserved, psh_protocol, psh_tcp_len)

    # 创建最终用于checksum的内容
    chk = psh + tcp_header + payload_data

    # 必要时追加1字节的padding
    if len(chk) % 2 != 0:
        chk += '\0'

    tcp_checksum = checksum(chk)

    # 重新构建tcp header，把checksum结果填进去
    tcp_header = pack('!HHLLBBHHH' , tcp_sport, tcp_dport, tcp_seq, tcp_ack_seq, tcp_offset_reserv, tcp_flags, tcp_window_size, tcp_checksum, tcp_urgent_ptr)

    # 最终的tcp/ip packet
    packet = tcp_header + payload_data
    # 发送出去
    s.sendto(packet, (ip_dest, 0))

if __name__ == '__main__':
    src_ip = '127.0.0.1'
    src_port = 1017
    dst_ip = '127.0.0.1'
    dst_port = 6666

    # fake_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    # fake_sock.bind((src_ip, src_port))
    # fake_sock.connect((dst_ip, dst_port))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    seqNum = 19890602 #随便初始化的一个值
    ackNum = 0
    # syn
    raw_tcp(s, src_ip, src_port, dst_ip, dst_port, seq=seqNum, ack_seq=ackNum, syn_flag=1, ack_flag=0)

    for i in range(2):
        data, addr = s.recvfrom(1024)
        print addr
        print data
        print 'len: ', len(data)
        print 'seq: ', unpack('!I', data[24:28])
        ackNum = unpack('!I', data[24:28])[0]+1
        print 'ack: ', unpack('!I', data[28:32])
        str2asc.printBinary(data)

    # ack
    raw_tcp(s, src_ip, src_port, dst_ip, dst_port, seq=seqNum+1, ack_seq=ackNum)
    # psh + payload
    payload = "hello raw"
    raw_tcp(s, src_ip, src_port, dst_ip, dst_port, seq=seqNum+1, ack_seq=ackNum, psh_flag=1, payload_data='hello raw')
    for i in range(4):
        data, addr = s.recvfrom(1024)

    # 对于服务器返回值的ack
    raw_tcp(s, src_ip, src_port, dst_ip, dst_port, seq=seqNum+1+len(payload), ack_seq=ackNum+len(payload))
