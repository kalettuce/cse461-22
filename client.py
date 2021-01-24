from socket import *
import struct

attu2 = '128.208.1.138'
attu3 = '128.208.1.139'
port = 12235
ID = 423

def makepacket(length, psec, step, message):
    header = struct.pack('>iihh', length, psec, step, ID)
    pad = len(message) % 4
    if (pad != 0):
        pad = 4 - pad
    return header + message + pad * b'\x00'

# stage a
packet = makepacket(12, 0, 1, "hello world".encode('utf-8'))
print(packet)
s = socket(AF_INET, SOCK_DGRAM)
s.sendto(packet, (attu2, port))
data = s.recv(4096)

# stage b
_, _, _, _, num, length, udp_port, secA = struct.unpack('>iihhiiii', data)
i = 0
while (i < num):
    message = struct.pack('>i', i) + b'\x00' * length
    packet = makepacket(len(message), secA, 1, message)
    s.sendto(packet, (attu2, udp_port))
    s.settimeout(0.5)
    try:
        dataB = s.recv(4096)
        i += 1
    except timeout:
        continue

dataB = s.recv(4096)

# stage c
_, _, _, _, tcp_port, secB = struct.unpack('>iihhii', dataB)
tcps = socket(AF_INET, SOCK_STREAM)
tcps.connect((attu2, tcp_port))
dataC = tcps.recv(4096)

# stage d
pl, _, _, _, num2, len2, secC, c = struct.unpack('>iihhiiii', dataC)
cpk = struct.pack('>i', c)
_, _, _, ch = struct.unpack('>cccc', cpk)
for i in range(num2):
    message = struct.pack('>c', ch) * len2
    packet = makepacket(len(message), secC, 1, message)
    print(packet)
    tcps.send(packet)

dataD = tcps.recv(4096)
print(dataD)
print("done")