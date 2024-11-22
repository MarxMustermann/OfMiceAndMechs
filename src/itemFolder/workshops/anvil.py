import src


class Anvil(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Anvil"
    name = "anvil"
    description = "Use it to hammer things"
    walkable = False
    bolted = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display = "WA")

        self.outs = [(0,-1,0)]
        self.ins = [(1,0,0),(-1,0,0)]
        self.scheduledItems = []

        self.applyOptions.extend(
                        [
                                                                ("produce item", "produce MetalBars"),
                                                                ("produce 10 item", "produce 10 MetalBars"),
                                                                ("check schedule production", "check schedule"),
                                                                ("schedule production", "schedule production"),
                        ]
                        )
        self.applyMap = {
                    "produce item": self.produceItem,
                    "produce item_k": self.produceItemK,
                    "produce 10 item": self.produce10Item,
                    "produce 10 item_k": self.produce10ItemK,
                    "check schedule production": self.checkProductionScheduleHook,
                    "schedule production": self.scheduleProductionHook,
                        }

    def produce10ItemK(self,character):
        self.produceItemK(character)
        self.produceItemK(character)
        self.produceItemK(character)
        self.produceItemK(character)
        self.produceItemK(character)
        self.produceItemK(character)
        self.produceItemK(character)
        self.produceItemK(character)
        self.produceItemK(character)
        self.produceItemK(character)

    def produceItemK(self,character):
        self.produceItem(character,preferInventoryOut=False)

    def produce10Item(self,character):
        self.produceItem(character)
        self.produceItem(character)
        self.produceItem(character)
        self.produceItem(character)
        self.produceItem(character)
        self.produceItem(character)
        self.produceItem(character)
        self.produceItem(character)
        self.produceItem(character)
        self.produceItem(character)

    def produceItem(self,character,preferInventoryOut=True):

        scrapFound = []
        for item in character.inventory:
            if item.type == "Scrap":
                scrapFound.append(item)

        scrapFound.extend(self.checkForInputScrap())

        if not scrapFound:
            character.addMessage("You need to have scrap to use the anvil")
            character.changed("no scrap error",{})
            return

        scrap = scrapFound[-1]

        dropsSpotsFull = self.checkForDropSpotsFull()
        if not character.getFreeInventorySpace() > 0 and scrap not in character.inventory and dropsSpotsFull:
            character.addMessage("You have no free space to put the item in")
            character.changed("inventory full error",{})
            return

        if self.scheduledItems:
            self.scheduledItems.pop()

        new = src.items.itemMap["MetalBars"]()

        character.timeTaken += 10
        character.addMessage("You produce a metal bar")
        character.addMessage("It takes you 10 turns to do that")
        if scrap in character.inventory:
            character.inventory.remove(scrap)
        else:
            self.container.addAnimation(scrap.getPosition(),"showchar",1,{"char":"--"})
            if scrap.amount == 1:
                self.container.removeItem(scrap)
            else:
                scrap.amount -= 1
                scrap.setWalkable()

        if dropsSpotsFull or (preferInventoryOut and character.getFreeInventorySpace() > 0):
            character.inventory.append(new)
        else:
            for output in self.outs:
                targetPos = (self.xPosition+output[0], self.yPosition+output[1], self.zPosition+output[2])
                targetFull = False
                itemList = self.container.getItemByPosition(targetPos)

                if len(itemList) > 15:
                    targetFull = True
                for item in itemList:
                    if item.walkable is False:
                        targetFull = True

                if not targetFull:
                    self.container.addItem(new,targetPos)
                    self.container.addAnimation(new.getPosition(),"showchar",1,{"char":"++"})

        character.changed("hammered scrap",{})

    def checkForDropSpotsFull(self):
        targetFull = True

        for output in self.outs:
            targetPos = (self.xPosition+output[0], self.yPosition+output[1], self.zPosition+output[2])
            targetFull = False
            itemList = self.container.getItemByPosition(targetPos)

            if len(itemList) > 15:
                targetFull = True
            for item in itemList:
                if item.walkable is False:
                    targetFull = True

            if not targetFull:
                break

        return targetFull

    def checkForInputScrap(self):

        # fetch input scrap
        result = []

        for offset in self.ins:
            for item in self.container.getItemByPosition(
                (self.xPosition + offset[0], self.yPosition + offset[1], self.zPosition+offset[2])
            ):
                if item.type == "Scrap":
                    result.append(item)
        return result

    def checkProductionScheduleHook(self,character):
        character.addMessage(self.scheduledItems)

    def scheduleProductionHook(self,character):
        self.scheduledItems.append("MetalBars")

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
        character.addMessage("you bolt down the Anvil")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Amvil")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(Anvil)
