import socket
import threading
import os
import base64
import sys
import time
import signal
reload(sys)
sys.setdefaultencoding('iso-8859-1')
from shutil import copyfile
import logging
from thread import *

listen_port = 8080
max_conn=5
buffer_size=4096

def start():
	try:
		sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)		#create an INET, STREAMing socket
		sock.bind(('',listen_port))
		sock.listen(max_conn)
		print('Serving HTTP on port %s ...' % listen_port)
	except socket.error as message: 
		if sock: 
			sock.close() 
		print("Could not open socket: " + str(message) )
		sys.exit(1) 

	while 1:
		try:
			conn,addr = sock.accept()					#accept Request
			data=conn.recv(65535)
			print(data)
			#start_new_thread(conn_string , (conn, data, addr))
			thr_multiple=Multiple(conn,addr,data)
			thr_multiple.daemon = True	
			thr_multiple.start()

		except:
			sock.close()
			print("Client socket failed")	
			sys.exit(1)

	sock.close()

class Multiple(threading.Thread):
	def __init__(self,conn,addr,data):
		threading.Thread.__init__(self)
		print("client connected at ",conn)			#show on terminal the socket at which client is connected
		self.conn = conn 
		self.addr = addr 
		self.data = data
		self.size = 65535
		print("Thread number:"+str(threading.activeCount()))		#print active no. of threads
	
	def run(self):
		global webserver, port
		try:
			first_line = self.data.split('\n')[0]
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

		except Exception, e:
			pass

		try:
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)		#create an INET, STREAMing socket
			s.connect((webserver, port))
			s.send(self.data)
	
			while 1:
				reply = s.recv(buffer_size)

				if(len(reply) > 0):
					self.conn.send(reply.encode())
	
					dar = float(len(reply))
					dar = float(dar/1024)
					dar = "%.3s" %(str(dar))
					dar = "%s KB" %(dar)
					print " Request served %s >> %s << " % ( str(self.addr[0]) , str(dar) )	
				else:
					break
			s.close()
			self.conn.close()
		except socket.error, (value, message) :
			s.close()
			self.conn.close()
			sys.exit(1)

if __name__ == '__main__':
	start()
