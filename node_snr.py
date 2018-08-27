#!/usr/bin/env python
import os

nodeSnrCmd = '''tsql -S sql-dw -U USERNAME -P PASSWORD<<'END1' > /tmp/node_snr.txt
use modem_data_staging;
execute spUS_SNR_all;
go
quit
END1'''
nodeListedCmd = '''tsql -S sql-dw -U USERNAME -P PASSWORD<<'END2' > /tmp/nodes_listed.txt
use Observium_Staging;
select distinct([ports].port_descr_circuit) as node, replace(devices.hostname, '.bendcable.net', '') as cmts from [observium_staging]..[ports] inner join [devices] on [devices].device_id = [ports].
device_id where devices.hostname like 'UBR%' and [ports].ifdescr like '%upstream%' and port_descr_descr is not null order by cmts, node;
go
quit
END2'''

nodesSnrResult = ''
nodeListedResult = ''

skipLines = ['1>', '1> 2> 3> AVG_SNR~port_descr_circuit', '1> 2> 3> node~cmts', 'locale is \"en_US.UTF-8\"', 'locale charset is \"UTF-8\"', 'using default charset \"UTF-8\"', 'locale is \"en_US.UTF-8\"', 'locale charset is \"UTF-8\"', 'u
sing default charset \"UTF-8\"']
snrLevels = {27:5, 30:3}
severityStrings = {5:'Critical', 4:'Error', 3:'Warning', 0:'Clear'}
severityInts = {'Critical':5, 'Error':4, 'Warning':3, 'Clear':0}
ubrMap = {'ubr2':'REDACTED', 'ubr3':'REDACTED', 'ubr4':'REDACTED', 'ubr-sr1':'REDACTED', 'ubr-sr2':'REDACTED', 'ubrtest':'REDACTED'}
circuits = {}
circuitResults = {}

def replaceJunk(stringIn, skipLines):
    cleanStr = stringIn.replace('[\'','')
    cleanStr = cleanStr.replace('\']','')
    cleanStr = cleanStr.replace('\', \'','')
    cleanStr = cleanStr.replace('          ','~')
    cleanStr = cleanStr.replace('         ','~')
    cleanStr = cleanStr.replace('        ','~')
    cleanStr = cleanStr.replace('       ','~')
    cleanStr = cleanStr.replace('      ','~')
    cleanStr = cleanStr.replace('     ','~')
    cleanStr = cleanStr.replace('    ','~')
    cleanStr = cleanStr.replace('   ','~')
    cleanStr = cleanStr.replace('  ','~')
    cleanStr = cleanStr.replace(' ubr','~ubr')
    cleanStr = cleanStr.replace('\\t','~')
    cleanList = cleanStr.split('\\n')
    clean = []
    for entry in cleanList:
        if len(entry) == 0 or entry in skipLines or '~' not in entry: continue
        clean.append(entry)
    return clean

def correlateNodes(nodesSnrResult=nodesSnrResult, nodeListedResult=nodeListedResult):
    circuit = {}
    circuitB = {}
    nodesSnr = replaceJunk(nodesSnrResult, skipLines)
    for entry in nodesSnr:
        if entry in skipLines:
            continue
        nodeData = entry.split('~')
        nodeName = nodeData[1]
        if nodeName == 'NULL': continue
        circuit[nodeName] = {'SNR':nodeData[0]}
    nodesListed = replaceJunk(nodeListedResult, skipLines)
    for entry in nodesListed:
        if entry in skipLines:
            continue
        nodeData = entry.split('~')
        nodeName = nodeData[0]
        circuitB[nodeName] = {'UBR':nodeData[1]}
    for entry in circuit:
        circuit[entry]['UBR'] = circuitB[entry]['UBR']
    return circuit

def processCircuitData(circuits=circuits, snrLevels=snrLevels, severityStrings=severityStrings):
    for entry in circuits:
        severity = 0
        for level in snrLevels:
            if float(circuits[entry]['SNR']) < float(level):
                if snrLevels[level] > severity:
                   severity = snrLevels[level]
        circuits[entry]['Status'] = severityStrings[severity]
    return circuits

def createEvents(circuitResults=circuitResults, debug=True, showClears=False, ubrMap=ubrMap):
    callsToRun = []
    for entry in circuitResults:
        component = entry
        host = ubrMap[circuitResults[entry]['UBR']]
        severity = circuitResults[entry]['Status']
        snr = circuitResults[entry]['SNR']
        if severity == 'Clear' and showClears == False:
            continue
        message = 'SNR for node %s is %s' % (component, snr)
        callsToRun.append('zensendevent -d \'%s\' -y \'%s_%s\' -p \'%s\' -c \'%s\' -k \'%s_node_snr\' -s \'%s\' \'%s\'' % (host, component, host, component, '/Cable Plant/SNR', component, severity, message))
    if debug == True:
        for callToRun in callsToRun:
            print 'Command %s' % callToRun
    elif debug == False:
        for callToRun in callsToRun:
            print 'Running %s' % callToRun
            os.system(callToRun)

os.system(nodeSnrCmd)
nodeSnrFile = '/tmp/node_snr.txt'
with open(nodeSnrFile) as file:
    content = file.readlines()
nodesSnrResult = str(content)
os.system(nodeListedCmd)
nodeListedFile = '/tmp/nodes_listed.txt'
with open(nodeListedFile) as file:
    content = file.readlines()
nodeListedResult = str(content)

circuits = correlateNodes(nodesSnrResult=nodesSnrResult, nodeListedResult=nodeListedResult)
circuitResults = processCircuitData(circuits=circuits, snrLevels=snrLevels, severityStrings=severityStrings)
createEvents(circuitResults=circuitResults, debug=False, showClears=True)
