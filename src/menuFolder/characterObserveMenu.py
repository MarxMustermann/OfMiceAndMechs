import src

# bad code: should be abstracted
# bad code: uses global function to render
class CharacterObserveMenu(src.menues.SubMenu):
    """
    menu to give an overview about players
    """

    type = "CharacterObserveMenu"

    def __init__(self, char=None):
        self.char = char
        super().__init__()
        self.sidebared = False
        self.skipKeypress = True

    def getTitle(self):
        return "OBSERVE CHARACTERS"

    def render(self):

        # set up helper variables
        char = self.char
        terrain = char.getTerrain()
        text = []

        # handle weird edge cases
        if char.dead:
            return ""

        # collect the characters to show
        all_characters = terrain.getAllCharacters()
        nearby_characters = []
        if char.container.isRoom:
            nearby_characters = char.container.characters

        # show characters
        for show_character in all_characters:
            text.append(f"{show_character.name} ({show_character.getBigPosition()}))\n")

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
        if key in ("esc",):
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
src.menues.add_menu(CharacterObserveMenu)
