import src

class RoomSourceMenu(src.subMenu.SubMenu):
    """
    """

    type = "RoomSourceMenu"
    def __init__(self, room):
        """
        initialise inernal state

        Parameters:
            text: the text to show
        """

        super().__init__()
        self.room = room
        self.submenu = None

    def handleKey(self, key, noRender=False, character = None):
        if self.submenu and self.submenu.done:
            sourceType = self.submenu.text.split(":")[0].strip()
            rawCoordinate = self.submenu.text.split(":")[1].strip(" ()")
            coordinate = []
            for num in rawCoordinate.split(","):
                coordinate.append(int(num))
            while len(coordinate) > 2:
                coordinate.pop()
            coordinate = tuple(coordinate)
            source = (coordinate,sourceType)
            character.container.sources.append(source)

            self.submenu = None


        if self.submenu:
            self.submenu.handleKey(key, noRender, character)
            if self.submenu.done:
                self.handleKey("~",noRender,character)
            return False

        self.persistentText = "sources to fetch resources from:\n\n"
        for source in self.room.sources:
            self.persistentText += f"{source[1]}: {source[0]}\n"
        self.persistentText += "\n\npresss c to add source"
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        if key == "c":
            self.submenu = src.menuFolder.InputMenu.InputMenu(f"input source.\nCurrent tile is {character.container.getTilePosition()}.\nFormat to input source is \nresourceType: tilecoordinate")
            self.submenu.handleKey("~", noRender, character)
            return False

        # exit the submenu
        if key in ("esc",):
            self.done = True
            return True
        return None
