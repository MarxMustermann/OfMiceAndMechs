import requests
import time

time1 = time.time()
print(time1)
x = requests.get("http://127.0.0.1:5000/",json={"type":"renderTerrain","x":3,"y":8})
x.text
time2 = time.time()
print(time2)
result = x.json()
print(result)
print(time1)
print(time2)
print(result["lookUp"])
