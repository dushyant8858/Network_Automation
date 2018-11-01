# root@UbuntuDockerGuest-1:~# cat pythonS1script1.py 

#!/usr/bin/evn python

import getpass
import sys
import telnetlib

HOST = "192.168.248.129"
user = raw_input("Enter your telnet username: ")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until("Username: ")
tn.write(user + "\n")
if password:
    tn.read_until("Password: ")
    tn.write(password + "\n")

tn.write("en\n")
tn.write("cisco\n")

tn.write("config t\n")


for n in range (2,10):
    
    tn.write("vlan " + str(n) + "\n")
    tn.write("name Python_vlan_" + str(n) + "\n")


tn.write("end\n")
tn.write("exit\n")

print tn.read_all()