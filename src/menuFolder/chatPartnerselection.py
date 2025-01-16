import src

# bad code: since there is no need to wait for some return this submenue should not wrap around the Chat menu
# bad code: sub menues should be implemented in the base class
class ChatPartnerselection(src.subMenu.SubMenu):
    """
    Spawns a Chat submenu with a player selected character
    """

    def __init__(self):
        """
        initialise internal state
        """

        self.type = "ChatPartnerselection"
        self.subMenu = None
        super().__init__()

    def handleKey(self, key, noRender=False, character = None):
        """
        set up the selection and spawn the chat
        keystrokes after the setup will be delegated

        Parameters:
            key: the key pressed
            noRender: a flag toskip rendering
        Returns:
            returns True when done
        """

        # wrap around the chat menu
        if self.subMenu:
            return self.subMenu.handleKey(key, noRender=noRender, character=character)

        # exit the submenu
        if key == "esc":
            return True

        # set title
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), "nobody to talk to"))
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\nConversation menu\n"))
        out = "\n"

        # offer the player the option to select from characters to talk to
        # bad code: should be done in __init__
        if not self.options and not self.getSelection():
            options = []
            # get characters in room
            if src.gamestate.gamestate.mainChar.room:
                for char in src.gamestate.gamestate.mainChar.room.characters:
                    if char == src.gamestate.gamestate.mainChar:
                        continue
                    if char in src.gamestate.gamestate.mainChar.subordinates:
                        continue
                    if char.faction != src.gamestate.gamestate.mainChar.faction:
                        continue
                    if not (char.xPosition//15 == src.gamestate.gamestate.mainChar.xPosition//15 and char.yPosition//15 == src.gamestate.gamestate.mainChar.yPosition//15):
                        continue
                    options.append((char, char.name))
            # get character on terrain
            else:
                for char in src.gamestate.gamestate.mainChar.terrain.characters:
                    # bad pattern: should only list nearby characters
                    if char == src.gamestate.gamestate.mainChar:
                        continue
                    if char in src.gamestate.gamestate.mainChar.subordinates:
                        continue
                    if char.faction != src.gamestate.gamestate.mainChar.faction:
                        continue
                    if not (char.xPosition//15 == src.gamestate.gamestate.mainChar.xPosition//15 and char.yPosition//15 == src.gamestate.gamestate.mainChar.yPosition//15):
                        continue

                    if char.rank and src.gamestate.gamestate.mainChar.rank:
                        if char.rank < src.gamestate.gamestate.mainChar.rank:
                            options.append((char, char.name + " (outranks you)"))
                        elif char.rank == src.gamestate.gamestate.mainChar.rank:
                            options.append((char, char.name + " (same rank)"))
                    else:
                        options.append((char, char.name))

            for char in src.gamestate.gamestate.mainChar.subordinates:
                options.insert(0,(char, char.name))

            self.setOptions("talk with whom?", options)

        # delegate the actual selection to the super class
        if not self.getSelection():
            super().handleKey(key, noRender=noRender, character=character)

        # spawn the chat submenu
        if self.getSelection():
            self.subMenu = src.chats.ChatMenu(self.selection)
            self.subMenu.handleKey(key, noRender=noRender, character=character)
            return None

        # wait for input
        else:
            return False
