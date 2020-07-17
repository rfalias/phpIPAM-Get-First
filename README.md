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
VLANName:prod_vlan203
```
