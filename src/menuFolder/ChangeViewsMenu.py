import collections

import SubMenu

from src.interaction import main, urwid


class ChangeViewsMenu(SubMenu):
    type = "ChangeViewsMenu"

    def __init__(self):
        super().__init__()
        self.firstKey = True

    def handleKey(self, key, noRender=False, character=None):
        if character and key in ("a",):
            character.personality["viewChar"] = "activity"
        if character and key in ("A",):
            character.personality["viewColour"] = "activity"
        if character and key in ("r",):
            character.personality["viewChar"] = "rank"
        if character and key in ("R",):
            character.personality["viewColour"] = "rank"
        if character and key in ("h",):
            character.personality["viewChar"] = "health"
        if character and key in ("H",):
            character.personality["viewColour"] = "health"
        if character and key in ("n",):
            character.personality["viewChar"] = "name"
        if character and key in ("N",):
            character.personality["viewColour"] = "name"
        if character and key in ("f",):
            character.personality["viewChar"] = "faction"
        if character and key in ("F",):
            character.personality["viewColour"] = "faction"

        viewChar = character.personality["viewChar"]
        viewColour = character.personality["viewColour"]

        self.persistentText = []
        self.persistentText.append("change view menu\n\n")
        color = "#fff"
        if viewChar == "activity":
            color = "#f00"
        if viewColour == "activity":
            color = "#0f0"
        self.persistentText.append((urwid.AttrSpec(color, "default"), "press a/A to show NPC activity marking\n"))

        color = "#fff"
        if viewChar == "rank":
            color = "#f00"
        if viewColour == "rank":
            color = "#0f0"
        self.persistentText.append((urwid.AttrSpec(color, "default"), "press r/R to rank marking\n"))
        color = "#fff"
        if viewChar == "health":
            color = "#f00"
        if viewColour == "health":
            color = "#0f0"
        self.persistentText.append((urwid.AttrSpec(color, "default"), "press h/H to show health marking\n"))
        color = "#fff"
        if viewChar == "name":
            color = "#f00"
        if viewColour == "name":
            color = "#0f0"
        self.persistentText.append((urwid.AttrSpec(color, "default"), "press n/N to show name marking\n"))
        color = "#fff"
        if viewChar == "faction":
            color = "#f00"
        if viewColour == "faction":
            color = "#0f0"
        self.persistentText.append((urwid.AttrSpec(color, "default"), "press f/F to show faction indicator\n"))
        self.persistentText.append("\n\nsmall letters for display color, big letters for display char")
        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        # exit the submenu
        if key in ("esc",):
            self.done = True
            return True
        return None
