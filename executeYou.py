#!/usr/bin/env python3

import socket

import time
import json
import urwid

HOST = input("enter server adress")  # The server's hostname or IP address
PORT = 65440  # The port used by the server

header = urwid.Text(u"")
main = urwid.Text(u"")
footer = urwid.Text(u"")

main.set_layout('left', 'clip')

frame = urwid.Frame(urwid.Filler(main, "top"), header=header, footer=footer)


def draw(raw):
    def deserializeUrwid(inData):
        outData = []
        for item in inData:
            if item[0] == "tuple":
                outData.append((urwid.AttrSpec(item[1][0], item[1][1]), deserializeUrwid(item[2])))
            if item[0] == "list":
                outData.append(deserializeUrwid(item[1]))
            if item[0] == "str":
                outData.append(item[1])

        return outData

    # header.set_text((urwid.AttrSpec("default","default"),deserializeUrwid(raw["head"])))
    main.set_text((urwid.AttrSpec("default", "default"), deserializeUrwid(raw["main"])))
    footer.set_text((urwid.AttrSpec("default", "default"), deserializeUrwid(raw["footer"])))


def getData(request=b'ignore'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(request)
        data = b""
        while True:
            part = s.recv(1024)
            data += part
            if not part:
                break
        return data.decode("utf-8")


commands = []


def keyboardListener(key):
    header.set_text(str(key))
    if not isinstance(key, str):
        return

    commands.append(key)


loop = urwid.MainLoop(frame, unhandled_input=keyboardListener)


def tmp3(loop, user_data):
    if not commands:
        data = getData(request=b'redraw')
    else:
        data = getData(request=json.dumps(commands).encode("utf-8"))
        commands.clear()

    raw = json.loads(data)
    draw(raw)

    loop.set_alarm_in(0.01, tmp3)


loop.set_alarm_in(0.1, tmp3)

loop.run()
