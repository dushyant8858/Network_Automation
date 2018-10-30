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

def sigint_handler(signum, frame):
	print("You pressed CTRL+C!")
	sys.exit()

class Config():
	#def __init__(self, ls1, ls2, port, url2, defaultfile ,timer):
	def __init__(self):
		if os.path.isfile("ws.conf"):			#Checks whether given file is present or not
			print("Configuration file is present")
		else:
			print("Configuration file is absent")
			sys.exit()

		self.fh=open("ws.conf","r")
		global ls1, ls2, port, url2, defaultfile, timer, version

		for self.line in self.fh:
			i=int(0)
			if 'ListenPort' in self.line:
				try:
					port=self.line.split()[1]
					if int(port) < 1024 or int(port) > 65535:
						print("Requested port no:"+port+" Port nos less than 1024 and greater than 65,535 not allowed. Change configuration.")
						sys.exit()
				except:
					print("Port no. not found. Server quits")
					sys.exit()

			if 'Documentroot' in self.line:	
				try:				
					url2=self.line.split()[1]
				except:
					print("No root directory in config")
					

			if 'DirectoryIndex' in self.line:	
				try:
					defaultfile=self.line.split()[1]
				except:
					print("No index page in config")				
		
			if 'KeepaliveTime' in self.line:
				try:
					timer = self.line.split()[1]
				except:
					print("Timer not present. Server sets it to 0.")
					timer = 0

			if 'ContentType' in self.line:
				try:
					ls1.append(self.line.split()[1])
				except:
					ls1.append('')
					print("Improper file types in config")
				try:
					ls2.append(self.line.split()[2])
				except:
					ls2.append('')
					print("Improper content types in config")

class Server():
	def __init__(self):
		global port
		self.host = '' 
		self.port = int(port)
		self.threads=[]
		self.create_socket()
	def create_socket(self):
		try:
			sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)#create an INET, STREAMing socket
			sock.bind((self.host,self.port))#bind the socket to a host, and a port
			sock.listen(200)#queue up as many as 200 connect requests
			print ('Serving HTTP on port %s ...' % self.port)
			self.sock=sock
			self.accept_req()#call accept_req()
		except socket.error as message: 
			if sock: 
				sock.close() 
			print ("Could not open socket: " + str(message) )
			sys.exit(1) 

	def accept_req(self):	
		while 1:
			try:
				conn,addr=self.sock.accept()#accept Request
				if conn:
					thr_multiple=Multiple(conn,addr)
					thr_multiple.daemon = True
					thr_multiple.start()
					conn.send((u"\r\n"))
					#self.threads.append(thr_multiple)
				#for elements in self.threads:
					#elements.join()
			except:
				http_response=version + " 500 Internal Error\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>500 Internal Error: Cannot allocate memory </body></html>"
				self.conn.send(http_response.encode()) 
				self.conn.close()
				
            
class Multiple(threading.Thread, Config):
	def __init__(self,conn,addr):
		global ls1, ls2, port, url2, defaultfile, timer, version
		threading.Thread.__init__(self)
		print ("client connected at ",conn)
		self.conn = conn 
		self.addr = addr 
		self.size = 65535
		print("Thread number:"+str(threading.activeCount()))
		
	def run(self):
		global version
		now = time.time()
		future = now + int(timer)
		try:
			while (time.time() < future):
				request=self.conn.recv(65535)
				if request != '':				
					print(request.decode())
				if "Connection: keep-alive" in request:
					print ("Persistent connection\n")
					now = time.time()
					future = now + int(timer)
				if request:
					#http_response=(file1)
					str1=request.decode()
					str2=str1.splitlines()[0]				#get first line of http request message
					method, url, version=str2.split()
					print("HTTP request msg\n"+str2)
					self.sendfile(method, url, version, str1)
			print("Server timed out a connection")
			self.conn.close()
		except:
			print("Tried opening a closed socket")


	def sendfile(self,method, url, version, str1):
		self.method = method
		self.version = version
		self.url = url
		self.str1 = str1
		url1 = url2			
		#url1="/home/jaimeen/Downloads/tcpserver"
		url1 += url
		print("Path of file: " + url1)
		#filename= url.split(".")[0]
		#print(filename)
		if not ( (version == "HTTP/1.0") or (version == "HTTP/1.1") ):
			print("version is not correct")
			http_response=version + " 400 Bad Request\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>400 Bad Request Reason: Invalid Version </body></html>"
			self.conn.send(http_response.encode())

		if (method == "POST"):
			postdata = str1.split("keep-alive")[1]
			print(str1)
			print(postdata)
			if ( url == "/" ) or ( url == "/rootdirectory/"):
				if defaultfile == "":
					http_response = version + " 200 OK\nContent-  Type: text/html\nContent-Length: 20\n"					
					http_response += "Connection: Keep-Alive\nKeep-Alive: max=5, timeout=10\n\n"
					http_response += "Index file is absent"
					self.conn.send(http_response)
				else:	
					print("sending index file")	
					url1 += defaultfile		
					http_response = version + " 200 OK\nContent-  Type: text/html\nContent-Length:"

					copyfile(url1, "temp.txt")
					fh=open("temp.txt","a")
					fh.write("<html><h1>POST DATA:</h1>\n<pre>\n" + postdata + "\n</pre> </html>")
					fh.close()

					http_response += str(os.path.getsize("temp.txt")) + "\n"
					#print(str(os.path.getsize("temp.txt")  )  )	
		
					http_response += "Connection: Keep-Alive\nKeep-Alive: max=5, timeout=10\n\n"
					fi = open("temp.txt", "r")
					newdata=fi.read()
					http_response += newdata
					print("Post data attached")
					self.conn.send(http_response)
					fi.close()	

			flag = "0"
			for i in range( 0, len(ls1)):
				if ( ls1[i] in str(url) ):
					flag = "1"
					if ls2[i] == '':	
						http_response=version + " 500 Internal Error\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>500 Internal Error: Content type not found in config</body></html>"
						self.conn.send(http_response.encode())
					else:
						print("Transferring post request file")			

						http_response = version + " 200 ok\nContent-Type:"+ ls2[i] +"\nContent-Length: "

						copyfile(url1, "temp.txt")
						fh=open("temp.txt","a")
						fh.write("<html><h1>POST DATA:</h1>\n<pre>\n" + postdata + "\n</pre> </html>")
						fh.close()

						http_response += str(os.path.getsize("temp.txt")) + "\n"
						#print(str(os.path.getsize("temp.txt")  )  )					

						http_response += "Connection: Keep-Alive\nKeep-Alive: max=5, timeout=10\n\n"
						fi = open("temp.txt", "r")
						newdata=fi.read()
						http_response += newdata
						print("Post data attached")
						self.conn.send(http_response)
						fi.close()

			if flag == "0":
				http_response=version + " 500 Internal Error\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>500 Internal Error: File type not found in config</body></html>"
				self.conn.send(http_response.encode())	

			if not os.path.isfile(url1):
				http_response=version + " 404 NOT FOUND\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>404 Not Found Reason URL does not exist </body></html>"
				self.conn.send(http_response.encode()) 
				self.conn.close()
			

		if (method == "GET"):		
			if ( url == "/" ) or ( url == "/rootdirectory/"):
				if defaultfile == "":
					http_response = version + " 200 OK\nContent-  Type: text/html\nContent-Length: 20\n"					
					http_response += "Connection: Keep-Alive\nKeep-Alive: max=5, timeout=10\n\n"
					http_response += "Index file is absent"
					self.conn.send(http_response)
				else:
					print("sending index file")	
					url1 += defaultfile		
					fh= open( url1, "r")
					file2=fh.read()
					http_response = version + " 200 OK\nContent-  Type: text/html\nContent-Length:"
					lengthoffile=os.path.getsize(url1)
					http_response +=str(lengthoffile) + "\n"
					http_response += "Connection: Keep-Alive\nKeep-Alive: max=5, timeout=10\n\n"
					http_response += file2
					self.conn.send(http_response)
					fh.close()
					#self.conn.close()	
		
			elif (url == "/favicon.ico"):
				print("Favicon passed")

			elif os.path.isfile(url1):
				flag = "0"
				for i in range(0,len(ls1)):
					if ( ls1[i] in str(url) ):
						flag = "1"
						if ls2[i] == '':	
							http_response=version + " 500 Internal Error\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>500 Internal Error: Content type not found in config</body></html>"
							self.conn.send(http_response.encode()) 
						else:
							print("Transferring file")			
							fh= open(url1, "rb")
							file2=fh.read()
							http_response = version + " 200 OK\nContent-Type:"+ ls2[i] +"\nContent-Length:"
							lengthoffile=os.path.getsize(url1)
							http_response +=str(lengthoffile) + "\n"
							http_response += "Connection: Keep-Alive\nKeep-Alive: max=5, timeout=10\n\n"
							http_response += file2
							self.conn.send(http_response)
							fh.close()
				
				if flag == "0":
					http_response=version + " 500 Internal Error\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>500 Internal Error: File type not found in config</body></html>"
					self.conn.send(http_response.encode()) 					

			else:
				http_response=version + " 404 NOT FOUND\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>404 Not Found Reason URL does not exist :<<requestedurl>></body></html>"
				self.conn.send(http_response.encode()) 
				#self.conn.close()
		
		elif (method == "HEAD") or (method == "PUT") or (method == "DELETE") or (method == "OPTIONS") or (method == "CONNECT"):
			http_response=version + " 501 Not Implemented\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>501 Not implemented Reason: Method Not implemented</body></html>"
			self.conn.send(http_response.encode())
			self.conn.close()

		else:
			http_response=version + " 400 Bad Request\nConnection: Keep-Alive\nKeep-Alive: max=5, timeout=10 \n\n <html><body>400 Bad request reason: Invalid Method ></body></html>"
			self.conn.send(http_response.encode())
			self.conn.close()
      
if __name__ == '__main__':
	signal.signal(signal.SIGINT, sigint_handler)
	ls1 = []
	ls2 = []
	port = int(0)
	url2 = ""
	defaultfile = ""
	timer = int(0)
	version = "HTTP/1.1"
	config = Config()
	server = Server()

