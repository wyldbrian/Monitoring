#!/bin/bash
#
# This script goes through and checks specified IP addresses for listings on various blacklists. Upon finding that an IP is listed it will send a Zenoss event.
#
# Start by creating an array of the blacklists we want checked. Simply add a blacklist to the list if you want it checked.
#
BLISTS="
    dnsbl.sorbs.net
    spam.dnsbl.sorbs.net
    bl.spamcop.net
    sbl.spamhaus.org
    dnsbl-1.uceprotect.net
    spam.spamrats.com
    b.barracudacentral.org
    access.redhawk.org
    black.junkemailfilter.com
    ips.backscatterer.org
    bl.mailspike.net
"
# Another test
# Next we create an additional Array that includes the servers we want to check. This array includes various formats for the server name and IP for usage in the events and checks.
#
SERVERS="
        146.160.228.216,216.228.160.146,c650-1.noc.bendbroadband.com,c650
        147.160.228.216,216.228.160.147,c670-2.noc.bendbroadband.com,c670
        244.160.228.216,216.228.160.244,fw-noc1-5500.bendcable.net,noc1-5500
        254.160.228.216,216.228.160.254,fw-noc1-5500.bendcable.net,noc1-5500
	252.160.228.216,216.228.160.252,PORTAL,PORTAL
        140.160.228.216,216.228.160.140,s1mq0,s1mq0
        141.160.228.216,216.228.160.141,s1mq0,s1mq0
        142.160.228.216,216.228.160.142,s1mq0,s1mq0
        143.160.228.216,216.228.160.143,s1mq0,s1mq0
        144.160.228.216,216.228.160.144,s1mq0,s1mq0
"
#
# Now that we have our arrays created we begin looping through each server with each blacklist. We use awk to strip out portions of the array as we go.
#
for SERV in ${SERVERS}; do
        for BL in ${BLISTS}; do
                if [[ $(host $(echo ${SERV} | awk -F, '{print $1}').${BL}) == *NXDOMAIN* ]]; then
                        zensendevent -d $(echo ${SERV} | awk -F, '{print $3}') -y ${BL}_$(echo ${SERV} | awk -F, '{print $4}') -p "Listed IP: $(echo ${SERV} | awk -F, '{print $2}')" -s Clear -c "/App/Email/Blacklist" -k ${BL}_$(echo ${SERV} | awk -F, '{print $4}') "No longer blacklisted on ${BL}"
                else
                        zensendevent -d $(echo ${SERV} | awk -F, '{print $3}') -y ${BL}_$(echo ${SERV} | awk -F, '{print $4}') -p "Listed IP: $(echo ${SERV} | awk -F, '{print $2}')" -s Warning -c "/App/Email/Blacklist" -k ${BL}_$(echo ${SERV} | awk -F, '{print $4}') "Blacklisted on ${BL}"
                fi
        done
done
#
#
