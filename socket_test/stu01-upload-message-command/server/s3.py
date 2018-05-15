#/usr/bin/python env
#coding:utf8

"""
开发一个支持多用户在线的FTP程序
要求
    1、 用户md5加密认证
    2、 允许同时多用户登录(socketserver)
    3、 执行命令:
            客户端:xxx
            服务器：subprocess
        能够聊天:
            客户端发送xxx，服务器检测回复ooo

    4、 上传文件（文件名必须一致）
            文件传输过程中显示进度条
            支持文件的断点续传（可选），思路：先发送指令到服务端获取当前续传文件字节，在发送给客户端,客户端seek到该子节点，开始读取发送。
"""


import socketserver
import hashlib
import json
import getpass
import subprocess
import os

class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
            # print self.request,self.client_address,self.server
            conn = self.request
            conn.sendall(bytes('欢迎来到XXX，请输入用户名和密码，登入系统：',encoding='utf-8'))     #1
            # Flag = True
            # while Flag:
            respone_messge = {'header': '', 'content': ''}
            while True:
                #接受客户端发送过来的用户名和密码字典
                recv_data = conn.recv(1024) #4
                client_json = str(recv_data,encoding='utf-8')
                client_dict = json.loads(client_json)
                print(type(client_dict),client_dict)

                #用户验证
                if client_dict["header"] == "login":
                    print(client_dict)
                    client_user = client_dict['user']
                    client_passwd = client_dict['passwd']
                    user_obj = User()

                    respone_messge['header'] = 'login'
                    if user_obj.login(client_user,client_passwd) == 0:
                        #print("登入成功")
                        respone_messge['content'] = '登入成功'
                        conn.sendall(bytes(json.dumps(respone_messge), encoding='utf-8'))
                        continue
                    elif user_obj.login(client_user,client_passwd) == 1:
                        #print("密码错误")
                        respone_messge['content'] = '登入失败'
                        conn.sendall(bytes(json.dumps(respone_messge), encoding='utf-8'))
                        continue

                #执行命令功能
                elif client_dict["header"] == "remote_command":
                    #执行客户端发送过来的命令，并存储在字典中
                    #recv_data = conn.recv(1024)
                    client_json = str(recv_data, encoding='utf-8')
                    client_dict = json.loads(client_json)
                    temp_command = exec_command(client_dict)
                    #respone_messge['content'] = temp_command

                    # 给客户端回复消息头，告诉客户端要发送命令结果给它了
                    respone_messge['header'] = 'respone_command'
                    respone_messge_str = json.dumps(respone_messge)
                    conn.sendall(bytes(respone_messge_str, encoding='utf-8')) #5

                    #接受客户端消息头，检查是否"recive"状态，然后发送数据
                    recv_data = conn.recv(1024)
                    client_json = str(recv_data, encoding='utf-8')
                    client_dict = json.loads(client_json)
                    if client_dict['content'] == 'receive':
                        #把命令结果发送给客户端
                        conn.sendall(bytes(temp_command, encoding='utf-8'))
                        #在发送一条消息告诉客户端，已经发送完毕
                        conn.sendall(bytes('command_stop', encoding='utf-8'))
                        continue

                # 聊天功能
                elif client_dict["header"] == "send_chatbot":
                    # 接收客户端发送过来的聊天文本
                    # recv_data = conn.recv(1024)
                    #client_json = str(recv_data, encoding='utf-8')
                    #client_dict = json.loads(client_json)
                    #client_text = client_dict['text']
                    # respone_messge['content'] = temp_command

                    #处理文本，并返回欢迎信息给客户端
                    respone_messge['header'] = 'receive_chatbot'
                    respone_messge['text'] = "\n欢迎登入8888客服平台，请输入您咨询的服务：\n1）查询余额\n2）充值缴费\n3）人工服务\n4）退出服务"
                    respone_messge_str = json.dumps(respone_messge)
                    conn.sendall(bytes(respone_messge_str, encoding='utf-8'))

                    #接收客户端发送的选项信息
                    recv_data = conn.recv(1024)
                    client_json = str(recv_data, encoding='utf-8')
                    client_dict = json.loads(client_json)
                    client_str = client_dict['text'].strip()
                    if client_dict['header'] == "receive_text":
                        if client_str == "1":
                            respone_messge['text'] = "余额为0，穷鬼，赶紧走吧！"
                        elif client_str == "2":
                            respone_messge['text'] = "你辣么穷，还是留着钱吃饭吧！！！"
                        elif client_str == "3":
                            respone_messge['text'] = "客服已下班，明天再来吧。。。"
                        elif client_str == "4":
                            continue
                        respone_messge_str = json.dumps(respone_messge)
                        conn.sendall(bytes(respone_messge_str, encoding='utf-8'))
                        continue

                # FTP功能
                elif client_dict["header"] == "send_file":
                    ObjFtp = FtpServer(conn)
                    dt = ObjFtp.recv_write()
                    ObjFtp.rename(dt)
                    ObjFtp.sendreport(dt)

class User:
    def __init__(self):
        '''
        设置初始化函数变量：用户名，密码，初始化用户字典
        '''
        self.Name = None
        self.Passwd = None
        self.UserInfo = {}

    def initialize(self):
        '''
        初始化环境
        创建一个空的字典文件，用于存储用户和密码
        :return:
        '''
        with open('user.db','w') as f:
            json.dump(self.UserInfo,f)

    def regist(self):
        '''
        用户注册;
        1.读取字典，判断用户输入的用户名是否在字典的key中。
        2.如果用户输入的key在字典中,则存储用户注册的信息{"用户名":"hash过后的密码值"}
        :return:
        '''
        self.Name = input("请输入用户名:")
        tmp_passwd = getpass.getpass("请输入密码：")
        print(tmp_passwd)

        self.Passwd = self.has(tmp_passwd)
        with open("user.db",'r') as f:
            # a  =(f.read())
            # print(type(json.loads(a)))
            self.UserInfo = json.loads(f.read())
            # print(self.UserInfo)
            # print(type(self.UserInfo))

        if self.Name in self.UserInfo:
            print("已经有此用户")
        else:
            self.UserInfo[self.Name] = self.Passwd
            print(self.UserInfo)
            with open('user.db','w') as f:
                json.dump(self.UserInfo,f)
                print("注册成功")

    def login(self,name,passwd):
        '''
        调用has方法讲密码hash处理，并返回值,对比用户输入的值和字典存储的值是否一致
        :return:
        '''
        # self.Name = input("请输入用户名:")
        # self.Passwd = getpass.getpass("请输入密码：")

        self.Name = name
        self.Passwd = passwd
        with open("user.db",'r') as f:
            temp_dict = json.loads(f.read())
        if self.Name in temp_dict:
            temp_passwd = temp_dict[self.Name]
            if temp_dict[self.Name] == self.has(self.Passwd):
                #print("登入成功")
                return 0
        else:
            #print("没有此用户")
            return 1


    def has(self,passwd):
        '''
        处理用户的密码.
        将密码转换为hash值
        :param passwd:
        :return:
        '''
        has_obj = hashlib.md5(bytes("user_defined_passwd",encoding="utf-8"))
        has_obj.update(bytes(passwd,encoding='utf-8'))
        has_passwd = has_obj.hexdigest()
        return has_passwd


def exec_command(client_dict):
    client_command = client_dict['command']
    print(client_command)
    #temp_command = subprocess.call(client_command,shell=True)
    temp_command = subprocess.getstatusoutput(client_command)
    if temp_command[0] == 0:
        return temp_command[1]
    else:
        return "命令不存在"


class FtpServer:
    def __init__(self,conn):
        self.Conn = conn
    def recv_write(self):
        # 返回一个包给客户端（解决粘包）
        self.Conn.sendall(bytes("send_respone_Hander", encoding='utf-8'))
        # 接收
        file_size = 0
        dict_bytes = self.Conn.recv(1024)
        dict_str = str(dict_bytes, encoding='utf-8')
        dt = json.loads(dict_str)
        file_size = int(dt['size'])
        #print(dt)
        self.Conn.sendall(bytes("send_respone_FileInfo", encoding='utf-8'))

        # 写入文件
        with open("temp_file", 'wb') as f:
            while file_size >=0:
                ret_bytes = self.Conn.recv(1024)
                # 把bytes转换成字符串
                ret_str = str(ret_bytes)
                # 每次接收1024字节，接收完毕退出
                f.write(ret_bytes)
                file_size -= 1024
                #print(type(file_size),file_size)
                #print(ret_str)
            #print("接收完毕")
        return dt

    def rename(self,dt):
        # 重新修改文件名
        file_rename = dt['name']
        if os.path.exists(file_rename):
            os.remove(file_rename)
        os.rename("temp_file", file_rename)
        print("\n文件：%s\t已完成接收"%file_rename)
        return dt

    def hash(self,dt):
        # hash验证
        has = hashlib.md5()
        file_rename = dt['name']
        with open(file_rename, 'rb') as f:
            has = hashlib.md5()
            has.update(f.read())
            hash_value = has.hexdigest()
        #print("dt:%s,lt:%s" % (dt['hash'], hash_value))
        return hash_value

    def sendreport(self,dt):
        hash_value = self.hash(dt)
        file_name = dt['name']
        # 告诉客户端接收完毕
        if dt['hash'] == hash_value:
            self.Conn.sendall(bytes("\n文件：%s \t传输完毕\n" % file_name, encoding='utf-8'))
        else:
            self.Conn.sendall(bytes("\n文件：%s \t传输失败\n" % file_name, encoding='utf-8'))




if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('127.0.0.1',8888),MyServer)
    server.serve_forever()

    user_obj = User()

    #obj.initialize()
    #obj.regist()
    #obj.login()