import socket 
import sys
import time  
from time import sleep 
host='127.0.0.1' 
port=5044 
backlog=5 
try: 
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

	client.connect((host,port)) 
except socket.error(): 
	print("not possible to listen") 
	sys.exit() 

msg= "GET / HTTP/1.1\r\nHost: localhost:"+str(port)+"\r\nConnection: Keep-alive\r\n\r\nGET / HTTP/1.1\r\nHost: localhost:"+str(port)+"\r\nConnection: keep-alive" 

for i in range(0,2): 
	client.send(msg) 
	while(True): 
		data = client.recv(1024) 
		if data: 
			print data
