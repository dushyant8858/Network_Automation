import getpass
import sys
import telnetlib

HOST = "192.168.13.146"
user = raw_input ("Enter your username:")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST,timeout=5)


tn.read_until("login:")
tn.write(user+ "\n")

if password:

    tn.read_until("Password:")
    tn.write(password+"\n")

tn.write("configure\n")
tn.write("set int lo0 unit 0 family inet address 1.1.1.1/32\n")
tn.write("commit and-quit\n")
tn.write("exit\n")

print tn.read_all()
