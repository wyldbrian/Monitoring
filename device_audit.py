#!/usr/bin/env zendmd
#
for device in dmd.Devices.getSubDevicesGen():
    print "%s,%s,%s,%s,%s,%s,%s,%s,%s" % (device.snmpSysName, device.manageIp, device.getLocationName(), device.rackSlot, device.zSnmpVer, device.zSnmpCommunity, device.getProdState(), device.getPriority(), device.sysUpTime())
