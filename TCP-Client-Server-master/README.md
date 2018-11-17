# README:

python version: 2.7.14

To run the code:

$ cd tcpserver 

$ python tcpserver6.py


1. Logger, global variables, class objects are initialized in main method.

2. Class Config reads the .conf file and extracts contents from it.

3.  Class server creates a socket and binds it to ip and port no.

4. The accept_req function waits on new connections. If there’s a connection, it spawns a new thread.

5. Class multiple runs the thread. It initializes a timer and accepts request from client during that time.

6. The sendfile() function serves the file transfer. Error handling is managed inside this function. It checks whether method is POST or GET and then proceeds.

If method is post, then check whether index file is requested or regular file.
Open the requested file, attach the postdata to it and send the file. If file does not exist or file type is not supported then  send errors.

Similar logic is followed for GET method. No data has to be attached in this case.

If any other method is requested then send error stating that method type is not implemented.

If method name is wrong, then send error.

If favicon is requesed then ignore it
