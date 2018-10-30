# -*- coding: utf-8 -*-
import socket
import os
import sys
import time

def checkArgs():		
	if len(sys.argv) != 2:
		print("Error: Must supply 1 argument\nUSAGE: " + sys.argv[0] + " portnumber")
		sys.exit()
	return sys.argv[1]
checkArgs()

if int(sys.argv[1]) > 5000 and int(sys.argv[1]) < 65535:
	port=int(sys.argv[1])
else:
	print("You can use port numbers above 5000 and below 65535 only")
	sys.exit()

s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", port))
print("Waiting on port:" + str(port))

def sendfile(filename, clientAdd):
	clientAddr = clientAdd
	if os.path.isfile(filename):
		fh= open(filename, "r")
		while True:
			partfile = fh.readline(1024)
			if not partfile:
				break
			s.sendto(partfile.encode(), clientAddr)
			msg, clientAddr = s.recvfrom(1024)
			msg=msg.decode()
			#print(msg)
			if not msg == "ACK":
				s.sendto(partfile.encode(), clientAddr)
		partfile="Complete"
		s.sendto(partfile.encode(), clientAddr)
		fh.close()
		print("File sent")
	else:
		msg="No such file"
		s.sendto(msg.encode(), clientAddr)		
	return

def sendimage(imagefile, clientAdd):
	clientAddr = clientAdd	
	try:
		fh= open(imagefile, "rb")
		while True:
			partimage = fh.readline(1024)
			if not partimage:
				break
			s.sendto(partimage, clientAddr)
			msg, clientAddr = s.recvfrom(1024)
			msg=msg.decode()
			#print(msg)
			if not msg == "ACK":
				s.sendto(partimage, clientAddr)
		partimage="Complete"
		s.sendto(partimage, clientAddr)
		fh.close()
		print("Image sent")
	except:
		msg="No such image file"
		s.sendto(partimage, clientAddr)	
	return

def savefile(filename):
	ack="ACK"	
	fh= open( filename, "w")
	while True:
		partfile, clientAddr = s.recvfrom(1024)
		partfile = partfile.decode()
		if partfile == "Complete":
			break
		fh.write(partfile)
		s.sendto(ack.encode(), clientAddr)
		#print(ack)
	fh.close()
	print("File Received")
	return

def saveimage(imagefile):
	ack="ACK"
	fh= open( imagefile, "wb")
	while True:
		partimage, clientAddr = s.recvfrom(1024)
		if partimage == "Complete":
			break
		fh.write(partimage)
		s.sendto(ack.encode(), clientAddr)
		#print(ack)
	fh.close()
	print("Image Received")
	return

def renamefile(oldfilename, newfilename):
	msg, clientAddr = s.recvfrom(1024)
	fmsg=msg.decode()
	if fmsg == "No such file present on Client":
		return	
	if fmsg == "Correct file":
		os.rename(oldfilename, newfilename)	
		msg="Renamed Successfully"
		print(msg)
		time.sleep(1)
		s.sendto(msg.encode(), clientAddr)		
		return

def listfile():
	files = [f for f in os.listdir('.') if os.path.isfile(f)]
	files2 = [item+"\n" for item in files]
	msg=''.join(files2)
	s.sendto(msg.encode(), clientAddr)		
	return

def callexit():
	msg = "Server has exited" 
	print(msg)
	s.close()	
	sys.exit()	
	return

def nosuchcommand(errorcomm):
	msg = errorcomm + ", No such Command"
	s.sendto(msg.encode(), clientAddr)		
	return	

ls=[]
while 1:
	comm, clientAddr = s.recvfrom(1024)
    #print(comm.decode())
	ls=comm.split()
	#print(ls[1])
	if ls[0] == "get":
		sendfile(ls[1], clientAddr)
	elif ls[0] == "getimage":
		sendimage(ls[1], clientAddr)
	elif ls[0] == "put":
		savefile(ls[1])	
	elif ls[0] == "putimage":
		saveimage(ls[1])
	elif ls[0] == "rename":
		renamefile(ls[1], ls[2])
	elif ls[0] == "list":
		listfile()
	elif ls[0] == "exit":
		callexit()
	else:
		nosuchcommand(ls[0])
