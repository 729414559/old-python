#/usr/bin/python env
#coding:utf8

##################
#最基础的
##################

# import socket
#
# #创建socket对象
# sk = socket.socket()
# #绑定IP和端口（传入一个元组）
# sk.bind(("127.0.0.1",9999,))
# #限制几个客户端来连接
# sk.listen(5)
#
# #循环接收客户端发送的消息
# while True:
#     #接收客户端的请求（该语句会阻塞，它会等待对方回复）conn：表示当前建立的链路。address：表示客户端的IP和端口
#     conn,address = sk.accept()
#     #给当前连接的客户端发送一段字符串（python2.7可直接发送,python3需要转换成bytes字节在发送）
#     conn.sendall(bytes("你好呀呀呀",encoding='utf-8'))
#     print(address,conn)


# ##################
# #一边法一边收
# ##################
# import socket
#
# #创建socket对象
# sk = socket.socket()
# #绑定IP和端口（传入一个元组）
# sk.bind(("127.0.0.1",9999,))
# #限制几个客户端来连接
# sk.listen(5)
#
# #循环接收客户端发送的消息
# while True:
#     conn, address = sk.accept()
#     conn.sendall(bytes("你好,我是服务器",encoding='utf-8'))
#     while True:
#         ret_bytes = conn.recv(1024)
#         ret_str = str(ret_bytes,encoding='utf-8')
#         if ret_str == "quit":
#             break
#         print(ret_str)
#         conn.sendall(bytes("服务端已收到：\t"+ret_str,encoding='utf-8'))



# ##################
# #发送字典
# ##################
# import socket
# import json
#
# sk = socket.socket()
# sk.bind(("127.0.0.1",9999,))
# sk.listen(5)
#
# #接收
# conn, address = sk.accept()
# ret_bytes = conn.recv(1024)
# #把bytes串转换成字符串
# ret_str = str(ret_bytes,encoding='utf-8')
# #把字符串转换成字典
# ret_dict = json.loads(ret_str)
# print(ret_dict)
#
# #发送
# conn.sendall(bytes("服务端已收到：\t"+ret_str,encoding='utf-8'))


#
# ##################
# #接收大文件
# ##################
# import socket
# import os
# import json
# import hashlib
#
# sk = socket.socket()
# sk.bind(("127.0.0.1",9999,))
# sk.listen(5)
#
# def recv_write():
#     # 接收
#     file_size = 0
#     conn, address = sk.accept()
#     dict_bytes = conn.recv(1024)
#     dict_str = str(dict_bytes, encoding='utf-8')
#     dt = json.loads(dict_str)
#     dict_file_size = dt['size']
#
#     #写入文件
#     with open("temp_file",'w',encoding='utf-8') as f:
#         while True:
#             ret_bytes = conn.recv(1024)
#             #把bytes转换成字符串
#             ret_str = str(ret_bytes,encoding='utf-8')
#             #每次接收1024字节，接收完毕退出
#             if int(dict_file_size) <= 0:
#                 break
#             else:
#                 f.write(ret_str)
#                 dict_file_size -= 1024
#     return dict_str,conn
#
# def rename(dict_str):
#     #重新修改文件名
#     dt = json.loads(dict_str)
#     file_rename = dt['name']
#     if os.path.exists(file_rename):
#         os.remove(file_rename)
#     os.rename("temp_file",file_rename)
#     return dt
#
# def hash(dt):
#     #hash验证
#     has = hashlib.md5()
#     file_rename = dt['name']
#     with open(file_rename,'rb') as f:
#         has = hashlib.md5()
#         has.update(f.read())
#         hash_value = has.hexdigest()
#     print("dt:%s,lt:%s"%(dt['hash'],hash_value))
#     return file_rename,hash_value
#
# def sendreport(conn,file_rename,hash_value):
#     #告诉客户端接收完毕
#     if dt['hash'] == hash_value:
#         conn.sendall(bytes("文件：%s \t传输完毕"%file_rename,encoding='utf-8'))
#     else:
#         conn.sendall(bytes("文件：%s \t传输失败"%file_rename, encoding='utf-8'))
#
# if __name__ =='__main__':
#     dict_str,conn = recv_write()
#     dt = rename(dict_str)
#     file_rename,hash_value = hash(dt)
#     sendreport(conn,file_rename,hash_value)




##################
#接收大文件
##################
import socket
import os
import json
import hashlib

sk = socket.socket()
sk.bind(("127.0.0.1",9999,))
sk.listen(5)

def recv_write():
    # 接收
    file_size = 0
    conn, address = sk.accept()
    dict_bytes = conn.recv(1024)
    dict_str = str(dict_bytes, encoding='utf-8')
    dt = json.loads(dict_str)
    dict_file_size = dt['size']
    #conn.sendall(bytes("",encoding='utf-8'))

    #写入文件
    with open("temp_file",'wb') as f:
        while True:
            ret_bytes = conn.recv(1024)
            #把bytes转换成字符串
            ret_str = str(ret_bytes)
            #每次接收1024字节，接收完毕退出
            if int(dict_file_size) <= 0:
                break
            f.write(ret_bytes)
            dict_file_size -= 1024
            print(ret_str)
        print("接收完毕")
    return dict_str,conn

def rename(dict_str):
    #重新修改文件名
    dt = json.loads(dict_str)
    file_rename = dt['name']
    if os.path.exists(file_rename):
        os.remove(file_rename)
    os.rename("temp_file",file_rename)
    return dt

def hash(dt):
    #hash验证
    has = hashlib.md5()
    file_rename = dt['name']
    with open(file_rename,'rb') as f:
        has = hashlib.md5()
        has.update(f.read())
        hash_value = has.hexdigest()
    print("dt:%s,lt:%s"%(dt['hash'],hash_value))
    return file_rename,hash_value

def sendreport(conn,file_rename,hash_value):
    #告诉客户端接收完毕
    if dt['hash'] == hash_value:
        conn.sendall(bytes("文件：%s \t传输完毕"%file_rename,encoding='utf-8'))
    else:
        conn.sendall(bytes("文件：%s \t传输失败"%file_rename, encoding='utf-8'))

if __name__ =='__main__':
    dict_str,conn = recv_write()
    dt = rename(dict_str)
    #file_rename,hash_value = hash(dt)
    #sendreport(conn,file_rename,hash_value)

