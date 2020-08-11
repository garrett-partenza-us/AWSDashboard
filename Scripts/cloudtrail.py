#import needed modules
import json
from elasticsearch import Elasticsearch
from collections.abc import Mapping
from ip2geotools.databases.noncommercial import DbIpCity
import boto3
import gzip
import io

#fresh dictionary to send to elasticsearch 
build_doc={}

#recursively convert multilayer dictioary to a single layer
def recursiveAppend(value):

    for key, value in value.items():
        if isinstance(value, dict):
            recursiveAppend(value)
        else:
            build_doc[key]=value
   
#function that executes on trigger
#passes in event (contains bukcet name and key) and context
def lambda_handler(event, context):
    
    false="false"
    true="true"
    null="null"
    es = Elasticsearch(['https://dso-es.digitalization-demo-test.com/'], scheme="https", port=443, http_auth=('gpartenza', 'gpartenza'))
    
    #iterate over all events
    for record in event['Records']:
        
        #get bucket and key
        s3client = boto3.client('s3')
        bucket = str(event['Records'][0]['s3']['bucket']['name']).strip()
        key = str(event['Records'][0]['s3']['object']['key']).strip()
        
        #use bucket and key along with boto3 to read event details
        response = s3client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read()
   
        with gzip.GzipFile(fileobj=io.BytesIO(content), mode='rb') as f:
             data = json.loads(f.read(), encoding="utf-8")
             data = data['Records'][0]
                
             #convert dictionary depth to one
             recursiveAppend(data)
                
             #if the event has a geo-ip, index it to a unique index in elasticsearch called "cloudtrail_geoip"
             try:
                 response = DbIpCity.get(str(data['sourceIPAddress']), api_key='free')
                 lat = (response.latitude)
                 lon = (response.longitude)
                 sourceIP = {}
                 sourceIP['geo'] = {'location':(str(lat)+","+str(lon))}
                 es.index(index='cloudtrail_geoip', body=sourceIP)
             except Exception as e:
                 pass
             
             #finally index the event detailed data to elasticsearch index called "cloudtrail"
             es.index(index='cloudtrail', body=build_doc)

