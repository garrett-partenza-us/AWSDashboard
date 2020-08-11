#import necessary modules
from elasticsearch import Elasticsearch
import io
import gzip
import json
import boto3
from urllib.parse import unquote_plus
import ast


#function executes on trigger
#passes in event (contains bucket name and key) and context
def lambda_handler(event, context):
    
    #specify elasticsearch endpoint
    es = Elasticsearch(['https://dso-es.digitalization-demo-test.com/'], scheme="https", port=443, http_auth=('gpartenza', 'gpartenza'))
    
    #iterate over all recieved events
    s3client = boto3.client('s3')
    for record in event['Records']:
        
        #extract the bucket name and key name to pull the hard details of the threat
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        response = s3client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read()
        
        #decompress
        with gzip.GzipFile(fileobj=io.BytesIO(content), mode='rb') as fh:
            
            #format multiple jsons into a list of jsons
            new_str = fh.read()
            new_str = new_str.decode('utf-8')
            raw_str = (repr(new_str))
            dict_list = raw_str.split("\\n")
            false="false"
            true="true"
            null="null"
            dict_list = dict_list[:-1]
            
            #iterate over list of jsons and format to send to elasticsearch
            for d in dict_list:
                try:
                    d = d.replace("'","\"")
                    d = d.replace("\\n","")
                    if d[0]=="\"":
                        d=d[1:]
                    dict = json.loads(d)
                    
                    #only take what we want
                    build_doc = {}
                    build_doc["threat_id"] = dict["id"]
                    build_doc["doc_type"] = "_doc"
                    build_doc["region"] = dict["region"]
                    build_doc["arn"] = dict["arn"]
                    build_doc["type"] = dict["type"]
                    build_doc["severity"] = dict["severity"]
                    build_doc["time"] = dict["createdAt"]
                    build_doc["title"] = dict["title"]
                    build_doc["description"] = dict["description"]
                    try:
                        build_doc["ipAddressV4"] = (dict["service"]["action"]["awsApiCallAction"]["remoteIpDetails"]["ipAddressV4"])
                    except:
                        pass
                    try:
                        build_doc["org"] = (dict["service"]["action"]["awsApiCallAction"]["remoteIpDetails"]["organization"]["org"])
                    except:
                        pass
                    try:
                        build_doc["countryName"] = (dict["service"]["action"]["awsApiCallAction"]["remoteIpDetails"]["country"]["countryName"])
                    except:
                        pass
                    try:
                        build_doc["cityName"] = (dict["service"]["action"]["awsApiCallAction"]["remoteIpDetails"]["city"]["cityName"])
                    except:
                        pass
                    
                    #send geo_ip of threat to elasticsearch if it exists 
                    try:
                        es_entries = {}
                        es_entries['geo'] = { 'location': (str(dict["service"]["action"]["awsApiCallAction"]["remoteIpDetails"]["geoLocation"]["lat"])).strip()+","+(str(dict["service"]["action"]["awsApiCallAction"]["remoteIpDetails"]["geoLocation"]["lon"])).strip()}
                        es_entries['threat_type'] = dict["type"]
                        es_entries['arn'] = dict["arn"]
                        es_entries['severity'] = dict["severity"]
                        es_entries['description'] = dict["description"]
                        
                        es.index(index="guard_duty_cord", body=es_entries)

                    except:
                        pass
                    
                    #index data to elasticsearch
                    es.index(index='guard_duty', body=build_doc)
                except Exception as e:
                    print("Could not send data for "+str(d))
                    print(e)
