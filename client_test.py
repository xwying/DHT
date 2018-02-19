import socket
from client import Client
HOST = '128.180.159.199'
PORT = 8001

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((HOST, PORT))

test_client = Client((HOST, PORT))

while True:
    msg = input("Please input msg:")
    # s.send(cmd.encode('utf-8'))
    # data = s.recv(1024)
    print(test_client.request(msg.encode('utf-8')))

    #s.close()