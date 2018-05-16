#/usr/bin/python env
#coding:utf8
import socket
import os
import json

class FtpUpload:
    def __init__(self):
        ip_port = ('127.0.0.1', 8000)
        self.sk = socket.socket()
        self.sk.connect(ip_port)

    def sys_messge(self):
        #欢迎信息
        data_bytes = self.sk.recv(1024)
        print(str(data_bytes, encoding='utf-8'))

    def user_login(self):
        #输入用户密码
        user = input("Username：")
        passwd = input("Password：")
        self.sk.sendall(bytes(user,encoding='utf-8'))
        data_bytes = self.sk.recv(1024)
        #print(str(data_bytes,encoding='utf-8'))
        # 发送用户信息
        self.sk.sendall(bytes(passwd, encoding='utf-8'))
        #接收验证信息
        data_bytes = self.sk.recv(1024)
        data_verify_str = str(data_bytes,encoding='utf-8')
        if data_verify_str == "登入成功":
            return True
        else:
            return False

    def upload_files(self,file_name):
        # for n in os.listdir():
        #     if n in file_path:
        # file_path = os.path.relpath(file_name)
        def getallfiles(path):
            alldir = []
            allfile = []
            for dirpath, dirname, filename in os.walk(path):
                for dir in dirname:
                    # allfile.append(os.path.join(dirpath,dir))
                    alldir.append(os.path.join(dirpath, dir))
                for name in filename:
                    allfile.append(os.path.join(dirpath, name))
            return allfile, alldir

        def one_send_file(file_name):
            # 但文件发送
            file_size_str = os.path.getsize(file_name)
            file_size_int = int(file_size_str)
            allfile_json = json.dumps(list(""))
            # 类型|大小|文件名|文件路径
            self.sk.sendall(bytes("file|%s|%s|no|%s" % (file_size_int, file_name,allfile_json), encoding='utf-8'))
            # 接收服务端通知，告诉自己要开始发送文件
            data = self.sk.recv(1024)
            data_str = str(data, encoding='utf-8')
            if data_str == "server-respone":
                with open(file_name, 'rb') as f:
                    while file_size_int >0:
                        #print(file_size_int)
                        f_data = f.read(1024)
                        self.sk.sendall(bytes(f_data))
                        file_size_int -= 1024
                # 发送完成接收返回消息
                data_byte = self.sk.recv(1024)
                data_str = str(data_byte, encoding='utf-8')
                print(data_str)

        def send_file(allfile, alldir):
            print(allfile)
            # 循环列表依次发送
            for file_path in allfile:
                file_size_str = os.path.getsize(file_path)
                file_size_int = int(file_size_str)
                allfile_json = json.dumps(list(""))
                # 类型|大小|文件名|文件路径
                self.sk.sendall(bytes("file|%s|%s|yes|%s" % (file_size_int, file_path,allfile_json), encoding='utf-8'))
                # 接收服务端通知，告诉自己要开始发送文件
                data = self.sk.recv(1024)
                data_str = str(data, encoding='utf-8')
                if data_str == "server-respone":
                    # 依次打开文件发送
                    print(file_path)
                    with open(file_path, 'rb') as f:
                        while file_size_int >0:
                            f_data = f.read(1024)
                            self.sk.sendall(bytes(f_data))
                            file_size_int -= 1024
                    # 发送完成接收返回消息
                    data_byte = self.sk.recv(1024)
                    data_str = str(data_byte, encoding='utf-8')
                    print(data_str)

        def send_dir(allfile, alldir):
            # 发送文件夹名，告诉服务端创建它
            # 类型|大小|文件夹名|所有文件夹路径
            alldir_json = json.dumps(alldir)
            self.sk.sendall(bytes("dir|%s|%s|null|%s" % (0, file_name, alldir_json), encoding='utf-8'))
            self.sk.recv(1024)

        # 如果是文件夹，获取该文件的所有目录结构
        allfile, alldir = getallfiles(file_name)
        if os.path.isfile(file_name):
            one_send_file(file_name)
        elif os.path.isdir(file_name):
            send_dir(allfile, alldir)
            send_file(allfile, alldir)

    def choose_files(self):
        while True:
            temp_str = input("请选择操作：[help 帮助]")
            command = temp_str.split()
            if command[0].strip() == "help":
                print("返回上一层目录请输入[cd ..]\n查看当前目录[ls]\n进入当前目录[cd 目录]\n上传目录和文件[put 目录名称]\n查看远程目录[lls]\n下载远程文件和目录[wget 文件名]")
            elif command[0].strip() == "cd" and command[1].strip() == "..":
                parent_dir = os.path.dirname(os.getcwd())
                os.chdir(parent_dir)
                print(os.getcwd())
            elif command[0].strip() == "ls":
                self.ls_command()
            elif command[0].strip() == "cd" and command[1].strip() != '':
                print("cd %s"%command[1])
                if os.path.isdir(command[1]):
                    os.chdir(command[1])
                else:
                    print("%s 不是目录"%command[1])
                    continue
            elif command[0].strip() == "put" and command[1].strip() != '':
                #print("1111111", command[1])
                #file_path = os.getcwd(command[1])
                file_path = os.path.relpath(command[1])
                self.upload_files(file_path)
            elif command[0].strip() == "lls":
                print("查看远程目录")
            elif command[0].strip() == "wget" and command[1].strip() != '':
                print("下载远程文件到本地")
            else:
                print("输入错误")

    def ls_command(self):
        file_list = []
        d_file_list = []
        for n in os.listdir():
            if os.path.isfile(n):
                file_list.append(n)
            if os.path.isdir(n):
                d_file_list.append(n)
        file_list += d_file_list
        for n in file_list:
            if os.path.isfile(n):
                print("文件：%s" % n)
            if os.path.isdir(n):
                print("目录：%s" % n)

def start():
    c_obj = FtpUpload()
    c_obj.sys_messge()
    while True:
        if c_obj.user_login():
            c_obj.choose_files()
            print("登入成功")
            break
        else:
            print("登入失败")
            continue


if __name__ == '__main__':
    start()