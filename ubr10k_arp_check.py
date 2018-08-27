#!/usr/bin/env python

#+-----------------------------------------------------------------------+
#| File Name: ubr10k_arp_check.py                                        |
#+-----------------------------------------------------------------------+
#| Description: This script checks UBR10K arp tables for abusive devices |
#+-----------------------------------------------------------------------+
#| Usage: pass UBR10K IP addresses to the script for processing          |
#+-----------------------------------------------------------------------+
#| Authors: Brian Spaulding                                              |
#+-----------------------------------------------------------------------+
#| Date: 2016-04-15                                                      |
#+-----------------------------------------------------------------------+
#| Version: 1.1.2                                                        |
#+-----------------------------------------------------------------------+

####################################################
#             Import necessary modules             #
####################################################

import paramiko
import subprocess
import MySQLdb
import sys
import os
import socket
from threading import Thread
from collections import Counter

####################################################
#            Enable or disable debugging           #
####################################################

DEBUG = False

####################################################
#         Pull active alarms from MySQL DB         #
####################################################

db = MySQLdb.connect("localhost","REDACTED","REDACTED","zenoss_zep")
cursor = db.cursor()
cursor.execute("SELECT event_key FROM v_event_summary WHERE event_class = '/Cable Plant/IP Abuse' AND status_id in ('0','1')")
rows = cursor.fetchall()
db.close()

alarms = []
for row in rows:
        alarms.append(row[0])

if DEBUG:
        for alarm in alarms:
                print "Mac address %s has an active alarm" % alarm

####################################################
#       Confirm that each device is a UBR10K       #
####################################################

ubr_ips = []
devnull = open(os.devnull, 'w')
for ip in sys.argv:
        try:
                check_model = str(subprocess.check_output(['snmpget', '-v2c', '-ccaution', ip, 'sysDescr.0'], stderr=devnull))
                if "UBR10K" in check_model:
                        ubr_ips.append(ip)
                else:
                        raise Exception()
        except:
                if ip not in sys.argv[0]:
                        print "%s is not a valid UBR10K IP address or hostname" % ip
                        pass

if DEBUG:
        for ip in ubr_ips:
                name = str(subprocess.check_output(['snmpget', '-v2c', '-ccaution', ip, 'sysName.0'])).rsplit(None, 1)[-1]
                print "Device %s(%s) is ready for processing" % (name, ip)

####################################################
#       Build function to gather arp tables        #
####################################################

def ipabusealert(ip):
        macs = []
        name = str(subprocess.check_output(['snmpget', '-v2c', '-ccaution', ip, 'sysName.0'])).rsplit(None, 1)[-1]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
                ssh.connect( ip, username='noc_monitor', password='49bbb31ba0dfc6a996b97cae51d98f43', look_for_keys=False, timeout=2)
        except:
                message = "Unable to SSH into %s to gather arp table" % name
                subprocess.call(['zensendevent', '-d', name, '-y', 'ssh_error', '-p', 'SSH Error', '-s', 'Info', '-c', '/Cable Plant/', '-k', 'ssh_error', message])
                sys.exit(0)
        stdin, stdout, stderr = ssh.exec_command("show arp")
        for line in stdout:
                if "Bundle" in line and not " 10." in line and not ".1 " in line:
                        try:
                                macs.append(line.split()[3].strip())
                        except IndexError:
                                pass
        ssh.close()
        counter_mac = Counter(macs)
        for mac in counter_mac:
                if counter_mac[mac] >= 10:
                        message = "Customer mac address %s has %s entries in the arp table" % (mac, counter_mac[mac])
                        subprocess.call(['zensendevent', '-d', name, '-y', mac, '-p', mac, '-s', 'Warning', '-c', '/Cable Plant/IP Abuse', '-k', mac, message])
                elif mac in alarms:
                        message = "Customer mac address %s has %s entries in the arp table" % (mac, counter_mac[mac])
                        subprocess.call(['zensendevent', '-d', name, '-y', mac, '-p', mac, '-s', 'Clear', '-c', '/Cable Plant/IP Abuse', '-k', mac, message])
                        alarms.remove(mac)
        for mac in alarms:
                if mac not in counter_mac:
                        message = "Customer mac address %s has 0 entries in the arp table" % mac
                        subprocess.call(['zensendevent', '-d', name, '-y', mac, '-p', mac, '-s', 'Clear', '-c', '/Cable Plant/IP Abuse', '-k', mac, message])


####################################################
#     Call threaded function for each device       #
####################################################

threads = []

for ip in ubr_ips:
        t = Thread(target=ipabusealert, args=(ip,))
        threads.append(t)
        t.start()

for t in threads:
        t.join()
