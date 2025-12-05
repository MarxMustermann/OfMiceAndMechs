import numpy
import regex

import src
import tcod

class CharacterStatsMenu(src.subMenu.SubMenu):
    def __init__(self):
        self.type = "CharacterStatsMenu"
        self.index = 0
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nStats\n\n"))
        text = self.text(character)
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        # exit submenu
        return key == "esc"

    def text(self, character):
        text = "Character Statistics:\n\n"

        for stat_name in character.stats:
            stat = character.stats[stat_name]
            if isinstance(stat, int):
                text += f"{stat_name}: {stat}\n"
            elif isinstance(stat, dict):
                stat_sum = sum(stat.values())
                text += f"{stat_name}: {stat_sum}\n"
                if len(stat):
                    amount_to_number = len(max(stat.keys(), key=len)) + len(":")
                    for inner_stat_name in stat:
                        inner_name = self.capitalize(inner_stat_name)
                        text += (
                            f" {inner_name}:"
                            + " " * (amount_to_number - len(inner_name))
                            + f"{stat[inner_stat_name]}\n"
                        )
            text += "\n"

        text += f"terrains known: {len(character.terrainInfo)}"
        return text

    @staticmethod
    def capitalize(source: str):
        r = regex.Regex(r"(?<!^)[A-Z]")

        m = r.findall(source)
        if m:
            source = r.sub(" \\g<0>", source)

        return source.capitalize()
