import socket
import sys
import os
import hashlib
import time
import struct
from Crypto.Cipher import AES

def menu():
    try:
        print("\nEnter one of the following commands: \n")		# Display Menu to user
        usrinput = raw_input("1. GET *filename* (Subfolder) \n2. PUT *filename* (Subfolder) \n3. List (Subfolder) \nEnter your command: ")
	spliter = usrinput.split()
        if usrinput[:3] == 'GET':
                try:							#check if subfolder is entered or not
                    if len(spliter) == 2:
                        (command, filename) = usrinput.split()		#if no subfolder is entered, return command and file name
                        return (command,filename)
                    if len(spliter) == 3:
                        (command, filename, subfolder) = usrinput.split()
                        return (command, filename, subfolder)		#if subfolder is entered, return command, filename and subfolder
                except:
                    return "Error: Wrong Command"
        elif usrinput[:3] == 'PUT':
                try:
                    if len(spliter) == 2:
                        (command, filename) = usrinput.split()
                        return (command,filename)
                    if len(spliter) == 3:
                        (command, filename, subfolder) = usrinput.split()
                        return (command, filename, subfolder)
                except:
                    return "Error: Wrong Command"
        elif usrinput[:4] == 'List':
            try:
                if len(spliter) == 1:
                    (command) = usrinput.split()
                    return (command)
                if len(spliter) == 2:
                    (command, subfolder) = usrinput.split()
                    return (command, subfolder)
	    except:
                    return "Error: Wrong Command"
        else:
            return "Error: Wrong Command"
    except KeyboardInterrupt:
        print("\nYou pressed Ctrl+C. Client quits.")
        sys.exit()

def keyGenerator(password1):
    length = len(password1)
    if length == 16:
        key = password1					#if password length is 16, return password
        return key
    elif length < 16:
        while length < 16:
            password1 = password1 + "A"			#if password length is less than 16, return password padded with A
            length +=1
        key = password1
        return key
    elif 16 < length < 24:
        while length < 24:				#if password length is greater than 16, return password padded with A
            password1 = password1 + "A"
            length +=1
        key = password1
        return key

def encrypt_file(password1, infilename, outfilename=None, chunksize=64*1024):		#function to encrypt file
    try:
	    key = keyGenerator(password1)							#function to generate key using password
	    if not outfilename:
		outfilename = infilename

	    iv = 'This is an IV456'
	    encryptor = AES.new(key, AES.MODE_CBC, iv)
	    filesize = os.path.getsize(infilename)

	    with open(infilename, 'rb') as infile:
		path = "Encrypt" +"/"+ outfilename
		if os.path.isdir("Encrypt"):
		    if os.path.isfile("Encrypt/dfcconf.txt"):
		        pass
		    else:
		        from shutil import copyfile
		        copyfile("dfcconf.txt", "Encrypt/dfcconf.txt")
		else:
		    os.mkdir("Encrypt")
		    os.chdir("Encrypt")
		    with open("dfcconf.txt", "w"):
		        pass
		    os.chdir("..")
		    from shutil import copyfile
		    copyfile("dfcconf.txt", "Encrypt/dfcconf.txt")

		with open(path, 'wb') as outfile:
		    outfile.write(struct.pack('<Q', filesize))
		    outfile.write(iv)
		    while True:
		        chunker = 16
		        chunk = infile.read(chunker -chunksize)
		        if len(chunk) == 0:
		            break
		        elif len(chunk) % 16 != 0:
		            chunk += ' ' * (16 - len(chunk) % 16)
		        chunker+=16
		        outfile.write(encryptor.encrypt(chunk))
	    return (path)
    except:
		print("\nUnable to encrypt")

def decrypt_file(password1, infilename, output_filename, chunksize=24*1024):			#function to decrypt file
    try:
	    key = keyGenerator(password1)								#function to generate key using password
	    #print(key)
	    outfilename = output_filename

	    with open(infilename, 'rb') as infile:
		origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
		iv = infile.read(16)
		decryptor = AES.new(key, AES.MODE_CBC, iv)

		with open(outfilename, 'wb') as outfile:
		    with open(outfilename, 'wb') as outfile:
		        while True:
		            chunk = infile.read(chunksize)
		            if len(chunk) == 0:
		                break
		            outfile.write(decryptor.decrypt(chunk))
		        outfile.truncate(origsize)
		print("All parts Decrypted")
    except:
		print("\nUnable to encrypt")

def checkuserdict(username1 , password1):				#Check dictionary for no. of users
    if (len(userdict)) == 1:
        for item in userdict:
            for x in item:
                username1 = x
                print("Username: " + str(username1))
            password1 = item[username]


    if (len(userdict)) >= 2:						#If more than 2 users then ask user to enter username
        print("More than 1 user exists. Please enter user you want to login with.")
        try:
            while True:
                c = 0
                username1 = raw_input("Enter username: ")
                for item in userdict:
                    if username1 in item.keys():
                        print("OK. Entered username exists")
                        password1 = item[username]
                        c = 1
                        break
                if c == 1:
                    break
                else:
                    print("Username does not exist. Try again")

        except KeyboardInterrupt:
            print("\nYou pressed Ctrl +c. Client quits.")
            sys.exit()

    if (len(userdict)) <= 0:
        print ("There are no username details in dfc.conf. Make sure you have atleast one user verified by server.")
        sys.exit()

    return username1, password1

def verify(clientSocket, username1, password1, serverName, serverPort):			#Verify username and password
    c = 0
    try:
        usrdetails = str(username1 + ":" + password1)
        clientSocket.sendto(usrdetails.encode(), (serverName, serverPort))
        reply = clientSocket.recv(1024)
        reply = int(reply)
        if reply == 1:
            print('\n' + "Credentials verified for username: " + str(username1) + " at Server on port: " + str(serverPort))
            c = 1
        else:
            print('\n' + "Server: " + str(serverPort) + " cannot verify this user: " +str(username1) + " or Password is incorrect.")
        return c
    except:
        print("\nServer on port: " + str(serverPort) +  " is inactive or Server Details incorrect.\n")
        return c

def filebreak(filename, filesize):			#Divide file into 4 parts and return the 4 parts
    a = filesize
    b = int(a/4)
    c = int(a/2)
    d = int(a*0.75)
    with open(filename, 'rb') as rbfile:
        rbfile.seek(0)
        a1 = rbfile.read(b - 0)
        rbfile.seek(b)
        b1 = rbfile.read(c - b)
        rbfile.seek(c)
        c1 = rbfile.read(d - c)
        rbfile.seek(d)
        d1 = rbfile.read(d - filesize)

    return a1, b1, c1, d1

def serverchecker(serverName, serverPort):			#Checks if server is active or not. Returns 1 if active, returns 0 if inactive
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        clientSocket.close()
        return 1
    except:
        return 0

def getfile(filename):

    c1 = 0
    c3 = 0
    c3 = serverchecker(serverName3, serverPort3)
    c1 = serverchecker(serverName1, serverPort1)		#if server 1 and server 3 are active, ask for file parts
    if c3 == 1 and c1 == 1:
        c1 = get_part(serverName1, serverPort1)
    	time.sleep(0.5)
    if c1 == 1:
        c3 = get_part(serverName3, serverPort3)
        time.sleep(0.5)
    if c1 == 0 or c3 == 0:					#else ask server 2 and server 4 for file parts
        c2 = get_part(serverName2, serverPort2)
        time.sleep(0.5)
        c4 = get_part(serverName4, serverPort4)

    filename1 = ''

    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if ("." + filename + ".1" + ".enc") in files and ("." + filename + ".2" + ".enc") in files and ("." + filename + ".3" + ".enc") in files and ("." + filename + ".4" + ".enc") in files:
        print("All parts available. File has been reconstructed")		#check if all 4 file parts are downloaded
        f = open("recieved_" + filename + ".enc", "wb")
        fh = open("." + filename + ".1" + ".enc", "rb")				#read each part and write into single file
        content = fh.read()
        f.write(content)
        fh.close()
        fh = open("." + filename + ".2" + ".enc", "rb")
        content = fh.read()
        f.write(content)
        fh.close()
        fh = open("." + filename + ".3" + ".enc", "rb")
        content = fh.read()
        f.write(content)
        fh.close()
        fh = open("." + filename + ".4" + ".enc", "rb")
        content = fh.read()
        f.write(content)
        fh.close()

        f.close()

        filename1 = "recieved_" + filename + '.enc'
        filename2 = "recieved_" + filename

        decrypt_file(password1, filename1, filename2, chunksize=24 * 1024)	#decrypt the reconstructed file
	print("Decrypted successfully")
    else:
        print("File is incomplete. One or more parts are missing.")

    if os.path.isfile("." + filename + ".1" + '.enc'):				#delete individual parts
        os.remove("." + filename + ".1" + '.enc')
    if os.path.isfile("." + filename + ".2" + '.enc'):
        os.remove("." + filename + ".2" + '.enc')
    if os.path.isfile("." + filename + ".3" + '.enc'):
        os.remove("." + filename + ".3" + '.enc')
    if os.path.isfile("." + filename + ".4" + '.enc'):
        os.remove("." + filename + ".4" + '.enc')
    if os.path.isfile(filename1):
        os.remove(filename1)

def get_part(serverName, serverPort):

    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))				#connect to server
        clientSocket.settimeout(1)

        ab = verify(clientSocket, username1, password1, serverName, serverPort)		#verify username and password
        if ab == 1:
            message = str("Connection")
            clientSocket.sendto(message.encode(), (serverName, serverPort))
            modifiedMessage = clientSocket.recv(1024)
            print(modifiedMessage.decode() + " from Server " + str(serverPort))
            time.sleep(0.1)
            clientSocket.sendto(command, (serverName, serverPort))

            get_part_data(clientSocket, serverName, serverPort)			#get data for four file parts
            get_part_data(clientSocket, serverName, serverPort)
            get_part_data(clientSocket, serverName, serverPort)
            get_part_data(clientSocket, serverName, serverPort)
        else:
            print("Username/Password couldnt be verified. Please try again.")
	return 1
    except:
        print("\nServer at port: " + str(serverPort) + "is inactive or Server Details incorrect.\n")
	return 0

def get_part_data(clientSocket, serverName, serverPort):
    try:
        subfolder = "N/A"
        totalbytesrecv = 0
        clientSocket.sendto(filename.encode(), (serverName, serverPort))
        time.sleep(0.1)
        clientSocket.sendto(subfolder.encode(), (serverName, serverPort))
        serverfilecheck = clientSocket.recv(1024)			#check if file is present on server or not
        if serverfilecheck[:2] == "Ok":
            filesize = clientSocket.recv(1024)				#receive file size
            filename1 = clientSocket.recv(1024)				#receive file name
            filename1 = filename1 + '.enc'
            newfile = open(filename1, 'wb')
            x = clientSocket.recv(1024)
            x = int(x)
            if x < 512:
                recvdatabytes = clientSocket.recv(1024)			#receive chunks of 1024 bytes
                newfile.write(recvdatabytes)
            else:
                while totalbytesrecv < filesize:
                    recvdatabytes = clientSocket.recv(1024)
                    newfile.write(recvdatabytes)
                    filesize = int(filesize)
                    totalbytesrecv += 1024
            print("File part recieved: " + str(filename1))
        else:
            print ("\n A particular filepart does not exist at server:" + str(serverPort))
    except:
     print("Error while file transfer.")

def getfilesubfolder(filename, subfolder):
    c1 = 0
    c3 = 0
    c3 = serverchecker(serverName3, serverPort3)
    c1 = serverchecker(serverName1, serverPort1)
    if c3 == 1 and c1 == 1:
        c1 = get_part2(serverName1, serverPort1, subfolder)
    time.sleep(0.5)
    if c1 == 1:
        c3 = get_part2(serverName3, serverPort3, subfolder)
        time.sleep(0.5)
    if c1 == 0 or c3 == 0:
        c2 = get_part2(serverName2, serverPort2, subfolder)
        time.sleep(0.5)
        c4 = get_part2(serverName4, serverPort4, subfolder)

    filename1 = ''
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if ("." + filename + ".1" + '.enc') in files and ("." + filename + ".2" + '.enc') in files and (
                "." + filename + ".3" + '.enc') in files and ("." + filename + ".4" + '.enc') in files:
        print("All parts available")
        f = open("recieved_" + filename + '.enc', "wb")
        fh = open("." + filename + ".1" + '.enc', "rb")
        content = fh.read()
        f.write(content)
        fh.close()
        fh = open("." + filename + ".2" + '.enc', "rb")
        content = fh.read()
        f.write(content)
        fh.close()
        fh = open("." + filename + ".3" + '.enc', "rb")
        content = fh.read()
        f.write(content)
        fh.close()
        fh = open("." + filename + ".4" + '.enc', "rb")
        content = fh.read()
        f.write(content)
        fh.close()
        f.close()

        filename1 = "recieved_" + filename + '.enc'
        filename2 = "recieved_" + filename

        decrypt_file(password1, filename1, filename2, chunksize=24 * 1024)
	print("Decrypted suceessfully")

    else:
        print("File is incomplete. One or more parts missing.")
	
    if os.path.isfile("." + filename + ".1" + '.enc'):
        os.remove("." + filename + ".1" + '.enc')
    if os.path.isfile("." + filename + ".2" + '.enc'):
        os.remove("." + filename + ".2" + '.enc')
    if os.path.isfile("." + filename + ".3" + '.enc'):
        os.remove("." + filename + ".3" + '.enc')
    if os.path.isfile("." + filename + ".4" + '.enc'):
        os.remove("." + filename + ".4" + '.enc')
    if os.path.isfile(filename1):
        os.remove(filename1)

def get_part2(serverName, serverPort, subfolder):
    #subfolder1 = subfolder
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        clientSocket.settimeout(1)

        ab = verify(clientSocket, username1, password1, serverName, serverPort)
        if ab == 1:
            message = str("Connection")
            clientSocket.sendto(message.encode(), (serverName, serverPort))
            modifiedMessage = clientSocket.recv(1024)
            print(modifiedMessage.decode() + " from Server " + str(serverPort))
            time.sleep(0.1)
            clientSocket.sendto(command, (serverName, serverPort))

            get_part_data2(clientSocket, serverName, serverPort, subfolder)
            get_part_data2(clientSocket, serverName, serverPort, subfolder)
            get_part_data2(clientSocket, serverName, serverPort, subfolder)
            get_part_data2(clientSocket, serverName, serverPort, subfolder)
        else:
            print("Invalid Username/Password. Please try again.")
        return 1
    except:
        print("\nServer is not active or Server Details incorrect.\n" + "Inactive Server" + str(serverPort))
        return 0


def get_part_data2(clientSocket, serverName, serverPort, subfolder):
    try:
        totalbytesrecv = 0
        clientSocket.sendto(filename.encode(), (serverName, serverPort))
        time.sleep(0.1)
        clientSocket.sendto(subfolder.encode(), (serverName, serverPort))
        serverfilecheck = clientSocket.recv(1024)
        if serverfilecheck[:2] == "Ok":
            filesize = clientSocket.recv(1024)
            filename1 = clientSocket.recv(1024)
            filename1 = filename1 + '.enc'
            newfile = open(filename1, 'wb')
            x = clientSocket.recv(1024)
            x = int(x)
            if x < 512:
                recvdatabytes = clientSocket.recv(1024)
                newfile.write(recvdatabytes)
            else:
                while totalbytesrecv < filesize:
                    recvdatabytes = clientSocket.recv(1024)
                    newfile.write(recvdatabytes)
                    filesize = int(filesize)
                    totalbytesrecv += 1024
            print("File part recieved: " + str(filename1))
        else:
            print ("\nWarning! A particular filepart does not exist at server:" + str(serverPort))
    except:
        print("Error while file transfer.")


def parts_list(data):
    partlist.append(data)				#Append all data from different users to this list

def List():
    list_part(serverName1, serverPort1)			#get list data from all servers
    list_part(serverName2, serverPort2)
    list_part(serverName3, serverPort3)
    list_part(serverName4, serverPort4)
    printlist(partlist)
    #print(partlist)

def list_part(serverName, serverPort):

    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        clientSocket.settimeout(1)

        ab = verify(clientSocket, username1, password1, serverName, serverPort)		#verify username and password
        if ab ==1:
            message = str("Connection")
            clientSocket.sendto(message.encode(), (serverName, serverPort))
            modifiedMessage = clientSocket.recv(1024)
            print(modifiedMessage.decode() + " from Server " + str(serverPort))
            time.sleep(0.1)
            clientSocket.sendto(command, (serverName, serverPort))
            time.sleep(0.1)
            subfolder = "N/A"
            clientSocket.sendto(subfolder, (serverName, serverPort))
            length, clientAddress = clientSocket.recvfrom(1024)
	    #print(length)
            length = int(length)
            x = 0
            length = length -1
            while x <= length:
                data, clientAddress = clientSocket.recvfrom(1024)
                parts_list(data)						#save data from users
                x += 1
        else:
            print("Username/Password couldnt be verified. Please try again.")
    except:
        print("\nServer is not active or Server Details incorrect.\n" + "Inactive Server" + str(serverPort))


def List1(subfolder):
    list_part1(serverName1, serverPort1, subfolder)
    list_part1(serverName2, serverPort2, subfolder)
    list_part1(serverName3, serverPort3, subfolder)
    list_part1(serverName4, serverPort4, subfolder)
    printlist(partlist)

def list_part1(serverName, serverPort, subfolder):

    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        clientSocket.settimeout(1)

        ab = verify(clientSocket, username1, password1, serverName, serverPort)
        if ab == 1:
            message = str("Connection")
            clientSocket.sendto(message.encode(), (serverName, serverPort))
            modifiedMessage = clientSocket.recv(1024)
            print(modifiedMessage.decode() + " from Server " + str(serverPort))
            time.sleep(0.1)
            clientSocket.sendto(command, (serverName, serverPort))
            time.sleep(0.1)
            clientSocket.sendto(subfolder, (serverName, serverPort))
            length, clientAddress = clientSocket.recvfrom(1024)
            # try:
            length = int(length)
            x = 0
            length = length - 1
            while x <= length:
                data, clientAddress = clientSocket.recvfrom(1024)
                parts_list(data)
                x += 1
        else:
            print("Invalid Username/Password. Please try again.")
    except:
        print("\nServer is not active or Server Details incorrect.\n" + "Inactive Server" + str(serverPort))

def printlist(partlist):

    filelist = partlist
    #print(partlist)
    flist = []
    for i in filelist:
    	part = i[-2:]
	filename = i[:-2]

    	if part == ".1" or part == ".2" or part == ".3" or part == ".4":
    		file1 = filename + ".1"
    		file2 = filename + ".2"
    		file3 = filename + ".3"
    		file4 = filename + ".4"
			
    		if (file1 in filelist) and (file2 in filelist) and (file3 in filelist) and (file4 in filelist):
    			if not filename in flist:
    				flist.append(filename)
    		else:
    			if not (filename + " Incomplete") in flist:
    				flist.append(filename + " Incomplete")
    	else:
    		if not i in flist:
    				flist.append(i)
    length = len(flist)
    x = 0
    while x < length:
	#print(flist[x])
	temp = flist[x]
	temp2 = temp[0]
	if temp2 == "." :
		flist[x] = flist[x].strip(".")
	x +=1 
  
    Allfiles = '\n'.join(flist)   
    print(Allfiles)
    del partlist[:]
		
def putfile(filename):
    filepath = encrypt_file(password1, filename, outfilename=None, chunksize=64 * 1024)
    os.chdir("Encrypt")
    if os.path.isfile(filename):
        filesize = os.path.getsize(filename)
        part1, part2, part3, part4 = filebreak(filename, filesize)
        hashoffile = hashlib.md5(open(filename, "rb").read()).hexdigest()
        hashoffile = int(hashoffile, 16)				#create hash of file and use its modulo 4 to decide which server gets which parts
        hashoffile = (hashoffile % 4)
        if hashoffile == 0:
            send_part(filename, part1, 1, serverName1, serverPort1)
            send_part(filename, part2, 2, serverName1, serverPort1)
            send_part(filename, part2, 2, serverName2, serverPort2)
            send_part(filename, part3, 3, serverName2, serverPort2)
            send_part(filename, part3, 3, serverName3, serverPort3)
            send_part(filename, part4, 4, serverName3, serverPort3)
            send_part(filename, part4, 4, serverName4, serverPort4)
            send_part(filename, part1, 1, serverName4, serverPort4)
        elif hashoffile ==1:
            send_part(filename, part4, 4, serverName1, serverPort1)
            send_part(filename, part1, 1, serverName1, serverPort1)
            send_part(filename, part1, 1, serverName2, serverPort2)
            send_part(filename, part2, 2, serverName2, serverPort2)
            send_part(filename, part2, 2, serverName3, serverPort3)
            send_part(filename, part3, 3, serverName3, serverPort3)
            send_part(filename, part3, 3, serverName4, serverPort4)
            send_part(filename, part4, 4, serverName4, serverPort4)
        elif hashoffile ==2:
            send_part(filename, part3, 3, serverName1, serverPort1)
            send_part(filename, part4, 4, serverName1, serverPort1)
            send_part(filename, part4, 4, serverName2, serverPort2)
            send_part(filename, part1, 1, serverName2, serverPort2)
            send_part(filename, part1, 1, serverName3, serverPort3)
            send_part(filename, part2, 2, serverName3, serverPort3)
            send_part(filename, part2, 2, serverName4, serverPort4)
            send_part(filename, part3, 3, serverName4, serverPort4)
        elif hashoffile ==3:
            send_part(filename, part2, 2, serverName1, serverPort1)
            send_part(filename, part3, 3, serverName1, serverPort1)
            send_part(filename, part3, 3, serverName2, serverPort2)
            send_part(filename, part4, 4, serverName2, serverPort2)
            send_part(filename, part4, 4, serverName3, serverPort3)
            send_part(filename, part1, 1, serverName3, serverPort3)
            send_part(filename, part1, 1, serverName4, serverPort4)
            send_part(filename, part2, 2, serverName4, serverPort4)
        else:
            print("Error while generating hash!. Client quits.")
            sys.exit()
    else:
        print("\nError! The file name entered does not exist.")
    os.chdir("..")

def send_part(filename, partname, part , serverName, serverPort):

    filepartname = "." + filename + "." + str(part)			#construct file part name
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        clientSocket.settimeout(1)

        ab = verify(clientSocket, username1, password1, serverName, serverPort)		#verify username and password
        if ab ==1:
            message = str("Connection")
            clientSocket.sendto(message.encode(), (serverName, serverPort))
            modifiedMessage = clientSocket.recv(1024)
            print('\n' + modifiedMessage.decode() + " from Server " + str(serverPort))
            clientSocket.sendto(command, (serverName, serverPort))

            with open(filepartname, 'wb') as wbfile:
                wbfile.write(partname)
            bytestobesent = 0
            filepart = partname
            filesize = len(filepart)
            print("The size of the file is: " + str(filesize) + " B")
            time.sleep(0.1)
            clientSocket.sendto(filepartname.encode(), (serverName, serverPort))	#send file part name
            time.sleep(0.1)
	    clientSocket.sendto(str(filesize).encode(), (serverName, serverPort))	#send file size
	    time.sleep(0.1)
            subfolder = "N/A"
            clientSocket.sendto(subfolder.encode(), (serverName, serverPort))            
            serverfilecheck = clientSocket.recv(1024)
            serverfilecheck = serverfilecheck.decode()				#check if file is present on server or not
            time.sleep(0.1)
            if serverfilecheck[:3] != 'Err':
                with open(filepartname, 'rb') as rbfile:
                    x = filesize // 2
                    clientSocket.sendto(str(x), (serverName, serverPort))
                    time.sleep(0.1)
                    if x < 512:
                        atatimebytes = rbfile.read(1024)
                        clientSocket.sendto(atatimebytes, (serverName, serverPort))
                    else:
                        while bytestobesent < filesize:
                            atatimebytes = rbfile.read(1024)				#receive file in chunks of 1024 bytes
                            clientSocket.sendto(atatimebytes, (serverName, serverPort))
                            x = filesize - bytestobesent
                            if x < 1024:
                                atatimebytes = rbfile.read(x)
                                clientSocket.sendto(atatimebytes, (serverName, serverPort))
                                bytestobesent += x
                            else:
                                bytestobesent += 1024
            else:
                print("\nError: Filename already exists in server.")
            os.remove(filepartname)
        else:
            print("Username/Password couldnt be verified. Please try again.")
    except:
        print("\nServer at port: "  + str(serverPort) + "  is inactive or Server Details incorrect.\n" + "File part not sent: " + str(filepartname))

def putfilesubfolder(filename, subfolder):

    filepath = encrypt_file(password1, filename, outfilename=None, chunksize=64 * 1024)
    try:
    	os.chdir("Encrypt")
    except:	
	print("Encrypt directory not found")
    if os.path.isfile(filename):
        filesize = os.path.getsize(filename)
        # print("%"*100)
        # print(filesize)
        part1, part2, part3, part4 = filebreak(filename, filesize)
        hashoffile = hashlib.md5(open(filename, "rb").read()).hexdigest()
        hashoffile = int(hashoffile, 16)
        hashoffile = (hashoffile % 4)
        print(filename)
        if hashoffile == 0:
            send_part1(filename, part1, 1, serverName1, serverPort1, subfolder)
            send_part1(filename, part2, 2, serverName1, serverPort1, subfolder)
            send_part1(filename, part2, 2, serverName2, serverPort2, subfolder)
            send_part1(filename, part3, 3, serverName2, serverPort2, subfolder)
            send_part1(filename, part3, 3, serverName3, serverPort3, subfolder)
            send_part1(filename, part4, 4, serverName3, serverPort3, subfolder)
            send_part1(filename, part4, 4, serverName4, serverPort4, subfolder)
            send_part1(filename, part1, 1, serverName4, serverPort4, subfolder)
        elif hashoffile == 1:
            send_part1(filename, part4, 4, serverName1, serverPort1, subfolder)
            send_part1(filename, part1, 1, serverName1, serverPort1, subfolder)
            send_part1(filename, part1, 1, serverName2, serverPort2, subfolder)
            send_part1(filename, part2, 2, serverName2, serverPort2, subfolder)
            send_part1(filename, part2, 2, serverName3, serverPort3, subfolder)
            send_part1(filename, part3, 3, serverName3, serverPort3, subfolder)
            send_part1(filename, part3, 3, serverName4, serverPort4, subfolder)
            send_part1(filename, part4, 4, serverName4, serverPort4, subfolder)
        elif hashoffile == 2:
            send_part1(filename, part3, 3, serverName1, serverPort1, subfolder)
            send_part1(filename, part4, 4, serverName1, serverPort1, subfolder)
            send_part1(filename, part4, 4, serverName2, serverPort2, subfolder)
            send_part1(filename, part1, 1, serverName2, serverPort2, subfolder)
            send_part1(filename, part1, 1, serverName3, serverPort3, subfolder)
            send_part1(filename, part2, 2, serverName3, serverPort3, subfolder)
            send_part1(filename, part2, 2, serverName4, serverPort4, subfolder)
            send_part1(filename, part3, 3, serverName4, serverPort4, subfolder)
        elif hashoffile == 3:
            send_part1(filename, part2, 2, serverName1, serverPort1, subfolder)
            send_part1(filename, part3, 3, serverName1, serverPort1, subfolder)
            send_part1(filename, part3, 3, serverName2, serverPort2, subfolder)
            send_part1(filename, part4, 4, serverName2, serverPort2, subfolder)
            send_part1(filename, part4, 4, serverName3, serverPort3, subfolder)
            send_part1(filename, part1, 1, serverName3, serverPort3, subfolder)
            send_part1(filename, part1, 1, serverName4, serverPort4, subfolder)
            send_part1(filename, part2, 2, serverName4, serverPort4, subfolder)
        else:
            print("Error while generating hash!. System will shutdown.")
            sys.exit()
    else:
        print("\nError! The file name entered does not exist.")
    os.chdir("..")

def send_part1(filename, partname, part, serverName, serverPort, subfolder):

    infile = filename + '.enc'

    filepartname = "." + filename + "." + str(part)
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        clientSocket.settimeout(1)

        ab = verify(clientSocket, username1, password1, serverName, serverPort)
        if ab == 1:
            message = str("Connection")
            clientSocket.sendto(message.encode(), (serverName, serverPort))
            modifiedMessage = clientSocket.recv(1024)
            print('\n' + modifiedMessage.decode() + " from Server " + str(serverPort))
            clientSocket.sendto(command, (serverName, serverPort))

            with open(filepartname, 'wb') as wbfile:
                wbfile.write(partname)
            bytestobesent = 0
            filepart = partname
            filesize = len(filepart)
            print("The size of the files is: " + str(filesize) + " Bytes")
            time.sleep(0.1)
            clientSocket.sendto(filepartname.encode(), (serverName, serverPort))
            time.sleep(0.1)
            clientSocket.sendto(str(filesize).encode(), (serverName, serverPort))
            time.sleep(0.1)
            clientSocket.sendto(subfolder, (serverName, serverPort))
            serverfilecheck = clientSocket.recv(1024)
            serverfilecheck = serverfilecheck.decode()
            time.sleep(0.1)
            if serverfilecheck[:3] != 'Err':
                with open(filepartname, 'rb') as rbfile:
                    x = filesize // 2
                    clientSocket.sendto(str(x), (serverName, serverPort))
                    time.sleep(0.1)
                    if x < 512:
                        atatimebytes = rbfile.read(1024)
                        clientSocket.sendto(atatimebytes, (serverName, serverPort))
                    else:
                        while bytestobesent < filesize:
                            atatimebytes = rbfile.read(1024)
                            clientSocket.sendto(atatimebytes, (serverName, serverPort))
                            x = filesize - bytestobesent
                            if x < 1024:
                                atatimebytes = rbfile.read(x)
                                clientSocket.sendto(atatimebytes, (serverName, serverPort))
                                bytestobesent += x
                            else:
                                bytestobesent += 1024
            else:
                print("\nError! Filename already exists in server. Try changing filename.")
            os.remove(filepartname)
        else:
            print("Invalid Username/Password. Please try again.")
    except:
        print("\nServer is not active or Server Details incorrect.\n" + "Inactive Server" + str(
            serverPort) + "The file has not been sent.\n" + "File part not sent: " + str(filepartname))

if __name__ == '__main__':

    serverName1 = ''			#defining global variables
    serverName2 = ''
    serverName3 = ''
    serverName4 = ''
    serverPort1 = ''
    serverPort2 = ''
    serverPort3 = ''
    serverPort4 = ''
    username = ''
    password = ''
    username1 = ''
    password1 = ''
    userdict = []
    servchkdict = []
    partlist = []

    if os.path.isfile("dfcconf.txt"):
	    with open("dfcconf.txt", 'r') as conffile:			#opening conf file and reading contents
		conffile = iter(conffile)
		for line in conffile:
		    if "DFS1" in line:
		        try:
		            line = line.split(" ")
		            line = line[2].split(":")
		            serverName1 = line[0]
		            serverPort1 = int(line[1])
		        except:
		            serverName1 = '127.0.0.1'
		            serverPort1 = 10001
		            print("File formating has been changed. The DFS1 server default IP = 127.0.0.1 and default port = 10001")
		    elif "DFS2" in line:
		        try:
		            line = line.split(" ")
		            line = line[2].split(":")
		            serverName2 = line[0]
		            serverPort2 = int(line[1])
		        except:
		            serverName2 = '127.0.0.1'
		            serverPort2 = 10002
		            print("File formating has been changed. The DFS1 server default IP = 127.0.0.1 and default port = 10002")
		    elif "DFS3" in line:
		        try:
		            line = line.split(" ")
		            line = line[2].split(":")
		            serverName3 = line[0]
		            serverPort3 = int(line[1])
		        except:
		            serverName3 = '127.0.0.1'
		            serverPort3 = 10003
		            print("File formating has been changed. The DFS1 server default IP = 127.0.0.1 and default port = 10003")
		    elif "DFS4" in line:
		        try:
		            line = line.split(" ")
		            line = line[2].split(":")
		            serverName4 = line[0]
		            serverPort4 = int(line[1])
		        except:
		            serverName4 = '127.0.0.1'
		            serverPort4 = 10004
		            print("File formating has been changed. The DFS1 server default IP = 127.0.0.1 and default port = 10004")
		    elif "Username" in line:
		        try:
		            line1 = line.split(" ")
		            line2 = line1[1].splitlines()
		            username = line2[0]
		            line = next(conffile)
		            if "Password" in line:
		                line = line.split(" ")
		                line3 = line[1].splitlines()
		                password = line3[0]
		            newrecord = {}
		            newrecord[username] = password
		            userdict.append(newrecord)
		        except:
		            print ("The formating of dfc.conf has been changed. Username and Password details have not been read. Please use the previous working formating.")
		            sys.exit()
    else:
	    print("Conf file does not exist. Client quits.")
	    sys.exit()

    print (username1)
    print (password1)
    username1, password1 = checkuserdict(username1, password1)		#checking user dictionary for no. of users

    while True:
        usrinput = menu()
	try:
        	command = usrinput[0]	

		if command == "GET":
		    try:
		        filename = usrinput[1]
		        subfolder = usrinput[2]
		        getfilesubfolder(filename, subfolder)
		    except:
		        print("No sub folder mentioned")
		        getfile(filename)
		elif command == "PUT":
		    try:
		        filename = usrinput[1]
		        subfolder = usrinput[2]
		        putfilesubfolder(filename, subfolder)
		    except:
		        print("No sub folder mentioned")
		        putfile(filename)
		elif command == "List":
		    try:
		        subfolder = usrinput[1]
		        List1(subfolder)
		    except:
		        print("No sub folder mentioned")
		        List()
		else:
		    print("\nErroneous command. Use exact command name and syntax mentioned in the menu.")

	except:
		print("Erroneous command\n")
