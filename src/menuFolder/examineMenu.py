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
        self.last_move_blocked = False

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

        self.last_move_blocked = False
        if key == "W":
            if self.offset == (0,1,0):
                self.offset = (0,0,0)
            elif self.offset in ((0,-1,0),(1,0,0),(-1,0,0),):
                if src.interaction.moveCharacter("north",self.character,False,None,None):
                    self.last_move_blocked = True
            else:
                self.offset = (0,-1,0)
        if key == "A":
            if self.offset == (1,0,0):
                self.offset = (0,0,0)
            elif self.offset in ((-1,0,0),(0,-1,0),(0,1,0),):
                if src.interaction.moveCharacter("west",self.character,False,None,None):
                    self.last_move_blocked = True
            else:
                self.offset = (-1,0,0)
        if key == "S":
            if self.offset == (0,-1,0):
                self.offset = (0,0,0)
            elif self.offset in ((0,1,0),(1,0,0),(-1,0,0),):
                if src.interaction.moveCharacter("south",self.character,False,None,None):
                    self.last_move_blocked = True
            else:
                self.offset = (0,1,0)
        if key == "D":
            if self.offset == (-1,0,0):
                self.offset = (0,0,0)
            elif self.offset in ((1,0,0),(0,-1,0),(0,1,0),):
                if src.interaction.moveCharacter("east",self.character,False,None,None):
                    self.last_move_blocked = True
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
        cursorview = []
        for y in range(-2,3):
            cursorview.append([])
            for x in range(-2,3):
                cursorview[y+2].append(" ")
        under_cursor = "  "

        if isinstance(self.character.container,src.rooms.Room):
            room = self.character.container
            room_render = room.render(advanceAnimations=False)
            for x in range(-2,3):
                for y in range(-2,3):
                    local_offset = (x,y,0)
                    adapted_x = self.character.xPosition+local_offset[0]
                    adapted_y = self.character.yPosition+local_offset[1]
                    if adapted_y < 0 or adapted_y >= len(room_render) or adapted_x < 0 or adapted_x >= len(room_render[adapted_y]):
                        continue

                    render = room_render[adapted_y][adapted_x]
                    cursorview[local_offset[1]+2][local_offset[0]+2] = render
                    if local_offset == self.offset:
                        under_cursor = render

        color = "#fff"
        if self.last_move_blocked:
            color = "#f00"
        cursorview[self.offset[1]+2][self.offset[0]+2] = (src.interaction.urwid.AttrSpec(color, "black"),"XX")
        counter = 0
        while counter < len(cursorview):
            line = cursorview[counter]
            text.append("           ")
            if counter == 1:
                text.append(under_cursor)
            else:
                text.append("  ")
            text.append("           ")
            text.extend(line)
            text.append("\n")

            counter += 1
        text.append("\n")
        text.append("press W/A/S/D to change what spot you look at\n\n")

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
            text.append("no items found\n\n")

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
                text.append("no markers found\n")
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
