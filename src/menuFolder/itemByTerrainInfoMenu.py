import src

# bad code: should be abstracted
# bad code: uses global function to render
class ItemByTerrainInfoMenu(src.menues.SubMenu):
    """
    menu to show the players attributes
    """

    type = "ItemByTerrainInfoMenu"

    def __init__(self, char=None):
        self.char = char
        super().__init__()
        self.sidebared = False
        self.skipKeypress = True

    def getTitle(self):
        return "ITEMS ON TERRAIN"

    def render(self,size=None):
        char = self.char

        if char.dead:
            return ""

        text = []

        terrain = char.getTerrain()
        items_list = terrain.get_all_item()

        compressed_items = {}
        for item in items_list:
            item_type = item.type
            if not item_type in compressed_items:
                compressed_items[item_type] = []
            compressed_items[item_type].append(item)

        for item_type,item_list in compressed_items.items():
            line = ""
            line += f"{item_type}"
            line += " "*(20-len(line))
            line += f" ({len(item_list)})"
            line += "\n"
            text.append(line)

        return text

    def handleKey(self, key, noRender=False, character = None):
        """
        show the attributes and ignore keystrokes

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        if self.skipKeypress:
            self.skipKeypress = False
            key = "~"

        # exit the submenu
        if key in ("esc","o",):
            return True
        if key in ("ESC","lESC",):
            self.char.rememberedMenu.append(self)
            self.sidebared = True
            return True
        if key in ("rESC",):
            self.char.rememberedMenu2.append(self)
            self.sidebared = True
            return True

        text = self.render()

        # show info
        if src.interaction.main:
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), [text]))
        if src.interaction.header:
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
        return None

# register the menu type
src.menues.add_menu(ItemByTerrainInfoMenu)
