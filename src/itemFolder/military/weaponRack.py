import random

import src


class WeaponRack(src.items.Item):
    """
    ingame item increasing the players armor
    """

    type = "WeaponRack"
    name = "weapon rack"
    bolted = False
    walkable = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="RW")

        self.applyOptions.extend(
                        [
                                                                ("addSword", "add swords"),
                                                                ("takeBest", "take best sword"),
                                                                ("checkSwords", "check swords"),
                                                                ("takeWorst", "take worst sword"),
                        ]
                        )
        self.applyMap = {
                    "addSword": self.addSword,
                    "takeBest":self.takeBest,
                    "checkSwords":self.checkSwords,
                    "takeWorst":self.takeWorst,
                        }

        self.swords = []

    def addSword(self,character):
        items = character.searchInventory("Sword")
        if not items:
            character.addMessage("you have no swords with you")
            return
        if len(items) >= 25:
            character.addMessage("weapon rack full")
            return
        self.swords.extend(items)
        character.removeItemsFromInventory(items)

    def checkSwords(self,character):
        qualites = []
        for sword in self.swords:
            qualites.append(sword.baseDamage)
        qualites = sorted(qualites)
        qualites.reverse()
        character.addMessage(f"qualites {qualites}")
        character.addMessage(f"numSwords {len(self.swords)}")

    def takeBest(self,character):
        self.take(character,best=True)

    def takeWorst(self,character):
        self.take(character,best=False)

    def take(self,character,best=True):
        if character.getFreeInventorySpace() < 1:
            character.addMessage("you have no free inventory space")
            return
        if not self.swords:
            character.addMessage("no swords left")
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

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the ScrapCompactor")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the ScrapCompactor")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(WeaponRack)
