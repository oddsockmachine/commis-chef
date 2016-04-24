from time import sleep
import requests
from datetime import datetime

def count_words_at_url(url, wait=0):
    resp = requests.get(url)
    result = len(resp.text.split())
    sleep(wait)
    print datetime.now()
    print result
    return result
