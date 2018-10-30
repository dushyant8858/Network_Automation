import socket
import sys
if len(sys.argv) <= 1: 
    print 'Usage: "python S.py port"\n[port : It is the port of the Proxy Server'
    sys.exit(2)

# Server socket created, bound and starting to listen
Serv_Port = int(sys.argv[1]) # sys.argv[1] is the port number entered by the user
Serv_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.socket function creates a socket.

# Prepare a server socket
print "starting server ...."
Serv_Sock.bind(('', Serv_Port))
Serv_Sock.listen(5)


def caching_object(splitMessage, Cli_Sock):
    #this method is responsible for caching
    Req_Type = splitMessage[0]
    Req_path = splitMessage[1]
    Req_path = Req_path[1:]
    print "Request is ", Req_Type, " to URL : ", Req_path

    #Searching available cache if file exists
    file_to_use = "/" + Req_path
    print file_to_use
    try:
        file = open(file_to_use[1:], "r")
        data = file.readlines()
        print "File Present in Cache\n"

        #Proxy Server Will Send A Response Message
        #Cli_Sock.send("HTTP/1.0 200 OK\r\n")
        #Cli_Sock.send("Content-Type:text/html")
        #Cli_Sock.send("\r\n")


        #Proxy Server Will Send Data
        for i in range(0, len(data)):
            print (data[i])
            Cli_Sock.send(data[i])
        print "Reading file from cache\n"

    except IOError:
        print "File Doesn't Exists In Cache\n fetching file from server \n creating cache"
        serv_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_name = Req_path
        print "HOST NAME:", host_name
        try:
            serv_proxy.connect((host_name, 80))
            print 'Socket connected to port 80 of the host'
            fileobj = serv_proxy.makefile('r', 0)
            fileobj.write("GET " + "http://" + Req_path + " HTTP/1.0\n\n")

            # Read the response into buffer
            buffer = fileobj.readlines()

            # Create a new file in the cache for the requested file.
            # Also send the response in the buffer to client socket
            # and the corresponding file in the cache
            tmpFile = open("./" + Req_path, "wb")
            for i in range(0, len(buffer)):
                tmpFile.write(buffer[i])
                Cli_Sock.send(buffer[i])
        except:
            print 'Illegal Request'

    Cli_Sock.close()
while True:
    # Start receiving data from the client
    print 'Initiating server... \n Accepting connection\n'
    Cli_Sock, addr = Serv_Sock.accept() # Accept a connection from client
    #print addr

    print ' connection received from: ', addr
    message = Cli_Sock.recv(1024) #Recieves data from Socket

    splitMessage = message.split()
    if len(splitMessage) <= 1:
        continue

    caching_object(splitMessage, Cli_Sock)

