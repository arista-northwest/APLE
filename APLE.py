#!/usr/bin/env python3

import re, sys, os, pyeapi, pprint, argparse, json, time
from terminaltables import AsciiTable

READ_FILE = '/Users/paulc/Desktop/Demo/J2A.txt'

###############################################################################
##### APLE TOOL ############################################################
##### msft-team@arista.com ####################################################
# VERSION 1.0 - paulc   - Initial arista policy language evaluation concept

###############################################################################
# ARGUMENTS TO PASS INTO THE TOOL
###############################################################################

parser = argparse.ArgumentParser(description = 'Define what additional arguments you want to pass to the tool')
parser.add_argument('--set', help='Configures n1-n4 with a set of baseline parameters to test against')
parser.add_argument('--baseline', help='Configures n1-n4 with a set of baseline parameters to test against')
parser.add_argument('--topo', help='Builds a 4 node PTP BGP peer topology between two cEOS containers')
args = parser.parse_args()


###############################################################################
# SETTING eAPI PARAMS
###############################################################################

n1      = pyeapi.connect(transport='https', host='', username='eapi', password='admin', port=4000)
n1eapi  = pyeapi.client.Node(n1)
n2      = pyeapi.connect(transport='https', host='', username='eapi', password='admin', port=4010)
n2eapi  = pyeapi.client.Node(n2)
n3      = '' 
n3eapi  = ''
n4      = ''
n4eapi  = ''

#node1 = pyeapi.connect_to(n1)
#node2 = pyeapi.connect_to(n2)

###############################################################################
# CONFIGURE BASELINE
###############################################################################

aspath      = 'ip as-path access-list ASPLIST permit 65000_65001_65002 any'
comlist     = 'ip community-list COMMLIST permit 65000:10 65000:20'
comlist1    = 'ip community-list COMMLIST1 perit 65000:1 65000:2'
comlist2    = 'ip community-list COMMLIST2 permit 65000:3'
comlist3    = 'ip community-list COMMLIST3 permit 65000:2'
extcom      = 'ip extcommunity-list COLOR_20 permit color 20'
v4list      = 'ip prefix-list DEFAULT_V4 seq 10 permit 0.0.0.0/0'
v6list      = 'ipv6 prefix-list DEFAULT_V6\nseq 10 permit ::/0'
tagv4list   = 'ip prefix-list TAG_IP seq 10 permit 25.0.0.255/32'
tagv4       = 'ip route 25.0.0.255/32 25.0.0.1 tag 100'
tagv6list   = 'ipv6 prefix-list DEFAULT_V6\nseq 10 permit 2001::25.0.0.255/128'
tagv6       = 'ipv6 route 2001::25.0.0.255/128 2001::25.0.0.1 tag 100'

###############################################################################
# READ OPERATOR LOGIC
###############################################################################



###############################################################################
# READ POLICY AND CONFIGURE N1-N4
###############################################################################
global command

def configure ():
    print (fmt1 + ' READ POLICY AND CONFIGURE PEER N1-N4 '  + fmt1)
    print ('### CONFIG COMPLETE\n')


###############################################################################
# SHOW DATA BEFORE POLICY PUSH
###############################################################################
global command

def show ():
    v0 = pr[1].find('()')

    print (fmt1 + ' SHOW DATA BEFORE POLICY '  + fmt1)

    n1eapi.run_commands([
      "enable",
      "configure",
      "router bgp 65000",
      "address-family ipv4",
      "no neighbor 10.0.0.3 rcf in"
    ])

    time.sleep(2)

    print ('### SHOW ALL ROUTES')
    command = n1eapi.run_commands(['show ip route'])

    table_data = [['ROUTE', 'ROUTE-TYPE']]

    for item in command[0]['vrfs']['default']['routes']:
        routes = command[0]['vrfs']['default']['routes'][item]['routeType']
        table_data.append([item, routes])

    table = AsciiTable(table_data)
    print (table.table)

    print ('\n' + '### SHOW ALL BGP LEARNED ROUTES')
    command = n1eapi.run_commands(['show ip bgp detail'])
    #pprint.pprint (command)

    table_data = [['BGP ROUTES', 'LOCAL-PREFERENCE', 'MED', 'COLOR', 'AS-PATH']]

    for item in command[0]['vrfs']['default']['bgpRouteEntries']:
        bgproute = command[0]['vrfs']['default']['bgpRouteEntries'][item]['bgpRoutePaths']
        for items in bgproute[0]:
            if items == 'localPreference':
                locpref = (bgproute[0]['localPreference'])
            elif items == 'asPathEntry':
                aspath = (bgproute[0]['asPathEntry']['asPath'])
            elif items == 'med':
                med = (bgproute[0]['med'])
            elif items == 'routeDetail':
                color = (bgproute[0]['routeDetail']['extCommunityList'])
        table_data.append([item, locpref, med, color, aspath])

    table = AsciiTable(table_data)
    print (table.table)

###############################################################################
# PUSH RCF POLICY
###############################################################################
def push ():
    v0 = pr[1].split()
    print (v0[2])

    print ('\n' + fmt1 + ' PUSHING THE FOLLOWING POLICY TO THE NODE ' + fmt1 + '\n')
    print (rcf)
    a = r'\n'.join([str(item) for item in pr])
    z = ("'" + a + "'")
    n1eapi.run_commands(["bash timeout 10 echo -e " + z + " > /mnt/flash/RCF-in.txt"])
    n1eapi.run_commands([
      "enable",
      "configure",
      "router general",
      "control-functions",
      "pull replace flash:RCF-in.txt",
      "commit"
    ])
    time.sleep(1)
    n1eapi.run_commands([
      "enable",
      "configure",
      "router bgp 65000",
      "address-family ipv4",
      "neighbor 10.0.0.3 rcf in " + v0[1] + "()"
    ])
    time.sleep(1)


###############################################################################
# EVALUATE RCF POLICY
###############################################################################
global command

def evaluate ():

    print (fmt1 + ' SHOW DATA AFTER THE POLICY '  + fmt1)

    print ('### SHOW ALL ROUTES')
    command = n1eapi.run_commands(['show ip route'])
    #pprint.pprint (command)

    table_data = [['ROUTE', 'ROUTE-TYPE']]

    for item in command[0]['vrfs']['default']['routes']:
        routes = command[0]['vrfs']['default']['routes'][item]['routeType']
        table_data.append([item, routes])

    table = AsciiTable(table_data)
    print (table.table)

    print ('\n' + '### SHOW ALL BGP LEARNED ROUTES')
    command = n1eapi.run_commands(['show ip bgp detail'])
    #pprint.pprint (command)

    table_data = [['BGP ROUTES', 'LOCAL-PREFERENCE', 'MED', 'COLOR', 'AS-PATH']]

    for item in command[0]['vrfs']['default']['bgpRouteEntries']:
        bgproute = command[0]['vrfs']['default']['bgpRouteEntries'][item]['bgpRoutePaths']
        for items in bgproute[0]:
            if items == 'localPreference':
                locpref = (bgproute[0]['localPreference'])
            elif items == 'asPathEntry':
                aspath = (bgproute[0]['asPathEntry']['asPath'])
            elif items == 'med':
                med = (bgproute[0]['med'])
            elif items == 'routeDetail':
                color = (bgproute[0]['routeDetail']['extCommunityList'])
        table_data.append([item, locpref, med, color, aspath])
        #print (item, '\t', locpref, '\t\t\t', med, '\t', color, '\t', aspath)

    table = AsciiTable(table_data)
    print (table.table)

with open(READ_FILE) as r:

###############################################################################
# BUILD TOPOLOGY
###############################################################################



###############################################################################
# VARIABLES
###############################################################################
    li = 0
    nf = True
    pr = []     # Builds the RCF rule to push to the DUT
    rv = []     # Rule evaluation results
    sv = []     # Sets values according to the rules evaluated

###############################################################################
# VISUAL FORMAT
###############################################################################
    fmt1    = ('#' * 20)
    fmt2    = ('#' * 25)

###############################################################################
# FUNC MAIN
###############################################################################
    for row in r:
        if re.search('FUNCTION', row):
            pr.append(row)
            for row in r:
                if re.search('FUNCTION', row):
                    break
                else:
                    pr.append(row)
        rcf = ''.join([str(item) for item in pr])
        configure ()
        show ()
        push ()
        evaluate ()
