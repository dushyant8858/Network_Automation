#!/usr/bin/evn python

import getpass
import sys
import telnetlib


user = raw_input("Enter your telnet username: ")
password = getpass.getpass()



f = open("ipTableOfSwitch")

for line in f:
    print("******** Configuring the " + str(line).strip() + " Switch ********")

    HOST = line
    tn = telnetlib.Telnet(HOST)

    tn.read_until("Username: ")
    tn.write(user + "\n")
    if password:
        tn.read_until("Password: ")
        tn.write(password + "\n")

    tn.write("en\n")
    tn.write("cisco\n")

    tn.write("config t\n")


    for n in range (2,4):
    
        tn.write("vlan " + str(n) + "\n")
        tn.write("name Python_vlan_" + str(n) + "\n")

    tn.write("end\n")
    tn.write("wr\n")
    tn.write("exit\n")

    print tn.read_all()
