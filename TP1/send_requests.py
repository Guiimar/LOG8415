import json
import requests

def consumeGETRequestSync(url_lb):
    url=url_lb
    r=requests.get(url)
    print(r.status_code)
    print(r.json(),end=' status ')
