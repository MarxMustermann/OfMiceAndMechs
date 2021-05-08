import src
import random

class CityBuilder(src.items.ItemNew):
    type = "CityBuilder"
    def __init__(self,xPosition=0,yPosition=0,name="CityBuilder",creator=None,noId=False):
        super().__init__("CB",xPosition,yPosition,name=name,creator=creator)
        self.commands = {}
        self.tasks = [{"task":"build factory"}]
        self.tasks = []
        self.internalRooms = []
        self.scrapFields = []
        self.reservedPlots = []
        self.usedPlots = []
        self.stockPiles = []
        self.roadTiles = []
        self.unusedRoadTiles = []
        self.unusedTiles = []
        self.unfinishedRoadTiles = []
        self.plotPool = []
        self.stuck = False
        self.stuckReason = None
        self.runningTasks = []

        #config options
        self.numReservedPathPlots = 5
        self.numBufferPlots = 3
        self.pathsOnAxis = False
        self.idleExtend = False
        self.hasMaintenance = True
        self.runsJobOrders = True

        self.error = {}

        self.attributesToStore.extend([
           "tasks","runningTasks","error","commands","error","scrapFields",
           ])

        self.tupleListsToStore.extend([
           "unfinishedRoadTiles","usedPlots","plotPool","reseredPlots","roadTiles","unusedRoadTiles",
           ])

    def addTasksToLocalRoom(self,tasks,character):
        jobOrder = src.items.itemMap["JobOrder"]()
        jobOrder.tasks = list(reversed([
            {
                "task":"go to room manager",
                "command":self.commands["go to room manager"]
            },
            {
                "task":"insert job order",
                "command":"scj",
            },
            {
                "task":"add Tasks",
                "command":None,
                "tasks": list(reversed(tasks)),
            },
            {
                "task":"return from room manager",
                "command":self.commands["return from room manager"]
            },
            ]))
        jobOrder.taskName = "install city builder"

        character.addMessage("running job order to add local room task")
        character.jobOrders.append(jobOrder)
        character.runCommandString("Jj.j")

    def apply(self,character):
        options = [("showMap","show map"),
                   ("addTaskExpand","add task expand"),
                   ("reservePlot","reserve plot"),
                   ("addTaskExpandStorage","add task expand storage"),
                   ("addTaskExpandStorageSpecific","add task expand storage specific"),
                   ("addRoom","add room"),
                   ("addBuildMine","add build mine"),
                   ("addBuildFactory","add build factory"),
                   ("clearTasks","clear tasks"),
                   ("clearError","clear error")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        selection = self.submenue.selection
        if selection == "showMap":
            self.showMap(self.character)
        elif selection == "addBuildMine":
            newTask = {"task":"build mine"}
            self.tasks.append(newTask)
        elif selection == "addBuildFactory":
            newTask = {"task":"build factory"}
            self.tasks.append(newTask)
        elif selection == "addRoom":
            options = []
            for plot in self.plotPool:
                options.append((plot,"%s"%(plot,)))
            self.submenue = src.interaction.SelectionMenu("Where do you want to build the room?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.triggerAddRoom
        elif selection == "reservePlot":
            options = []
            for plot in self.plotPool:
                options.append((plot,"%s"%(plot,)))
            self.submenue = src.interaction.SelectionMenu("Where do you want to expand from?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.reservePlot
        elif selection == "addTaskExpand":
            options = [("random","random")]
            for plot in self.plotPool:
                options.append((plot,"%s"%(plot,)))
            self.submenue = src.interaction.SelectionMenu("Where do you want to expand from?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.triggerExpand
        elif selection == "addTaskExpandStorageSpecific":
            options = []
            if not self.unusedRoadTiles:
                self.character.addMessage("no unused road tiles")
                return
            for plot in self.unusedRoadTiles:
                options.append((plot,"%s"%(plot,)))
            self.submenue = src.interaction.SelectionMenu("Where do you want to expand from?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.triggerExpandStorage
            self.storageCoordinate = None
        elif selection == "addTaskExpandStorage":
            newTask = {"task":"extend storage"}
            self.tasks.append(newTask)
        elif selection == "clearTasks":
            self.tasks = []
            self.runningTasks = []
        elif selection == "clearError":
            self.error = {}
        else:
            self.character.addMessage("unknown selection")

    def triggerExpandStorage(self):
        if not self.storageCoordinate:
            self.storageCoordinate = self.submenue.selection

            options = [("UniformStockpileManager","UniformStockpileManager"),("TypedStockpileManager","TypedStockpileManager"),]
            self.submenue = src.interaction.SelectionMenu("What type of stockpile should be placed?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.triggerExpandStorage
            self.stockPileType = None
            return

        if not self.stockPileType:
            self.stockPileType = self.submenue.selection

            options = [("storage","storage"),("source","source"),("sink","sink")]
            self.submenue = src.interaction.SelectionMenu("what function should the stockpile have?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.triggerExpandStorage
            self.stockPileFunction = None
            return

        if not self.stockPileFunction:
            self.stockPileFunction = self.submenue.selection

            if self.stockPileType == "UniformStockpileManager":
                self.submenue = src.interaction.InputMenu("type ItemType")
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.triggerExpandStorage
                self.stockPileItemType = None
                return

        if self.stockPileType == "UniformStockpileManager":
            if not self.stockPileItemType: 
                self.stockPileItemType = self.submenue.text

        newTask = {"task":"extend storage","coordinate":self.storageCoordinate,"stockPileType":self.stockPileType,"stockPileFunction":self.stockPileFunction}
        if self.stockPileType == "UniformStockpileManager":
            newTask["itemType"] = self.stockPileItemType
        self.tasks.append(newTask)

    def triggerAddRoom(self):
        plot = self.submenue.selection
        if not plot:
            self.character.addMessage("no selection")
            return

        if not plot in self.plotPool:
            self.character.addMessage("not in plot pool")
            return

        newTask = {"task":"build room","plot":list(plot)}
        self.tasks.append(newTask)

    def reservePlot(self):
        plot = self.submenue.selection
        if not plot:
            self.character.addMessage("no selection")
            return

        if not plot in self.plotPool:
            self.character.addMessage("not in plot pool")
            return

        self.plotPool.remove(plot)
        self.reservedPlots.append(plot)

 
    def triggerExpand(self):
        newTask = {"task":"expand"}
        if self.submenue.selection and not self.submenue.selection == "random":
            newTask["from"] = self.submenue.selection
        self.character.addMessage(newTask)
        self.tasks.append(newTask)

    def doRegisterResult(self,task,context):
        character = context["character"]

        error = context["jobOrder"].error
        if error:
            context["character"].addMessage("got error")
            if context["jobOrder"].error["type"] == "item not found":
                task = self.runningTasks.pop()
                self.tasks.append(task)
                self.addTasksToLocalRoom([
                    {"task":"add item","type":error["itemType"]},
                    ],context["character"])
                context["character"].addMessage("handled error")
            else:
                self.registerError(error)
        else:
            character.addMessage("success")
            task = self.runningTasks[-1]
            if task["task"] == "build roads":
                character.addMessage("handle success")
                plot = context["jobOrder"].information["plot"]
                self.unfinishedRoadTiles.remove(plot)
                if not (plot[0] == self.room.xPosition and plot[1] == self.room.yPosition):
                    self.roadTiles.append(plot)
                    self.unusedRoadTiles.append(plot)
        
        self.runningTasks = []

    def registerError(self,error):
        task = self.runningTasks.pop()
        self.tasks.append(task)
        self.error = error
    
    def doIdleExtend(self,character):
        character
        if self.idleExtend:
            if len(self.plotPool) < self.numReservedPathPlots + self.numBufferPlots:
                self.tasks.append({"task":"expand"})
                character.addMessage("idle extend")
                return
        character.addMessage("no tasks left")

    def getTaskResolvers(self):
        taskDict = {}
        self.addTriggerToTriggerMap(taskDict,"expand",self.doExpand)
        self.addTriggerToTriggerMap(taskDict,"build roads",self.doBuildRoads)
        self.addTriggerToTriggerMap(taskDict,"set up basic production",self.doSetUpBasicProduction)
        self.addTriggerToTriggerMap(taskDict,"prepare scrap field",self.doPrepareScrapField) # should be somewhere else?
        self.addTriggerToTriggerMap(taskDict,"extend storage",self.doExtendStorage)
        self.addTriggerToTriggerMap(taskDict,"set up internal storage",self.doSetUpInternalStorage)
        self.addTriggerToTriggerMap(taskDict,"build room",self.doSetUpRoom)
        self.addTriggerToTriggerMap(taskDict,"build mine",self.doSetUpMine)
        self.addTriggerToTriggerMap(taskDict,"build factory",self.doSetUpFactory)
        return taskDict

    def doSetUpRoom(self,context):
        character = context["character"]
        task = context["task"]
        plot = task["plot"]

        self.useJoborderRelayToLocalRoom(character,[
            {"task":"set up","type":"room","coordinate":plot,"command":None},
            ],"ArchitectArtwork",information={"plot":plot})
        self.plotPool.remove(tuple(plot))
        self.usedPlots.append(tuple(plot))

    def doSetUpInternalStorage(self,context):
        self.tasks.append({"task":"extend storage"})

    def doExtendStorage(self,context):
        character = context["character"]
        task = context["task"]

        if not "stockPileCoordinate" in task:
            if not self.unusedRoadTiles:
                self.tasks.append(task)
                newTask = {"task":"build roads"}
                self.tasks.append(newTask)
                newTask = {"task":"expand"}
                self.tasks.append(newTask)
                self.runningTasks = []
                return

            if not task.get("coordinate"):
                task["stockPileCoordinate"] = self.unusedRoadTiles.pop()
            else:
                task["stockPileCoordinate"] = task["coordinate"]
                self.unusedRoadTiles.remove(task["coordinate"])
            self.usedPlots.append(task["stockPileCoordinate"])
            self.stockPiles.append(task["stockPileCoordinate"])
            self.tasks.append(task)
            self.runningTasks = []
            return

        task["stockPileName"] = "storage_%s_%s"%(task["stockPileCoordinate"][0],task["stockPileCoordinate"][1])

        setupTask = {"task":"set up","type":"stockPile","name":task["stockPileName"],"coordinate":task["stockPileCoordinate"],"command":None,}
        if task.get("stockPileType"):
            setupTask["StockpileType"] = task["stockPileType"]
            if task["stockPileType"] == "UniformStockpileManager":
                setupTask["ItemType"] = task["itemType"]

        tasks = [
                setupTask,
            ]

        stockPileFunction = task.get("stockPileFunction")
        newTask = {"task":"connect stockpile","type":"add to storage","stockPile":task["stockPileName"],"stockPileCoordinate":task["stockPileCoordinate"],"command":None,}
        if stockPileFunction:
            newTask["function"] = stockPileFunction

        tasks.append(newTask)
        self.useJoborderRelayToLocalRoom(character,tasks,"ArchitectArtwork")

    def doPrepareScrapField(self,context):
        character = context["character"]
        self.useJoborderRelayToLocalRoom(character,[
            {"task":"clear paths","coordinate":task["coordinate"],"command":None},
            ],"RoadManager")

    def doSetUpBasicProduction(self,character):
        self.addTasksToLocalRoom([
            {"task":"add machine","type":"FloorPlate"},
            {"task":"add machine","type":"ScrapCompactor"},
            {"task":"add item","type":"ProductionManager"},
            ])

    def doBuildRoads(self,context):
        character = context["character"]
        if self.unfinishedRoadTiles:
            plot = self.unfinishedRoadTiles[-1]
            self.useJoborderRelayToLocalRoom(character,[
                {"task":"set up","type":"road","coordinate":plot,"command":None},
                ],"ArchitectArtwork",information={"plot":plot})
        else:
            character.addMessage("no road tile found to build")
            self.runningTasks = []

    def doExpand(self,context):
        if not self.plotPool:
            return
        
        task = context["task"]

        if not "from" in task:
            plot = random.choice(self.plotPool)
        else:
            plot = task["from"]

        if not plot in self.plotPool:
            return

        self.expandFromPlot(plot)
        newTask = {"task":"build roads"}
        self.tasks.append(newTask)
        self.runningTasks = []
        return

    def doMaintenance(self,character):
        if not "go to room manager" in self.commands and "return from room manager" in self.commands:
            character.addMessage("no room manager")
            return

        if self.error:
            character.addMessage("Error while running task")
            return

        if self.runningTasks:
            character.addMessage("item blocked tasks running")
            return

        if not self.tasks:
            self.doIdleExtend(character)
            return

        if not self.usedPlots:
            plot = (self.container.xPosition,self.container.yPosition)
            self.plotPool.append(plot)

            self.expandFromPlot(plot)

        task = self.tasks.pop()
        self.runningTasks.append(task)

        resolverMap = self.getTaskResolvers()
        if task["task"] in resolverMap:
            for taskResolver in resolverMap[task["task"]]:
                taskResolver({"character":character,"task":task})
                
    def doSetUpFactory(self,context):
        character = context["character"]
        task = context["task"]

        if not task.get("basePlot"):
            random.shuffle(self.plotPool)
            plot = self.plotPool.pop()

        self.useJoborderRelayToLocalRoom(character,[
            #{"task":"set up","type":"stockPile","name":task["metalBarStorageName"],"coordinate":task["metalBarStorageCoordinate"],"command":None,"StockpileType":"UniformStockpileManager","ItemType":"MetalBars"},
            #{"task":"set up","type":"stockPile","name":task["stockPileName"],"coordinate":task["stockPileCoordinate"],"command":None,"StockpileType":"UniformStockpileManager","ItemType":"Scrap"},
            {"task":"set up","type":"factory","coordinate":plot},
            ],"ArchitectArtwork")

    def doSetUpMine(self,context):
        character = context["character"]
        task = context["task"]

        if not self.scrapFields:
            self.tasks.append(task)
            newTask = {"task":"expand"}
            self.tasks.append(newTask)
            self.runningTasks = []
            return
        if not task.get("scrapField"):
            task["scrapField"] = random.choice(self.scrapFields)

        if not task.get("expanded storage"):
            self.tasks.append(task)
            newTask = {"task":"extend storage"}
            self.tasks.append(newTask)
            self.runningTasks = []
            task["expanded storage"] = True
            return

        if not task.get("stockPileCoordinate"):
            self.runningTasks = []
            directions = [(0,1),(0,-1),(1,0),(-1,0)]
            random.shuffle(directions)
            neighbourRoad = None
            neighbourPlot = None
            neighbourUndiscovered = None
            for direction in directions:
                position = (task["scrapField"][0][0]+direction[0],task["scrapField"][0][1]+direction[1],)
                if position in self.unusedRoadTiles:
                    neighbourRoad = position
                    continue
                if position in self.plotPool:
                    neighbourPlot = position
                    continue
                if not position in self.usedPlots and not position in self.stockPiles:
                    neighbourUndiscovered = position
                    continue

            if neighbourRoad:
                self.tasks.append(task)
                task["stockPileCoordinate"] = neighbourRoad
                self.unusedRoadTiles.remove(neighbourRoad)
                character.addMessage("expand done")
                task["undiscoveredCounter"] = 0
                task["scrapRetryCounter"] = 0
                return
            elif neighbourPlot:
                self.tasks.append(task)
                newTask = {"task":"expand","from":neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand plot")
                return
            elif neighbourUndiscovered:
                if not "undiscoveredCounter" in task:
                    task["undiscoveredCounter"] = 0
                task["undiscoveredCounter"] += 1
                if task["undiscoveredCounter"] > 5:
                    if not "scrapRetryCounter" in task:
                        task["scrapRetryCounter"] = 0

                    if task["scrapRetryCounter"] > 5:
                        return

                    self.tasks.append(task)
                    del task["scrapField"]
                    task["undiscoveredCounter"] = 0
                    return

                self.tasks.append(task)
                newTask = {"task":"expand","target":neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand undiscovered")
                return
            else:
                character.addMessage("no way to place")
                return

        if not task.get("oreProcessingCoordinate"):
            self.runningTasks = []
            directions = [(0,1),(0,-1),(1,0),(-1,0)]
            random.shuffle(directions)
            neighbourRoad = None
            neighbourPlot = None
            neighbourUndiscovered = None
            for direction in directions:
                position = (task["stockPileCoordinate"][0]+direction[0],task["stockPileCoordinate"][1]+direction[1],)
                if position in self.unusedRoadTiles:
                    neighbourRoad = position
                    continue
                if position in self.plotPool:
                    neighbourPlot = position
                    continue
                if not position in self.usedPlots and not position in self.stockPiles:
                    neighbourUndiscovered = position
                    continue

            if neighbourRoad:
                self.tasks.append(task)
                task["oreProcessingCoordinate"] = neighbourRoad
                self.unusedRoadTiles.remove(neighbourRoad)
                character.addMessage("expand done")
                return
            elif neighbourPlot:
                self.tasks.append(task)
                newTask = {"task":"expand","from":neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand plot")
                return
            elif neighbourUndiscovered:
                if not "undiscoveredCounter" in task:
                    task["undiscoveredCounter"] = 0
                task["undiscoveredCounter"] += 1
                if task["undiscoveredCounter"] > 5:
                    if not "scrapRetryCounter" in task:
                        task["scrapRetryCounter"] = 0

                    if task["scrapRetryCounter"] > 5:
                        return

                    self.tasks.append(task)
                    del task["scrapField"]
                    task["undiscoveredCounter"] = 0
                    return

                self.tasks.append(task)
                newTask = {"task":"expand","target":neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand undiscovered")
                return
            else:
                character.addMessage("no way to place")
                return

        if not task.get("metalBarStorageCoordinate"):
            self.runningTasks = []
            directions = [(0,1),(0,-1),(1,0),(-1,0)]
            random.shuffle(directions)
            neighbourRoad = None
            neighbourPlot = None
            neighbourUndiscovered = None
            for direction in directions:
                position = (task["oreProcessingCoordinate"][0]+direction[0],task["oreProcessingCoordinate"][1]+direction[1],)
                if position in self.unusedRoadTiles:
                    neighbourRoad = position
                    continue
                if position in self.plotPool:
                    neighbourPlot = position
                    continue
                if not position in self.usedPlots and not position in self.stockPiles:
                    neighbourUndiscovered = position
                    continue

            if neighbourRoad:
                self.tasks.append(task)
                task["metalBarStorageCoordinate"] = neighbourRoad
                task["metalBarStorageName"] = "bardropoff %s"%(task["metalBarStorageCoordinate"],)
                self.unusedRoadTiles.remove(neighbourRoad)
                character.addMessage("expand done")
                return
            elif neighbourPlot:
                self.tasks.append(task)
                newTask = {"task":"expand","from":neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand plot")
                return
            elif neighbourUndiscovered:
                if not "undiscoveredCounter" in task:
                    task["undiscoveredCounter"] = 0
                task["undiscoveredCounter"] += 1
                if task["undiscoveredCounter"] > 5:
                    if not "scrapRetryCounter" in task:
                        task["scrapRetryCounter"] = 0

                    if task["scrapRetryCounter"] > 5:
                        return

                    self.tasks.append(task)
                    del task["scrapField"]
                    task["undiscoveredCounter"] = 0
                    return

                self.tasks.append(task)
                newTask = {"task":"expand","target":neighbourPlot}
                self.tasks.append(newTask)
                character.addMessage("expand undiscovered")
                return
            else:
                character.addMessage("no way to place")
                return

        if not task.get("didBasicSetup"):
            task["stockPileName"] = "miningStockPile_%s_%s"%(task["stockPileCoordinate"][0],task["stockPileCoordinate"][1])
            self.useJoborderRelayToLocalRoom(character,[
                {"task":"set up","type":"stockPile","name":task["metalBarStorageName"],"coordinate":task["metalBarStorageCoordinate"],"command":None,"StockpileType":"UniformStockpileManager","ItemType":"MetalBars"},
                {"task":"connect stockpile","type":"add to storage","function":"source","stockPileCoordinate":task["metalBarStorageCoordinate"],"stockPile":task["metalBarStorageName"]},
                {"task":"set up","type":"oreProcessing","coordinate":task["oreProcessingCoordinate"],"command":None},
                {"task":"set up","type":"stockPile","name":task["stockPileName"],"coordinate":task["stockPileCoordinate"],"command":None,"StockpileType":"UniformStockpileManager","ItemType":"Scrap"},
                {"task":"set up","type":"mine","stockPile":task["stockPileName"],"stocKPileCoordinate":task["stockPileCoordinate"],"scrapField":task["scrapField"],"command":None},
                ],"ArchitectArtwork")
            task["didBasicSetup"] = True
            self.tasks.append(task)
            return

        if not task.get("didExtendStorage"):
            newTask = {"task":"extend storage"}
            self.tasks.append(task)
            self.tasks.append(newTask)
            self.runningTasks = []
            task["didExtendStorage"] = True
            return

        self.useJoborderRelayToLocalRoom(character,[
            {"task":"set up","setupInfo":{
                "miningSpot":task["scrapField"],
                "scrapStockPileName":task["stockPileName"],"scrapStockPileCoordinate":task["stockPileCoordinate"],
                "metalBarStockPileName":task["metalBarStorageName"],"metalBarStockPileCoordinate":task["metalBarStorageCoordinate"],
                "oreProcessing":task["oreProcessingCoordinate"]}}
            ],"MiningManager")

    def expandFromPlot(self,plot):
        self.usedPlots.append(plot)
        self.plotPool.remove(plot)

        plotCandiates = [
                        (plot[0]-1,plot[1]),
                        (plot[0]+1,plot[1]),
                        (plot[0],plot[1]-1),
                        (plot[0],plot[1]+1),
                       ]

        self.getTerrain().addItem(src.items.MarkerBean(plot[0]*15+7,plot[1]*15+7))
        self.unfinishedRoadTiles.append(plot)

        axisPlots = []
        for candidate in plotCandiates:
            if not candidate in self.usedPlots and not candidate in self.plotPool:
                if candidate[0] in (0,14) or candidate[1] in (0,14):
                    continue

                numScrap = 0
                for x in range(candidate[0]*15+1,candidate[0]*15+14):
                    for y in range(candidate[1]*15+1,candidate[1]*15+14):
                        for item in self.getTerrain().getItemByPosition((x,y,0)):
                            if item.type == "Scrap":
                                numScrap += item.amount

                if numScrap > 100:
                    self.scrapFields.append([list(candidate),numScrap])
                    self.usedPlots.append(candidate)
                    continue

                self.plotPool.append(candidate)
                if self.pathsOnAxis and 7 in (candidate):
                    axisPlots.append(candidate)

        if self.pathsOnAxis:
            for plot in axisPlots:
                if plot in self.plotPool:
                    self.expandFromPlot(plot)

    def showMap(self,character):
        mapContent = []
        for x in range(0,15):
            mapContent.append([])
            for y in range(0,15):
                if not x in (0,14) and not y in (0,14):
                    char = "  "
                elif not x == 7 and not y == 7:
                    char = "##"
                else:
                    char = "  "
                mapContent[x].append(char)

        for plot in self.plotPool:
            mapContent[plot[1]][plot[0]] = "__"
        for plot in self.usedPlots:
            mapContent[plot[1]][plot[0]] = "xx"
        for plot in self.stockPiles:
            mapContent[plot[1]][plot[0]] = "pp"
        for plot in self.scrapFields:
            mapContent[plot[0][1]][plot[0][0]] = "*#"
        for plot in self.unfinishedRoadTiles:
            mapContent[plot[1]][plot[0]] = ".."
        for plot in self.roadTiles:
            mapContent[plot[1]][plot[0]] = "::"
        mapContent[self.room.yPosition][self.room.xPosition] = "CB"

        mapText = ""
        for x in range(0,15):
           mapText += "".join(mapContent[x])+"\n"
        self.submenue = src.interaction.TextMenu(text=mapText)
        character.macroState["submenue"] = self.submenue


    def getConfigurationOptions(self,character):
        options = super().getConfigurationOptions(character)
        options["x"] = ("show map",self.showMap)
        options["e"] = ("retry task",self.retryTask)
        return options

    def retryTask(self,character):
        self.error = {}
        if self.runningTasks:
            self.tasks.extend(self.runningTasks)
            self.runningTasks = []

    def getLongInfo(self):
        text = """
commands:
%s

error:
%s

runningTasks:
%s

tasks:
%s

reservedPlots:
%s

usedPlots:
%s

roadTiles:
%s

unfinishedRoadTiles:
%s

plotPool:
%s

unusedRoadTiles:
%s

scrapFields:
%s
"""%(self.commands,self.error,self.runningTasks,self.tasks,self.reservedPlots,self.usedPlots,self.roadTiles,self.unfinishedRoadTiles,self.plotPool,self.unusedRoadTiles,self.scrapFields)
        return text
