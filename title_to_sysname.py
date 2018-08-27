#!/usr/bin/env zendmd
#
#The purpose of this script is to automatically update device Titles and IDs in the event a devices SysName Changes
#A few times a day this script will go through and check SNMP SysName on all devices and rename the device with its SysName
#If the modeler goes through and finds a new SNMP SysName (every 8 hours) this script will come in behind that and update the Title/ID fields
#
GO = True
log = open('/tmp/device_name_changes.txt', "w")
for d in dmd.Devices.getSubDevices():
        if d.id != d.snmpSysName or d.title != d.snmpSysName:
                newid = d.snmpSysName
                print >>log, "Device ID: " + d.id
                print >>log, "Device Title: " + d.title
                print >>log, "Device SysName: " + d.snmpSysName
                print >>log, "Device IP: " + d.manageIp
                print >>log, "New Device Info: " + newid
                if GO == True:
                        if d.id == newid and d.title == newid:
                                print >>log, "Change not needed."
                        elif len(newid) > 0:
                                d.setTitle(newid)
                                print >>log, "Changed Title to: " + newid
                                d.renameDevice(newid)
                                print >>log, "Changed ID to: " + newid
                                commit()
                        else:
                                print >>log, "SysName not set. No changes made."
                print >>log, '-'*40

