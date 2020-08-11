#import elastic search module to send data
from elasticsearch import Elasticsearch
#import datetime module to timestamp data
from datetime import datetime

#lambda function executes on trigger
def lambda_handler(event, context):
    
    #specify endpoint
    es = Elasticsearch(['https://dso-es.digitalization-demo-test.com/'], scheme="https", port=443, http_auth=('gpartenza', 'gpartenza'))
    
    #timestamp data
    event["timestamp"] = datetime.utcnow()
    
    #send data to elasticsearch
    es.index(index='codepipeline', body=event)
