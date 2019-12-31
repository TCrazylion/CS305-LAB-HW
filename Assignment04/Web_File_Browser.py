# -*- coding: UTF-8 -*-
#11710418 唐润哲

import asyncio
import mimetypes
import urllib.parse as up
from Http_Lab import *

def open_file(rp,path): #判断文件类型并打开or下载文件
    extension = path[0:-1]
    file_type = 'application/octet-stream' #default
    get_type = mimetypes.guess_type(extension)[0]
    if get_type is None:
        rp.set_headers('Accept-Ranges', 'bytes')
    else:
        file_type = get_type
    rp.body = []
    rp.set_headers('Content-Type', file_type)
    rp.set_headers('Content-Length', str(os.path.getsize(extension)))
    rp.message = rp.get_file(extension)

def ls(return_path):#列出目录内容
    insides = os.listdir()
    return_path.fill_dir(insides)
    text2 = "<a href=\"{}\">{}</a><br\r\n>"
    return_path.dir.insert(0, text2.format('../', "../"))#上级目录

async def cd(reader, writer):
    input = await reader.read(0xffffffff)
    message = input.decode().split('\r\n')
    messages = message[0].split(' ') #去掉空格
    method = up.unquote(messages[0])#访问方法
    path = up.unquote(messages[1])
    if path[-1] != '/':
        path += '/'
    path = '.' + path
    return_path = Http_Lab(path)#文件路径
    error = False

    if method not in('GET','HEAD'):
        return_path.set_error_message(405)
        error = True
    else:
        if path == './':  # 根目录
            ls(return_path)
        elif os.path.isdir(path):  # 子目录
            os.chdir(path)
            ls(return_path)
            os.chdir(os.path.dirname(__file__))
        elif os.path.isfile(path[0:-1]):  # 文件
            open_file(return_path,path)
        else:
            error = True
            return_path.set_error_message(404)

    if  error != True: #根据error报告决定返回
        if method == 'HEAD':
            writer.write(return_path.get_head())
        elif method == 'GET':
            writer.write(return_path.get_response())
    else:
        writer.write(return_path.get_response_error())

    await writer.drain()
    writer.close()

def echo():
    loop = asyncio.get_event_loop()
    server_inital = asyncio.start_server(cd, '127.0.0.1', 9942, )
    server = loop.run_until_complete(server_inital)
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

if __name__ == "__main__":
    try:
        echo()
    except KeyboardInterrupt:
        exit(1)