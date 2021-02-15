from socket import *
import struct

ATTU2 = '128.208.1.138'
ATTU3 = '128.208.1.139'
ATTU8 = '128.208.1.141'
ID = 423

# modify here to change the target addres
TARGET = ATTU2
UDP_PORT = 12235

def make_packet(msg_len, psec, step, msg):
    """
    Returns a packet with the given information, as bytes in big-endian order
    """
    header = struct.pack('>iihh', msg_len, psec, step, ID)
    pad_len = (4 - len(msg) % 4) % 4
    return header + msg + pad_len * b'\x00'

def str_header(header):
    """
    returns header as a string "[length, psec, stage, ID]"
    """
    pay_len, psec, stage, ID = struct.unpack('>iihh', header)
    return "[" + str(pay_len) + ", " + str(psec) + ", " + str(stage) + ", " + str(ID) + "]"

# stage a
print("--- STAGE A ---")
udp_socket = socket(AF_INET, SOCK_DGRAM)
packet = make_packet(12, 0, 1, "hello world".encode('ascii') + b'\x00')
udp_socket.sendto(packet, (TARGET, UDP_PORT))
data_A = udp_socket.recv(4096)

# stage b
num, length, udp_port_2, secret_A = struct.unpack('>iiii', data_A[12:])
print("stage a2 server response header:", str_header(data_A[:12]))
print("Secret A:", secret_A, "\n")
print("--- STAGE B ---")
i = 0
udp_socket.settimeout(0.5)
while (i < num):
    message = struct.pack('>i', i) + b'\x00' * length
    packet = make_packet(len(message), secret_A, 1, message)
    udp_socket.sendto(packet, (TARGET, udp_port_2))
    # if no response, send again by not incrementing i
    try:
        data_B = udp_socket.recv(4096)
        print("ACK", i, "received")
        i += 1
    except timeout:
        continue
# receive secret_B
data_B = udp_socket.recv(4096)

# stage c
tcp_port, secret_B = struct.unpack('>ii', data_B[12:])
print("stage b2 server response header:", str_header(data_B[:12]))
print("Secret B:", secret_B, "\n")
print("--- STAGE C ---")
tcp_socket = socket(AF_INET, SOCK_STREAM)
tcp_socket.connect((TARGET, tcp_port))
data_C = tcp_socket.recv(4096)

# stage d
num_2, length_2, secret_C, c = struct.unpack('>iiii', data_C[12:])
print("stage c2 server response header:", str_header(data_C[:12]))
print("Secret C:", secret_C, "\n")
print("--- STAGE D ---")
# extracting the character from the original data with padding
c_char, = struct.unpack('>c', (struct.pack('>i', c))[:1])
for i in range(num_2):
    message = struct.pack('>c', c_char) * length_2
    packet = make_packet(len(message), secret_C, 1, message)
    tcp_socket.send(packet)
data_D = tcp_socket.recv(4096)
secret_D, = struct.unpack('>i', data_D[12:])
print("stage d2 server response header:", str_header(data_D[:12]))
print("Secret D:", secret_D)
print("done")
