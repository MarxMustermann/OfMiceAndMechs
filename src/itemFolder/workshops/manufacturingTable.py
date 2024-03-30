import src


class ManufacturingTable(src.items.Item):
    """
    """

    type = "ManufacturingTable"
    name = "ManufacturingTable"
    description = "Use it to build simple things"
    walkable = False
    bolted = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display = "MT")

        self.applyOptions.extend(
                        [
                                                                ("produce item", "produce item"),
                                                                ("configure item", "configure item"),
                                                                ("draw stockpiles", "draw stockpiles"),
                        ]
                        )
        self.applyMap = {
                    "produce item": self.produceItem,
                    "configure item": self.configureItemHook,
                    "draw stockpiles": self.drawStockpiles,
                        }

        self.ins = [(-1,0,0),(0,-1,0),(0,1,0)]
        self.outs = [(1,0,0)]
        self.lastProduction = None
        self.toProduce = None
        self.numUsed = 0
        self.inUse = False
        self.disabled = False

    """
    auto generate stockpiles
    """
    def drawStockpiles(self,character):
        # paint each output
        for out in self.outs:
            # calculate position to add the output to
            stockpilePos = (self.xPosition+out[0],self.yPosition+out[1],self.zPosition)

            # remove old markings
            self.container.clearMarkings(stockpilePos)

            # add output stockpile
            self.container.addStorageSlot(stockpilePos,self.toProduce)

        # get the materials needed
        materialsNeeded = src.items.rawMaterialLookup.get(self.toProduce)
        if self.toProduce == "MetalBars":
            materialsNeeded = ["Scrap"]
        if not materialsNeeded:
            materialsNeeded = ["MetalBars"]

        # paint inputs for materials needed
        counter = 0
        for material in materialsNeeded:
            # calculate position to add the input to
            stockpilePos = (self.xPosition+self.ins[counter][0],self.yPosition+self.ins[counter][1],self.zPosition)

            # remove old markings
            self.container.clearMarkings(stockpilePos)

            # add input stockpile
            self.container.addInputSlot(stockpilePos,material)

            # prepare next loop round
            counter += 1

    def configureItemHook(self,character):
        self.configureItem({"character":character})

    def configureItem(self,params):
        character = params["character"]

        if "type" not in params:
            options = []
            options.append(("None","None"))
            options.append(("MetalBars","MetalBars"))
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
            submenue = src.interaction.SelectionMenu("what item to produce?",options,targetParamName="type")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"configureItem","params":params}
            return

        if params.get("type") == "byName":
            submenue = src.interaction.InputMenu("Type the name of the item to produce",targetParamName="type")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"configureItem","params":params}
            return

        if params.get("type") == "Machine":
            character.addMessage("Not possible. Use a MachiningTable.")
            return
        blackListed = ["GlassHeart","Machine",]
        if params.get("type") in blackListed:
            character.addMessage("Not possible.")
            return

        if params.get("type") == "None":
            self.toProduce = None
            self.numUsed = 0
            return

        if params.get("type") not in src.items.itemMap:
            if params.get("type"):
                character.addMessage("Item type unknown.")
            return

        self.toProduce = params.get("type")
        self.numUsed = 0

    def produceItem(self,character):
        if self.disabled:
            character.addMessage("This item is disabled")
            character.changed("failed manufacturing",{})
            return False
        if not self.bolted:
            character.addMessage("This item needs to be bolted down to be used")
            character.changed("failed manufacturing",{})
            return

        if self.inUse:
            character.addMessage("This item is in use")
            character.changed("failed manufacturing",{})
            return

        params = {"character":character,"type":self.toProduce,"key":"k"}

        materialsNeeded = src.items.rawMaterialLookup.get(self.toProduce)
        if self.toProduce == "MetalBars":
            materialsNeeded = ["Scrap"]

        if not materialsNeeded:
            materialsNeeded = ["MetalBars"]

        itemsFound = []
        for material in materialsNeeded:
            for item in self.getInputItems():
                if item in itemsFound:
                    continue
                if item.type == material:
                    itemsFound.append(item)
                    break

        if not len(materialsNeeded) == len(itemsFound):
            character.addMessage(f"You need to put the raw items into the manufacturing tables input\nitems: {materialsNeeded}")
            character.changed("failed manufacturing",{})
            return

        dropsSpotsFull = self.checkForDropSpotsFull()
        if dropsSpotsFull:
            character.addMessage("the manufacturing tables output slot is full")
            character.changed("failed manufacturing",{})
            return

        if not self.toProduce == "MetalBars" or itemsFound[0].amount == 1:
            self.container.removeItems(itemsFound)
        else:
            itemsFound[0].amount -= 1
            itemsFound[0].setWalkable()

        params["productionTime"] = 75-min(50,self.numUsed)
        if self.toProduce == "MetalBars":
            params["productionTime"] = params["productionTime"]//10
        params["doneProductionTime"] = 0
        self.produceItem_wait(params)
        character.runCommandString("."*(params["productionTime"]//10+1),nativeKey=True)
        self.numUsed += 1

        self.inUse = True

    def produceItem_wait(self,params):
        character = params["character"]
        ticksLeft = params["productionTime"]-params["doneProductionTime"]

        progressbar = "X"*(params["doneProductionTime"]//10)+"."*(ticksLeft//10)
        if ticksLeft > 10:
            character.timeTaken += 10
            params["doneProductionTime"] += 10
            submenue = src.interaction.OneKeystrokeMenu(progressbar,targetParamName="abortKey")
            submenue.tag = "metalWorkingProductWait"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItem_wait","params":params}
        else:
            character.timeTaken += ticksLeft
            params["doneProductionTime"] += ticksLeft
            submenue = src.interaction.OneKeystrokeMenu(progressbar,targetParamName="abortKey")
            submenue.tag = "metalWorkingProductWait"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItem_done","params":params}

    def produceItem_done(self,params):
        character = params["character"]
        if not params["type"]:
            return
        character.addMessage("You produce a "+params["type"])
        character.addMessage("It took you "+str(params["productionTime"])+" turns to do that")

        badListed = ["Sword","Armor","Rod"]
        if params["type"] in badListed:
            character.addMessage("producing this item here will result in a low quality item")
            new = src.items.itemMap[params["type"]](badQuality=True)
        else:
            new = src.items.itemMap[params["type"]]()
        new.bolted = False

        dropsSpotsFull = self.checkForDropSpotsFull()

        if dropsSpotsFull:
            character.addMessage("you failed to produce since the dropspots is full.")
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

        character.changed("manufactured",{"item":new,"table":self})
        self.inUse = False

    def readyToUse(self):
        if self.disabled:
            return False
        if not self.toProduce:
            return False
        if not self.bolted:
            return False
        if self.inUse:
            return False

        materialsNeeded = src.items.rawMaterialLookup.get(self.toProduce)
        if self.toProduce == "MetalBars":
            materialsNeeded = ["Scrap"]
        if not materialsNeeded:
            materialsNeeded = ["MetalBars"]

        itemsFound = []
        for material in materialsNeeded:
            for item in self.getInputItems():
                if item in itemsFound:
                    continue
                if item.type == material:
                    itemsFound.append(item)
                    break

        if not len(materialsNeeded) == len(itemsFound):
            return False

        dropsSpotsFull = self.checkForDropSpotsFull()
        if dropsSpotsFull:
            return False

        return True

    def getInputItems(self):

        result = []

        for offset in self.ins:
            for item in self.container.getItemByPosition(
                (self.xPosition + offset[0], self.yPosition + offset[1], self.zPosition+offset[2])
            ):
                if item.bolted:
                    continue
                result.append(item)
        return result

    def isOutputEmpty(self):

        for output in self.outs:
            targetPos = (self.xPosition+output[0], self.yPosition+output[1], self.zPosition+output[2])
            targetFull = False
            itemList = self.container.getItemByPosition(targetPos)

            if not itemList:
                return True

        return False

    def checkForDropSpotsFull(self):

        for output in self.outs:
            targetPos = (self.xPosition+output[0], self.yPosition+output[1], self.zPosition+output[2])
            targetFull = False
            itemList = self.container.getItemByPosition(targetPos)

            if itemList:
                if len(itemList) > 10 or (not itemList[0].walkable):
                    targetFull = True

            if not targetFull:
                break

        return targetFull

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
        if self.disabled:
            options["d"] = ("enable", self.enable)
        else:
            options["d"] = ("disable", self.disable)
        return options

    def enable(self,character):
        character.addMessage("you enable the Machine")
        self.disabled = False

    def disable(self,character):
        character.addMessage("you disable the Machine")
        self.disabled = True

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the ManufacuringTable")
        character.changed("boltedItem",{"character":character,"item":self})
        self.numUsed = 0

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the ManufacturingTable")
        character.changed("unboltedItem",{"character":character,"item":self})
        self.numUsed = 0

    def getLongInfo(self):
        """
        generate simple text description

        Returns:
            the decription text
        """

        text = super().getLongInfo()
        text += f"""

toProduce: {self.toProduce}
numUsed: {self.numUsed}
"""

        return text

    def render(self):
        if self.disabled or self.toProduce == None:
            return "mT"
        if self.inUse:
            return "mt"
        if self.readyToUse():
            return "MT"
        else:
            return "Mt"


src.items.addType(ManufacturingTable)
