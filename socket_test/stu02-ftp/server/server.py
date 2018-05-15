#/usr/bin/python env
#coding:utf8

'''
用户认证
支持断点续传
客户端支持目录切换
客户端可以查看服务端文件(如果写不出忽略)
'''

import socketserver
import os
import json

class MyServer(socketserver.BaseRequestHandler):

    def handle(self):
        # print self.request,self.client_address,self.server
        conn = self.request
        conn.sendall(bytes('欢迎使用FTP系统',encoding='utf-8'))
        #登入
        while True:
            if user_login(conn) == True:
                ftp_receive(conn)
                break
            else:
                #如果用户密码不对，继续登入
                continue


def user_login(conn):
    # 接收用户名密码
    data_bytes = conn.recv(1024)
    data_user_str = str(data_bytes, encoding='utf-8')
    print(data_user_str)
    conn.sendall(bytes('null', encoding='utf-8'))
    data_bytes = conn.recv(1024)
    data_passwd_str = str(data_bytes, encoding='utf-8')
    print(data_passwd_str)
    # 判断用户密码
    if data_user_str == 'darren' and data_passwd_str == "123":
        conn.sendall(bytes('登入成功', encoding='utf-8'))
        return True
    else:
        conn.sendall(bytes('登入失败', encoding='utf-8'))
        return False

def ftp_receive(conn):
    while True:
        data = conn.recv(1024)
        data_str = str(data,encoding='utf-8')
        print(data_str)
        hander,file_size_str,file_path,file_status,file_dir_list = data_str.split('|')
        file_size_int = int(file_size_str)
        print(hander, file_size_int, file_path,file_status)
        if hander == "file":
            #发送消息告诉客户端要开始发送
            conn.sendall(bytes("server-respone",encoding='utf-8'))

            #如果是单文件
            if file_status == "no":
                with open(file_path, 'wb') as f:
                    while file_size_int >=0:
                        #print(file_size_int)
                        # 接收文件
                        data = conn.recv(1024)
                        f.write(data)
                        file_size_int -= 1024
                if os.path.getsize(file_path) == int(file_size_str):
                    print("%s 文件接收完毕" % file_path)
                conn.sendall(bytes('发送完成 %s' % file_path, encoding='utf-8'))
                continue
            #如果是目录下的多文件
            elif file_status == "yes":
                #按文件路径依次
                with open(file_path,'wb') as f:
                    while file_size_int >0:
                        # 接收文件
                        data = conn.recv(1024)
                        f.write(data)
                        file_size_int -= 1024
                if os.path.getsize(file_path) == int(file_size_str):
                    print("%s 文件接收完毕"%file_path)
                conn.sendall(bytes('发送完成 %s'%file_path,encoding='utf-8'))
                continue
        elif hander == "dir":
            os.mkdir(file_path)
            file_path_list = json.loads(file_dir_list)
            for dir in file_path_list:
                os.mkdir(dir)
            conn.sendall(bytes('目录创建完成 %s' % file_path, encoding='utf-8'))

        elif hander == "lls":
            root_path = os.listdir()
            root_path_str = str(root_path)
            conn.sendall(bytes(root_path,encoding='utf-8'))
if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('127.0.0.1',8000),MyServer)
    server.serve_forever()