from socket import *
from dnslib import DNSRecord
import time

# Upstream Address, use google DNS
remoteServer = '8.8.8.8'
localPort = 53


# Query the DNS
def query(query_data, remote_server, local_port):
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.sendto(query_data, (remote_server, local_port))
    response, server_address = client_socket.recvfrom(2048)
    return response


serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', localPort))
print("The server is ready to receive")

cache = {}
dying = {}

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    print('Request Inbound')
    request = DNSRecord.parse(message)
    question = request.questions
    rid = request.header.id

    if cache.get(repr(question)):  # Local cache is the same with the server
        server_reply_dns = cache.get(repr(question))
        print('Local match server')
        if time.time() <= dying[repr(question)]:
            local_reply_dns = DNSRecord.parse(server_reply_dns)
            local_reply_dns.header.id = rid
            for numbers in local_reply_dns.rr:
                numbers.ttl = int(dying[repr(question)] - time.time())
            server_reply_dns = DNSRecord.pack(local_reply_dns)
        else:
            print('Local outdated')
            server_reply_dns = query(message, remoteServer, localPort)
            local_reply_dns = DNSRecord.parse(server_reply_dns)
            min_ttl = 600
            for numbers in local_reply_dns.rr:
                if numbers.ttl < min_ttl:
                    min_ttl = numbers.ttl
            for numbers in local_reply_dns.rr:
                numbers.ttl = min_ttl
            cache[repr(question)] = DNSRecord.pack(local_reply_dns)
            dying[repr(question)] = time.time() + local_reply_dns.a.ttl
            print('Required')
    else:
        server_reply_dns = query(message, remoteServer, localPort)
        local_reply_dns = DNSRecord.parse(server_reply_dns)
        min_ttl = 600
        for numbers in local_reply_dns.rr:
            if numbers.ttl < min_ttl:
                min_ttl = numbers.ttl
        for numbers in local_reply_dns.rr:
            numbers.ttl = min_ttl
        cache[repr(question)] = DNSRecord.pack(local_reply_dns)
        dying[repr(question)] = time.time() + local_reply_dns.a.ttl
        print('Required')

    serverSocket.sendto(DNSRecord.pack(local_reply_dns), clientAddress)
    print('Answers sent')
    print('---------罪----恶----的----分----割----线-------------')
