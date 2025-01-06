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
PORT = 65481  # The port used by the server

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

def draw(raw):
    print("draw")
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
                root_console.print(x=x,y=y,string=char,fg=(255,255,255),bg=(0,0,0))
                x += len(char)
            else:
                root_console.print(x=x,y=y,string=char[1],fg=tuple(char[0][0]),bg=tuple(char[0][1]))
                x += len(char[1])
        y += 1
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

def sendKeystrokes():
    getTcodEvents()
    global commands
    if not commands:
        return
    info = {"commands":commands}
    info = json.dumps(info)
    data = info.encode("utf-8")
    s.sendall(data+b"\n")
    commands = []

def getTcodEvents():
    global commands

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
            if key == tcod.event.KeySym.N1:
                translatedKey = "1"
            if key == tcod.event.KeySym.N2:
                translatedKey = "2"
            if key == tcod.event.KeySym.N3:
                translatedKey = "3"
            if key == tcod.event.KeySym.N4:
                translatedKey = "4"
            if key == tcod.event.KeySym.N5:
                translatedKey = "5"
            if key == tcod.event.KeySym.N6:
                translatedKey = "6"
            if key == tcod.event.KeySym.N7:
                translatedKey = "7"
            if key == tcod.event.KeySym.N8:
                translatedKey = "8"
            if key == tcod.event.KeySym.N9:
                translatedKey = "9"
            if key == tcod.event.KeySym.N0:
                translatedKey = "0"
            if key == tcod.event.KeySym.COMMA:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = ";"
                else:
                    translatedKey = ","
            if key == tcod.event.KeySym.MINUS:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "_"
                else:
                    translatedKey = "-"
            if key == tcod.event.KeySym.PLUS or key == tcod.event.KeySym.KP_PLUS:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "*"
                else:
                    translatedKey = "+"
            if key == tcod.event.KeySym.a:
                if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                    translatedKey = "ctrl a"
                elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "A"
                else:
                    translatedKey = "a"
            if key == tcod.event.KeySym.b:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "B"
                else:
                    translatedKey = "b"
            if key == tcod.event.KeySym.c:
                if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                    translatedKey = "ctrl c"
                elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "C"
                else:
                    translatedKey = "c"
            if key == tcod.event.KeySym.d:
                if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                    translatedKey = "ctrl d"
                elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "D"
                else:
                    translatedKey = "d"
            if key == tcod.event.KeySym.e:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "E"
                else:
                    translatedKey = "e"
            if key == tcod.event.KeySym.f:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "F"
                else:
                    translatedKey = "f"
            if key == tcod.event.KeySym.g:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "G"
                else:
                    translatedKey = "g"
            if key == tcod.event.KeySym.h:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "H"
                else:
                    translatedKey = "h"
            if key == tcod.event.KeySym.i:
                if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                    translatedKey = "ctrl i"
                elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "I"
                else:
                    translatedKey = "i"
            if key == tcod.event.KeySym.j:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "J"
                else:
                    translatedKey = "j"
            if key == tcod.event.KeySym.k:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "K"
                else:
                    translatedKey = "k"
            if key == tcod.event.KeySym.l:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "L"
                else:
                    translatedKey = "l"
            if key == tcod.event.KeySym.m:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "M"
                else:
                    translatedKey = "m"
            if key == tcod.event.KeySym.n:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "N"
                else:
                    translatedKey = "n"
            if key == tcod.event.KeySym.o:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "O"
                else:
                    translatedKey = "o"
            if key == tcod.event.KeySym.p:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "P"
                else:
                    translatedKey = "p"
            if key == tcod.event.KeySym.q:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "Q"
                else:
                    translatedKey = "q"
            if key == tcod.event.KeySym.r:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "R"
                else:
                    translatedKey = "r"
            if key == tcod.event.KeySym.s:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "S"
                else:
                    translatedKey = "s"
            if key == tcod.event.KeySym.t:
                if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                    translatedKey = "ctrl t"
                elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "T"
                else:
                    translatedKey = "t"
            if key == tcod.event.KeySym.u:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "U"
                else:
                    translatedKey = "u"
            if key == tcod.event.KeySym.v:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "V"
                else:
                    translatedKey = "v"
            if key == tcod.event.KeySym.w:
                if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                    translatedKey = "ctrl w"
                elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "W"
                else:
                    translatedKey = "w"
            if key == tcod.event.KeySym.x:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "X"
                else:
                    translatedKey = "x"
            if key == tcod.event.KeySym.y:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "Y"
                else:
                    translatedKey = "y"
            if key == tcod.event.KeySym.z:
                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                    translatedKey = "Z"
                else:
                    translatedKey = "z"

            if translatedKey is None:
                print(event)
                continue

            commands.append(translatedKey)


while 1:
    data = getData()
    if data not in [None,""]:
        raw = json.loads(data)
        if "pseudoDisplay" in raw:
            draw(raw["pseudoDisplay"])

    sendKeystrokes()
    time.sleep(0.01)
