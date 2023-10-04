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
                                                                ("produce item", "produce item"),
                                                                ("check schedule production", "check schedule"),
                                                                ("schedule production", "schedule production"),
                        ]
                        )
        self.applyMap = {
                    "produce item": self.produceItem,
                    "produce item_k": self.produceItemK,
                    "check schedule production": self.checkProductionScheduleHook,
                    "schedule production": self.scheduleProductionHook,
                        }

    def produceItemK(self,character):
        self.produceItem(character,preferInventoryOut=False)

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
        character.addMessage("It takes you a hundred turns to do that")
        if scrap in character.inventory:
            character.inventory.remove(scrap)
        else:
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
                    if item.walkable == False:
                        targetFull = True

                if not targetFull:
                    self.container.addItem(new,targetPos)

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
                if item.walkable == False:
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

src.items.addType(Anvil)
