import src

class AlchemyTable(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "AlchemyTable"
    name = "AlchemyTable"
    description = "Use it to build brew potions"
    walkable = False
    bolted = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display = "AT")

        self.applyOptions.extend(
                        [
                                                                ("produce potion", "produce potion"),
                                                                ("check schedule production", "check schedule"),
                                                                ("schedule production", "schedule production"),
                                                                ("repeat", "repeat last production"),
                        ]
                        )
        self.applyMap = {
                    "produce potion": self.producePotionHook,
                    "check schedule production": self.checkProductionScheduleHook,
                    "schedule production": self.scheduleProductionHook,
                    "repeat": self.repeat,
                        }

        self.ins = [(-1,0,0),(0,1,0)]
        self.outs = [(1,0,0)]
        self.scheduledItems = []
        self.lastProduction = None

    def producePotionHook(self,character):
        self.producePotion({"character":character})

    def producePotion(self,params):
        character = params["character"]

        if "type" not in params:
            options = []
            options.append(("IncreaseHealthRegenPotion","IncreaseHealthRegenPotion"))
            options.append(("IncreaseMaxHealthPotion","IncreaseMaxHealthPotion"))
            options.append(("StrengthPotion","StrengthPotion"))
            options.append(("byName","produce by name"))
            submenue = src.menuFolder.SelectionMenu.SelectionMenu("what item to produce?",options,targetParamName="type")
            submenue.tag = "metalWorkingProductSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"producePotion","params":params}
            return

        if params.get("type") == "byName":
            submenue = src.menuFolder.InputMenu.InputMenu("Type the name of the item to produce",targetParamName="type")
            submenue.tag = "metalWorkingProductInput"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItem","params":params}
            return

        if not "Potion" in params.get("type"):
            character.addMessage("You can only produce Potions here.")
            return

        if params.get("type") not in src.items.itemMap:
            if params.get("type"):
                character.addMessage("Item type unknown.")
            return

        vials = []
        for item in character.inventory+self.getInputItems():
            if item.type != "Vial":
                continue
            if item.uses < 10:
                continue
            vials.append(item)

        if not vials:
            character.addMessage("You need to have a full vial in your inventory to use produce a potion")
            character.changed("no full Vial error",{})
            return

        vial = vials[-1]

        dropsSpotsFull = self.checkForDropSpotsFull()
        if not character.getFreeInventorySpace() > 0 and vial not in character.inventory and dropsSpotsFull:
            character.addMessage("You have no free inventory space to put the item in")
            character.changed("inventory full error",{})
            return

        if params["type"] in self.scheduledItems:
            self.scheduledItems.remove(params["type"])

        if vial in character.inventory:
            character.inventory.remove(vial)
        else:
            self.container.removeItem(vial)

        self.lastProduction = params["type"]

        params["productionTime"] = 100
        params["doneProductionTime"] = 0
        params["hitCounter"] = character.numAttackedWithoutResponse
        self.producePotion_wait(params)

    def producePotion_wait(self, params):
        character = params["character"]
        if params["hitCounter"] != character.numAttackedWithoutResponse:
            character.addMessage("You got hit while working")
            return
        ticksLeft = params["productionTime"] - params["doneProductionTime"]
        character.timeTaken += 1
        params["doneProductionTime"] += 1
        progressbar = "X" * (params["doneProductionTime"] // 10) + "." * (ticksLeft // 10)
        submenue = src.menuFolder.OneKeystrokeMenu.OneKeystrokeMenu(progressbar, targetParamName="abortKey")
        submenue.tag = "alchemyTableProductWait"
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {
            "container": self,
            "method": "producePotion_done" if ticksLeft <= 0 else "producePotion_wait",
            "params": params,
        }
        character.runCommandString(".", nativeKey=True)
        if ticksLeft % 10 != 9 and src.gamestate.gamestate.mainChar == character:
            src.interaction.skipNextRender = True

    def producePotion_done(self,params):
        character = params["character"]
        character.addMessage("You produce a %s"%(params["type"],))
        character.addMessage("It took you %s turns to do that"%(params["doneProductionTime"],))

        dropsSpotsFull = self.checkForDropSpotsFull()

        preferInventoryOut = True
        if params.get("key") == "k":
            preferInventoryOut = False

        new = src.items.itemMap[params["type"]]()
        new.bolted = False

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

        character.changed("brewed potion",{"item":new})

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

    def repeat(self,character):
        if not self.lastProduction:
            character.addMessage("no last produced item found")
            return
        params = {"character":character,"type":self.lastProduction}
        self.produceItem(params)

    def scheduleProduction(self,params):

        character = params["character"]

        if "type" not in params:
            options = []
            options.append(("delete","delete"))
            options.append(("IncreaseHealthRegenPotion","IncreaseHealthRegenPotion"))
            options.append(("IncreaseMaxHealthPotion","IncreaseMaxHealthPotion"))
            options.append(("StrengthPotion","StrengthPotion"))
            options.append(("byName","produce by name"))
            submenue = src.menuFolder.SelectionMenu.SelectionMenu("what potion to produce?",options,targetParamName="type")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"scheduleProduction","params":params}
            return

        if params["type"] == "delete":
            self.scheduledItems = []
            return

        if params.get("type") == "byName":
            submenue = src.menuFolder.InputMenu.InputMenu("Type the name of the potion to produce",targetParamName="type")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"scheduleProduction","params":params}
            return

        if "amount" not in params:
            options = []
            options.append((1,"1"))
            options.append((5,"5"))
            options.append((10,"10"))
            options.append((50,"50"))
            options.append((100,"100"))
            options.append((500,"500"))
            options.append((1000,"1000"))
            submenue = src.menuFolder.SelectionMenu.SelectionMenu("how many items to shedule?",options,targetParamName="amount")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"scheduleProduction","params":params}
            return

        amount = params["amount"]
        for _i in range(amount):
            self.scheduledItems.append(params["type"])

        character.addMessage(self.scheduledItems)

    def readyToUse(self):

        vials = []
        for item in character.inventory+self.getInputItems():
            if item.type != "Vial":
                continue
            if item.uses < 10:
                continue
            vials.append(item)

        if not vials:
            return True
        else:
            return False

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
        character.addMessage("you bolt down the AlchemyTable")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the AlchemyTable")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(AlchemyTable)
