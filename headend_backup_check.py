#!/usr/bin/env python

#+-----------------------------------------------------------------------+
#| File Name: headend_backup_check.py                                    |
#|                                                                       |
#| Description: Check dacsupport for new headend backup files            |
#|                                                                       |
#+-----------------------------------------------------------------------+
#| Authors: Brian Spaulding                                              |
#+-----------------------------------------------------------------------+
#| Date: 2016-03-16                                                      |
#+-----------------------------------------------------------------------+

import paramiko
import subprocess
from threading import Thread

directories = ['cast','casmr','dac6000','sdm']
threads = []

####################################################
#       Build function to check directories        #
####################################################

def backupcheck(directory):
        command = "find /backup/%s/* -maxdepth 1 -type f -mtime -1" % directory
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect( 'REDACTED', username='REDACTED', password='REDACTED', look_for_keys=False)
        stdin, stdout, stderr = ssh.exec_command(command)
        warning_message = "Backup failed for %s (no new files in /backup/%s)" % (directory,directory)
        clear_message   = "Backup successful for %s (new files found in /backup/%s)" % (directory,directory)
        output = stdout.read()
        if "backup" not in output:
                subprocess.call(['zensendevent', '-d', 'dacsupport', '-y', directory, '-p', 'Backup', '-s', 'Warning', '-c', '/Status/Backup', '-k', directory, warning_message])
        elif "backup" in output:
                subprocess.call(['zensendevent', '-d', 'dacsupport', '-y', directory, '-p', 'Backup', '-s', 'Clear', '-c', '/Status/Backup', '-k', directory, clear_message])
        ssh.close()

####################################################
#  Thread each SSH connection and generate events  #
####################################################

t1 = Thread(target=backupcheck, args=(directories[0],))
t2 = Thread(target=backupcheck, args=(directories[1],))
t3 = Thread(target=backupcheck, args=(directories[2],))
t4 = Thread(target=backupcheck, args=(directories[3],))
threads.extend([t1, t2, t3, t4])

for t in threads:
        t.start()

for t in threads:
        t.join()
