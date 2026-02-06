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
        self.index = 0

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
        if key == "w":
            self.index -= 1
        if key == "s":
            self.index += 1

        (show_characters,items,markers) = self.get_things_to_show()
        if self.index < 0:
            self.index = len(show_characters)+len(items)+len(markers)-1
        if self.index >= len(show_characters)+len(items)+len(markers):
            self.index = 0

        if not noRender:
            # show info
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
            self.persistentText = self.render()
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        return False

    def get_things_to_show(self):
        pos = self.character.getPosition(offset=self.offset)
        show_characters = self.character.container.getCharactersOnPosition(pos)
        items = self.character.container.getItemByPosition(pos)
        markers = []
        if isinstance(self.character.container,src.rooms.Room):
            room = self.character.container
            markers = self.character.container.getMarkersOnPosition(pos)
        return (show_characters,items,markers)

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
            if counter == 2:
                text.append(under_cursor)
            else:
                text.append("  ")
            text.append("           ")
            text.extend(line)
            text.append("\n")

            counter += 1
        text.append("\n")
        text.append("press W/A/S/D to change what spot you look at\n\n")

        # collect things to display
        (show_characters,items,markers) = self.get_things_to_whow()
        total_amount_shown = len(items)+len(show_characters)+len(markers)
        text.append(f"{total_amount_shown} things were found on the selected spot:\n(press w/s to view details for a different thing)\n\n")
        display_counter = 0

        # list characters on postion
        text.append("\n")
        for show_character in show_characters:
            color = "#666"
            if display_counter == self.index:
                color = "#fff"

            line = "- "
            line += show_character.charType
            if show_character == self.character:
                line += " (You)"
            elif show_character.faction == self.character.faction:
                line += " (ally)"
            else:
                line += " (enemy)"
            line += "\n"

            text.append((src.interaction.urwid.AttrSpec(color, "default"),line))

            display_counter += 1

        if items:
            for item in items:
                color = "#666"
                if display_counter == self.index:
                    color = "#fff"

                line = f"- {item.name}"
                if item.bolted:
                    line += " (bolted)"
                line += f" => {item.description}"
                line += "\n"

                text.append((src.interaction.urwid.AttrSpec(color, "default"),line))

                display_counter += 1

        if isinstance(self.character.container,src.rooms.Room):
            room = self.character.container

            # list markers on floor
            markers = self.character.container.getMarkersOnPosition(pos)
            for marker in markers:
                color = "#666"
                if display_counter == self.index:
                    color = "#fff"

                line = "- "
                line += str(marker[0])
                line += "\n"

                text.append((src.interaction.urwid.AttrSpec(color, "default"),line))

                display_counter += 1

        text.append("\n\ndetails for the currently selected thing:\n\n")

        if self.index < 0:
            text.append("nothing selected")
        elif self.index <= len(show_characters)-1:
            show_character = show_characters[self.index]

            char = show_character
            text.append(f"name:        {char.name}")
            if char == self.character:
                text.append(" (You)")
            elif char.faction == self.character.faction:
                text.append(" (ally)")
            else:
                text.append(" (enemy)")
            text.append("\n")
            text.append(f"health:      {char.health}/{char.adjustedMaxHealth}\n")
            text.append(f"faction:     {char.faction}\n")
            if char.level:
                text.append(f"level:       {char.level}\n")
            text.append(f"exhaustion:  {char.exhaustion}\n")
            text.append(f"timeTaken:   {round(char.timeTaken,2)}\n")
            text.append(f"movemmentsp: {char.adjustedMovementSpeed}\n")
            text.append(f"attacksp:    {char.attackSpeed}\n")
            text.append("\n")
        elif self.index <= len(show_characters)+len(items)-1:
            show_item = items[self.index-len(show_characters)]

            #registerInfo = ""
            #for (key, value) in mainItem.fetchSpecialRegisterInformation().items():
            #    self.character.setRegisterValue(key, value)
            #    registerInfo += f"{key}: {value}\n"

            # print info
            text.append("\n\n")
            info = show_item.getLongInfo()
            if info:
                text.append(info)

            # notify listeners
            self.character.changed("examine", show_item)

        elif self.index <= len(show_characters)+len(items)+len(markers)-1:
            marker_to_show = markers[self.index-len(show_characters)-len(items)]

            text.append(marker_to_show[0])
            text.append("\n")
            text.append(str(marker_to_show[1]))
            text.append("\n")
        else:
            text.append("nothing to show details on")

        return text
