import src

class MachiningTable(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "MachiningTable"
    name = "MachiningTable"
    description = "Use it to build machines" 
    walkable = False
    bolted = False

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

    def produceItemHook(self,character):
        self.produceItem({"character":character})

    def produceItem(self,params):
        character = params["character"]           

        if not "type" in params:
            options = []
            options.append(("Rod","Rod Machine"))
            options.append(("Frame","Frame Machine"))
            options.append(("Case","Case Machine"))
            options.append(("Wall","Wall Machine"))
            options.append(("ScrapCompactor","ScrapCompactor Machine"))
            submenue = src.interaction.SelectionMenu("Produce machine for what item?",options,targetParamName="type")
            submenue.tag = "machiningProductSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"produceItem","params":params}
            return
        
        preferInventoryOut = True
        if params.get("key") == "k":
            preferInventoryOut = False
        
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
        if not character.getFreeInventorySpace() > 0 and not metalBar in character.inventory and dropsSpotsFull:
            character.addMessage("You have no free inventory space to put the item in")
            character.changed("inventory full error",{})
            return 

        new = src.items.itemMap["Machine"]()
        new.setToProduce(params["type"])
        new.bolted = False

        if params["type"] in self.scheduledItems:
            self.scheduledItems.remove(params["type"])

        character.timeTaken += 1000
        character.addMessage("You produce a wall")
        character.addMessage("It takes you 10o0 turns to do that")
        if metalBar in character.inventory:
            character.inventory.remove(metalBar)
        else:
            self.container.removeItem(metalBar)

        if dropsSpotsFull or (preferInventoryOut and (character.getFreeInventorySpace() > 0 or not metalBar in character.inventory)):
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

        if not "type" in params:
            options = []
            options.append(("delete","delete"))
            options.append(("Wall","Wall"))
            options.append(("10Wall","10 Walls"))
            options.append(("Door","Door"))
            options.append(("10Door","10 Doors"))
            options.append(("RoomBuilder","RoomBuilder"))
            options.append(("10RoomBuilder","10 RoomBuilder"))
            options.append(("Painter","Painter"))
            options.append(("CityPlaner","CityPlaner"))
            submenue = src.interaction.SelectionMenu("what item to produce?",options,targetParamName="type")
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

            for i in range(0,amount):
                self.scheduledItems.append(params["type"])

        character.addMessage(self.scheduledItems)

src.items.addType(MachiningTable)
