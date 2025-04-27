import src


class CharacterStatsMenu(src.subMenu.SubMenu):
    def __init__(self):
        self.type = "CharacterStatsMenu"
        self.index = 0
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nStats\n\n"))
        text = "Character Statistics\n\n"

        for stat in character.stats:
            text += f"{stat}:   {character.stats[stat]}\n"

        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        # exit submenu
        return key == "esc"
