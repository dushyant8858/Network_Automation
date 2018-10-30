import socket
import os
import sys
import hashlib				#import libraries
import threading
import time

def chkPort(port):
    if port < 5000 or port > 65535:
        print ("Use port number between 5000 and 65535")		#Check if port no. is valid or not
        sys.exit()

def user_dict_read(port):
    if os.path.isfile("dfsconf.txt"):			#Open conf file and read parameters from it
        with open('dfsconf.txt', 'r') as rfile:
            for line in rfile:
                line = line.split(" ")
                username = line[0]
                password = line[1].splitlines()
                password = password[0]
                newrecord = {}
                newrecord[username] = password
                userdict.append(newrecord)
    else:
        print("Conf file not found\nServer at " + str(port)+ "quits")
        sys.exit()

class Server:
    def __init__(self, port):
        self.host = ''
        self.port = port
        self.threads = []

    def startserver(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.socket.settimeout(1)
        try:
            print("Hosting server on port no. " + str(self.port))
            self.socket.bind((self.host, self.port))

        except Exception as e:
            print ("Error: Failed to create socket for port: " + str(port))
            self.shutdown()
            sys.exit(1)

        print ("Server successfully acquired socket with port:", self.port)
        self._wait_for_connections()

    def _wait_for_connections(self):
        while True:
            print ("Waiting for connection from client" + '\n')
            try:
                self.socket.listen(1024)
                self.accept_req()
            except socket.error as message:
                print ("Error: Could not listen to connections: " + str(message))
                sys.exit(1)

    def accept_req(self):
        while 1:
            try:
                conn, addr = self.socket.accept()
                print("Received a connection from:", addr)
                if conn:
                    thr_multiple = Multiple(conn, addr)
                    thr_multiple.daemon = True
                    thr_multiple.start()
                    self.threads.append(thr_multiple)
            except KeyboardInterrupt:
                print("\nYou pressed Ctrl+C. Server quits")
                sys.exit()

    def shutdown(self):
        try:
            print('\n' + "Server quits due to shutdown")
            server.socket.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            print ("Error: Could not shut down the socket", e)


class Multiple(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        print ("Client connected at ", conn)
        self.conn = conn
        self.addr = addr
        self.threads = []

    def run(self):
	try:
		data = self.conn.recv(1024)
		#print(data)
		data = data.split(":")			#Receive username:password from client
		username1 = data[0]
		password1 = data[1]
		#print(userdict)
		#print(password1)
		#print (username1)
		c = 0
		for item in userdict:
		    if username1 in item.keys():
		        if password1 == item[username1]:	#If username and password matches then serve request
		            c = 1
		        else:
		            print("The password did not match.")
		c = str(c)
		#print(c)
		self.conn.send(c.encode())

		if c == '1':
		    if os.path.isdir(username1):		#if directory is present for username then use that directory, else create new directory for username
		        pass
		    else:
		        os.mkdir(username1)
		    message = self.conn.recv(1024)
		    #print (message)
		    modifiedMessage = str(message) + "_Acknowledge"
		    self.conn.send(modifiedMessage.encode())


		    command = self.conn.recv(1024)		#receive command from client and call respective function
		    if command == "GET":
		        self.getfile(username1)
		    elif command == "PUT":
		        self.putfile(username1)
		    elif command == "List":
		        self.List(username1)
		else:
		    print("Username/Password was not verified.")
		    self.conn.close()
        except:
            print("A server check occured.")
            self.conn.close()	

    def putfile(self, username1):			#Putfile function is called when client wants to send a file to server
        totalbytesrecv = 0
        filename = self.conn.recv(1024)			#receive filename
        filename = filename.decode()
 	filename = filename.replace('.enc', '')		#since it is encrypted, remove the .enc extension
        print("\nThe client sends this file to the server: " + filename)

        filesize = self.conn.recv(1024)			#receive file size
        filesize = filesize.decode()
        print ("Size of file: " + filesize + " B")
	subfolder = self.conn.recv(1024)		#receive subfolder name	
	print("*"*100)	
	print(subfolder)
        if subfolder != "N/A":				#if subfolder is received then open subfolder or create subfolder then open it
            if os.path.isdir(username1 + "/" + subfolder):
                pass
            else:
                os.mkdir(username1 + "/" + subfolder)
            if os.path.isfile(username1 + "/" + subfolder + "/" + filename):

                fileexist = str("Error! File of this name already exists.")	#if file already exists ons erver, then ask client not to transfer it
                self.conn.send(fileexist.encode())
                print(fileexist)
            else:
                filedoesnotexist = str("recieving file- " + filename)
                self.conn.send(filedoesnotexist.encode())			#else receive the file
                newfile = open(username1 + "/" + subfolder + "/" + filename, 'wb')
                x = self.conn.recv(1024)					#receive file data
                x = int(x)
                if x < 512:
                    recvdatabytes = self.conn.recv(1024)
                    newfile.write(recvdatabytes)
                else:
                    while totalbytesrecv < filesize:
                        recvdatabytes = self.conn.recv(1024)
                        newfile.write(recvdatabytes)
                        filesize = int(filesize)
                        x = filesize - totalbytesrecv
                        if x < 1024:
                            recvdatabytes = self.conn.recv(x)
                            newfile.write(recvdatabytes)
                            totalbytesrecv += x
                        else:
                            totalbytesrecv += 1024
        else:
            if os.path.isfile(username1 + "/" + filename):			#if subfolder is not present in request, then use main directory of server
                fileexist = str("Error! File of this name already exists.")
                self.conn.send(fileexist.encode())
                print(fileexist)
            else:
                filedoesnotexist = str("recieving file- " + filename)
                self.conn.send(filedoesnotexist.encode())
                newfile = open(username1 + "/" + filename, 'wb')
                x = self.conn.recv(1024)
                x = int(x)
                if x < 512:
                    recvdatabytes = self.conn.recv(1024)
                    newfile.write(recvdatabytes)
                else:
                    while totalbytesrecv < filesize:
                        recvdatabytes = self.conn.recv(1024)
                        newfile.write(recvdatabytes)
                        filesize = int(filesize)
                        x = filesize - totalbytesrecv
                        if x < 1024:
                            recvdatabytes = self.conn.recv(x)
                            newfile.write(recvdatabytes)
                            totalbytesrecv += x
                        else:
                            totalbytesrecv += 1024

    def List(self, username1):
        path1 = ""
        subfolder = self.conn.recv(1024)			#receive subfolder name
        print(subfolder)
        if subfolder != "N/A":					#if subfolder is given, then create/open subfolder 
            if os.path.isdir(username1 + "/" + subfolder):
                path1 = os.path.abspath(os.curdir)
                path1 = path1 + "/" + username1 + "/" + subfolder
                if os.path.isdir(path1):
                    list1 = [f for f in os.listdir(path1)]
                    length = len(list1)
                    print("\nThe client has requested to list all files on the current server directory.They are: ")
                    print(list1)
                    x = 0
                    length1 = str(length)			#send length of list to client
                    self.conn.send(length1.encode())
                    print(length)
		    length = length - 1
		    
                    while x <= length:
                        a = list1[x]				#send list elements to client
                        self.conn.send(a.encode())
                        time.sleep(0.1)
                        x += 1
			print(x)
                    self.conn.close()
                else:
                    list1 = "There is no subdirectory for username: " + username1
                    list1 = str(list1)
                    self.conn.send(list1.encode())
                    self.conn.close()
            else:
                list1 = "There is no subdirectory for username: " + username1
                list1 = str(list1)
                self.conn.send(list1.encode())
                self.conn.close()
        else:
            path1 = os.path.abspath(os.curdir)			#if subfolder is not present then use main directory
            path1 = path1 + "/" + username1
            if os.path.isdir(path1):
                list1 = [f for f in os.listdir(path1)]
                print(list1)
                for line in list1:
                    if line[0] != ".":
                        list1.remove(line)
                length = len(list1)
                print("\nThe client has requested to list all files on the main server directory.They are: ")
                print(list1)
                x = 0
                length1 = str(length)
		#print(length1)
                self.conn.send(length1)		#send length of list to client	
                length = length - 1
                while x <= length:
                    a = list1[x]		#send list elements to client
                    self.conn.send(a.encode())
                    time.sleep(0.1)
                    x += 1
                self.conn.close()
            else:
                list1 = "There is no username directory for username: " + username1
                list1 = str(list1)
                self.conn.send(list1.encode())
                self.conn.close()


    def getfile(self, userName1):			#function to send file to client
        filename = self.conn.recv(1024)			#receive file name
        subfolder = self.conn.recv(1024)		#receive subfolder name
        # print(filename)
        # print (subfolder)
        filename1 = "." + filename + "." + str(1)	#construct file part name
        filename2 = "." + filename + "." + str(2)
        filename3 = "." + filename + "." + str(3)
        filename4 = "." + filename + "." + str(4)

	try:
		if subfolder != "N/A":
		    path1 = userName1 + "/" + subfolder + "/" + filename1
		    path2 = userName1 + "/" + subfolder + "/" + filename2	#if subfolder is requested open it and add file name at its end
		    path3 = userName1 + "/" + subfolder + "/" + filename3
		    path4 = userName1 + "/" + subfolder + "/" + filename4
		else:
		    path1 = userName1 + "/" + filename1
		    path2 = userName1 + "/" + filename2
		    path3 = userName1 + "/" + filename3
		    path4 = userName1 + "/" + filename4

	except: 
	    print("\nSubfolder Error. It might not be present. Server quits")
	    sys.exit()

        print(path1)
        if os.path.isfile(path1):
            self.send_file(userName1, filename1, subfolder)	#send file to client
            time.sleep(0.1)
        else:
            print("\nError! The file name entered does not exist.")
            filenotexist = str(0)
            self.conn.send(filenotexist.encode())
            time.sleep(0.1)
        if os.path.isfile(path2):
            self.send_file(userName1, filename2, subfolder)
            time.sleep(0.1)
        else:
            print("\nError! The file name entered does not exist.")
            filenotexist = str(0)
            self.conn.send(filenotexist.encode())
            time.sleep(0.1)
        if os.path.isfile(path3):
            self.send_file(userName1, filename3, subfolder)
            time.sleep(0.1)
        else:
            print("\nError! The file name entered does not exist.")
            filenotexist = str(0)
            self.conn.send(filenotexist.encode())
            time.sleep(0.1)
        if os.path.isfile(path4):
            self.send_file(userName1, filename4, subfolder)
            time.sleep(0.1)
        else:
            print("\nError! The file name entered does not exist.")
            filenotexist = str(0)
            self.conn.send(filenotexist.encode())
            time.sleep(0.1)

    def send_file(self, userName1, filename, subfolder):
        print(os.getcwd())
        if subfolder != "N/A":
            os.chdir(userName1 + "/" + subfolder)
            path = filename

        else:
            path = userName1 + "/" + filename

        # print(os.getcwd())
        bytestobesent = 0

        filesize = os.path.getsize(path)		#read size of file
        print("\nThe user will get a file from server sub directory")
        print("The size of the file is- " + str(filesize) + " Bytes")
        fileexist = str("Ok, File of this name exists.")
        self.conn.send(fileexist.encode())		#send confirmation that file exits
        time.sleep(0.1)
        self.conn.send(str(filesize).encode())		#send sie of file
        time.sleep(0.1)
        self.conn.send(str(filename).encode())		#send filename
        time.sleep(0.1)
        with open(path, 'rb') as rbfile:
            x = filesize // 2
            self.conn.send(str(x))			#send file content
            time.sleep(0.1)
            if x < 512:
                atatimebytes = rbfile.read(1024)
                self.conn.send(atatimebytes)
            else:
                while bytestobesent < filesize:
                    atatimebytes = rbfile.read(1024)
                    self.conn.send(atatimebytes)
                    bytestobesent += 1024
                print("File part complete")
        if subfolder != "N/A":
            os.chdir("..")
            os.chdir("..")
            #print(os.getcwd())

if __name__ == '__main__':				#main function

    port = 10003				
    chkPort(port)			#check if port no. is valid or not
    userdict = []
    user_dict_read(port)			#read configuration parameters

    server = Server(port)		#create server object
    server.startserver()		#start server function
