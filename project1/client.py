from socket import *
import struct

ATTU2 = '128.208.1.138'
ATTU3 = '128.208.1.139'
ATTU8 = '128.208.1.141'
UDP_PORT = 12235
ID = 423

"""
Returns a packet with the given information, as bytes in big-endian order
"""
def make_packet(msg_len, psec, step, msg):
    header = struct.pack('>iihh', msg_len, psec, step, ID)
    pad_len = (4 - len(msg) % 4) % 4;
    return header + msg + pad_len * b'\x00'

# stage a
udp_socket = socket(AF_INET, SOCK_DGRAM)
packet = make_packet(12, 0, 1, "hello world".encode('utf-8') + b'\x00')
udp_socket.sendto(packet, (ATTU2, UDP_PORT))
data_A = udp_socket.recv(4096)

# stage b
_, _, _, _, num, length, udp_port_2, secret_A = struct.unpack('>iihhiiii', data_A)
i = 0
while (i < num):
    message = struct.pack('>i', i) + b'\x00' * length
    packet = make_packet(len(message), secret_A, 1, message)
    udp_socket.sendto(packet, (ATTU2, udp_port_2))
    udp_socket.settimeout(0.5)
    # if no response, send again by not incrementing i
    try:
        data_B = udp_socket.recv(4096)
        i += 1
    except timeout:
        continue
# receive secret_B
data_B = udp_socket.recv(4096)

# stage c
_, _, _, _, tcp_port, secret_B = struct.unpack('>iihhii', data_B)
tcp_socket = socket(AF_INET, SOCK_STREAM)
tcp_socket.connect((ATTU2, tcp_port))
data_C = tcp_socket.recv(4096)

# stage d
_, _, _, _, num2, length2, secret_C, c = struct.unpack('>iihhiiii', data_C)
# extracting the character from the original data with padding
c_char, _, _, _ = struct.unpack('>cccc', struct.pack('>i', c))
for i in range(num2):
    message = struct.pack('>c', c_char) * length2
    packet = make_packet(len(message), secret_C, 1, message)
    tcp_socket.send(packet)
data_D = tcp_socket.recv(4096)
_, _, _, _, secret_D = struct.unpack('>iihhi', data_D)
print("Secret D:", secret_D)
print("done")
