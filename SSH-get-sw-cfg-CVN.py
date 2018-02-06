#Open SSHv2 connection to devices
import paramiko
import re
import sys
import time
import os

def find_hostname(config):
#Find hostname in configuration file
    line = config.split("hostname ")[1]
    hostname = line.split("\n",1)[0]
    hostname = hostname[:-1]
    return hostname

def host_is_up(ipv4):
#Check ping to host, if host is up response will be 0
    print "------------------------------------------------------------------------------"
    print "Check the availability of device %s" %ipv4
    response = os.system("ping -c 1 " + ipv4)
    return response == 0

def check_ipv4_validity(ip_address):
    a = ip_address.split(".")
    return (len(a)==4) and (1 <= int(a[0]) <= 255) and (0 <= int(a[1]) <= 255) and (0 <= int(a[2]) <= 255) and (0 <= int(a[3]) <= 255)

def excute_command(ip,username,password,switch_file):
    #This fuction will firstly SSH to Fortigate device, then from this device telnet to other switch to get configuration 
    try:
        #Logging into device (logging in to intermediate device (Fortigate) first)
        print "------------------------------------------------------------------------------"
        print "Started logging into Fortigate device %s" % ip
        session = paramiko.SSHClient()

        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
        session.connect(ip, username = username, password = password, timeout = 5)
        
        connection = session.invoke_shell()
        
        #Entering global config mode
        connection.send("\n")
        #connection.send("enable\n")
        time.sleep(1)
        
              
        #Open switch selected file for reading
        selected_switch_file = open(switch_file, 'r')
            
        #Starting from the beginning of the file
        selected_switch_file.seek(0)
        
        #telnet to each switch in the file
        for each_line in selected_switch_file.readlines():
            temp = each_line.split(" ")
            ipv4 = temp[0]
            username = temp[1]
            password = temp[2].rstrip("\n")
            print "------------------------------------------------------------------------------"
            print "Started logging into Switch %s" % ipv4
            connection.send("execute telnet %s \n" % ipv4)
            time.sleep(2)
            connection.send(username+"\n")
            time.sleep(2)
            connection.send(password+"\n")
            time.sleep(2)
            #For Cisco device and AT X610
            connection.send("terminal length 0\n")
            #For AT 8000S device
            connection.send("terminal datadump\n")
            time.sleep(2)
            connection.send("show running-config\n")
            #depend on the length of configuration file
            time.sleep(40)
            output = connection.recv(65535)
            #Write configuration to text file
            hostname = find_hostname(output)
            newfile = open(hostname,"w")
            output = output.split("show running-config")[1]
            newfile.write(output)
            newfile.close
            print "Saved configuration file of device %s" % hostname
            print "------------------------------------------------------------------------------"
            connection.send("exit\n")
            time.sleep(2)
        #Closing the switch file
        selected_switch_file.close()
            
        #Closing the connection
        session.close()
     
    except paramiko.AuthenticationException:
        print "* Invalid username or password. \n* Please check the username/password file or the device configuration!"
        print "* Closing program...\n"
    except paramiko.SSHException:
        print "* The device is not available"
        
#Define the input file, inlcuding ip, username and password of FW in firewall file, list of switch in switch file
#Must give argrument (file name) to command line
firewall_input = sys.argv[1]
switch_file = sys.argv[2]
        
#Open the input file
selected_firewall_input = open(firewall_input, 'r')
selected_firewall_input.seek(0)

#Getting each line in the input file to process
for each_line in selected_firewall_input.readlines():
    temp = each_line.split(" ")
    ipv4 = temp[0]
    username = temp[1]
    password = temp[2].rstrip("\n")
    
    #print 'IP is', ipv4
    #print 'Username is', username
    #print 'Password is', password
    
    if check_ipv4_validity(ipv4) and host_is_up(ipv4):
       excute_command(ipv4,username,password,switch_file) 
    else:
        print "This ip address %s is invalid or not available" % ipv4
        print "------------------------------------------------------------------------------"
       
#Closing the input file
selected_firewall_input.close()
