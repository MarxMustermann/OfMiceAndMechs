import src

class StockPlaner(src.items.Item):
    """
    """


    type = "StockPlaner"

    def __init__(self, name="StockPlaner", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="CP", name=name)

        self.applyOptions.extend(
                        [
                                                                ("showMap", "show map"),
                        ]
                        )
        self.applyMap = {
                    "showMap": self.showMap,
                        }
        self.plannedRooms = []
        self.specialPurposeRooms = []
        self.generalPurposeRooms = []
        
    def addScrapCompactorFromMap(self,params,instaSpawn=False):
        """
        handle a character having selected building a room
        and adding a task to the items task list

        Parameters:
            params: parameters given from the interaction menu
        """

        character = params["character"]

        if not "type" in params:
            params["type"] = "random"
            options = []
            index = 0
            for item in self.prefabs["ScrapToMetalBars"]:
                index += 1
                options.append((index,f"prefab{index}"))
            submenue = src.interaction.SelectionMenu("what floorplan to use?",options,targetParamName="type")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"addScrapCompactorFromMap","params":params}
            return

        if params["type"] == "random":
            params["type"] = random.randint(1,len(self.prefabs["ScrapToMetalBars"]))

        character = params["character"]

        room = self.addRoom(params["coordinate"])

        floorPlan = copy.deepcopy(self.prefabs["ScrapToMetalBars"][params["type"]-1])
        room.resetDirect()
        room.floorPlan = floorPlan 

        if instaSpawn:
            room.spawnPlaned()
            room.spawnPlaned()
            room.addRandomItems()
            room.spawnGhouls(character)

        #self.container.sources.append((room.getPosition(),"MetalBars"))

        for otherRoom in self.rooms:
            otherRoom.sources.append((room.getPosition(),"MetalBars"))
        self.sourcesList.append((room.getPosition(),"MetalBars"))

    def getAvailableRooms(self):
        terrain = self.getTerrain()

        result = []
        for room in terrain.rooms:
            if len(room.itemsOnFloor) > 13+13+12+12 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots:
                continue

            pos = room.getPosition()
            if pos in self.generalPurposeRooms or (pos[0],pos[1]) in self.generalPurposeRooms:
                continue
            if pos in self.specialPurposeRooms or (pos[0],pos[1]) in self.specialPurposeRooms:
                continue
            result.append(room)

        return result

    def clearFieldFromMap(self,params):
        architect = src.items.itemMap["ArchitectArtwork"]()
        self.container.container.addItem(architect,(1,1,0))
        architect.doClearField(params["coordinate"][0], params["coordinate"][1])
        self.container.container.removeItem(architect)

    def addMinefieldFromMap(self,params):
        architect = src.items.itemMap["ArchitectArtwork"]()
        self.container.container.addItem(architect,(1,1,0))
        architect.doAddMinefield(params["coordinate"][0], params["coordinate"][1],20)
        self.container.container.removeItem(architect)

    def addScrapFieldFromMap(self,params):
        architect = src.items.itemMap["ArchitectArtwork"]()
        self.container.container.addItem(architect,(1,1,0))
        architect.doAddScrapfield(params["coordinate"][0], params["coordinate"][1],200)
        self.container.container.removeItem(architect)
        self.scrapFields.append((params["coordinate"][0],params["coordinate"][1]))

        for otherRoom in self.rooms:
            otherRoom.sources.append((params["coordinate"],"rawScrap"))

    def addFarmFromMap(self,params,forceSpawn=0):
        room = self.addRoom(params["coordinate"])
        if not room:
            return
        for offset in [(-1,0),(1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
            pos = (params["coordinate"][0]+offset[0],params["coordinate"][1]+offset[1])
            self.clearFieldFromMap({"coordinate":pos})

            item = src.items.itemMap["AutoFarmer"]()
            self.getTerrain().addItem(item,((params["coordinate"][0]+offset[0])*15+7,(params["coordinate"][1]+offset[1])*15+7,0))
            self.getTerrain().minimapOverride[pos] = (src.interaction.urwid.AttrSpec("#030", "black"), ",.")

            for x in (2,4,10,12):
                for y in (2,4,10,12):
                    item = src.items.itemMap["MoldSpore"]()
                    self.container.container.addItem(item,((params["coordinate"][0]+offset[0])*15+x,(params["coordinate"][1]+offset[1])*15+y,0))
                    item.apply(params["character"],forceSpawn=forceSpawn)

        floorPlan = {}
        floorPlan["buildSites"] = []
        floorPlan["buildSites"].append([(4,5,0),"ScratchPlate", {"commands":{"noscratch":"jjaKsdJsJs"},"settings":{"scratchThreashold":1000}}])

        item = src.items.itemMap["Command"]()
        item.command = "14dj13wj13aj13aj13sj13sj13dj13dj13wj13adja"
        item.bolted = True
        room.addItem(item,(6,6,0))

        item = src.items.itemMap["Command"]()
        item.command = "ww5a"+10*"Lw"+"d"+10*"Jw"+"ddJwddJwss"
        item.bolted = True
        room.addItem(item,(7,6,0))

        item = src.items.itemMap["Command"]()
        item.command = "wajjaaJsdddsdjaj"
        item.bolted = True
        room.addItem(item,(5,6,0))

        corpseAnimator = src.items.itemMap["CorpseAnimator"]()
        room.addItem(corpseAnimator,(4,6,0))

        item = src.items.itemMap["BloomShredder"]()
        room.addItem(item,(3,3,0))

        item = src.items.itemMap["BioPress"]()
        room.addItem(item,(5,3,0))

        item = src.items.itemMap["GooProducer"]()
        room.addItem(item,(7,3,0))
        item = src.items.itemMap["GooDispenser"]()
        room.addItem(item,(8,3,0))

        for i in range(0,10):
            item = src.items.itemMap["Corpse"]()
            room.addItem(item,(3,6,0))

        ghoulFeeder = src.items.itemMap["GhoulFeeder"]()
        room.addItem(ghoulFeeder,(2,6,0))

        room.floorPlan = floorPlan

        room.spawnPlaned()
        room.spawnPlaned()

        return room

    def addWorkshopRoomFromMap(self,params):
        room = self.addRoom(params["coordinate"],roomType="WorkshopRoom")
        room.doBasicSetup()
        self.workshopRooms.append(room)
        return room

    def addTrapRoomFromMap(self,params):
        room = self.addRoom(params["coordinate"],roomType="TrapRoom")
        room.faction = params["character"].faction
        return room

    def addTempleRoomFromMap(self,params):
        room = self.addRoom(params["coordinate"],roomType="TempleRoom")
        room.faction = params["character"].faction

        #specialItemSlotPositions = [(1,1),(2,1),(3,1),(4,1),(5,1),(7,1),(8,1),(9,1),(10,1),(11,1),(1,3),(1,4),(1,5),(1,7),(1,8)]
        specialItemSlotPositions = [(1,1,0),(2,1,0),(3,1,0),(4,1,0),(5,1,0),(7,1,0)]#,(8,1),(9,1),(10,1),(11,1),(1,3),(1,4),(1,5),(1,7),(1,8)]
        counter = 1
        for pos in specialItemSlotPositions:
            slotItem = src.items.itemMap["SpecialItemSlot"]()
            slotItem.itemID = counter
            slotItem.faction = room.faction
            slotItem.hasItem = False
            room.addItem(slotItem,pos)
            counter += 1

        return room

    def addTeleporterRoomFromMap(self,params):
        room = self.addRoom(params["coordinate"],roomType="TeleporterRoom")

    def magicAdvanceRoomFromMap(self,params):
        character = params["character"]

        room = self.container.container.getRoomByPosition(params["coordinate"])[0]

        room.spawnPlaned()
        room.spawnPlaned()
        room.addRandomItems()

    def setConnectionsFromMap(self,params,noFurtherInteraction=False):
        character = params["character"]
        if not "selection" in params:
            params["selection"] = None

        if params["selection"] == "done":
            return

        room = self.container.container.getRoomByPosition(params["coordinate"])[0]

        if params["selection"] in ("w","a","s","d",):
            if params["selection"] == "w":
                positions = [(6,0,0),(6,12,0)]
                otherRoom = (0,-1)
            if params["selection"] == "a":
                positions = [(0,6,0),(12,6,0)]
                otherRoom = (-1,0)
            if params["selection"] == "s":
                positions = [(6,12,0),(6,0,0)]
                otherRoom = (0,1)
            if params["selection"] == "d":
                positions = [(12,6,0),(0,6,0)]
                otherRoom = (1,0)

            oldItem = room.getItemByPosition(positions[0])[0]
            if oldItem.walkable:
                newItem = src.items.itemMap["Wall"]()
            else:
                newItem = src.items.itemMap["Door"]()
                newItem.walkable = True
            room.removeItem(oldItem)
            room.addItem(newItem,positions[0])

            roomList = self.container.container.getRoomByPosition((params["coordinate"][0]+otherRoom[0],params["coordinate"][1]+otherRoom[1]))
            if roomList:
                otherRoom = roomList[0]
                oldItem = otherRoom.getItemByPosition(positions[1])[0]
                if oldItem.walkable:
                    newItem = src.items.itemMap["Wall"]()
                else:
                    newItem = src.items.itemMap["Door"]()
                    newItem.walkable = True
                otherRoom.removeItem(oldItem)
                otherRoom.addItem(newItem,positions[1])

        if noFurtherInteraction:
            return

        options = []
        options.append(("w","toggle north"))
        options.append(("a","toggle west"))
        options.append(("s","toggle south"))
        options.append(("d","toggle east"))
        options.append(("done","done"))
        submenue = src.interaction.SelectionMenu("What do you want to do?",options)
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"setConnectionsFromMap","params":params}
        return

    def addStorageRoomFromMap(self,params,instaSpawn=False):
        room = self.addRoom(params["coordinate"])
        """
        room.addStorageSlot((3,3,0),None)
        room.addStorageSlot((4,3,0),None)
        room.addStorageSlot((5,3,0),None)
        room.addStorageSlot((6,3,0),None)

        room.walkingSpace.add((3,4,0))
        room.walkingSpace.add((4,4,0))
        room.walkingSpace.add((5,4,0))
        room.walkingSpace.add((6,4,0))
        """

        floorPlan = copy.deepcopy(random.choice(self.prefabs["storage"]))
        room.resetDirect()
        room.floorPlan = floorPlan 

        self.container.storageRooms.append(room)

        for otherRoom in self.rooms:
            pos = room.getPosition()
            otherRoom.sources.insert(0,(pos,"Corpse"))
            otherRoom.sources.insert(0,(pos,"Scrap"))
            otherRoom.sources.insert(0,(pos,"Sheet"))
            otherRoom.sources.insert(0,(pos,"Frame"))
            otherRoom.sources.insert(0,(pos,"ScrapCompactor"))
            otherRoom.sources.insert(0,(pos,"Rod"))
            otherRoom.sources.insert(0,(pos,"Armor"))
            otherRoom.sources.insert(0,(pos,"MetalBars"))
            otherRoom.sources.insert(0,(pos,"Sword"))
            otherRoom.sources.insert(0,(pos,"Painter"))
            otherRoom.sources.insert(0,(pos,"ScratchPlate"))
            otherRoom.sources.insert(0,(pos,"CorpseAnimator"))
            otherRoom.sources.insert(0,(pos,"LightningRod"))

        if instaSpawn:
            room.spawnPlaned()
            room.spawnPlaned()
            room.addRandomItems()
        return room

    def setFloorplanFromMap(self,params):

        character = params["character"]

        if not "type" in params:
            options = []
            options.append(("storage","storage"))
            options.append(("wallProduction","wall production"))
            options.append(("basicMaterialsProduction","basic material production"))
            options.append(("caseProduction","case production"))
            options.append(("scrapCompactor","scrap compactor"))
            options.append(("scrapCompactorProduction","scrap compactor production"))
            options.append(("basicRoombuildingItemsProduction","basic room building items production"))
            options.append(("productionRoom","production room"))
            options.append(("exit","exit menu"))
            submenue = src.interaction.SelectionMenu("what floorplan to use?",options,targetParamName="type")
            submenue.tag = "floorplanSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"setFloorplanFromMap","params":params}
            return

        terrain = self.getTerrain()
        room = terrain.getRoomByPosition(params["coordinate"])[0]

        floorPlanType = params["type"]

        if floorPlanType == "exit":
            return
        
        walkingSpaces = []
        outputSlots = []
        inputSlots = []
        buildSites = []
        storageSlots = []

        if floorPlanType == "basicMaterialsProduction":
            for y in (1,4,6,8,11,):
                for x in range(1,12):
                    walkingSpaces.append((x,y,0))
            for y in (2,3,5,7,9,10,):
                walkingSpaces.append((1,y,0))
                inputSlots.append(((2,y,0),"Scrap",{}))
                buildSites.append(((3,y,0),"ScrapCompactor",{}))
                inputSlots.append(((4,y,0),"MetalBars",{}))

                if y == 2:
                    itemType = "Rod"
                if y == 3:
                    itemType = "Sheet"
                if y == 5:
                    itemType = "Radiator"
                if y == 7:
                    itemType = "Stripe"
                if y == 9:
                    itemType = "Bolt"
                if y == 10:
                    itemType = "Mount"

                buildSites.append(((5,y,0),"Machine",{"toProduce":itemType}))
                outputSlots.append(((6,y,0),itemType,{}))

                if y == 2:
                    itemType = "Frame"
                if y == 3:
                    itemType = "Tank"
                if y == 5:
                    itemType = "Heater"
                if y == 7:
                    itemType = "pusher"
                if y == 9:
                    itemType = "puller"
                if y == 10:
                    itemType = "Connector"

                buildSites.append(((7,y,0),"Machine",{"toProduce":itemType}))
                outputSlots.append(((8,y,0),itemType,{}))

                if y == 2:
                    itemType = "Case"
                if y == 3:
                    itemType = "GooFlask"
                if y == 5:
                    itemType = None
                if y == 7:
                    itemType = None
                if y == 9:
                    itemType = None
                if y == 10:
                    itemType = "MemoryCell"

                if itemType:
                    buildSites.append(((9,y,0),"Machine",{"toProduce":itemType}))
                    outputSlots.append(((10,y,0),itemType,{}))

                walkingSpaces.append((11,y,0))

        if floorPlanType == "caseProduction":
            for y in (1,4,7,10,):
                for x in range(1,12):
                    walkingSpaces.append((x,y,0))
            for y in (2,3,5,6,8,9,):
                walkingSpaces.append((1,y,0))
                inputSlots.append(((2,y,0),"Scrap",{}))
                buildSites.append(((3,y,0),"ScrapCompactor",{}))
                inputSlots.append(((4,y,0),"MetalBars",{}))
                buildSites.append(((5,y,0),"Machine",{"toProduce":"Rod"}))
                outputSlots.append(((6,y,0),"Rod",{}))
                buildSites.append(((7,y,0),"Machine",{"toProduce":"Frame"}))
                outputSlots.append(((8,y,0),"Frame",{}))
                buildSites.append(((9,y,0),"Machine",{"toProduce":"Case"}))
                outputSlots.append(((10,y,0),"Case",{}))
                walkingSpaces.append((11,y,0))
            walkingSpaces.append((6,11,0))

        if floorPlanType == "scrapCompactorProduction":
            for y in (1,4,6,8,11,):
                for x in range(1,12):
                    walkingSpaces.append((x,y,0))
            for y in (2,3,5,7,9,10,):
                for x in (1,7,):
                    inputSlots.append( ((x  ,y,0),"Scrap",{}))
                    buildSites.append( ((x+1,y,0),"ScrapCompactor",{}))
                    inputSlots.append(((x+2,y,0),"MetalBars",{}))
                    buildSites.append( ((x+3,y,0),"Machine",{"toProduce":"ScrapCompactor"}))
                    outputSlots.append(((x+4,y,0),"ScrapCompactor",{}))
                walkingSpaces.append((6,y,0))
            walkingSpaces.append((6,11,0))

        if floorPlanType == "basicRoombuildingItemsProduction":
            for y in (3,6,10,):
                for x in range(1,12):
                    if x == 6:
                        continue
                    walkingSpaces.append((x,y,0))
            for y in range(1,12):
                walkingSpaces.append((6,y,0))
            walkingSpaces.append((6,11,0))
            walkingSpaces.append((1,7,0))
            walkingSpaces.append((1,8,0))
            walkingSpaces.append((1,9,0))
            walkingSpaces.append((2,8,0))
            walkingSpaces.append((7,8,0))
            walkingSpaces.append((11,7,0))
            walkingSpaces.append((11,8,0))
            walkingSpaces.append((11,9,0))
            walkingSpaces.append((5,1,0))
            walkingSpaces.append((7,1,0))
            walkingSpaces.append((8,1,0))
            walkingSpaces.append((9,1,0))

            inputSlots.append( (( 7,2,0),"Scrap",{}))
            buildSites.append( (( 8,2,0),"ScrapCompactor",{}))
            inputSlots.append( (( 9,2,0),"MetalBars",{}))
            buildSites.append( ((10,2,0),"Machine",{"toProduce":"Door"}))
            inputSlots.append( ((10,1,0),"Case",{}))
            outputSlots.append(((11,2,0),"Door",{}))
            inputSlots.append( (( 7,5,0),"Scrap",{}))
            buildSites.append( (( 8,5,0),"ScrapCompactor",{}))
            inputSlots.append( (( 9,5,0),"MetalBars",{}))
            buildSites.append( ((10,5,0),"Machine",{"toProduce":"Door"}))
            inputSlots.append( ((10,4,0),"Case",{}))
            outputSlots.append(((11,5,0),"Door",{}))
            inputSlots.append( (( 1,2,0),"Scrap",{}))
            buildSites.append( (( 2,2,0),"ScrapCompactor",{}))
            inputSlots.append( (( 3,2,0),"MetalBars",{}))
            buildSites.append( (( 4,2,0),"Machine",{"toProduce":"Door"}))
            inputSlots.append( (( 4,1,0),"Case",{}))
            outputSlots.append((( 5,2,0),"Door",{}))
            inputSlots.append( (( 1,5,0),"Scrap",{}))
            buildSites.append( (( 2,5,0),"ScrapCompactor",{}))
            inputSlots.append( (( 3,5,0),"MetalBars",{}))
            buildSites.append( (( 4,5,0),"Machine",{"toProduce":"Door"}))
            inputSlots.append( (( 4,4,0),"Case",{}))
            outputSlots.append((( 5,5,0),"Door",{}))

            outputSlots.append((( 5,8,0),"RoomBuilder",{}))
            buildSites.append( (( 4,8,0),"Machine",{"toProduce":"RoomBuilder"}))
            inputSlots.append( (( 3,8,0),"Case",{}))
            inputSlots.append( (( 4,7,0),"pusher",{}))
            buildSites.append( (( 3,7,0),"Machine",{"toProduce":"pusher"}))
            inputSlots.append( (( 2,7,0),"Stripe",{}))
            inputSlots.append( (( 4,9,0),"puller",{}))
            buildSites.append( (( 3,9,0),"Machine",{"toProduce":"puller"}))
            inputSlots.append( (( 2,9,0),"Bolt",{}))

            outputSlots.append(((10,8,0),"RoomBuilder",{}))
            buildSites.append( (( 9,8,0),"Machine",{"toProduce":"RoomBuilder"}))
            inputSlots.append( (( 8,8,0),"Case",{}))
            inputSlots.append( (( 9,7,0),"pusher",{}))
            buildSites.append( (( 8,7,0),"Machine",{"toProduce":"pusher"}))
            inputSlots.append( (( 7,7,0),"Stripe",{}))
            inputSlots.append( (( 9,9,0),"puller",{}))
            buildSites.append( (( 8,9,0),"Machine",{"toProduce":"puller"}))
            inputSlots.append( (( 7,9,0),"Bolt",{}))

        if floorPlanType == "productionRoom":
            for y in (1,4,7,11,):
                for x in range(1,12):
                    walkingSpaces.append((x,y,0))
            for y in (2,3,5,6,8,9,10):
                walkingSpaces.append((1,y,0))
                walkingSpaces.append((11,y,0))

        if floorPlanType == "scrapCompactor":
            for y in (1,4,7,10,):
                for x in range(1,12):
                    walkingSpaces.append((x,y,0))
            for y in (2,3,5,6,8,9,):
                walkingSpaces.append((1,y,0))
                for x in (3,6,9,):
                    inputSlots.append( ((x-1,y,0),"Scrap",{}))
                    buildSites.append( ((x  ,y,0),"ScrapCompactor",{}))
                    outputSlots.append(((x+1,y,0),"MetalBars",{}))
                walkingSpaces.append((11,y,0))
            walkingSpaces.append((6,11,0))

        if floorPlanType == "wallProduction":
            for y in range(1,12):
                walkingSpaces.append((6,y,0))
            for x in range(1,12):
                if x == 6:
                    continue
                walkingSpaces.append((x,3,0))
            for x in range(1,12):
                if x == 6:
                    continue
                walkingSpaces.append((x,6,0))
            for x in range(1,12):
                if x == 6:
                    continue
                walkingSpaces.append((x,9,0))

            basePositions = [(1,1,0),(1,4,0),(1,7,0),(7,1,0),(7,4,0),(7,7,0),]
            for basePosition in basePositions:
                outputSlots.append(((basePosition[0]+4,basePosition[1]+1,0),"Wall",{}))
                inputSlots.append(((basePosition[0],basePosition[1]+1,0),"Scrap",{}))
                buildSites.append(((basePosition[0]+1,basePosition[1]+1,0),"ScrapCompactor",{}))
                inputSlots.append(((basePosition[0]+2,basePosition[1]+1,0),"MetalBars",{}))
                inputSlots.append(((basePosition[0]+3,basePosition[1],0),"Case",{}))
                buildSites.append(((basePosition[0]+3,basePosition[1]+1,0),"Machine",{"toProduce":"Wall"}))
            basePositions = [(1,10,0),(7,10,0)]
            for basePosition in basePositions:
                outputSlots.append(((basePosition[0]+4,basePosition[1],0),"Wall",{}))
                inputSlots.append(((basePosition[0],basePosition[1],0),"Scrap",{}))
                buildSites.append(((basePosition[0]+1,basePosition[1],0),"ScrapCompactor",{}))
                inputSlots.append(((basePosition[0]+2,basePosition[1],0),"MetalBars",{}))
                inputSlots.append(((basePosition[0]+3,basePosition[1]+1,0),"Case",{}))
                buildSites.append(((basePosition[0]+3,basePosition[1],0),"Machine",{"toProduce":"Wall"}))
            
            walkingSpaces.append((5,11,0))
            walkingSpaces.append((7,11,0))
            walkingSpaces.append((8,11,0))
            walkingSpaces.append((9,11,0))
            walkingSpaces.append((7,1,0))
            walkingSpaces.append((8,1,0))
            walkingSpaces.append((9,1,0))
            walkingSpaces.append((5,1,0))

        if floorPlanType == "storage":
            for y in range(1,12):
                walkingSpaces.append((6,y,0))
            for x in range(1,12):
                if x == 6:
                    continue
                storageSlots.append(((x,1,0),None,{}))
            for x in range(1,12):
                if x == 6:
                    continue
                walkingSpaces.append((x,2,0))
            for x in range(1,12):
                if x == 6:
                    continue
                storageSlots.append(((x,3,0),None,{}))
            for x in range(1,12):
                if x == 6:
                    continue
                walkingSpaces.append((x,4,0))
            for x in range(1,12):
                if x == 6:
                    continue
                storageSlots.append(((x,5,0),None,{}))
            for x in range(1,12):
                if x == 6:
                    continue
                walkingSpaces.append((x,6,0))
            for x in range(1,12):
                if x == 6:
                    continue
                storageSlots.append(((x,7,0),None,{}))
            for x in range(1,12):
                if x == 6:
                    continue
                walkingSpaces.append((x,8,0))
            for x in range(1,12):
                if x == 6:
                    continue
                storageSlots.append(((x,9,0),None,{}))
            for x in range(1,12):
                if x == 6:
                    continue
                walkingSpaces.append((x,10,0))
            for x in range(1,12):
                if x == 6:
                    continue
                if x > 6:
                    continue
                storageSlots.append(((x,11,0),None,{}))

        floorPlan = {}
        if walkingSpaces:
            floorPlan["walkingSpace"] = walkingSpaces
        if outputSlots:
            floorPlan["outputSlots"] = outputSlots
        if inputSlots:
            floorPlan["inputSlots"] = inputSlots
        if buildSites:
            floorPlan["buildSites"] = buildSites
        if storageSlots:
            floorPlan["storageSlots"] = storageSlots

        room.floorPlan = floorPlan
        room.tag = floorPlanType
        room.requiredDuties.append("painting")
        params["character"].changed("assigned floor plan",params)
        self.showMap(params["character"], cursor = params["coordinate"])

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
        character.addMessage("you bolt down the CityPlaner")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the CityPlaner")
        character.changed("unboltedItem",{"character":character,"item":self})

    def setGeneralPurposeRoomFromMap(self,params):
        self.generalPurposeRooms.append((params["coordinate"][0],params["coordinate"][1],0))
        params["character"].changed("designated room",params)
        self.showMap(params["character"], cursor = params["coordinate"])

        terrain = self.getTerrain()
        room = terrain.getRoomByPosition(params["coordinate"])[0]
        room.tag = "generalPurposeRoom"

    def setSpecialPurposeRoomFromMap(self,params):
        character = params["character"]

        if not "tag" in params:
            submenue = src.interaction.InputMenu("enter the tag for this room",targetParamName="tag",stealAllKeys=False)
            submenue.tag = "tagInput"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"setSpecialPurposeRoomFromMap","params":params}
            return

        self.specialPurposeRooms.append((params["coordinate"][0],params["coordinate"][1],0))
        terrain = self.getTerrain()
        room = terrain.getRoomByPosition(params["coordinate"])[0]
        room.tag = params["tag"]
        params["character"].changed("designated room",params)
        self.showMap(params["character"], cursor = params["coordinate"])

    def scheduleRoomFromMap(self,params):
        self.plannedRooms.append((params["coordinate"][0],params["coordinate"][1],0))
        params["character"].changed("scheduled room",params)
        self.showMap(params["character"], cursor = params["coordinate"])

    def clearRoomDesignation(self,params):
        pos = (params["coordinate"][0],params["coordinate"][1],0)
        if pos in self.specialPurposeRooms:
            self.specialPurposeRooms.remove(pos)
        if pos in self.generalPurposeRooms:
            self.generalPurposeRooms.remove(pos)
        terrain = self.getTerrain()
        room = terrain.getRoomByPosition(params["coordinate"])[0]
        room.tag = None
        params["character"].changed("designated room",params)
        self.showMap(params["character"], cursor = params["coordinate"])

    def unscheduleRoomFromMap(self,params):

        self.plannedRooms.remove((params["coordinate"][0],params["coordinate"][1],0))

        self.showMap(params["character"], cursor = params["coordinate"])

    def showMap(self, character, cursor = None):
        """
        """
        terrain = self.getTerrain()

        # render empty map
        mapContent = []
        for x in range(0, 15):
            mapContent.append([])
            for y in range(0, 15):
                if x not in (0, 14) and y not in (0, 14):
                    char = "  "
                elif not x == 7 and not y == 7:
                    char = "##"
                else:
                    char = "  "
                mapContent[x].append(char)

        functionMap = {}

        for x in range(1,14):
            for y in range(1,14):
                functionMap[(x,y)] = {}
                functionMap[(x,y)]["r"] = {
                    "function": {
                        "container":self,
                        "method":"scheduleRoomFromMap",
                        "params":{"character":character},
                    },
                    "description":"schedule building a room",
                }
        
        for room in terrain.rooms:
            del functionMap[(room.xPosition,room.yPosition)]

        for room in terrain.rooms:
            if not (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                mapContent[room.yPosition][room.xPosition] = "EE"
                functionMap[(room.xPosition,room.yPosition)] = {}
                functionMap[(room.xPosition,room.yPosition)]["f"] = {
                        "function": {
                            "container":self,
                            "method":"setFloorplanFromMap",
                            "params":{"character":character},
                        },
                        "description":"to set floor plan",
                    }
                functionMap[(room.xPosition,room.yPosition)]["g"] = {
                        "function": {
                            "container":self,
                            "method":"setGeneralPurposeRoomFromMap",
                            "params":{"character":character},
                        },
                        "description":"to designate room as general storage room",
                    }
                functionMap[(room.xPosition,room.yPosition)]["p"] = {
                        "function": {
                            "container":self,
                            "method":"setSpecialPurposeRoomFromMap",
                            "params":{"character":character},
                        },
                        "description":"to designate room as special storage room",
                    }
            else:
                mapContent[room.yPosition][room.xPosition] = room.displayChar

        for pos in self.plannedRooms:
            mapContent[pos[1]][pos[0]] = "xx"
        for pos in self.specialPurposeRooms:
            if (pos[0],pos[1]) in functionMap:
                del functionMap[(pos[0],pos[1])]
            mapContent[pos[1]][pos[0]] = "sp"
            functionMap[(pos[0],pos[1])] = {}
            functionMap[(pos[0],pos[1])]["x"] = {
                    "function": {
                        "container":self,
                        "method":"clearRoomDesignation",
                        "params":{"character":character},
                    },
                    "description":"clear room designation",
                }
        for pos in self.generalPurposeRooms:
            if (pos[0],pos[1]) in functionMap:
                del functionMap[(pos[0],pos[1])]
            mapContent[pos[1]][pos[0]] = "gp"
            functionMap[(pos[0],pos[1])] = {}
            functionMap[(pos[0],pos[1])]["x"] = {
                    "function": {
                        "container":self,
                        "method":"clearRoomDesignation",
                        "params":{"character":character},
                    },
                    "description":"clear room designation",
                }

        for pos in self.plannedRooms:
            del functionMap[(pos[0],pos[1])]
            functionMap[(pos[0],pos[1])] = {}
            functionMap[(pos[0],pos[1])]["x"] = {
                    "function": {
                        "container":self,
                        "method":"unscheduleRoomFromMap",
                        "params":{"character":character},
                    },
                    "description":"unschedule building a room",
                }

        """
        for scrapField in self.scrapFields:
            plot = scrapField
            mapContent[plot[1]][plot[0]] = "*#"

            if plot not in functionMap:
                functionMap[plot] = {}

            functionMap[plot]["m"] = {
                "function": {
                    "container":self,
                    "method":"buildMineFromRoom",
                    "params":{"character":character},
                },
                "description":"build mine from room",
            }

        for plot in self.reservedPlots:
            mapContent[plot[1]][plot[0]] = "RR"
                
            if plot not in functionMap:
                functionMap[plot] = {}

            functionMap[plot]["R"] = {
                "function": {
                    "container":self,
                    "method":"unreservePlotFromMap",
                    "params":{"character":character},
                },
                "description":"remove reservation",
            }
        """

        plot = (self.container.xPosition,self.container.yPosition)
        mapContent[plot[1]][plot[0]] = "CB"

        extraText = "\n\n"
        """
        for task in reversed(self.tasks):
            extraText += "%s\n"%(task,)
        """

        self.submenue = src.interaction.MapMenu(mapContent=mapContent,functionMap=functionMap, extraText=extraText, cursor=cursor)
        character.macroState["submenue"] = self.submenue

    def getFloorPlanFromDict(self,rawFloorplan):
        converted = {}
        if "buildSites" in rawFloorplan:
            buildSites = []
            for item in rawFloorplan["buildSites"]:
                buildSites.append((tuple(item[0]),item[1],item[2]))
            converted["buildSites"] = buildSites
        if "inputSlots" in rawFloorplan:
            inputSlots = []
            for item in rawFloorplan["inputSlots"]:
                inputSlots.append((tuple(item[0]),item[1],item[2]))
            converted["inputSlots"] = inputSlots
        if "outputSlots" in rawFloorplan:
            outputSlots = []
            for item in rawFloorplan["outputSlots"]:
                outputSlots.append((tuple(item[0]),item[1],item[2]))
            converted["outputSlots"] = outputSlots
        if "storageSlots" in rawFloorplan:
            outputSlots = []
            for item in rawFloorplan["storageSlots"]:
                outputSlots.append((tuple(item[0]),item[1],item[2]))
            converted["storageSlots"] = outputSlots
        if "walkingSpace" in rawFloorplan:
            walkingSpace = []
            for item in rawFloorplan["walkingSpace"]:
                walkingSpace.append(tuple(item))
            converted["walkingSpace"] = walkingSpace
        return converted

    def addWorkshop(self,smallMachinesToAdd,bigMachinesToAdd,room):

        if not smallMachinesToAdd and not bigMachinesToAdd:
            return

        room.addGhoulSquare((6,6,0))

        newOutputs = []

        if smallMachinesToAdd:
            newOutputs.extend(smallMachinesToAdd[0:3])
            room.addWorkshopSquare((0,6,0),machines=smallMachinesToAdd[0:3])
            command = "a5w"+"4s4aJwJsddJwJsddww4aJwddJwddww"+"5sd"
            room.floorPlan["buildSites"].append(((7,11,0),"Command",{"extraName":"produce items southwest","command":command}))
            smallMachinesToAdd = smallMachinesToAdd[3:]
        elif bigMachinesToAdd:
            newOutputs.extend(bigMachinesToAdd[0:2])
            room.addBigWorkshopSquare((0,6,0),machines=bigMachinesToAdd[0:2])
            command = src.items.itemMap["Command"]()
            command.bolted = True
            command.command = "a5w"+"3s3aJwJs3d3w"+"5sd"
            command.extraName = "produce items southwest"
            room.addItem(command,(7,11,0))
            bigMachinesToAdd = bigMachinesToAdd[2:]

        if smallMachinesToAdd:
            newOutputs.extend(smallMachinesToAdd[0:3])
            room.addWorkshopSquare((6,0,0),machines=smallMachinesToAdd[0:3])
            command = "aa5w"+"wwddJwJsddJwJs4aww2dJwddJw4a4s"+"5sdd"
            room.floorPlan["buildSites"].append(((8,11,0),"Command",{"extraName":"produce items northeast","command":command}))
            smallMachinesToAdd = smallMachinesToAdd[3:]
        elif bigMachinesToAdd:
            newOutputs.extend(bigMachinesToAdd[0:2])
            room.addBigWorkshopSquare((6,0,0),machines=bigMachinesToAdd[0:2])
            command = src.items.itemMap["Command"]()
            command.bolted = True
            command.command = "aa5w"+"3w3dJwJs3a3s"+"5sdd"
            command.extraName = "produce items northeast"
            room.addItem(command,(8,11,0))
            bigMachinesToAdd = bigMachinesToAdd[2:]

        if smallMachinesToAdd:
            newOutputs.extend(smallMachinesToAdd[0:3])
            room.addWorkshopSquare((0,0,0),machines=smallMachinesToAdd[0:3])
            command = "aaa5w"+"ww4aJwJsddJwJsddww4aJwddJwdd4s"+"5sddd"
            room.floorPlan["buildSites"].append(((9,11,0),"Command",{"extraName":"produce items northwest","command":command}))
            smallMachinesToAdd = smallMachinesToAdd[3:]
        elif bigMachinesToAdd:
            newOutputs.extend(bigMachinesToAdd[0:2])
            room.addBigWorkshopSquare((0,0,0),machines=bigMachinesToAdd[0:2])
            command = src.items.itemMap["Command"]()
            command.bolted = True
            command.command = "aaa5w"+"3w3aJwJs3d3s"+"5sddd"
            command.extraName = "produce items northwest"
            room.addItem(command,(9,11,0))
            bigMachinesToAdd = bigMachinesToAdd[2:]

src.items.addType(CityPlaner)
