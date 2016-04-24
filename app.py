from flask import Flask, request
from parse_hook import *
app = Flask(__name__)
from redis import Redis
from rq import Queue
from my_module import count_words_at_url

q = Queue('normal', connection=Redis('192.168.99.100', 6379))


@app.route('/')
def hello_world():
    result = q.enqueue(count_words_at_url, 'http://nvie.com', 1)
    return 'Hello World!'

@app.route('/githook', methods=['GET', 'POST'])
def githook():
    print "githook received...",
    data = request.get_json()
    print "data decoded...",
    result = q.enqueue(handle_push, data)
    print "job added to queue\n"
    return 'Hook received and added to work queue'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
