import telnetlib
import re
import sys
import time
import os

def find_hostname(config):
#Find hostname in configuration file
	return config.split("#".encode(),1)[0]

def host_is_up(ipv4):
#Check ping to host, if host is up response will be 0
	print("---------------------------------------")
	print("Check the availability of device %s" %ipv4)
	response = os.system("ping -n 2 " + ipv4)
	return response == 0

def check_ipv4_validity(ip_address):
	a = ip_address.split(".")
	return (len(a)==4) and (1 <= int(a[0]) <= 255) and (0 <= int(a[1]) <= 255) and (0 <= int(a[2]) <= 255) and (0 <= int(a[3]) <= 255)

	
#Define the input file, inlcuding ip, username and password file
switch_file = "input02.txt"
#Open switch selected file for reading
selected_switch_file = open(switch_file, 'r')
			
#Starting from the beginning of the file
selected_switch_file.seek(0)

#Switch file must contain IP address of TFTP Server in first line
#Switch file must contain intermediate device in second line , included IP, username and password
#Switch file must include IP USERNAME PASSWORD HOSTNAME from line no.3, for ex:
#192.168.1.10 admin password switch01

#read TFTP Server
tftp_server = selected_switch_file.readline()
tftp_server = tftp_server.rstrip("\n")
tftp_server = tftp_server.rstrip(" ")
print("TFTP Server is %s" % tftp_server)

#read intermediate device 
temp = selected_switch_file.readline().split(" ")
#print('temp is', temp)
ipv4 = temp[0].rstrip(" ")
username = temp[1]
password = temp[2].rstrip("\n")

print("=======================================")
print('intermediate switch\'s IP is', ipv4)

#Logging into device (logging in to intermediate device first)
TELNET_PORT = 23
TELNET_TIMEOUT = 5
READ_TIMEOUT = 5
print("---------------------------------------")
print("Started logging into intermediate switch %s" % ipv4)
connection = telnetlib.Telnet(ipv4, TELNET_PORT, TELNET_TIMEOUT)
time.sleep(3)
#Entering global config mode
connection.write((username + "\n").encode('ascii'))
time.sleep(3)
connection.write((password + "\n").encode('ascii'))
time.sleep(3)
connection.write("enable\n".encode('ascii'))
time.sleep(3)

for each_line in selected_switch_file.readlines():
	temp = each_line.split(" ")
	ipv4 = temp[0].rstrip(" ")
	username = temp[1]
	password = temp[2].rstrip("\n")
	hostname = temp[3].rstrip("\n")        
  
	print("===============================================================================")
	print('Start working with device\'s IP ', ipv4)
	print('Username is', username)
	print('Hostname is', hostname)

	if check_ipv4_validity(ipv4) and host_is_up(ipv4):
	   print("---------------------------------------")
	   print("Started logging into Switch %s" % ipv4)
	   connection.write(("telnet " + ipv4 + "\n").encode('ascii'))
	   time.sleep(3)
	   connection.write((username + "\n").encode('ascii'))
	   time.sleep(3)
	   connection.write((password + "\n").encode('ascii'))
	   time.sleep(3)
	   connection.write("enable\n".encode('ascii'))
	   time.sleep(3)
	   command = "copy running-config tftp://"+tftp_server+"/"+hostname+"\n"
	   #print("excute command: ", command)
	   connection.write(command.encode('ascii'))
	   time.sleep(1)
	   connection.write("\n".encode('ascii'))
	   time.sleep(1)
	   connection.write("\n".encode('ascii'))
	   time.sleep(3)
	   connection.write("exit\n".encode('ascii'))
	   connection.write("exit\n".encode('ascii'))
	   print("Saved configuration file of device %s" % hostname)
	   print("===============================================================================")
	   output = connection.read_very_eager()
	   print(output)
	else:
		print("This ip address %s is invalid or not available" % ipv4)
		print("===============================================================================")

connection.close()
#Closing the switch file
selected_switch_file.close()
