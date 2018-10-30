import getpass
import sys
import telnetlib

HOST =("192.168.13.144","192.168.13.145","192.168.13.146")

print "******You are now Configuring CISCO and ARISTA router******"
user = raw_input ("Enter your username of CISCO and ARISTA:")
password = getpass.getpass()


for i in HOST:

    if i is "192.168.13.144":
        tn = telnetlib.Telnet(HOST[0],timeout=5)
        tn.read_until("Username:")
        tn.write(user+ "\n")

        if password:

            tn.read_until("Password:")
            tn.write(password+"\n")
        tn.write("config t\n")
        tn.write("int lo1\n")
        tn.write("ip addr 2.2.2.2 255.255.255.255\n")
        tn.write("end\n")
        tn.write("exit\n")

        print tn.read_all()



    elif i is "192.168.13.145":

        tn = telnetlib.Telnet(HOST[1],timeout=5)
        tn.read_until("Username:")
        tn.write(user+ "\n")

        if password:

            tn.read_until("Password:")
            tn.write(password+"\n")

        tn.write("en\n")
        tn.write("conf t\n")
        tn.write("int lo1\n")
        tn.write("ip addr 2.2.2.2  255.255.255.255\n")
        tn.write("end\n")
        tn.write("exit\n")
        print tn.read_all()


    elif i is "192.168.13.146":

        print "******You are now Configuring Juniper router******"
        user = raw_input ("Enter your Juniper username:")
        passJUNOS = getpass.getpass()

        tn = telnetlib.Telnet(HOST[2],timeout=5)

        tn.read_until("login:")
        tn.write(user+ "\n")

        if passJUNOS:
            tn.read_until("Password:")
            tn.write(passJUNOS+"\n")

        tn.write("configure\n")
        tn.write("set int lo0 unit 0 family inet address 2.2.2.2/32\n")
        tn.write("commit and-quit\n")
        tn.write("exit\n")
    print tn.read_all()
