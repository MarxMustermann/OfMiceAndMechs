import src

class StockpileMetaManager(src.items.Item):
    type = "StockpileMetaManager"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="stockpile meta manager",creator=None,noId=False):
        self.jobOrders = []
        self.commands = {}
        self.stockPiles = []
        self.stockPileInfo = {}
        self.assignedPlots = []
        self.assignedPlotsInfo = {}
        self.tasks = []
        self.lastAction = ""
        self.roomManagerName = ""

        super().__init__("SM",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False
        self.blocked = False

        #settings
        self.autoExpand = True

        self.attributesToStore.extend([
               "stockPiles","stockPileInfo","assignedPlots","assignedPlotsInfo","roomManagerName"])

        self.applyOptions.extend([("clearInventory","clear inventory"),("addItem","add item"),("addTask","add task"),("doMaintenance","do maintenance"),("test","test")])
        self.applyMap = {
                            "clearInventory":self.doClearInventory,
                            "addItem":self.doAddItem,
                            "addTask":self.addTask,
                            "doMaintenance":self.doMaintenance,
                            "test":self.test,
                        }

    def addTask(self,character):
        self.tasks.append({"task":"extend storage"})

    def applyOld(self,character):
        if not (character.xPosition == self.xPosition and character.yPosition == self.yPosition-1):
            character.addMessage("this item can only be used from north")
            return
        if self.blocked and not self.character.dead:
            character.runCommandString("Js")
            character.addMessage("item blocked - auto retry")
            return

        self.lastAction = "apply"

        self.blocked = True
        options = [("clearInventory","clear inventory"),("addItem","add item"),("addTask","add Task"),("doMaintanance","do maintanance"),("test","test")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def test(self,character):
        character = src.characters.Character(name="logistics npc")
        character.godMode = True
        character.xPosition = self.xPosition
        character.yPosition = self.yPosition-1
        self.container.addCharacter(character,self.xPosition,self.yPosition-1)
        character.macroState["macros"] = {
                              "a":["J","s",".","s","s","s","j","_","a"],
                            }
        character.runCommandString("_a")

    def doMaintenance(self,character):
        """
        if self.tasks:
            task = self.tasks.pop()
            if task["task"] == "extend storage":
                self.useJoborderRelayToLocalRoom(context["character"],[
                        {"task":"add task","tasks":[{"task":"extend storage"},],}
                    ],"CityBuilder")
            return
        """

        self.lastAction = "doMaintanance"
        if self.assignedPlots:

            self.lastAction = "addStockPileItem"
            character.addMessage("add stockpile item "+stockpile)
            character.inventory.append(src.items.TypedStockpileManager())
            plot = self.assignedPlots.pop()
            command = []
            command.extend(self.assignedPlotsInfo[plot]["pathTo"])
            command.extend(["L","s"])
            command.extend(self.assignedPlotsInfo[plot]["pathFrom"])
            self.stockPileInfo[plot] = self.assignedPlotsInfo[plot]
            self.stockPiles.append(plot)
            del self.assignedPlotsInfo[plot]

            convertedCommand = []
            for char in command:
                convertedCommand.append((char,"norecord"))

            character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
            self.blocked = False
            return

        #check stockpiles
        for stockpile in self.stockPiles:
            if not "stockPileType" in self.stockPileInfo[stockpile]:
                self.lastAction = "initialCheckStockpile"
                jobOrder = src.items.itemMap["JobOrder"]()
                jobOrder.tasks = [
                    {
                        "task":"processStatusReport",
                        "command":None
                    },
                    {
                        "task":"insert completed job order into stockpile manager",
                        "command":"scj",
                    },]
                if self.roomManagerName:
                    jobOrder.tasks.append(
                        {
                            "task":"move to stockpile manager",
                            "command":self.commands["return from room manager"],
                        })
                jobOrder.tasks.extend([
                    {
                        "task":"walk back to stockpile manager",
                        "command":self.stockPileInfo[stockpile]["pathFrom"]
                    },
                    {
                        "task":"generateStatusReport",
                        "command":None
                    },
                    {
                        "task":"insert job order",
                        "command":["s","c","j"],
                    },
                    {
                        "task":"go to stockpile",
                        "command":self.stockPileInfo[stockpile]["pathTo"],
                    },])
                if self.roomManagerName:
                    jobOrder.tasks.append(
                        {
                            "task":"move to room manager",
                            "command":self.commands["go to room manager"],
                        })
                jobOrder.tasks.extend([
                    {
                        "task":"clear head",
                        "command":".zclear ", 
                    },
                    ])
                jobOrder.taskName = "get statusreport initial"
                jobOrder.information["stockPile"] = stockpile

                character.addMessage("running job order to check stockpile")
                character.jobOrders.append(jobOrder)
                character.runCommandString("Jj.j")
                self.blocked = False
                return

        #check sinks
        for stockpile in self.stockPiles:
            if self.stockPileInfo[stockpile].get("sink") == True and self.stockPileInfo[stockpile]["amount"] >= self.stockPileInfo[stockpile]["desiredAmount"]:
                self.lastAction = "check sinks"
                jobOrder = src.items.itemMap["JobOrder"]()
                jobOrder.tasks = [
                    {
                        "task":"processStatusReport",
                        "command":None
                    },
                    {
                        "task":"insert completed job order into stockpile manager",
                        "command":"scwj",
                    },]
                if self.roomManagerName:
                    jobOrder.tasks.append(
                        {
                            "task":"return from stockpile manager",
                            "command":self.commands["return from room manager"],
                        })
                jobOrder.tasks.extend([
                    {
                        "task":"walk back to stockpile manager",
                        "command":self.stockPileInfo[stockpile]["pathFrom"],
                    },
                    {
                        "task":"generateStatusReport",
                        "command":None
                    },
                    {
                        "task":"insert job order",
                        "command":["s","c","j"],
                    },
                    {
                        "task":"go to stockpile",
                        "command":self.stockPileInfo[stockpile]["pathTo"],
                    },
                    ])
                if self.roomManagerName:
                    jobOrder.tasks.append(
                        {
                            "task":"move to room manager",
                            "command":self.commands["go to room manager"],
                        })
                jobOrder.tasks.append(
                    {
                        "task":"clear head",
                        "command":"zclear ",
                    })
                jobOrder.taskName = "get statusreport sink"
                jobOrder.information["stockPile"] = stockpile

                character.addMessage("running job order to check sink stockpile")
                character.jobOrders.append(jobOrder)
                character.runCommandString("Jj.j")
                self.blocked = False
                return

        #check sinks
        for stockpile in self.stockPiles:
            if self.stockPileInfo[stockpile].get("source") == True and (self.stockPileInfo[stockpile]["amount"] == 0 or ("desiredAmount" in self.stockPileInfo[stockpile] and self.stockPileInfo[stockpile]["amount"] <= self.stockPileInfo[stockpile]["desiredAmount"])):
                self.lastAction = "check sources"
                jobOrder = src.items.itemMap["JobOrder"]()
                jobOrder.tasks = [
                    {
                        "task":"processStatusReport",
                        "command":None
                    },
                    {
                        "task":"insert completed job order into stockpile manager",
                        "command":"scj",
                    },]
                if self.roomManagerName:
                    jobOrder.tasks.append(
                        {
                            "task":"return from room manager",
                            "command":self.commands["return from room manager"],
                        })
                jobOrder.tasks.extend([
                    {
                        "task":"walk back to stockpile manager",
                        "command":self.stockPileInfo[stockpile]["pathFrom"]
                    },
                    {
                        "task":"generateStatusReport",
                        "command":None
                    },
                    {
                        "task":"insert job order",
                        "command":"scj",
                    },
                    {
                        "task":"go to stockpile",
                        "command":self.stockPileInfo[stockpile]["pathTo"],
                    },])
                if self.roomManagerName:
                    jobOrder.tasks.append(
                        {
                            "task":"move to room manager",
                            "command":self.commands["go to room manager"],
                        })
                jobOrder.tasks.append(
                    {
                        "task":"clear head",
                        "command":"zclear ",
                    })
                jobOrder.taskName = "get statusreport source"
                jobOrder.information["stockPile"] = stockpile

                character.addMessage("running job order to check source stockpile")
                character.jobOrders.append(jobOrder)
                character.runCommandString("Jj.j")
                self.blocked = False
                return

        # fill stockpile
        needyStockpiles = {}
        sources = {}
        for stockPile in self.stockPiles:
            stockPileInfo = self.stockPileInfo[stockPile]
            if "desiredAmount" in stockPileInfo:
                if stockPileInfo["desiredAmount"] > stockPileInfo["amount"]:
                    itemType = stockPileInfo.get("itemType")
                    if itemType == None:
                        itemType = "all"
                    if not needyStockpiles.get(itemType):
                        needyStockpiles[itemType] = []
                    needyStockpiles[itemType].append(stockPile)

            if stockPileInfo.get("source") == True:
                itemType = stockPileInfo.get("itemType")
                if itemType == None:
                    itemType = "all"
                if not sources.get(itemType):
                    sources[itemType] = []
                sources[itemType].append(stockPile)

        stockPileFound = None
        for itemType in needyStockpiles.keys():
            if not itemType in sources:
                continue
            stockPile = sources[itemType][0]
            stockPileFound = stockPile
            targetStockPile = needyStockpiles[itemType][0]
            break

        if stockPileFound:
            self.lastAction = "fill sink"
            character.addMessage("fill desired stockpile amount"+stockPileFound)
            command = []

            sourceStockPileInfo = self.stockPileInfo[stockPile]
            targetStockPileInfo = self.stockPileInfo[targetStockPile]
            amount = min(10-len(character.inventory),targetStockPileInfo["maxAmount"]-targetStockPileInfo["amount"],sourceStockPileInfo["amount"])

            tasks = []
            tasks.append(
                {
                    "task":"move to room manager",
                    "command":self.commands["go to room manager"],
                })
            tasks.extend([
                    {
                        "task":"go to source stockpile",
                        "command":sourceStockPileInfo["pathTo"],
                    },
                    {
                        "task":"fetch resources",
                        "command":"Js.sj"*amount,
                    },
                    {
                        "task":"return to room manager",
                        "command":sourceStockPileInfo["pathFrom"],
                    },
                    ])
            sourceStockPileInfo["amount"] -= amount

            tasks.extend([
                    {
                        "task":"go to target stockpile",
                        "command":targetStockPileInfo["pathTo"],
                    },
                    {
                        "task":"store resources",
                        "command":"Js.j"*amount,
                    },
                    {
                        "task":"return to room manager",
                        "command":targetStockPileInfo["pathFrom"],
                    },
                    ])

            tasks.append(
                {
                    "task":"return from room manager",
                    "command":self.commands["return from room manager"],
                })

            targetStockPileInfo["amount"] += amount

            jobOrder = src.items.itemMap["JobOrder"]()
            jobOrder.tasks = list(reversed(tasks))
            jobOrder.taskName = "transfer resources"

            character.addJobOrder(jobOrder)

            self.blocked = False
            return
        self.blocked = False

    def doClearInventory(self,character):
        self.lastAction = "clearInventory"

        amount = len(character.inventory)
        command = "Js.s.j"*amount
        character.runCommandString(command)
        self.blocked = False

    def doAddItem(self,character):
        self.lastAction = "addItem"

        if not character.inventory:
            character.addMessage("empty inventory")
            self.blocked = False
            return
        item = character.inventory[-1]

        stockPileFound = None
        for stockPile in self.stockPiles:
            stockPileInfo = self.stockPileInfo[stockPile]

            if not stockPileInfo["active"] == True:
                continue

            if stockPileInfo.get("source") == True:
                continue

            if not stockPileInfo["amount"] < stockPileInfo["maxAmount"]:
                continue

            if not stockPileInfo.get("itemType") in (None,"",item.type):
                continue

            stockPileFound = stockPile
            break

        if not stockPileFound:
            character.addMessage("full")
            if self.autoExpand:
                self.useJoborderRelayToLocalRoom(character,[
                    {"task":"add task","tasks":[
                        {"task":"extend storage"},
                        ]},
                    ],"CityBuilder")

            self.blocked = False
            return

        command = []
        if self.roomManagerName:
            command.extend(self.commands["go to room manager"])
        command.extend(stockPileInfo["pathTo"])
        command.extend(["J","s",".","j"])
        command.extend(stockPileInfo["pathFrom"])
        if self.roomManagerName:
            command.extend(self.commands["return from room manager"])
        stockPileInfo["amount"] += 1

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
        self.blocked = False

    def configure(self,character):
        if self.blocked:
            character.runCommandString("sc")
            character.addMessage("item blocked - auto retry")
            return

        self.blocked = True

        self.lastAction = "configure"

        options = [
                    ("runJobOrder","run job order"),
                    ("addCommand","add command"),
                    ("stockpile","stockpile selection"),
                    ("addStockpile","add stockpile"),
                    ("reset","reset machine"),
                    ("configureStockpiles","set stockpile settings"),
                    ("addPlot","add plot"),
                  ]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def doAddStockpile(self,task,context=None):
        nodeName = task["nodeName"]
        self.stockPiles.append(task["nodeName"])
        self.stockPileInfo[task["nodeName"]] = {}
        self.stockPileInfo[task["nodeName"]]["pathTo"] = task["pathTo"]
        self.stockPileInfo[task["nodeName"]]["pathFrom"] = task["pathFrom"] 
        if task.get("function") == "source":
            self.stockPileInfo[task["nodeName"]]["source"] = True
        if task.get("function") == "sink":
            self.stockPileInfo[task["nodeName"]]["sink"] = True
        self.stockPileInfo[task["nodeName"]]["active"] = False

    def configure2(self):
        self.lastAction = "configure2"
        if self.submenue.selection == "runJobOrder":
            if not self.character.jobOrders:
                self.character.addMessage("no job order found")
                self.blocked = False
                return
            
            jobOrder = self.character.jobOrders[-1]
            
            if jobOrder.getTask()["task"] == "add stockpile":
                self.doAddStockpile(jobOrder.popTask())
            if jobOrder.getTask()["task"] == "do maintanence":
                self.character.runCommandString("Js.sssj")
            if jobOrder.getTask()["task"] == "store item":
                self.character.runCommandString("Js.sj")
                jobOrder.popTask()
            if jobOrder.getTask()["task"] == "clear inventory":
                amount = len(self.character.inventory)
                command = "Js.s.j"*amount
                self.character.runCommandString(command)
            if jobOrder.getTask()["task"] == "configure machine":
                task = jobOrder.popTask()

                if "commands" in task:
                    self.commands.update(task["commands"])
                if "managerName" in task:
                    self.roomManagerName = task["managerName"]
            if jobOrder.getTask()["task"] == "processStatusReport":
                stockPile = jobOrder.information["stockPile"]
                stockPileInfo = self.stockPileInfo[stockPile]

                if self.character.getRegisterValue("type") == "UniformStockpileManager":
                    stockPileInfo["stockPileType"] = self.character.getRegisterValue("type")
                    stockPileInfo["amount"] = self.character.getRegisterValue("numItemsStored")
                    stockPileInfo["maxAmount"] = self.character.getRegisterValue("maxAmount")
                if self.character.getRegisterValue("type") == "TypedStockpileManager":
                    stockPileInfo["stockPileType"] = self.character.getRegisterValue("type")
                    stockPileInfo["maxAmount"] = self.character.getRegisterValue("max amount")
                    stockPileInfo["amount"] = self.character.getRegisterValue("num free slots")-stockPileInfo["maxAmount"]
                if stockPileInfo.get("source"):
                    stockPileInfo["desiredAmount"] = 0
                if stockPileInfo.get("sink"):
                    stockPileInfo["desiredAmount"] = stockPileInfo["maxAmount"]
                stockPileInfo["active"] = True
                jobOrder.popTask()
                self.character.jobOrders.pop()

            self.blocked = False
            return

        if self.submenue.selection == "reset":
            self.stockPiles = []
            self.stockPileInfo = {}
            self.blocked = False
            return
        if self.submenue.selection == "stockpile":
            options = []
            for stockpile in self.stockPiles:
                options.append((stockpile,stockpile))
            self.submenue = src.interaction.SelectionMenu("what stockpile do you want to configure?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stockPileSelection
            self.stockPile = None
            self.blocked = False
            return
        if self.submenue.selection == "addPlot":
            position = (self.xPosition,self.yPosition-1)
            items = self.container.getItemByPosition(position)
            mapFound = None
            pathingnodeFound = None
            for item in items:
                if isinstance(item,src.items.Map):
                    mapFound = item
                if isinstance(item,src.items.PathingNode):
                    pathingnodeFound = item

            if not pathingnodeFound:
                self.character.addMessage("no pathing node found")
                self.blocked=False
                return
            if not mapFound:
                self.character.addMessage("no map found")
                self.blocked=False
                return

            options = []
            for node in mapFound.getReachableNodes(pathingnodeFound.nodeName):
                if node in self.stockPiles or node in self.assignedPlots:
                    continue
                options.append((node,node))
            self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addPlot
            return
        if self.submenue.selection == "addStockpile":
            position = (self.xPosition,self.yPosition-1)
            items = self.container.getItemByPosition(position)
            mapFound = None
            pathingnodeFound = None
            for item in items:
                if isinstance(item,src.items.Map):
                    mapFound = item
                if isinstance(item,src.items.PathingNode):
                    pathingnodeFound = item

            if not pathingnodeFound:
                self.character.addMessage("no pathing node found")
                return
            if not mapFound:
                self.character.addMessage("no map found")
                return

            options = []
            for node in mapFound.getReachableNodes(pathingnodeFound.nodeName):
                options.append((node,node))
            self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addStockpile
            return
        if self.submenue.selection == "configureStockpiles":
            options = []
            for stockpile in self.stockPiles:
                options.append((stockpile,stockpile))
            self.submenue = src.interaction.SelectionMenu("what stockpile do you want to configure?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.configureStockpile
            self.stockPile = None
            return
        if self.submenue.selection == "addCommand":
            options = []
            options.append(("full","stockpiles full"))
            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def stockPileSelection(self):
        if not self.stockPile:
            self.stockPile = self.submenue.selection
            options = [
                        ("configureStockpiles","set stockpile settings"),
                        ("showInfo","set stockpile information"),
                        ("deleteStockpile","delete stockpile"),
                      ]
            self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stockPileSelection
            return

        if self.submenue.selection == "showInfo":
            self.submenue = src.interaction.TextMenu(str(self.stockPileInfo[self.stockPile]))
            self.character.macroState["submenue"] = self.submenue
        if self.submenue.selection == "deleteStockpile":
            del self.stockPileInfo[self.stockPile]
            self.stockPiles.remove(self.stockPile)
            self.character.addMessage("deleted stockpile")
        if self.submenue.selection == "configureStockpiles":
            options = []
            options.append(("desiredAmount","desired amount"))
            options.append(("itemType","item type"))
            options.append(("stockPileType","stockpile type"))
            options.append(("maxAmount","max amount"))
            options.append(("amount","amount"))
            options.append(("active","active"))
            options.append(("clear","clear"))
            options.append(("source","set as source"))
            options.append(("sink","set as sink"))
            self.submenue = src.interaction.SelectionMenu("Setting the setting to set.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.configureStockpile

            self.settingType = None
            return

    def configureStockpile(self):
        if not self.stockPile:
            self.stockPile = self.submenue.selection
            options = []
            options.append(("desiredAmount","desired amount"))
            options.append(("itemType","item type"))
            options.append(("stockPileType","stockpile type"))
            options.append(("maxAmount","max amount"))
            options.append(("amount","amount"))
            options.append(("active","active"))
            options.append(("clear","clear"))
            options.append(("source","set as source"))
            options.append(("sink","set as sink"))
            self.submenue = src.interaction.SelectionMenu("Setting the setting to set.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.configureStockpile

            self.settingType = None
            return

        if not self.settingType:
            self.settingType = self.submenue.selection

            self.submenue = src.interaction.InputMenu("input the settings value")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.configureStockpile

            return
        settingValue = self.submenue.text
        if self.settingType in ("desiredAmount","maxAmount","amount",):
            settingValue = int(settingValue)
        if self.settingType in ("active","clear","source","sink",):
            if settingValue in ("True","true"):
                settingValue = True
            else:
                settingValue = False
        self.stockPileInfo[self.stockPile][self.settingType] = settingValue
        self.blocked = False


    def addPlot(self):
        position = (self.xPosition,self.yPosition-1)
        items = self.container.getItemByPosition(position)
        mapFound = None
        pathingnodeFound = None
        for item in items:
            if isinstance(item,src.items.Map):
                mapFound = item
            if isinstance(item,src.items.PathingNode):
                pathingnodeFound = item

        if not pathingnodeFound:
            self.character.addMessage("no pathing node found")
            return
        if not mapFound:
            self.character.addMessage("no map found")
            return

        self.assignedPlots.append(self.submenue.selection)
        self.assignedPlotsInfo[self.submenue.selection] = {}
        self.assignedPlotsInfo[self.submenue.selection]["pathTo"] = mapFound.routes[pathingnodeFound.nodeName][self.submenue.selection]
        self.assignedPlotsInfo[self.submenue.selection]["pathFrom"] = mapFound.routes[self.submenue.selection][pathingnodeFound.nodeName]
        self.assignedPlotsInfo[self.submenue.selection]["maxAmount"] = 23*4
        self.assignedPlotsInfo[self.submenue.selection]["amount"] = 0
        self.blocked = False

    def addStockpile(self):
        position = (self.xPosition,self.yPosition-1)
        items = self.container.getItemByPosition(position)
        mapFound = None
        pathingnodeFound = None
        for item in items:
            if isinstance(item,src.items.Map):
                mapFound = item
            if isinstance(item,src.items.PathingNode):
                pathingnodeFound = item

        if not pathingnodeFound:
            self.character.addMessage("no pathing node found")
            return
        if not mapFound:
            self.character.addMessage("no map found")
            return

        self.stockPiles.append(self.submenue.selection)
        self.stockPileInfo[self.submenue.selection] = {}
        self.stockPileInfo[self.submenue.selection]["pathTo"] = mapFound.routes[pathingnodeFound.nodeName][self.submenue.selection]
        self.stockPileInfo[self.submenue.selection]["pathFrom"] = mapFound.routes[self.submenue.selection][pathingnodeFound.nodeName]
        self.stockPileInfo[self.submenue.selection]["active"] = False
        self.blocked = False

    def setCommand(self):
        itemType = self.submenue.selection
        
        commandItem = None
        for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1)):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage("added command for %s - %s"%(itemType,commandItem.command))
        self.blocked = False
        return

    def runCommand(self,trigger):
        if not trigger in self.commands:
            return

        command = self.commands[trigger]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]

    def getState(self):
        state = super().getState()
        state["commands"] = self.commands
        jobOrderStates = []
        for item in self.jobOrders:
            jobOrderStates.append(item.getState())
        state["jobOrders"] = jobOrderStates
        return state

    def setState(self,state):
        super().setState(state)
        if "commands" in state:
            self.commands = state["commands"]

        if "jobOrders" in state:
            for jobOrderState in state["jobOrders"]:
                self.jobOrders.append(getItemFromState(jobOrderState))

    def getLongInfo(self):
        stockPileInfo = ""
        for (stockpile,info) in self.stockPileInfo.items():
            stockPileInfo += "\n  %s: "%(stockpile,)
            for (key,value) in info.items():
                if key in ("pathTo","pathFrom"):
                    continue
                stockPileInfo += "  %s: %s "%(key,value)
        text = """
item: StockpileMetaManager

tasks:
%s

stockpiles:
%s

stockPileInfo:
%s

assignedPlots:
%s

assignedPlotsInfo:
%s

lastAction:
%s

commands:
%s

roomManagerName:
%s

description:

"""%(self.tasks,self.stockPiles,stockPileInfo,self.assignedPlots,self.assignedPlotsInfo,self.lastAction,self.commands,self.roomManagerName)
        return text

src.items.addType(StockpileMetaManager)
