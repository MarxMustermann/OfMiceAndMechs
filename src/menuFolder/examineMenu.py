import src

class ExamineMenu(src.subMenu.SubMenu):
    """
    a menu showing a text
    """

    type = "ExamineMenu"

    def __init__(self, character, text="",specialKeys=None):
        """
        initialise internal state

        Parameters:
            text: the text to show
        """

        super().__init__()
        if not specialKeys:
            specialKeys = {}
        self.specialKeys = specialKeys
        self.character = character

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

        if key in self.specialKeys:
            self.callIndirect(self.specialKeys[key])
            return True

        if not noRender:
            # show info
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
            self.persistentText = self.render()
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        return False

    def render(self):
        pos = self.character.getPosition()
        text = f"you are examining the position: {pos}\n\n"

        if isinstance(self.character.container,src.rooms.Room):
            room = self.character.container

            text += "special fields:\n"
            found = False
            if pos in room.walkingSpace:
                found = True
                text += "is walking space\n"
            for inputSlot in room.inputSlots:
                if pos == inputSlot[0]:
                    found = True
                    text += f"is input slot for {inputSlot[1]} ({inputSlot[2]})\n"
            for outputSlot in room.outputSlots:
                if pos == outputSlot[0]:
                    found = True
                    text += f"is output slot for {outputSlot[1]} ({outputSlot[2]})\n"
            for storageSlot in room.storageSlots:
                if pos[0] == storageSlot[0][0] and pos[1] == storageSlot[0][1]:
                    found = True
                    text += f"is storage slot for {storageSlot[1]} ({storageSlot[2]})\n"
            for buildSite in room.buildSites:
                if pos == buildSite[0]:
                    found = True
                    text += f"is build site for {buildSite[1]} ({buildSite[2]})\n"
            text += "\n"
        else:
            text += "this field is not special\n"

        items = self.character.container.getItemByPosition(pos)
        mainItem = None
        if items:
            if len(items) == 1:
                text += f"there is a {items[0].name}"
                if items[0].bolted:
                    text += f" X"
                text += f":\n\n"
            else:
                text += f"there are {len(items)} items:\n"
                for item in items:
                    text += f"* {item.name}"
                    if item.bolted:
                        text += f" X"
                    text += f"\n"
                text += "\nOn the top is:\n\n"
            mainItem = items[0]
        else:
            text += "there are no items"

        if mainItem:
            registerInfo = ""
            for (key, value) in mainItem.fetchSpecialRegisterInformation().items():
                self.character.setRegisterValue(key, value)
                registerInfo += f"{key}: {value}\n"

            # print info
            info = mainItem.getLongInfo()
            if info:
                text += info

            # notify listeners
            self.character.changed("examine", mainItem)

        submenue = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu(text)
        self.character.add_submenu(submenue)

        return "examine stuff"
