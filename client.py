from socket import *
import struct

attu2 = '128.208.1.138'
attu3 = '128.208.1.139'
port = 12235
ID = 423

def makepacket(length, step, psec, message):
    header = struct.pack('>iihh', length, step, psec, ID)
    return header + message.encode('utf-8') + (4 - len(message) % 4) * b'\x00'

packet = makepacket(12, 1, 0, "hello world")
print(packet)

s = socket(AF_INET, SOCK_DGRAM)
s.sendto(packet, (attu2, port))
data = s.recv(4096)
print(data)
print("done")