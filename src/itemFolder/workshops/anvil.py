import src


class Anvil(src.items.itemMap["WorkShop"]):
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
        self.scheduledAmount = 0

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
                    "produce item_J": self.produceItem_J,
                    "produce item_k": self.produceItem_k,
                    "produce item_K": self.produceItem_K,
                    "produce 10 item": self.produce10Item,
                    "produce 10 item_k": self.produce10Item_k,
                    "check schedule production": self.checkProductionScheduleHook,
                    "schedule production": self.scheduleProductionHook,
                        }

    def produceItem_K(self,character):
        self.produceItem(character,preferInventoryOut=False,amount=None)

    def produceItem_J(self,character):
        self.produceItem(character,preferInventoryOut=True,amount=None)

    def produce10Item_k(self,character):
        self.produceItem(character,preferInventoryOut=False,amount=10)

    def produceItem_k(self,character):
        self.produceItem(character,preferInventoryOut=False)

    def produce10Item(self,character):
        self.produceItem(character,preferInventoryOut=True,amount=10)

    def produceItem(self,character,preferInventoryOut=True,amount=1):
        self.produceItemLooped({"amount":amount,"character":character,"preferInventoryOut":preferInventoryOut})

    def produceItemLooped(self,params):
        if "rawAmount" in params:
            params["amount"] = int(params["rawAmount"])
            del params["rawAmount"]

        amount = params.get("amount")
        character = params.get("character")
        preferInventoryOut = params.get("preferInventoryOut")

        if amount == None:
            submenue = src.menuFolder.inputMenu.InputMenu("Type how many of the items produce",targetParamName="rawAmount")
            submenue.tag = "anvilAmountInput"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItemLooped","params":params}
            return

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

        if self.scheduledAmount != None and self.scheduledAmount > 0:
            self.scheduledAmount -= 1

        params = {
            "character": character,
            "scrap": scrap,
            "preferInventoryOut": preferInventoryOut,
            "dropsSpotsFull": dropsSpotsFull,
        }
        params["productionTime"] = 10
        params["doneProductionTime"] = 0
        params["hitCounter"] = character.numAttackedWithoutResponse
        params["extraAmount"] = amount-1

        self.produceItem_wait(params)

    def produceItem_done(self,params):
        character = params["character"]
        scrap = params["scrap"]
        preferInventoryOut = params["preferInventoryOut"]
        dropsSpotsFull = params["dropsSpotsFull"]

        new = src.items.itemMap["MetalBars"]()
        character.stats["items produced"]["MetalBars"] = character.stats["items produced"].get("MetalBars", 0) + 1
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

        if params["extraAmount"]:
            self.produceItem(character,preferInventoryOut=preferInventoryOut,amount=params["extraAmount"])

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

    def checkForInputScrap(self,character=None):

        # fetch input scrap
        result = []

        if character:
            for item in character.inventory:
                if not item.type == "Scrap":
                    continue
                result.append(item)

        for offset in self.ins:
            for item in self.container.getItemByPosition(
                (self.xPosition + offset[0], self.yPosition + offset[1], self.zPosition+offset[2])
            ):
                if item.type == "Scrap":
                    result.append(item)
        return result

    def checkProductionScheduleHook(self,character):
        character.addMessage(self.scheduledAmount)

    def scheduleProductionHook(self,character):
        self.scheduledAmount += 1

src.items.addType(Anvil)
