import src
import random

class YouWonMachine(src.items.Item):
    """
    ingame item to change z-levels
    """

    type = "YouWonMachine"
    def __init__(self):
        super().__init__(display="YW")
        self.broken = True
        self.neededRepairItems = []
        repairCandidates = ["Rod","Heater","puller","Stripe","Bolt","Case","Tank"]
        for i in range(0,random.randint(3,5)):
            candidate = random.choice(repairCandidates)
            self.neededRepairItems.append(candidate)
            repairCandidates.remove(candidate)

    def apply(self, character):
        """
        handle a character trying to go up

        Parameters:
            character: the character using the item
        """

        if self.broken:
            neededItems = self.neededRepairItems[:]
            itemsToConsume = []
            for item in character.inventory:
                if item.type in neededItems:
                    neededItems.remove(item.type)
                    itemsToConsume.append(item)

            if neededItems:
                character.messages.append("This machine is broken")
                character.messages.append("you need to have %s in you inventory to repair the machine, if you activate the machine you win"%(neededItems,))
            else:
                character.messages.append("you repair the machine")
                for item in itemsToConsume:
                    character.inventory.remove(item)
                self.broken = False
        else:
            neededItems = random.choice(["MemoryCell","PocketFrame"])
            for item in character.inventory:
                if item.type in neededItems:
                    neededItems.remove(item.type)

            if neededItems:
                character.messages.append("activate the machine and win the game")
                character.messages.append("you need to have a memory cell in your inventory to activate the machine")
            else:
                character.messages.append("you won the game.")

src.items.addType(YouWonMachine)
