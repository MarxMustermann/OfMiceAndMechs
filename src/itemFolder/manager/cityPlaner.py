import src

class CityPlaner(src.items.Item):
    """
    """


    type = "CityPlaner"

    def __init__(self, name="CityPlaner", noId=False):
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
                options.append((index,"prefab%s"%(index,)))
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
            room.spawnGhuls(character)

        #self.container.sources.append((room.getPosition(),"MetalBars"))

        for otherRoom in self.rooms:
            otherRoom.sources.append((room.getPosition(),"MetalBars"))
        self.sourcesList.append((room.getPosition(),"MetalBars"))

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

        ghulFeeder = src.items.itemMap["GhulFeeder"]()
        room.addItem(ghulFeeder,(2,6,0))

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

    def scheduleRoomFromMap(self,params):
        print(params)
        """
        handle a character having selected building a room
        and adding a task to the items task list

        Parameters:
            params: parameters given from the interaction menu
        """

        self.plannedRooms.append((params["coordinate"][0],params["coordinate"][1],0))
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

        
        for room in terrain.rooms:
            if not (len(room.itemsOnFloor) > 13+13+12+12 or room.floorPlan):
                mapContent[room.yPosition][room.xPosition] = "EE"
            else:
                mapContent[room.yPosition][room.xPosition] = room.displayChar

        for pos in self.plannedRooms:
            mapContent[pos[1]][pos[0]] = "xx"

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

        room.addGhulSquare((6,6,0))

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
