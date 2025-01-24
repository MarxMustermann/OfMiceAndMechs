import requests

x = requests.get("http://127.0.0.1:5000/",json={"type":"runCode","code":'result = {"tick":src.gamestate.gamestate.tick+2000}'})
print(x.text)
