# Monitoring

This repo contains a variety of scripts used to monitor anything from offline cable modems and modem SNR to SSL cert expiration and IP reputation. 

Most of these scripts are written for Zenoss 4 (Core) or Nagios, and several of them call `zensendevent`, which is a Zenoss specific command line tool for sending alarms.

Zenoss has changed a ton since I wrote these scripts, but as of August 2018 there is still a [free version](https://www.zenoss.com/get-started).

### Purpose of each...

Here's a list of each script and what it does.
- **ubr10k_arp_check.py** - finds and alerts on > 10 entries of the same mac address in a Cisco UBR10k mac table
- **offline_modems.py** - checks the percentage of offline modems per node (upstream) on Cisco UBRs
- **title_to_sysname.py** - modifies device titles in Zenoss to match their SNMP sysnames
- **node_snr.py** - pulls the last known SNR for each node (upstream)
- **headend_backup_check.py** - checks a remote machine to see if new backups exist
- **usage_validation.pl** - checks the usage for a specific cable modem to confirm accurate tracking
- **ssl_cert_check.sh** - checks the expiration of muliple SSL certs and calculates the remaining duration
- **severity_escalation.py** - escalates alarms based on component type and number of occurences
- **scpuser_expire.sh** - checks the expiration of the scpuser account and calculates remaining duration
- **device_audit.py** - pulls and displays all devices from Zenoss
- **blacklist_check.sh** - runs serveral public ips against multiple blacklists to see if they've been flagged


