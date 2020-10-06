#!/usr/bin/env python3

import re, sys, os, pyeapi, pprint, argparse, json, time
from terminaltables import AsciiTable

READ_FILE = '/Users/paulc/github/code/Demo/Eval.txt'

###############################################################################
##### APLE TOOL ############################################################
##### msft-team@arista.com ####################################################
# VERSION 1.0 - paulc   - Initial arista policy language evaluation concept

###############################################################################
# ARGUMENTS TO PASS INTO THE TOOL
###############################################################################

parser = argparse.ArgumentParser(description = 'Define what additional arguments you want to pass to the tool')
parser.add_argument('--set', help='Configures n1-n4 with a set of baseline parameters to test against')
parser.add_argument('--topo', help='Builds a 4 node PTP BGP peer topology between two cEOS containers')
parser.add_argument('--v6', help='Evaluates RCF for a v6 policy')
args = parser.parse_args()


###############################################################################
# SETTING eAPI PARAMS
###############################################################################

n1      = pyeapi.connect(transport='https', host='', username='eapi', password='admin', port=4000)
n1eapi  = pyeapi.client.Node(n1)
n2      = pyeapi.connect(transport='https', host='', username='eapi', password='admin', port=4010)
n2eapi  = pyeapi.client.Node(n2)
n3      = pyeapi.connect(transport='https', host='', username='eapi', password='admin', port=4020)
n3eapi  = pyeapi.client.Node(n3)
n4      = ''
n4eapi  = ''

#node1 = pyeapi.connect_to(n1)
#node2 = pyeapi.connect_to(n2)


###############################################################################
# READ OPERATOR LOGIC
###############################################################################



###############################################################################
# READ POLICY AND CONFIGURE N1-N4
###############################################################################
def configure ():

    global command, v, BGP, EXT, COMR, COMA, COMM, comrl, comal, comml, ASP, PF4, PF6, pf4t, pf6t, aspl, extl, TAG, tagl

    v = -1
    BGP = False     # Look for BGP params
    EXT = False     # Look for extended community params
    COMR = False    # Look for remove community params
    COMA = False    # Look for add community params
    COMM = False    # Look for match community params
    ASP = False     # Look for as-path params
    PF4 = False     # Look for v4 prefx-lists
    PF6 = False     # Look for v6 prefix-lists
    TAG = False     # Look for TAG params
    comml = []

    print (fmt1 + ' READ POLICY AND CONFIGURE N1-N4 '  + fmt1)
    for line in pr:
        if re.search('match ext_community_list COLOR', line):
            extl = ''.join([x for x in line.split() if x.startswith('COLOR_')]).strip('COLOR_')
            EXT = True
        if re.search('match as_path_list', line):
            aspl = ''.join([x for x in line.split() if x.startswith('AS') or x.startswith('CONTAINS-AS') or x.startswith('as-path-') or x.startswith('FROM-AS')]).lstrip('AS').lstrip('CONTAINS-AS').lstrip('FROM-AS').lstrip('as-path-')
            ASP = True
        if re.search('prefix_list_v4', line):
            PF4 = True
            v0 = line.split()
            pf4t = v0[-2]
        if re.search('prefix_list_v6', line):
            PF6 = True
            pf6t = ''
        if re.search('community remove', line):
            COMR = True
            v0 = line.split()
            comrl = v0[-1][:-1]
        if re.search('community add', line) or re.search('community =', line):
            COMA = True
            v0 = line.split()
            comal = v0[-1][:-1]
        if re.search('community match community_list', line):
            COMM = True
            v0 = line.split()
            comml.append(v0[-2])
        if re.search('igp.tag is', line):
            TAG = True
            fnd = re.search('\-?\d+', line)
            tagl = (fnd.group(0))
        if re.search('return' , line):
            if v <= 6:
                v += 1
            elif v >= 7:
                v = 0
            commands()

    print ('### CONFIG COMPLETE\n')

def commands ():

    global v, EXT, ASP, PF4, COMR, COMA, COMM, comrl, comal, comml, pf4t, aspl, extl, TAG, tagl

    RMAP = ['10', '20', '30', '40', '50', '60', '70', '80']
    v4RMAP = ['25.0.0.255/32', '50.0.0.255/32', '75.0.0.255/32', '100.0.0.255/32', '125.0.0.255/32', '150.0.0.255/32', '175.0.0.255/32', '200.0.0.255/32']
    v6RMAP = ['2001::25.0.0.255/32', '2001::50.0.0.255/32', '2001::75.0.0.255/32', '2001::100.0.0.255/32', '2001::125.0.0.255/32', '2001::150.0.0.255/32', '2001::175.0.0.255/32', '2001::200.0.0.255/32']

    if EXT == True:
        n2eapi.run_commands(["enable", "configure", "route-map COLOR permit " + RMAP[v], "no set extcommunity color " + RMAP[v], "set extcommunity color " + extl])
        print ("N2 - Coniguring color 10293 on route route-map " + RMAP[v] + " for prefix " + v4RMAP[v])
        n1eapi.run_commands(["enable", "configure","ip extcommunity-list COLOR_10293 permit color " + extl])
        print ("N1 - Configuring extended community list for color " + extl)
        EXT = False
    if ASP == True:
        n2eapi.run_commands([ "enable", "configure", "route-map COLOR permit " + RMAP[v], "set as-path prepend " + aspl])
        print ("N2 - Coniguring AS path prepend " + aspl + " on route-map " + RMAP[v])
        n1eapi.run_commands([ "enable", "configure", "ip as-path access-list AS" + aspl + " permit " + aspl + " any"])
        print ("N1 - Configuring AS-path access list for " + aspl)
        ASP = False
    if PF4 == True:
        n1eapi.run_commands([ "enable", "configure", "ip prefix-list " + pf4t, "no seq 10", "seq 10 permit " + v4RMAP[v]])
        print ("N1 - Coniguring prefix-list " + pf4t + " to allow route " + v4RMAP[v])
        PF4 = False
    if COMR == True:
        n1eapi.run_commands([ "enable", "configure", "ip community-list " + comrl + " permit 0:10 0:20 0:30 0:40"])
        print ("N1 - Configuring community-list " + comrl + " to remove 0:10 0:20 0:30 0:40")
        COMR = False
    if COMA == True:
        n1eapi.run_commands([ "enable", "configure", "ip community-list " + comal + " permit 0:100"])
        print ("N1 - Configuring community-list " + comal + "to add 0:100")
        COMA = False
    if COMM == True:
        for nl in comml:
            n1eapi.run_commands([ "enable", "configure", "ip community-list " + nl + " permit 0:10"])
            n1eapi.run_commands([ "enable", "configure", "ip community-list " + nl + " permit 0:20"])
            n1eapi.run_commands([ "enable", "configure", "ip community-list " + nl + " permit 0:30"])
            n1eapi.run_commands([ "enable", "configure", "ip community-list " + nl + " permit 0:40"])
            print ("N1 - Configuring community-list " + nl + " to match 0:10 0:20 0:30 0:40")
            comml = []
            COMM = False
    if TAG == True:
        n2eapi.run_commands([ "enable", "configure", "route-map COLOR permit " + RMAP[v], "set tag " + tagl])
        print ("N2 - Coniguring IGP tag of " + tagl + " on route-map " + RMAP[v])
        TAG = False

###############################################################################
# SHOW DATA BEFORE POLICY PUSH
###############################################################################
global command

def show ():
    v0 = pr[1].find('()')

    print (fmt1 + ' SHOW DATA BEFORE POLICY '  + fmt1)

    n1eapi.run_commands([
      "enable",
      "configure replace flash:stage.cfg"
    ])

    time.sleep(1)

    n2eapi.run_commands([
      "enable",
      "configure replace flash:stage.cfg"
    ])

    time.sleep(1)

    print ('### SHOW ALL ROUTES ON N1')
    command = n1eapi.run_commands(['show ip route'])

    table_data = [['ROUTE', 'ROUTE-TYPE']]

    for item in command[0]['vrfs']['default']['routes']:
        routes = command[0]['vrfs']['default']['routes'][item]['routeType']
        table_data.append([item, routes])

    table = AsciiTable(table_data)
    print (table.table)

    print ('\n' + '### SHOW ALL BGP LEARNED ROUTES FROM N1 AFTER RCF POLICY IS APPLIED')
    command = n1eapi.run_commands(['show ip bgp detail'])
    #pprint.pprint (command)

    table_data = [['BGP ROUTES', 'LOCAL-PREFERENCE', 'MED', 'COMMUNITY', "EXT-COMMUNITY", 'NEXT-HOP', 'TAG', 'AS-PATH']]

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
                community = (bgproute[0]['routeDetail']['communityList'])
            elif items == 'nextHop':
                nexthop = (bgproute[0]['nextHop'])
            elif items == 'tag':
                tag = (bgproute[0]['tag'])
        table_data.append([item, locpref, med, community, color, nexthop, tag,  aspath])

    table = AsciiTable(table_data)
    print (table.table)

    print ('\n' + '### SHOW ALL BGP ADVERTISED ROUTES TO N2 AFTER RCF POLICY IS APPLIED')
    command = n1eapi.run_commands(['sh ip bgp neighbors 10.0.0.1 advertised-routes detail'])
    #pprint.pprint (command)

    table_data = [['BGP ROUTES', 'LOCAL-PREFERENCE', 'MED', 'COMMUNITY', "EXT-COMMUNITY", 'NEXT-HOP', 'TAG', 'AS-PATH']]

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
                community = (bgproute[0]['routeDetail']['communityList'])
            elif items == 'nextHop':
                nexthop = (bgproute[0]['nextHop'])
            elif items == 'tag':
                tag = (bgproute[0]['tag'])
        table_data.append([item, locpref, med, community, color, nexthop, tag, aspath])

    table = AsciiTable(table_data)
    print (table.table)

###############################################################################
# PUSH RCF POLICY
###############################################################################
def push ():
    v0 = pr[1].split()

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

    print ('### SHOW ALL ROUTES ON N1')
    command = n1eapi.run_commands(['show ip route'])
    #pprint.pprint (command)

    table_data = [['ROUTE', 'ROUTE-TYPE']]

    for item in command[0]['vrfs']['default']['routes']:
        routes = command[0]['vrfs']['default']['routes'][item]['routeType']
        table_data.append([item, routes])

    table = AsciiTable(table_data)
    print (table.table)

    print ('\n' + '### SHOW ALL BGP LEARNED ROUTES FROM N1 AFTER RCF POLICY IS APPLIED')
    command = n1eapi.run_commands(['show ip bgp detail'])
    #pprint.pprint (command)

    table_data = [['BGP ROUTES', 'LOCAL-PREFERENCE', 'MED', 'COMMUNITY', "EXT-COMMUNITY", 'NEXT-HOP', 'TAG', 'AS-PATH']]

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
                community = (bgproute[0]['routeDetail']['communityList'])
            elif items == 'nextHop':
                nexthop = (bgproute[0]['nextHop'])
            elif items == 'tag':
                tag = (bgproute[0]['tag'])
        table_data.append([item, locpref, med, community, color, nexthop, tag,  aspath])
        #print (item, '\t', locpref, '\t\t\t', med, '\t', color, '\t', aspath)

    table = AsciiTable(table_data)
    print (table.table)

    print ('\n' + '### SHOW ALL BGP ADVERTISED ROUTES TO N2 AFTER RCF POLICY IS APPLIED')
    command = n1eapi.run_commands(['sh ip bgp neighbors 10.0.0.1 advertised-routes detail'])
    #pprint.pprint (command)

    table_data = [['BGP ROUTES', 'LOCAL-PREFERENCE', 'MED', 'COMMUNITY', "EXT-COMMUNITY", 'NEXT-HOP', 'TAG', 'AS-PATH']]

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
                community = (bgproute[0]['routeDetail']['communityList'])
            elif items == 'nextHop':
                nexthop = (bgproute[0]['nextHop'])
            elif items == 'tag':
                tag = (bgproute[0]['tag'])
        table_data.append([item, locpref, med, community, color, nexthop, tag,  aspath])

    table = AsciiTable(table_data)
    print (table.table)

###############################################################################
# BUILD cEOS TOPOLOGY
###############################################################################





with open(READ_FILE) as r:

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
        show ()
        configure ()
        push ()
        evaluate ()
