#!/bin/bash
#
#
#Lists of ssl cert sites to check as a array
#
#When adding new certificates to be checked add them to this list in the following format:
#site:port,server
 SSLSITES="
        REDACTED:443,HOWARD
        REDACTED:443,GARMISCH
        REDACTED:443,EXCHANGE
        REDACTED:443,as1
"
# Create a function to get the difference beween 2 dates
datediff() {
    d1=$(date -d "$1" +%s) #first passed arg in epoch time
    d2=$(date -d "$2" +%s) #second passed arg in epoch time
    echo $(( ($d1 - $d2)/60/60/24 )) #convert difference from epoch to days
}
#Run each site through the check in a loop
for ssl in ${SSLSITES}; do
        now=$(date)
#get current date
        sslxp=$(timeout 5s openssl s_client -connect $(echo ${ssl} | awk -F, '{print $1}') 2>/dev/null | openssl x509 -noout -dates | awk /notAfter/ | awk -F= '{print $2}' | awk '{print $1 " " $2 " " $4}')
#this pulls the expiration date out of the open ssl cert and times out if no response.
        if [ "$sslxp" == '' ]; then  #if command timed out send an informational that the site could not be reached
                zensendevent -d $(echo ${ssl} | awk -F, '{print $2}')  -y ${ssl}_check -p "SSL Cert: $(echo ${ssl} | awk -F: '{print $1}')" -s Info -c "/Domain/Certificate" -k ${ssl}_check "Unable to reach site"
        else
                diff=$(datediff "$sslxp" "$now")
#pass todays date and the expiration date to the datediff function
                if [ "$diff" -le "15" ]; then
#if less than 15 days to cert expiration then send a critical alert
                        zensendevent -d $(echo ${ssl} | awk -F, '{print $2}')  -y ${ssl}_check -p "SSL Cert: $(echo ${ssl} | awk -F: '{print $1}')" -s Critical -c "/Domain/Certificate" -k ${ssl}_check "SSL Cert Expires in $diff Days"
                else if [ "$diff" -le "30" ]; then
#if less than 30 days to cert expiration send a warning alert
                        zensendevent -d $(echo ${ssl} | awk -F, '{print $2}')  -y ${ssl}_check -p "SSL Cert: $(echo ${ssl} | awk -F: '{print $1}')" -s Warning -c "/Domain/Certificate" -k ${ssl}_check "SSL Cert Expires in $diff Days"
                else
#if more than 30 days until cert expiration, send a clear
                        zensendevent -d $(echo ${ssl} | awk -F, '{print $2}')  -y ${ssl}_check -p "SSL Cert: $(echo ${ssl} | awk -F: '{print $1}')" -s Clear -c "/Domain/Certificate" -k ${ssl}_check "SSL Cert Expires in $diff Days"
                fi
                fi
        fi
done
