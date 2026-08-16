import src

class MessagesMenu(src.menues.SubMenu):
    type = "MessagesMenu"

    def __init__(self, char=None):
        self.char = char
        self.scrollIndex = 0
        self.skipKeypress = True
        self.sidebared = False
        super().__init__()

    def getTitle(self):
        return "MESSAGE LOG"

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
            self.sidebared = True
            self.char.rememberedMenu.append(self)
            return True
        if key in ("rESC",):
            self.sidebared = True
            self.char.rememberedMenu2.append(self)
            return True
        if key == "w" and self.scrollIndex > 0:
            self.scrollIndex -= 1
        if key == "s":
            self.scrollIndex += 1

        char = self.char

    def render(self,size=None):
        char = self.char
        out = []

        if not self.sidebared:
            out.append(f"press w/s to scroll\npress esc to close menu\n\noldest message on top - skipping {self.scrollIndex} messages\n\n")

        if self.scrollIndex:
            to_print = char.messages[-46-self.scrollIndex:-self.scrollIndex]
        else:
            to_print = char.messages[-46:]
        for message in reversed(to_print):
            if message[1] == src.gamestate.gamestate.tick:
                color = "#fff"
            elif message[1] > src.gamestate.gamestate.tick - 1:
                color = "#fff"
            elif message[1] > src.gamestate.gamestate.tick - 2:
                color = "#fff"
            elif message[1] > src.gamestate.gamestate.tick - 3:
                color = "#aaa"
            elif message[1] > src.gamestate.gamestate.tick - 4:
                color = "#999"
            elif message[1] > src.gamestate.gamestate.tick - 5:
                color = "#888"
            elif message[1] > src.gamestate.gamestate.tick - 6:
                color = "#777"
            else:
                color = "#666"

            message_content = message[0]
            adapted_message = ""
            lines = message_content.splitlines()
            for line in lines:
                words = line.split(" ")
                first_word = True
                line_to_add = ""
                for word in words:
                    if first_word:
                        first_word = False
                    else:
                        line_to_add += " "
                    if size:
                        if len(line_to_add)+len(word)+1 > size[0]-3:
                            adapted_message += line_to_add+"\n"
                            line_to_add = ""
                    line_to_add += word
                adapted_message += line_to_add+"\n"

            out.append((src.interaction.urwid.AttrSpec(color, "default"),f"- {adapted_message}"))
        return out

# register the menu type
src.menues.add_menu(MessagesMenu)
