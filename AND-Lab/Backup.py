import getpass
import telnetlib

print "******You are now Backing up CISCO and ARISTA router******"

user = raw_input ("Enter your username of CISCO and ARISTA:")
password = getpass.getpass()

HOST =("192.168.13.144","192.168.13.145","192.168.13.146")

for i in HOST:


