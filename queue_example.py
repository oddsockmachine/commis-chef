from redis import Redis
from rq import Queue

q = Queue('low', connection=Redis('127.0.0.1', 6379))

from my_module import count_words_at_url
for i in range(10):
    result = q.enqueue(count_words_at_url, 'http://nvie.com', 1)
