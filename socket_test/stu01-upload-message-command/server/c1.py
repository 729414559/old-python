#/usr/bin/python env
#coding:utf8

##################
#最基础的
##################

# import socket
#
# #创建socket对象
# obj = socket.socket()
# #连接服务端IP和端口
# obj.connect(("127.0.0.1",9999,))
# #接收服务端发送过来的消息（1024表示最多只能接收1024个字节）
# ret_bytes = obj.recv(1024)
# #把bytes字节转换成字符串（因python3 scoket传输数据时必须为字节，所以接收后需要重新转换成字符串）
# ret_str = str(ret_bytes,encoding='utf-8')
# print(ret_str)
# #关闭客户端
# obj.close()

# ##################
# #一边收一边发
# ##################
# import socket
#
#
# obj = socket.socket()
# obj.connect(("127.0.0.1",9999,))
#
#
# ret_bytes = obj.recv(1024)
# ret_str = str(ret_bytes,encoding='utf-8')
# print(ret_str)
#
# while True:
#     #发送
#     inp = input("请输入要发送的内容：")
#     if inp == "quit":
#         obj.sendall(bytes("quit", encoding='utf-8'))
#         break
#     obj.sendall(bytes(inp,encoding='utf-8'))
#     #接收
#     ret_bytes = obj.recv(1024)
#     ret_str = str(ret_bytes,encoding='utf-8')
#     print(ret_str)
#
# # #关闭客户端
# # obj.close()


# ##################
# #发送字典
# ##################
# import socket
# import json
# import re
#
# obj = socket.socket()
# obj.connect(("127.0.0.1",9999,))
#
# #发送
# dt = {"name":"darren","age":18}
# #把字典转换成字符串
# dt_str = json.dumps(dt)
# obj.sendall(bytes(dt_str,encoding='utf-8'))
#
# #接收
# ret_bytes = obj.recv(1024)
# ret_str = str(ret_bytes,encoding='utf-8')
# print(ret_str)
# print(type(ret_str))
# #因接收时候有其它字符，匹配出字典的字符串
# ret_list = re.findall("\{.*\}",ret_str.strip())
# #转换成字典
# ret_dict = json.loads(ret_list[0])
# print(ret_dict)
# print(type(ret_dict))
#
# # #关闭客户端
# obj.close()




# ##################
# #发送大文件
# ##################
# import socket
# import os
# import json
# import hashlib
#
#
# obj = socket.socket()
# obj.connect(("127.0.0.1",9999,))
#
# def file_info():
#     #选择文件
#     for n in os.listdir():
#         if os.path.isfile(n):
#             file_size = os.path.getsize(n)
#             print("%s \t%s"%(n,file_size))
#     #获取文件大小
#     file_name = input("Please choose file:")
#     file_size = os.path.getsize(file_name)
#     return file_name,file_size
#
# def hash(file_name,file_size):
#     #获取文件hash值
#     has = hashlib.md5()
#     with open(file_name,'rb') as f:
#         has = hashlib.md5()
#         has.update(f.read())
#         m = has.hexdigest()
#     print(m)
#     file_info = {"name":file_name,"size":file_size,"hash":m}
#     return file_info
#
# def send_file(file_info,file_name,file_size):
#     #发送文件大小信息
#     file_info_str = json.dumps(file_info)
#     obj.sendall(bytes(file_info_str,encoding='utf-8'))
#     #读取发送的文件
#     with open(file_name,'r',encoding='utf-8') as f:
#         while True:
#             block = f.read(1024)
#             if int(file_size) <=0:
#                 break
#             else:
#                 obj.sendall(bytes(block,encoding='utf-8'))
#                 file_size -= 1024
#                 print(file_size)
#
# def recv_response():
#     #接收服务端，最后的验证字段
#     ret_bytes = obj.recv(1024)
#     ret_str = str(ret_bytes,encoding='utf-8')
#     print(ret_str)
#     #关闭客户端
#     obj.close()
#
# if __name__ =='__main__':
#     file_name, file_size = file_info()
#     file_info = hash(file_name,file_size)
#     send_file(file_info,file_name,file_size)
#     recv_response()




##################
#发送大文件
##################
import socket
import os
import json
import hashlib


obj = socket.socket()
obj.connect(("127.0.0.1",9999,))

def file_info():
    #选择文件
    for n in os.listdir():
        if os.path.isfile(n):
            file_size = os.path.getsize(n)
            print("%s \t%s"%(n,file_size))
    #获取文件大小
    file_name = input("Please choose file:")
    file_size = os.path.getsize(file_name)
    return file_name,file_size

def hash(file_name,file_size):
    #获取文件hash值
    has = hashlib.md5()
    with open(file_name,'rb') as f:
        has = hashlib.md5()
        has.update(f.read())
        m = has.hexdigest()
    print(m)
    file_info = {"name":file_name,"size":file_size,"hash":m}
    return file_info

def send_file(file_info,file_name,file_size):
    #发送文件大小信息
    file_info_str = json.dumps(file_info)
    obj.sendall(bytes(file_info_str,encoding='utf-8'))
    #obj.recv(1024)
    #读取发送的文件
    #with open(file_name,'r',encoding='utf-8') as f:
    with open(file_name, 'rb') as f:
        total_size = file_size
        while True:
            if int(file_size) <=0:
                print("发送完成")
                break
            block = f.read(1024)
            obj.sendall(bytes(block))
            file_size -= 1024
            #统计发送百分比
            tmp_num = (file_size / total_size) *100
            print("剩余：%.3f%%" %tmp_num)

def recv_response():
    #接收服务端，最后的验证字段
    ret_bytes = obj.recv(1024)
    ret_str = str(ret_bytes,encoding='utf-8')
    print(ret_str)
    #关闭客户端
    obj.close()

if __name__ =='__main__':
    file_name, file_size = file_info()
    file_info = hash(file_name,file_size)
    send_file(file_info,file_name,file_size)
    #recv_response()