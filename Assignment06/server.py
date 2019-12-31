import asyncio
import os
import mimetypes
import urllib
#需要：1.只提供GET和HEAD方法。当收到POST等方法时，返回case405
#!!添加connection:close
#收到一个路径时检测他，使用path拼接法
#A收到一个directory时回复一个页面，包括它第一层的file和directory
#B收到一个file,先检查是不是熟悉的后缀，否则回复一个.*
#C什么都不是就回复case404
#DThe functions should include: browsing directory, jumping, and open files. Editing directory and files are not asked to supported

"新需求：多线程+TCP套接字处理。还要实现range header support(用户可以中断和继续下载文件)。" \
"以及session cookie support"
"存在302和206的新情况"
ok=[
b'HTTP/1.0 200 OK\r\n',
b'Content-Type:text/html; charset=utf-8\r\n',
b'Connection: close\r\n',
b'\r\n'
]
case404=[
b'HTTP/1.0 404 Not Found \r\n',
b'Content-Type:text/html; charset=utf-8\r\n',
b'Connection: close\r\n',
b'\r\n',
b'<html><body>404 Not Found<body></html>\r\n',
b'\r\n'
]
case405=[
b'HTTP/1.0 405 Method Not Allowed \r\n',
b'Content-Type:text/html; charset=utf-8\r\n',
b'Connection: close\r\n',
b'\r\n',
b'<html><body>405 Method Not Allowed<body></html>\r\n',
b'\r\n'
]

index='Index of ./'

async def browser(reader,writer):
	data=b''
	gethead=False
	totaldata=[]
	while True:
		receive = await reader.readline()
		if (gethead == False):
			data = receive
			gethead = True
		totaldata = totaldata + receive.decode().split(' ')
		if receive == b'\r\n' or receive==b'':
			break
	print(totaldata)
	data = data.decode()
	method=data.split(' ')[0]
	url=''
	try:
		i1=0
		i2=0
		for j in range(0,len(data)-1):
			if data[j]==' ':
				i1=j
				break
		for j in range(len(data)-1,0,-1):
			if data[j]==' ':
				i2=j
				break
		url=data[i1+1:i2]
	except IndexError:
		pass
	#############################
	if method!="GET" and method!="HEAD":
		writer.writelines(case405)
		await writer.drain()
		writer.close()
	else:
		try:
			doturl=urllib.parse.unquote('.'+url)
			flag=True
			"在这里加入判断cookie的部分"
			if 'Cookie:' in totaldata:
				cookiedoturl=totaldata[totaldata.index('Cookie:')+1].replace("\r\n","").replace(";","")
				newurl = 'http://localhost:8080' + cookiedoturl[1:]
				if cookiedoturl!="./" and doturl=="./" and method=="GET":
					writer.writelines([
						b'HTTP/1.1 302 Found\r\n',
						bytes('Location: ' +  newurl+ '\r\n', 'utf-8'),
						b'Content-Type:text/html; charset=utf-8\r\n',
						b'Connection: close\r\n',
						b'\r\n'
					])
					flag=False
					writer.close()


			if os.path.isfile(doturl)==False and flag==True:
				#"如果不是file而是directory"
				#print(os.listdir(doturl))
				href=''
				dd=''
				if url.split("/")[1]!="":
					href+=('<a href=\"'+os.path.dirname(url)+'\">../</a><br>')
					dd='/'
				for choice in os.listdir(doturl):
					choice=urllib.parse.quote(choice)
					href+=('<a href=\"'+(url+dd+choice)+'\">'+(choice)+'/</a><br>')
				"遇到了很严重的状况，关于byte和str,先拼str再转码"
				"path一定要设置！"
				startget=[
					b'HTTP/1.0 200 OK\r\n',
					b'Content-Type:text/html; charset=utf-8\r\n',
					bytes('Set-Cookie: ' + doturl + '; Path=/;\r\n', 'utf-8'),
					b'Connection: close\r\n',
					b'\r\n'
					b'<html><head><title>'+(index+url).encode('utf-8')+b'</title></head>\r\n',
					b'<body bgcolor="white">\r\n',
					b'<h1>\r\n',
					(index+url).encode('utf-8'),
					b'</h1><hr>\r\n',
					b'<pre>\r\n',
					##这里是各种超链接
					href.encode('utf-8'),
					b'</pre>\r\n',
					b'<hr>\r\n',
					b'</body></html>\r\n'
				]
				starthead=[
					b'HTTP/1.0 200 OK\r\n',
					b'Content-Type:text/html; charset=utf-8\r\n',
					bytes('Set-Cookie: ' + doturl + '\r\n', 'utf-8'),#完成对于dir-head的cookie
					b'Connection: close\r\n',
					b'\r\n'
				]
				if method == "HEAD":
					writer.writelines(starthead)
				else:
					#没有处理cookie-dir的部分
					writer.writelines(startget)
			elif os.path.isfile(doturl)==True and flag==True:
				"如果是file,需要读出来吗？"
				thisfile= open(doturl,'rb')
				thiscontentlength=str(os.path.getsize(doturl))#需要./吗，不需要
				decidetype=''

				if mimetypes.guess_type(url)[0] is not None:
					decidetype+=('Content-Type:'+mimetypes.guess_type(doturl)[0]+'; charset=utf-8\r\n')
				else:
					decidetype+=('Content-Type:application/octet-stream; charset=utf-8\r\n')
				#这个是head方法，添加cookie保持不变即可
				starthead=[
					b'HTTP/1.0 200 OK\r\n',
					decidetype.encode('utf-8'),
					b'Content-Length:' + thiscontentlength.encode('utf-8'),
					b'\r\n',
					b'Connection: close\r\n'
					b'\r\n'
				]
				#这个是get方法，read时要先转换成二进制
				startget=[
					b'HTTP/1.0 200 OK\r\n',
					decidetype.encode('utf-8'),
					b'Content-Length:' + thiscontentlength.encode('utf-8'),
					b'\r\n',
					b'Connection: close\r\n',
					b'\r\n',
					thisfile.read()
					]
				if method == "HEAD":
					writer.writelines(starthead)
				else:
					"在这里加入处理端点传输的部分"
					if 'Range:' in totaldata:
						print('!')
						rangemessage=totaldata[totaldata.index('Range:')+1].strip().replace('bytes=','')
						startid,endid=rangemessage.split('-')
						if startid=='':startid=(int)(thiscontentlength)-(int)(endid)
						elif endid=='':endid=(int)(thiscontentlength)-1
						startid=int(startid)
						endid=int(endid)
						thisfile.seek(startid)
						startidstr=str(startid)
						endidstr=str(endid)
						thiscontentlengthstr=str(thiscontentlength)
						writer.writelines([
						b'HTTP/1.1 206 Partial Content\r\n',
						decidetype.encode('utf-8'),
						b'Accept-Ranges: bytes\r\n',
						bytes('Content-Range: ' + 'bytes '+startidstr+'-'+endidstr+'/'+thiscontentlengthstr+'\r\n' , 'utf-8'),
						b'Connection: keep-alive\r\n',
						b'\r\n',
						thisfile.read(endid-startid+1)
					])

					else:
						writer.writelines(startget)

		#如果什么都没有，就抛出404
		except FileNotFoundError:
			writer.writelines(case404)
		writer.close()






if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	coro = asyncio.start_server(browser, '127.0.0.1', 8080, loop=loop)#定义地址和端口
	server = loop.run_until_complete(coro)#在循环中不断执行操作
	# Serve requests until Ctrl+C is pressed
	print('Serving on {}'.format(server.sockets[0].getsockname()))
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass
	# Close the server
	server.close()
	loop.run_until_complete(server.wait_closed())
	loop.close()