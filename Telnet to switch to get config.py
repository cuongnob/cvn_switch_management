#Open telnet connection to devices

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
    print("------------------------------------------------------------------------------")
    print("Check the availability of device %s" %ipv4)
    response = os.system("ping -c 1 " + ipv4)
    return response == 0

def check_ipv4_validity(ip_address):
    a = ip_address.split(".")
    return (len(a)==4) and (1 <= int(a[0]) <= 255) and (0 <= int(a[1]) <= 255) and (0 <= int(a[2]) <= 255) and (0 <= int(a[3]) <= 255)

def open_telnet_to_get_config(switch_file):
    #Change exception message
    try:
        #Define telnet parameters

        TELNET_PORT = 23
        TELNET_TIMEOUT = 5
        READ_TIMEOUT = 5

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
            print("------------------------------------------------------------------------------")
            print("Started logging into Switch %s" % ipv4)
            #Logging into device
            connection = telnetlib.Telnet(ipv4, TELNET_PORT, TELNET_TIMEOUT)
            time.sleep(3)
            connection.write(username + "\n")
            time.sleep(3)
            connection.write(password + "\n")
            time.sleep(3)
            connection.write("enable\n")
            time.sleep(1)
            #Setting terminal length for entire output - no pagination
            connection.write("terminal length 0\n")
            time.sleep(1)
            #Setting terminal length for AT 8000S device
            connection.write("terminal datadump\n")
            time.sleep(1)   
            connection.write("show running-config\n")
            #depend on the length of configuration file
            time.sleep(40)
            output=connection.read_very_eager()
            #Cut out text before show running command
            output = output.split("show running-config")[1]
            #Write configuration to text file
            hostname = find_hostname(output)
            newfile = open(hostname,"w")
            output = output.split("show running-config")[1]
            newfile.write(output)
            newfile.close
            print("Saved configuration file of device %s" % hostname)
            print("------------------------------------------------------------------------------")
            connection.write("exit\n")
            time.sleep(2)
        #Closing the switch file
        selected_switch_file.close()
         
        #Closing the connection
        connection.close()
        
    except IOError:
        print("Input parameter error! Please check username, password and file name.")
		
#Calling the Telnet function
#switch_file = sys.argv[1]
open_telnet_to_get_config(switch_file)