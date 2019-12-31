# -*- coding: UTF-8 -*-
#11710418 唐润哲

import os
import urllib.parse as up
import html

def join(array):
    return ''.join(array)

class Http_Lab(object):
    def __init__(self, path):
        self.head = ['HTTP/1.0 200 OK\r\n', 'Connection: close\r\n',
                     'Content-Type:text/html; charset=utf-8\r\n','\r\n']
        self.body_default = ['</pre>\r\n ', '<hr> \r\n','\r\n']
        self.body = ['<!DOCTYPE html>\r\n','<html>\r\n','<head><title>Index of {}</title></head>\r\n',
                     '<body bgcolor="white"> \r\n','<h1>Index of {}</h1><hr>\r\n ','<pre>\r\n']
        self.body[2] = self.body[2].format(path)
        self.body[4] = self.body[4].format(path)
        self.file = []
        self.message = ''
        self.dir = []
        self.error = ['<!DOCTYPE html>\r\n', "<html>\r\n<body>{} {}<body>\r\n</html>\r\n"]
        self.path = path

    def get_file(self, name_of_file):
        try:
            file = open(name_of_file, mode='rb')
        except FileNotFoundError:
            return b'File Not Found'
        result = file.read()
        file.close()
        return result

    def fill_dir(self, names):
        text1="<a href=\"{}\">{}</a><br\r\n>"
        for i in names:
            format1 = text1.format(up.quote(i), html.escape(i))
            format2 = text1.format(up.quote(i + '/'), html.escape(i + '/'))
            if os.path.isfile(i):
                self.file.append(format1)
            elif os.path.isdir(i):
                self.dir.append(format2)

    def set_headmessage(self, code, message):
        self.head[0] = 'HTTP/1.0 {} {}\r\n'.format(code, message)

    def set_error_message(self, code):
        if code == 404:
            message = "Not Found"
        elif code == 405:
            message = "Method Not Allowed"
        self.error[1] = self.error[1].format(code, message)
        self.set_headmessage(code, message)

    def set_headers(self, name, value):
        for i in range(len(self.head)):
            split1=self.head[i].split(':')[0]
            count1=self.head[i].count(':')
            if split1 == name and count1 > 0:
                self.head[i] = name + ': ' + value + '\r\n'
                return
        self.head.insert(-1, name + ': ' + value + '\r\n')

    def get_head(self):
        return (join(self.head)).encode()

    def get_body(self):
        if self.message == '':
            return (join(self.body) + join(self.dir) + join(self.file) + join(self.body_default)).encode()
        else:
            return ((join(self.body) + join(self.dir) + join(self.file)).encode() + self.message + join(self.body_default).encode())

    def get_error(self):
        return join(self.error).encode()

    def get_response_error(self):
        return self.get_head() + self.get_error()

    def get_response(self):
        return self.get_head() + self.get_body()





