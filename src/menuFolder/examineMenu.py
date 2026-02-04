import src

class ExamineMenu(src.subMenu.SubMenu):
    """
    a menu showing a text
    """

    type = "ExamineMenu"

    def __init__(self, character, offset=(0,0,0)):
        """
        initialise internal state

        Parameters:
            text: the text to show
        """

        super().__init__()
        self.character = character
        self.offset = offset

    def handleKey(self, key, noRender=False, character = None):
        """
        show the text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in (
            "esc",
            "enter",
            "space",
            " ",
            "j",
            "k",
        ):
            if self.followUp:
                self.callIndirect(self.followUp)
            self.done = True
            return True

        if key == "W":
            if self.offset == (0,1,0):
                self.offset = (0,0,0)
            else:
                self.offset = (0,-1,0)
        if key == "A":
            if self.offset == (1,0,0):
                self.offset = (0,0,0)
            else:
                self.offset = (-1,0,0)
        if key == "S":
            if self.offset == (0,-1,0):
                self.offset = (0,0,0)
            else:
                self.offset = (0,1,0)
        if key == "D":
            if self.offset == (-1,0,0):
                self.offset = (0,0,0)
            else:
                self.offset = (1,0,0)

        if not noRender:
            # show info
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
            self.persistentText = self.render()
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        return False

    def render(self):
        pos = self.character.getPosition(offset=self.offset)
        direction_map = {(0,0,0):"downwards",(1,0,0):"west",(-1,0,0):"east",(0,1,0):"south",(0,-1,0):"north"}
        small_pos = self.character.getSpacePosition(offset=self.offset)
        text = [f"you are looking {direction_map[self.offset]} and examining the position: {small_pos}\n\n"]
        cursoview = []
        cursoview.extend([["  ","OO","\n"],["OO","@@","OO","\n"],["  ","OO","\n","\n"]])
        cursoview[self.offset[1]+1][self.offset[0]+1] = "XX"
        text.append(cursoview)

        # list characters on postion
        text.append("\n")
        show_characters = self.character.container.getCharactersOnPosition(pos)
        if not show_characters:
            text.append("no characters found\n\n")
        else:
            text.append("characters:\n\n")
        for show_character in show_characters:
            text.append("- ")
            text.append(show_character.charType)
            if show_character == self.character:
                text.append(" (You)")
            elif show_character.faction == self.character.faction:
                text.append(" (ally)")
            else:
                text.append(" (enemy)")

            text.append("\n\n")

        items = self.character.container.getItemByPosition(pos)
        mainItem = None
        if items:
            text.append(f"there are {len(items)} items:\n")
            for item in items:
                text.append(f"- {item.name}")
                if item.bolted:
                    text.append(f" (bolted)")
                text.append(f" => {item.description}")
                text.append(f"\n")
            text.append("\n")
            mainItem = items[0]
        else:
            text.append("there are no items\n\n")

        if isinstance(self.character.container,src.rooms.Room):
            room = self.character.container

            # list markers on floor
            markers = self.character.container.getMarkersOnPosition(pos)
            if markers:
                text.append(f"there markings on the floor:\n")
            for marker in markers:
                text.append("- ")
                text.append(str(marker[0]))
                text.append("\n")
            if not markers:
                text.append("this field is not special\n")
            text.append("\n")

        if mainItem:
            registerInfo = ""
            for (key, value) in mainItem.fetchSpecialRegisterInformation().items():
                self.character.setRegisterValue(key, value)
                registerInfo += f"{key}: {value}\n"

            # print info
            text.append("\n\n")
            info = mainItem.getLongInfo()
            if info:
                text.append(info)

            # notify listeners
            self.character.changed("examine", mainItem)

        return text
