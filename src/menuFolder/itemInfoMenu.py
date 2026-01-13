import src

# bad code: should be abstracted
# bad code: uses global function to render
class ItemInfoMenu(src.subMenu.SubMenu):
    """
    menu to show the players attributes
    """

    type = "ItemInfoMenu"

    def __init__(self, char=None):
        self.char = char
        super().__init__()
        self.sidebared = False
        self.skipKeypress = True

    def render(self):
        char = self.char

        if char.dead:
            return ""

        text = []

        if char.container.isRoom:
            items_list = char.container.getItems()
        else:
            items_list = char.container.getNearbyItems(char)

        compressed_items = {}
        for item in items_list:
            item_type = item.type
            if not item_type in compressed_items:
                compressed_items[item_type] = []
            compressed_items[item_type].append(item)

        for item_type,item_list in compressed_items.items():
            text.append(f"{item_type} ({len(item_list)}):\n")
            counter = 0
            details = ""
            for item in item_list:
                details += f"{item.getPosition()},"
                counter += 1
                if counter == 10:
                    if item != item_list[-1]:
                        details += "\n"
                    counter = 0
                else:
                    details += " "
            details += f"\n"

            text.append((src.interaction.urwid.AttrSpec("#888", "black"),details))

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
