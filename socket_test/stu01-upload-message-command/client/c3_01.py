#/usr/bin/python env
#coding:utf8
import socket
import getpass
import json
import os,time
import hashlib



def init():
    # #接收服务器返回验证信息
    while True:
        func_obj = ChooseFunc()
        func_obj.login()
    #sk.close()

def login_system(user,passwd):
    '''
    1.初始化用户名和密码信息，返回json字典
    :return:
    '''
    user_dict = {'header':'login','user':user,'passwd':passwd}
    user_json = json.dumps(user_dict)
    return  user_json



class ChooseFunc:
    ip_port = ('127.0.0.1', 8888)
    def __init__(self):
        self.Sk = socket.socket()
        self.Connect = self.Sk.connect(ChooseFunc.ip_port)
        # sk.settimeout(5)
    def login(self):
        #欢迎消息
        data = self.Sk.recv(1024)  # 2
        print(str(data,encoding='utf-8'))

        while True:
            # 验证用户名和密码是否正确
            inp_user = input('请输入用户名：')
            # inp_passwd = getpass.getpass("请输入密码：") #only just can use on commmand line
            inp_passwd = input("请输入密码：")
            user_dict = login_system(inp_user, inp_passwd)
            self.Sk.sendall(bytes(user_dict, encoding='utf-8'))  # 3
            # 接收服务器返回验证信息
            data = self.Sk.recv(1024)  # 6
            client_json = str(data, encoding='utf-8')
            client_dict = json.loads(client_json)
            #print(type(client_dict),client_dict) #print server send messge
            if client_dict['header'] == 'login':
                if client_dict['content'] == "登入成功":
                    #打印登入成功的消息
                    print("恭喜您，登入成功！\n")

                    # 让用户选择功能（执行命令，聊天，发送文件）
                    while True:
                        user_input = int(input("请选择你需要的功能：\n1 )远程执行命令\n2 )机器人聊天\n3 )发送文件"))
                        if user_input == 1:
                            if self.send_command() =='quit':
                                continue
                        elif user_input == 2:
                            if self.send_chatbot() == 'quit':
                                continue
                        elif user_input == 3:
                            if self.send_files() == 'quit':
                                continue
                else:
                    print("\n登入失败\n")
                    continue
    def send_command(self):
        while True:
            linux_command = input("请输入命令：")
            if linux_command == 'quit':
                return 'quit'
            user_dict = {'header': 'remote_command', 'command': linux_command}
            user_json = json.dumps(user_dict)
            self.Sk.sendall(bytes(user_json,encoding='utf-8'))

            data = self.Sk.recv(1024)  # 6
            s_json = str(data, encoding='utf-8')
            c_dict = json.loads(s_json)
            if c_dict['header'] == 'respone_command':
                c_dict['content'] = 'receive'
                self.Sk.sendall(bytes(json.dumps(c_dict), encoding='utf-8'))
                server_data = b''
                while True:
                    server_bytes =self.Sk.recv(1024)
                    server_data += server_bytes
                    #print(str(server_data)[-13:-1])
                    if str(server_data)[-13:-1] == "command_stop":
                        break
                str_server_respone = str(server_data,encoding='utf-8')
                print(str_server_respone.replace('command_stop',''))

    def send_chatbot(self):
        while True:
            #发送header头部，告诉服务器需要进入聊天功能
            #user_dict = {'header': 'send_chatbot', 'text': text_input}
            user_dict = {'header': 'send_chatbot'}
            user_json = json.dumps(user_dict)
            self.Sk.sendall(bytes(user_json, encoding='utf-8'))

            # 接收服务端发来的欢迎消息
            data = self.Sk.recv(1024)  # 6
            s_json = str(data, encoding='utf-8')
            c_dict = json.loads(s_json)
            if c_dict['header'] == 'receive_chatbot':
                print(c_dict['text'])

            #把用户输入的功能序号发送给服务端
            user_dict = {'header': 'receive_text'}
            text_input = input("\n请选择服务\t退出请输入[quit]：").strip()
            if text_input == 'quit':
                return 'quit'
            elif text_input == '1':
                user_dict['text'] = '1'
            elif text_input == '2':
                user_dict['text'] = '2'
            elif text_input == '3':
                user_dict['text'] = '3'
            elif text_input == '4':
                user_dict['text'] = '4'
                user_json = json.dumps(user_dict)
                self.Sk.sendall(bytes(user_json, encoding='utf-8'))
                return 'quit'
            user_json = json.dumps(user_dict)
            self.Sk.sendall(bytes(user_json, encoding='utf-8'))

            #接收服务端返回的消息结果
            data = self.Sk.recv(1024)  # 6
            s_json = str(data, encoding='utf-8')
            c_dict = json.loads(s_json)
            print(c_dict['text'])
            time.sleep(2)

    def send_files(self):
        Ftp_obj = FtpClient(self.Sk)
        while True:
            file_name, file_size = Ftp_obj.file_info()
            if file_name == 'quit':
                return 'quit'
            Ftp_obj.send_hander()
            file_info = Ftp_obj.hash(file_name, file_size)
            Ftp_obj.send_file(file_info, file_name, file_size)
            Ftp_obj.recv_response()


class FtpClient:
    def __init__(self,sk):
        self.ObjSk = sk
    def file_info(self):
        # 选择文件
        for n in os.listdir():
            if os.path.isfile(n):
                file_size = os.path.getsize(n)
                print("%s \t%s" % (n, file_size))
        # 获取文件大小
        file_name = input("Please choose file: [quit pls input 'quit']")
        if file_name == 'quit':
            return 'quit',0
        file_size = os.path.getsize(file_name)
        return file_name, file_size

    def hash(self,file_name, file_size):
        # 获取文件hash值
        has = hashlib.md5()
        with open(file_name, 'rb') as f:
            has = hashlib.md5()
            has.update(f.read())
            m = has.hexdigest()
        #print(m)
        file_info = {"name": file_name, "size": file_size, "hash": m}
        return file_info

    def send_hander(self):
        #发送header给服务端，告诉服务端进入ftp功能
        user_dict = {'header': 'send_file'}
        user_json = json.dumps(user_dict)
        self.ObjSk.sendall(bytes(user_json, encoding='utf-8'))
        #服务端接收hader后，在返回一个消息（用于解决粘包问题）
        client_bytes = self.ObjSk.recv(1024)
        client_str = str(client_bytes, encoding='utf-8')
        print(client_str)

    def send_file(self,file_info, file_name, files_size):
        # 发送文件大小信息
        file_info_str = json.dumps(file_info)
        self.ObjSk.sendall(bytes(file_info_str, encoding='utf-8'))
        #服务端接收文件大小消息后，在返回一个消息（用于解决粘包问题）
        client_bytes = self.ObjSk.recv(1024)
        client_str = str(client_bytes, encoding='utf-8')
        print(client_str)
        # obj.recv(1024)
        # 读取发送的文件
        # with open(file_name,'r',encoding='utf-8') as f:
        file_size = int(files_size)
        with open(file_name, 'rb') as f:
            total_size = file_size
            while file_size >=0:
                block = f.read(1024)
                self.ObjSk.sendall(bytes(block))
                file_size -= 1024
                # 统计发送百分比
                tmp_num = (file_size / total_size) * 100
                if tmp_num<=0:
                    break
                print("剩余：%.3f%%" % tmp_num)
            print("发送完成")

    def recv_response(self):
        # 接收服务端，最后的验证字段
        ret_bytes = self.ObjSk.recv(1024)
        ret_str = str(ret_bytes, encoding='utf-8')
        print(ret_str)
        # 关闭客户端
        #self.ObjSk.close()

class FtpClientAgain:
    def __init__(self,sk):
        self.ObjSk = sk

    def send_hander(self):
        #发送header给服务端，告诉服务端进入ftp功能
        user_dict = {'header': 'send_file_again'}
        user_json = json.dumps(user_dict)
        self.ObjSk.sendall(bytes(user_json, encoding='utf-8'))
        #服务端接收hader后，在返回一个消息（用于解决粘包问题）
        client_bytes = self.ObjSk.recv(1024)
        client_str = str(client_bytes, encoding='utf-8')
        print(client_str)

    def file_info(self):
        # 选择文件
        for n in os.listdir():
            if os.path.isfile(n):
                file_size = os.path.getsize(n)
                print("%s \t%s" % (n, file_size))
        # 获取文件大小
        file_name = input("Please choose file: [quit pls input 'quit']")
        if file_name == 'quit':
            return 'quit',0
        file_size = os.path.getsize(file_name)
        return file_name, file_size

    def hash(self,file_name, file_size):
        # 获取文件hash值
        has = hashlib.md5()
        with open(file_name, 'rb') as f:
            has = hashlib.md5()
            has.update(f.read())
            m = has.hexdigest()
        #print(m)
        file_info = {"name": file_name, "size": file_size, "hash": m}
        return file_info

    def send_file(self,file_info, file_name, files_size):
        # 发送文件大小信息
        file_info_str = json.dumps(file_info)
        self.ObjSk.sendall(bytes(file_info_str, encoding='utf-8'))
        #服务端接收文件大小消息后，在返回一个消息（用于解决粘包问题）
        client_bytes = self.ObjSk.recv(1024)
        client_str = str(client_bytes, encoding='utf-8')
        print(client_str)
        # obj.recv(1024)
        # 读取发送的文件
        # with open(file_name,'r',encoding='utf-8') as f:
        file_size = int(files_size)
        with open(file_name, 'rb') as f:
            total_size = file_size
            while file_size >=0:
                block = f.read(1024)
                self.ObjSk.sendall(bytes(block))
                file_size -= 1024
                # 统计发送百分比
                tmp_num = (file_size / total_size) * 100
                if tmp_num<=0:
                    break
                print("剩余：%.3f%%" % tmp_num)
            print("发送完成")

    def recv_response(self):
        # 接收服务端，最后的验证字段
        ret_bytes = self.ObjSk.recv(1024)
        ret_str = str(ret_bytes, encoding='utf-8')
        print(ret_str)
        # 关闭客户端
        #self.ObjSk.close()


if __name__ == '__main__':
    init()


