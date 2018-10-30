# -*- coding: utf-8 -*-
import socket
import sys
import os
import netaddr
try:
    s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print("Failed to create socket")
    sys.exit()

def checkArgs():			#function for checking no. of arguments
	if len(sys.argv) != 3:
		print("Error: Must supply 2 argument\nUSAGE: " + sys.argv[0] + " ipaddress portnumber")
		sys.exit()
	return sys.argv[1]
checkArgs()

host = str(sys.argv[1])
#host = '127.0.0.1'

if int(sys.argv[2]) > 5000 and int(sys.argv[2]) < 65535:
	port=int(sys.argv[2])
else:
	print("You can use port numbers above 5000 and below 65535 only")
	sys.exit()
serverAddr = (host, port)

def savefile(filename):
	ack="ACK"	
	msg, serverAddr = s.recvfrom(1024)
	s.sendto(ack.encode(), serverAddr)
	#print(ack)	
	fmsg=msg.decode()
	if fmsg == "No such file":
		print(fmsg)
	else:
		fh= open( "received_" + filename, "w")
		fh.write(fmsg)
		while True:
			partfile, serverAddr = s.recvfrom(1024)
			partfile = partfile.decode()
			if partfile == "Complete":
				break					
			fh.write(partfile.decode())
			s.sendto(ack.encode(), serverAddr)
			#print(ack)
		print("File Received")
		fh.close()
	return

def saveimage(imagefile):
	ack="ACK"
	msg, serverAddr = s.recvfrom(1024)
	s.sendto(ack.encode(), serverAddr)
	#print(ack)
	if msg == "No such image file":
		print(msg)
	else:
		fh= open( "received_" + imagefile, "wb")
		fh.write(msg)		
		while True:
			partimage, serverAddr = s.recvfrom(1024)
			if partimage == "Complete":
				break
			fh.write(partimage)
			s.sendto(ack.encode(), serverAddr)
			#print(ack)
		print("Image Received")
		fh.close()
	return

def sendfile(filename, serverAdd):
	serverAddr = serverAdd	
	if os.path.isfile(filename):	
		fh = open(filename, "r")
		while True:
			partfile = fh.readline(1024)
			if not partfile:
				break
			s.sendto(partfile.encode(), serverAddr)
			msg, serverAddr = s.recvfrom(1024)
			msg=msg.decode()
			#print(msg)
			if not msg == "ACK":
				s.sendto(partfile.encode(), serverAddr)
		partfile="Complete"
		s.sendto(partfile.encode(), serverAddr)
		fh.close()
		print("File sent")
	else:
		print("No such file present on Client")	
	return


def sendimage(imagefile, serverAdd):
	serverAddr = serverAdd
	if os.path.isfile(imagefile):	
		fh= open(imagefile, "rb")
		while True:
			partimage = fh.readline(1024)
			if not partimage:
				break
			s.sendto(partimage, serverAddr)
			msg, serverAddr = s.recvfrom(1024)
			msg=msg.decode()
			#print(msg)
			if not msg == "ACK":
				s.sendto(partimage, serverAddr)
		partimage="Complete"
		s.sendto(partimage, serverAddr)
		fh.close()
		print("Image sent")
	else:
		print("No such image file present on Client")	
	return

		
def renamefile(oldfilename, newfilename):
	global serverAddr
	if os.path.isfile(oldfilename):
		#host = '127.0.0.1'
		#port = 5000
		#serverAddr = (host, port)
		msg="Correct file"
		s.sendto(msg.encode(), serverAddr)	
		rmsg, serverAddr = s.recvfrom(1024)
		print(rmsg.decode())	
	else:
		#host = '127.0.0.1'
		#port = 5001
		#serverAddr = (host, port)
		msg="No such file present on Client"
		s.sendto(msg.encode(), serverAddr)	
		print("No such file present on Client")
	return

def listfile():
	msg, serverAddr = s.recvfrom(4096)
	print(msg.decode())
	return

def callexit():
	print("Client is exiting now")
	s.close()
	sys.exit()
	return

def nosuchcommand():
	msg, serverAddr = s.recvfrom(1024)
	print(msg.decode())
	return

while 1:
	comm=raw_input("\nEnter a command:\nget [filename]\ngetimage [filename]\nput [filename]\nputimage [filename]\nrename [old_filename] [new_filename]\nlist\nexit\n")
	s.sendto(comm.encode(), serverAddr)
	ls=comm.split()
	if ls[0] == "get":	
		savefile(ls[1])
	elif ls[0] == "getimage":
		saveimage(ls[1])
	elif ls[0] == "put":
		sendfile(ls[1], serverAddr)
	elif ls[0] == "putimage":
		sendimage(ls[1], serverAddr)
	elif ls[0] == "rename":
		renamefile(ls[1], ls[2])
	elif ls[0] == "list":
		listfile()
	elif ls[0] == "exit":
		callexit()
	else:
		nosuchcommand()
