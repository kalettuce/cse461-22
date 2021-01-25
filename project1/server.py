from socket import *
import random
import string
import struct
import threading

#TODO: REMOVE
import sys

# student ID
ID = 690

def validate_header(data, expected_secret = -1):
    if len(data) < 12:
        return False
    # extract header
    length, psecret, step, _ = struct.unpack(">iihh", data[:12])
    expected_data_length = length + ((4 - length % 4) % 4) + 12
    if len(data) != expected_data_length or step != 1:
        return False
    if expected_secret != -1 and expected_secret != psecret:
        return False
    return True

"""
Returns a packet with the given information, as bytes in big-endian order
"""
def make_packet(msg_len, psec, step, msg):
    header = struct.pack('>iihh', msg_len, psec, step, ID)
    pad_len = (4 - len(msg) % 4) % 4;
    return header + msg + pad_len * b'\x00'

UDP_PORT = 12235

def thread_function(data_a, client_address, stream):
    # stage a
    if not validate_header(data_a):
        return

    if data_a[12:24].decode('ascii') != 'hello world\x00':
        return

    num_a = random.randrange(3, 20)
    len_a = random.randrange(10,25)
    udp_port_a = random.randrange(20000, 60000)
    secret_a = random.randrange(0x7fffffff)
    message_a = struct.pack('>iiii', num_a, len_a, udp_port_a, secret_a);

    packet_a = make_packet(16, 0, 2, message_a)
    udp_socket.sendto(packet_a, client_address)

    # stage b
    udp_socket_b = socket(AF_INET, SOCK_DGRAM)
    udp_socket_b.bind(('', udp_port_a))
    udp_socket_b.settimeout(3)
    table = [False for i in range(num_a)]

    # always drop first packet
    udp_socket_b.recv(4096)

    # loop to receive all stage b packets
    i = 0
    while i < num_a:
        data_b = udp_socket_b.recv(4096)
        if not validate_header(data_b, secret_a):
            udp_socket_b.close()
            return

        pk_id, = struct.unpack('>i', data_b[12:16])
        if table[pk_id] == False:
            if random.randrange(1, 5) <= 3:
                table[pk_id] = True
                ack_packet = make_packet(4, secret_a, 1, data_b[12:16])
                udp_socket_b.sendto(ack_packet, client_address)
                i += 1
            else:
                continue
        else:
            udp_socket_b.close()
            return
    tcp_port = random.randrange(30000, 60000)
    secret_b = random.randrange(0x7fffffff)
    message_b = struct.pack('>ii', tcp_port, secret_b)
    packet_b = make_packet(8, secret_a, 2, message_b)
    udp_socket_b.sendto(packet_b, client_address)
    udp_socket_b.close()
    
    # stage c
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.bind(('', tcp_port))
    tcp_socket.listen()
    tcp_conn, _ = tcp_socket.accept()

    # make packet c
    num_c = random.randrange(3, 20)
    len_c = random.randrange(10,25)
    secret_c = random.randrange(0x7fffffff)
    char_c = random.choice(string.ascii_letters).encode('ascii')
    #char_c = random.randrange(0x21, 0x7f) # printable chars
    message_c = struct.pack(">iiic", num_c, len_c, secret_c, char_c)
    packet_c = make_packet(13, secret_b, 2, message_c)
    tcp_conn.send(packet_c)

    # stage d
    for i in range(num_c):
        data_d = tcp_conn.recv(4096)
        if not validate_header(data_d, secret_c):
            tcp_conn.close()
            tcp_socket.close()
            return
        length, = struct.unpack('>i', data_d[:4])
        if length != len_c:
            tcp_conn.close()
            tcp_socket.close()
            return
        for c in data_d[12:12+length]:
            if c != char_c:
                tcp_conn.close()
                tcp_socket.close()
                return
        
        secret_d = random.randrange(0x7fffffff)
        message_d = struct.pack('>i', secret_d)
        packet_d = make_packet(4, secret_c, 2, message_d)
        stream.write(len(packet_d))
        tcp_conn.send(packet_d)
        #tcp_conn.close()
        #tcp_socket.close()


if __name__ == "__main__":
    sys.stdout.write('test')
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    udp_socket.bind(('', UDP_PORT))
    
    while True:
        # receive and inspect the data
        data_a, client_address = udp_socket.recvfrom(4096)
        t = threading.Thread(target=thread_function,\
                             args=(data_a, client_address, sys.stdout))
        t.start()
