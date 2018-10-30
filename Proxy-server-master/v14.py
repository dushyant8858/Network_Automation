import socket
import threading
import os
import base64
import sys
import time
import signal
reload(sys)
sys.setdefaultencoding('iso-8859-1')
from thread import *
import hashlib
import datetime
from time import strptime

listen_port = 8080
max_conn=5
buffer_size=65535
timer = 30
timetrack = {}
etagtrack = {}

fh = open( "/home/jaimeen/Downloads/proxy/blocked.txt", "r")
blocked = fh.read()

def start():
	try:
		sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)		#create an INET, STREAMing socket
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('',listen_port))
		sock.listen(max_conn)
		print('Serving HTTP on port %s ...' % listen_port)
	except socket.error as message: 
		if sock: 
			sock.close() 
		print("Could not open socket: " + str(message) )
		sys.exit() 

	while 1:
		conn,addr = sock.accept()					#accept Request		
		conn_thread = threading.Thread( target = conn_string , args = (conn, addr))
		conn_thread.setDaemon(True)
		conn_thread.start()
	sys.exit()
	sock.close()

def conn_string(conn, addr):	

	print("Thread number:"+str(threading.activeCount()))		#print active no. of threads
	try:
		data=conn.recv(65535)
		#print(data)
		first_line = data.split('\n')[0]

		method = first_line.split(' ')[0]
		#print(method)
		if method == "GET":
			print(data)
		url = first_line.split(' ')[1]
		http_pos = url.find("://")
		if (http_pos == -1):
			temp = url
		else:
			temp = url[(http_pos+3):]
		
		port_pos = temp.find(":")
		webserver_pos = temp.find("/")
		if webserver_pos == -1:
			webserver_pos = len(temp)
		webserver = ""
		port = -1
	
		if(port_pos == -1 or webserver_pos < port_pos):
			port = 80
			webserver = temp[:webserver_pos]
		else:
			port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
			webserver = temp[:port_pos]

		if "Host: " in data:
			Host = data.split("Host: ")[1].split("\n")[0]	
		
		if (method == "POST") or (method == "HEAD") or (method == "PUT") or (method == "DELETE") or (method == "OPTIONS") or (method == "CONNECT") or (method == "PATCH") or (method == "PROPFIND") or (method == "COPY") or (method == "MOVE"):
			#print("Method name:" + method + " Not supported Method")
			http_response= "HTTP/1.1 501 Not Implemented\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>501 Not implemented Reason: Method Not implemented</body></html>"
			conn.send(http_response.encode())			#check if method is not implemented
			conn.close()

		elif not ( (method == "GET") or (method == "POST") or (method == "HEAD") or (method == "PUT") or (method == "DELETE") or (method == "OPTIONS") or (method == "CONNECT") or (method == "PATCH") or (method == "PROPFIND") or (method == "COPY") or (method == "MOVE")):
			#print("Method name:" + method + "Invalid Method")
			http_response="HTTP/1.1 400 Bad Request\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>400 Bad request reason: Invalid Method ></body></html>"
			conn.send(http_response.encode())			#check if method is invalid
			conn.close()
		
		elif url in blocked or "pokemon" in url:	
			print("Site is blocked")
			http_response="HTTP/1.0 450 Blocked\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>450 Blocked: Website cannot be accessed as it does not conform to usage policies</body></html>"
			conn.send(http_response.encode())			#check if site is blocked
			conn.close()	

		else:		
			proxy_server(webserver, port, conn, addr,data, url )		#call proxy server which communicates with actual server and replies back to client

	except Exception, e:
		pass

def proxy_server(webserver, port, conn, addr,data, url ):

	cachefilename = url
	m = hashlib.md5()
	m.update(cachefilename)
	hashname = m.hexdigest()
	
	if os.path.isfile("/home/jaimeen/Downloads/proxy/cache/" + hashname):
		print("Cache file exists")
		#print(timetrack)
		flag = True
		try:
			mtime = os.path.getmtime("/home/jaimeen/Downloads/proxy/cache/" + hashname) 
			#print(mtime)
			if mtime < float(time.time() - float(timetrack[hashname])):
				print("Now checking etag")
				etag = etagtrack[hashname]
				cachevalidity = cachevalidation(webserver, port, url, etag )
				if cachevalidity == False:
					print("It is expired so we will not use it")
					os.remove("/home/jaimeen/Downloads/proxy/cache/" + hashname)
					flag = False
					
				else:		
					print("Using cached data")
					fh = open("/home/jaimeen/Downloads/proxy/cache/" + hashname)
					cachedata = fh.readlines()
					fh.close()
					conn.send("HTTP/1.0 200 OK\r\n")
					conn.send("Content-Type:text/html")
					conn.send("\r\n")

					for i in range(0, len(cachedata)):
						#print (cachedata[i])
						conn.send(cachedata[i])	

			else:
				print("Using cached data")
				fh = open("/home/jaimeen/Downloads/proxy/cache/" + hashname)
				cachedata = fh.readlines()
				fh.close()
				conn.send("HTTP/1.0 200 OK\r\n")
				conn.send("Content-Type:text/html")
				conn.send("\r\n")

				for i in range(0, len(cachedata)):
					#print (cachedata[i])
					conn.send(cachedata[i])

		except Exception as error:
			pass
			#print(error)

	#print(url)
	if not (os.path.isfile("/home/jaimeen/Downloads/proxy/cache/" + hashname)) or flag == False:
		try:
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)		#create an INET, STREAMing socket
			s.settimeout(5)		
			s.connect((webserver, port))
			s.sendall(data)
			buffr = ''
			while 1:
				reply = s.recv(buffer_size)

				if(len(reply) > 0):
					
					if "pokemon" in reply:
						print("Site is blocked")
						http_response="HTTP/1.0 450 Blocked\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>450 Blocked: Website cannot be accessed as it does not conform to usage policies</body></html>"
						conn.send(http_response.encode())			#check if site contains pokemon
						conn.close()
					else:
						conn.send( reply)
						buffr += reply
						dar = float(len(reply))
						dar = float(dar/1024)
						dar = "%.3s" %(str(dar))
						dar = "%s KB" %(dar)
						print " Request served %s >> %s << " % ( str(addr[0]) , str(dar) )	
						#print(reply)
				else:
					break
			#print(buffr)
			prefetch( webserver, port,buffr, url)
			if not "no-cache" in buffr:
				savecache(url, buffr)
			s.close()
			conn.close()

		except socket.timeout:
			print 'A socket timed out ',client_addr,error_msg
			#print(buffr)
			if not "no-cache" in buffr:
				prefetch( webserver, port,buffr, url)
				savecache(url, buffr)
			if s:
				s.close()
			if conn:
				conn.close()

def savecache(url ,buffr):

	try:
		cachefilename = url
		m = hashlib.md5()
		m.update(cachefilename)
		hashname = m.hexdigest()
		etagtrack[hashname] = ""
		fh=open("/home/jaimeen/Downloads/proxy/cache/" + hashname, 'wb')
		if buffr == "":
			fh.write("HTTP/1.0 200 OK\n\n\n\n")
			fh.close()
		else:
			fh.writelines(buffr)
			fh.close()
		print("New cache file created")

		if "ETag: " in buffr:
			etagtrack[hashname] = buffr.split("ETag: ")[1].split(" ")[0]

		if "Cache-Control: max-age=" in buffr:	
			maxage = str1.split("Cache-Control: max-age=")[1].split(" ")[0]	
			timetrack[hashname] = float(maxage)
		else:
			timetrack[hashname] = float(timer)	

	except Exception as error:
		print(error)

def cachevalidation( webserver, port, url, etag ):
	try:
		s1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)		#create an INET, STREAMing socket
		s1.settimeout(5)		
		s1.connect((webserver, port))
		http_msg = "GET " + url + " HTTP/1.0\nIf-None-Match: " + etag + "\n\n"
		s1.sendall(http_msg)
		buffr2 = ''
		while 1:
			reply2 = s1.recv(4096)
			if len(reply2) > 0:
				buffr2 +=reply2 
			else:
				break
		
		s1.close()
		if "304 Not Modified" in buffr2:
			print("Use old cache")
			return True
		else:
			return False
		
	except socket.timeout:
		print 'A socket timed out ',client_addr,error_msg
		s1.close()		
		print("Validation error")
		return False

def prefetch( webserver, port,buffr, url):
	try:
		s2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)		#create an INET, STREAMing socket
		s2.settimeout(5)		
		s2.connect((webserver, port))

		a1 = buffr.count("Link: ")
		a2 = buffr.count("link rel=\"prefetch\"")

		for i in range(0, int(a1)):
			if "Link: " in buffr:
				t1 = buffr.split("Link: ")[1].split("\n")[0]
				if "rel=prefetch" in t1:
					link = buffr.split("Link: ")[1].split(" ")[0].split("<")[1].split(">")[0]
					buffr = buffr.split("Link: ")[1]
					url = url + link
					http_msg = "GET " + url + " HTTP/1.0\n\n"
					s2.sendall(http_msg)
					buffr2 = ''
					while 1:
						reply2 = s2.recv(4096)
						if len(reply2) > 0:
							buffr2 +=reply2 
						else:
							break
					savecache(url ,buffr2)
					s2.close()

		for i in range(0, int(a2)):
			if "link rel=\"prefetch\"" in buffr:
				link = buffr.split("link rel=\"prefetch\"")[1].split("\n")[0].split("\"")[1].split("\"")[0]	
				buffr = buffr.split("link rel=\"prefetch\"")[1]
				url = url + link
				http_msg = "GET " + url + " HTTP/1.0\n\n"
				s2.sendall(http_msg)
				buffr2 = ''
				while 1:
					reply2 = s2.recv(4096)
					if len(reply2) > 0:
						buffr2 +=reply2 
					else:
						break
				savecache(url ,buffr2)
				s2.close()
				
	except socket.timeout:
		print 'A socket timed out ',client_addr,error_msg
		s2.close()		
		print("Prefetch error")


start()
