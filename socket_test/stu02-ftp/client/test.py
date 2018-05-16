#/usr/bin/python env
#coding:utf8

import os

# def getallfiles(path):
#     alldir = []
#     allfile = []
#     for dirpath,dirname,filename in os.walk(path):
#         for dir in dirname:
#             #allfile.append(os.path.join(dirpath,dir))
#             alldir.append(os.path.join(dirpath,dir))
#         for name in filename:
#             allfile.append(os.path.join(dirpath,name))
#     return  allfile,alldir
#
# if __name__ == '__main__':
#     allfile,alldir = getallfiles('test')
#     # for file in allfile:
#     #     print(file)
#
#     # for dir in alldir:
#     #     print(dir)
#     # print(alldir)
#     if not allfile:
#         print("it is null")
#     else:
#         print(allfile)

file_size = os.path.getsize('Qt5Widgets.dll')
file_size_int = int(file_size)
with open('Qt5Widgets.dll','rb') as f:
    while file_size_int >0:
        print(file_size_int)
        print(f.read(1024))
        file_size_int -= 1024
print("Finished")