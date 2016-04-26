from flask import Flask, request
from parse_hook import *
app = Flask(__name__)
from redis import Redis
from rq import Queue

q = Queue('normal', connection=Redis('192.168.99.100', 6379))


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/githook', methods=['GET', 'POST'])
def githook():
    print "githook received...",
    data = request.get_json()
    commit = data.get("after")
    print "data decoded...",
    print commit,
    result = q.enqueue(handle_push, data)
    print "job added to queue\n"
    return 'Hook received and added to work queue'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
