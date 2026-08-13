import numpy
import regex

import src
import tcod

class CharacterStatsMenu(src.menues.SubMenu):
    def __init__(self,character):
        self.type = "CharacterStatsMenu"
        self.character = character
        self.offset = 0
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):

        # change offset
        if key == "a":
            self.offset -= 1
            if self.offset < 0:
                self.offset = 0
        if key == "d":
            self.offset += 1

        # exit submenu
        if key == "esc":
            self.done = True
            return True
        return False

    def getTitle(self):
        return "CHARACTER STATISTICS"

    def text(self, character):
        text = "Character Statistics:\n\n"

        counter = 0
        if self.offset:
            text += f"{self.offset} entries skipped\n\n"
        for stat_name in character.stats:
            stat = character.stats[stat_name]
            if isinstance(stat, int):
                counter += 1
                if counter <= self.offset:
                    continue
                text += f"{stat_name}: {stat}\n"
            elif isinstance(stat, dict):
                if counter+len(stat) <= self.offset:
                    counter += len(stat)
                    continue
                stat_sum = sum(stat.values())
                text += f"{stat_name}: {stat_sum}\n"
                if len(stat):
                    max_length = 0
                    for inner_stat_name in stat:
                        inner_name = self.beautify(inner_stat_name)
                        if len(inner_name) > max_length:
                            max_length = len(inner_name)
                    amount_to_number = max_length + 1
                    for inner_stat_name in stat:
                        counter += 1
                        if counter <= self.offset:
                            continue
                        inner_name = self.beautify(inner_stat_name)
                        text += (
                            f" {inner_name}:"
                            + " " * (amount_to_number - len(inner_name))
                            + f"{stat[inner_stat_name]}\n"
                        )
            text += "\n"

        text += f"terrains known: {len(character.terrainInfo)}"
        return text

    def render(self,size=None):
        return self.text(self.character)

    @staticmethod
    def beautify(source: str):
        r = regex.Regex(r"(?<!^)[A-Z]")

        m = r.findall(source)
        if m:
            source = r.sub(" \\g<0>", source)

        return source.capitalize()

# register the menu type
src.menues.add_menu(CharacterStatsMenu)
