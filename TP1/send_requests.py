import json
import requests

from threading import Thread
import time
import boto3

def consumeGETRequestSync(url_lb,path):
    url="http://{}/{}".format(url_lb, path)
    print(url)
    #headers={'content-type': 'application/json'}
    r=requests.get(url)
    print(r.status_code)
    print(r.json(),end=' status ')

def first_thread(lb_dns,path):
    print('Starting sending 1000 requests')
    for _ in range(1000):
        consumeGETRequestSync(lb_dns,path)
    print('Finished sending 1000 requests')

#5OO requests then 60 seconds sleep then 1000 requests
def second_thread(lb_dns,path):
    for _ in range(500):
        consumeGETRequestSync(lb_dns,path)
    
    time.sleep(60)

    for _ in range(1000):
        consumeGETRequestSync(lb_dns,path)

    print('Finished sending 500 plus 1000 requests ')

