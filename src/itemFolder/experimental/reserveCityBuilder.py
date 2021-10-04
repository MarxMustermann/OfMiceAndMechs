import src
import random
import urwid

class ReserveCityBuilder(src.items.Item):

    type = "ReserveCityBuilder"
    def __init__(self):
        super().__init__(display=(urwid.AttrSpec("#ff2", "black"), "RC"))
        self.broken = True
        self.firstUsage = True
        self.neededRepairItems = []
        repairCandidates = ["Rod","Heater","puller","Stripe","Bolt","Tank"]
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
            if self.firstUsage:
                item = src.items.itemMap["Note"]()
                item.text = "%s"%(self.neededRepairItems,)
                character.messages.append("The prints a list of needed items")
                pos = (self.xPosition-1,self.yPosition,self.zPosition)
                self.container.addItem(item,pos)
                self.firstUsage = False

            neededItems = self.neededRepairItems[:]
            itemsToConsume = []
            for item in character.inventory:
                if item.type in neededItems:
                    neededItems.remove(item.type)
                    itemsToConsume.append(item)

            if neededItems:
                character.messages.append("This machine is broken")
                character.messages.append("you need to have %s in you inventory to repair the machine"%(neededItems,))
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
    
    def render(self):
        if self.broken:
            return (urwid.AttrSpec("#aa8", "black"), "RC")
        else:
            return (urwid.AttrSpec("#ff2", "black"), "RC")

src.items.addType(ReserveCityBuilder)
