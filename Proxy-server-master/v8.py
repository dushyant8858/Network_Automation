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
timer = 6000
timetrack = {}
etagtrack = {}

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
		
		if (method == "POST") or (method == "HEAD") or (method == "PUT") or (method == "DELETE") or (method == "OPTIONS") or (method == "CONNECT") or (method == "PATCH") or (method == "PROPFIND") or (method == "COPY") or (method == "MOVE"):
			#print("Method name:" + method + " Not supported Method")
			http_response= "HTTP/1.1 501 Not Implemented\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>501 Not implemented Reason: Method Not implemented</body></html>"
			conn.send(http_response.encode())			#check if method is not implemented
			conn.close()

		if not ( (method == "GET") or (method == "POST") or (method == "HEAD") or (method == "PUT") or (method == "DELETE") or (method == "OPTIONS") or (method == "CONNECT") or (method == "PATCH") or (method == "PROPFIND") or (method == "COPY") or (method == "MOVE")):
			#print("Method name:" + method + "Invalid Method")
			http_response="HTTP/1.1 400 Bad Request\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>400 Bad request reason: Invalid Method ></body></html>"
			conn.send(http_response.encode())			#check if method is invalid
			conn.close()
		
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
			if mtime < timetrack[hashname]:
				#cachevalidity = cachevalidation( url, etagtrack[hashname] )
				#if cachevalidity == False:
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
			if not "no-cache" in buffr:
				savecache(url, buffr)
			s.close()
			conn.close()

		except socket.timeout:
			print 'A socket timed out ',client_addr,error_msg
			#print(buffr)
			if not "no-cache" in buffr:
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

		try:
			if "Cache-Control: max-age=" in buffr:	
				maxage = str1.split("Cache-Control: max-age=")[1].split(" ")[0]	
				timetrack[hashname] = time.time() - float(maxage)

			elif "Expires: " in buffr:
				day = buffr.split("Expires: ")[1].split(" ")[1]		
				month = buffr.split("Expires: ")[1].split(" ")[2]	
				month = (strptime(month,'%b').tm_mon)
				year = buffr.split("Expires: ")[1].split(" ")[3]	
				hour = buffr.split("Expires: ")[1].split(" ")[4].split(":")[0]
				minutes = buffr.split("Expires: ")[1].split(" ")[4].split(":")[1]
				t1 = datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes))
				t2 = time.mktime(t1.timetuple())

				day = buffr.split("Date: ")[1].split(" ")[1]		
				month = buffr.split("Date: ")[1].split(" ")[2]	
				month = (strptime(month,'%b').tm_mon)
				year = buffr.split("Date: ")[1].split(" ")[3]	
				hour = buffr.split("Date: ")[1].split(" ")[4].split(":")[0]
				minutes = buffr.split("Date: ")[1].split(" ")[4].split(":")[1]
				t3 = datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes))
				t4 = time.mktime(t3.timetuple())

				maxage2 = t2-t4
				timetrack[hashname] = time.time() - float(maxage2)
		
			elif "Last-Modified: " in buffr:
				day = buffr.split("Last-Modified: ")[1].split(" ")[1]		
				month = buffr.split("Last-Modified: ")[1].split(" ")[2]	
				month = (strptime(month,'%b').tm_mon)
				year = buffr.split("Last-Modified: ")[1].split(" ")[3]	
				hour = buffr.split("Last-Modified: ")[1].split(" ")[4].split(":")[0]
				minutes = buffr.split("Last-Modified: ")[1].split(" ")[4].split(":")[1]
				t5 = datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes))
				t6 = time.mktime(t5.timetuple())

				day = buffr.split("Date: ")[1].split(" ")[1]		
				month = buffr.split("Date: ")[1].split(" ")[2]	
				month = (strptime(month,'%b').tm_mon)
				year = buffr.split("Date: ")[1].split(" ")[3]	
				hour = buffr.split("Date: ")[1].split(" ")[4].split(":")[0]
				minutes = buffr.split("Date: ")[1].split(" ")[4].split(":")[1]
				t3 = datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes))
				t4 = time.mktime(t3.timetuple())

				maxage3 = (t4-t6)/10
				timetrack[hashname] = time.time() - float(maxage3)

			else:
				timetrack[hashname] = time.time() - timer
		
		except:
			timetrack[hashname] = time.time() - timer

	except Exception as error:
		print(error)


start()
