import src

class MessagesMenu(src.subMenu.SubMenu):

    def render(self):
        char = self.char
        out = []

        if self.scrollIndex:
            to_print = char.messages[-46-self.scrollIndex:-self.scrollIndex]
        else:
            to_print = char.messages[-46:]
        for message in reversed(to_print):
            if message[1] == src.gamestate.gamestate.tick:
                color = "#fff"
            elif message[1] > src.gamestate.gamestate.tick - 2:
                color = "#eee"
            elif message[1] > src.gamestate.gamestate.tick - 3:
                color = "#eee"
            elif message[1] > src.gamestate.gamestate.tick - 4:
                color = "#ddd"
            elif message[1] > src.gamestate.gamestate.tick - 5:
                color = "#ccc"
            elif message[1] > src.gamestate.gamestate.tick - 6:
                color = "#bbb"
            elif message[1] > src.gamestate.gamestate.tick - 7:
                color = "#aaa"
            elif message[1] > src.gamestate.gamestate.tick - 8:
                color = "#999"
            elif message[1] > src.gamestate.gamestate.tick - 9:
                color = "#888"
            elif message[1] > src.gamestate.gamestate.tick - 10:
                color = "#888"
            else:
                color = "#666"
            out.append((src.interaction.urwid.AttrSpec(color, "default"),f"- {message[0]}\n"))
        return out

    type = "MessagesMenu"

    def __init__(self, char=None):
        self.char = char
        self.scrollIndex = 0
        self.skipKeypress = True
        super().__init__()

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
        if key in ("esc","x"):
            character.changed("closedMessages")
            return True
        if key in ("ESC","lESC",):
            self.char.rememberedMenu.append(self)
            return True
        if key in ("rESC",):
            self.char.rememberedMenu2.append(self)
            return True
        if key == "w" and self.scrollIndex > 0:
            self.scrollIndex -= 1
        if key == "s":
            self.scrollIndex += 1

        char = self.char

        text = [f"press w/s to scroll\noldest message on top - skipping {self.scrollIndex} messages\n\n",self.render()]

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "messages"))
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), [text]))
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
        return None
