from redis import Redis
from subprocess import Popen
import time

redis_server = Popen('redis-server')
time.sleep(1)


redis_obj = Redis(host='127.0.0.1', port=6379, decode_responses=True)

redis_obj.set("test", "testing")
print("The value of test keys is", redis_obj.get("test"))

print("The keys is", redis_obj.keys())

redis_server.kill()
