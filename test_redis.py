from redis import Redis
from subprocess import Popen
import time

redis_server = Popen('redis-server --port 6380', shell=True)
time.sleep(1)


redis_obj = Redis(host='localhost', port=6380, decode_responses=True)

redis_obj.set("test", "testing")
print("The value of test keys is", redis_obj.get("test"))

print("The keys is", redis_obj.keys())

redis_server.kill()
