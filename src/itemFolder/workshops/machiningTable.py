import src


class MachiningTable(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "MachiningTable"
    name = "MachiningTable"
    description = "Use it to build machines"
    walkable = False
    bolted = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display = "WX")

        self.applyOptions.extend(
                        [
                                                                ("produce item", "produce item"),
                                                                ("check schedule production", "check schedule"),
                                                                ("schedule production", "schedule production"),
                        ]
                        )
        self.applyMap = {
                    "produce item": self.produceItemHook,
                    "check schedule production": self.checkProductionScheduleHook,
                    "schedule production": self.scheduleProductionHook,
                        }

        self.ins = [(1,0,0),(-1,0,0),]
        self.outs = [(0,-1,0),]
        self.scheduledItems = []
        self.default_item_types = ["Rod","Frame","Case","Wall","Sheet","Sword","Armor","Bolt","ScrapCompactor"]

    def produceItemHook(self,character):
        self.produceItem({"character":character})

    def produceItem(self,params):
        character = params["character"]

        if "type" not in params:
            options = []
            for item_type in self.default_item_types:
                options.append((item_type,item_type))
            options.append(("byName","produce by name"))
            submenue = src.menuFolder.SelectionMenu.SelectionMenu("Produce machine for what item?",options,targetParamName="type")
            submenue.tag = "machiningProductSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItem","params":params}
            return

        if params.get("type") == "byName":
            submenue = src.menuFolder.InputMenu.InputMenu("Type the name of the item to produce?",targetParamName="type")
            submenue.tag = "machiningTableProductInput"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItem","params":params}
            return

        if params.get("type") not in src.items.itemMap:
            if params.get("type"):
                character.addMessage("Item type unknown.")
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

        if metalBar in character.inventory:
            character.inventory.remove(metalBar)
        else:
            self.container.removeItem(metalBar)

        if params["type"] in self.scheduledItems:
            self.scheduledItems.remove(params["type"])

        params["productionTime"] = 1000
        params["doneProductionTime"] = 0
        self.produceItem_wait(params)
        character.runCommandString("."*(params["productionTime"]//10),nativeKey=True)

    def produceItem_wait(self,params):
        character = params["character"]
        ticksLeft = params["productionTime"]-params["doneProductionTime"]

        baseProgressbar = "X"*(params["doneProductionTime"]//10)+"."*(ticksLeft//10)
        progressBar = ""
        while len(baseProgressbar) > 10:
            progressBar += baseProgressbar[:10]+"\n"
            baseProgressbar = baseProgressbar[10:]
        progressBar += baseProgressbar
        if ticksLeft > 10:
            character.timeTaken += 10
            params["doneProductionTime"] += 10
            submenue = src.menuFolder.OneKeystrokeMenu.OneKeystrokeMenu(progressBar,targetParamName="abortKey")
            submenue.tag = "metalWorkingProductWait"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItem_wait","params":params}
        else:
            character.timeTaken += ticksLeft
            params["doneProductionTime"] += ticksLeft
            submenue = src.menuFolder.OneKeystrokeMenu.OneKeystrokeMenu(progressBar,targetParamName="abortKey")
            submenue.tag = "metalWorkingProductWait"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItem_done","params":params}

    def produceItem_done(self,params):
        character = params["character"]

        preferInventoryOut = True
        if params.get("key") == "k":
            preferInventoryOut = False

        dropsSpotsFull = self.checkForDropSpotsFull()
        if not character.getFreeInventorySpace() > 0 and dropsSpotsFull:
            character.addMessage("You have no free inventory space to put the item in")
            character.changed("inventory full error",{})
            return

        new = src.items.itemMap["Machine"]()
        new.setToProduce(params["type"])
        new.bolted = False

        character.addMessage("You produce a wall")
        character.addMessage("It takes you 1000 turns to do that")

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

        character.changed("constructed machine",{})

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

    def scheduleProduction(self,params):

        character = params["character"]

        if "type" not in params:
            options = []
            options.append(("delete","delete"))
            for item_type in self.default_item_types:
                options.append((item_type,item_type))
            options.append(("Bolt","Bolt"))
            submenue = src.menuFolder.SelectionMenu.SelectionMenu("what item to produce?",options,targetParamName="type")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"scheduleProduction","params":params}
            return

        if params["type"] == "delete":
            self.scheduledItems = []
        elif params["type"]:
            amount = 1
            if params["type"].startswith("10"):
                params["type"] = params["type"][2:]
                amount = 10

            for _i in range(amount):
                self.scheduledItems.append(params["type"])

        character.addMessage(self.scheduledItems)

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
        character.addMessage("you bolt down the MachiningTable")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the MachiningTable")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(MachiningTable)
