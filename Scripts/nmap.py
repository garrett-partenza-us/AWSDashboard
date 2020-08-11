#Import packacges
import os
from datetime import datetime
import sys
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime
from elasticsearch import Elasticsearch
import json
import ssl


#Takes in dictionary, sends to elasticsearch
def send(d):

    d["timestamp"] = datetime.utcnow()
    es = Elasticsearch(['https://dso-es.digitalization-demo-test.com/'], scheme="https", port=443, http_auth=('gpartenza', 'gpartenza'))
    es.index(index="nmap", body = d)


#Scan target for operating system
def os_scan(ip, target):
    p = Popen("sudo nmap "+str(ip)+" -O", shell=True, stdout=PIPE, stderr=STDOUT)
    output = p.stdout.read()
    output = output.decode("utf-8")
    output=output.replace("hackthissite.org","")
    form = {"ScanType":"OS Detection Scan", "target":target, "ip":targets[target][1], "id":targets[target][0], "scan":output}   
    send(form)

#Scan target for ports
def port_scan(ip, target):
    p = Popen("sudo nmap "+str(ip)+" -O", shell=True, stdout=PIPE, stderr=STDOUT)
    output = p.stdout.read()
    output = output.decode("utf-8")
    output=output.replace("hackthissite.org","")
    form = {"ScanType":"Port Scan", "target":target, "ip":targets[target][1], "id":targets[target][0], "scan":output}
    send(form)

#Scan target for version detection
def version_scan(ip, target):
    p = Popen("sudo nmap "+str(ip)+" -O", shell=True, stdout=PIPE, stderr=STDOUT)
    output = p.stdout.read()
    output = output.decode("utf-8")
    output=output.replace("hackthissite.org","")
    form = {"ScanType":"Version Detection Scan", "target":target, "ip":targets[target][1], "id":targets[target][0], "scan":output}
    send(form)

#Scan target with firewall spoofing
def spoof_firewall_scan(ip, target):

    p = Popen("sudo nmap "+str(ip)+" -O", shell=True, stdout=PIPE, stderr=STDOUT)
    output = p.stdout.read()
    output = output.decode("utf-8")
    output=output.replace("hackthissite.org","")
    form = {"ScanType":"Firewall Spoof Scan", "target":target, "ip":targets[target][1], "id":targets[target][0], "scan":output}
    send(form)

#Main
def main():
    for target in targets:

        os_scan(targets[target][1], target)
        port_scan(targets[target][1], target)
        version_scan(targets[target][1], target)
        spoof_firewall_scan(targets[target][1], target)

#Targets
targets = {"DevSecOps SonarQube":["i-071d90c18e8b28b1b", "137.74.187.100"], "Machine-learning-models":["i-0ca8dde4ae1640ac8", "184.168.131.241"]}


print("started")
if __name__ == "__main__":

    main()
