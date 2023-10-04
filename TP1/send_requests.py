import json
import requests
from threading import Thread
import time
import boto3

def consumeGETRequestSync(url_lb,path):
    url="http://{}/{}".format(url_lb, path)
    print(url)
    headers={'content-type': 'application/json'}
    r=requests.get(url,headers=headers)
    print(r.status_code)
    print(r.json(),end=' status ')

def first_thread(lb_dns,path):
    print('Starting sending 1000 requests')
    for _ in range(100):
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

if __name__=='__main__':
    
    client = boto3.client('elbv2', region_name='us-east-1',)

    url = client.describe_load_balancers()['LoadBalancers'][0]['DNSName']
    
    first_sending_thread=Thread(target=first_thread,args=(url,'cluster1'))
    second_sending_thread=Thread(target=second_thread,args=(url,'cluster2'))

    first_sending_thread.start()
    second_sending_thread.start()

    first_sending_thread.join()
    second_sending_thread.join()

    print('script terminated')
