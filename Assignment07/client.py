import rdt
import time

test1 = 'test1test1test1'

test2 = 'test2kajshdak'

if __name__ == '__main__':
    client = rdt.socket()
    client.send(test1.encode('utf-8'), ('127.0.0.1', 9942))
    client.send(test2.encode('utf-8'), ('127.0.0.1', 9942))
    with open('test.txt') as testfile:
        client.send(testfile.read().encode('utf-8'), ('127.0.0.1', 9942))
