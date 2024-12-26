import src

# bad code: should be abstracted
# bad code: uses global functions to render
class InventoryMenu(src.subMenu.SubMenu):
    """
    shows and interacts with a characters inventory
    """

    type = "InventoryMenu"

    def __init__(self, char=None):
        """
        initialise the internal state

        Parameters:
            char: the character that owns the inventory that should be shown
        """

        self.subMenu = None
        self.skipKeypress = False
        self.activate = False
        self.drop = False
        self.char = char
        self.sidebared = False
        self.cursor = 0
        super().__init__()
        self.footerText = "press j to activate, press l to drop, press esc to exit"

    def handleKey(self, key, noRender=False, character=None):
        """
        show the inventory

        Parameters:
            key: the key pressed
            noRender: a flag to skip rendering
        Returns:
            returns True when done
        """

        if self.subMenu:
            self.subMenu.handleKey(key, noRender=noRender, character=character)
            if self.drop:
                direction = self.subMenu.keyPressed
                if direction == "w":
                    pos = (self.char.xPosition, self.char.yPosition - 1, self.char.zPosition)
                elif direction == "s":
                    pos = (self.char.xPosition, self.char.yPosition + 1, self.char.zPosition)
                elif direction == "d":
                    pos = (self.char.xPosition + 1, self.char.yPosition + 0, self.char.zPosition)
                elif direction == "a":
                    pos = (self.char.xPosition - 1, self.char.yPosition + 0, self.char.zPosition)
                else:
                    pos = (self.char.xPosition, self.char.yPosition, self.char.zPosition)

                item = self.char.inventory[self.cursor]
                self.char.addMessage(f"you drop a {item.type}")
                self.char.drop(self.char.inventory[self.cursor], pos)
                self.char.timeTaken += self.char.movementSpeed

                self.drop = False
                self.subMenu = None
                return True
            self.subMenu = None
            self.skipKeypress = True
            return False

        if self.skipKeypress:
            self.skipKeypress = False
        else:
            # exit the submenu
            if key == "esc":
                return True
            if key in (
                "ESC",
                "lESC",
            ):
                self.char.rememberedMenu.append(self)
                self.sidebared = True
                return True
            if key in ("rESC",):
                self.char.rememberedMenu2.append(self)
                self.sidebared = True
                return True

            # do activation
            if key == "j":
                item = self.char.inventory[self.cursor]
                self.char.addMessage(f"you activate the {item.type}")
                item.apply(self.char)
                self.char.timeTaken += self.char.movementSpeed

            # do drop
            if key == "l":
                item = self.char.inventory[self.cursor]
                self.char.addMessage(f"you drop a {item.type}")
                self.char.drop(self.char.inventory[self.cursor])
                self.char.timeTaken += self.char.movementSpeed

            # equip as tool
            if key == "t":
                item = self.char.inventory[self.cursor]
                self.char.tool = item
                self.char.addMessage(f"you equiped {item.type} as tool")
                self.char.inventory.remove(item)

            # do drop
            if key == "L":
                self.subMenu = src.menuFolder.OneKeystrokeMenu.OneKeystrokeMenu("Drop where?\n\n w - north\n s - south\n a - left\n d - right")
                self.subMenu.handleKey("~", noRender=noRender, character=character)
                self.drop = True
                return False

            # handle cursor movement
            if key == "w":
                self.cursor -= 1
            if key == "s":
                self.cursor += 1

            # handle out of bounds cursor
            if self.cursor > len(self.char.inventory) - 1:
                self.cursor = 0
            if self.cursor < 0:
                self.cursor = len(self.char.inventory) - 1

        if not noRender:
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\ninventory overview\n\n"))

            # bad code: uses global function
            self.persistentText = (
                src.interaction.urwid.AttrSpec("default", "default"),
                self.render(self.char),
            )

            # show the render
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        return False

    # bad code: global function
    # bad code: should be abstracted
    def render(self, char=None):
        """
        render the inventory of the player into a string

        Returns:
            the rendered string
        """
        character = char
        sidebared = self.sidebared
        cursor = self.cursor

        try:
            self.cursor
        except:
            self.cursor = 0

        if character is None:
            char = src.gamestate.gamestate.mainChar
        else:
            char = character

        txt = []
        if not sidebared:
            txt.append("your inventory:\n\n")
        if len(char.inventory):
            counter = 0
            for item in char.inventory:
                counter += 1
                if not sidebared and counter == cursor + 1:
                    txt.extend(["-> "])
                if isinstance(item.render(), int):
                    txt.extend(
                        [
                            str(counter),
                            " - ",
                            src.canvas.displayChars.indexedMapping[item.render()],
                            " - ",
                            item.name,
                            "\n",
                        ]
                    )
                    if not sidebared and counter == cursor + 1:
                        txt.extend(
                            [
                                item.getDetailedInfo(),
                                "\n\n",
                            ]
                        )
                else:
                    txt.extend([str(counter), " - ", item.render(), " - ", item.name, "\n"])
                    if not sidebared and counter == cursor + 1:
                        txt.extend(
                            [
                                item.getDetailedInfo(),
                                "\n\n",
                            ]
                        )
            txt.append("\n")
            if not sidebared:
                txt.append("press ws to move cursor\npress L to drop item nearby\npress l to drop item\n")
        else:
            txt.append("empty Inventory\n\n")
        return txt
