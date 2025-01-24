#!/usr/bin/env python3

"""
HOST = "ofmiceandmechs.com" #input("enter server address")  # The server's hostname or IP address
PORT = 23  # The port used by the server
"""

import gzip
import json
import socket
import time

import tcod

HOST = "127.0.0.1" #input("enter server address")  # The server's hostname or IP address
PORT = 65487  # The port used by the server

screen_width = 200
screen_height = 51

tileset = tcod.tileset.load_tilesheet(
    "scaled_8x16.png", 16, 16, tcod.tileset.CHARMAP_CP437
)

context = tcod.context.new_terminal(
                         screen_width,
                         screen_height,
                         tileset=tileset,
                         title="OfMiceAndMechs",
                         vsync=True,
                     )

root_console = tcod.Console(screen_width, screen_height, order="F")

mana = 0
maxMana = 10
available_actions = {
        "M":{"action":"spawn enemy","cost":50},
        "H":{"action":"heal","cost":5},
        "s":{"action":"speed boost","cost":2},
        "S":{"action":"stun","cost":20},
        "+":{"action":"increase game speed","cost":0},
        "-":{"action":"decrease game speed","cost":0},
        }

def draw(raw):
    offsetX = 20
    offsetY = 5
    root_console.clear()
    y=0
    for line in raw:
        x = 0
        for char in line:
            if char is None:
                continue
            if char == "\n":
                1/0
            if char == "":
                x += 1
                continue
            if isinstance(char,str):
                if "\n" in char:
                    1/0
                root_console.print(x=x+offsetX,y=y+offsetY,string=char,fg=(255,255,255),bg=(0,0,0))
                x += len(char)
            else:
                root_console.print(x=x+offsetX,y=y+offsetY,string=char[1],fg=tuple(char[0][0]),bg=tuple(char[0][1]))
                x += len(char[1])
        y += 1
    root_console.print(x=5,y=0,string=f"mana: {mana}/{maxMana} manaRegen: 1/s")

    counter = 3
    for (key,value) in available_actions.items():
        root_console.print(x=2,y=counter,string=f"{key} ({value['cost']}): {value['action']}")
        counter += 1

    context.present(root_console)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.setblocking(False)

dataString = b""
def getData():
        global dataString
        while True:
            try:
                part = s.recv(1024)
            except:
                part = None

            if not part:
                break

            dataString += part

        if b"\n-*_*-\n" not in dataString:
            return None
        valuepart = dataString.split(b"\n-*_*-\n")[0]
        dataString = dataString.split(b"\n-*_*-\n")[-1]

        valuepart = gzip.decompress(valuepart)
        return valuepart.decode("utf-8")

commands = ["~"]
actions = []

def sendKeystrokes():
    getTcodEvents()
    global commands
    global actions
    if not commands and not actions:
        return
    info = {"commands":commands,"actions":actions}
    info = json.dumps(info)
    data = info.encode("utf-8")
    s.sendall(data+b"\n")
    commands = []
    actions = []

def getTcodEvents():
    global commands
    global mana

    events = tcod.event.get()

    for event in events:
        if isinstance(event, tcod.event.Quit):
            raise SystemExit()
        if isinstance(event, tcod.event.WindowEvent):
            if event.type == "WINDOWCLOSE":
                raise SystemExit()
            if event.type == "WINDOWEXPOSED":
                commands.append("~")
        if isinstance(event,tcod.event.MouseButtonDown):# or isinstance(event,tcod.event.MouseButtonUp):
            pass
            """
            tcodContext.convert_event(event)
            clickPos = (event.tile.x,event.tile.y)
            if src.gamestate.gamestate.clickMap:
                if not clickPos in src.gamestate.gamestate.clickMap:
                    continue

                value = src.gamestate.gamestate.clickMap[clickPos]
                if isinstance(value,str) or isinstance(value,list):
                    src.gamestate.gamestate.mainChar.runCommandString(value,nativeKey=True)
                elif isinstance(value,dict):
                    if not "params" in value:
                        value["params"] = {}
                    value["params"]["event"] = event
                    src.saveing.Saveable.callIndirect(None,value)
                else:
                    value()

            if isinstance(event,tcod.event.MouseButtonUp):
                src.gamestate.gamestate.dragState = None
            """

        if isinstance(event,tcod.event.TextInput):
            translatedKey = event.text

            if translatedKey is None:
                continue

            if translatedKey in available_actions:
                cost = available_actions[translatedKey]["cost"]
                if mana >= cost:
                    actions.append(available_actions[translatedKey]["action"])
                    mana -= cost
            else:
                commands.append(translatedKey)

        if isinstance(event,tcod.event.KeyDown):
            key = event.sym
            translatedKey = None
            if key == tcod.event.KeySym.LSHIFT:
                continue
            if key == tcod.event.KeySym.RETURN:
                translatedKey = "enter"
            if key == tcod.event.KeySym.BACKSPACE:
                translatedKey = "backspace"
            if key == tcod.event.KeySym.SPACE:
                translatedKey = " "
            if key == tcod.event.KeySym.PERIOD:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = ":"
                else:
                    translatedKey = "."
            if key == tcod.event.KeySym.HASH:
                translatedKey = "#"
            if key == tcod.event.KeySym.ESCAPE:
                if event.mod in (tcod.event.Modifier.RSHIFT,):
                    translatedKey = "rESC"
                elif event.mod in (tcod.event.Modifier.LSHIFT,):
                    translatedKey = "lESC"
                elif event.mod in (tcod.event.Modifier.SHIFT,):
                    translatedKey = "ESC"
                else:
                    translatedKey = "esc"
            if key == tcod.event.KeySym.i:
                if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                    translatedKey = "ctrl i"

            if translatedKey is None:
                print(event)
                continue

            commands.append(translatedKey)


lastTime = time.time()
while 1:
    if (time.time() - lastTime) > 1:
        mana = min(maxMana,mana+1)
        lastTime += 1
    data = getData()
    if data not in [None,""]:
        raw = json.loads(data)
        if "pseudoDisplay" in raw:
            draw(raw["pseudoDisplay"])

    sendKeystrokes()
    time.sleep(0.01)
