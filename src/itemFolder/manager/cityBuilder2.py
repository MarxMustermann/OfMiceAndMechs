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

        self.prefabs = {"ScrapToMetalBars":[]}

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

        scrapToMetalBarsPrefabPaths = ["scrapToMetalbars1.json","scrapToMetalbars2.json"]
        for path in scrapToMetalBarsPrefabPaths:
            with open("data/floorPlans/"+path) as fileHandle:
                rawFloorplan = json.load(fileHandle)    
            floorPlan = self.getFloorPlanFromDict(rawFloorplan)
            print(floorPlan)
            self.prefabs["ScrapToMetalBars"].append(floorPlan)

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

    def apply(self,character):
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
                command = src.items.itemMap["Command"]()
                command.bolted = True
                command.command = "a5w"+"4s4aJwJsddJwJsddww4aJwddJwddww"+"5sd"
                command.extraName = "produce items southwest"
                room.addItem(command,(7,11,0))
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
                command = src.items.itemMap["Command"]()
                command.bolted = True
                command.command = "aa5w"+"wwddJwJsddJwJs4aww2dJwddJw4a4s"+"5sdd"
                command.extraName = "produce items northeast"
                room.addItem(command,(8,11,0))
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
                command = src.items.itemMap["Command"]()
                command.bolted = True
                command.extraName = "produce items northwest"
                command.command = "aaa5w"+"ww4aJwJsddJwJsddww4aJwddJwdd4s"+"5sddd"
                room.addItem(command,(9,11,0))
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
