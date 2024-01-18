import random

import src


class ArmorStand(src.items.Item):
    """
    ingame item increasing the players armor
    """

    type = "ArmorStand"
    name = "armor stand"
    bolted = False
    walkable = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="RA")

        self.applyOptions.extend(
                        [
                                                                ("addArmor", "add armor"),
                                                                ("takeBest", "take best armor"),
                                                                ("checkArmor", "check armor"),
                                                                ("takeWorst", "take worst armor"),
                        ]
                        )
        self.applyMap = {
                    "addArmor": self.addArmor,
                    "takeBest":self.takeBest,
                    "checkArmor":self.checkArmor,
                    "takeWorst":self.takeWorst,
                        }

        self.armors = []

    def addArmor(self,character):
        items = character.searchInventory("Armor")
        if not items:
            character.addMessage("you have no armor with you")
            return
        if len(items) >= 25:
            character.addMessage("armor stand full")
            return
        self.armors.extend(items)
        character.removeItemsFromInventory(items)

    def checkArmor(self,character):
        qualites = []
        for armor in self.armors:
            qualites.append(armor.armorValue)
        qualites = sorted(qualites)
        qualites.reverse()
        character.addMessage(f"qualites {qualites}")
        character.addMessage(f"numArmor {len(self.armors)}")

    def takeBest(self,character):
        self.take(character,best=True)

    def takeWorst(self,character):
        self.take(character,best=False)

    def take(self,character,best=True):
        if character.getFreeInventorySpace() < 1:
            character.addMessage("you have no free inventory space")
            return
        if not self.armors:
            character.addMessage("no armor left")
            return

        selected = None
        for armor in self.armors:
            if best:
                if selected == None or selected.armorValue < armor.armorValue:
                    selected = armor
            else:
                if selected == None or selected.armorValue > armor.armorValue:
                    selected = armor

        character.addToInventory(selected)
        self.armors.remove(selected)

src.items.addType(ArmorStand)
