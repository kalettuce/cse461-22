from socket import *
import sys

attu2 = '128.208.1.138'
attu3 = '128.208.1.139'
port = 12235

message = bytearray()
message.append(0x00)
message.append(0x00)
message.append(0x00)
message.append(0x0C)
message.append(0x00)
message.append(0x00)
message.append(0x00)
message.append(0x00)
message.append(0x00)
message.append(0x01)
message.append(0x01)
message.append(0xA7)
payload = bytes("hello world", 'utf-8')
message.extend(payload)
message.append(0x00)
print(message)
s = socket(AF_INET, SOCK_DGRAM)
s.sendto(message, (attu2, port))
data, server = s.recvfrom(4096)
print(data)
print("done")