from elasticsearch import Elasticsearch
import os
import sys
import subprocess
import json
import ssl
from datetime import datetime


def send(form):
    
    wanted = ["assetType", "numericSeverity", "confidence", "title", "description", "hostname", "agentId", "publicDnsName", "privateIpAddress", "publicIpAddress", "id", "recommendation"] 
    new = {}
    def iterdict(d):
       
        for k, v in d.items():
            if isinstance(v, dict):
                iterdict(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item,dict):
                        iterdict(item)
            else:
                try: v=' '.join(v.split())
                except: pass
                try: v=v.decode("utf-8")
                except: pass
                try: k = k.decode("utf-8") 
                except: pass
                
                try:
                    if k in wanted:
                        if k == "numericSeverity":
                            new[str(k)] = int(v)
                        else:
                            new[str(k)] = v
                except:
                    pass
        return(new)
    form = iterdict(form)
    form["timestamp"] = datetime.now()
    es = Elasticsearch(['https://dso-es.digitalization-demo-test.com/'], scheme="https", port=443, http_auth=('gpartenza', 'gpartenza'))
    es.index(index="inspector", body = form)
    

def find(run_arn):
    output = subprocess.check_output("aws inspector list-findings --assessment-run-arns "+str(run_arn), shell=True)
    output = output.decode("utf-8")
    output = json.loads(output)
    list_findings = output["findingArns"]
    
    
    find_f = open("findings_test.txt", "w")
    for finding in list_findings:
        findings = get(finding.decode("utf-8"))

def get(finding_arn):
    output = subprocess.check_output("aws inspector describe-findings --finding-arns "+str(finding_arn), shell=True)
    output = output.decode("utf-8")
    output = json.loads(output)
    
    send(output)
    

f = open("/home/ubuntu/Inspector/arn.txt", "r")
find(json.loads(f.read())["assessmentRunArn"].strip())
print("Findings gathered")
