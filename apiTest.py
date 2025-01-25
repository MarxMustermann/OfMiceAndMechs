import requests

x = requests.get("http://127.0.0.1:5000/",json={"type":"renderTerrain","x":3,"y":8})
print(x.text)
