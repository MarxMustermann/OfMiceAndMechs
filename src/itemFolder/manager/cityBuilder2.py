import src
import random
import copy
import json

class CityBuilder2(src.items.Item):
    """
    a ingame item to build and extend cities
    is a representation of a city and holds the coresponding information
    takes tasks and delegates tasks to other manager
    """


    type = "CityBuilder2"

    def __init__(self, name="CityBuilder2", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="CC", name=name)

        self.prefabs = {"ScrapToMetalBars":[],"storage":[]}

        self.architect = None
        self.questArtwork = None
        self.plotPool = []
        self.reservedPlots = []
        self.scrapFields = []
        self.workshopRooms = []

        self.generateFloorPlans()
        self.enemyRoomCounter = 0
        self.rooms = []
        self.sourcesList = []

        self.charges = 0

    def generateFloorPlans(self):
        # scrap => metal bar processing
        floorPlan = {}
        floorPlan["inputSlots"] = []
        floorPlan["buildSites"] = []
        floorPlan["outputSlots"] = []
        floorPlan["storageSlots"] = []

        for y in (1,3,5,7,9,11,):
            floorPlan["storageSlots"].append(((1,y,0),"Scrap",{}))
            floorPlan["inputSlots"].append(((2,y,0),"Scrap",{}))
            floorPlan["buildSites"].append(((3,y,0),"ScrapCompactor",{}))
            floorPlan["outputSlots"].append(((4,y,0),"MetalBars",{}))
            floorPlan["storageSlots"].append(((5,y,0),"MetalBars",{}))

        for y in (1,3,5,7,9,):
            for x in range(7,12):
                itemType = "Scrap"
                if (y-1)%4 == 0:
                    itemType = "MetalBars"
                floorPlan["storageSlots"].append(((x,y,0),"MetalBars",{}))

        floorPlan["inputSlots"].append(((7,11,0),"Corpse",{}))
        floorPlan["buildSites"].append(((8,11,0),"CorpseAnimator",{}))
        floorPlan["buildSites"].append(((9,11,0),"Command",{"command":"dKdj"}))
        floorPlan["buildSites"].append(((10,11,0),"Command",{"command":"w7aJwJs3d4w3aJwJs3d4w3aJwJs3d8s4dsj"}))
        floorPlan["inputSlots"].append(((11,11,0),"Corpse",{}))

        floorPlan["walkingSpace"] = []
        for y in range(1,12):
            floorPlan["walkingSpace"].append((6,y,0))
        for y in (2,4,6,8,10,):
            for x in range(1,12):
                if x == 6:
                    continue
                floorPlan["walkingSpace"].append((x,y,0))
        self.prefabs["ScrapToMetalBars"].append(floorPlan)

        # scrap => metal bar processing
        floorPlan = {}
        floorPlan["inputSlots"] = []
        floorPlan["buildSites"] = []
        floorPlan["outputSlots"] = []
        floorPlan["storageSlots"] = []
        floorPlan["walkingSpace"] = []

        for pos in ((3,2,0),(3,4,0),(3,8,0),(3,10,0),(8,2,0),(8,4,0),(8,8,0),(8,10,0)):
            floorPlan["inputSlots"].append(((pos[0]-1,pos[1],pos[2]),"Scrap",{}))
            floorPlan["buildSites"].append((pos,"ScrapCompactor",{}))
            floorPlan["outputSlots"].append(((pos[0]+1,pos[1],pos[2]),"MetalBars",{}))
            floorPlan["storageSlots"].append(((pos[0]+2,pos[1],pos[2]),"MetalBars",{}))

        for y in (5,7,):
            for x in range(2,6,):
                floorPlan["inputSlots"].append(((x,y,0),"Scrap",{}))

        for y in range(1,12):
            floorPlan["walkingSpace"].append((6,y,0))
        for y in (1,3,6,9,11):
            for x in range(1,12):
                if x == 6:
                    continue
                floorPlan["walkingSpace"].append((x,y,0))
        for y in (2,4,5,7,8,10):
            for x in (1,11):
                floorPlan["walkingSpace"].append((x,y,0))

        floorPlan["inputSlots"].append(((7,5,0),"Corpse",{"maxAmount":2}))
        floorPlan["buildSites"].append(((8,5,0),"CorpseAnimator"))
        floorPlan["buildSites"].append(((9,5,0),"Command",{"command":"saaKw3dwj"}))
        floorPlan["buildSites"].append(((10,5,0),"Command",{"command":"dww3aJwJs5aJwJsaa6s2dJwJs5dJwJs3d4waj"}))

        floorPlan["inputSlots"].append(((7,7,0),"Corpse",{"maxAmount":2}))
        floorPlan["buildSites"].append(((8,7,0),"CorpseAnimator"))
        floorPlan["buildSites"].append(((9,7,0),"Command",{"command":"dj"}))
        floorPlan["buildSites"].append(((10,7,0),"Command",{"command":"w5a"+4*"KwKsa"+"wwLdLdwwLdLdw5dsLdLdssLdLd4sLdLdssLdLds5awLdLdwwLdLdwwd"+4*"KwKsd"+"d"+8*"Js"+"3dsj"}))

        self.prefabs["ScrapToMetalBars"].append(floorPlan)

        floorPlan = {}
        floorPlan["inputSlots"] = []
        floorPlan["buildSites"] = []
        floorPlan["outputSlots"] = []
        floorPlan["storageSlots"] = []
        floorPlan["walkingSpace"] = set()
        floorPlan["conditions"] = [{"no doors":[(6,0,0),(6,12,0)]}]

        for x in (4,8):
            for y in range(1,12):
                floorPlan["walkingSpace"].add((x,y,0))

        for x in (1,5,9):
            for y in (1,3,5,7,9):
                floorPlan["inputSlots"].append(((x,y,0),"Scrap",{}))
                floorPlan["buildSites"].append(((x+1,y,0),"ScrapCompactor",{}))
                floorPlan["outputSlots"].append(((x+2,y,0),"MetalBars",{}))

                floorPlan["walkingSpace"].add((x,y+1,0))
                floorPlan["walkingSpace"].add((x+1,y+1,0))
                floorPlan["walkingSpace"].add((x+2,y+1,0))

            floorPlan["buildSites"].append((((x,11,0),"CorpseAnimator",{})))

            if not x==1:
                command = 4*"Jwaawwdd"+"Jw"+"2a8s2d"+"j"
            else:
                command = 4*"Jwddwwaa"+"Jw"+"2d8s2a"+"j"
            floorPlan["buildSites"].append((((x+1,10,0),"Command",{"command":command})))

            floorPlan["buildSites"].append((((x+1,11,0),"Command",{"command":"Kdwj"})))

            floorPlan["inputSlots"].append(((x+2,11,0),"Corpse",{"maxAmount":2}))

        self.prefabs["ScrapToMetalBars"].append(floorPlan)

        self.prefabs["ScrapToMetalBars"] = []
        scrapToMetalBarsPrefabPaths = ["scrapToMetalbars1.json","scrapToMetalbars2.json","scrapToMetalbars3.json"]
        for path in scrapToMetalBarsPrefabPaths:
            with open("data/floorPlans/"+path) as fileHandle:
                rawFloorplan = json.load(fileHandle)    
            floorPlan = self.getFloorPlanFromDict(rawFloorplan)
            self.prefabs["ScrapToMetalBars"].append(floorPlan)

        floorPlan = {}
        floorPlan["storageSlots"] = []
        floorPlan["walkingSpace"] = set()
        for startPos in ((1,1),(1,5),(1,9,),(7,1),(7,5),(7,9,)):
            floorPlan["storageSlots"].append(((0+startPos[0],startPos[1],0),None,{}))
            floorPlan["storageSlots"].append(((1+startPos[0],startPos[1],0),None,{}))
            floorPlan["storageSlots"].append(((2+startPos[0],startPos[1],0),None,{}))
            floorPlan["storageSlots"].append(((3+startPos[0],startPos[1],0),None,{}))
            floorPlan["storageSlots"].append(((4+startPos[0],startPos[1],0),None,{}))
            floorPlan["walkingSpace"].add((0+startPos[0],startPos[1]+1,0))
            floorPlan["walkingSpace"].add((1+startPos[0],startPos[1]+1,0))
            floorPlan["walkingSpace"].add((2+startPos[0],startPos[1]+1,0))
            floorPlan["walkingSpace"].add((3+startPos[0],startPos[1]+1,0))
            floorPlan["walkingSpace"].add((4+startPos[0],startPos[1]+1,0))
            floorPlan["storageSlots"].append(((0+startPos[0],startPos[1]+2,0),None,{}))
            floorPlan["storageSlots"].append(((1+startPos[0],startPos[1]+2,0),None,{}))
            floorPlan["storageSlots"].append(((2+startPos[0],startPos[1]+2,0),None,{}))
            floorPlan["storageSlots"].append(((3+startPos[0],startPos[1]+2,0),None,{}))
            floorPlan["storageSlots"].append(((4+startPos[0],startPos[1]+2,0),None,{}))
        for y in range(1,12):
            floorPlan["walkingSpace"].add((6,y,0))
        self.prefabs["storage"].append(floorPlan)

        try:
            with open("gamestate/globalInfo.json", "r") as globalInfoFile:
                rawState = json.loads(globalInfoFile.read())
        except:
            rawState = {"saves": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],"customPrefabs":[]}

        for rawFloorPlan in rawState["customPrefabs"]:
            floorPlan = self.getFloorPlanFromDict(rawFloorPlan)
            self.prefabs["ScrapToMetalBars"].append(floorPlan)

        self.applyOptions.extend(
                        [
                                                                ("showMap", "show map"),
                                                                ("addProductionLine1", "add weapon production line"),
                                                                ("addProductionLine2", "add crystal compactor production line"),
                                                                ("addProductionLine3", "add scrapcompactor production line"),
                                                                ("addProductionLine4", "add basics production line"),
                                                                ("addProductionLine5", "add sheet production line"),
                                                                ("addProductionLine6", "add rod production line"),
                                                                ("addProductionLine7", "add wall production line"),
                                                                ("spawnCity", "spawn City"),
                        ]
                        )
        self.applyOptions = []
        self.applyMap = {
                    "showMap": self.showMap,
                    "addProductionLine1": self.addProductionLine1,
                    "addProductionLine2": self.addProductionLine2,
                    "addProductionLine3": self.addProductionLine3,
                    "addProductionLine4": self.addProductionLine4,
                    "addProductionLine5": self.addProductionLine5,
                    "addProductionLine6": self.addProductionLine6,
                    "addProductionLine7": self.addProductionLine7,
                    "spawnCity": self.spawnCity,
                        }
        
    def registerRoom(self,room):
        self.rooms.append(room)

    def addRoom(self,position,addEnemyRoom=True,roomType="EmptyRoom"):

        if self.container.container.getRoomByPosition(position):
            return
        
        offsets = ((-1,0),(1,0),(0,-1),(0,1))
        foundNeighbours = []
        for offset in offsets:
            if self.container.container.getRoomByPosition((position[0]+offset[0],position[1]+offset[1])):
                foundNeighbours.append(offset)

        if not foundNeighbours:
            doors = "6,0 0,6 6,12 12,6"
        else:
            doors = []
            for foundNeighbour in foundNeighbours:
                if foundNeighbour == (-1,0):
                    doors.append("0,6")
                    reversePos = (12,6,0)
                elif foundNeighbour == (1,0):
                    doors.append("12,6")
                    reversePos = (0,6,0)
                elif foundNeighbour == (0,-1):
                    doors.append("6,0")
                    reversePos = (6,12,0)
                elif foundNeighbour == (0,1):
                    doors.append("6,12")
                    reversePos = (6,0,0)
                neighbourRoom = self.container.container.getRoomByPosition((position[0]+foundNeighbour[0],position[1]+foundNeighbour[1]))[0]
                wall = neighbourRoom.getItemByPosition(reversePos)[0]
                neighbourRoom.removeItem(wall)
                door = src.items.itemMap["Door"]()
                door.walkable = True
                neighbourRoom.addItem(door,reversePos)
            doors = " ".join(doors)

        room = self.architect.doAddRoom(
            {
                "coordinate": position,
                "roomType": roomType,
                "doors": doors,
                "offset": [1,1],
                "size": [13, 13],
            },
            None,
        )

        room.sources.extend(self.sourcesList)

        for storageRoom in self.container.storageRooms:
            pos = storageRoom.getPosition()
            room.sources.insert(0,(pos,"Corpse"))
            room.sources.insert(0,(pos,"Scrap"))
            room.sources.insert(0,(pos,"Sheet"))
            room.sources.insert(0,(pos,"Frame"))
            room.sources.insert(0,(pos,"ScrapCompactor"))
            room.sources.insert(0,(pos,"Rod"))
            room.sources.insert(0,(pos,"Armor"))
            room.sources.insert(0,(pos,"MetalBars"))
            room.sources.insert(0,(pos,"Sword"))
            room.sources.insert(0,(pos,"Painter"))
            room.sources.insert(0,(pos,"ScratchPlate"))
            room.sources.insert(0,(pos,"CorpseAnimator"))

        for item in self.scrapFields:
            room.sources.insert(0,(item,"rawScrap"))

        self.rooms.append(room)

        #if addEnemyRoom:
        #    self.addEnemyRoomFromMap({"coordinate":(random.randint(2,11),random.randint(2,11))})

        room.sources.append((self.container.getPosition(),"ScrapCompactor"))
        room.sources.append((self.container.getPosition(),"MetalBars"))
        room.sources.append((self.container.getPosition(),"Painter"))
        room.sources.append((self.container.getPosition(),"Sheet"))
        room.sources.append((self.container.getPosition(),"CorpseAnimator"))
        room.sources.append((self.container.getPosition(),"Corpse"))
        room.sources.append((self.container.getPosition(),"ScratchPlate"))

        return room

    def addProductionLine1(self,character,instaSpawn=False):
        toAdd = ["Rod","Sword","Armor","Sheet","Bolt","Rod","Sword","Armor","Rod"]
        self.addProductionLine(character,instaSpawn=instaSpawn,toAdd=toAdd)

    def addProductionLine2(self,character,instaSpawn=False):
        toAdd = ["CrystalCompressor","CrystalCompressor","CrystalCompressor","CrystalCompressor","CrystalCompressor","CrystalCompressor","CrystalCompressor","CrystalCompressor","CrystalCompressor"]
        self.addProductionLine(character,instaSpawn=instaSpawn,toAdd=toAdd)

    def addProductionLine3(self,character,instaSpawn=False):
        toAdd = ["ScrapCompactor","ScrapCompactor","ScrapCompactor","ScrapCompactor","ScrapCompactor","ScrapCompactor","ScrapCompactor","ScrapCompactor","ScrapCompactor"]
        self.addProductionLine(character,instaSpawn=instaSpawn,toAdd=toAdd)

    def addProductionLine4(self,character,instaSpawn=False):
        toAdd = ["Sheet","Rod","Bolt","Frame","Mount","Puller","Pusher","Stripe","Tank"]
        self.addProductionLine(character,instaSpawn=instaSpawn,toAdd=toAdd)

    def addProductionLine5(self,character,instaSpawn=False):
        toAdd = ["Sheet","Sheet","Sheet","Sheet","Sheet","Sheet","Sheet","Sheet","Sheet"]
        self.addProductionLine(character,instaSpawn=instaSpawn,toAdd=toAdd)

    def addProductionLine6(self,character,instaSpawn=False):
        toAdd = ["Rod","Rod","Rod","Rod","Rod","Rod","Rod","Rod","Rod"]
        self.addProductionLine(character,instaSpawn=instaSpawn,toAdd=toAdd)

    def addProductionLine7(self,character,instaSpawn=False):
        toAdd = ["Wall",]
        self.addProductionLine(character,instaSpawn=instaSpawn,toAdd=toAdd)

    def addProductionLine(self,character,instaSpawn=False,toAdd=None):
        if not self.workshopRooms:
            character.addMessage("no workshop rooms available")
            return
        character.addMessage("trying to add production line")
        room = self.workshopRooms.pop()
        if not toAdd:
            items = ["Rod","Sword","Armor","Sheet","Bolt","Rod","Sword","Armor","Rod"]
        else:
            items = toAdd
        self.addWorkshop(items,[],room)
        for item in items:
            for otherRoom in self.rooms:
                if (room.getPosition(),item) in otherRoom.sources:
                    continue
                otherRoom.sources.append((room.getPosition(),item))
            self.sourcesList.append((room.getPosition(),item))

        if instaSpawn:
            room.spawnPlaned()
            room.spawnPlaned()
            room.addRandomItems()

    def spawnCity(self,character):
        if len(self.rooms) > 1:
            character.addMessage("need to remove old city first")

        citylocation = self.container.getPosition()
        backGuardRoom = self.addWorkshopRoomFromMap({"coordinate":(citylocation[0],citylocation[1]+1),"character":character})
        
        guardRoom = self.addTrapRoomFromMap({"coordinate":(citylocation[0],citylocation[1]-1),"character":character})
        guardRoom.chargeStrength = 20

        guardRoom = self.addTrapRoomFromMap({"coordinate":(citylocation[0],citylocation[1]-2),"character":character})
        guardRoom.chargeStrength = 20

        self.addWorkshopRoomFromMap({"coordinate":(citylocation[0]+1,citylocation[1]),"character":character})
        self.addWorkshopRoomFromMap({"coordinate":(citylocation[0]-1,citylocation[1]),"character":character})

        backGuardRoom = self.addTrapRoomFromMap({"character":character,"coordinate":(citylocation[0]+0,citylocation[1]+2)})
        backGuardRoom.chargeStrength = 20

        generalStorage = self.addStorageRoomFromMap({"character":character,"coordinate":(citylocation[0]+1,citylocation[1]+2)},instaSpawn=True)
        for i in range(1,10):
            generalStorage.addItem(src.items.itemMap["Painter"](),(1,1,0))
        for i in range(1,10):
            generalStorage.addItem(src.items.itemMap["Corpse"](),(2,1,0))
        item = src.items.itemMap["CorpseAnimator"]()
        item.bolted = False
        generalStorage.addItem(item,(3,1,0))
        item = src.items.itemMap["CorpseAnimator"]()
        item.bolted = False
        generalStorage.addItem(item,(4,1,0))
        item = src.items.itemMap["CorpseAnimator"]()
        item.bolted = False
        generalStorage.addItem(item,(5,1,0))

        for x in range(1,6):
            for i in range(1,25):
                generalStorage.addItem(src.items.itemMap["CrystalCompressor"](),(x,11,0))

        for x in range(1,6):
            for i in range(1,25):
                generalStorage.addItem(src.items.itemMap["Bomb"](),(x,9,0))

        for x in range(1,6):
            for i in range(1,25):
                generalStorage.addItem(src.items.itemMap["MetalBars"](),(x+6,11,0))

        for i in range(1,10):
            item = src.items.itemMap["ScratchPlate"]()
            item.bolted = False
            generalStorage.addItem(item,(7,1,0))
        for i in range(1,10):
            generalStorage.addItem(src.items.itemMap["Sheet"](),(8,1,0))
        for i in range(1,10):
            generalStorage.addItem(src.items.itemMap["Sheet"](),(9,1,0))
        for i in range(1,10):
            generalStorage.addItem(src.items.itemMap["Sheet"](),(10,1,0))

        self.addWorkshopRoomFromMap({"coordinate":(citylocation[0]+1,citylocation[1]+1),"character":character})
        
        self.addScrapCompactorFromMap({"coordinate":(citylocation[0]-1,citylocation[1]+1),"character":character,"type":"random"},instaSpawn=True)
        self.addWorkshopRoomFromMap({"coordinate":(citylocation[0]-1,citylocation[1]+2),"character":character})

        guardRoom2 = self.addTrapRoomFromMap({"coordinate":(citylocation[0]-1,citylocation[1]-1),"character":character})
        guardRoom2.chargeStrength = 5

        guardRoom3 = self.addTrapRoomFromMap({"coordinate":(citylocation[0]+1,citylocation[1]-1),"character":character})
        guardRoom3.chargeStrength = 5

        self.setConnectionsFromMap({"character":character,"coordinate":(citylocation[0],citylocation[1]-1),"selection":"w"},noFurtherInteraction=True)
        self.setConnectionsFromMap({"character":character,"coordinate":(citylocation[0],citylocation[1]),"selection":"w"},noFurtherInteraction=True)
        self.setConnectionsFromMap({"character":character,"coordinate":(citylocation[0],citylocation[1]),"selection":"d"},noFurtherInteraction=True)
        self.setConnectionsFromMap({"character":character,"coordinate":(citylocation[0],citylocation[1]),"selection":"a"},noFurtherInteraction=True)
        self.setConnectionsFromMap({"character":character,"coordinate":(citylocation[0],citylocation[1]+1),"selection":"d"},noFurtherInteraction=True)
        self.setConnectionsFromMap({"character":character,"coordinate":(citylocation[0],citylocation[1]+1),"selection":"a"},noFurtherInteraction=True)

        self.setConnectionsFromMap({"character":character,"coordinate":(citylocation[0],citylocation[1]-2),"selection":"w"},noFurtherInteraction=True)
        self.setConnectionsFromMap({"character":character,"coordinate":(citylocation[0],citylocation[1]-2),"selection":"a"},noFurtherInteraction=True)
        self.setConnectionsFromMap({"character":character,"coordinate":(citylocation[0],citylocation[1]-2),"selection":"s"},noFurtherInteraction=True)
        self.setConnectionsFromMap({"character":character,"coordinate":(citylocation[0],citylocation[1]-2),"selection":"d"},noFurtherInteraction=True)

        self.addProductionLine1(character,instaSpawn=True)
        self.addProductionLine2(character,instaSpawn=True)
        self.addProductionLine3(character,instaSpawn=True)
        self.addProductionLine2(character)

        self.addScrapFieldFromMap({"character":character,"coordinate":(citylocation[0]+1,citylocation[1]-2)})

        return {"backGuardRoom":backGuardRoom}

    def addEnemyRoomFromMap(self,params):
        room = self.addRoom(params["coordinate"],addEnemyRoom=False)

        self.enemyRoomCounter += 1

        for i in range(0,self.enemyRoomCounter):
            enemy = src.characters.Monster()
            enemy.godMode = True
            enemy.macroState["macros"]["g"] = ["g","g","_","g"]
            enemy.runCommandString("_g")
            room.addCharacter(enemy,random.randint(2,11),random.randint(2,11))

        item = src.items.itemMap["ScrapCompactor"]()
        item.bolted = False
        room.addItem(item,(random.randint(2,11),random.randint(2,11),0))

    def addActiveEnemies(self,params):

        for i in range(0,10):
            enemy = src.characters.Monster()
            enemy.godMode = True
            self.container.container.addCharacter(enemy,params["coordinate"][0]*15+random.randint(2,11),params["coordinate"][1]*15+random.randint(2,11))
            quest = src.quests.ClearTerrain()
            quest.autoSolve = True
            enemy.quests.append(quest)
            enemy.runCommandString("**")

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
            print("selected prefab")
            params["type"] = random.randint(1,len(self.prefabs["ScrapToMetalBars"]))
            print(params["type"])

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
            self.clearFieldFromMap({"coordinate":(params["coordinate"][0]+offset[0],params["coordinate"][1]+offset[1])})

            item = src.items.itemMap["AutoFarmer"]()
            self.container.container.addItem(item,((params["coordinate"][0]+offset[0])*15+7,(params["coordinate"][1]+offset[1])*15+7,0))

            for x in (2,4,10,12):
                for y in (2,4,10,12):
                    item = src.items.itemMap["MoldSpore"]()
                    self.container.container.addItem(item,((params["coordinate"][0]+offset[0])*15+x,(params["coordinate"][1]+offset[1])*15+y,0))
                    item.apply(params["character"],forceSpawn=forceSpawn)

        floorPlan = {}
        floorPlan["buildSites"] = []
        floorPlan["buildSites"].append([(4,5,0),"ScratchPlate", {"commands":{"noscratch":"jjaKsdJsJs"},"settings":{"scratchThreashold":1000}}])

        item = src.items.itemMap["Command"]()
        item.command = "15dj13wj13aj13aj13sj13sj13dj13dj13wj13adja"
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
        self.workshopRooms.append(room)
        return room

    def addTrapRoomFromMap(self,params):
        room = self.addRoom(params["coordinate"],roomType="TrapRoom")
        room.faction = params["character"].faction
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
            otherRoom.sources.insert(0,(pos,"CrystalCompressor"))

        if instaSpawn:
            room.spawnPlaned()
            room.spawnPlaned()
            room.addRandomItems()
        return room

    def addRoomFromMap(self,params):
        """
        handle a character having selected building a room
        and adding a task to the items task list

        Parameters:
            params: parameters given from the interaction menu
        """

        self.addRoom(params["coordinate"])

    def showMap(self, character):
        """
        handle a character trying to view the map of the city
        (the map shows what this item thinks is true not actual truth)

        Parameters:
            character: the character to show the map to
        """

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

        for room in self.rooms:
            mapContent[room.yPosition][room.xPosition] = room.displayChar

        functionMap = {}

        for x in range(1,14):
            for y in range(1,14):
                functionMap[(x,y)] = {}
                functionMap[(x,y)]["r"] = {
                    "function": {
                        "container":self,
                        "method":"addRoomFromMap",
                        "params":{"character":character},
                    },
                    "description":"add room",
                }
                functionMap[(x,y)]["c"] = {
                    "function": {
                        "container":self,
                        "method":"addScrapCompactorFromMap",
                        "params":{"character":character,"type":"random"},
                    },
                    "description":"add random scrapcompactor room",
                }
                functionMap[(x,y)]["C"] = {
                    "function": {
                        "container":self,
                        "method":"addScrapCompactorFromMap",
                        "params":{"character":character},
                    },
                    "description":"add scrapcompactor prefab",
                }
                functionMap[(x,y)]["e"] = {
                    "function": {
                        "container":self,
                        "method":"addEnemyRoomFromMap",
                        "params":{"character":character,"type":"random"},
                    },
                    "description":"add enemy room",
                }
                functionMap[(x,y)]["E"] = {
                    "function": {
                        "container":self,
                        "method":"addActiveEnemies",
                        "params":{"character":character,"type":"random"},
                    },
                    "description":"add active enemies",
                }
                functionMap[(x,y)]["W"] = {
                    "function": {
                        "container":self,
                        "method":"addWorkshopRoomFromMap",
                        "params":{"character":character,"type":"random"},
                    },
                    "description":"add workshopp room",
                }
                functionMap[(x,y)]["t"] = {
                    "function": {
                        "container":self,
                        "method":"addTrapRoomFromMap",
                        "params":{"character":character,"type":"random"},
                    },
                    "description":"add trap room",
                }
                functionMap[(x,y)]["T"] = {
                    "function": {
                        "container":self,
                        "method":"addTeleporterRoomFromMap",
                        "params":{"character":character,"type":"random"},
                    },
                    "description":"add teleporter room",
                }
                functionMap[(x,y)]["S"] = {
                    "function": {
                        "container":self,
                        "method":"addStorageRoomFromMap",
                        "params":{"character":character,"type":"random"},
                    },
                    "description":"add storage room",
                }
                functionMap[(x,y)]["y"] = {
                    "function": {
                        "container":self,
                        "method":"setConnectionsFromMap",
                        "params":{"character":character},
                    },
                    "description":"set connections",
                }
                functionMap[(x,y)]["A"] = {
                    "function": {
                        "container":self,
                        "method":"magicAdvanceRoomFromMap",
                        "params":{"character":character},
                    },
                    "description":"magic advance room",
                }
                functionMap[(x,y)]["f"] = {
                    "function": {
                        "container":self,
                        "method":"addFarmFromMap",
                        "params":{"character":character},
                    },
                    "description":"add farm",
                }
                functionMap[(x,y)]["D"] = {
                    "function": {
                        "container":self,
                        "method":"clearFieldFromMap",
                        "params":{"character":character},
                    },
                    "description":"clear field",
                }
                functionMap[(x,y)]["o"] = {
                    "function": {
                        "container":self,
                        "method":"addScrapFieldFromMap",
                        "params":{"character":character},
                    },
                    "description":"add scrap field",
                }
                functionMap[(x,y)]["m"] = {
                    "function": {
                        "container":self,
                        "method":"addMinefieldFromMap",
                        "params":{"character":character},
                    },
                    "description":"add mine field",
                }


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

        plot = (self.container.xPosition,self.container.yPosition)
        mapContent[plot[1]][plot[0]] = "CB"

        extraText = "\n\n"
        for task in reversed(self.tasks):
            extraText += "%s\n"%(task,)

        self.submenue = src.interaction.MapMenu(mapContent=mapContent,functionMap=functionMap, extraText=extraText)
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

        room.doBasicSetup()
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

src.items.addType(CityBuilder2)
