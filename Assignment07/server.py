import rdt
import time
server = rdt.socket()
server.bind(('127.0.0.1', 9942))

# conn, client = server.accept()
data = server.recv(2048)
print(data)
data = server.recv(2048)
print(data)

with open('test.txt', 'w') as file:
    file.write(server.recv(2048).decode('utf-8'))

