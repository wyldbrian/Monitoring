#!/bin/bash

#+-----------------------------------------------------------------------+
#| File Name: scpuser_expire.sh                                          |
#+-----------------------------------------------------------------------+
#| Description: This script checks to see how many days are left until   |
#|              the user account scpuser expires. Nagios then checks     |
#|              /var/tmp/scpuser_expire for the results.                 |
#|              Under 30 days = Critcal, over = Clear                    |
#+-----------------------------------------------------------------------+
#| Authors: Brian Spaulding                                              |
#+-----------------------------------------------------------------------+
#| Date: 2016-10-11                                                      |
#+-----------------------------------------------------------------------+

hostname=$(hostname -s)
currentdate=$(date +%s)
userexp=$(chage -l scpuser | grep 'Password expires' | cut -d : -f 2)
passexp=$(date -d "$userexp" +%s)
exp=$(expr \( $passexp - $currentdate \))
expday=$(expr \( $exp / 86400 \))

if [ $expday -lt 30 ]; then
        echo "2: The user account scpuser on $hostname will expire in $expday days" > /var/tmp/scpuser_expire
elif [ $expday -ge 30 ]; then
        echo "0: The user account scpuser on $hostname will expire in $expday days" > /var/tmp/scpuser_expire
else
        echo "3: Script error, unable to determine password expiration" > /var/tmp/scpuser_expire
fi