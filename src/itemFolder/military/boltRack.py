import random

import src


class BoltRack(src.items.Item):
    """
    ingame item increasing the players armor
    """

    type = "BoltRack"
    name = "bolt rack"
    bolted = False
    walkable = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="RW")

        self.applyOptions.extend(
                        [
                                                                ("addBolts", "add bolts"),
                                                                ("takeBolts", "take bolts"),
                                                                ("checkBolts", "check bolts"),
                        ]
                        )
        self.applyMap = {
                    "addBolts": self.addBolts,
                    "takeBolts":self.takeBolts,
                    "checkBolts":self.checkBolts,
                        }

        self.bolts = 0

    def addBolts(self,character):
        items = character.searchInventory("Bolt")
        if not items:
            character.addMessage("you have no bolts with you")
            return
        if len(self.bolts) >= 100:
            character.addMessage("bolt rack full")
            return
        self.bolts.extend(items)
        character.removeItemsFromInventory(items)

    def checkBolts(self,character):
        character.addMessage(f"numBolts {self.numBolts}")

    def takeBolts(self,character):
        if character.getFreeInventorySpace() < 1:
            character.addMessage("you have no free inventory space")
            return
        if self.numBolts:
            character.addMessage("no bolts left")
            return

        selected = None
        for sword in self.swords:
            if best:
                if selected == None or selected.baseDamage < sword.baseDamage:
                    selected = sword
            else:
                if selected == None or selected.baseDamage > sword.baseDamage:
                    selected = sword

        character.addToInventory(selected)
        self.swords.remove(selected)

src.items.addType(WeaponRack)
