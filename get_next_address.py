#!/usr/bin/env python
import argparse
from urlparse import urlparse
from urlparse import urljoin
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import socket
import struct
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(description='Get next available IP address in a sepcific vlan')
parser.add_argument('-v', '--vlan', required=False, help="VLAN ID to get Next Available IP Address from. Overrides --dvlan")
parser.add_argument('-d', '--dvlan', required=False, help="Detailed vlan name to get next address from")
parser.add_argument('-a', '--app', required=True, help="App ID for phpIPAM,check the API section")
parser.add_argument('-t', '--token', required=True, help="API Token for phpIPAM")
parser.add_argument('-n', '--name', required=True, help="Hostname making the reservation")
parser.add_argument('-i', '--ipam', required=True, help="Base URL of IPAM server: https://ipam.local")
parser.add_argument('--allow-duplicate', required=False, action='store_true', help="Allow requesting of duplicate hostnames")

class reservation:
    def __init__(self):
        self.hostname = None
        self.ip_address = None
        self.netmask = None
        self.dns = None
        self.description = None


def cidr_to_netmask(cidr):
    network, net_bits = cidr.split('/')
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return netmask


def resolve_vlan(vlanid, app, token, res, url):
    token_head = {"token": token}
    u = urljoin(url, 'api/%s/vlan/%s' % (app,vlanid))
    response = requests.get(u, headers=token_head, verify=False)
    return response.json()['data']['number']

def get_subnets_by_vlan(vlan, app, token, res, url):
    token_head = {"token": token}
    u = urljoin(url, 'api/%s/subnets/all' % app)
    response = ""
    try:
        response = requests.get(u, headers=token_head, verify=False)
    except Exception as E:
        print("Error connecting: %s" % E)
        exit(-3)
    for x in response.json()['data']:
        desc = x['description']
        res_vlan = resolve_vlan(x['vlanId'], app, token, res, url)
        if vlan in res_vlan:
            ns = []
            try:
                ns = x['nameservers']['namesrv1'].split(';')
            except:
                ns = []

            res.dns = ns
            res.description = desc
            res.netmask = x['mask']
            return x['id']


def get_subnets_by_id(vid, app, token, res, url):
    token_head = {"token": token}
    u = urljoin(url, 'api/%s/subnets/%s' % (app,vid))
    response = ""
    try:
        response = requests.get(u, headers=token_head, verify=False)
    except Exception as E:
        print("Error connecting: %s" % E)
        exit(-3)
    data = response.json()['data']
    ns = []
    try:
        ns = data['nameservers']['namesrv1'].split(';')
    except:
        ns = []
    res.dns = ns
    res.description = data['description']
    res.netmask = data['mask']
    return data['id']


def get_subnets_by_desc(vlan, app, token, res, url):
    token_head = {"token": token}
    u = urljoin(url, 'api/%s/subnets/all' % app)
    response = ""
    try:
        response = requests.get(u, headers=token_head, verify=False)
    except Exception as E:
        print("Error connecting: %s" % E)
        exit(-3)
    for x in response.json()['data']:
        desc = x['description']
        #res_vlan = resolve_vlan(x['vlanId'], app, token, res, url)
        if vlan in desc:
            ns = []
            try:
                ns = x['nameservers']['namesrv1'].split(';')
            except:
                ns = []

            res.dns = ns
            res.description = desc
            res.netmask = x['mask']
            return x['id']


def search_hostname(app, token, res, url):
    token_head = {"token": token}
    u = urljoin(url, 'api/%s/addresses/search_hostname/%s' % (app,res.hostname))
    response = ""
    try:
        response = requests.get(u, headers=token_head, verify=False)
    except Exception as E:
        print("Error connecting: %s" % E)
        exit(-3)
    if not response.json()['success']:
        return False
    res.ip_address = response.json()['data'][0]['ip']
    vid = response.json()['data'][0]['subnetId']
    snID = get_subnets_by_id(vid, app, token, res, url)
    return res

def pretty_print(res):
    print("Hostname:%s"%res.hostname)
    print("IPAddress:%s"%res.ip_address)
    print("Netmask:%s"% cidr_to_netmask("%s/%s"%(res.ip_address, res.netmask)))
    print("DNSServers:%s"%" ".join(res.dns))
    print("VLANName:%s"%res.description)


def reserve_address(vlan_id, app, token, res, url):
    head = {
            "token": token,
            'Content-Type': 'application/json'
           }
    d = "{\"hostname\":\"%s\"}" % res.hostname
    req_u = urljoin(url, "/api/%s/addresses/first_free/%s/" % (app,vlan_id))
    req_ip = requests.request("POST", req_u, headers=head, verify=False)
    res.ip_address = req_ip.json()['data']
    ip_id = req_ip.json()['id']
    req_p = urljoin(url, "api/%s/addresses/%s/"  % (app, ip_id))
    requests.request("PATCH", req_p, headers=head, data=d, verify=False)


if __name__ == "__main__":
    res = reservation()
    args = parser.parse_args()
    res.hostname = args.name
    url = urljoin(args.ipam,'/api/%s/subnets/all')
    vl_id =""
    do_search = False
    if not args.allow_duplicate:
        do_search = search_hostname(args.app, args.token, res, args.ipam)
    if do_search:
        print("Existing record found")
        pretty_print(res)
        exit(0)
    if args.vlan:
        vl_id = get_subnets_by_vlan(args.vlan, args.app, args.token, res, args.ipam)
    elif args.dvlan:
        vl_id = get_subnets_by_desc(args.dvlan, args.app, args.token, res, args.ipam)

    if (vl_id == "" or vl_id <= 0):
        print("No vlan found")
        exit(-5)
    reserve_address(vl_id, args.app, args.token, res, args.ipam)
    pretty_print(res)
