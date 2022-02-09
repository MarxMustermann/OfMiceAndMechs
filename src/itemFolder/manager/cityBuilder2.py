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
        self.cityLeader = None

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
                                                                ("spawnRank6", "spawn rank 6"),
                                                                ("spawnRank5", "spawn rank 5"),
                                                                ("spawnRank4", "spawn rank 4"),
                                                                ("spawnRank3", "spawn rank 3"),
                                                                ("spawnMilitary", "spawn military"),
                                                                ("spawnRankUnranked", "spawn unranked"),
                                                                ("addProductionLine", "add production line"),
                        ]
                        )
        self.applyMap = {
                    "showMap": self.showMap,
                    "spawnRank6": self.spawnRank6,
                    "spawnRank5": self.spawnRank5,
                    "spawnRank4": self.spawnRank4,
                    "spawnRank3": self.spawnRank3,
                    "spawnRankUnranked": self.spawnRankUnranked,
                    "addProductionLine": self.addProductionLine,
                    "spawnMilitary": self.spawnMilitary,
                        }

    def addRoom(self,position,addEnemyRoom=True,roomType="EmptyRoom"):
        room = self.architect.doAddRoom(
            {
                "coordinate": position,
                "roomType": roomType,
                "doors": "6,0 0,6 6,12 12,6",
                "offset": [1,1],
                "size": [13, 13],
            },
            None,
        )

        for item in self.scrapFields:
            room.sources.append((item,"Scrap"))

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

    def spawnRank6(self,character):
        self.spawnRank(6,character)
    def spawnRank5(self,character):
        self.spawnRank(5,character)
    def spawnRank4(self,character):
        self.spawnRank(4,character)
    def spawnRank3(self,character):
        self.spawnRank(3,character)
    def spawnRankUnranked(self,character):
        self.spawnRank(None,character)
    def spawnMilitary(self,character):
        self.spawnRank(None,character,isMilitary=True)

    def addProductionLine(self,character):
        if not self.workshopRooms:
            character.addMessage("no workshop rooms available")
            return
        character.addMessage("trying to add production line")
        room = self.workshopRooms.pop()
        items = ["Rod","Sword","Armor","Sheet","Bolt","Rod","Sword","Armor","Rod"]
        self.addWorkshop(items,[],room)
        for item in items:
            for otherRoom in self.container.container.rooms:
                otherRoom.sources.append((room.getPosition(),item))

    def spawnRank(self,rank,actor,isMilitary=False):
        if not rank == 3:
            if not self.cityLeader:
                actor.addMessage("no rank 3 to hook into")
                return

        char = src.characters.Character()
        char.registers["HOMEx"] = self.container.xPosition
        char.registers["HOMEy"] = self.container.yPosition
        char.isMilitary = isMilitary
        char.personality["abortMacrosOnAttack"] = False

        if rank == 3:
            if not self.cityLeader or self.cityLeader.dead:
                self.cityLeader = char
        if rank == 4:
            self.cityLeader.subordinates.append(char)

        quest = src.quests.BeUsefull()
        quest.assignToCharacter(char)
        quest.activate()
        char.quests.append(quest)
        char.faction = actor.faction
        if rank:
            char.rank = rank
        self.container.addCharacter(char,5,6)
        char.runCommandString("********")
        char.godMode = True

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

    def addScrapCompactorFromMap(self,params):
        """
        handle a character having selected building a room
        and adding a task to the items task list

        Parameters:
            params: parameters given from the interaction menu
        """

        character = params["character"]

        if not "type" in params:
            params["type"] = "random"
            character.addMessage("spawned submenu")
            character.addMessage(params)
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

        #room.spawnPlaned()
        #room.spawnPlaned()
        #room.addRandomItems()
        #room.spawnGhuls(character)

        self.container.sources.append((room.getPosition(),"MetalBars"))

    def addWorkshopRoomFromMap(self,params):
        room = self.addRoom(params["coordinate"],roomType="WorkshopRoom")
        self.workshopRooms.append(room)

    def addTrapRoomFromMap(self,params):
        room = self.addRoom(params["coordinate"],roomType="TrapRoom")

    def addTeleporterRoomFromMap(self,params):
        room = self.addRoom(params["coordinate"],roomType="TeleporterRoom")

    def addStorageRoomFromMap(self,params):
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

        for otherRoom in self.container.container.rooms:
            pos = room.getPosition()
            otherRoom.sources.insert(0,(pos,"Corpse"))
            otherRoom.sources.insert(0,(pos,"Frame"))
            otherRoom.sources.insert(0,(pos,"ScrapCompactor"))
            otherRoom.sources.insert(0,(pos,"Rod"))
            otherRoom.sources.insert(0,(pos,"Armor"))
            otherRoom.sources.insert(0,(pos,"MetalBars"))
            otherRoom.sources.insert(0,(pos,"Sword"))
            otherRoom.sources.insert(0,(pos,"Painter"))

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

        functionMap = {}

        for x in range(1,12):
            for y in range(1,12):
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


    def configure(self,character):

        prefabsToPlace = ["ScrapToMetalBars","ScrapToMetalBars"]
        for room in self.container.emptyRooms:
            if not prefabsToPlace:
                continue
            prefabType = prefabsToPlace.pop()
            valid = True
            for i in range(0,5):
                floorPlan = copy.deepcopy(random.choice(self.prefabs[prefabType]))
                conditions = floorPlan.get("conditions")

                valid = True
                if conditions:
                    for condition in conditions:
                        if "no doors" in condition:
                            for pos in condition["no doors"]:
                                if room.getPositionWalkable(pos):
                                    valid = False
                                break
                        if not valid:
                            break
                if valid:
                    break

            if not valid:
                floorPlan = copy.deepcopy(self.prefabs[prefabType][0])

            room.resetDirect()
            room.floorPlan = floorPlan 
            room.spawnPlaned()
            room.spawnPlaned()
            room.addRandomItems()
            room.spawnGhuls(character)
        return

        for room in self.container.storageRooms:
            room.doBasicSetup()
            room.addStorageSquare((0,0,0))
            room.addStorageSquare((6,0,0))
            room.addStorageSquare((0,6,0))
            room.addStorageSquare((6,6,0))

            for i in range(0,10):
                painter = src.items.itemMap["Painter"]()
                room.addItem(painter,(1,1,0))

            for otherRoom in self.container.rooms:
                pos = room.getPosition()
                otherRoom.sources.insert(0,(pos,"Corpse"))
                otherRoom.sources.insert(0,(pos,"Frame"))
                otherRoom.sources.insert(0,(pos,"ScrapCompactor"))
                otherRoom.sources.insert(0,(pos,"Rod"))
                otherRoom.sources.insert(0,(pos,"Armor"))
                otherRoom.sources.insert(0,(pos,"MetalBars"))
                otherRoom.sources.insert(0,(pos,"Sword"))
                otherRoom.sources.insert(0,(pos,"Painter"))


        smallMachinesToAdd = []

        smallMachinesToAdd.extend(["Armor","Armor","Armor"])
        smallMachinesToAdd.extend(["Sword","Sword","Sword"])
        smallMachinesToAdd.extend(["Rod","Rod","Rod"])

        smallMachinesToAdd.extend(["Painter","Connector","Case"])
        smallMachinesToAdd.extend(["Frame","puller","pusher"])
        smallMachinesToAdd.extend(["Heater","Tank","Rod"])

        smallMachinesToAdd.extend(["ScrapCompactor","ScrapCompactor","ScrapCompactor"])
        smallMachinesToAdd.extend(["CorpseAnimator","CommandCycler"])


        bigMachinesToAdd = ["Wall","Wall"]

        for room in self.container.workshopRooms:
            room.resetDirect()
            room.doBasicSetup()

            if not smallMachinesToAdd and not bigMachinesToAdd:
                break

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


            room.spawnPlaned()
            room.spawnPlaned()
            room.addRandomItems()
            room.spawnGhuls(character)

            pos = room.getPosition()
            for machine in newOutputs:
                for otherRoom in self.container.rooms:
                    otherRoom.sources.append((pos,machine))

src.items.addType(CityBuilder2)
