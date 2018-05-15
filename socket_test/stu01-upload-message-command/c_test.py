#/usr/bin/python env
#coding:utf8

import socket

import socket

ip_port = ('127.0.0.1',8001)
sk = socket.socket()
sk.connect(ip_port)

while True:
    inp = input('please input:')
    sk.sendall(bytes(inp,encoding='utf-8'))
    data_bytes = sk.recv(1024)
    print(str(data_bytes,encoding='utf-8'))
sk.close()