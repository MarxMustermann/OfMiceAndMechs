import src

class MetalWorkingBench(src.items.itemMap["WorkShop"]):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "MetalWorkingBench"
    name = "MetalWorkingBench"
    description = "Use it to build simple things"
    walkable = False
    bolted = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display = "WM")

        self.applyOptions.extend(
                        [
                                                                ("produce item", "produce item"),
                                                                ("check schedule production", "check schedule"),
                                                                ("schedule production", "schedule production"),
                                                                ("repeat", "repeat last production"),
                        ]
                        )
        self.applyMap = {
                    "produce item": self.produceItemHook,
                    "check schedule production": self.checkProductionScheduleHook,
                    "schedule production": self.scheduleProductionHook,
                    "repeat": self.repeat,
                    "repeat_k": self.repeat_k,
                    "repeat_J": self.repeat_J,
                    "repeat_K": self.repeat_K,
                        }

        self.ins = [(1,0,0),]
        self.outs = [(0,1,0),(0,-1,0)]
        self.scheduledItems = []
        self.lastProduction = None

    def produceItemHook(self,character):
        self.produceItem({"character":character})

    def produceItem(self,params):
        character = params["character"]

        if "type" not in params:
            options = []
            options.append(("Bolt","Bolt"))
            options.append(("Rod","Rod"))
            options.append(("Frame","Frame"))
            options.append(("Case","Case"))
            options.append(("Wall","Wall"))
            options.append(("Door","Door"))
            options.append(("RoomBuilder","RoomBuilder"))
            options.append(("Painter","Painter"))
            options.append(("CityPlaner","CityPlaner"))
            options.append(("ScrapCompactor","ScrapCompactor"))
            options.append(("Sword","Sword"))
            options.append(("Armor","Armor"))
            options.append(("CoalBurner","CoalBurner"))
            options.append(("Vial","Vial"))
            options.append(("Statue","Statue"))
            options.append(("Sheet","Sheet"))
            options.append(("CorpseAnimator","Corpseanimator"))
            options.append(("Shrine","Shrine"))
            options.append(("Throne","Throne"))
            options.append(("ItemCollector","ItemCollector"))
            options.append(("PersonnelTracker","PersonnelTracker"))
            options.append(("ArmorStand","ArmorStand"))
            options.append(("WeaponRack","WeaponRack"))
            options.append(("byName","produce by name"))
            submenue = src.menuFolder.selectionMenu.SelectionMenu("what item to produce?",options,targetParamName="type")
            submenue.tag = "metalWorkingProductSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItem","params":params}
            return

        if params.get("key") not in ("J","K",):
            params["amount"] = 1

        if params.get("type") == "byName":
            submenue = src.menuFolder.inputMenu.InputMenu("Type the name of the item to produce",targetParamName="type")
            submenue.tag = "metalWorkingProductInput"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItem","params":params}
            return

        if params.get("type") not in src.items.itemMap:
            if params.get("type"):
                character.addMessage("Item type unknown.")
            return

        if params.get("type") in src.items.nonManufacturedTypes:
            ty = params.get("type")
            character.addMessage(f"cannot produce item type {ty}")
            return

        if "rawAmount" in params:
            params["amount"] = int(params["rawAmount"])
            del params["rawAmount"]

        if not "amount" in params:
            submenue = src.menuFolder.inputMenu.InputMenu("Type how many of the items produce",targetParamName="rawAmount")
            submenue.tag = "metalWorkingAmountInput"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItem","params":params}
            return

        metalBarsFound = []
        for item in character.inventory+self.getInputItems():
            if item.type == "MetalBars":
                metalBarsFound.append(item)

        if not metalBarsFound:
            character.addMessage("You need to have metal bars in your inventory to use the metal working bench")
            character.changed("no metalBars error",{})
            return

        metalBar = metalBarsFound[-1]

        dropsSpotsFull = self.checkForDropSpotsFull()
        if not character.getFreeInventorySpace() > 0 and metalBar not in character.inventory and dropsSpotsFull:
            character.addMessage("You have no free inventory space to put the item in")
            character.changed("inventory full error",{})
            return

        if params["type"] in self.scheduledItems:
            self.scheduledItems.remove(params["type"])

        if metalBar in character.inventory:
            character.inventory.remove(metalBar)
        else:
            self.container.removeItem(metalBar)

        self.lastProduction = params["type"]

        timeModifier = 1
        if params["type"] == "Frame":
            timeModifier = 2
        if params["type"] == "Case":
            timeModifier = 3
        if params["type"] == "Wall":
            timeModifier = 4
        params["productionTime"] = 100*timeModifier
        params["doneProductionTime"] = 0
        params["hitCounter"] = character.numAttackedWithoutResponse
        self.produceItem_wait(params)

    def produceItem_done(self,params):
        character = params["character"]
        character.addMessage("You produce a %s"%(params["type"],))
        character.addMessage("It took you %s turns to do that"%(params["doneProductionTime"],))

        badListed = ["Sword","Armor","Rod"]
        if params["type"] in badListed:
            character.addMessage("producing this item here will result in a low quality item")
            new = src.items.itemMap[params["type"]](badQuality=True)
        else:
            new = src.items.itemMap[params["type"]]()
        new.bolted = False

        dropsSpotsFull = self.checkForDropSpotsFull()

        preferInventoryOut = True
        if params.get("key") in ("k","K",):
            preferInventoryOut = False

        if (dropsSpotsFull or preferInventoryOut) and character.getFreeInventorySpace() > 0:
            character.inventory.append(new)
        elif dropsSpotsFull:
            character.addMessage("you failed to produce since both your inventory and the dropspots are full.")
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
                    break

        character.changed("worked metal",{"item":new})

        params["amount"] -= 1
        if params["amount"]:
            self.produceItem(params)

    def getInputItems(self):

        result = []

        for offset in [(0,1,0),(0,-1,0),(1,0,0),(-1,0,0)]:
            for item in self.container.getItemByPosition(
                (self.xPosition + offset[0], self.yPosition + offset[1], self.zPosition+offset[2])
            ):
                if item.bolted:
                    continue
                result.append(item)
        return result

    def checkForDropSpotsFull(self):

        for output in self.outs:
            targetPos = (self.xPosition+output[0], self.yPosition+output[1], self.zPosition+output[2])
            targetFull = False
            itemList = self.container.getItemByPosition(targetPos)

            if len(itemList):
                targetFull = True

            if not targetFull:
                break

        return targetFull

    def checkProductionScheduleHook(self,character):
        character.addMessage(self.scheduledItems)

    def scheduleProductionHook(self,character):
        self.scheduleProduction({"character":character})

    def repeat_K(self,character):
        self.repeat(character,key="K")

    def repeat_J(self,character):
        self.repeat(character,key="J")

    def repeat_k(self,character):
        self.repeat(character,key="k")

    def repeat(self,character,key="j"):
        if not self.lastProduction:
            character.addMessage("no last produced item found")
            return
        params = {"character":character,"type":self.lastProduction,"key":key}
        self.produceItem(params)

    def scheduleProduction(self,params):

        character = params["character"]

        if "type" not in params:
            options = []
            options.append(("delete","delete"))
            options.append(("Bolt","Bolt"))
            options.append(("Rod","Rod"))
            options.append(("Frame","Frame"))
            options.append(("Case","Case"))
            options.append(("Wall","Wall"))
            options.append(("Door","Door"))
            options.append(("RoomBuilder","RoomBuilder"))
            options.append(("Painter","Painter"))
            options.append(("CityPlaner","CityPlaner"))
            options.append(("ScrapCompactor","ScrapCompactor"))
            options.append(("Sword","Sword"))
            options.append(("Armor","Armor"))
            options.append(("CoalBurner","CoalBurner"))
            options.append(("Vial","Vial"))
            options.append(("Statue","Statue"))
            options.append(("Sheet","Sheet"))
            options.append(("CorpseAnimator","Corpseanimator"))
            options.append(("Shrine","Shrine"))
            options.append(("Throne","Throne"))
            options.append(("ItemCollector","ItemCollector"))
            options.append(("PersonnelTracker","PersonnelTracker"))
            options.append(("ArmorStand","ArmorStand"))
            options.append(("WeaponRack","WeaponRack"))
            options.append(("byName","produce by name"))
            submenue = src.menuFolder.selectionMenu.SelectionMenu("what item to produce?",options,targetParamName="type")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"scheduleProduction","params":params}
            return

        if params["type"] == "delete":
            self.scheduledItems = []
            return

        if params.get("type") == "byName":
            submenue = src.menuFolder.inputMenu.InputMenu("Type the name of the item to produce",targetParamName="type")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"scheduleProduction","params":params}
            return

        if params.get("type") in self.reserved_manufactured_items:
            character.addMessage("cannot produce item type")

        if "amount" not in params:
            options = []
            options.append((1,"1"))
            options.append((5,"5"))
            options.append((10,"10"))
            options.append((50,"50"))
            options.append((100,"100"))
            options.append((500,"500"))
            options.append((1000,"1000"))
            submenue = src.menuFolder.selectionMenu.SelectionMenu("how many items to shedule?",options,targetParamName="amount")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"scheduleProduction","params":params}
            return

        amount = params["amount"]
        for _i in range(amount):
            self.scheduledItems.append(params["type"])

        character.addMessage(self.scheduledItems)

    def readyToUse(self):

        metalBarsFound = []
        for item in self.getInputItems():
            if item.type == "MetalBars":
                metalBarsFound.append(item)

        if metalBarsFound:
            return True
        else:
            return False


src.items.addType(MetalWorkingBench)
