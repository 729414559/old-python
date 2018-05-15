# #/usr/bin/python env
# #coding:utf8
#
# '''
# 服务端需要启用两个端口来监听。
# 当不使用多路复用，只能采用如下方法实现。（如下方法其实还有问题，因为当客户端recv文件时，不知道是哪个服务端实例发送过来的数据）
# 这时，就可以采用多路复用，给每个I/O（文件描述符）都打一个标记。
# '''
# import socket
#
# sk1 = socket.socket
# sk1.bind('127.0.0.1',8001)
# sk1.listen()
#
# while True:
#     conn, address = sk1.accept()
#     while True:
#         content_bytes = conn.recv(1024)
#         content_str = str(content_bytes,encoding='utf-8')
#         conn.sendall(bytes(content_str + "\t回复内容",encoding='utf-8'))
#     conn.close()
#
#
# sk2 = socket.socket
# sk2.bind('127.0.0.1',8002)
# sk2.listen()
#
# while True:
#     conn, address = sk2.accept()
#     while True:
#         content_bytes = conn.recv(1024)
#         content_str = str(content_bytes,encoding='utf-8')
#         conn.sendall(bytes(content_str + "\t回复内容",encoding='utf-8'))
#     conn.close()






# '''
# 多路复用方式实现
#
# readable_list, writeable_list, error_list = select.select(inputs, [], inputs,1)
#
# 句柄列表11, 句柄列表22, 句柄列表33 = select.select(句柄序列1, 句柄序列2, 句柄序列3, 超时时间)
# 参数： 可接受四个参数（前三个必须）
# 返回值：三个列表
# select方法用来监视文件句柄，如果句柄发生变化，则获取该句柄。
# 1、参数1 含有（accetp和read）发生变化时,句柄接收数据，则获取发生变化的句柄并添加到 返回值1 序列中
# 2、参数2 含有发送数据句柄时，则将该序列中所有的句柄添加到 返回值2
# 3、参数3 序列中的句柄发生错误时，则将该发生错误的句柄添加到 返回值3 序列中
# 4、超时时间 未设置，则select会一直阻塞，直到监听的句柄发生变化
#    超时时间 ＝ 1时，那么如果监听的句柄均无任何变化，则select会阻塞 1 秒，之后返回三个空列表，如果监听的句柄有变化，则直接执行。
# '''
#
# import socket
# import select
#
# #创建socke对象
# sk1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sk1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sk1.bind(('127.0.0.1',8001))
# sk1.listen(5)
#
# sk2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sk2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sk2.bind(('127.0.0.1',8002))
# sk2.listen(5)
#
# #把socke对象放入列表中
# sk_list = [sk1,sk2,]
#
# # 利用select，监听socket对象变化
# while True:
#     '''
#     r_list 获取指外部发过来的数据对象信息，序列中的句柄发生可读时（accetp和read），则获取发生变化的句柄并添加到 返回值1 序列中
#     w_list第2个是监控和接收所有要发出去的data(outgoing data)
#     err_list 第3个监控错误信息
#     1 第4个是超时时间，未设置，则select会一直阻塞，直到监听的句柄发生变化，1时，
#     那么如果监听的句柄均无任何变化，则select会阻塞 1 秒，之后返回三个空列表，如果监听的句柄有变化，则直接执行。
#     '''
#     r_list, w_list, err_list = select.select(sk_list, [], sk_list, 1) # 当监控句柄变化时r_list列表会更新
#
#     for sk in r_list:
#         # 循环r_list，判断值，是否sk_list列表中某个socket对象值，如果是，就判定该值为socket对象。然后初始化该对象的连接信息，然后在把该对象的连接信息存到sk_list的列表中
#         if sk == sk1 or sk == sk2:
#             conn, address = sk.accept()
#             sk_list.append(conn)
#             print(conn)
#         # 如果判定不是一个socket对象（循环的值，不在sk_list列表中），那么它就是一个成功建立连接的用户，可以直接收发信息
#         else:
#             try:
#                 received = sk.recv(1024)
#                 print(str(received,encoding='utf-8'))
#                 sk.sendall(bytes("服务端回复：\n",encoding='utf-8'))
#             except Exception as ex:
#                 #如果监控到异常（例如客户端断开连接）则把该连接从成功建立连接的列表中移除，下次不在循环它
#                 sk_list.remove(sk)




# '''
# I/O多路复用，读写分离
# '''
# import socket
# import select
# import time
#
# #创建socke对象
# sk1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sk1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sk1.bind(('127.0.0.1',8001))
# sk1.listen(5)
#
# #定义两个队列:1 Scoket对象队列， 2 发送数据队列
# input_list = [sk1,]
# output_list = []
# #定义一个字典，存储socket对象的连接和收到的值
# message_data = {}
#
# while True:
#     #i/o变化后接收，发送，异常，超时
#     r_list, w_list, e_list = select.select(input_list, output_list, input_list,1)
#     # print("r_list：%s" % r_list)
#     # print("w_list：%s"%w_list)
#     # print("e_list：%s" % e_list)
#     # print("\n")
#
#     #读取数据
#     for sk in r_list:
#         if sk == sk1:
#             conn,address = sk.accept()
#             input_list.append(conn)
#             #print(conn)
#             #message_data[sk] = None
#             message_data[sk] = None #把当前连接存入字典，并设定一个空值
#         else:
#             try:    #定义异常捕获，以免客户端断开发生异常
#                 received = sk.recv(1024)
#                 received_str = str(received,encoding='utf-8')
#                 print(received_str)
#                 output_list.append(sk)  #把当前连接存入，即将发送数据的队列
#                 #message_data[sk] = received_str
#                 message_data[sk]=[received_str] #把socket对象连接和接收到的值存储到字典中
#                 print(message_data)
#             except Exception as ex:
#                 pass
#
#     #发送数据
#     for conn in w_list: #循环发送数据队列，获取一个socket连接对象（该队列为output_list的返回值）
#         #data = message_data[conn]
#         data = message_data[conn][0]    #把该对象值取出来
#         del message_data[conn][0]       #删除该连接对象的值（因为已经拿到该值，发送数据后就不需要了）
#         conn.sendall(bytes(data+"\tOK",encoding='utf-8'))   #发送数据给客户端
#         output_list.remove(conn)        #在发送数据队列中，移除该对象
#
#     #发送错误处理
#     for sk in e_list:
#         input_list.remove(sk)   #如果socket对象发生异常则移除该对象





# """
# 此处的Socket服务端相比与原生的Socket，他支持当某一个请求不再发送数据时，服务器端不会等待而是可以去处理其他请求的数据。
# 但是，如果每个请求的耗时比较长时，select版本的服务器端也无法完成同时操作。
# """
#

# import select
# import socket
# import sys
# import queue
#
# # 创建套接字并设置该套接字为非阻塞模式
# server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# server.setblocking(0)
#
# #绑定套接字
# server_address = ('127.0.0.l',8000)
# print(sys.stdin,"starting up on %s port %s"%server_address)
#
# #将该socket变成服务模式
# #backlog等于5，表示内核已经接到了连接请求，但是服务器还没有调用accept进行处理的连接个数为5
# #这个值不能无限大，因为要在内核中维护连接队列
# server.listen(5)
#
# #初始化读取数据的监听列表，最开始时希望从server这个套接字上读取数据
# inputs = [server]
#
# #将初始化写入数据的监听列表，最开始并没有客户端连接进来，所以列表为空
# outputs = []
#
# # 要发往客户端的数据
# message_queues = []
# while inputs:
#     print(sys.stderr, 'waiting for the next event')
#
#     #调用select，监听所有监听列表中的套接字，并将准备好的套接字加入到对应的列表中
#     readable,writable,exceptional = select.select(inputs,outputs,inputs)#列表中的socket 套接字  如果是文件呢？



# import socketserver
# import time
# import threading
#
# def process(x):
#     print(x)
#     time.sleep(1)
#
# # for n in range(10):
# #     process(n)
#
# for n in range(10):
#     t = threading.Thread(target=process,args=(n,))
#     t.start()
import socketserver

class MyServer(socketserver.BaseRequestHandler):

    def handle(self):
        # print self.request,self.client_address,self.server
        conn = self.request
        conn.sendall('欢迎致电 10086，请输入1xxx,0转人工服务.')
        Flag = True
        while Flag:
            data = conn.recv(1024)
            if data == 'exit':
                Flag = False
            elif data == '0':
                conn.sendall('通过可能会被录音.balabala一大推')
            else:
                conn.sendall('请重新输入.')


if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('127.0.0.1',8009),MyServer)
    server.serve_forever()