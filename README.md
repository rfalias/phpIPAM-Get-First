**Pull next address from a phpIPAM server**
Reserves a new address, supplied by a given VLAN ID.

Ensure vlan id is correctly configured in all subnets.

Return data is in a 'grep' style format for easy consumption by scripts

Example:
```
python get_next_address.py -v 203 -a APPNAME -t SECRET_KEY -n "HOSTNAME_WANTED" -i https://phpipam.local

Hostname:testfrompywq
IPAddress:10.200.16.3
Netmask:255.255.240.0
DNSServers:10.200.17.7 10.200.17.8
VLANName:vlan203
```

```
usage: get_next_address.py [-h] [-v VLAN] [-d DVLAN] -a APP -t TOKEN -n NAME
                           -i IPAM [--allow-duplicate]

Get next available IP address in a sepcific vlan

optional arguments:
  -h, --help            show this help message and exit
  -v VLAN, --vlan VLAN  VLAN ID to get Next Available IP Address from.
                        Overrides --dvlan
  -d DVLAN, --dvlan DVLAN
                        Detailed vlan name to get next address from
  -a APP, --app APP     App ID for phpIPAM,check the API section
  -t TOKEN, --token TOKEN
                        API Token for phpIPAM
  -n NAME, --name NAME  Hostname making the reservation
  -i IPAM, --ipam IPAM  Base URL of IPAM server: https://ipam.local
  --allow-duplicate     Allow requesting of duplicate hostnames

```
