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

        items = self.character.container.getItemByPosition(pos)
        mainItem = None
        if items:
            if len(items) == 1:
                text.append(f"there is a {items[0].name}")
                if items[0].bolted:
                    text.append(f" X")
                text.append(f":\n\n")
            else:
                text.append(f"there are {len(items)} items:\n")
                for item in items:
                    text.append(f"* {item.name}")
                    if item.bolted:
                        text.append(f" X")
                    text.append(f"\n")
                text.append("\nOn the top is:\n\n")
            mainItem = items[0]
        else:
            text.append("there are no items")

        if isinstance(self.character.container,src.rooms.Room):
            room = self.character.container

            text.append("special fields:\n")
            found = False
            if pos in room.walkingSpace:
                found = True
                text.append("is walking space\n")
            for inputSlot in room.inputSlots:
                if pos == inputSlot[0]:
                    found = True
                    text.append(f"is input slot for {inputSlot[1]} ({inputSlot[2]})\n")
            for outputSlot in room.outputSlots:
                if pos == outputSlot[0]:
                    found = True
                    text.append(f"is output slot for {outputSlot[1]} ({outputSlot[2]})\n")
            for storageSlot in room.storageSlots:
                if pos[0] == storageSlot[0][0] and pos[1] == storageSlot[0][1]:
                    found = True
                    text.append(f"is storage slot for {storageSlot[1]} ({storageSlot[2]})\n")
            for buildSite in room.buildSites:
                if pos == buildSite[0]:
                    found = True
                    text.append(f"is build site for {buildSite[1]} ({buildSite[2]})\n")
            text.append("\n")
        else:
            text.append("this field is not special\n")

        if mainItem:
            registerInfo = ""
            for (key, value) in mainItem.fetchSpecialRegisterInformation().items():
                self.character.setRegisterValue(key, value)
                registerInfo += f"{key}: {value}\n"

            # print info
            info = mainItem.getLongInfo()
            if info:
                text.append(info)

            # notify listeners
            self.character.changed("examine", mainItem)

        return text
