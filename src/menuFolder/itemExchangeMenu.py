import numpy
import regex

import src
import tcod

class ItemExchangeMenu(src.menues.SubMenu):
    def __init__(self,character,partner):
        self.type = "ItemExchangeMenu"
        self.index = 0
        self.character = character
        self.partner = partner
        self.index = [0,0]
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):

        # move the cursor
        if key == "d":
            self.index[0] = 1
        if key == "a":
            self.index[0] = 0
        if key == "w":
            self.index[1] -= 1
            if self.index[1] < 0:
                self.index[1] = 9
        if key == "s":
            self.index[1] += 1
            if self.index[1] > 9:
                self.index[1] = 0

        # exchange item
        if key == "j":
            if self.index[0] == 0:
                giver = self.character
                taker = self.partner
            if self.index[0] == 1:
                giver = self.partner
                taker = self.character
            if self.index[1] < len(giver.inventory):
                item = giver.inventory[self.index[1]]
                giver.inventory.remove(item)
                taker.addToInventory(item)

        # exit submenu
        return key == "esc"

    def getTitle(self):
        return "EXCHANGE ITEMS"

    def render(self,size=None):
        text = []
        
        text.append("YOU                           | "+self.partner.name+"\n\n")

        for i in range(1,11):
            line_left = []
            line_left.append(f"{i} ")
            if self.index[0] == 0 and self.index[1] == i-1:
                line_left.append("=> ")
            else:
                line_left.append("-  ")
            if i <= len(self.character.inventory):
                item = self.character.inventory[i-1]
                line_left.extend([" ",item.metaRender()," "])
                line_left.append(item.name)
            text.append(line_left)
            text.append(" "*(30-len(src.interaction.stringifyUrwid(line_left))))
 
            line_right = []
            line_right.append(f"{i} ")
            if self.index[0] == 1 and self.index[1] == i-1:
                line_right.append("=> ")
            else:
                line_right.append("-  ")
            if i <= len(self.partner.inventory):
                item = self.partner.inventory[i-1]
                line_right.extend([" ",item.metaRender()," "])
                line_right.append(item.name)
            text.append(line_right)

            text.append("\n")

        return text

    @staticmethod
    def beautify(source: str):
        r = regex.Regex(r"(?<!^)[A-Z]")

        m = r.findall(source)
        if m:
            source = r.sub(" \\g<0>", source)

        return source.capitalize()

# register the menu type
src.menues.add_menu(ItemExchangeMenu)
