import src

'''
gomode item for terraforming and things
'''
class ArchitectArtwork(src.items.ItemNew):
    type = "ArchitectArtwork"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="scrap compactor",creator=None,noId=False):
        super().__init__("AA",xPosition,yPosition,name=name,creator=creator,runsJobOrders=True)

        self.godMode = False
        self.attributesToStore.extend([
               "godMode"])

    def getJobOrderTriggers(self):
        result = super().getJobOrderTriggers()
        self.addTriggerToTriggerMap(result,"add scrap field",self.jobOrderAddScrapField)
        self.addTriggerToTriggerMap(result,"set up",self.doSetUp)
        self.addTriggerToTriggerMap(result,"connect stockpile",self.doConnectStockpile)
        return result

    def doConnectStockpile(self,task,context):
        jobOrder = context["jobOrder"]

        if not "pathFrom" in jobOrder.information:
            tasks = [
                    {"task":"go to room manager","command":self.commands["go to room manager"]},
                    {"task":"insert job order","command":"scj"},
                    {"task":"relay job order","command":None,"ItemType":"RoadManager",},
                    {"task":"print paths","command":None,"to":task["stockPileCoordinate"]},
                    {"task":"return from room manager","command":self.commands["return from room manager"]},
                    {"task":"reactivate architect","command":"scj"},
                    task,
                    ]
            context["jobOrder"].tasks.extend(list(reversed(tasks)))
            return

        if task["type"] == "add to storage":
            self.useJoborderRelayToLocalRoom(context["character"],[
                {"task":"add stockpile","nodeName":task["stockPile"],"pathFrom":jobOrder.information["pathFrom"],"pathTo":jobOrder.information["pathTo"]},
                {"task":"do maintanence"},
                ],"StockpileMetaManager")

        if task["type"] == "set wrong item to storage":
            newJobOrder = src.items.itemMap["JobOrder"]()
            newJobOrder.taskName = "configure stockpile"

            storageCommand = jobOrder.information["pathFrom"]+"Js.sjj"+jobOrder.information["pathTo"]

            tasks = [
                    {"task":"go to room manager","command":self.commands["go to room manager"]},
                    {"task":"go to stockPile","command":jobOrder.information["pathTo"]},
                    {"task":"insert job order","command":"scj"},
                    {"task":"configure machine","command":None, "commands":{"wrong":storageCommand}},
                    {"task":"return from stockPile","command":jobOrder.information["pathFrom"]},
                    {"task":"return from room manager","command":self.commands["return from room manager"]},
                    ]
            newJobOrder.tasks = list(reversed(tasks))
            context["character"].addJobOrder(newJobOrder)


        """
        self.useJoborderRelayToLocalRoom(context["character"],[
            {"task":"add stockpile","nodeName":task["stockPile"],"pathFrom":paths[task["stockPile"]]["pathFrom"],"pathTo":paths[task["stockPile"]]["pathTo"]},
        ],"StockpileMetaManager")
        """

    def jobOrderAddScrapField(self,task,character):
        self.doAddScrapfield(task["coordinate"][0],task["coordinate"][1],task["amount"])

    def doSetUp(self,task,context):
        if task["type"] == "stockPile":
            self.useJoborderRelayToLocalRoom(context["character"],[
                {"task":"add pathing node","nodeName":task["name"],"coordinate":task["coordinate"],"command":None,"offset":[7,6]},
                ],"RoadManager")
            items = []
            if task.get("StockpileType") == "UniformStockpileManager":
                item = src.items.itemMap["UniformStockpileManager"](task["coordinate"][0]*15+7,task["coordinate"][1]*15+7)
                item.storedItemType = "Scrap"
                item.storedItemWalkable = None
                item.restrictStoredItemType = True
                item.restrictStoredItemWalkable = False
                items.append(item)
            else:
                items.append(src.items.itemMap["TypedStockpileManager"](task["coordinate"][0]*15+7,task["coordinate"][1]*15+7))
            self.getTerrain().addItems(items)

        if task["type"] == "oreProcessing":
            items = []
            positions = [(2,2),(2,4),(2,6),(5,4),(5,2),(9,4),(9,2),(12,2),(12,4),(12,6),(12,9),(12,11),(12,13),(9,11),(9,13),(5,13),(5,11),(2,9),(2,11),(2,13)]
            for position in positions:
                items.append(src.items.itemMap["ScrapCompactor"](task["coordinate"][0]*15+position[0],task["coordinate"][1]*15+position[1]))
            self.getTerrain().addItems(items)
        if task["type"] == "mine":
            """
            self.useJoborderRelayToLocalRoom(context["character"],[
                {"task":"clear paths","coordinate":task["scrapField"],},
                ],"RoadManager")
            """
            items = []
            item = src.items.itemMap["ItemCollector"](task["scrapField"][0][0]*15+7,task["scrapField"][0][1]*15+7)

            stockPileCoordinate = task["stocKPileCoordinate"]
            if stockPileCoordinate:
                clearInventoryCommand = "Js.j"*10
                if stockPileCoordinate[0] > task["scrapField"][0][0]:
                    item.commands["fullInventory"] = "12dwd"+clearInventoryCommand+"as12a"
                if stockPileCoordinate[0] < task["scrapField"][0][0]:
                    item.commands["fullInventory"] = "12awa"+clearInventoryCommand+"ds12d"
                if stockPileCoordinate[1] < task["scrapField"][0][1]:
                    item.commands["fullInventory"] = "12wawwd"+clearInventoryCommand+"assd12s"
                if stockPileCoordinate[1] > task["scrapField"][0][1]:
                    item.commands["fullInventory"] = "12s"+clearInventoryCommand+"12w"
            items.append(item)
            self.getTerrain().addItems(items)

        if task["type"] == "road":
            self.doClearField(task["coordinate"][0],task["coordinate"][1])
            self.useJoborderRelayToLocalRoom(context["character"],[
                {"task":"add road","coordinate":task["coordinate"],},
                ],"RoadManager")

    def doRegisterResult(self,task,context):
        if context["jobOrder"].error:
            if not context["jobOrder"].getTask():
                context["character"].jobOrders.pop()
                if context["character"].jobOrders:
                    jobOrder = context["character"].jobOrders[-1]
                    jobOrder.error = context["jobOrder"].error

    '''
    '''
    def apply(self,character):
        options = [("showMap","shop map of the area"),
                   ("addScrapField","add scrap field"),
                   ("addRoom","add room"),
                   ("clearField","clear coordinate"),
                   ("test","test"),
                 ]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def test(self):
        pass

    def apply2(self):
        if self.submenue.selection == "test":
            self.test()
        if self.submenue.selection == "showMap":
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

            for (coordinate,rooms,) in self.getTerrain().roomByCoordinates.items():
                if not rooms:
                    continue
                mapContent[coordinate[1]][coordinate[0]] = "RR"

            mapText = ""
            for x in range(0,15):
               mapText += "".join(mapContent[x])+"\n"
            self.submenue = src.interaction.TextMenu(text=mapText)
            self.character.macroState["submenue"] = self.submenue
        elif self.submenue.selection == "addScrapField":
            self.submenue = None
            self.addScrapField(wipe=True)
        elif self.submenue.selection == "addRoom":
            self.submenue = None
            self.addRoom(wipe=True)
        elif self.submenue.selection == "clearField":
            self.submenue = None
            self.clearField(wipe=True)

    def clearField(self,wipe=False):
        if not self.submenue:
            self.submenue = src.interaction.InputMenu("enter the coordinate ( x,y ) current: %s,%s"%(self.character.xPosition//15,self.character.yPosition//15))
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.clearField
            return

        targetX = int(self.submenue.text.split(",")[0])
        targetY = int(self.submenue.text.split(",")[1])

        self.doClearField(targetX,targetY)

    def doClearField(self,x,y):
        terrain = self.getTerrain()

        minX = 15*x
        minY = 15*y
        maxX = minX+15
        maxY = minY+15
        toRemove = []
        for x in range(minX,maxX):
            for y in range(minY,maxY):
                toRemove.extend(terrain.getItemByPosition((x,y,0)))
        terrain.removeItems(toRemove)

        if (x,y) in terrain.roomByCoordinates:
            for room in terrain.roomByCoordinates[(x,y)]:
                terrain.removeRoom(room)

    def addScrapField(self,wipe=False):
        if wipe:
            self.targetX = None
            self.targetY = None
            self.targetAmount = None

        if not self.submenue:
            self.submenue = src.interaction.InputMenu("enter the coordinate ( x,y ) current: %s,%s"%(self.character.xPosition//15,self.character.yPosition//15))
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addScrapField
            return

        if not self.targetY:
            self.targetX = int(self.submenue.text.split(",")[0])
            self.targetY = int(self.submenue.text.split(",")[1])

            self.submenue = src.interaction.InputMenu("enter the amount of scrap piles (AMOUNt)")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addScrapField
            return

        amount = int(self.submenue.text)

        if self.room:
            terrain = self.room.terrain
        if self.terrain:
            terrain = self.terrain

        if not terrain:
            self.character.addMessage("no terrain found")
            return

        self.doAddScrapfield(self.targetX,self.targetY,amount)

    def doAddScrapfield(self,x,y,amount):
        if self.room:
            terrain = self.room.terrain
        if self.terrain:
            terrain = self.terrain

        import random
        counter = 0
        minX = 15*x
        minY = 15*y
        maxX = minX+13
        maxY = minY+13
        maxItems = amount
        items = []
        while counter < maxItems:
            if not random.randint(1,30) == 10:
                item = src.items.itemMap["Scrap"](random.randint(minX,maxX),random.randint(minY,maxY),amount=random.randint(1,20))
            else:
                item = src.items.itemMap[random.choice(list(src.items.itemMap.keys()))](random.randint(minX,maxX),random.randint(minY,maxY))
                item.bolted = False
            items.append(item)
            counter += 1
        terrain.addItems(items)

    def addRoom(self,wipe=False):
        if wipe:
            self.targetX = None
            self.targetY = None
            self.targetOffsetX = None
            self.targetOffsetY = None
            self.targetRoomType = None

        if not self.submenue:
            self.submenue = src.interaction.InputMenu("enter the coordinate ( x,y ) current: %s,%s"%(self.character.xPosition//15,self.character.yPosition//15))
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addRoom
            return

        if not self.targetY:
            self.targetX = int(self.submenue.text.split(",")[0])
            self.targetY = int(self.submenue.text.split(",")[1])

            self.submenue = src.interaction.InputMenu("enter the offset ( x,y )")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addRoom
            return

        if not self.targetOffsetY:
            self.targetOffsetX = int(self.submenue.text.split(",")[0])
            self.targetOffsetY = int(self.submenue.text.split(",")[1])

            options = []
            for key,value in src.rooms.roomMap.items():
                options.append((key,key))
            self.submenue = src.interaction.SelectionMenu("select the room to produce",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addRoom
            return

        if not self.targetRoomType:
            self.targetRoomType = self.submenue.selection
            if self.targetRoomType == "EmptyRoom":
                self.emptyRoomSizeX = None
                self.emptyRoomSizeY = None
                self.entryPointX = None
                self.entryPointY = None

                self.submenue = src.interaction.InputMenu("enter the rooms size ( x,y )")
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.addRoom
                return

        if self.targetRoomType == "EmptyRoom":

            if not self.emptyRoomSizeY:
                self.emptyRoomSizeX = int(self.submenue.text.split(",")[0])
                self.emptyRoomSizeY = int(self.submenue.text.split(",")[1])

                self.submenue = src.interaction.InputMenu("enter the doors positions ( x,y x,y x,y )")
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.addRoom
                return

        if self.room:
            terrain = self.room.terrain
        if self.terrain:
            terrain = self.terrain

        if not terrain:
            self.character.addMessage("no terrain found")
            return

        room = src.rooms.roomMap[self.targetRoomType](self.targetX,self.targetY,self.targetOffsetX,self.targetOffsetY)
        if self.targetRoomType == "EmptyRoom":
            entryPoints = []
            for part in self.submenue.text.split(" "): 
                entryPointX = int(part.split(",")[0])
                entryPointY = int(part.split(",")[1])
                entryPoint = (entryPointX,entryPointY,)

                entryPoints.append(entryPoint)

            self.character.addMessage(entryPoints)

            room.reconfigure(self.emptyRoomSizeX,self.emptyRoomSizeY,doorPos=entryPoints)
        terrain.addRooms([room])
