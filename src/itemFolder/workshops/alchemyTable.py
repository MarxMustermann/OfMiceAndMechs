import src

class AlchemyTable(src.items.itemMap["WorkShop"]):
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
                        ]
                        )
        self.applyMap = {
                    "produce potion": self.producePotionHook,
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
            for potionType in src.items.potionTypes:
                options.append((potionType.type,potionType.name))
            options.append(("byName","produce by name"))
            submenue = src.menuFolder.selectionMenu.SelectionMenu("what item to produce?",options,targetParamName="type")
            submenue.tag = "alchemyTableProductSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"producePotion","params":params}
            return

        if params.get("type") == "byName":
            submenue = src.menuFolder.inputMenu.InputMenu("Type the name of the item to produce",targetParamName="type")
            submenue.tag = "alchemyTableProductInput"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"producePotion","params":params}
            return

        if params.get("type") == None:
            return

        if not "Potion" in params.get("type"):
            character.addMessage("You can only produce Potions here.")
            return

        if params.get("type") not in src.items.itemMap:
            if params.get("type"):
                character.addMessage("Item type unknown.")
            return
        accessible_items = character.inventory+self.getInputItems()
        flasks = []
        for item in accessible_items:
            if item.type != "Flask":
                continue
            flasks.append(item)

        if not flasks:
            character.addMessage("You need to have a Flask in your inventory to use produce a potion")
            character.changed("no Flask error",{})
            return

        flask = flasks[-1]

        dropsSpotsFull = self.checkForDropSpotsFull()
        if not character.getFreeInventorySpace() > 0 and flask not in character.inventory and dropsSpotsFull:
            character.addMessage("You have no free inventory space to put the item in")
            character.changed("inventory full error",{})
            return
        needed_Ingredients = {ing:None for ing in src.items.itemMap[params["type"]].Ingredients()}
        for item in accessible_items:
            t = type(item)
            if t in needed_Ingredients and needed_Ingredients[t] is None:
                needed_Ingredients[t] = item
        have_ingredients = all(needed_Ingredients[ing] is not None for ing in needed_Ingredients)
        
        if not have_ingredients:
            n = ""
            i = 1
            for ing in needed_Ingredients:
                if needed_Ingredients[ing] is None:
                    n+= ing.name
                    if i != len(needed_Ingredients):
                        n+= ", "
            character.addMessage("you don't have the "+ n +" ingredient in your inventory")
            return
        if params["type"] in self.scheduledItems:
            self.scheduledItems.remove(params["type"])
        to_remove = [flask] + [needed_Ingredients[ing] for ing in needed_Ingredients]
        for item in to_remove:
            if item in character.inventory:
                character.inventory.remove(item)
            else:
                self.container.removeItem(item)

        self.lastProduction = params["type"]

        params["productionTime"] = 100
        params["doneProductionTime"] = 0
        params["hitCounter"] = character.numAttackedWithoutResponse
        self.produceItem_wait(params)

    def produceItem_done(self,params):
        character = params["character"]
        character.stats["items produced"][params["type"]] = character.stats["items produced"].get(params["type"], 0) + 1
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
            submenue = src.menuFolder.selectionMenu.SelectionMenu("what potion to produce?",options,targetParamName="type")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"scheduleProduction","params":params}
            return

        if params["type"] == "delete":
            self.scheduledItems = []
            return

        if params.get("type") == "byName":
            submenue = src.menuFolder.inputMenu.InputMenu("Type the name of the potion to produce",targetParamName="type")
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
            submenue = src.menuFolder.selectionMenu.SelectionMenu("how many items to shedule?",options,targetParamName="amount")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"scheduleProduction","params":params}
            return

        amount = params["amount"]
        for _i in range(amount):
            self.scheduledItems.append(params["type"])

        character.addMessage(self.scheduledItems)

    def readyToUse(self):

        flasks = []
        for item in character.inventory+self.getInputItems():
            if item.type != "Flask":
                continue
            flasks.append(item)

        if not flasks:
            return True
        else:
            return False

src.items.addType(AlchemyTable)
