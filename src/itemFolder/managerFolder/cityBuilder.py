import src
import random

class CityBuilder(src.items.ItemNew):
    type = "CityBuilder"
    def __init__(self,xPosition=0,yPosition=0,name="CityBuilder",creator=None,noId=False):
        super().__init__("CB",xPosition,yPosition,name=name,creator=creator)
        self.commands = {}
        self.tasks = []
        self.internalRooms = []
        self.architects = []
        self.roadManagers = []
        self.scrapFields = []
        self.miningManagers = []
        self.stockPileManagers = []
        self.usedPlots = []
        self.stockPiles = []
        self.roadTiles = []
        self.unusedRoadTiles = []
        self.unusedTiles = []
        self.unfinishedRoadTiles = []
        self.plotPool = []
        self.stuck = False
        self.stuckReason = None

        #config options
        self.numReservedPathPlots = 5
        self.numBufferPlots = 3
        self.pathsOnAxis = False
        self.idleExtend = False
        self.hasStockpileMetaManager = False

        self.attributesToStore.extend([
           "tasks",
           ])


    def addTasksToLocalRoom(self,tasks):
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

        self.character.addMessage("running job order to add local room task")
        self.character.jobOrders.append(jobOrder)
        self.character.runCommandString("Jj.j")

    def apply(self,character):
        self.tasks.append({"task":"expand",})

    def doMaintenance(self,character):
        if not self.tasks:
            if self.idleExtend:
                if len(self.plotPool) < self.numReservedPathPlots + self.numBufferPlots:
                    self.tasks.append({"task":"expand"})
                    character.addMessage("idle extend")
                    return
            character.addMessage("no tasks left")
            return

        if not "go to room manager" in self.commands and "return from room manager" in self.commands:
            character.addMessage("no room manager")
            return

        if not self.usedPlots:
            plot = (self.container.xPosition,self.container.yPosition)
            self.plotPool.append(plot)

            self.expandFromPlot(plot)

        self.character = character
        task = self.tasks.pop()
        if task["task"] == "expand":
            if not self.plotPool:
                return
            plot = random.choice(self.plotPool)
            self.expandFromPlot(plot)
            newTask = {"task":"build roads"}
            self.tasks.append(newTask)
            return
        if task["task"] == "build roads":
            if self.unfinishedRoadTiles:
                plot = self.unfinishedRoadTiles.pop()
                self.useJoborderRelayToLocalRoom(character,[
                    {"task":"set up","type":"road","coordinate":plot,"command":None},
                    ],"ArchitectArtwork")
                self.roadTiles.append(plot)
                self.unusedRoadTiles.append(plot)
        if task["task"] == "set up basic production":
            self.addTasksToLocalRoom([
                {"task":"add machine","type":"FloorPlate"},
                {"task":"add machine","type":"ScrapCompactor"},
                {"task":"add item","type":"ProductionManager"},
                ])
        if task["task"] == "add architect":
            self.addTasksToLocalRoom([
                {"task":"add item","type":"ArchitectArtwork"},
                ])
            self.architects.append("")
            return
        if task["task"] == "add mining manager":
            self.addTasksToLocalRoom([
                {"task":"add item","type":"MiningManager"},
                ])
            self.miningManagers.append("")
            return
        if task["task"] == "add road manager":
            self.addTasksToLocalRoom([
                {"task":"add item","type":"RoadManager"},
                ])
            self.roadManagers.append("")
            return
        if task["task"] == "prepare scrap field":
            self.useJoborderRelayToLocalRoom(character,[
                {"task":"clear paths","coordinate":task["coordinate"],"command":None},
                ],"RoadManager")
            return

        if task["task"] == "extend storage":

            if not self.architects:
                if not self.roadManagers:
                    self.tasks.append(task)
                    newTask = {"task":"add road manager"}
                    self.tasks.append(newTask)
                    return
                self.tasks.append(task)
                newTask = {"task":"add architect"}
                self.tasks.append(newTask)
                return

            if not "stockPileCoordinate" in task:
                if not self.unusedRoadTiles:
                    self.tasks.append(task)
                    newTask = {"task":"expand"}
                    self.tasks.append(newTask)
                    return
                task["stockPileCoordinate"] = self.unusedRoadTiles.pop()
                self.usedPlots.append(task["stockPileCoordinate"])
                self.stockPiles.append(task["stockPileCoordinate"])
                self.tasks.append(task)
                return

            task["stockPileName"] = "storage_%s_%s"%(task["stockPileCoordinate"][0],task["stockPileCoordinate"][1])
            self.useJoborderRelayToLocalRoom(character,[
                {"task":"set up","type":"stockPile","name":task["stockPileName"],"coordinate":task["stockPileCoordinate"],"command":None},
                {"task":"connect stockpile","type":"add to storage","stockPile":task["stockPileName"],"stockPileCoordinate":task["stockPileCoordinate"],"command":None},
                ],"ArchitectArtwork")

        if task["task"] == "set up internal storage":
            if not self.hasStockpileMetaManager:
                self.addTasksToLocalRoom([
                    {"task":"add item","type":"StockpileMetaManager"},
                    ])
                self.hasStockpileMetaManager = True
                self.tasks.append({"task":"extend storage"})
        if task["task"] == "build mine":
            if not self.architects:
                if not self.roadManagers:
                    self.tasks.append(task)
                    newTask = {"task":"add road manager"}
                    self.tasks.append(newTask)
                    return
                self.tasks.append(task)
                newTask = {"task":"add architect"}
                self.tasks.append(newTask)
                return

            if not self.hasStockpileMetaManager:
                self.tasks.append(task)
                newTask = {"task":"set up internal storage"}
                self.tasks.append(newTask)
                return

            if not self.scrapFields:
                self.tasks.append(task)
                newTask = {"task":"expand"}
                self.tasks.append(newTask)
                return
            if not task.get("scrapField"):
                task["scrapField"] = random.choice(self.scrapFields)

            if not self.miningManagers:
                self.tasks.append(task)
                newTask = {"task":"add mining manager"}
                self.tasks.append(newTask)
                return

            if not task.get("stockPileCoordinate"):
                directions = [(0,1),(0,-1),(1,0),(-1,0)]
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
                    self.character.addMessage("expand done")
                    task["undiscoveredCounter"] = 0
                    task["scrapRetryCounter"] = 0
                    return
                elif neighbourPlot:
                    self.tasks.append(task)
                    newTask = {"task":"expand","target":neighbourPlot}
                    self.tasks.append(newTask)
                    self.character.addMessage("expand plot")
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
                    self.character.addMessage("expand undiscovered")
                    return
                else:
                    self.character.addMessage("no way to place")
                    return

            if not task.get("oreProcessingCoordinate"):
                directions = [(0,1),(0,-1),(1,0),(-1,0)]
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
                    self.character.addMessage("expand done")
                    return
                elif neighbourPlot:
                    self.tasks.append(task)
                    newTask = {"task":"expand","target":neighbourPlot}
                    self.tasks.append(newTask)
                    self.character.addMessage("expand plot")
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
                    self.character.addMessage("expand undiscovered")
                    return
                else:
                    self.character.addMessage("no way to place")
                    return


            task["stockPileName"] = "miningStockPile_%s_%s"%(task["stockPileCoordinate"][0],task["stockPileCoordinate"][1])
            self.useJoborderRelayToLocalRoom(character,[
                {"task":"set up","type":"oreProcessing","coordinate":task["oreProcessingCoordinate"],"command":None},
                {"task":"set up","type":"stockPile","name":task["stockPileName"],"coordinate":task["stockPileCoordinate"],"command":None,"StockpileType":"UniformStockpileManager"},
                {"task":"connect stockpile","type":"set wrong item to storage","stockPile":task["stockPileName"],"stockPileCoordinate":task["stockPileCoordinate"],"command":None},
                {"task":"set up","type":"mine","stockPile":task["stockPileName"],"stocKPileCoordinate":task["stockPileCoordinate"],"scrapField":task["scrapField"],"command":None},
                ],"ArchitectArtwork")

    def configure(self,character):

        self.lastAction = "configure"

        self.submenue = src.interaction.OneKeystrokeMenu("""
c: addCommand
s: machine settings
j: run job order
r: reset
x: show map
m: do maintenance
""")
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

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
                    self.scrapFields.append((candidate,numScrap))
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

    def configure2(self):
        self.lastAction = "configure2"

        if self.submenue.keyPressed == "m":
            self.doMaintenance(self.character)
        elif self.submenue.keyPressed == "x":
            self.showMap(self.character)
        elif self.submenue.keyPressed == "j":
            if not self.character.jobOrders:
                self.character.addMessage("no job order")
                self.blocked = False
                return
            jobOrder = self.character.jobOrders[-1]
            task = jobOrder.popTask()
            if not task:
                self.character.addMessage("no tasks left")
                return

            if task["task"] == "configure machine":
                for (commandName,command) in task["commands"].items():
                    self.commands[commandName] = command

            if task["task"] == "add task":
                self.tasks.extend(task["tasks"])

            self.blocked = False
            return

    def getLongInfo(self):
        text = """
commands:
%s

tasks:
%s

usedPlots:
%s

roadTiles:
%s

unfinishedRoadTiles:
%s

plotPool:
%s

scrapFields:
%s
"""%(self.commands,self.tasks,self.usedPlots,self.roadTiles,self.unfinishedRoadTiles,self.plotPool,self.scrapFields)
        return text
