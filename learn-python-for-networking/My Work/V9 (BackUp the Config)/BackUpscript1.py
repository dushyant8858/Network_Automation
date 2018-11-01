
#!/usr/bin/evn python

import getpass
import sys
import telnetlib


user = raw_input("Enter your telnet username: ")
password = getpass.getpass()



f = open("ipTableOfSwitch")

for line in f:
    print("******** Backing up the configuration of " + str(line).strip() + " Switch ********")

    HOST = line
    tn = telnetlib.Telnet(HOST)

    tn.read_until("Username: ")
    tn.write(user + "\n")
    if password:
        tn.read_until("Password: ")
        tn.write(password + "\n")

    tn.write("en\n")
    tn.write("cisco\n")

    tn.write("terminal length 0\n")
    tn.write("sh run\n")
    tn.write("exit\n")

    readoutput = tn.read_all()
    saveoutput = open("Switch " +  str(HOST).strip(), "w")
    saveoutput.write(readoutput)
    saveoutput.close
    print("******** DONE copying the configiration of " + str(HOST).strip()+ " Switch ********")