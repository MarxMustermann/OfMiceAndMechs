import requests
import time

time1 = time.time()
print(time1)
x = requests.post("http://127.0.0.1:5000/",data={"type":"renderTerrain","x":3,"y":8,"vSizeX":5,"vSizeY":5,"vOffsetX":50,"vOffsetY":50})
result = x.json()
time2 = time.time()
print(time2)

print(result)

x = requests.post("http://127.0.0.1:5000/",data={"type":"addItem","terrainX":3,"terrainY":8,"x":52,"y":52,"itemType":"Bolt"})
result = x.json()

x = requests.post("http://127.0.0.1:5000/",data={"type":"renderTerrain","x":3,"y":8,"vSizeX":5,"vSizeY":5,"vOffsetX":50,"vOffsetY":50})
result = x.json()
print(result)

print(time1)
print(time2)
