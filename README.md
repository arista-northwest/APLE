Prepared by: <msft-team@arista.com>  
Date: September 30th, 2020  
Version: 1.0



# APLE Tool

The Arista Policy Language Evaluator (APLE) is a python script used to evaluate RCF policies. The script uses an assumed cEOS topology shown below which is used to evaluate the the BGP control plane for a given RCF policy. The script also allows you to pass a `--topo` argument if you wish to have the below topology built for you. 

<u>There are four general steps of the script:</u>  
1) Read the RCF policy and configure N1-N4 devices accordingly.  
2) Show the relevant data used prior to the policy applied.   
3) Push the RCF policy to the DUT, compile, commit, and apply to the neighbor.   
4) Show the relevant data used after the policy has been applied.   


## Topology

**N1** - The DUT used for RCF-in and RCF-out testing.  
**N2** - eBGP peer to N1.  
**N3** - iBGP peer to N1.  
**N4** - The DUT for RCF-in and RCF-out.  

![](/images/TOPO.jpg)


## Arguments

If you wish to either generate the baseline configs used to test policies or build the cEOS topology, pass in the arguments below.

```
usage: APLE.py [-h] [--set SET] [--topo TOPO] [--v6 V6]

Define what additional arguments you want to pass to the tool

optional arguments:
  -h, --help   show this help message and exit
  --set SET    Configures n1-n4 with a set of baseline parameters to test against
  --topo TOPO  Builds a 4 node PTP BGP peer topology between two cEOS containers
  --v6 V6      Evaluates RCF for a v6 policy

```

## Requirements

Linux server with docker.  
cEOS image      
python3 ~ **It is now considered a crime if you use Python2**

```
sudo docker import cEOS-lab.tar.xz ceosimage:latest  
pip3 install pyeapi  
pip3 install terminaltables 
```

## Read File
Set your READ file path in the script: `READ_FILE=/path/to/file`


The script will run a loop over the RCF policy language and will create a RCF policy for every function that it finds to push to N1. Each funtion will be evaluated in serial and the environement will be staged to support what is read. 

## eAPI Params
Open APLE.py and edit under this section listed below. Set the username and password for eAPI, or the default uses username admin password admin.

```
###############################################################################
# SETTING eAPI PARAMS
###############################################################################
```

## Baseline Routing

A baseline set of prefixes are generated and manipulated based on the policies read.


BGP Baseline Routes:

| v4/v6 Route       | Loc-Pref | MED | Community | Ext-Community | v4/v6 NH| TAG | ASN | 
| :---      | :----   			 | :--- 	               | :----     |:--- |:--- |:--- | :---
| 25.0.0.255/32<br> 2001::25.0.0.255/128  | 100              | 0   | ['0:20']  | ['Color:CO(00):20'] | 10.0.0.3 <br> 2001::10.0.0.3 | 0| 65001   |
| 50.0.0.255/32<br> 2001::50.0.0.255/128  | 100              | 0   | ['0:80']  | NONE                  | 10.0.0.3 <br> 2001::10.0.0.3 | 0 | 65001   |
| 75.0.0.255/32<br> 2001::75.0.0.255/128  | 100              | 0   | ['0:50']  | ['Color:CO(00):50'] | 10.0.0.3 <br> 2001::10.0.0.3 | 0 |65001   |
| 100.0.0.255/32 <br> 2001::100.0.0.255/128  | 100              | 0   | ['0:10']  | ['Color:CO(00):10'] | 10.0.0.3 <br> 2001::10.0.0.3 | 0 |65001   |
| 125.0.0.255/32 <br> 2001::125.0.0.255/128  | 100              | 0   | ['0:30']  | ['Color:CO(00):30'] | 10.0.0.3 <br> 2001::10.0.0.3 | 0 |65001   |
| 150.0.0.255/32<br> 2001::150.0.0.255/128  | 100              | 0   | ['0:70']  | ['Color:CO(00):70'] | 10.0.0.3 <br> 2001::10.0.0.3| 0 |65001   |
| 175.0.0.255/32<br> 2001::175.0.0.255/128  | 100              | 0   | ['0:60']  | ['Color:CO(00):60'] | 10.0.0.3 <br> 2001::10.0.0.3 | 0 |65001   |
| 200.0.0.255/32 <br> 2001::200.0.0.255/128 | 100              | 0   | ['0:40']  | ['Color:CO(00):40'] | 10.0.0.3 <br> 2001::10.0.0.3| 0 | 65001   |

## Step 1 - Configure

The script uses eAPI to configure the devices and reads the function(s) that have been programmed in the read file.

In this example we read:

```
#########################FUNCTION########################
function  ADVERTISE_AS8068  () {
#########################TERM############################
#  ALLOW_8068_OVERLOAD  
#########################################################
# if source_protocol is BGP and
if as_path match as_path_list AS8068 and
ext_community match ext_community_list COLOR_10293 {
local_preference = 10 ;
return true ;
#########################TERM############################
#  ALLOW_8068  
#########################################################
#} else if source_protocol is BGP and
} else if as_path match as_path_list AS8068 {
return true ;
  }
}
```

Since source protocol BGP is a new feature it is **#commented** out.  The script will read the as-path parameter and configure as-path prepending on N2 with 8068. The script will read the ext_community parameter and configure a route with a new color parameter of 10293.

If succesfull the following will print out.  

```
#################### READ POLICY AND CONFIGURE N1-N4 ####################
N2 - Coniguring color 10293 on route route-map 10 for prefix 25.0.0.255/32
N1 - Configuring extended community list for color 10293
N2 - Coniguring AS path prepend 8068 on route-map 10
N1 - Configuring AS-path access list for 8068
N2 - Coniguring AS path prepend 8068 on route-map 20
N1 - Configuring AS-path access list for 8068
### CONFIG COMPLETE
```
## Step 2 - Pre-policy Evaluation

The script will evaluate what the DUT was recieving prior to the RCF policy.

In this example we see this printed below:

```
#################### SHOW DATA BEFORE POLICY ####################
### SHOW ALL ROUTES ON N1
+----------------+------------+
| ROUTE          | ROUTE-TYPE |
+----------------+------------+
| 50.0.0.255/32  | eBGP       |
| 10.0.0.0/31    | connected  |
| 200.0.0.255/32 | eBGP       |
| 125.0.0.255/32 | eBGP       |
| 25.0.0.255/32  | eBGP       |
| 75.0.0.255/32  | eBGP       |
| 175.0.0.255/32 | eBGP       |
| 10.0.0.2/31    | connected  |
| 150.0.0.255/32 | eBGP       |
| 100.0.0.255/32 | eBGP       |
+----------------+------------+

### SHOW ALL BGP LEARNED ROUTES FROM N1 AFTER RCF POLICY IS APPLIED
+----------------+------------------+-----+-----------+---------------------+----------+-----+---------+
| BGP ROUTES     | LOCAL-PREFERENCE | MED | COMMUNITY | EXT-COMMUNITY       | NEXT-HOP | TAG | AS-PATH |
+----------------+------------------+-----+-----------+---------------------+----------+-----+---------+
| 50.0.0.255/32  | 100              | 0   | ['0:20']  | ['Color:CO(00):20'] | 10.0.0.3 | 0   | 65001   |
| 200.0.0.255/32 | 100              | 0   | ['0:80']  | []                  | 10.0.0.3 | 0   | 65001   |
| 125.0.0.255/32 | 100              | 0   | ['0:50']  | ['Color:CO(00):50'] | 10.0.0.3 | 0   | 65001   |
| 25.0.0.255/32  | 100              | 0   | ['0:10']  | ['Color:CO(00):10'] | 10.0.0.3 | 0   | 65001   |
| 75.0.0.255/32  | 100              | 0   | ['0:30']  | ['Color:CO(00):30'] | 10.0.0.3 | 0   | 65001   |
| 175.0.0.255/32 | 100              | 0   | ['0:70']  | ['Color:CO(00):70'] | 10.0.0.3 | 0   | 65001   |
| 150.0.0.255/32 | 100              | 0   | ['0:60']  | ['Color:CO(00):60'] | 10.0.0.3 | 0   | 65001   |
| 100.0.0.255/32 | 100              | 0   | ['0:40']  | ['Color:CO(00):40'] | 10.0.0.3 | 0   | 65001   |
+----------------+------------------+-----+-----------+---------------------+----------+-----+---------+

### SHOW ALL BGP ADVERTISED ROUTES TO N2 AFTER RCF POLICY IS APPLIED
+----------------+------------------+-----+-----------+---------------------+----------+-----+---------+
| BGP ROUTES     | LOCAL-PREFERENCE | MED | COMMUNITY | EXT-COMMUNITY       | NEXT-HOP | TAG | AS-PATH |
+----------------+------------------+-----+-----------+---------------------+----------+-----+---------+
| 50.0.0.255/32  | 100              | 0   | ['0:20']  | ['Color:CO(00):20'] | 10.0.0.3 | 0   | 65001   |
| 200.0.0.255/32 | 100              | 0   | ['0:80']  | []                  | 10.0.0.3 | 0   | 65001   |
| 125.0.0.255/32 | 100              | 0   | ['0:50']  | ['Color:CO(00):50'] | 10.0.0.3 | 0   | 65001   |
| 25.0.0.255/32  | 100              | 0   | ['0:10']  | ['Color:CO(00):10'] | 10.0.0.3 | 0   | 65001   |
| 75.0.0.255/32  | 100              | 0   | ['0:30']  | ['Color:CO(00):30'] | 10.0.0.3 | 0   | 65001   |
| 175.0.0.255/32 | 100              | 0   | ['0:70']  | ['Color:CO(00):70'] | 10.0.0.3 | 0   | 65001   |
| 150.0.0.255/32 | 100              | 0   | ['0:60']  | ['Color:CO(00):60'] | 10.0.0.3 | 0   | 65001   |
| 100.0.0.255/32 | 100              | 0   | ['0:40']  | ['Color:CO(00):40'] | 10.0.0.3 | 0   | 65001   |
+----------------+------------------+-----+-----------+---------------------+----------+-----+---------+
```

## Step 3 - Push the RCF policy

The script will then push the RCF policy to the /mnt/flash directory.  If the policy was to be evaluated as inbound the file will be called `RCF-in.txt`.  If the policy was to be evaluated as outbound the file will be called `RCF-out.txt`

The N2 DUT compiles and commits the script and the applies it to the BGP neighbor.

The script will show you what's been commited as show below.

```
#################### PUSHING THE FOLLOWING POLICY TO THE NODE ####################

#########################FUNCTION########################
function  ADVERTISE_AS8068  () {
#########################TERM############################
#  ALLOW_8068_OVERLOAD  
#########################################################
# if source_protocol is BGP and
if as_path match as_path_list AS8068 and
ext_community match ext_community_list COLOR_10293 {
local_preference = 10 ;
return true ;
#########################TERM############################
#  ALLOW_8068  
#########################################################
#} else if source_protocol is BGP and
} else if as_path match as_path_list AS8068 {
return true ;
  }
}
```

## Step 4 - Post-policy Evaluation

The script will evaluate what the DUT is recieving after the RCF policy.

In this example we see this printed below:

```
#################### SHOW DATA AFTER THE POLICY ####################
### SHOW ALL ROUTES ON N1
+---------------+------------+
| ROUTE         | ROUTE-TYPE |
+---------------+------------+
| 50.0.0.255/32 | eBGP       |
| 10.0.0.0/31   | connected  |
| 25.0.0.255/32 | eBGP       |
| 10.0.0.2/31   | connected  |
+---------------+------------+

### SHOW ALL BGP LEARNED ROUTES FROM N1 AFTER RCF POLICY IS APPLIED
+---------------+------------------+-----+-----------+------------------------+----------+-----+------------+
| BGP ROUTES    | LOCAL-PREFERENCE | MED | COMMUNITY | EXT-COMMUNITY          | NEXT-HOP | TAG | AS-PATH    |
+---------------+------------------+-----+-----------+------------------------+----------+-----+------------+
| 50.0.0.255/32 | 100              | 0   | ['0:20']  | ['Color:CO(00):20']    | 10.0.0.3 | 0   | 65001 8068 |
| 25.0.0.255/32 | 10               | 0   | ['0:10']  | ['Color:CO(00):10293'] | 10.0.0.3 | 0   | 65001 8068 |
+---------------+------------------+-----+-----------+------------------------+----------+-----+------------+

### SHOW ALL BGP ADVERTISED ROUTES TO N2 AFTER RCF POLICY IS APPLIED
+---------------+------------------+-----+-----------+------------------------+----------+-----+------------+
| BGP ROUTES    | LOCAL-PREFERENCE | MED | COMMUNITY | EXT-COMMUNITY          | NEXT-HOP | TAG | AS-PATH    |
+---------------+------------------+-----+-----------+------------------------+----------+-----+------------+
| 50.0.0.255/32 | 100              | 0   | ['0:20']  | ['Color:CO(00):20']    | 10.0.0.3 | 0   | 65001 8068 |
| 25.0.0.255/32 | 10               | 0   | ['0:10']  | ['Color:CO(00):10293'] | 10.0.0.3 | 0   | 65001 8068 |
+---------------+------------------+-----+-----------+------------------------+----------+-----+------------+
```


Here we can see that the policy works!   
v4 Routes with color 10293 and an as path with 8068 get local pref equal to 10.   
v4 Routes with an as path of 8068 and no color are allowed and no local pref changes.

## NOTES
<u>Version 1.0 Planned Fixes </u>    
- Topology builder needs to be bug fixed.  
- RCF Policy logic needs to be validated with more scenarios.  
