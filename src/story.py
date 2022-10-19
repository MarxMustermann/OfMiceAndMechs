"""
story code and story related code belongs here
most thing should be abstracted and converted to a game mechanism later

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
most of this code is currenty not in use and needs to be reintegrated
"""

import src.saveing
import src.rooms
import src.canvas
import src.cinematics
import src.chats
import src.quests
import src.items
import src.interaction
import src.events
import config
import src.gamestate

import random
import requests
import json
import copy

phasesByName = None

#####################################
#
#    convenience functions
#
#####################################

def showMessage(message, trigger=None):
    """
    helper to add message cinematic

    Parameters:
        message: the message to add
        trigger: function that should be called after showing the message
    """

    cinematic = src.cinematics.ShowMessageCinematic(message)
    src.cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger

def showGame(duration, trigger=None):
    """
    helper to add show game cinematic

    Parameters:
        duration: how long the game should be shown
        trigger: function that should be called after showing the game
    """

    cinematic = src.cinematics.ShowGameCinematic(duration, tickSpan=1)
    src.cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger


def showQuest(quest, assignTo=None, trigger=None, container=None):
    """
    helper to add show quest cinematic

    Parameters:
        quest: the quest to add
        assignTo: he character to assign the quest to
        trigger: function that should be called after showing the game
        container: quest to add the quest as subquest to
    """

    cinematic = src.cinematics.ShowQuestExecution(
        quest, tickSpan=1, assignTo=assignTo, container=container
    )
    src.cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger


def showText(text, rusty=False, autocontinue=False, trigger=None, scrolling=False):
    """
    helper to add text cinematic

    Parameters:
        text: the text to show
    """

    cinematic = src.cinematics.TextCinematic(
        text, rusty=rusty, autocontinue=autocontinue, scrolling=scrolling
    )
    src.cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger

def say(text, speaker=None, trigger=None):
    """
    add message cinematic mimicing speech

    Parameters:
        speaker: the character that should be shown as speaking
        trigger: function that should be called after showing the game
    """

    prefix = ""
    if speaker:
        # add speakers icon as prefix
        display = speaker.display
        if isinstance(display, str):
            prefix = display
        elif isinstance(display, int):
            display = src.canvas.displayChars.indexedMapping[speaker.display]
            if isinstance(display, str):
                prefix = display
            else:
                prefix = display[1]
        else:
            prefix = display[1]
        prefix += ": "

    # add message
    showMessage(prefix + '"' + text + '"', trigger=trigger)

class WorldBuildingPhase(src.saveing.Saveable):
    """
    Phase for a new world building phase
    """

    def __init__(self, name="worldbuilding", seed=0):
        """
        initialise own state

        Parameters:
            name: the name of the phase
            seed: rng seed
        """

        super().__init__()

        self.name = name
        self.seed = seed

        # register with dummy id
        self.id = name

        self.attributesToStore.append("name")

    def start(self, seed=0, difficulty=None):
        newRoom = src.rooms.DungeonRoom()
        newRoom.addCharacter(src.gamestate.gamestate.mainChar,7,7)
        src.gamestate.gamestate.extraRoots.append(newRoom)
        pass

    def end(self):
        pass

#########################################################################
#
#     building block phases
#
#########################################################################

class BasicPhase(src.saveing.Saveable):
    """
    the base class for the all phases
    """

    # bad code: creating default attributes in init and set them externally later
    def __init__(self, name, seed=0):
        """
        initialise own state

        Parameters:
            name: the name of the phase
            seed: rng seed
        """
        self.callbacksToStore = []
        self.objectsToStore = []
        self.tupleDictsToStore = []
        self.tupleListsToStore = []


        super().__init__()
        self.name = name
        self.seed = seed

        # register with dummy id
        self.id = name

        self.attributesToStore.append("name")
        self.attributesToStore.append("seed")

    def start(self, seed=0, difficulty=None):
        """
        set up and start to run this game phase
        """

        # set state
        src.gamestate.gamestate.currentPhase = self
        self.tick = src.gamestate.gamestate.tick
        self.seed = seed

    def end(self):
        """
        do nothing when done
        """

        pass

#########################################################################
#
#     phases with actual usage
#
#########################################################################

# obsolete: not really used anymore
class Challenge(BasicPhase):
    """
    gamemode for solving escape rooms 
    """

    def __init__(self, seed=0):
        """
        configure super class

        Parameters:
            seed: rng seed
        """

        super().__init__("challenge", seed=seed)

    # bad code: superclass call should not be prevented
    def start(self, seed=0, difficulty=None):
        """
        start running the phase by placing the main char

        Parameters:
            seed: rng seed
        """

        showText("escape the room. Your seed is: %s" % (seed))
        self.roomCounter = 0
        self.seed = seed
        self.restart()

    def restart(self):
        """
        reset the challenge on completion
        """

        self.seed = ((self.seed % 317) + (self.seed // 317)) * 321 + self.seed % 300
        challengeRoom = src.gamestate.gamestate.terrain.challengeRooms[self.roomCounter]
        if src.gamestate.gamestate.mainChar.room:
            src.gamestate.gamestate.mainChar.room.removeCharacter(
                src.gamestate.gamestate.mainChar
            )
            src.gamestate.gamestate.mainChar.room = None
        if src.gamestate.gamestate.mainChar.terrain:
            src.gamestate.gamestate.mainChar.terrain.removeCharacter(
                src.gamestate.gamestate.mainChar
            )
            src.gamestate.gamestate.mainChar.terrain = None
        mainCharRoom = challengeRoom
        mainCharRoom.addCharacter(src.gamestate.gamestate.mainChar, 4, 4)

        if self.roomCounter == 1:
            showText("resetting. escape the room. again")
        if self.roomCounter > 1:
            showText("roomrun count: " + str(self.roomCounter))

        src.gamestate.gamestate.mainChar.inventory = []
        counter = 0
        while counter < 10:
            if (self.seed + counter) % 2 == 0:
                item = src.items.itemMap["Coal"](None, None, creator=self)
                src.gamestate.gamestate.mainChar.inventory.append(item)
                counter += 1
                continue
            if (self.seed + counter) % 5 == 0:
                item = src.items.itemMap["Wall"](None, None, creator=self)
                src.gamestate.gamestate.mainChar.inventory.append(item)
                counter += 1
                continue
            if (self.seed + counter) % 3 == 0:
                item = src.items.itemMap["Coal"](None, None, creator=self)
                src.gamestate.gamestate.mainChar.inventory.append(item)
                counter += 1
                continue
            if (self.seed + counter) % 7 == 0:
                item = src.items.itemMap["Pipe"](None, None, creator=self)
                src.gamestate.gamestate.mainChar.inventory.append(item)
                counter += 1
                continue
            if (self.seed + counter) % 13 == 0:
                item = src.items.itemMap["GooFlask"](None, None, creator=self)
                item.charges = 1
                src.gamestate.gamestate.mainChar.inventory.append(item)
                counter += 1
                continue
            counter += 1

        src.gamestate.gamestate.mainChar.satiation = 30 + self.seed % 900
        src.gamestate.gamestate.mainChar.reputation = (self.seed + 12) % 200

        src.gamestate.gamestate.mainChar.questsDone = []
        src.gamestate.gamestate.mainChar.solvers = []
        for quest in src.gamestate.gamestate.mainChar.quests:
            quest.done = True
            quest.completed = True
        src.gamestate.gamestate.mainChar.quests = []

        quest = src.quests.LeaveRoomQuest(challengeRoom)
        quest.endTrigger = {"container": self, "method": "restart"}
        quest.failTrigger = {"container": self, "method": "fail"}
        src.gamestate.gamestate.mainChar.serveQuest = quest
        src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)

        self.roomCounter += 1

    def win(self):
        """
        handle a player win
        """

        showText("you won the challenge")

    def fail(self):
        """
        handle a player loose
        """

        print("you lost the challenge (winning is not always possible)")

class OpenWorld(BasicPhase):
    """
    the phase is intended to give the player access to the true gameworld without manipulations

    this phase should be left as blank as possible
    """

    def __init__(self, seed=0):
        """
        set up super class
        """
        super().__init__("OpenWorld", seed=seed)

    # bad code: superclass call should not be prevented
    def start(self, seed=0, difficulty=None):
        """
        start phase by placing main char
        """

        src.cinematics.showCinematic("staring open world Scenario.")

        src.gamestate.gamestate.mainChar.xPosition = 65
        src.gamestate.gamestate.mainChar.yPosition = 111
        src.gamestate.gamestate.mainChar.reputation = 100
        src.gamestate.gamestate.mainChar.terrain = src.gamestate.gamestate.terrain
        src.gamestate.gamestate.terrain.addCharacter(
            src.gamestate.gamestate.mainChar, 65, 111
        )

        # npc1 = characters.Character(xPosition=4,yPosition=3,creator=void,seed=src.gamestate.gamestate.tick+2)
        # npc1.xPosition = 10
        # npc1.yPosition = 10
        # npc1.terrain = src.gamestate.gamestate.terrain
        # src.gamestate.gamestate.terrain.addCharacter(npc1,10,10)

        # add basic set of abilities in openworld phase
        src.gamestate.gamestate.mainChar.questsDone = [
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "CollectQuestMeta",
            "FireFurnaceMeta",
            "ExamineQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
            "LeaveRoomQuest",
        ]

        src.gamestate.gamestate.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

        # npc1.solvers = [
        #          "SurviveQuest",
        #          "Serve",
        #          "NaiveMoveQuest",
        #          "MoveQuestMeta",
        #          "NaiveActivateQuest",
        #          "ActivateQuestMeta",
        #          "NaivePickupQuest",
        #          "PickupQuestMeta",
        #          "DrinkQuest",
        #          "ExamineQuest",
        #          "FireFurnaceMeta",
        #          "CollectQuestMeta",
        #          "WaitQuest"
        #          "NaiveDropQuest",
        #          "NaiveDropQuest",
        #          "DropQuestMeta",
        #        ]

class Dungeon(BasicPhase):
    """
    game mode ment to offer dungeon crawling
    """

    def __init__(self, seed=0):
        """
        set up super class

        Parameters:
            seed: rng seed
        """
        super().__init__("Dungeon", seed=seed)

    def start(self, seed=0, difficulty=None):
        """
        place main char and add entry point to dungeon

        Parameters:
            seed: rng seed
        """

        src.cinematics.showCinematic("staring open world Scenario.")

        src.gamestate.gamestate.mainChar.xPosition = 65
        src.gamestate.gamestate.mainChar.yPosition = 111
        src.gamestate.gamestate.mainChar.terrain = src.gamestate.gamestate.terrain
        src.gamestate.gamestate.terrain.addCharacter(
            src.gamestate.gamestate.mainChar, 65, 111
        )

        item = src.items.itemMap["RipInReality"]()
        src.gamestate.gamestate.terrain.addItem(item,(67, 113, 0))

        # add basic set of abilities in openworld phase
        src.gamestate.gamestate.mainChar.questsDone = [
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "CollectQuestMeta",
            "FireFurnaceMeta",
            "ExamineQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
            "LeaveRoomQuest",
        ]

        src.gamestate.gamestate.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest",
            "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

class PrefabDesign(BasicPhase):

    def __init__(self, seed=0):
        super().__init__("PrefabDesign", seed=seed)

        self.stats = {}
        self.floorPlan = None

    def advance(self):
        print("advance story")
        self.askAction()
        return

    def runFloorplanGeneration(self):
        self.floorPlan = self.generateFloorPlan()
        self.saveFloorPlan(self.floorPlan)
        self.spawnRooms(self.floorPlan)
        return

    def addFloorPlan(self):
        if not self.floorPlan:
            return

        converted = self.convertFloorPlanToDict(self.floorPlan)

        try:
            # register the save
            with open("gamestate/globalInfo.json", "r") as globalInfoFile:
                rawState = json.loads(globalInfoFile.read())
        except:
            rawState = {"saves": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],"customPrefabs":[]}

        rawState["customPrefabs"].append(converted)

        with open("gamestate/globalInfo.json", "w") as globalInfoFile:
            json.dump(rawState,globalInfoFile)

        submenu = src.interaction.TextMenu("""
the floorplan is available in basebuilder mode and main game now""")

    def askAction(self):
        options = [("generateFloorPlan", "generate floor plan"), ("simulateUsage", "simulate usage"), ("submitFloorPlan", "submit floor plan"), ("addFloorPlan", "add floor plan to loadable prefabs"),("donateFloorPlan", "donate floor plan")]
        submenu = src.interaction.SelectionMenu(
            "what do you want to do?", options,
        )
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.macroState["submenue"].followUp = {
            "container": self,
            "method": "runAction",
            "params": {}
        }

    def runAction(self,extraParams):
        if not "selection" in extraParams:
            return

        if extraParams["selection"] == "generateFloorPlan":
            self.runFloorplanGeneration()
        if extraParams["selection"] == "simulateUsage":
            self.simulateUsage()
        if extraParams["selection"] == "addFloorPlan":
            self.addFloorPlan()
        if extraParams["selection"] == "donateFloorPlan":
            self.donateFloorPlan()
        print("run action")
        print(extraParams)

    def donateFloorPlan(self):
        options = [("yes", "Yes"), ("no", "No")]
        submenu = src.interaction.SelectionMenu(
            "Do you want to donate the room?\n\nSelect \"Yes\" to make the rooms design public domain and upload the room.\nThis will require an internet connection", options,
            targetParamName="upload",
        )
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.macroState["submenue"].followUp = {
            "container": self,
            "method": "uploadFloorPlan",
            "params": {}
        }

    def uploadFloorPlan(self,extraParams):
        if not self.floorPlan:
            return
        if extraParams["upload"] == "yes":
            converted = self.convertFloorPlanToDict(self.floorPlan)
            requests.post("http://ofmiceandmechs.com/floorPlanDump.php",{"floorPlan":json.dumps(converted)})

    def generateFloorPlan(self):
        import copy
        floorPlan = {}
        floorPlan["buildSites"] = []
        floorPlan["inputSlots"] = self.toBuildRoom.inputSlots[:]
        floorPlan["outputSlots"] = self.toBuildRoom.outputSlots[:]
        floorPlan["storageSlots"] = self.toBuildRoom.storageSlots[:]
        floorPlan["walkingSpace"] = copy.deepcopy(self.toBuildRoom.walkingSpace)

        toDelete = []
        for item in self.toBuildRoom.itemsOnFloor:
            pos = item.getPosition()
            if pos[0] == 0 or pos[0] == 12 or pos[1] == 0 or pos[1] == 12:
                continue
            extraInfos = {}
            if item.type == "Scrap":
                floorPlan["inputSlots"].append((pos,item.type,{}))
                continue
            if item.type == "Corpse":
                floorPlan["inputSlots"].append((pos,item.type,{"maxAmount":2}))
                continue
            if item.type == "MetalBars":
                floorPlan["outputSlots"].append((pos,item.type,{}))
                continue
            if item.type == "ScrapCompactor":
                floorPlan["outputSlots"].append(((pos[0]+1,pos[1],pos[2]),"MetalBars",{}))
                floorPlan["inputSlots"].append(((pos[0]-1,pos[1],pos[2]),"Scrap",{}))
            if item.type == "Command":
                extraInfos["command"] = item.command
                floorPlan["walkingSpace"].add(item.getPosition())
            floorPlan["buildSites"].append((pos,item.type,extraInfos))

        blockedPositions = []
        for x in range(0,13):
            for y in (0,12):
                blockedPositions.append((x,y,0))
        for y in range(0,13):
            for x in (0,12):
                blockedPositions.append((x,y,0))

        placedScrapCompactor = False
        placedCorpseAnimator = False
        placedScratchPlate = False
        scrapCompactorPositions = []
        corpseAnimatorPositions = []
        corpseStockpilePositions = []
        scratchPlatePositions = []
        scratchPlate = None
        commandPositions = []
        for buildSite in floorPlan["buildSites"]:
            if buildSite[1] == "ScrapCompactor":
                placedScrapCompactor = True
                scrapCompactorPositions.append(buildSite[0])
            if buildSite[1] == "CorpseAnimator":
                placedCorpseAnimator = True
                corpseAnimatorPositions.append(buildSite[0])
            if buildSite[1] == "Command":
                commandPositions.append(buildSite[0])
                continue
            if buildSite[1] == "ScratchPlate":
                placedScratchPlate = True
                scratchPlatePositions.append(buildSite[0])
                scratchPlate = buildSite
                continue
            blockedPositions.append(buildSite[0])
        for inputSlot in floorPlan["inputSlots"]:
            if inputSlot[1] == "Corpse":
                corpseStockpilePositions.append(inputSlot[0])
            blockedPositions.append(inputSlot[0])
        for outputSlot in floorPlan["outputSlots"]:
            blockedPositions.append(outputSlot[0])
        for storageSlot in floorPlan["storageSlots"]:
            blockedPositions.append(storageSlot[0])

        import copy
        if self.toBuildRoomClone3:
            self.toBuildRoomClone3.container.removeRoom(self.toBuildRoomClone3)
        self.toBuildRoomClone3 = self.architect.doAddRoom(
            {
                "coordinate": (6,6),
                "roomType": "EmptyRoom",
                "doors": "0,6 12,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )

        for pos in blockedPositions:
            self.toBuildRoomClone3.addItem(src.items.itemMap["Wall"](),pos)

        # add a scrap compactor
        if not placedScrapCompactor:
            pos = (random.randint(1,12),random.randint(1,12),0)
            if pos in blockedPositions or (pos[0]+1,pos[1],pos[2]) in blockedPositions or (pos[0]-1,pos[1],pos[2]) in blockedPositions or (pos[0],pos[1]-1,pos[2]) in blockedPositions:
                for x in range(1,12):
                    for y in range(1,12):
                        pos = (x,y,0)
                        if pos in blockedPositions or (pos[0]+1,pos[1],pos[2]) in blockedPositions or (pos[0]-1,pos[1],pos[2]) in blockedPositions or (pos[0],pos[1]-1,pos[2]) in blockedPositions:
                            pos = None
                        if pos:
                            break
                    if pos:
                        break

            if pos == None:
                src.gamestate.gamestate.mainChar.addMessage("no room to place scrap compactor")
                return

            floorPlan["outputSlots"].append(((pos[0]+1,pos[1],pos[2]),"MetalBars",{}))
            floorPlan["inputSlots"].append(((pos[0]-1,pos[1],pos[2]),"Scrap",{}))
            floorPlan["buildSites"].append((pos,"ScrapCompactor",{}))

            self.toBuildRoomClone3.addItem(src.items.itemMap["Wall"](),(pos[0]+1,pos[1],pos[2]))
            self.toBuildRoomClone3.addItem(src.items.itemMap["Wall"](),(pos[0]-1,pos[1],pos[2]))
            self.toBuildRoomClone3.addItem(src.items.itemMap["Wall"](),pos)

            blockedPositions.append((pos[0]+1,pos[1],pos[2]))
            blockedPositions.append((pos[0]-1,pos[1],pos[2]))
            blockedPositions.append((pos[0],pos[1]-1,pos[2]))
            blockedPositions.append(pos)

            scrapCompactorPositions.append(pos)

        # add a corpse animator
        if not placedCorpseAnimator:
            pos = (random.randint(1,12),random.randint(1,12),0)
            if pos in blockedPositions or (pos[0]+1,pos[1],pos[2]) in blockedPositions:
                for x in range(1,12):
                    for y in range(1,12):
                        pos = (x,y,0)
                        if pos in blockedPositions or (pos[0]+1,pos[1],pos[2]) in blockedPositions:
                            pos = None
                        if pos:
                            break
                    if pos:
                        break

            if pos == None:
                src.gamestate.gamestate.mainChar.addMessage("no room to place corpse animator")
                return

            floorPlan["buildSites"].append((pos,"CorpseAnimator",{}))
            self.toBuildRoomClone3.addItem(src.items.itemMap["Wall"](),pos)

            blockedPositions.append(pos)
            blockedPositions.append((pos[0]+1,pos[1],pos[2]))

            corpseAnimatorPositions.append(pos)

        if not corpseStockpilePositions:
            pos = (random.randint(1,12),random.randint(1,12),0)
            if pos in blockedPositions or (pos[0],pos[1]-1,pos[2]) in blockedPositions:
                for x in range(1,12):
                    for y in range(1,12):
                        pos = (x,y,0)
                        if pos in blockedPositions or (pos[0],pos[1]-1,pos[2]) in blockedPositions:
                            pos = None
                        if pos:
                            break
                    if pos:
                        break


            if pos == None:
                src.gamestate.gamestate.mainChar.addMessage("no room to place corpse stockpile")
                return

            floorPlan["inputSlots"].append((pos,"Corpse",{"maxAmount":2}))
            corpseStockpilePositions.append(pos)
            self.toBuildRoomClone3.addItem(src.items.itemMap["Wall"](),pos)

            blockedPositions.append(pos)

        if not scratchPlatePositions:
            pos = (random.randint(1,12),random.randint(1,12),0)
            if pos in blockedPositions:
                for x in range(1,12):
                    for y in range(1,12):
                        pos = (x,y,0)
                        if pos in blockedPositions or (pos[0],pos[1]-1,pos[2]) in blockedPositions:
                            pos = None
                        if pos:
                            break
                    if pos:
                        break


            if pos == None:
                src.gamestate.gamestate.mainChar.addMessage("no room to place scratch plate")
                return

            scratchPlatePositions.append(pos)

            placedScratchPlate = True
            blockedPositions.append(pos)

            buildSite = (pos,"ScratchPlate",{})
            floorPlan["buildSites"].append(buildSite)
            scratchPlate = buildSite

        if not "commands" in scratchPlate[2]:
            feedingPos = (corpseStockpilePositions[0][0],corpseStockpilePositions[0][1]-1,corpseStockpilePositions[0][2])
            scratchPlatePos = (scratchPlatePositions[0][0],scratchPlatePositions[0][1],scratchPlatePositions[0][2])
            corpseAnimatorPos = (corpseAnimatorPositions[0][0]+1,corpseAnimatorPositions[0][1],corpseAnimatorPositions[0][2])

            pathToFeeder = self.toBuildRoomClone3.getPathCommandTile(scratchPlatePos,feedingPos)[0]
            pathToAnimator = self.toBuildRoomClone3.getPathCommandTile(feedingPos,corpseAnimatorPos)[0]
            pathToStart = self.toBuildRoomClone3.getPathCommandTile(corpseAnimatorPos,scratchPlatePos)[0]
            scratchPlate[2]["commands"] = {"noscratch":"jj"+pathToFeeder+"Ks"+pathToAnimator+"JaJa"+pathToStart}

        if not "settings" in scratchPlate[2]:
            scratchPlate[2]["settings"] = {"scratchThreashold":1000}

        for corpseAnimatorPos in corpseAnimatorPositions:
            commandPos = (corpseAnimatorPos[0]+1,corpseAnimatorPos[1],corpseAnimatorPos[2])
            if not commandPos in commandPositions:
                command = ""
                lastPos = commandPos
                for compactorPos in scrapCompactorPositions:
                    #print("generating path for scrap compactor")
                    newPos = (compactorPos[0],compactorPos[1]-1,compactorPos[2])
                    (moveComand,path) = self.toBuildRoomClone3.getPathCommandTile(lastPos,newPos)
                    if path:
                        command += moveComand+"Js"
                        lastPos = newPos
                    else:
                        #print("generating path from north failed, try south")
                        newPos = (compactorPos[0],compactorPos[1]+1,compactorPos[2])
                        (moveComand,path) = self.toBuildRoomClone3.getPathCommandTile(lastPos,newPos)
                        if path:
                            command += moveComand+"Jw"
                            lastPos = newPos
                        else:
                            #print("generating path from north and south failed, giving up")
                            src.gamestate.gamestate.mainChar.addMessage("could not generate path to Scrap compactor on %s"%(compactorPos,))

                feedingPos = (corpseStockpilePositions[0][0],corpseStockpilePositions[0][1]-1,corpseStockpilePositions[0][2])
                scratchPlatePos = (scratchPlatePositions[0][0],scratchPlatePositions[0][1],scratchPlatePositions[0][2])

                pathToFeeder = self.toBuildRoomClone3.getPathCommandTile(lastPos,feedingPos)[0]
                pathToScratchPlate = self.toBuildRoomClone3.getPathCommandTile(feedingPos,scratchPlatePos)[0]
                pathToStart = self.toBuildRoomClone3.getPathCommandTile(scratchPlatePos,commandPos)[0]

                activateCommand = ((len(command)+len(pathToFeeder)+len(pathToScratchPlate)+len(pathToStart))//13+5)*"Js"

                command = command + pathToFeeder + activateCommand + pathToScratchPlate + "jj" + pathToStart + "j"

                floorPlan["buildSites"].append((commandPos,"Command",{"command":command}))
                blockedPositions.append(commandPos)

        if not floorPlan["buildSites"]:
            del floorPlan["buildSites"]

        for item in floorPlan["walkingSpace"]:
            if item[0] == 0 or item[0] == 12 or item[1] == 0 or item[1] == 12:
                toDelete.append(item)
        for item in toDelete:
            floorPlan["walkingSpace"].remove(item)

        for x in range(1,12):
            for y in range(1,12):
                pos = (x,y,0)
                fillIn = True
                if "inputSlots" in floorPlan:
                    for inputSlot in floorPlan["inputSlots"]:
                        if inputSlot[0] == pos:
                            fillIn = False
                if "outputSlots" in floorPlan:
                    for outputSlot in floorPlan["outputSlots"]:
                        if outputSlot[0] == pos:
                            fillIn = False
                if "storageSlots" in floorPlan:
                    for storageSlot in floorPlan["storageSlots"]:
                        if storageSlot[0] == pos:
                            fillIn = False
                if "buildSites" in floorPlan:
                    for buildSite in floorPlan["buildSites"]:
                        if buildSite[0] == pos:
                            fillIn = False
                if "walkingSpace" in floorPlan:
                    if pos in floorPlan["walkingSpace"]:
                        fillIn = False
                if fillIn:
                    floorPlan["walkingSpace"].add(pos)

        return floorPlan

    def saveFloorPlan(self,floorPlan):
        if not floorPlan:
            src.gamestate.gamestate.mainChar.addMessage("no floor plan generated")
            return
        converted = self.convertFloorPlanToDict(floorPlan)

        with open("floorPlan.json","w") as fileHandle:
            import json
            json.dump(converted,fileHandle,indent=4)

        self.stats["current"] = {}

    def spawnRooms(self, floorPlan):
        if self.toBuildRoomClone:
            self.toBuildRoomClone.container.removeRoom(self.toBuildRoomClone)
        self.toBuildRoomClone = self.architect.doAddRoom(
            {
                "coordinate": (7,6),
                "roomType": "EmptyRoom",
                "doors": "0,6 12,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        self.toBuildRoomClone.floorPlan = copy.deepcopy(floorPlan)
        self.toBuildRoomClone.spawnPlaned()
        self.toBuildRoomClone.spawnPlaned()
        self.toBuildRoomClone.addRandomItems()
        self.toBuildRoomClone.spawnGhuls(src.gamestate.gamestate.mainChar)

        return

    def simulateUsage(self):
        if not self.floorPlan:
            return

        floorPlan = self.floorPlan

        if self.toBuildRoomClone4:
            self.toBuildRoomClone4.container.removeRoom(self.toBuildRoomClone4)
        self.toBuildRoomClone4 = self.architect.doAddRoom(
            {
                "coordinate": (8,8),
                "roomType": "EmptyRoom",
                "doors": "0,6 12,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        self.toBuildRoomClone4.floorPlan = copy.deepcopy(floorPlan)
        self.toBuildRoomClone4.spawnPlaned()
        self.toBuildRoomClone4.spawnPlaned()
        self.toBuildRoomClone4.spawnGhuls(src.gamestate.gamestate.mainChar)

        self.spawnMaintanenceNPCs(self.toBuildRoomClone4)

        self.stats["current"]["1500"] = {"produced":0}

        for i in range(0,1500):
            self.toBuildRoomClone4.advance(advanceMacros=True)
            self.handleMaintanenceNPCs(self.toBuildRoomClone4)

        if self.toBuildRoomClone6:
            self.toBuildRoomClone6.container.removeRoom(self.toBuildRoomClone6)
        self.toBuildRoomClone6 = self.architect.doAddRoom(
            {
                "coordinate": (6,8),
                "roomType": "EmptyRoom",
                "doors": "0,6 12,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        self.toBuildRoomClone6.floorPlan = copy.deepcopy(floorPlan)
        self.toBuildRoomClone6.spawnPlaned()
        self.toBuildRoomClone6.spawnPlaned()
        self.toBuildRoomClone6.addRandomItems()
        self.toBuildRoomClone6.spawnGhuls(src.gamestate.gamestate.mainChar)

        self.spawnMaintanenceNPCs(self.toBuildRoomClone6)

        self.stats["current"]["15000"] = {"produced":0}

        for i in range(0,15000):
            self.toBuildRoomClone6.advance(advanceMacros=True)
            self.handleMaintanenceNPCs(self.toBuildRoomClone6)

        if self.toBuildRoomClone2:
            self.toBuildRoomClone2.container.removeRoom(self.toBuildRoomClone2)
        self.toBuildRoomClone2 = self.architect.doAddRoom(
            {
                "coordinate": (7,8),
                "roomType": "EmptyRoom",
                "doors": "0,6 12,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        self.toBuildRoomClone2.floorPlan = copy.deepcopy(floorPlan)
        self.toBuildRoomClone2.spawnPlaned()

        if self.toBuildRoomClone5:
            self.toBuildRoomClone5.container.removeRoom(self.toBuildRoomClone5)
        self.toBuildRoomClone5 = self.architect.doAddRoom(
            {
                "coordinate": (8,6),
                "roomType": "EmptyRoom",
                "doors": "0,6 12,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        self.toBuildRoomClone5.floorPlan = copy.deepcopy(floorPlan)
        self.toBuildRoomClone5.spawnPlaned()
        self.toBuildRoomClone5.spawnPlaned()
        self.toBuildRoomClone5.spawnGhuls(src.gamestate.gamestate.mainChar)
        
        self.spawnMaintanenceNPCs()
        self.maintananceLoop()

        ticksPerBar = 15000/self.stats["current"]["15000"]["produced"]
        submenu = src.interaction.TextMenu("""
your room produces a MetalBar every %s ticks on average."""%(ticksPerBar,))

        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

    def spawnMaintanenceNPCs(self,room=None):
        if not room:
            room = self.toBuildRoomClone5

        charCount = 0
        for character in room.characters:
            if isinstance(character,src.characters.Ghul):
                continue
            charCount += 1

        if charCount < 5:
            character = src.characters.Character(3,3)
            character.runCommandString("*********")
            room.addCharacter(character,0,6)
            for i in range(0,10):
                character.inventory.append(src.items.itemMap["Scrap"]())


            quest = src.quests.RestockRoom(targetPosition=(room.xPosition,room.yPosition,0),toRestock="Scrap")
            quest.activate()
            quest.assignToCharacter(character)
            character.quests.append(quest)
            quest = src.quests.GoToPosition(targetPosition=(0,6,0))
            quest.assignToCharacter(character)
            character.quests.append(quest)

        if charCount < 5:
            character = src.characters.Character(3,3)
            character.runCommandString("*********")
            room.addCharacter(character,0,6)
            for i in range(0,10):
                character.inventory.append(src.items.itemMap["Corpse"]())

            quest = src.quests.RestockRoom(targetPosition=(room.xPosition,room.yPosition,0),toRestock="Corpse")
            quest.activate()
            quest.assignToCharacter(character)
            character.quests.append(quest)
            quest = src.quests.GoToPosition(targetPosition=(0,6,0))
            quest.assignToCharacter(character)
            character.quests.append(quest)

        if charCount < 5:
            character = src.characters.Character(3,3)
            character.runCommandString("*********")
            room.addCharacter(character,0,6)

            quest = src.quests.FetchItems(targetPosition=(room.xPosition,room.yPosition,0),toCollect="MetalBars")
            quest.activate()
            quest.assignToCharacter(character)
            character.quests.append(quest)
            quest = src.quests.GoToPosition(targetPosition=(0,6,0))
            quest.assignToCharacter(character)
            character.quests.append(quest)

    def convertFloorPlanToDict(self,floorPlan):
        converted = {}
        if "buildSites" in floorPlan:
            buildSites = []
            for item in floorPlan["buildSites"]:
                buildSites.append([list(item[0]),item[1],item[2]])
            converted["buildSites"] = buildSites
        if "inputSlots" in floorPlan:
            inputSlots = []
            for item in floorPlan["inputSlots"]:
                inputSlots.append([list(item[0]),item[1],item[2]])
            converted["inputSlots"] = inputSlots
        if "outputSlots" in floorPlan:
            outputSlots = []
            for item in floorPlan["outputSlots"]:
                outputSlots.append([list(item[0]),item[1],item[2]])
            converted["outputSlots"] = outputSlots
        if "storageSlots" in floorPlan:
            outputSlots = []
            for item in floorPlan["storageSlots"]:
                outputSlots.append([list(item[0]),item[1],item[2]])
            converted["storageSlots"] = outputSlots
        if "walkingSpace" in floorPlan:
            walkingSpace = []
            for item in floorPlan["walkingSpace"]:
                walkingSpace.append(list(item))
            converted["walkingSpace"] = walkingSpace
        return converted

    def maintananceLoop(self):
        self.handleMaintanenceNPCs(self.toBuildRoomClone4)
        self.handleMaintanenceNPCs(self.toBuildRoomClone5)
        self.handleMaintanenceNPCs(self.toBuildRoomClone6)

        terrain = src.gamestate.gamestate.terrainMap[7][7]
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
        event.setCallback({"container": self, "method": "maintananceLoop"})
        terrain.addEvent(event)


    def handleMaintanenceNPCs(self, room=None):
        if room == None:
            room = self.toBuildRoomClone5

        for npc in room.characters[:]:
            if isinstance(npc,src.characters.Ghul):
                continue
            if len(npc.quests) > 1:
                continue
            if not npc.xPosition == 0 or not npc.yPosition == 6:
                continue

            if room == self.toBuildRoomClone4:
                for item in npc.inventory:
                    if not item.type == "MetalBars":
                        continue
                    try:
                        self.stats["current"]["1500"]["produced"] += 1
                    except:
                        pass
            if room == self.toBuildRoomClone6:
                for item in npc.inventory:
                    if not item.type == "MetalBars":
                        continue
                    try:
                        self.stats["current"]["15000"]["produced"] += 1
                    except:
                        pass
            room.removeCharacter(npc)
            npc.die()

        if room.timeIndex%15 == 0:
            self.spawnMaintanenceNPCs(room)

    def start(self,seed=None, difficulty=None):
        showText("""
Hello,

in this mode you can build rooms to use in other modes. Currently only rooms that process scrap into metal bars can be built.

Use the items to build a room in the center and use the "pc" item to see how well your room performs.

If your room performs well enough you can upload your room and maybe it will be included in the main game.

I hope you have fun.

-- press space to continue --
""")


        architect = src.items.itemMap["ArchitectArtwork"]()
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addItem(architect,(124, 110, 0))
        self.architect = architect
        rooms = []

        toBuildRoom = architect.doAddRoom(
            {
                "coordinate": (7,7),
                "roomType": "EmptyRoom",
                "doors": "0,6 12,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        self.toBuildRoom = toBuildRoom
        storageRoom = architect.doAddRoom(
            {
                "coordinate": (6,7),
                "roomType": "EmptyRoom",
                "doors": "12,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        self.storageRoom = storageRoom
        storageRoom2 = architect.doAddRoom(
            {
                "coordinate": (8,7),
                "roomType": "EmptyRoom",
                "doors": "0,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        self.storageRoom2 = storageRoom2

        self.toBuildRoomClone = None
        self.toBuildRoomClone2 = None
        self.toBuildRoomClone3 = None
        self.toBuildRoomClone4 = None
        self.toBuildRoomClone5 = None
        self.toBuildRoomClone6 = None

        for x in range(1,6):
            for y in range(1,6):
                item = src.items.itemMap["ScrapCompactor"]()
                storageRoom.addItem(item,(x,y,0))
                item.bolted = False
        for x in range(7,12):
            for y in range(1,6):
                item = src.items.itemMap["ScrapCompactor"]()
                storageRoom.addItem(item,(x,y,0))
                item.bolted = False
        for x in range(7,12):
            for y in range(7,12):
                for i in range(1,10):
                    item = src.items.itemMap["Corpse"]()
                    storageRoom.addItem(item,(x,y,0))
                    item.bolted = False

        for x in range(1,6):
            for y in range(1,6):
                for i in range(1,10):
                    item = src.items.itemMap["MetalBars"]()
                    storageRoom2.addItem(item,(x,y,0))
                    item.bolted = False
        for x in range(7,12):
            for y in range(1,6):
                item = src.items.itemMap["Scrap"](amount=20)
                storageRoom2.addItem(item,(x,y,0))
                item.bolted = False
        for x in range(1,6):
            for y in range(7,12):
                for i in range(1,10):
                    item = src.items.itemMap["Sheet"]()
                    storageRoom2.addItem(item,(x,y,0))
                    item.bolted = False

        for y in range(7,12):
            item = src.items.itemMap["CorpseAnimator"]()
            storageRoom.addItem(item,(1,y,0))
            item.bolted = False

        item = src.items.itemMap["ScratchPlate"]()
        storageRoom.addItem(item,(5,11,0))
        item.bolted = False

        item = src.items.itemMap["ScratchPlate"]()
        storageRoom.addItem(item,(5,11,0))
        item.bolted = False

        item = src.items.itemMap["ScratchPlate"]()
        storageRoom.addItem(item,(5,11,0))
        item.bolted = False

        item = src.items.itemMap["ScratchPlate"]()
        storageRoom.addItem(item,(5,11,0))
        item.bolted = False

        item = src.items.itemMap["ScratchPlate"]()
        storageRoom.addItem(item,(5,11,0))
        item.bolted = False

        item = src.items.itemMap["ScratchPlate"]()
        storageRoom.addItem(item,(5,11,0))
        item.bolted = False

        item = src.items.itemMap["Painter"]()
        item.paintMode = "inputSlot"
        item.itemType = "Scrap"
        storageRoom.addItem(item,(3,11,0))
        item.bolted = False

        item = src.items.itemMap["Painter"]()
        item.paintMode = "outputSlot"
        item.itemType = "MetalBars"
        storageRoom.addItem(item,(3,10,0))
        item.bolted = False

        item = src.items.itemMap["Painter"]()
        item.paintMode = "walkingSpace"
        storageRoom.addItem(item,(3,9,0))
        item.bolted = False

        item = src.items.itemMap["Painter"]()
        item.paintMode = "delete"
        storageRoom.addItem(item,(3,8,0))
        item.bolted = False

        item = src.items.itemMap["FunctionTrigger"]()
        item.function = {"container":self,"method":"advance"}
        storageRoom.addItem(item,(3,7,0))

        mainChar = src.characters.Character()
        storageRoom.addCharacter(mainChar,6,6)
        src.gamestate.gamestate.mainChar = mainChar

        mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest",
            "NaiveDropQuest",
            "NaiveMurderQuest",
            "DropQuestMeta",
            "DeliverSpecialItem",
        ]
        mainChar.godMode = True

class BackToTheRoots(BasicPhase):
    """
    """

    def __init__(self, seed=0):
        """
        set up super class

        Parameters:
            seed: rng seed
        """

        super().__init__("BackToTheRoots", seed=seed)

        self.specialItemSlotPositions = [(1,1),(2,1),(3,1),(4,1),(5,1),(7,1),(8,1),(9,1),(10,1),(11,1),(1,3),(1,4),(1,5),(1,7),(1,8)]
        self.leaderQuests = {} # to save
        self.citylocations = []
        self.cityIds = {}
        self.cityNPCCounters = {}
        self.leaders = {} # to save
        self.scoreTracker = {}

        self.startDelay = int(random.random()*0)+3000
        self.epochLength = 2000
        self.firstEpoch = True
        self.npcCounter = 0
        self.gatherTime = 300

        self.attributesToStore.extend([
            "startDelay","epochLength","firstEpoch","npcCounter","gatherTime"
            ])
        self.tupleListsToStore.extend([
            "specialItemSlotPositions","citylocations"])
        self.tupleDictsToStore.extend(["cityIds","cityNPCCounters","scoreTracker"])

    def genNPC(self, cityCounter, citylocation, flaskUses=10, spawnArmor=False, spawnWeapon=False):
        self.npcCounter += 1

        npc = src.characters.Character()
        item = src.items.itemMap["GooFlask"]()
        item.uses = flaskUses

        npc.inventory.append(item)
        npc.runCommandString("10.10*")
        npc.macroState["macros"]["j"] = ["J", "f"]
        npc.faction = "city #%s"%(cityCounter,)
        npc.registers["HOMEx"] = citylocation[0]
        npc.registers["HOMEy"] = citylocation[1]

        # add basic set of abilities in openworld phase
        npc.questsDone = [
            "BeUsefull",
            "GoToTile",
        ]

        npc.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest",
            "NaiveDropQuest",
            "NaiveMurderQuest",
            "DropQuestMeta",
            "DeliverSpecialItem",
        ]

        if spawnWeapon:
            npc.weapon = src.items.itemMap["Rod"]()
        if spawnArmor:
            npc.armor = src.items.itemMap["Armor"]()

        npc.personality["abortMacrosOnAttack"] = False
        npc.personality["doIdleAction"] = False
        return npc

    def getState(self):
        state = super().getState()

        #self.leaderQuests = {} # to save
        #self.leaders = {} # to save

        convertedLeaderMap = []
        for (key,value) in self.leaders.items():
            if value:
                value = value.id
            convertedLeaderMap.append([list(key),value])
        state["leaders"] = convertedLeaderMap

        convertedLeaderQuestsMap = []
        for (key,value) in self.leaderQuests.items():
            if value:
                value = value.id
            convertedLeaderQuestsMap.append([list(key),value])
        state["leaderQuests"] = convertedLeaderQuestsMap

        return state

    def setState(self,state):
        super().setState(state)

        if "leaders" in state:
            self.leaders = {}
            for entry in state["leaders"]:
                def setValue(value, key):
                    self.leaders[key] = value

                newKey = tuple(entry[0])
                src.saveing.loadingRegistry.callWhenAvailable(entry[1], setValue, newKey)
                self.leaders[newKey] = None

        if "leaderQuests" in state:
            self.leaderQuests = {}
            for entry in state["leaderQuests"]:
                def setValue(value, key):
                    self.leaderQuests[key] = value

                newKey = tuple(entry[0])
                src.saveing.loadingRegistry.callWhenAvailable(entry[1], setValue, newKey)
                self.leaderQuests[newKey] = None

    def start(self, seed=0, difficulty=None):
        """
        set up terrain and spawn main character

        Parameters:
            seed: rng seed
        """

        mainChar = src.gamestate.gamestate.mainChar

        # build cities
        numCities = 0
        self.citylocations.append((7,7))
        while numCities < 4:
            pos = (random.randint(3,11),random.randint(4,11))

            foundEnemyCity = None
            for cityPos in self.citylocations:
                if abs(pos[0]-cityPos[0])+abs(pos[1]-cityPos[1]) > 5:
                    continue
                foundEnemyCity = cityPos
                break

            if foundEnemyCity:
                continue

            self.citylocations.append(pos)
            numCities += 1
        self.citylocations.remove((7,7))

        # add old main fortress
        architect = src.items.itemMap["ArchitectArtwork"]()
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addItem(architect,(124, 110, 0))
        rooms = []

        room = architect.doAddRoom(
            {
                "coordinate": (7,7),
                "roomType": "EmptyRoom",
                "doors": "0,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        rooms.append(room)

        room = architect.doAddRoom(
            {
                "coordinate": (7-1,7+0),
                "roomType": "EmptyRoom",
                "doors": "6,0 12,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        rooms.append(room)

        room = architect.doAddRoom(
            {
                "coordinate": (7-1,7-1),
                "roomType": "EmptyRoom",
                "doors": "12,6 6,12",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        rooms.append(room)

        room = architect.doAddRoom(
            {
                "coordinate": (7,7-1),
                "roomType": "EmptyRoom",
                "doors": "12,6 0,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        rooms.append(room)

        room = architect.doAddRoom(
            {
                "coordinate": (7+1,7-1),
                "roomType": "EmptyRoom",
                "doors": "0,6 6,12",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        rooms.append(room)

        room = architect.doAddRoom(
            {
                "coordinate": (7+1,7),
                "roomType": "EmptyRoom",
                "doors": "6,0 6,12",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        rooms.append(room)

        room = architect.doAddRoom(
            {
                "coordinate": (7+1,7+1),
                "roomType": "EmptyRoom",
                "doors": "6,0 0,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        rooms.append(room)

        room = architect.doAddRoom(
            {
                "coordinate": (7,7+1),
                "roomType": "EmptyRoom",
                "doors": "12,6 0,6",
                "offset": [1,1],
                "size": [13, 13],
                },
            None,
        )
        rooms.append(room)

        # add treasure room
        room = rooms[0]
        sword = src.items.itemMap["Sword"]()
        armor = src.items.itemMap["Armor"]()
        armor.armorValue = 100

        ripInReality = src.items.itemMap["RipInReality"](treasure=[armor,sword])
        room.addItem(ripInReality,(6,6,0))


        roomCounter = 0
        for room in reversed(rooms[1:-1]):
            roomCounter += 1
            for i in range(0,3):
                pos = (int(random.random()*12)+1,int(random.random()*12)+1)
                enemy = src.characters.Monster(pos[0],pos[1])
                enemy.health = 10*roomCounter
                enemy.baseDamage = roomCounter
                enemy.godMode = True
                enemy.macroState["macros"]["g"] = ["g","g","_","g"]
                enemy.runCommandString("_g")
                room.addCharacter(enemy, pos[0], pos[1])
        
        placedMainChar = False

        currentTerrain = src.gamestate.gamestate.terrainMap[6][7]

        # add minefield
        offsets = [(0,0)]
        for offset in offsets:
            architect.doClearField(7+offset[0],7+offset[1])
            currentTerrain.noPlacementTiles.append((7+offset[0],7+offset[1]))

        for offset in offsets:
            for x in range(1,14):
                for y in range(1,14):
                    pos = (15*(7+offset[0])+x,15*(7+offset[1])+y,0)
                    if (pos[0]+pos[1])%2:
                        if random.random() > 0.3:
                            mine = src.items.itemMap["LandMine"]()
                            currentTerrain.addItem(mine,pos)
                        if random.random() < 0.1:
                            item = src.items.itemMap["Scrap"]()
                            currentTerrain.addItem(item,pos)
                    else:
                        if random.random() < 0.1 or 1==1:
                            if random.random() < 0.3 or 1==1:
                                mine = src.items.itemMap["FireCrystals"]()
                                currentTerrain.addItem(mine,pos)
                            else:
                                mine = src.items.itemMap["LandMine"]()
                                currentTerrain.addItem(mine,pos)
                        
                        #item = src.items.itemMap["Scrap"](amount=int(random.random()*13))
                        #currentTerrain.addItem(item,pos)

        enemy = src.characters.Character(6,6)
        rooms[0].addCharacter(enemy, 6, 6)
        item = src.items.itemMap["GooFlask"]()
        item.uses = 100
        enemy.inventory.append(item)

        offsets = []
        for x in (-1,0,1,2):
            for y in (-1,0,1,2):
                offsets.append((x,y))
        for citylocation in self.citylocations:
            for offset in offsets:
                terrain = src.gamestate.gamestate.terrainMap[6][7]
                terrain.noPlacementTiles.append((citylocation[0]+offset[0],citylocation[1]+offset[1]))

        #src.gamestate.gamestate.mainChar = enemy
        #placedMainChar = True

        # add random items
        y = 0
        for row in src.gamestate.gamestate.terrainMap[:]:
            y += 1
            x = 0
            for terrain in row[:]:
                x += 1

                if not (y == 7 and x == 8):
                    continue
                """
                if random.choice([True,False]) or 1==1:
                    terrain = src.terrains.Desert()
                    terrain.xPosition = x-1
                    terrain.yPosition = y-1
                    src.gamestate.gamestate.terrainMap[y-1][x-1] = terrain
                """

                items = []
                molds = []
                landmines = []
                for i in range(0,random.randint(1,100)):
                    item = src.items.itemMap["MetalBars"]()
                    items.append(item)
                for i in range(0,random.randint(1,100)):
                    item = src.items.itemMap["Rod"]()
                    if item.baseDamage > 10:
                        item.baseDamage = random.randint(7,10)
                    items.append(item)
                for i in range(0,random.randint(1,30)):
                    item = src.items.itemMap["Armor"]()
                    if item.armorValue > 3:
                        item.armorValue = random.randint(1,3)
                    items.append(item)
                for i in range(0,random.randint(1,30)):
                    item = src.items.itemMap["GooFlask"]()
                    item.uses = random.randint(1,3)
                    items.append(item)
                for i in range(0,random.randint(1,200)):
                    item = src.items.itemMap["FireCrystals"]()
                    items.append(item)
                for i in range(0,random.randint(1,1500)):
                    item = src.items.itemMap["LandMine"]()
                    items.append(item)
                    landmines.append(item)
                for i in range(0,random.randint(1,300)):
                    item = src.items.itemMap["Bomb"]()
                    items.append(item)
                    landmines.append(item)
                for i in range(0,random.randint(1,200)):
                    item = src.items.itemMap["Bolt"]()
                    items.append(item)
                    landmines.append(item)
                for i in range(0,random.randint(1,2000)):
                    item = src.items.itemMap["Mold"]()
                    items.append(item)
                    molds.append(item)
            
                terrain.randomAddItems(items)
                for mold in molds:
                    mold.spawn()
                    pass

                for landmine in landmines:
                    scrap = src.items.itemMap["Scrap"](amount=random.randint(1,3))
                    if random.choice([True,False]):
                        if landmine.getPosition()[0]:
                            terrain.addItem(scrap,landmine.getPosition())
                
                #for i in range(0,random.randint(1,20)):
                #for i in range(0,200):
                for i in range(0,150):
                    xPos = int(random.random()*13+1)*15+int(random.random()*13+1)
                    yPos = int(random.random()*13+1)*15+int(random.random()*13+1)
                    foundCity = None
                    for cityLocation in self.citylocations:
                        if abs(xPos//15-cityLocation[0])+abs(yPos//15-cityLocation[1]) < 5:
                            foundCity = cityLocation
                            break

                    if foundCity:
                        continue

                    if (xPos//15,yPos//15) in [(6,6),(6,7),(6,8),(7,6),(7,7),(7,8),(8,6),(8,7),(8,8)]:
                        continue

                    if (xPos//15,yPos//15) in currentTerrain.noPlacementTiles:
                        continue

                    enemy = src.characters.Monster(xPos,yPos)
                    enemy.health = random.randint(1, 100)
                    enemy.baseDamage = random.randint(1, 10)
                    enemy.godMode = True
                    #enemy.aggro = 1000000
                    enemy.macroState["macros"]["g"] = ["g","g","_","g"]
                    enemy.runCommandString("_g")
                    #enemy.disabled = True
                    terrain.addCharacter(enemy, xPos, yPos)

        cityCounter = 1
        for citylocation in self.citylocations:
            currentTerrain = src.gamestate.gamestate.terrainMap[6][7]
            
            architect = src.items.itemMap["ArchitectArtwork"]()
            currentTerrain.addItem(architect,(124, 110, 0))

            architect.doClearField(citylocation[0]  , citylocation[1]  )
            architect.doClearField(citylocation[0]+1, citylocation[1]  )
            architect.doClearField(citylocation[0]-1, citylocation[1]  )
            architect.doClearField(citylocation[0]  , citylocation[1]+1)
            architect.doClearField(citylocation[0]  , citylocation[1]-1)
            architect.doClearField(citylocation[0]+1, citylocation[1]+1)
            architect.doClearField(citylocation[0]+1, citylocation[1]-1)
            architect.doClearField(citylocation[0]-1, citylocation[1]+1)
            architect.doClearField(citylocation[0]-1, citylocation[1]-1)

            mainRoom = architect.doAddRoom(
                {
                    "coordinate": citylocation,
                    "roomType": "ComandCenter",
                    "faction": "city #%s"%(cityCounter,),
                    "doors": "6,12",
                    "offset": [1,1],
                    "size": [13, 13],
                    },
                None,
            )

            leader = self.genNPC(cityCounter,citylocation)
            leader.registers["ATTNPOSx"] = 5
            leader.registers["ATTNPOSy"] = 3
            mainRoom.addCharacter(leader,7,3)
            leader.rank = 3
            leader.inventory.insert(0,src.items.itemMap["GooFlask"](uses = 100))
            leader.faction = "city #%s"%(cityCounter,)
            self.leaders[citylocation] = leader


            rooms = []


            cityBuilder = src.items.itemMap["CityBuilder2"]()
            cityBuilder.architect = architect
            mainRoom.addItem(cityBuilder,(7,1,0))
            mainRoom.rooms = rooms
            cityBuilder.registerRoom(mainRoom)

            dutyArtwork = src.items.itemMap["DutyArtwork"]()

            mainRoom.addItem(architect,(3,1,0))
            mainRoom.addItem(dutyArtwork,(4,1,0))

            cityData = cityBuilder.spawnCity(leader)

            self.cityNPCCounters[citylocation] = 0

            scrapFieldpos = (citylocation[0]+2,citylocation[1]-2)
            architect.doAddScrapfield(scrapFieldpos[0],scrapFieldpos[1],1200,leavePath=True)

            counter = 1
            for pos in self.specialItemSlotPositions:
                slotItem = src.items.itemMap["SpecialItemSlot"]()
                slotItem.itemID = counter
                slotItem.faction = leader.faction
                if counter == cityCounter:
                    slotItem.hasItem = True
                cityData["backGuardRoom"].addItem(slotItem,(pos[0],pos[1],0))
                counter += 1

            slotItem = src.items.itemMap["SpecialItem"]()
            slotItem.itemID = cityCounter


            for i in range(0,3):
                subleader = self.genNPC(cityCounter,citylocation)
                subleader.registers["ATTNPOSx"] = 3+i*3
                subleader.registers["ATTNPOSy"] = 4
                mainRoom.addCharacter(subleader,3+i*3,4)
                subleader.inventory.insert(0,src.items.itemMap["GooFlask"](uses = 100))

                leader.subordinates.append(subleader)

                quest = src.quests.Serve(superior=leader)
                subleader.superior = leader
                subleader.rank = 4
                subleader.assignQuest(quest, active=True)

                for j in range(0,3):
                    subsubleader = self.genNPC(cityCounter,citylocation)
                    subsubleader.registers["ATTNPOSx"] = 2+i*3+j
                    subsubleader.registers["ATTNPOSy"] = 5
                    mainRoom.addCharacter(subsubleader, 2+i*3+j, 5)
                    subsubleader.inventory.insert(0,src.items.itemMap["GooFlask"](uses = 100))

                    subleader.subordinates.append(subsubleader)

                    quest = src.quests.Serve(superior=subleader)
                    subsubleader.superior = subleader
                    subsubleader.rank = 5
                    subsubleader.assignQuest(quest, active=True)
                        
                    """
                    if not placedMainChar and i == 2 and j == 2:
                        src.gamestate.gamestate.mainChar = subsubleader
                        placedMainChar = True
                    """

                    for k in range(0,3):
                        spawnArmor = False
                        spawnWeapon = False
                        worker = self.genNPC(cityCounter,citylocation,flaskUses=(2-k)+10,spawnWeapon=spawnWeapon,spawnArmor=spawnArmor)
                        worker.registers["ATTNPOSx"] = 2+i*3+j
                        worker.registers["ATTNPOSy"] = 7+k
                        mainRoom.addCharacter(worker,2+i*3+j,7+k)
                        subsubleader.subordinates.append(worker)

                        quest = src.quests.Serve(superior=subsubleader)
                        worker.superior = subsubleader
                        worker.rank = 6
                        worker.assignQuest(quest, active=True)

                        if not placedMainChar and i == 2 and j == 2 and k == 2:
                            src.gamestate.gamestate.mainChar = worker
                            placedMainChar = True

            quest = src.quests.ObtainAllSpecialItems()
            leader.assignQuest(quest, active=True)
            self.leaderQuests[citylocation] = quest

            self.cityIds[citylocation] = cityCounter
            self.scoreTracker[citylocation] = -1

            cityCounter += 1

            xPos = 1
            yPos = 1
            enemy = src.characters.Guardian(xPos,yPos)
            enemy.health = 1500
            enemy.baseDamage = 100 + random.randint(1, 10)
            enemy.godMode = True
            enemy.aggro = 1000000
            enemy.macroState["macros"]["g"] = ["g","g","_","g"]
            enemy.runCommandString("_g")
            enemy.faction = leader.faction
            mainRoom.addCharacter(enemy, xPos, yPos)

            xPos = 1
            yPos = 11
            enemy = src.characters.Guardian(xPos,yPos)
            enemy.health = 1500
            enemy.baseDamage = 100 + random.randint(1, 10)
            enemy.godMode = True
            enemy.aggro = 1000000
            enemy.macroState["macros"]["g"] = ["g","g","_","g"]
            enemy.runCommandString("_g")
            enemy.faction = leader.faction
            mainRoom.addCharacter(enemy, xPos, yPos)

            xPos = 11
            yPos = 1
            enemy = src.characters.Guardian(xPos,yPos)
            enemy.health = 1500
            enemy.baseDamage = 100 + random.randint(1, 10)
            enemy.godMode = True
            enemy.aggro = 1000000
            enemy.macroState["macros"]["g"] = ["g","g","_","g"]
            enemy.runCommandString("_g")
            enemy.faction = leader.faction
            mainRoom.addCharacter(enemy, xPos, yPos)

            xPos = 11
            yPos = 11
            enemy = src.characters.Guardian(xPos,yPos)
            enemy.health = 1500
            enemy.baseDamage = 100 + random.randint(1, 10)
            enemy.godMode = True
            enemy.aggro = 1000000
            enemy.macroState["macros"]["g"] = ["g","g","_","g"]
            enemy.runCommandString("_g")
            enemy.faction = leader.faction
            mainRoom.addCharacter(enemy, xPos, yPos)

            xPos = 7
            yPos = 13
            enemy = src.characters.Guardian(xPos,yPos)
            enemy.health = 1500
            enemy.baseDamage = 100 + random.randint(1, 10)
            enemy.godMode = True
            enemy.aggro = 1000000
            enemy.macroState["macros"]["g"] = ["g","g","_","g"]
            enemy.runCommandString("_g")
            enemy.faction = leader.faction
            mainRoom.addCharacter(enemy, xPos, yPos)

            xPos = 5
            yPos = 13
            enemy = src.characters.Guardian(xPos,yPos)
            enemy.health = 1500
            enemy.baseDamage = 100 + random.randint(1, 10)
            enemy.godMode = True
            enemy.aggro = 1000000
            enemy.macroState["macros"]["g"] = ["g","g","_","g"]
            enemy.runCommandString("_g")
            enemy.faction = leader.faction
            mainRoom.addCharacter(enemy, xPos, yPos)

        mainChar = src.gamestate.gamestate.mainChar
        mainChar.runCommandString("~~", clear=True)
        mainChar.personality["autoFlee"] = False
        mainChar.personality["abortMacrosOnAttack"] = False
        mainChar.personality["autoCounterAttack"] = False
        mainChar.personality["avoidItems"] = False

        """
        mainChar.health = 1000000
        mainChar.maxHealth = 1000000
        mainChar.baseDamage = 10000
        mainChar.satiation = 1000000
        mainChar.reputation = 1000000
        """
        
        src.gamestate.gamestate.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
            "NaiveMurderQuest",
        ]

        def waitNPC(char):
            newQuest = src.quests.WaitQuest()
            for charQuest in char.quests:
                if charQuest.type == "Serve":
                    charQuest.addQuest(newQuest)

        for cityLocation in self.citylocations:
            cityLeader = self.leaders[cityLocation]
            waitNPC(cityLeader)
            for subleader in cityLeader.subordinates:
                waitNPC(subleader)
                for subsubleader in subleader.subordinates:
                    waitNPC(subsubleader)
                    for worker in subsubleader.subordinates:
                        waitNPC(worker)
        self.startTutorial()

        self.checkRespawn()
        self.checkTutorialEnd()

    def checkTutorialEnd(self):
        terrain = src.gamestate.gamestate.terrainMap[6][7]

        endTutorial = False
        if isinstance(src.gamestate.gamestate.mainChar.container,src.rooms.Room):
            room = src.gamestate.gamestate.mainChar.container
            if room.container == src.gamestate.gamestate.terrainMap[6][7]:
                for citylocation in self.citylocations:
                    if not self.leaders[citylocation].faction == src.gamestate.gamestate.mainChar.faction:
                        continue

                    if (room.xPosition,room.yPosition) == citylocation:
                        endTutorial = True

        if endTutorial:
            self.startNewEpoch()
        else:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "checkTutorialEnd"})
            terrain.addEvent(event)

    def startTutorial(self):
        terrain = src.gamestate.gamestate.terrainMap[7][7]

    def almostStartNewEpoch(self):
        terrain = src.gamestate.gamestate.terrainMap[7][7]

        def gatherNPC(char):
            newQuest = src.quests.StandAttention()
            newQuest.setParameters({"lifetime":self.gatherTime})
            newQuest.generateSubquests(char)
            for charQuest in char.quests:
                if charQuest.type == "Serve":
                    charQuest.addQuest(newQuest)

        for cityLocation in self.citylocations:
            cityLeader = self.leaders[cityLocation]
            gatherNPC(cityLeader)
            for subleader in cityLeader.subordinates:
                gatherNPC(subleader)
                for subsubleader in subleader.subordinates:
                    gatherNPC(subsubleader)
                    for worker in subsubleader.subordinates:
                        gatherNPC(worker)

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + self.gatherTime)
        event.setCallback({"container": self, "method": "startNewEpoch"})
        terrain.addEvent(event)

    def checkRespawn(self):
        terrain = src.gamestate.gamestate.terrainMap[7][7]

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 10)
        event.setCallback({"container": self, "method": "checkRespawn"})
        terrain.addEvent(event)

        if src.gamestate.gamestate.mainChar.dead == False:
            return

        foundNPCs = []
        foundCityNPCs = []
        for cityLocation in self.citylocations:
            cityLeader = self.leaders[cityLocation]
            if cityLeader == None or cityLeader.dead == True:
                continue
            for subleader in cityLeader.subordinates:
                if subleader == None or subleader.dead == True:
                    continue
                for subsubleader in subleader.subordinates:
                    if subsubleader == None or subsubleader.dead == True:
                        continue
                    for worker in subsubleader.subordinates:
                        if worker == None or worker.dead == True:
                            continue
                        foundNPCs.append(worker)
                        if worker.faction == src.gamestate.gamestate.mainChar.faction:
                            foundCityNPCs.append(worker)

        if foundCityNPCs:
            src.gamestate.gamestate.mainChar = random.choice(foundCityNPCs)
        elif foundNPCs:
            src.gamestate.gamestate.mainChar = random.choice(foundNPCs)
        else:
            print("you lost the game")
            1/0

        src.gamestate.gamestate.mainChar.runCommandString("",clear=True)

        mainChar = src.gamestate.gamestate.mainChar
        mainChar.personality["autoFlee"] = False
        mainChar.personality["abortMacrosOnAttack"] = False
        mainChar.personality["autoCounterAttack"] = False
        mainChar.personality["avoidItems"] = False

    def rewardNPCDirect(self,character):
        print("rewarding npc")

    def startNewEpoch(self):
        src.gamestate.gamestate.mainChar.addMessage("starting new epoch")

        specialItemPositions = {}
        toFetchMap = {}
        hasItemMap = {}

        locatedItems = []
        missingItemMap = {}
        for cityLocation in self.citylocations:

            terrain = src.gamestate.gamestate.terrainMap[6][7]
            foundRoom = None
            for room in terrain.rooms:
                if room.xPosition == cityLocation[0] and room.yPosition == cityLocation[1]+1:
                    foundRoom = room

            if foundRoom:
                print("found room")
            else:
                print("did not find room")
                return
        
            missingItems = []
            foundItems = []
            for pos in self.specialItemSlotPositions:
                for item in foundRoom.getItemByPosition((pos[0],pos[1],0)):
                    if not item.type == "SpecialItemSlot":
                        continue
                    if not item.hasItem:
                        missingItems.append(item.itemID)
                        continue
                    foundItems.append(item.itemID)
                    specialItemPositions[item.itemID] = (cityLocation[0],cityLocation[1]+1)

            hasItemMap[cityLocation] = foundItems

            locatedItems.extend(foundItems)
            missingItemMap[cityLocation] = missingItems

        for cityLocation in self.citylocations:
            missingItems = missingItemMap[cityLocation]

            candidates = missingItems[:]
            for candidate in candidates[:]:
                if not candidate in locatedItems:
                    candidates.remove(candidate)

            if not candidates:
                print("city %s won the game"%(cityLocation,))
                cityLeader = self.leaders[cityLocation]
                print("%s won the game"%(cityLeader.name,))
                if cityLeader == src.gamestate.gamestate.mainChar:
                    print("you won the game")
                    showText("you won the game. Congratulations. entering free play now")
                    showText("you won the game. Congratulations. entering free play now\n(in case the previous screen was bugged)")
                    src.gamestate.gamestate.mainChar.quests = []
                    src.gamestate.gamestate.mainChar.runCommandString("",clear=True)
                else:
                    print("you lost the game")
                itemToFetch = None
                break
             
            itemToFetch = random.choice(candidates)
            toFetchMap[cityLocation] = itemToFetch

        def gatherNPC(char):
            newQuest = src.quests.StandAttention()
            newQuest.setParameters({"lifetime":self.gatherTime})
            newQuest.generateSubquests(char)
            for charQuest in char.quests:
                if charQuest.type == "Serve":
                    charQuest.addQuest(newQuest)

        for cityLocation in self.citylocations:
            cityLeader = self.leaders[cityLocation]
            gatherNPC(cityLeader)
            for subleader in cityLeader.subordinates:
                if subleader == None or subleader.dead:
                    continue
                gatherNPC(subleader)
                for subsubleader in subleader.subordinates:
                    if subsubleader == None or subsubleader.dead:
                        continue
                    gatherNPC(subsubleader)
                    for worker in subsubleader.subordinates:
                        if worker == None or worker.dead:
                            continue
                        gatherNPC(worker)

        if not self.firstEpoch:
            for cityLocation in self.citylocations:
                cityLeader = self.leaders[cityLocation]
                cityLeader.awardReputation(amount=10,reason="survived the epoch",carryOver=True)
                for subleader in cityLeader.subordinates:
                    if subleader == None or subleader.dead:
                        continue
                    subleader.awardReputation(amount=10,reason="survived the epoch",carryOver=True)
                    for subsubleader in subleader.subordinates:
                        if subsubleader == None or subsubleader.dead:
                            continue
                        subsubleader.awardReputation(amount=10,reason="survived the epoch",carryOver=True)
                        for worker in subsubleader.subordinates:
                            if worker == None or worker.dead:
                                continue
                            worker.awardReputation(amount=10,reason="survived the epoch",carryOver=True)

        for cityLocation in self.citylocations:
            numNpcs = len(hasItemMap[cityLocation])*50
            currentTerrain = src.gamestate.gamestate.terrainMap[6][7]

            foundRoom = None
            for room in terrain.rooms:
                if room.xPosition == cityLocation[0] and room.yPosition == cityLocation[1]:
                    foundRoom = room

            mainRoom = foundRoom

            for item in mainRoom.itemsOnFloor[:]:
                if not item.type == "Corpse":
                    continue
                mainRoom.removeItem(item)

            cityLeader = self.leaders[cityLocation]

            if cityLeader.faction == src.gamestate.gamestate.mainChar.faction:
                if 1==1:
                    rowwidth = 17

                    infogrid = []
                    for i in range(0,9*6*2):
                        infogrid.append(" "*rowwidth)

                    def getname(character):
                        if character == None or character.dead:
                            return ""
                        name = character.name.split(" ")[0][0]+". "+character.name.split(" ")[1]
                        if character == src.gamestate.gamestate.mainChar:
                            name = "== "+name+" =="
                        return name

                    infogrid[4] = cityLeader.name+" "*(rowwidth-len(cityLeader.name))
                    row2Counter = 0
                    row3Counter = 0

                    cityLeaderSubordinates = cityLeader.subordinates
                    while len(cityLeaderSubordinates) < 3:
                        cityLeaderSubordinates.append(None)

                    for subleader in cityLeaderSubordinates:
                        
                        if subleader and not subleader.dead:
                            infogrid[2*9+1+row2Counter*3] = getname(subleader)+" "*(rowwidth-len(getname(subleader)))
                            infogrid[3*9+1+row2Counter*3] = str(subleader.reputation)+" "*(rowwidth-len(str(subleader.reputation)))
                            subleaderSubordinates = subleader.subordinates
                        else:
                            infogrid[2*9+1+row2Counter*3] = " "*rowwidth
                            infogrid[3*9+1+row2Counter*3] = " "*rowwidth
                            subleaderSubordinates = [None,None,None]

                        while len(subleaderSubordinates) < 3:
                            subleaderSubordinates.append(None)

                        for subsubleader in subleaderSubordinates:

                            if subleader and not subleader.dead:
                                infogrid[4*9+row3Counter] = getname(subsubleader)+" "*(rowwidth-len(getname(subsubleader)))
                                infogrid[5*9+row3Counter] = str(subsubleader.reputation)+" "*(rowwidth-len(str(subsubleader.reputation)))
                                subsubleaderSubordinates = subsubleader.subordinates
                            else:
                                infogrid[4*9+row3Counter] = " "*rowwidth
                                infogrid[5*9+row3Counter] = " "*rowwidth
                                subsubleaderSubordinates = [None,None,None]

                            while len(subsubleaderSubordinates) < 3:
                                subsubleaderSubordinates.append(None)

                            lineCounter = 0
                            for worker in subsubleaderSubordinates:
                                if worker and not worker.dead:
                                    infogrid[(2+1+lineCounter)*2*9+row3Counter] = getname(worker)+" "*(rowwidth-len(getname(worker)))
                                    infogrid[((2+1+lineCounter)*2+1)*9+row3Counter] = str(worker.reputation)+" "*(rowwidth-len(str(worker.reputation)))
                                else:
                                    infogrid[(2+1+lineCounter)*2*9+row3Counter] = " "*rowwidth
                                    infogrid[((2+1+lineCounter)*2+1)*9+row3Counter] = " "*rowwidth
                                lineCounter += 1
                            row3Counter += 1
                        row2Counter += 1

                    reputationTree = """
cityleader:   """+"%s   "*9+"""
              """+"%s   "*9+"""
subleaders:   """+"%s   "*9+"""
              """+"%s   "*9+"""
squadleaders: """+"%s   "*9+"""
              """+"%s   "*9+"""

workers:      """+"%s   "*9+"""
              """+"%s   "*9+"""
workers:      """+"%s   "*9+"""
              """+"%s   "*9+"""
workers:      """+"%s   "*9+"""
              """+"%s   "*9+"""
"""
                    reputationTree = reputationTree%tuple(infogrid)

                    showText("""spacer""")
                    showText("""
a new epoch has started!

the current reputation is:
%s

press space to continue"""%(reputationTree))


            if cityLeader.dead:
                print("leader dead")
                continue
        
            # spawn reward npcs
            for i in range(0,numNpcs):
                newNPC = self.genNPC(self.cityIds[cityLocation],cityLocation)
                self.cityNPCCounters[cityLocation] += 1

                foundSubleaderReplacement = None
                counter = 0
                for subordinate in cityLeader.subordinates:
                    if subordinate.dead == True:
                        foundSubleaderReplacement = subordinate
                        break
                    counter += 1

                if len(cityLeader.subordinates) < 3:
                    counter = len(cityLeader.subordinates)
                    cityLeader.subordinates.append(None)
                    foundSubleaderReplacement = True

                if foundSubleaderReplacement:
                    cityLeader.subordinates[counter] = newNPC

                    mainRoom.addCharacter(newNPC,4+counter*3,4)

                    quest = src.quests.Serve(superior=cityLeader)
                    newNPC.assignQuest(quest, active=True)
                    newNPC.superior = cityLeader
                    newNPC.rank = 4
                    newNPC.inventory.insert(0,src.items.itemMap["GooFlask"](uses=100))

                    newNPC.addMessage("added as replacement 2nd tier officer")
                    continue

                if random.choice((True,True,False,)):
                    selectedSubLeader = random.choice(cityLeader.subordinates)
                else:
                    maxReputation = None
                    for char in cityLeader.subordinates:
                        if maxReputation == None or char.reputation >= maxReputation:
                            selectedSubLeader = char
                            maxReputation = char.reputation

                counter = cityLeader.subordinates.index(selectedSubLeader)

                foundSubsubleaderReplacement = None
                counter2 = 0
                for subsubordinate in selectedSubLeader.subordinates:
                    if subsubordinate.dead == True:
                        foundSubsubleaderReplacement = subsubordinate
                        break
                    counter2 += 1

                if len(selectedSubLeader.subordinates) < 3:
                    counter2 = len(selectedSubLeader.subordinates)
                    selectedSubLeader.subordinates.append(None)
                    foundSubsubleaderReplacement = True

                if foundSubsubleaderReplacement:
                    selectedSubLeader.subordinates[counter2] = newNPC

                    mainRoom.addCharacter(newNPC,3+counter*3+counter2,5)

                    quest = src.quests.Serve(superior=selectedSubLeader)
                    newNPC.assignQuest(quest, active=True)
                    newNPC.superior = selectedSubLeader
                    newNPC.rank = 5
                    newNPC.inventory.insert(0,src.items.itemMap["GooFlask"](uses=100))

                    newNPC.addMessage("added as replacement 2nd tier officer")
                    continue

                if random.choice((True,True,False,)):
                    selectedSubsubLeader = random.choice(selectedSubLeader.subordinates)
                else:
                    maxReputation = None
                    for char in selectedSubLeader.subordinates:
                        if maxReputation == None or char.reputation >= maxReputation:
                            selectedSubsubLeader = char
                            maxReputation = char.reputation

                counter2 = selectedSubLeader.subordinates.index(selectedSubsubLeader)

                foundWorkerReplacement = None
                counter3 = 0
                for worker in selectedSubsubLeader.subordinates:
                    if not worker or worker.dead == True:
                        foundWorkerReplacement = True
                        break
                    counter3 += 1

                if len(selectedSubsubLeader.subordinates) < 3:
                    counter3 = len(selectedSubsubLeader.subordinates)
                    selectedSubsubLeader.subordinates.append(None)
                    foundWorkerReplacement = True

                if foundWorkerReplacement:
                    selectedSubsubLeader.subordinates[counter3] = newNPC

                    mainRoom.addCharacter(newNPC,3+counter*3+counter2,7+counter3)

                    quest = src.quests.Serve(superior=selectedSubsubLeader)
                    newNPC.assignQuest(quest, active=True)
                    newNPC.superior = selectedSubsubLeader
                    newNPC.rank = 6

                    if src.gamestate.gamestate.mainChar.dead == True:
                        src.gamestate.gamestate.mainChar = newNPC

                    newNPC.addMessage("added as replacement worker")
                    continue

                """
                print("full tree adding machine")
                placedItem = False
                offset = (1,1)
                for y in (92,94,96,98,100,102):
                    for x in (107,109,111,113,115,117):
                        if currentTerrain.getItemByPosition((x,y,0)):
                            print("skipping"
                            continue
                        dropType = random.choice(["Machine","ItemUpgrader","ScrapCompactor"])
                        item = src.items.itemMap[dropType]()
                        if dropType == "Machine":
                            itemType = random.choice(["Rod","Armor"])
                            item.setToProduce(itemType)
                        if dropType == "ItemUpgrader":
                            item.level = 10
                        currentTerrain.addItem(item,(x,y,0))
                        item.bolted = False
                        placedItem = True
                        break

                    if placedItem:
                        break

                newNPC.die()
                """

        # do promotions
        for cityLocation in self.citylocations:
            toKill = []
            newScore = len(hasItemMap[cityLocation])
            cityLeader = self.leaders[cityLocation]

            foundQuest = None
            for quest in cityLeader.quests:
                if isinstance(quest,src.quests.ObtainAllSpecialItems): 
                    foundQuest = quest

            if foundQuest and newScore <= self.scoreTracker[cityLocation]:

                cityLeader = self.leaders[cityLocation]
                toKill.append(cityLeader)

                # promote subleaders
                candidates = []
                for subordinate in cityLeader.subordinates:
                    if subordinate.dead:
                        continue
                    candidates.append(subordinate)

                if not candidates:
                    continue

                maxReputation = None
                for char in candidates:
                    if maxReputation == None or char.reputation >= maxReputation:
                        subLeader = char
                        maxReputation = char.reputation

                serveQuest = subLeader.quests[0]
                subLeader.quests.remove(serveQuest)
                subLeader.rank = 3
                subLeader.inventory.insert(0,src.items.itemMap["GooFlask"](uses = 100))

                subLeader.quests.append(cityLeader.quests[0])
                subLeader.runCommandString("w")
                del subLeader.superior
                self.leaders[cityLocation] = subLeader

                oldSubordinatesSubLeader = subLeader.subordinates
                subLeader.subordinates = []
                subLeaderInsertIndex = None
                counter = 0
                for subordinate in cityLeader.subordinates:
                    if subordinate == subLeader:
                        subLeaderInsertIndex = counter
                        continue
                    subordinate.superior = subLeader
                    subLeader.subordinates.append(subordinate)
                    counter += 1

                # promote subsubleaders
                candidates = []
                for subordinate in oldSubordinatesSubLeader:
                    if subordinate.dead:
                        continue
                    candidates.append(subordinate)

                if not candidates:
                    continue

                maxReputation = None
                for char in candidates:
                    if maxReputation == None or char.reputation >= maxReputation:
                        subsubLeader = char
                        maxReputation = char.reputation

                subsubLeader.runCommandString("w")
                subsubLeader.rank = 4
                subsubLeader.inventory.insert(0,src.items.itemMap["GooFlask"](uses = 100))
                oldSubordinatesSubsubLeader = subsubLeader.subordinates
                subsubLeader.subordinates = []

                subsubLeader.superior = self.leaders[cityLocation]
                subLeader.subordinates.insert(subLeaderInsertIndex,subsubLeader)

                for subordinate in oldSubordinatesSubLeader:
                    if subordinate == subsubLeader:
                        continue
                    subordinate.superior = subsubLeader
                    subsubLeader.subordinates.append(subordinate)

                # promote workers
                candidates = []
                for subordinate in oldSubordinatesSubsubLeader:
                    if subordinate.dead:
                        continue
                    candidates.append(subordinate)

                if not candidates:
                    continue

                maxReputation = None
                for char in candidates:
                    if maxReputation == None or char.reputation > maxReputation:
                        worker = char
                        maxReputation = char.reputation

                worker.runCommandString("w"*(worker.yPosition-5))
                worker.rank = 5
                worker.inventory.insert(0,src.items.itemMap["GooFlask"](uses = 100))

                worker.superior = subsubLeader
                subsubLeader.subordinates.insert(subLeaderInsertIndex,worker)

                for subordinate in oldSubordinatesSubsubLeader:
                    if subordinate == worker:
                        continue
                    subordinate.superior = worker
                    worker.subordinates.append(subordinate)

            self.scoreTracker[cityLocation] = len(hasItemMap[cityLocation])

            for cityLeader in toKill:
                cityLeader.die()
                cityLeader.quests = []
                cityLeader.subordinates = []

            didForcePromotion = False
            forcePromoted = []
            if not toKill:
                # do force reward
                toForcePromote = []
                cityLeader = self.leaders[cityLocation]
                for subordinate in cityLeader.subordinates:
                    if subordinate.dead:
                        continue
                    for subsubordinate in subordinate.subordinates:
                        if subsubordinate.dead:
                            continue
                        if subsubordinate.reputation > 8000:
                            toForcePromote.append(subsubordinate)
                        for worker in subsubordinate.subordinates:
                            if worker.dead:
                                continue
                            if worker.reputation > 800:
                                toForcePromote.append(worker)

                for character in toForcePromote:
                    if not character.superior:
                        continue

                    character.addMessage("should be force promoted")
                    character.superior.addMessage("should be force demoted")

                    oldBoss = character.superior
                    oldSubordintes = character.subordinates
                    oldRank = character.rank

                    forcePromoted.append("%s (%s) => %s (%s) "%(character.name,character.rank,oldBoss.name,oldBoss.rank))

                    character.superior = oldBoss.superior
                    character.subordinates = oldBoss.subordinates
                    character.rank = oldBoss.rank
                    character.reputation = character.reputation//10
                    character.inventory.insert(0,src.items.itemMap["GooFlask"](uses=100))

                    oldBoss.superior = character
                    oldBoss.rank = oldRank
                    oldBoss.subordinates = oldSubordintes
                    oldBoss.reputation = oldBoss.reputation//10

                    if character.superior:
                        character.superior.subordinates.remove(oldBoss)
                        character.superior.subordinates.append(character)
                    else:
                        self.leaders[cityLocation] = character
                        character.quests = oldBoss.quests

                        oldBoss.quests = []
                        quest = src.quests.Serve(superior=character)
                        quest.activate()
                        quest.assignToCharacter(character)
                        oldBoss.assignQuest(quest,active=True)

                    character.subordinates.remove(character)
                    character.subordinates.append(oldBoss)

            if cityLeader.faction == src.gamestate.gamestate.mainChar.faction:
                showText("""
promotions this round:

forcePromoted: %s
toKill: %s

press space to continue"""%(forcePromoted,toKill))

            if toKill or forcePromoted:
                    cityLeader = self.leaders[cityLocation]
                    if cityLeader.faction == src.gamestate.gamestate.mainChar.faction:

                        if 1==1:
                            def getname(character):
                                if character == None or character.dead:
                                    return ""
                                name = character.name.split(" ")[0][0]+". "+character.name.split(" ")[1]
                                if character == src.gamestate.gamestate.mainChar:
                                    name = "== "+name+" =="
                                return name

                            
                            rowwidth = 17

                            infogrid = []
                            for i in range(0,9*6*2):
                                infogrid.append(" "*rowwidth)

                            infogrid[4] = cityLeader.name+" "*(rowwidth-len(cityLeader.name))

                            cityLeaderSubordinates = cityLeader.subordinates
                            while len(cityLeaderSubordinates) < 3:
                                cityLeaderSubordinates.append(None)

                            row2Counter = 0
                            row3Counter = 0
                            for subleader in cityLeaderSubordinates:
                                if subleader and not subleader.dead:
                                    infogrid[2*9+1+row2Counter*3] = getname(subleader)+" "*(rowwidth-len(getname(subleader)))
                                    infogrid[3*9+1+row2Counter*3] = str(subleader.reputation)+" "*(rowwidth-len(str(subleader.reputation)))
                                    subleaderSubordinates = subleader.subordinates
                                else:
                                    subleaderSubordinates = [None,None,None]
                        
                                while len(subleaderSubordinates) < 3:
                                    subleaderSubordinates.append(None)

                                for subsubleader in subleaderSubordinates:
                                    if subsubleader and not subsubleader.dead:
                                        infogrid[4*9+row3Counter] = getname(subsubleader)+" "*(rowwidth-len(getname(subsubleader)))
                                        infogrid[5*9+row3Counter] = str(subsubleader.reputation)+" "*(rowwidth-len(str(subsubleader.reputation)))
                                        subsubleaderSubordinates = subsubleader.subordinates
                                    else:
                                        infogrid[4*9+row3Counter] = " "*rowwidth
                                        infogrid[5*9+row3Counter] = " "*rowwidth
                                        subsubleaderSubordinates = [None,None,None]
                                    lineCounter = 0

                                    while len(subsubleaderSubordinates) < 3:
                                        subsubleaderSubordinates.append(None)
                                        
                                    for worker in subsubleaderSubordinates:
                                        if worker and not worker.dead:
                                            infogrid[(2+1+lineCounter)*2*9+row3Counter] = getname(worker)+" "*(rowwidth-len(getname(worker)))
                                            infogrid[((2+1+lineCounter)*2+1)*9+row3Counter] = str(worker.reputation)+" "*(rowwidth-len(str(worker.reputation)))
                                        else:
                                            infogrid[(2+1+lineCounter)*2*9+row3Counter] = " "*rowwidth
                                            infogrid[((2+1+lineCounter)*2+1)*9+row3Counter] = " "*rowwidth
                                        lineCounter += 1
                                    row3Counter += 1
                                row2Counter += 1

                            reputationTree = """
cityleader:   """+"%s   "*9+"""
              """+"%s   "*9+"""
subleaders:   """+"%s   "*9+"""
              """+"%s   "*9+"""
squadleaders: """+"%s   "*9+"""
              """+"%s   "*9+"""

workers:      """+"%s   "*9+"""
              """+"%s   "*9+"""
workers:      """+"%s   "*9+"""
              """+"%s   "*9+"""
workers:      """+"%s   "*9+"""
              """+"%s   "*9+"""
"""
                            reputationTree = reputationTree%tuple(infogrid)

                            showText("""
a new epoch has started!

the new reputation is:
%s

press space to continue"""%(reputationTree))

        for cityLocation in self.citylocations:
            if not cityLocation in toFetchMap or not toFetchMap[cityLocation]:
                self.leaderQuests[cityLocation].setPriorityObtain(7,(7,7),epochLength=self.epochLength)
                continue
            self.leaderQuests[cityLocation].setPriorityObtain(toFetchMap[cityLocation],specialItemPositions[toFetchMap[cityLocation]],epochLength=self.epochLength)

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + self.epochLength)
        event.setCallback({"container": self, "method": "endEpoch"})
        terrain.addEvent(event)

        locatedItems.sort()

        if self.firstEpoch:
            self.firstEpoch = False

    def endEpoch(self):
        self.startNewEpoch()

class Tutorials(BasicPhase):
    def __init__(self, seed=0):
        super().__init__("Tutorials", seed=seed)

    def start(self, seed=0, difficulty=None):
        """
            basic usage: movement + basic UI + item management
            fighting: some explanaition on fighting + arena?
            industry: how things are produced
            ghuls: how to use ghuls and commands
        """
        options = [("BasicUsageTutorial", "basic usage"), ("FightingTutorial", "fighting"),("Siege2","start main game")]
        submenu = src.interaction.SelectionMenu(
            "what do you want to know more about?\n(press w/s to change selection. press enter/space/d/j to select)\n", options,
            targetParamName="tutorialToStart",
        )
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.macroState["submenue"].followUp = {
            "container": self,
            "method": "startTutorial",
            "params": {}
        }

        mainChar = src.gamestate.gamestate.mainChar

        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addCharacter(
            src.gamestate.gamestate.mainChar, 124, 109
        )


        mainChar.runCommandString(".",nativeKey=True)

    def startTutorial(self,extraInfo):
        if not "tutorialToStart" in extraInfo:
            self.restartTutorial()
            return

        if extraInfo["tutorialToStart"] == "Siege2":
            nextPhase = Siege2()
            nextPhase.start()
            return

        if extraInfo["tutorialToStart"] == "BasicUsageTutorial":
            nextPhase = BasicUsageTutorial()
            nextPhase.start()
            return

        if extraInfo["tutorialToStart"] == "FightingTutorial":
            nextPhase = FightingTutorial()
            nextPhase.start()
            return

        submenu = src.interaction.TextMenu("NIY")
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.macroState["submenue"].followUp = {
            "container": self,
            "method": "restartTutorial",
        }

    def restartTutorial(self):
        nextPhase = Tutorials()
        nextPhase.start()

class FightingTutorial(BasicPhase):
    """
    """

    def __init__(self, seed=0):
        super().__init__("FightingTutorial", seed=seed)

        self.enemies = []

    def start(self, seed=0, difficulty=None):
        src.gamestate.gamestate.terrainMap[7][7] = src.terrains.Nothingness()
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addCharacter(
            src.gamestate.gamestate.mainChar, 124, 109
        )

        text = """
This tutorial will explain how fighting works in this game.

it will explain:
 * how to attack
 * health and healing
 * weapons and armor
 * weapons and armor quality
 * environments in fights
 * not to fight

press space to start
"""
        src.gamestate.gamestate.mainChar.addMessage(text)

        src.gamestate.gamestate.mainChar.solvers.append("NaiveMurderQuest")
        src.gamestate.gamestate.mainChar.solvers.append("NaiveActivateQuest")
        src.gamestate.gamestate.mainChar.personality["autoFlee"] = False
        src.gamestate.gamestate.mainChar.personality["abortMacrosOnAttack"] = False
        src.gamestate.gamestate.mainChar.personality["autoCounterAttack"] = False

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.macroState["submenue"].followUp = {
            "container": self,
            "method": "tutorialHowToAttack",
        }

    def tutorialHowToAttack(self):
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]

        src.gamestate.gamestate.mainChar.health = 99
        
        enemy = src.characters.Monster(4,4)
        enemy.health = 10
        enemy.baseDamage = 10
        enemy.maxHealth = 10
        enemy.godMode = True

        self.enemies.append(enemy)

        currentTerrain.addCharacter(enemy, 8*15+9, 7*15+8)

        text = """
Attacking is pretty simple, you move into an enemy and you will attack that enemy.

I spawned an enemy nearby. It looks something like <- 

Kill it.

press space to fight

reminder:
 * press x to see message log
 * press v to see your characters stats
"""
        src.gamestate.gamestate.mainChar.addMessage(text)
        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

        self.tutorialCheckFirstFight()

    def tutorialCheckFirstFight(self):
        if not self.enemies[0].dead:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "tutorialCheckFirstFight"})
            src.gamestate.gamestate.mainChar.container.addEvent(event)
        else:
            self.tutorialHowToHeal()

    def tutorialHowToHeal(self):
        mainChar = src.gamestate.gamestate.mainChar
        charPos = mainChar.getBigPosition()

        item = src.items.itemMap["GooFlask"]()
        item.uses = 100
        mainChar.container.addItem(item,(charPos[0]*15+5,charPos[1]*15+6,0))

        item = src.items.itemMap["Vial"]()
        item.uses = 10
        mainChar.container.addItem(item,(charPos[0]*15+5,charPos[1]*15+5,0))

        text = """
On top of the screen you should see a health bar. 
You should see that you have lost some heath.

There are 2 main healing items in this game:

Goo flasks are usually used for food, but also heal 1 health each time you drink.
Vials are dedicated healing items and heal 10 health per usage.

I droped some healing items nearby. Heal yourself using these.

press space to start healing

reminder:
 * press j to use items
"""
        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

        self.tutorialCheckHeal()

    def tutorialCheckHeal(self):
        if not src.gamestate.gamestate.mainChar.health == 100:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "tutorialCheckHeal"})
            src.gamestate.gamestate.mainChar.container.addEvent(event)
        else:
            self.tutorialWeapons()

    def tutorialWeapons(self):
        mainChar = src.gamestate.gamestate.mainChar
        charPos = mainChar.getBigPosition()

        item = src.items.itemMap["Sword"]()
        item.baseDamage = 15
        mainChar.container.addItem(item,(charPos[0]*15+8,charPos[1]*15+9,0))

        item = src.items.itemMap["Armor"]()
        item.armorValue = 2
        mainChar.container.addItem(item,(charPos[0]*15+8,charPos[1]*15+10,0))

        text = """
As you can imagine fighting with weapons and armor will be more effective.

Swords are the common weapons and are shown as wt.
Armor is shown as ar.

I dropped a sword and armor nearby.
Equip those by using them.

press space to start equiping

reminder:
 * press v to see your character stats
 * press j to use items
 * press j to use items
"""
        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

        self.tutorialCheckWeapon()

    def tutorialCheckWeapon(self):
        if not (src.gamestate.gamestate.mainChar.weapon and src.gamestate.gamestate.mainChar.armor):
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "tutorialCheckWeapon"})
            src.gamestate.gamestate.mainChar.container.addEvent(event)
        else:
            self.tutorialWeapongrades()

    def tutorialWeapongrades(self):
        mainChar = src.gamestate.gamestate.mainChar
        charPos = mainChar.getBigPosition()

        item = src.items.itemMap["Sword"]()
        item.baseDamage = 20
        mainChar.container.addItem(item,(charPos[0]*15+2,charPos[1]*15+2,0))

        item = src.items.itemMap["Sword"]()
        item.baseDamage = 19
        mainChar.container.addItem(item,(charPos[0]*15+2,charPos[1]*15+3,0))

        item = src.items.itemMap["Sword"]()
        item.baseDamage = 17
        mainChar.container.addItem(item,(charPos[0]*15+2,charPos[1]*15+4,0))

        item = src.items.itemMap["Sword"]()
        item.baseDamage = 25
        mainChar.container.addItem(item,(charPos[0]*15+2,charPos[1]*15+5,0))

        item = src.items.itemMap["Sword"]()
        item.baseDamage = 18
        mainChar.container.addItem(item,(charPos[0]*15+2,charPos[1]*15+6,0))


        item = src.items.itemMap["Armor"]()
        item.armorValue = 2
        mainChar.container.addItem(item,(charPos[0]*15+3,charPos[1]*15+2,0))
        
        item = src.items.itemMap["Armor"]()
        item.armorValue = 5
        mainChar.container.addItem(item,(charPos[0]*15+3,charPos[1]*15+3,0))

        item = src.items.itemMap["Armor"]()
        item.armorValue = 3
        mainChar.container.addItem(item,(charPos[0]*15+3,charPos[1]*15+4,0))

        item = src.items.itemMap["Armor"]()
        item.armorValue = 4
        mainChar.container.addItem(item,(charPos[0]*15+3,charPos[1]*15+5,0))

        item = src.items.itemMap["Armor"]()
        item.armorValue = 1
        mainChar.container.addItem(item,(charPos[0]*15+3,charPos[1]*15+6,0))


        text = """
Weapons and armor have different qualities.
Those qualities determine how hard a sword hits or how much damage armor absorbs.

Those stats can be seen in 3 ways:
 * examining the item
 * in the message log when equiping it
 * in the character stats when equipped

When equipping a weapon or armor you drop the one you are currently wearing.

I dropped some swords and armor nearby.
Equip the best of each.

press space to start equiping

reminder:
 * press v to see your character stats
 * press e to examine items
"""
        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

        self.tutorialCheckWeapongrades()

    def tutorialCheckWeapongrades(self):
        if not ((src.gamestate.gamestate.mainChar.weapon and src.gamestate.gamestate.mainChar.weapon.baseDamage == 25) and 
                (src.gamestate.gamestate.mainChar.armor and src.gamestate.gamestate.mainChar.armor.armorValue == 5)):
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "tutorialCheckWeapongrades"})
            src.gamestate.gamestate.mainChar.container.addEvent(event)
        else:
            self.tutorialCombatEnvironment()

    def tutorialCombatEnvironment(self):
        mainChar = src.gamestate.gamestate.mainChar
        charPos = mainChar.getBigPosition()

        mainChar.weapon = None
        mainChar.armor = None

        container = mainChar.container
        container.removeCharacter(mainChar)

        src.gamestate.gamestate.terrainMap[7][7] = src.terrains.Nothingness()
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addCharacter(
            mainChar,charPos[0]*15+10,charPos[1]*15+4
        )

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+8,charPos[1]*15+3,0))
        
        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+9,charPos[1]*15+3,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+10,charPos[1]*15+3,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+11,charPos[1]*15+3,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+11,charPos[1]*15+4,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+11,charPos[1]*15+5,0))

        item = src.items.itemMap["Scrap"](amount=5)
        mainChar.container.addItem(item,(charPos[0]*15+11,charPos[1]*15+6,0))

        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+8,charPos[1]*15+5,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+9,charPos[1]*15+5,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+9,charPos[1]*15+6,0))
        
        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+8,charPos[1]*15+6,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+7,charPos[1]*15+6,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+6,charPos[1]*15+6,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+5,charPos[1]*15+6,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+4,charPos[1]*15+6,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+3,charPos[1]*15+6,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+2,charPos[1]*15+6,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+8,charPos[1]*15+9,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+7,charPos[1]*15+9,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+6,charPos[1]*15+9,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+5,charPos[1]*15+9,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+4,charPos[1]*15+9,0))

        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+3,charPos[1]*15+9,0))

        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+9,charPos[1]*15+7,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+8,charPos[1]*15+7,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+6,charPos[1]*15+8,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+4,charPos[1]*15+7,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+2,charPos[1]*15+8,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+2,charPos[1]*15+9,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+2,charPos[1]*15+9,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+7,charPos[1]*15+3,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+6,charPos[1]*15+2,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+7,charPos[1]*15+1,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+5,charPos[1]*15+1,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+4,charPos[1]*15+2,0))
        
        item = src.items.itemMap["LandMine"]()
        mainChar.container.addItem(item,(charPos[0]*15+3,charPos[1]*15+1,0))
        
        item = src.items.itemMap["Scrap"](amount=20)
        mainChar.container.addItem(item,(charPos[0]*15+6,charPos[1]*15+3,0))

        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]

        enemies = []
        for pos in ((8,2),(10,2),(12,2),(12,4),(12,6),):
            enemy = src.characters.Monster(4,4)
            enemy.health = 10
            enemy.baseDamage = 10
            enemy.maxHealth = 10
            enemy.godMode = True

            quest = src.quests.SecureTile(toSecure=charPos)
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

            self.enemies.append(enemy)

            currentTerrain.addCharacter(enemy, charPos[0]*15+pos[0], charPos[1]*15+pos[1])

        text = """
Combats rarely happen in empty spaces.
Usually there are scrap piles, machines or other things in the way.
You can use those to block off enemies and keep them busy for a while.

There are other items that effect fighting. Landmines for example.
You should not step on them, but if you can make enemies step onto them they might be useful.

I spawned some scrap, random items, landmines and enemies on this field.
Also i took your weapos away to make the fight more fair.

Kill the enemies and try to use the environment to your advantage.

press space to start killing

"""
        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

        self.tutorialCheckFight2()

    def tutorialCheckFight2(self):
        foundSurvivor = False
        for enemy in self.enemies:
            if not enemy.dead:
                foundSurvivor = True

        if foundSurvivor:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "tutorialCheckFight2"})
            src.gamestate.gamestate.mainChar.container.addEvent(event)
        else:
            self.tutorialHowToNotFight()

class BasicUsageTutorial(BasicPhase):
    """
    """

    def __init__(self, seed=0):
        super().__init__("BasicUsageTutorial", seed=seed)

    def start(self, seed=0, difficulty=None):
        src.gamestate.gamestate.terrainMap[7][7] = src.terrains.Nothingness()
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addCharacter(
            src.gamestate.gamestate.mainChar, 124, 109
        )

        text = """
This tutorial will explain the basic interaction with the program.

it will explain:

 * the help menu
 * movement
 * how to pick things up
 * how to show the inventory
 * how to drop things
 * how to activate things
 * how to dock menus

press space to start
"""
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.doesOwnAction = False
        src.gamestate.gamestate.timedAutoAdvance = 1

        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.macroState["submenue"].followUp = {
            "container": self,
            "method": "tutorialExplainHelp",
        }


        # add basic set of abilities in openworld phase
        src.gamestate.gamestate.mainChar.questsDone = [
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "CollectQuestMeta",
            "FireFurnaceMeta",
            "ExamineQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
            "LeaveRoomQuest",
        ]

        src.gamestate.gamestate.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]
        src.gamestate.gamestate.mainChar.godMode = True
        src.gamestate.gamestate.mainChar.inventory = []

    def tutorialExplainHelp(self):
        mainChar = src.gamestate.gamestate.mainChar

        text = """
The keybindings are shown with some other information in the help menu.
If you only remember one thing, remember that the help menu exists.

You can open the help menu by:

 * pressing z
 * clicking the "press z for help" on the top of the screen
 * pressing ESC to open the main menu and selecting help

Please open the help menu and close it again by pressing ESC or clicking the X in the subwindow.

press space when you are ready.
"""
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

        mainChar.addListener(self.checkTutorialHelpClosed, "closedHelp")

    def checkTutorialHelpClosed(self):
        src.gamestate.gamestate.mainChar.delListener(self.checkTutorialHelpClosed, "closedHelp")
        self.tutorialExplainMessageLog()
        return

    def tutorialExplainMessageLog(self):
        text = """
Another menu that might be important is the message log.
Press x to open it.

Usually it shows the combat log and similar stuff. 
In this tutorial it also shows the instructions this tutorial ave you.
So press x, if you forget what you were supposed to do.

Please open and close the message menu.

press space when you are ready
"""
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)

        src.gamestate.gamestate.mainChar.addListener(self.checkTutorialMessageLogClosed, "closedMessages")

        return

    def checkTutorialMessageLogClosed(self):
        self.tutorialExplainMovement()
        src.gamestate.gamestate.mainChar.delListener(self.checkTutorialMessageLogClosed, "closedMessages")
        return

    def tutorialExplainMovement(self):
        mainChar = src.gamestate.gamestate.mainChar

        text = """
ok, great. Now lets get to something more exciting.

you can move around by using the wasd keys.

 * w = move a step north
 * a = move a step west
 * s = move a step south
 * d = move a step east

please move around a bit now.

press space when you are ready
"""
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        self.tutorialCheckMovement({"count":0,"lastPos":list(mainChar.getPosition())})

        mainChar.runCommandString(".",nativeKey=True)

    def tutorialCheckMovement(self,extraInfo=None):
        mainChar = src.gamestate.gamestate.mainChar

        if not tuple(extraInfo["lastPos"]) == mainChar.getPosition():
            extraInfo["count"] += 1
        extraInfo["lastPos"] = list(mainChar.getPosition())

        if extraInfo["count"] < 10:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "tutorialCheckMovement","params":extraInfo})
            mainChar.container.addEvent(event)
        else:
            self.tutorialExplainPickUp()

    def tutorialExplainPickUp(self):
        mainChar = src.gamestate.gamestate.mainChar

        text = """
great. That seems to work out fine.

now lets pick some stuff up.
This is more complicated that it seems and there a 3 ways to do that.

 * move onto a small item and press k
 * move against a big item and press k directly afterwards
 * move next to an item and press K and a direction (wasd) afterwards

I spawned 4 pieces of scrap and a wall nearby. Pick them up to proceed.

remember to press z if you forget the keybindings
        """
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

        mainChar.runCommandString(".",nativeKey=True)

        characterPos = mainChar.getPosition()
        baseX = characterPos[0]//15
        baseY = characterPos[1]//15

        for i in range(0,4):
            scrap = src.items.itemMap["Scrap"](amount=1)
            mainChar.container.addItem(scrap,(baseX*15+random.randint(1,11),baseY*15+random.randint(1,11),0))
        wall = src.items.itemMap["Wall"]()
        wall.bolted = False
        mainChar.container.addItem(wall,(baseX*15+random.randint(1,11),baseY*15+random.randint(1,11),0))

        self.tutorialCheckPickUp()

    def tutorialCheckPickUp(self):
        mainChar = src.gamestate.gamestate.mainChar

        numScrapFound = 0
        numWallFound = 0
        for item in mainChar.inventory:
            if item.type == "Scrap":
                numScrapFound += 1
            if item.type == "Wall":
                numWallFound += 1

        if not (numScrapFound > 3 and numWallFound > 0):
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "tutorialCheckPickUp"})
            mainChar.container.addEvent(event)
        else:
            self.tutorialExplainInventory()

    def tutorialExplainInventory(self):
        text = """
all the items you have collected go into your inventory.

You can open your inventory by pressing i and close it by pressing ESC.

I trust that you will be able to handle that.

other menus you can open are:
 c for character overview
 q for quests

press space to continue with dropping items.
        """
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.macroState["submenue"].followUp = {
            "container": self,
            "method": "tutorialExplainDrop",
        }
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)

    def tutorialExplainDrop(self):
        text = """
dropping an item can also be done in multiple ways.

you can
 * press l to drop an item where you stand
 * press L and direction (wasd) afterwards to drop an item nearby
 * use the inventory menu to drop a specific item

The item picked up last is the item that will be dropped when pressing l or L

now drop the items onto the floor again."""
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)

        self.tutorialCheckDrop()

    def tutorialCheckDrop(self):
        mainChar = src.gamestate.gamestate.mainChar

        if src.gamestate.gamestate.mainChar.inventory:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "tutorialCheckDrop"})
            mainChar.container.addEvent(event)
        else:
            self.tutorialExplainTestActivate()

    def tutorialExplainTestActivate(self):
        mainChar = src.gamestate.gamestate.mainChar

        text = """
other important interaction methods are activating and examining items.

It mostly works like picking up or dropping items.

 * press j to activate an item you stand on
 * walk against a big item and press j to activate it
 * press J and a direction (wasd) to activate a nearby item
 * use the inventory menu to activate a specific item

 * press e to examine an item 
 * walk against a big item and press e to examine it
 * press E and a direction (wasd) to examine a nearby item

Activating items is obviously important.
Examining an item often gives instructions how to use an item.
So remember to examine items you don't understand.

i dropped a combination lock nearby.
examine it and activate it.
        """
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)

        storyItem = src.items.itemMap["FunctionTrigger"]()
        storyItem.bolted = False
        storyItem.walkable = True
        storyItem.description = "combination lock"
        storyItem.name = "combination lock"
        storyItem.usageInfo = "activate the item and input the code 3798"
        storyItem.display = "cl"
        storyItem.function = {"container":self,"method":"getActivateCode"}
        
        characterPos = mainChar.getPosition()
        baseX = characterPos[0]//15
        baseY = characterPos[1]//15

        mainChar.container.addItem(storyItem,(baseX*15+7,baseY*15+7,0))

    def getActivateCode(self):
        submenu = src.interaction.InputMenu("Enter the code:",ignoreFirst=True)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.macroState["submenue"].followUp = {
                "container": self,
                "method": "checkActivateCode",
                "params":{}
            }

    def checkActivateCode(self, extraInfo):
        if not "text" in extraInfo or not extraInfo["text"] == "3798":
            submenu = src.interaction.TextMenu("wrong code - examine the combination lock for instructions. press z to view keybindings")
            src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
            return
        self.tutorialExplainDocking()

    def tutorialExplainDocking(self):
        mainChar = src.gamestate.gamestate.mainChar
        text = """
that worked, awesome. 

I'm sure you noticed that opening and closing the inventory can get annoying fast.
To solve this, the game offers you to dock menus to the left and right of the game map.

To do this, you first open the inventory menu.
Then you click the < arrow of the subwindow or press left_shift + ESC to dock the window to the left.
Clicking the > arrow of the subwindow or pressing right_shift + ESC will dock the window to the right.

please press space and then dock the inventory menu.

(the current window can't be docked)
"""
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)

        self.checkDocking()

    def checkDocking(self):
        mainChar = src.gamestate.gamestate.mainChar

        if (mainChar.rememberedMenu or mainChar.rememberedMenu2):
            self.tutorialRequestFill()
            return
        else:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "checkDocking"})
            mainChar.container.addEvent(event)

    def tutorialRequestFill(self):

        text = """
Please fill your inventory now to see it in action

press space to start
"""
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)

        characterPos = src.gamestate.gamestate.mainChar.getPosition()
        baseX = characterPos[0]//15
        baseY = characterPos[1]//15

        for i in range(0,30):
            scrap = src.items.itemMap["Scrap"](amount=1)
            src.gamestate.gamestate.mainChar.container.addItem(scrap,(baseX*15+random.randint(1,11),baseY*15+random.randint(1,11),0))

        self.checkFilled()

    def checkFilled(self):
        mainChar = src.gamestate.gamestate.mainChar

        if len(mainChar.inventory) > 9:
            self.tutorialExplainUndocking()
            return
        else:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "checkFilled"})
            mainChar.container.addEvent(event)

    def tutorialExplainUndocking(self):

        text = """
One last but pretty important thing and you are done with the tutorial.

to undock menus click the < or > arrow of the docked menu or
press left shift + ESC to undock left or
press right shift + ESC to undock right

undock and close all menus to continue
"""
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)

        self.checkUndocking()

    def checkUndocking(self):
        mainChar = src.gamestate.gamestate.mainChar

        if not (mainChar.rememberedMenu or mainChar.rememberedMenu2) and not mainChar.macroState["submenue"]:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "complete"})
            mainChar.container.addEvent(event)
            src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)
            return
        else:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "checkUndocking"})
            mainChar.container.addEvent(event)

    def complete(self):

        text = """
that was the basic usage. Thanks for participating.

Good luck on your adventures and maybe see you in another tutorial

press space to return to tutorial selection
"""
        src.gamestate.gamestate.mainChar.addMessage(text)

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.macroState["submenue"].followUp = {
                "container": self,
                "method": "restartTutorial",
            }
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)

    def restartTutorial(self):
        nextPhase = Tutorials()
        nextPhase.start()

class BaseBuilding(BasicPhase):
    """
    """

    def __init__(self, seed=0):
        """
        set up super class

        Parameters:
            seed: rng seed
        """

        super().__init__("BaseBuilding", seed=seed)

    def start(self, seed=0, difficulty=None):
        """
        set up terrain and spawn main character

        Parameters:
            seed: rng seed
        """

        showText("build a base.\n\npress space to continue")

        mainChar = src.gamestate.gamestate.mainChar
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addCharacter(
            src.gamestate.gamestate.mainChar, 124, 109
        )

        item = src.items.itemMap["GooFlask"]()
        item.uses = 100
        mainChar.inventory.append(item)

        #src.gamestate.gamestate.setTerrain(src.terrains.TutorialTerrain(),(1,1))
        #src.gamestate.gamestate.setTerrain(src.terrains.Nothingness(),(1,2))
        #src.gamestate.gamestate.setTerrain(src.terrains.GameplayTest(),(1,3))
        #src.gamestate.gamestate.setTerrain(src.terrains.ScrapField(),(1,4))
        #src.gamestate.gamestate.setTerrain(src.terrains.Desert(),(1,5))
        #src.gamestate.gamestate.setTerrain(src.terrains.TutorialTerrain(),(1,6))
        src.gamestate.gamestate.setTerrain(src.terrains.Ruin(),(1,7))
        src.gamestate.gamestate.setTerrain(src.terrains.Base(),(1,8))
        src.gamestate.gamestate.setTerrain(src.terrains.Base2(),(1,9))

        item = src.items.itemMap["ItemCollector"]()
        mainChar.inventory.append(item)

        items = []

        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.bolted = False
        item.godMode = True
        items.append((item, (15 * 8 + 8, 15 * 8 + 9, 0)))

        item = src.items.itemMap["RoadManager"]()
        roadManager = item
        item.bolted = False
        item.godMode = True
        items.append((item, (15 * 8 + 8, 15 * 8 + 8, 0)))

        item = src.items.itemMap["ProductionArtwork"]()
        item.bolted = False
        item.godMode = True
        items.append((item, (15 * 8 + 8, 15 * 8 + 10, 0)))

        currentTerrain.addItems(items)

        # add basic set of abilities in openworld phase
        src.gamestate.gamestate.mainChar.questsDone = [
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "CollectQuestMeta",
            "FireFurnaceMeta",
            "ExamineQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
            "LeaveRoomQuest",
        ]

        src.gamestate.gamestate.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]
        src.gamestate.gamestate.mainChar.macroState["macros"]["j"] = ["J", "f"]
        src.gamestate.gamestate.mainChar.godMode = True
        src.gamestate.gamestate.mainChar.faction = "german-sibiria"

        """
        architect.doAddScrapfield(10, 8, 280)
        architect.doAddScrapfield(10, 6, 280)
        architect.doAddScrapfield(10, 7, 280)
        """
        architect.doAddScrapfield(9, 7, 280)

        mainRoom = architect.doAddRoom(
                {
                       "coordinate": (7,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )
        src.gamestate.gamestate.mainChar.registers["HOMEx"] = 7
        src.gamestate.gamestate.mainChar.registers["HOMEy"] = 7
        mainRoom.storageRooms = []

        questArtwork = src.items.itemMap["QuestArtwork"]()
        questArtwork.bolted = True
        mainRoom.addItem(questArtwork, (1, 4, 0))

        cityBuilder = src.items.itemMap["CityBuilder2"]()
        cityBuilder.bolted = True
        cityBuilder.godMode = True
        cityBuilder.architect = architect
        cityBuilder.scrapFields = currentTerrain.scrapFields
        for scrapField in cityBuilder.scrapFields:
            mainRoom.sources.append((scrapField,"Scrap"))
        mainRoom.addItem(cityBuilder, (6, 6, 0))
        cityBuilder.registerRoom(mainRoom)

        tradingArtwork = src.items.itemMap["TradingArtwork2"]()
        cityBuilder.bolted = True
        mainRoom.addItem(tradingArtwork, (9, 9, 0))
        tradingArtwork.configure(src.gamestate.gamestate.mainChar)

        dutyArtwork = src.items.itemMap["DutyArtwork"]()
        mainRoom.addItem(dutyArtwork, (1, 3, 0))

        mainRoom.addInputSlot((7,8,0),"Scrap")
        mainRoom.addInputSlot((8,7,0),"Scrap")
        mainRoom.addInputSlot((9,8,0),"MetalBars")

        mainRoom.addOutputSlot((11,8,0),"MetalBars")
        mainRoom.addOutputSlot((11,7,0),"ScrapCompactor")
        mainRoom.addOutputSlot((11,9,0),"Painter")
        mainRoom.addOutputSlot((11,10,0),"Sheet")
        mainRoom.addOutputSlot((10,11,0),"CorpseAnimator")
        mainRoom.addOutputSlot((9,11,0),"Corpse")
        mainRoom.addOutputSlot((8,11,0),"ScratchPlate")

        for i in range(0,10):
            item = src.items.itemMap["Painter"]()
            mainRoom.addItem(item,(11,9,0))

        mainRoom.addStorageSlot((1,7,0),None)
        mainRoom.addStorageSlot((1,8,0),None)
        mainRoom.addStorageSlot((1,9,0),None)
        mainRoom.addStorageSlot((1,10,0),None)
        mainRoom.addStorageSlot((1,11,0),None)

        mainRoom.walkingSpace.add((2,7,0))
        mainRoom.walkingSpace.add((2,8,0))
        mainRoom.walkingSpace.add((2,9,0))
        mainRoom.walkingSpace.add((2,10,0))
        mainRoom.walkingSpace.add((2,11,0))

        mainRoom.walkingSpace.add((7,7,0))
        mainRoom.walkingSpace.add((10,7,0))
        mainRoom.walkingSpace.add((10,8,0))
        mainRoom.walkingSpace.add((10,9,0))
        mainRoom.walkingSpace.add((10,10,0))
        mainRoom.walkingSpace.add((9,10,0))
        mainRoom.walkingSpace.add((8,10,0))
        mainRoom.walkingSpace.add((7,10,0))

        mainRoom.sources.append((mainRoom.getPosition(),"ScrapCompactor"))
        mainRoom.sources.append((mainRoom.getPosition(),"MetalBars"))
        mainRoom.sources.append((mainRoom.getPosition(),"Painter"))
        mainRoom.sources.append((mainRoom.getPosition(),"Sheet"))
        mainRoom.sources.append((mainRoom.getPosition(),"CorpseAnimator"))
        mainRoom.sources.append((mainRoom.getPosition(),"Corpse"))
        mainRoom.sources.append((mainRoom.getPosition(),"ScratchPlate"))

        mainRoom.addRandomItems()

        #cityBuilder.addScrapCompactorFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,7),"type":"random"})
        #cityBuilder.spawnRank3(src.gamestate.gamestate.mainChar)
        #cityBuilder.spawnRank4(src.gamestate.gamestate.mainChar)
        #cityBuilder.spawnRank5(src.gamestate.gamestate.mainChar)
        #cityBuilder.spawnRank6(src.gamestate.gamestate.mainChar)

class Siege2(BasicPhase):
    """
    """

    def __init__(self, seed=0):
        """
        set up super class

        Parameters:
            seed: rng seed
        """

        super().__init__("BaseBuilding2", seed=seed)

    def start(self, seed=0, difficulty=None):
        """
        set up terrain and spawn main character

        Parameters:
            seed: rng seed
        """

        print("phase difficulty:")
        print(difficulty)
        self.difficulty = difficulty

        mainChar = src.gamestate.gamestate.mainChar
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        
        questMenu = src.interaction.QuestMenu(mainChar)
        mainChar.rememberedMenu.append(questMenu)
        messagesMenu = src.interaction.MessagesMenu(mainChar)
        mainChar.rememberedMenu2.append(messagesMenu)

        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.bolted = False
        item.godMode = True
        currentTerrain.addItem(item,(1,1,0))

        self.epochLength = 1000

        numGuards = 10
        baseHealth = 100
        self.baseMovementSpeed = 0.8
        if difficulty == "easy":
            numGuards = 5
            baseHealth = 25
            self.baseMovementSpeed = 1.1
        if difficulty == "difficult":
            numGuards = 30
            baseHealth = 200
            self.baseMovementSpeed = 0.5

        # add basic set of abilities in openworld phase
        src.gamestate.gamestate.mainChar.questsDone = [
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "CollectQuestMeta",
            "FireFurnaceMeta",
            "ExamineQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
            "LeaveRoomQuest",
        ]

        src.gamestate.gamestate.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]
        src.gamestate.gamestate.mainChar.macroState["macros"]["j"] = ["J", "f"]
        src.gamestate.gamestate.mainChar.godMode = True
        src.gamestate.gamestate.mainChar.faction = "city test"
        if difficulty == "easy":
            src.gamestate.gamestate.mainChar.baseDamage = 5
            src.gamestate.gamestate.mainChar.health = 200
            src.gamestate.gamestate.mainChar.maxHealth = 200
        if difficulty == "difficult":
            src.gamestate.gamestate.mainChar.baseDamage = 2
            src.gamestate.gamestate.mainChar.health = 50
            src.gamestate.gamestate.mainChar.maxHealth = 50

        mainRoom = architect.doAddRoom(
                {
                       "coordinate": (7,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )
        mainRoom.storageRooms = []

        spawnRoom = architect.doAddRoom(
                {
                       "coordinate": (7,13),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None)

        src.gamestate.gamestate.mainChar.registers["HOMEx"] = spawnRoom.xPosition
        src.gamestate.gamestate.mainChar.registers["HOMEy"] = spawnRoom.yPosition
        
        for x in range(1,6):
            item = src.items.itemMap["Sword"]()
            spawnRoom.addItem(item,(x,1,0))

            item = src.items.itemMap["Armor"]()
            spawnRoom.addItem(item,(x,3,0))

            item = src.items.itemMap["MetalBars"]()
            spawnRoom.addItem(item,(x,5,0))

            item = src.items.itemMap["MetalBars"]()
            spawnRoom.addItem(item,(x+6,5,0))

            item = src.items.itemMap["GooFlask"]()
            spawnRoom.addItem(item,(x,7,0))
            item = src.items.itemMap["GooFlask"]()
            spawnRoom.addItem(item,(x+6,7,0))
            item.uses = random.randint(2,12)

            item = src.items.itemMap["Bolt"]()
            spawnRoom.addItem(item,(x,9,0))

            item = src.items.itemMap["Bolt"]()
            spawnRoom.addItem(item,(x+6,9,0))

            item = src.items.itemMap["Scrap"]()
            spawnRoom.addItem(item,(x,11,0))

            item = src.items.itemMap["Bomb"]()
            spawnRoom.addItem(item,(x+6,11,0))

        for i in range(1,20):
            spawnRoom.damage()

        spawnRoom.addCharacter(
            src.gamestate.gamestate.mainChar, 6, 6
        )

        text = """
You are ambushed and you need to flee.

Try to reach the safety of the base in the north.


Press ESC to close this window.
"""
        submenu = src.interaction.TextMenu(text)
        submenu.followUp = {"container": self, "method": "showSecondText"}
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

        mainChar.personality["autoFlee"] = False
        mainChar.personality["abortMacrosOnAttack"] = False
        mainChar.personality["autoCounterAttack"] = False

        mainChar.runCommandString(".",nativeKey=True)


        cityBuilder = src.items.itemMap["CityBuilder2"]()
        cityBuilder.architect = architect
        mainRoom.addItem(cityBuilder,(7,1,0))
        cityBuilder.registerRoom(mainRoom)

        farmPositions = [(2,2),(4,2),(2,4),(10,2),(12,2),(12,4),(2,10),(4,12),(2,12),(12,10),(10,12),(12,12),  (4,4),(4,10),(10,4),(10,10)]
        farmPositions = [(2,2),(4,2),(2,4),(10,2),(12,2),(12,4),(2,10),(4,12),(2,12),(12,10),(10,12),(12,12),]

        farmPlots = []
        for farmPos in farmPositions:
            architect.doClearField(farmPos[0],farmPos[1])
            farmPlots.extend([
                (farmPos[0]-1,farmPos[1],0),
                (farmPos[0]-1,farmPos[1]-1,0),
                (farmPos[0],farmPos[1]-1,0),
                (farmPos[0]+1,farmPos[1]-1,0),
                (farmPos[0]+1,farmPos[1],0),
                (farmPos[0]+1,farmPos[1]+1,0),
                (farmPos[0],farmPos[1]+1,0),
                (farmPos[0]-1,farmPos[1]+1,0),
                ])

            architect.doClearField(farmPos[0]-1,farmPos[1])
            architect.doClearField(farmPos[0]-1,farmPos[1]-1)
            architect.doClearField(farmPos[0],farmPos[1]-1)
            architect.doClearField(farmPos[0]+1,farmPos[1]-1)
            architect.doClearField(farmPos[0]+1,farmPos[1])
            architect.doClearField(farmPos[0]+1,farmPos[1]+1)
            architect.doClearField(farmPos[0],farmPos[1]+1)
            architect.doClearField(farmPos[0]-1,farmPos[1]+1)
            farm = cityBuilder.addFarmFromMap({"coordinate":farmPos,"character":src.gamestate.gamestate.mainChar},forceSpawn=10)
            for i in range(1,30):
                farm.damage()

        for farmPlot in farmPlots:
            currentTerrain.minimapOverride[farmPlot] = (src.interaction.urwid.AttrSpec("#030", "black"), ",.")

        # add hardcoded treasure rooms
        def addTreasureRoom(pos,itemType):
            treasureRoom = architect.doAddRoom(
                    {
                           "coordinate": pos,
                           "roomType": "EmptyRoom",
                           "doors": "0,6 6,0 12,6 6,12",
                           "offset": [1,1],
                           "size": [13, 13],
                    },
                    None)

            for i in range(1,20):
                treasureRoom.damage()

            for i in range(1,25):
                item = src.items.itemMap[itemType]()
                #treasureRoom.addItem(item,(1,1,0))
            for i in range(1,25):
                item = src.items.itemMap[itemType]()
                #treasureRoom.addItem(item,(2,1,0))
            for i in range(1,25):
                item = src.items.itemMap[itemType]()
                #treasureRoom.addItem(item,(3,1,0))

            for i in range(random.randint(11,17),random.randint(18,25)):
                enemy = src.characters.Monster(4,4)
                enemy.health = 10*i
                enemy.baseDamage = i
                enemy.faction = "invader"
                enemy.godMode = True
                treasureRoom.addCharacter(enemy, random.randint(2,11), random.randint(2,11))

                quest = src.quests.SecureTile(toSecure=treasureRoom.getPosition())
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

        #addTreasureRoom((3,3),"Sword")
        #addTreasureRoom((11,11),"Armor")
        #addTreasureRoom((3,11),"Rod")
        #addTreasureRoom((11,3),"MetalBars")

        cityBuilder.spawnCity(src.gamestate.gamestate.mainChar)

        staffArtwork = src.items.itemMap["StaffArtwork"]()
        mainRoom.addItem(staffArtwork,(1,1,0))

        dutyArtwork = src.items.itemMap["DutyArtwork"]()
        mainRoom.addItem(dutyArtwork,(5,1,0))
        
        orderArtwork = src.items.itemMap["OrderArtwork"]()
        mainRoom.addItem(orderArtwork,(3,1,0))

        produtionArtwork = src.items.itemMap["ProductionArtwork"]()
        mainRoom.addItem(produtionArtwork,(3,11,0))

        personnelArtwork = src.items.itemMap["PersonnelArtwork"]()
        mainRoom.addItem(personnelArtwork,(9,1,0))
        personnelArtwork.spawnRank3(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank4(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank5(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank6(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank6(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank6(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank5(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank6(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank6(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank6(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank5(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank6(src.gamestate.gamestate.mainChar)
        personnelArtwork.spawnRank4(src.gamestate.gamestate.mainChar)

        questArtwork = src.items.itemMap["QuestArtwork"]()
        mainRoom.addItem(questArtwork,(1,3,0))

        orderArtwork.assignQuest({"character":src.gamestate.gamestate.mainChar,"questType":"cancel","groupType":"all","amount":0})
        orderArtwork.assignQuest({"character":src.gamestate.gamestate.mainChar,"questType":"BeUsefull","groupType":"rank 6","amount":0})
        
        epochArtwork = src.items.itemMap["EpochArtwork"](self.epochLength)
        self.epochArtwork = epochArtwork
        mainRoom.addItem(epochArtwork,(6,6,0))

        healingEffect = 50
        healthIncrease = 20
        baseDamageEffect = 2
        if difficulty == "easy":
            healingEffect = 100
            healthIncrease = 30
            baseDamageEffect = 3
        if difficulty == "difficult":
            healingEffect = 25
            healthIncrease = 10
            baseDamageEffect = 1
        assimilator = src.items.itemMap["Assimilator"](healingEffect=healingEffect,healthIncrease=healthIncrease,baseDamageEffect=baseDamageEffect)
        self.assimilator = assimilator
        mainRoom.addItem(assimilator,(11,5,0))

        basicTrainer = src.items.itemMap["BasicTrainer"]()
        self.basicTrainer = basicTrainer
        mainRoom.addItem(basicTrainer,(11,7,0))

        """
        miniMech = src.rooms.MiniMech()

        room = src.rooms.EmptyRoom(1,1,2,2)
        room.reconfigure(sizeX=6,sizeY=6,doorPos=[(2,0)])
        room.xPosition = 6
        room.yPosition = 13
        room.addItem(src.items.itemMap["RoomControls"](),(1,1,0))
        room.addItem(src.items.itemMap["Boiler"](),(1,4,0))
        room.addItem(src.items.itemMap["Boiler"](),(2,4,0))
        room.addItem(src.items.itemMap["Furnace"](),(1,3,0))
        room.addItem(src.items.itemMap["Furnace"](),(2,3,0))
        room.addItem(src.items.itemMap["Pile"](),(4,1,0))
        room.addItem(src.items.itemMap["Pile"](),(4,2,0))
        currentTerrain.addRoom(room)
        """

        containerQuest = src.quests.ReachBase()
        src.gamestate.gamestate.mainChar.quests.append(containerQuest)
        containerQuest.assignToCharacter(src.gamestate.gamestate.mainChar)
        containerQuest.activate()
        containerQuest.generateSubquests(src.gamestate.gamestate.mainChar)
        containerQuest.endTrigger = {"container": self, "method": "reachedBase"}

        #orderArtwork = src.items.itemMap["BluePrintingArtwork"]()
        #mainRoom.addItem(orderArtwork,(9,1,0))

        hiveStyles = ["simple","empty","attackHeavy","healthHeavy","single"]
        if difficulty == "easy":
            hiveStyles = ["empty","empty","empty","empty","empty"]
                
        random.shuffle(hiveStyles)

        # add hardcoded treasure rooms
        def addHive(pos):
            room = architect.doAddRoom(
                    {
                           "coordinate": pos,
                           "roomType": "EmptyRoom",
                           "doors": "0,6 6,0 12,6 6,12",
                           "offset": [1,1],
                           "size": [13, 13],
                    },
                    None)


            currentTerrain.minimapOverride[pos] = (src.interaction.urwid.AttrSpec("#484", "black"), "##")

            room.addItem(src.items.itemMap["MonsterSpawner"](),(6,6,0))

            hiveStyle = hiveStyles.pop()
            print(pos)
            print(hiveStyle)
            
            if hiveStyle == "empty":
                pass
            elif hiveStyle == "simple":
                for i in range(1,10):
                    enemy = src.characters.Monster(4,4)
                    enemy.godMode = True
                    enemy.health = 100
                    enemy.baseDamage = 10
                    enemy.faction = "invader"
                    room.addCharacter(enemy,random.randint(2,11),random.randint(2,11))

                    quest = src.quests.SecureTile(toSecure=pos)
                    quest.autoSolve = True
                    quest.assignToCharacter(enemy)
                    quest.activate()
                    enemy.quests.append(quest)
            elif hiveStyle == "attackHeavy":
                for i in range(1,10):
                    enemy = src.characters.Monster(4,4)
                    enemy.godMode = True
                    enemy.health = 10
                    enemy.baseDamage = 30
                    enemy.faction = "invader"
                    room.addCharacter(enemy,random.randint(2,11),random.randint(2,11))

                    quest = src.quests.SecureTile(toSecure=pos)
                    quest.autoSolve = True
                    quest.assignToCharacter(enemy)
                    quest.activate()
                    enemy.quests.append(quest)
            elif hiveStyle == "healthHeavy":
                for i in range(1,10):
                    enemy = src.characters.Monster(4,4)
                    enemy.godMode = True
                    enemy.health = 400
                    enemy.baseDamage = 6
                    enemy.faction = "invader"
                    room.addCharacter(enemy,random.randint(2,11),random.randint(2,11))

                    quest = src.quests.SecureTile(toSecure=pos)
                    quest.autoSolve = True
                    quest.assignToCharacter(enemy)
                    quest.activate()
                    enemy.quests.append(quest)
            elif hiveStyle == "single":
                enemy = src.characters.Monster(4,4)
                enemy.godMode = True
                enemy.health = 400
                enemy.baseDamage = 30
                enemy.faction = "invader"
                room.addCharacter(enemy,random.randint(2,11),random.randint(2,11))

                quest = src.quests.SecureTile(toSecure=pos)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)
            else:
                print(hiveStyle)
                1/0

            neighbours = [(pos[0]-1,pos[1]),(pos[0]+1,pos[1]),(pos[0],pos[1]-1),(pos[0],pos[1]+1)]
            fillMaterial = ["EncrustedBush","Bush","Sprout2"]
            if difficulty == "easy":
                fillMaterial = ["Bush","Sprout2","Sprout2"]
            for neighbour in neighbours:
                architect.doFillWith(neighbour[0],neighbour[1],fillMaterial)
                currentTerrain.minimapOverride[neighbour] = (src.interaction.urwid.AttrSpec("#474", "black"), "**")
            room.bio = True
        
        hivePositions = [(3,3,0),(11,11,0),(3,11,0),(11,3,0)]
        for hivePos in hivePositions:
            addHive(hivePos)

        tmpList = farmPlots[:]
        while tmpList:
            farmPlot = tmpList.pop()
            if not farmPlot in tmpList:
                continue
            fillMaterial = ["Bush","Bush","EncrustedBush"]
            if difficulty == "easy":
                fillMaterial = ["Bush","Bush","Sprout2"]
            architect.doSpawnItems(farmPlot[0],farmPlot[1],fillMaterial,20,repeat=10)

        for farmPlot in farmPlots:
            architect.doFillWith(farmPlot[0],farmPlot[1],["Mold","Mold","Sprout","Mold","Sprout2"])

        for farmPlot in farmPlots:
            if farmPlot in hivePositions:
                continue

            for i in range(1,4):
                enemy = src.characters.Monster(4,4)
                enemy.godMode = True
                enemy.health = baseHealth*4
                enemy.baseDamage = 7
                enemy.faction = "invader"
                enemy.tag = "hiveGuard"
                enemy.specialDisplay = "O-"
                currentTerrain.addCharacter(enemy,farmPlot[0]*15+random.randint(2,11),farmPlot[1]*15+random.randint(2,11))

                quest = src.quests.SecureTile(toSecure=farmPlot)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

        blockerRingPositions = [(7,4,0),(6,5,0)]
        for pos in blockerRingPositions:
            for i in range(0,2):
                enemy = src.characters.Monster(4,4)
                enemy.godMode = True
                enemy.health = 100
                enemy.baseDamage = 5
                currentTerrain.addCharacter(enemy, 15*pos[0]+random.randint(2,11), 15*pos[1]+random.randint(2,11))
                enemy.specialDisplay = "{-"
                enemy.faction = "invader"
                enemy.tag = "blocker"

                quest = src.quests.SecureTile(toSecure=pos)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

        print("generate stuff")
        for x in range(1,14):
            for y in range(1,14):
                print((x,y))
                if (x,y) == (8,5):
                    continue

                if (x,y) in farmPlots:
                    continue

                if currentTerrain.getRoomByPosition((x,y)):
                    continue

                for i in range(1,2):
                    mold = src.items.itemMap["Mold"]()
                    mold.dead = True
                    currentTerrain.addItem(mold,(15*x+random.randint(1,13),15*y+random.randint(1,13),0))

                placedMines = False

                if random.random() > 0.5 or (x,y) in blockerRingPositions:
                    placedMines = True
                    for i in range(1,2+random.randint(1,5)):
                        offsetX = random.randint(1,13)
                        offsetY = random.randint(1,13)
                        
                        xPos = 15*x+offsetX
                        yPos = 15*y+offsetY

                        if currentTerrain.getItemByPosition((xPos,yPos,0)):
                            continue

                        landmine = src.items.itemMap["LandMine"]()
                        currentTerrain.addItem(landmine,(xPos,yPos,0))

                for i in range(1,5+random.randint(1,20)):
                    offsetX = random.randint(1,13)
                    offsetY = random.randint(1,13)

                    xPos = 15*x+offsetX
                    yPos = 15*y+offsetY

                    if currentTerrain.getItemByPosition((xPos,yPos,0)):
                        continue

                    if not difficulty == "easy":
                        if placedMines:
                            landmine = src.items.itemMap["LandMine"]()
                            currentTerrain.addItem(landmine,(xPos,yPos,0))

                    scrap = src.items.itemMap["Scrap"](amount=random.randint(1,13))
                    currentTerrain.addItem(scrap,(xPos,yPos,0))

                spawnChance = 0.2
                maxNumSpawns = 3
                if difficulty == "easy":
                    spawnChance = 0.05
                    maxNumSpawns = 2
                if difficulty == "difficult":
                    spawnChance = 0.5
                    maxNumSpawns = 5

                if random.random() < spawnChance and not (x,y) in blockerRingPositions and not (x,y) in farmPlots:
                    if (x <= 5 and (y <= 5 or y >= 9)) or (x >= 9 and (y <= 5 or y >= 9)):
                        continue
                    for j in range(0,random.randint(1,maxNumSpawns)):
                        enemy = src.characters.Monster(4,4)
                        enemy.godMode = True
                        enemy.health = 15
                        enemy.baseDamage = 12
                        enemy.movementSpeed = self.baseMovementSpeed
                        pos = (15*x+random.randint(2,11), 15*y+random.randint(2,11))
                        currentTerrain.addCharacter(enemy, pos[0],pos[1])
                        enemy.specialDisplay = "ss"
                        enemy.faction = "invader"
                        enemy.tag = "lurker"

                        quest = src.quests.SecureTile(toSecure=(x,y,0))
                        quest.autoSolve = True
                        quest.assignToCharacter(enemy)
                        quest.activate()
                        enemy.quests.append(quest)

        numChasers = 12
        if difficulty == "easy":
            numChasers = 5
        if difficulty == "difficult":
            numChasers = 20

        for i in range(1,numChasers):
            enemy = src.characters.Monster(4,4)
            enemy.godMode = True
            enemy.health = baseHealth//10*i
            enemy.baseDamage = 10*10
            currentTerrain.addCharacter(enemy, 15*8+random.randint(2,11), 15*11+random.randint(2,11))
            enemy.specialDisplay = "[-"
            enemy.faction = "invader"

            quest = src.quests.SecureTile(toSecure=spawnRoom.getPosition(),endWhenCleared=True)
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

            quest = src.quests.Huntdown(target=mainChar)
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

        if difficulty == "easy":
            toClear = [(7,1),(7,13),(1,7),(13,7)]
            for bigX in range(0,14):
                for bigY in range(0,14):
                    for (x,y) in toClear:
                        currentTerrain.removeItems(currentTerrain.getItemByPosition((bigX*15+x,bigY*15+y,0)))

        waypoints = [(5,10),(9,10),(9,4),(5,4)]
        if not difficulty == "easy":
            for i in range(1,10):
                waypoints = waypoints[1:]+[waypoints[0]]

                enemy = src.characters.Monster(4,4)
                enemy.godMode = True
                enemy.health = baseHealth
                enemy.baseDamage = 7
                enemy.movementSpeed = self.baseMovementSpeed
                currentTerrain.addCharacter(enemy, 15*waypoints[0][0]+random.randint(2,11), 15*waypoints[0][1]+random.randint(2,11))
                enemy.specialDisplay = "X-"
                enemy.faction = "invader"
                enemy.tag = "patrol"

                quest = src.quests.PatrolQuest(waypoints=waypoints)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

        waypoints = [(5,4),(9,4),(9,10),(5,10)]
        for i in range(1,10):
            waypoints = waypoints[1:]+[waypoints[0]]

            enemy = src.characters.Monster(4,4)
            enemy.godMode = True
            enemy.health = baseHealth
            enemy.baseDamage = 7
            currentTerrain.addCharacter(enemy, 15*waypoints[0][0]+random.randint(2,11), 15*waypoints[0][1]+random.randint(2,11))
            enemy.movementSpeed = self.baseMovementSpeed
            enemy.specialDisplay = "X-"
            enemy.faction = "invader"
            enemy.tag = "patrol"

            quest = src.quests.PatrolQuest(waypoints=waypoints)
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

        self.wavecounterUI = {"type":"text","offset":(72,5), "text":"wavecounter"}

        self.numRounds = 1
        self.startRound()

        self.checkDead()

        src.gamestate.gamestate.uiElements.append(self.wavecounterUI)

        mainChar.messages = []
        mainChar.addMessage("press z for help")
        mainChar.addMessage("Try to reach the safety of the base in the north.")
        mainChar.addMessage("You are ambushed and you need to flee.")
        mainChar.addMessage("----------------")

    def showSecondText(self):
        text = """
Follow the instructions on the left side of the screen.

On the right side of the screen is a message log.

Close this window and press z to see the movement keys.

On the left top is a mini map.
"""

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

        src.gamestate.gamestate.mainChar.addMessage("On the left top is a mini map.")
        src.gamestate.gamestate.mainChar.addMessage("Close this window and press z to see the movement keys.")
        src.gamestate.gamestate.mainChar.addMessage("On the right side of the screen is a message log.")
        src.gamestate.gamestate.mainChar.addMessage("Follow the instructions on the left side of the screen.")
        src.gamestate.gamestate.mainChar.addMessage("----------------")

    def reachedBase(self):
        text = """
You arrived at the base. You are safe for now.
The base is under siege, so that safety is temporary.
Go to the command centre and get further instrucions.

----

Continue following the instructions the quests give you.
They will lead you to the epoch artwork.
Activate it.

"""
        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.addMessage("------------------"+text+"--------------------")

        containerQuest = src.quests.ActivateEpochArtwork(epochArtwork=self.epochArtwork)
        src.gamestate.gamestate.mainChar.quests.append(containerQuest)
        containerQuest.assignToCharacter(src.gamestate.gamestate.mainChar)
        containerQuest.activate()

    def checkDead(self):

        text = "epoch: %s tick: %s"%(src.gamestate.gamestate.tick//self.epochLength+1,src.gamestate.gamestate.tick%self.epochLength)
        self.wavecounterUI["text"] = "epoch: %s tick: %s"%(src.gamestate.gamestate.tick//self.epochLength+1,src.gamestate.gamestate.tick%self.epochLength)
        self.wavecounterUI["offset"] = (82-len(text)//2,5)

        if src.gamestate.gamestate.mainChar.dead:
            print("dead")
            print(src.gamestate.gamestate.tick)
            src.gamestate.gamestate.uiElements = [
                    {"type":"text","offset":(15,10), "text":"you were killed while holding against the siege"},
                    {"type":"text","offset":(15,12), "text":"you suvived %s ticks. That means wave no %s got you"%(src.gamestate.gamestate.tick,src.gamestate.gamestate.tick//1000+1,)},
                    ]
        else:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "checkDead"})
            currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
            currentTerrain.addEvent(event)

    def startRound(self):
        print("start round")
        terrain = src.gamestate.gamestate.terrainMap[7][7]

        remainingEnemyCounter = 0
        for character in terrain.characters:
            if not character.tag == "wave":
                continue
            remainingEnemyCounter += 1

        for room in terrain.rooms:
            for character in room.characters:
                if not character.tag == "wave":
                    continue
                remainingEnemyCounter += 1

        """
        counter = 0
        while counter < remainingEnemyCounter:
            if terrain.rooms:
                room = random.choice(terrain.rooms)
                print("damage room")
                room.damage()
            counter += 1
        """

        counter = 0

        spawnerRooms = []
        for room in terrain.rooms:
            for item in room.getItemByPosition((6,6,0)):
                if item.type == "MonsterSpawner":
                    spawnerRooms.append(room)
        
        if self.numRounds == 15 or not spawnerRooms:
            src.gamestate.gamestate.uiElements = [
                    {"type":"text","offset":(15,10), "text":"You won the game"},
                    ]
            return


        if not spawnerRooms:
            print("ending siege")
            return

        monsterStartRoom = random.choice(spawnerRooms)
        while counter < remainingEnemyCounter:
            enemy = src.characters.Monster(6,6)
            enemy.faction = "invader"
            enemy.tag = "wave"
            enemy.specialDisplay = "<c"
            monsterStartRoom.addCharacter(enemy, 6, 6)

            quest = src.quests.DestroyRooms()
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

            counter += 1

        #numMonsters = 1
        #if self.numRounds > 8:
        #    numMonsters = self.numRounds-8
        numMonsters = 10+self.numRounds+remainingEnemyCounter

        if self.difficulty == "easy":
            if self.numRounds < 3:
                numMonsters = 0
        if self.difficulty == "medium":
            if self.numRounds == 1:
                numMonsters = 0
                print("skipped wave")

        for i in range(0,numMonsters):
            enemy = src.characters.Monster(6,6)
            enemy.health = 10*i
            enemy.baseDamage = i
            enemy.faction = "invader"
            enemy.tag = "wave"
            monsterStartRoom.addCharacter(enemy, 6, 6)
            enemy.movementSpeed = 0.8

            quest = src.quests.ClearTerrain()
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

        numLurkers = 10
        if not self.difficulty == "easy":
            numLurkers = 5
        if not self.difficulty == "difficult":
            numLurkers = 20

        numLurkers = int(numLurkers*random.random()*2)
        for i in range(0,numLurkers):
            x = random.randint(1,13)
            y = random.randint(1,13)

            if self.numRounds == 1:
                continue

            if (x <= 5 and (y <= 5 or y >= 9)) or (x >= 9 and (y <= 5 or y >= 9)):
                continue

            enemy = src.characters.Monster(4,4)
            enemy.godMode = True
            enemy.health = 15
            enemy.baseDamage = 12
            enemy.movementSpeed = self.baseMovementSpeed
            monsterStartRoom.addCharacter(enemy, 6, 6)
            enemy.specialDisplay = "ss"
            enemy.faction = "invader"
            enemy.tag = "lurker"

            quest = src.quests.SecureTile(toSecure=(x,y,0))
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

        self.numRounds += 1
        
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + self.epochLength)
        event.setCallback({"container": self, "method": "startRound"})
        terrain.addEvent(event)

class Siege(BasicPhase):
    """
    the phase is intended to give the player access to the true gameworld without manipulations

    this phase should be left as blank as possible
    """

    def __init__(self, seed=0):
        """
        set up super class

        Parameters:
            seed: rng seed
        """

        super().__init__("Siege", seed=seed)

    def start(self, seed=0, difficulty=None):
        """
        set up terrain and spawn main character

        Parameters:
            seed: rng seed
        """

        showText("build a base.\n\npress space to continue")
        showText(
            "\n\n * press ? for help\n\n * press a to move left/west\n * press w to move up/north\n * press s to move down/south\n * press d to move right/east\n\npress space to continue\n\n"
        )

        src.gamestate.gamestate.setTerrain(src.terrains.GameplayTest(),(7,7))
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addCharacter(
            src.gamestate.gamestate.mainChar, 124, 109
        )

        self.miniBase = currentTerrain.rooms[0]

        """
        import json
        if seed%2==0:
            with open("states/theftBase1.json","r") as stateFile:
                room = json.loads(stateFile.read())
            src.gamestate.gamestate.terrain.addRoom(src.rooms.getRoomFromState(room,src.gamestate.gamestate.terrain))
        if seed%3==1:
            with open("states/theftBase2.json","r") as stateFile:
                room = json.loads(stateFile.read())
            src.gamestate.gamestate.terrain.addRoom(src.rooms.getRoomFromState(room,src.gamestate.gamestate.terrain))
        if seed%2==1:
            with open("states/caseStorage.json","r") as stateFile:
                room = json.loads(stateFile.read())
            src.gamestate.gamestate.terrain.addRoom(src.rooms.getRoomFromState(room,src.gamestate.gamestate.terrain))
        else:
            with open("states/emptyRoom1.json","r") as stateFile:
                room = json.loads(stateFile.read())
            src.gamestate.gamestate.terrain.addRoom(src.rooms.getRoomFromState(room,src.gamestate.gamestate.terrain))
        if seed%4:
            with open("states/emptyRoom2.json","r") as stateFile:
                room = json.loads(stateFile.read())
        else:
            wallRooms = ["states/wallRoom_1.json"]
            wallRoom = wallRooms[seed%5%len(wallRooms)]
            with open(wallRoom,"r") as stateFile:
                room = json.loads(stateFile.read())
        src.gamestate.gamestate.terrain.addRoom(src.rooms.getRoomFromState(room,src.gamestate.gamestate.terrain))
        with open("states/miniMech.json","r") as stateFile:
            room = json.loads(stateFile.read())
        src.gamestate.gamestate.terrain.addRoom(src.rooms.getRoomFromState(room,src.gamestate.gamestate.terrain))
        #room = src.rooms.EmptyRoom(1,1,2,2,creator=self)
        #room.reconfigure(sizeX=seed%12+3,sizeY=(seed+seed%236)%12+3,doorPos=(0,1))
        #src.gamestate.gamestate.terrain.addRoom(room)
        #room = src.rooms.EmptyRoom(4,9,-1,0,creator=self)
        #room.reconfigure(sizeX=14,sizeY=14,doorPos=(13,6))
        #src.gamestate.gamestate.terrain.addRoom(room)
        with open("states/globalMacroStorage.json","r") as stateFile:
            room = json.loads(stateFile.read())
        src.gamestate.gamestate.terrain.addRoom(src.rooms.getRoomFromState(room,src.gamestate.gamestate.terrain))
        """

        molds = []
        for bigX in range(1, 14):
            for bigY in range(1, 14):
                import random

                if 3 < bigX < 11 and 3 < bigY < 11:
                    continue
                if bigX > 7 and bigY == 7:
                    continue
                if random.randint(1, 1) == 1:
                    amount = max(30-(bigX+bigY)*2,0)
                    for i in range(0, amount):
                        pos = (bigX * 15 + random.randint(1, 13),bigY * 15 + random.randint(1, 13),0)
                        if currentTerrain.getItemByPosition(pos):
                            continue
                        molds.append(
                            (
                                src.items.itemMap["Mold"](),
                                pos,
                            )
                        )
        molds.append((src.items.itemMap["Mold"](),(155, 108, 0)))
        molds.append((src.items.itemMap["Mold"](),(159, 116, 0)))
        molds.append((src.items.itemMap["Mold"](),(138, 108, 0)))
        molds.append((src.items.itemMap["Mold"](),(145, 115, 0)))

        positions = [
            (187, 37, 0),
            (37, 37, 0),
            (37, 187, 0),
            (187, 187, 0),
            (202, 112, 0),
            (187, 112, 0),
            (172, 112, 0),
        ]
        positions = [
            (37, 37, 0),
            (37, 187, 0),
        ]
        counter = 0
        """
        for x in range(1, 14):
            for y in (1, 2, 12, 13):
                counter += 1
                if not counter % 3 == 0:
                    continue
                pos = (x * 15 + 7, y * 15 + 7, 0)
                if pos not in positions:
                    positions.append(pos)

        for y in range(1, 14):
            for x in (1, 2, 12, 13):
                counter += 1
                if not counter % 3 == 0:
                    continue
                pos = (x * 15 + 7, y * 15 + 7, 0)
                if pos not in positions:
                    positions.append(pos)
        """

        for pos in positions:
            commandBloom = src.items.itemMap["CommandBloom"]()
            currentTerrain.addItem(commandBloom,pos)
            if pos in ((187, 112, 0), (172, 112, 0), (157, 112, 0), (142, 112, 0)):
                commandBloom.masterCommand = "13a9kj"
            molds.append(
                (
                    src.items.itemMap["Mold"](),
                    (pos[0] + 4, pos[1] + 4, pos[2]),
                )
            )
            molds.append(
                (
                    src.items.itemMap["Mold"](),
                    (pos[0] - 4, pos[1] + 4, pos[2]),
                )
            )
            molds.append(
                (
                    src.items.itemMap["Mold"](),
                    (pos[0] + 4, pos[1] - 4, pos[2]),
                )
            )
            molds.append(
                (
                    src.items.itemMap["Mold"](),
                    (pos[0] - 4, pos[1] - 4, pos[2]),
                )
            )
            molds.append(
                (
                    src.items.itemMap["Bloom"](),
                    (pos[0] + 2, pos[1] + 2, pos[2]),
                )
            )
            molds.append(
                (
                    src.items.itemMap["Bloom"](),
                    (pos[0] - 2, pos[1] + 2, pos[2]),
                )
            )
            molds.append(
                (
                    src.items.itemMap["Bloom"](),
                    (pos[0] + 2, pos[1] - 2, pos[2]),
                )
            )
            molds.append(
                (
                    src.items.itemMap["Bloom"](),
                    (pos[0] - 2, pos[1] - 2, pos[2]),
                )
            )
            currentTerrain.addItem(
                src.items.itemMap["CommandBloom"](),(pos[0] - 6, pos[1], pos[2])
            )
            currentTerrain.addItem(
                src.items.itemMap["CommandBloom"](),(pos[0] - 6, pos[1], pos[2])
            )
            currentTerrain.addItem(
                src.items.itemMap["CommandBloom"](),(pos[0] + 6, pos[1], pos[2])
            )
            currentTerrain.addItem(
                src.items.itemMap["CommandBloom"](),(pos[0], pos[1] - 6, pos[2])
            )
            currentTerrain.addItem(
                src.items.itemMap["CommandBloom"](),(pos[0], pos[1] + 6, pos[2])
            )
            molds.append(
                (
                    src.items.itemMap["Mold"](),
                    (pos[0] + 6, pos[1] + 6, pos[2]),
                )
            )
            molds.append(
                (
                    src.items.itemMap["Mold"](),
                    (pos[0] - 6, pos[1] - 6, pos[2]),
                )
            )
            molds.append(
                (
                    src.items.itemMap["Mold"](),
                    (pos[0] + 6, pos[1] - 6, pos[2]),
                )
            )
            molds.append(
                (
                    src.items.itemMap["Mold"](),
                    (pos[0] - 6, pos[1] + 6, pos[2]),
                )
            )

        currentTerrain.addItems(molds)
        for mold in molds:
            mold[0].startSpawn()

        for pos in positions:
            crawler = src.characters.Monster(xPosition=pos[0], yPosition=pos[1])

            crawler.solvers = [
                "SurviveQuest",
                "Serve",
                "NaiveMoveQuest",
                "NaiveMurderQuest",
                "MoveQuestMeta",
                "NaiveActivateQuest",
                "ActivateQuestMeta",
                "NaivePickupQuest",
                "PickupQuestMeta",
                "DrinkQuest",
                "ExamineQuest",
                "FireFurnaceMeta",
                "CollectQuestMeta",
                "WaitQuest",
            ]
            crawler.runCommandString("jj",clear=True)
            currentTerrain.addCharacter(crawler, pos[0], pos[1])

        src.gamestate.gamestate.mainChar.addListener(self.checkRoomEnteredMain)
        src.gamestate.gamestate.mainChar.macroState["macros"]["j"] = ["J", "f"]

        # add basic set of abilities in openworld phase
        src.gamestate.gamestate.mainChar.questsDone = [
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "CollectQuestMeta",
            "FireFurnaceMeta",
            "ExamineQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
            "LeaveRoomQuest",
            "NaiveMurderQuest",
        ]

        src.gamestate.gamestate.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "NaiveMurderQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

        self.mainChar = src.gamestate.gamestate.mainChar
        self.mainChar.personality["autoFlee"] = False
        self.mainChar.personality["abortMacrosOnAttack"] = False
        self.mainChar.personality["autoCounterAttack"] = False

    def checkRoomEnteredMain(self):
        """
        handle the main character entering rooms
        by showing a message when the player enters the base the first time
        """

        if self.mainChar.room and self.mainChar.room == self.miniBase:
            showText(
                "\n\nUse the auto tutor for more information. The autotutor is represented by iD\n\n * press j to activate \n * press k to pick up\n * press l to drop\n * press i to view inventory\n * press @ to view your stats\n * press e to examine\n * press ? for help\n\nMove onto an item and press the key to interact with it. Move against big items and press the key to interact with them\n\npress space to continue\n\n"
            )
            src.gamestate.gamestate.mainChar.delListener(self.checkRoomEnteredMain)

class DesertSurvival(BasicPhase):
    """
    game mode offering a harsh survival experience
    """

    def __init__(self, seed=0):
        """
        set up the super class
        """
        super().__init__("DesertSurvival", seed=seed)

    # bad code: superclass call should not be prevented
    def start(self, seed=0, difficulty=None):
        """
        set up terrain and place char

        Parameters:
            seed: rng seed
        """

        import random

        src.cinematics.showCinematic("staring desert survival Scenario.")

        src.gamestate.gamestate.setTerrain(src.terrains.Desert(),(7,7))
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.heatmap[3][7] = 1
        currentTerrain.heatmap[4][7] = 1
        currentTerrain.heatmap[5][7] = 1
        currentTerrain.heatmap[6][7] = 1

        # place character on terrain
        src.gamestate.gamestate.mainChar.xPosition = 65
        src.gamestate.gamestate.mainChar.yPosition = 111
        src.gamestate.gamestate.mainChar.reputation = 100
        currentTerrain.addCharacter(
            src.gamestate.gamestate.mainChar, 65, 111
        )

        # add basic set of abilities in openworld phase
        src.gamestate.gamestate.mainChar.questsDone = [
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "CollectQuestMeta",
            "FireFurnaceMeta",
            "ExamineQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
            "LeaveRoomQuest",
        ]

        src.gamestate.gamestate.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

        reservedTiles = [
            (2, 6),
            (3, 6),
            (4, 6),
            (5, 6),
            (6, 6),
            (7, 6),
            (2, 7),
            (3, 7),
            (4, 7),
            (5, 7),
            (6, 7),
            (7, 7),
            (2, 8),
            (3, 8),
            (4, 8),
            (5, 8),
            (6, 8),
            (7, 8),
        ]

        while 1:
            x = random.randint(1, 14)
            y = random.randint(1, 14)
            if (x, y) in reservedTiles:
                continue

            reservedTiles.append((x, y))

            self.workshop = src.rooms.EmptyRoom(x, y, 2, 3)
            self.workshop.reconfigure(11, 8)
            break

        scrap = src.items.itemMap["Scrap"](2, 5, amount=10)
        self.workshop.addItems([scrap])
        sunscreen = src.items.itemMap["SunScreen"](9, 4, creator=self)
        self.workshop.addItems([sunscreen])
        scrapCompactor = src.items.itemMap["ScrapCompactor"](3, 5, creator=self)
        self.workshop.addItems([scrapCompactor])
        rodMachine = src.items.itemMap["Machine"](5, 5, creator=self)
        rodMachine.setToProduce("Rod")
        self.workshop.addItems([rodMachine])
        waterCondenserMachine = src.items.itemMap["Machine"](7, 2, creator=self)
        waterCondenserMachine.setToProduce("WaterCondenser")
        self.workshop.addItems([waterCondenserMachine])
        scrapper = src.items.itemMap["Scraper"](7, 5, creator=self)
        self.workshop.addItems([scrapper])
        case = src.items.itemMap["Case"](1, 1, creator=self)
        case.bolted = False
        self.workshop.addItems([case])
        case = src.items.itemMap["Case"](2, 1, creator=self)
        case.bolted = False
        self.workshop.addItems([case])
        case = src.items.itemMap["Case"](3, 1, creator=self)
        case.bolted = False
        self.workshop.addItems([case])
        case = src.items.itemMap["Case"](4, 1, creator=self)
        case.bolted = False
        self.workshop.addItems([case])
        sheet = src.items.itemMap["Sheet"](7, 1, creator=self)
        sheet.bolted = False
        self.workshop.addItems([sheet])
        currentTerrain.addRooms([self.workshop])

        while 1:
            x = random.randint(1, 14)
            y = random.randint(1, 14)
            if (x, y) in reservedTiles:
                continue

            reservedTiles.append((x, y))

            self.workshop = src.rooms.EmptyRoom(x, y, 2, 4, creator=self)
            self.workshop.reconfigure(8, 8)
            break

        currentTerrain.doSandStorm()

# NIY: not done and not integrated
# obsolete: maybe just delete and rebuild
class FactoryDream(BasicPhase):
    """
    game mode basically 
    """

    def __init__(self, seed=0):
        """
        initialise the super class

        Parameters:
            seed: rng seed
        """
        super().__init__("FactoryDream", seed=seed)

    def start(self, seed=0, difficulty=None):
        """
        set up terrain and place main char

        Parameters:
            seed: rng seed
        """
        
        import random

        src.cinematics.showCinematic("just look at my pretty factory")

        src.gamestate.gamestate.mainChar.terrain = src.gamestate.gamestate.terrain
        src.gamestate.gamestate.terrain.addCharacter(
            src.gamestate.gamestate.mainChar, 7 * 15 + 7, 7 * 15 + 7
        )

        # add basic set of abilities in openworld phase
        src.gamestate.gamestate.mainChar.questsDone = [
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "CollectQuestMeta",
            "FireFurnaceMeta",
            "ExamineQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
            "LeaveRoomQuest",
        ]

        src.gamestate.gamestate.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

        # fill one cargo pod with scrap
        cargoPod = src.rooms.EmptyRoom(5, 6, 2, 3, creator=self)
        cargoPod.reconfigure(11, 8)
        items = []
        for x in range(1, 9):
            for y in range(1, 6):
                scrap = src.items.itemMap["Scrap"](x, y, amount=10, creator=self)
                items.append(scrap)
        cargoPod.addItems(items)
        src.gamestate.gamestate.terrain.addRooms([cargoPod])

        cargoPod = src.rooms.ScrapStorage(6, 6, 1, 1, creator=self)
        src.gamestate.gamestate.terrain.addRooms([cargoPod])

        # fill other cargo pod with flasks
        cargoPod = src.rooms.EmptyRoom(6, 5, 2, 3, creator=self)
        cargoPod.reconfigure(11, 8)
        items = []
        for x in range(1, 9):
            for y in range(1, 6):
                flask = src.items.itemMap["GooFlask"](x, y)
                flask.uses = 100
                items.append(flask)
        cargoPod.addItems(items)
        src.gamestate.gamestate.terrain.addRooms([cargoPod])

        # place processing scrap into metal bars
        workshopMetal = src.rooms.EmptyRoom(6, 7, 1, 1, creator=self)
        items = []
        scrapCompactor = src.items.itemMap["ScrapCompactor"](4, 8)
        items.append(scrapCompactor)
        scrapCompactor = src.items.itemMap["ScrapCompactor"](8, 8)
        items.append(scrapCompactor)
        scrapCompactor = src.items.itemMap["ScrapCompactor"](7, 10)
        items.append(scrapCompactor)
        machine = src.items.itemMap["Machine"](3, 4)
        machine.setToProduce("Rod")
        items.append(machine)
        machine = src.items.itemMap["Machine"](5, 4)
        machine.setToProduce("Frame")
        items.append(machine)
        machine = src.items.itemMap["Machine"](7, 4)
        machine.setToProduce("Case")
        items.append(machine)
        machine = src.items.itemMap["Machine"](9, 4)
        machine.setToProduce("Wall")
        items.append(machine)
        machine = src.items.itemMap["Machine"](10, 8)
        machine.setToProduce("Sheet")
        items.append(machine)
        machine = src.items.itemMap["Machine"](9, 10)
        machine.setToProduce("FloorPlate")
        items.append(machine)
        stasisTank = src.items.itemMap["StasisTank"](
            9, 1
        )  # lets add the stasis tank to hold the local npc
        items.append(stasisTank)
        command = src.items.itemMap["Command"](
            6, 6
        )  # add a command for producing walls
        command.setPayload(
            list(
                "13dwwasjsjsjsjdss13aaaasslwdsjdddslwdsjdskwaaaakskwwwaaawlwdddddddlaaaaaaassdwjddwjddwjddwjdwksddddddddsjj12a"
            )
        )
        items.append(command)
        command = src.items.itemMap["Command"](
            5, 10
        )  # add a command for producing floors
        command.setPayload(list(""))
        items.append(command)
        command = src.items.itemMap["Command"](5, 10)  # add roombuilder
        command.setPayload(list(""))
        items.append(command)
        workshopMetal.reconfigure(13, 13)
        workshopMetal.addItems(items)
        src.gamestate.gamestate.terrain.addRooms([workshopMetal])

        items = []
        stockPile = src.items.itemMap["UniformStockpileManager"](15 * 7 + 7, 15 * 6 + 7)
        items.append(stockPile)
        stockPile = src.items.itemMap["UniformStockpileManager"](15 * 8 + 7, 15 * 6 + 7)
        items.append(stockPile)
        stockPile = src.items.itemMap["UniformStockpileManager"](15 * 9 + 7, 15 * 6 + 7)
        items.append(stockPile)
        stockPile = src.items.itemMap["UniformStockpileManager"](
            15 * 10 + 7, 15 * 6 + 7
        )
        items.append(stockPile)
        src.gamestate.gamestate.terrain.addItems(items)

class Tour(BasicPhase):
    """
    """

    def __init__(self, seed=0):
        super().__init__("Tour", seed=seed)

    def start(self, seed=0, difficulty=None):

        src.gamestate.gamestate.mainChar.terrain = src.gamestate.gamestate.terrain
        src.gamestate.gamestate.mainChar.godMode = True
        src.gamestate.gamestate.mainChar.satiation = 1000000000
        src.gamestate.gamestate.terrain.addCharacter(
            src.gamestate.gamestate.mainChar, 1 * 15 + 5, 1 * 15 + 5
        )

        # add basic set of abilities in openworld phase
        src.gamestate.gamestate.mainChar.questsDone = [
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "CollectQuestMeta",
            "FireFurnaceMeta",
            "ExamineQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
            "LeaveRoomQuest",
        ]

        src.gamestate.gamestate.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest",
            "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

        showText("""
Hello i'm MarxMustermann and the creator and current maintainer of this game.

This game not remotely finished, but is playable and is kind of complicated. So i build this mode to explain the game a bit.

This project heavyly inspired by cataclysm:dda and DF Fortress mode and Factorio, but wants to add story.

For now that means for me:
* top down roguelike on a large world with building and crafting (cataclysm)
* imperative programming for example for overcomplicated factories (factorio)
* functional programming for example for autoresoving build tasks (DF Fortress mode)
* prebuilds and lore

While each of these is a 10 year project easily and the idea might it might be an impossible goal, i did make some progress.

So let's give you a Tour!

The following scenarios represent the roguelike aspect: roguelikeStart, survival, dungeon
The following scenarios represent the imperative programming part of the game: siege, creative mode
The following scenarios represent the functional programming part of the game: 

-- press space to continue --
(loads of spoilers ahead)
""")
        sideNotes = """
some sidenotes:

    * Commands are ment to be recorded by standing on a sheet and activating it
    * Commands are ment to be be placed on the floor and activated while standing on them
    * You can activate commands while recording a command
    * The result of a recorded action may change  
    * Your commands can include moving commands
    * You cannot record two commands at once
    * Commands alone are not enough for full automation
"""

        showText("""
The first thing i want to show/explain is the imperative automation component.

The easyiest and most convienient way for automating things is to create commands.

Commands are ingame items that can be used to run the command stored in that item.
These commands can be recorded by activating a sheet, dooing something and activating the sheet again.
The keys pressed by the player inbetween the activations are recorded and stored as command in the item.

This means you can record actions and redo them later. In other words simple imperative automation.

-- press space to continue --
""")
        showText("""
So let's give it a go. I'll go and spawn you a world with some sheets and some examples for you.

Read the notes on the floor for more information.
""")

        terrain = src.gamestate.gamestate.mainChar.terrain

        
        # room 1
        roomPos = (1,1)
        item = src.items.itemMap["Note"]()
        item.text = "use the command in the center of the room"
        terrain.addItem(item,(15*roomPos[0]+8,15*roomPos[1]+9,0))

        item = src.items.itemMap["Command"]()
        item.command = "d"*13
        terrain.addItem(item,(15*roomPos[0]+7,15*roomPos[1]+7,0))
        item.bolted = True

        # room 2
        roomPos = (2,1)
        for x in range(2,5):
            for y in range(2,5):
                for i in range(1,4):
                    item = src.items.itemMap["Sheet"]()
                    terrain.addItem(item,(15*roomPos[0]+x,15*roomPos[1]+y,0))

        item = src.items.itemMap["Note"]()
        item.text = """
This room contains sheets so you can practice recording commands.

You can record a command by:
    * placing a sheet on the ground
    * activating it
    * selecting "create a written commmand"
    * selecting "start recording"
    * dooing some action
    * activating the sheet again

Continue to the east afterwards
"""
        terrain.addItem(item,(15*roomPos[0]+8,15*roomPos[1]+9,0))

        # room 3
        roomPos = (3,1)
        item = src.items.itemMap["Note"]()
        item.text = """
The intended usage for commands is for automation of simple processes.
A small machine setup for producing sheets is demonstrated in this room.

Continue to the east afterwards
"""
        terrain.addItem(item,(15*roomPos[0]+8,15*roomPos[1]+9,0))

        item = src.items.itemMap["Command"]()
        item.command = "a"*4+"w"*3+"Jw"+"dd"+"Jw"+"dd"+"sss"
        terrain.addItem(item,(15*roomPos[0]+7,15*roomPos[1]+7,0))

        item = src.items.itemMap["Scrap"]()
        item.amount = 15
        terrain.addItem(item,(15*roomPos[0]+2,15*roomPos[1]+3,0))
        item = src.items.itemMap["ScrapCompactor"]()
        item.charges = 100
        terrain.addItem(item,(15*roomPos[0]+3,15*roomPos[1]+3,0))
        item = src.items.itemMap["Machine"]()
        item.setToProduce("Sheet")
        item.charges = 100
        terrain.addItem(item,(15*roomPos[0]+5,15*roomPos[1]+3,0))

        # room 4
        roomPos = (4,1)
        item = src.items.itemMap["Note"]()
        item.text = """
I did cheat a bit in the last example to make things easier.
The production chains in this game are overcomplicated to offer some challenge to the player.
For example machines have a cooldown when used the cooldown.

This example is the same example as the last one, but has the cooldown for the machines activated.
That means the command will only work when the machines have no cooldown active

If the cooldown is active the environment changed and the command stops working.
Other examples for complications are input ressources running out or output fields filling up.

Try activating the command several times in a row and continue east afterwards.
"""

        terrain.addItem(item,(15*roomPos[0]+8,15*roomPos[1]+9,0))

        item = src.items.itemMap["Command"]()
        item.command = "a"*4+"w"*3+"Jw"+"dd"+"Jw"+"dd"+"sss"
        terrain.addItem(item,(15*roomPos[0]+7,15*roomPos[1]+7,0))

        item = src.items.itemMap["Scrap"]()
        item.amount = 15
        terrain.addItem(item,(15*roomPos[0]+2,15*roomPos[1]+3,0))
        item = src.items.itemMap["ScrapCompactor"]()
        item.charges = 0
        terrain.addItem(item,(15*roomPos[0]+3,15*roomPos[1]+3,0))
        item = src.items.itemMap["Machine"]()
        item.setToProduce("Sheet")
        item.charges = 0
        terrain.addItem(item,(15*roomPos[0]+5,15*roomPos[1]+3,0))

        # room 5
        roomPos = (5,1)
        item = src.items.itemMap["Note"]()
        item.text = """
The cooldown issue can be worked around by simply waiting for the cooldown to pass.

This can be automated in a crude way by recording a new command that waits a 100 ticks and then runs the other command.

I extended the last example with such a command. The new command is to the west of the tile center.

So commands can be chained to each other. Since there is no limit on how many commands run how many commands complex processes can be build.
The overcomplex production chains incurage this.

continue east to see an example for this.

"""

        terrain.addItem(item,(15*roomPos[0]+8,15*roomPos[1]+9,0))

        item = src.items.itemMap["Command"]()
        item.command = "a"*4+"w"*3+"Jw"+"dd"+"Jw"+"dd"+"sss"
        terrain.addItem(item,(15*roomPos[0]+7,15*roomPos[1]+7,0))

        item = src.items.itemMap["Command"]()
        item.command = "d100.ja"
        terrain.addItem(item,(15*roomPos[0]+6,15*roomPos[1]+7,0))

        item = src.items.itemMap["Scrap"]()
        item.amount = 15
        terrain.addItem(item,(15*roomPos[0]+2,15*roomPos[1]+3,0))
        item = src.items.itemMap["ScrapCompactor"]()
        item.charges = 0
        terrain.addItem(item,(15*roomPos[0]+3,15*roomPos[1]+3,0))
        item = src.items.itemMap["Machine"]()
        item.setToProduce("Sheet")
        item.charges = 0
        terrain.addItem(item,(15*roomPos[0]+5,15*roomPos[1]+3,0))

        # room 6
        roomPos = (6,1)
        item = src.items.itemMap["Note"]()
        item.text = """
This command in the tile center will take about 17000 ticks to complete.
This is a simplfied food production setup, it works like this (west to east):

The character uses the tree to drop 1 maggot 
The character picks it up and carries it into the room and drops it
The character does that 10 times to get 10 maggots
The character uses the maggot fermenter to produce 1 biomass from 10 maggots
The character does this 10 times
The character uses the bio press to produce 1 press cake from 10 biomass
The character does this 10 times
The character uses the goo producer to produce goo from 10 press cakes

This works by having the command to produce press cakes activate the command for producing biomass 10 times and so on.
There are 5 commands chained and each command is very short, but runtime and complexity can grow fast when chaining commands.

Feel free to run the command yourself. The game will start to run very fast and try to burn your CPU, but running the command should not take more than a few minutes.

Continue east to have somebody else do it.

"""
        terrain.addItem(item,(15*roomPos[0]+8,15*roomPos[1]+9,0))

        item = src.items.itemMap["Tree"]()
        item.numMaggots = 1000000000
        item.maxMaggot = 1000000000
        terrain.addItem(item,(15*roomPos[0]+2,15*roomPos[1]+4,0))

        room = src.rooms.roomMap["EmptyRoom"](roomPos[0],roomPos[1],5,2)
        room.reconfigure(9, 5, doorPos=[(0,2)])
        terrain.addRooms([room])

        item = src.items.itemMap["Command"]()
        item.command = "aasaaJwdKwdwddLw"
        room.addItem(item,(1,2,0))

        item = src.items.itemMap["MaggotFermenter"]()
        room.addItem(item,(2,1,0))

        item = src.items.itemMap["Command"]()
        item.command = "a10jdJw"
        room.addItem(item,(2,2,0))

        item = src.items.itemMap["BioPress"]()
        room.addItem(item,(4,1,0))

        item = src.items.itemMap["Command"]()
        item.command = "aa10jddJw"
        room.addItem(item,(4,2,0))

        item = src.items.itemMap["GooProducer"]()
        room.addItem(item,(6,1,0))

        item = src.items.itemMap["Command"]()
        item.command = "aa10jddJw"
        room.addItem(item,(6,2,0))

        item = src.items.itemMap["GooDispenser"]()
        room.addItem(item,(7,1,0))

        item = src.items.itemMap["Command"]()
        item.command = "3a3w7dj7a3s3d"
        terrain.addItem(item,(roomPos[0]*15+7,roomPos[1]*15+7,0))

        # room 7
        roomPos = (7,1)
        item = src.items.itemMap["Note"]()
        item.text = """
Obviously you are not supposed to play the game by running these long commands yourself.
After having completely automated a task you can have npcs running these commands for you.

The command in the middle of the room uses a growth tank to spawn a npc.
The npc will activate the command next to the growth tank and will start to run the long command from the previous example.

The idea is to have hook npc in a similar way into your base automation and have many of these npcs and run background tasks in your base.

If you are interested in further detail about how you can use commands continue south.
For more information on how handle changing conditions continue east

"""
        terrain.addItem(item,(15*roomPos[0]+8,15*roomPos[1]+9,0))

        room = src.rooms.roomMap["EmptyRoom"](roomPos[0],roomPos[1],5,2)
        room.reconfigure(8, 5, doorPos=[(0,2)])
        terrain.addRooms([room])

        item = src.items.itemMap["GooDispenser"]()
        item.charges = 100
        room.addItem(item,(1,1,0))
        item = src.items.itemMap["GrowthTank"]()
        item.commands["born"] = [("j")]
        room.addItem(item,(2,1,0))
        item = src.items.itemMap["GooFlask"]()
        room.addItem(item,(1,3,0))
        item = src.items.itemMap["Command"]()
        item.command = "s4a3s10aj"
        room.addItem(item,(3,1,0))

        item = src.items.itemMap["Command"]()
        item.command = "3a3w2dKsJwdJwJwaLsaa3s3d"
        terrain.addItem(item,(roomPos[0]*15+7,roomPos[1]*15+7,0))

        # room 7.2
        roomPos = (7,2)
        item = src.items.itemMap["Note"]()
        item.text = """
There are some tricks that can be used with commands that you can do.
But be aware of the fact that dooing complex automation only using commands is very hard to impossible.

By activating a command from your inventory you can build commands that doesn't stop where it started.
This is useful to to build endless loops to have npc do a job forever or for building fast travel system.

Moving, storing, stacking and copying commands works. 

So you could have a todo-stack of commands that get a npc takes in an endless loop and distributes those to a pool of workers.
You could have npcs that spawn more npcs. You could have self replicating strutures.

Go Nutz, but keep in mind working with commands only is very difficult.

"""
        terrain.addItem(item,(15*roomPos[0]+8,15*roomPos[1]+9,0))

        # room 8
        roomPos = (8,1)
        item = src.items.itemMap["Note"]()
        item.text = """
I tried building complex automation (small cities with 20 npcs), but i gave up on that because it just was to complicated.

For example:
When a machine producing sheet gets too little input material it stops producing and all machines dependend on the machine will stop producing.
When a machine producing sheet gets too much input material it will collect up and clutter up the room or kill npcs.

It was possible to balance this, but very error prone.

The solution for this issue is the ability to configure items to run commands on NPC on specific conditions.
The item check what conditions are true and run commands depending on it.
You cannot truely change the conditions, but you can set the commands to be run. (see the note to the right for how to do this)

For example:
run command (to fetch ressources) if ressources are missing
run command (to drink) if character is hungry

The machines in this room for example are set to produce missing ressources. Use them from the north or the command in the center of the room to try it.
Setups like these are player buildable and programmable.

continue east to get information about further helper items.
"""
        terrain.addItem(item,(15*roomPos[0]+8,15*roomPos[1]+9,0))

        item = src.items.itemMap["Command"]()
        item.command = "5w2aJsdKs7dls7awa2d5s"
        terrain.addItem(item,(roomPos[0]*15+7,roomPos[1]*15+7,0))

        item = src.items.itemMap["Machine"]()
        item.setToProduce("Case")
        item.commands["material Frame"] = "2a8sJsdKsa8wdLsdJs"
        item.charges = 1000
        terrain.addItem(item,(15*roomPos[0]+5,15*roomPos[1]+3,0))

        item = src.items.itemMap["Machine"]()
        item.setToProduce("Frame")
        item.commands["material Rod"] = "3dJsdKsa3aaLsdJs"
        item.charges = 1000
        terrain.addItem(item,(15*roomPos[0]+3,15*roomPos[1]+11,0))

        item = src.items.itemMap["Machine"]()
        item.setToProduce("Rod")
        item.commands["material MetalBars"] = "5w5dJwdKwa5a5saLsdJs"
        item.charges = 1000
        terrain.addItem(item,(15*roomPos[0]+6,15*roomPos[1]+11,0))

        item = src.items.itemMap["ScrapCompactor"]()
        item.charges = 1000
        terrain.addItem(item,(15*roomPos[0]+11,15*roomPos[1]+4,0))
        item = src.items.itemMap["Scrap"]()
        item.amount = 1000
        terrain.addItem(item,(15*roomPos[0]+10,15*roomPos[1]+4,0))

        # room 9
        roomPos = (9,1)
        item = src.items.itemMap["Note"]()
        item.text = """
I you try running the last example more than 7 times you will notice that the production output starts to clutter the room.
The character starts to bump into items and the recorded command will fail.
Storing item is a common issue that is hard to solve using commands.

So there are helper items that do to complex things like managing a stockpile for you.
They do this by calculating a command to do the task and run that command on a npc.

This example is the last example but with 2 smart items build in:
* a storage manager is used to store the produced case properly. 
* an item collector to gather scrap easily

"""
        terrain.addItem(item,(15*roomPos[0]+7,15*roomPos[1]+8,0))

        item = src.items.itemMap["UniformStockpileManager"]()
        terrain.addItem(item,(15*roomPos[0]+8,15*roomPos[1]+8,0))
        
        for i in range(0,10):
            item = src.items.itemMap["Sheet"]()
            terrain.addItem(item,(15*roomPos[0]+5,15*roomPos[1]+9,0))

        item = src.items.itemMap["Command"]()
        item.command = "5w2aJs2d5s"
        terrain.addItem(item,(roomPos[0]*15+7,roomPos[1]*15+7,0))

        item = src.items.itemMap["Machine"]()
        item.setToProduce("Case")
        item.commands["material Frame"] = "2a8sJsdKsa8wdLsdJs"
        item.commands["success"] = "dKsd5sdJs.ja5w2a"
        item.charges = 1000
        terrain.addItem(item,(15*roomPos[0]+5,15*roomPos[1]+3,0))

        item = src.items.itemMap["Machine"]()
        item.setToProduce("Frame")
        item.commands["material Rod"] = "3dJsdKsa3aaLsdJs"
        item.charges = 1000
        terrain.addItem(item,(15*roomPos[0]+3,15*roomPos[1]+11,0))

        item = src.items.itemMap["Machine"]()
        item.setToProduce("Rod")
        item.commands["material MetalBars"] = "5w5dJwdKwa5a5saLsdJs"
        item.charges = 1000
        terrain.addItem(item,(15*roomPos[0]+6,15*roomPos[1]+11,0))

        item = src.items.itemMap["ScrapCompactor"]()
        item.commands["material Scrap"] = "4a15sj15w3dLwd"
        item.charges = 1000
        terrain.addItem(item,(15*roomPos[0]+11,15*roomPos[1]+4,0))

        # room 9
        roomPos = (9,2)

        item = src.items.itemMap["ItemCollector"]()
        terrain.addItem(item,(roomPos[0]*15+7,roomPos[1]*15+7,0))

        item = src.items.itemMap["Scrap"]()
        item.amount = 1000
        terrain.addItem(item,(15*roomPos[0]+10,15*roomPos[1]+4,0))

        item = src.items.itemMap["Scrap"]()
        item.amount = 1
        terrain.addItem(item,(15*roomPos[0]+6,15*roomPos[1]+6,0))

        item = src.items.itemMap["Scrap"]()
        item.amount = 2
        terrain.addItem(item,(15*roomPos[0]+8,15*roomPos[1]+7,0))

        item = src.items.itemMap["Scrap"]()
        item.amount = 10
        terrain.addItem(item,(15*roomPos[0]+10,15*roomPos[1]+8,0))

    def showMainSelection(self):
        options = [
            ("story", "The story aspect of the game"),
            ("imperative", "The imperative programming aspect of the game"),
            ("functional", "The "),
            ("roguelike", "The roguelike aspect of the game"),
            ]
        cinematic = src.cinematics.SelectionCinematic("So... what do you want to know more about?\n\nThe order is historical btw", options, default="ok")
        cinematic.followUps = {
                    "story": {"container": self, "method": "niy"},
                    "imperative": {"container": self, "method": "niy"},
                    "functional": {"container": self, "method": "niy"},
                    "roguelike": {"container": self, "method": "niy"},
                }
        self.cinematic = cinematic
        src.cinematics.cinematicQueue.append(cinematic)

    def explainStoryAndLore(self):
        pass

    def niy():
        showText("""well.... that is not implemented yet. Sorry""")

class CreativeMode(BasicPhase):
    """
    mode to build stuff with disabled environmental danger
    """

    def __init__(self, seed=0):
        """
        initialise super class

        Parameters:
            seed: rng seed
        """

        super().__init__("CreativeMode", seed=seed)

    def start(self, seed=0, difficulty=None):
        """
        place main char and add godmode items
        """

        import random

        src.gamestate.gamestate.mainChar.terrain = src.gamestate.gamestate.terrain
        src.gamestate.gamestate.mainChar.godMode = True
        src.gamestate.gamestate.terrain.addCharacter(
            src.gamestate.gamestate.mainChar, 7 * 15 + 7, 7 * 15 + 7
        )

        # add basic set of abilities in openworld phase
        src.gamestate.gamestate.mainChar.questsDone = [
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "CollectQuestMeta",
            "FireFurnaceMeta",
            "ExamineQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
            "LeaveRoomQuest",
        ]

        src.gamestate.gamestate.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

        items = []
        item = src.items.itemMap["ArchitectArtwork"]()
        item.bolted = False
        item.godMode = True
        items.append((item, (15 * 7 + 8, 15 * 7 + 7, 0)))
        item = src.items.itemMap["ProductionArtwork"]()
        item.bolted = False
        item.godMode = True
        items.append((item, (15 * 7 + 8, 15 * 7 + 8, 0)))
        src.gamestate.gamestate.terrain.addItems(items)

class Tutorial(BasicPhase):
    def __init__(self, seed=0):
        super().__init__("Tutorial", seed=seed)

    """
    place main char
    bad code: superclass call should not be prevented
    """

    def start(self, seed=0, difficulty=None):
        showText(
            "Your current sitiuation is:\n\n\nYour memory has been resetted and you have been dumped here for manual work.\n\nIf you keep getting caught violating order XXI you will be killed.\nIf it were not for your heritage you would be dead a long time ago.\n\nAs your Implant i can only strictly advise against getting caught again."
        )
        say("now move to your assigned workplace.")
        showText(
            "Since you lost your memory again i will feed you the most important data.\n\nYou are represented by the @ character and you are in the wastelands.\n\nTo the east there is a scrap field. You may ignore it for now.\n\nTo your south is a minibase. You are assigned to work there\n\nYou can move by using the w a s d keys or the arrow keys.\n\nnow move to your assigned workplace."
        )

        self.mainChar = src.gamestate.gamestate.mainChar
        self.mainChar.xPosition = 70
        self.mainChar.yPosition = 74
        self.mainChar.terrain = src.gamestate.gamestate.terrain
        src.gamestate.gamestate.terrain.addCharacter(
            self.mainChar, self.mainChar.xPosition, self.mainChar.yPosition
        )

        self.seed = seed

        self.mainChar.addListener(self.checkNearTarget)

        # add basic set of abilities in openworld phase
        self.mainChar.questsDone = []

        self.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

        self.miniBase = src.gamestate.gamestate.terrain.miniBase

        self.reportQuest = None

        desiredProducts = [
            src.items.itemMap["GrowthTank"],
            src.items.itemMap["Hutch"],
            src.items.itemMap["Furnace"],
        ]

        numProducts = 0
        while (
            len(self.helper_getFilteredProducables()) not in (1,)
            or not numProducts == 3
        ):
            seed += seed % 42
            src.gamestate.gamestate.terrain.removeRoom(self.miniBase)

            self.miniBase = src.rooms.TutorialMiniBase(4, 8, 0, 0, seed=seed)
            src.gamestate.gamestate.terrain.addRoom(self.miniBase)

            itemsFound = []
            for item in self.miniBase.itemsOnFloor:
                if isinstance(item, src.items.itemMap["GameTestingProducer"]):
                    if (
                        item.product in desiredProducts
                        and item.product not in itemsFound
                    ):
                        itemsFound.append(item.product)

            numProducts = len(itemsFound)

        quest = src.quests.EnterRoomQuestMeta(self.miniBase, 3, 3)
        quest.endTrigger = {"container": self, "method": "reportForDuty"}
        # quest.endTrigger = {"container":self,"method":"scrapTest1"}
        self.mainChar.assignQuest(quest, active=True)

        queueOk = False
        while not queueOk:
            productionQueue = [self.helper_getFilteredProducables()[0]]

            counter = 0
            while counter < 3:
                productionQueue.append(desiredProducts[seed % len(desiredProducts)])
                seed += seed % 12 + counter
                counter += 1

            for item in desiredProducts:
                if item not in self.helper_getFilteredProducables():
                    productionQueue.append(item)
                    break

            seed += seed % 37

            queueOk = True
            for item in desiredProducts:
                if item not in productionQueue:
                    queueOk = False

        self.productionQueue = productionQueue

        self.miniBase.firstOfficer.silent = True

        self.dupPrevention = False

    def scrapTest1(self):
        if self.dupPrevention:
            return
        self.dupPrevention = True

        toRemove = []
        for item in mainChar.inventory:
            if isinstance(item, src.items.itemMap["Scrap"]):
                toRemove.append(item)
        for item in toRemove:
            mainChar.inventory.remove(item)

        itemCount = 0
        for item in src.gamestate.gamestate.terrain.itemsOnFloor:
            if isinstance(item, src.items.itemMap["Scrap"]):
                if (
                    (item.xPosition - 1, item.yPosition)
                    in src.gamestate.gamestate.terrain.watershedCoordinates
                    or (item.xPosition + 1, item.yPosition)
                    in src.gamestate.gamestate.terrain.watershedCoordinates
                    or (item.xPosition, item.yPosition - 1)
                    in src.gamestate.gamestate.terrain.watershedCoordinates
                    or (item.xPosition, item.yPosition + 1)
                    in src.gamestate.gamestate.terrain.watershedCoordinates
                ):
                    quest = src.quests.PickupQuestMeta(toPickup=item)
                    if len(mainChar.inventory) < 9:
                        method = "scrapTest1"
                    else:
                        method = "scrapTest2"
                    quest.endTrigger = {"container": self, "method": method}
                    self.mainChar.assignQuest(quest, active=True)
                    break

        self.dupPrevention = False

    def scrapTest2(self):
        quest = src.quests.EnterRoomQuestMeta(self.miniBase, 3, 3)
        quest.endTrigger = {"container": self, "method": "scrapTest1"}
        self.mainChar.assignQuest(quest, active=True)

    def checkNearTarget(self):
        if self.mainChar.xPosition // 15 in (
            4,
            5,
        ) and self.mainChar.yPosition // 15 in (
            8,
            9,
        ):
            self.mainChar.delListener(self.checkNearTarget)
            showText(
                "the minibase you are assigned to work in is to the west.\nenter the room through its door. The door is shown as [].\nopen the door and enter the room. Activate the door to open it.\n\nYou activate items by walking into them and pressing j afterwards"
            )
            say("walk into items and press j to activate them")

    def reportForDuty(self):
        showText(
            "I did not expect that you will start following orders after your memory wipe.\nYou might make it, if you continue to do so.\n\nNow report for duty and work your way out of here.\n\nyou can talk to people by pressing the h key.\nNavigate the chat options by using the w s keys or the arrow keys.\nUse the j or enter key to select dialog options"
        )
        self.reportQuest = src.quests.DummyQuest(
            description="report for duty", creator=self
        )
        self.mainChar.assignQuest(self.reportQuest, active=True)

        self.miniBase.firstOfficer.basicChatOptions.append(
            {
                "dialogName": "I hereby report for duty.",
                "chat": src.chats.ConfigurableChat,
                "params": {
                    "text": "You may serve.\n\nThey did not send someone for some time after my latest subordinate died. I question how they did expect any work getting done here.\n\nStart by gathering some scrap form the scrap field in the east.",
                    "info": [
                        {
                            "type": "text",
                            "text": "Return the scrap to me",
                            "name": "Starting now",
                            "delete": True,
                            "trigger": {"container": self, "method": "startDuty"},
                            "quitAfter": True,
                        }
                    ],
                    "allowExit": False,
                },
            }
        )

    def startDuty(self):
        self.miniBase.firstOfficer.basicChatOptions.pop()
        self.reportQuest.postHandler()
        self.scrapQuest = src.quests.DummyQuest(
            description="gather scrap", creator=self
        )
        self.mainChar.assignQuest(self.scrapQuest, active=True)
        self.mainChar.addListener(self.checkOutside)

    def checkOutside(self):
        if self.mainChar.room is None:
            self.mainChar.delListener(self.checkOutside)
            showText(
                "well that is not the most of productive task, but scrap metal is needed to produce other things.\nGo and grab some scrap.\n\nscrap is shown as *, or .; or %# . Almost the whole area in the east is composed of scrap.\n\nTo pick up items walk onto them or into them and press k. This works like activating items."
            )
            self.mainChar.addListener(self.checkScrapCollected)

    def checkScrapCollected(self):
        numScrapCollected = 0
        for item in self.mainChar.inventory:
            if isinstance(item, src.items.itemMap["Scrap"]):
                numScrapCollected += 1

        if numScrapCollected >= 1:
            showText(
                "you collected some scrap. return to your superviser and you may see what to do now"
            )
            self.mainChar.delListener(self.checkScrapCollected)

            self.miniBase.firstOfficer.basicChatOptions.append(
                {
                    "dialogName": "I collected some scrap.",
                    "chat": src.chats.ConfigurableChat,
                    "params": {
                        "text": "now go and produce some metal bars",
                        "info": [
                            {
                                "type": "text",
                                "text": "Return the scrap to me",
                                "name": "Starting now",
                                "delete": True,
                                "trigger": {
                                    "container": self,
                                    "method": "startMetalBarChecking",
                                },
                                "quitAfter": True,
                            }
                        ],
                        "allowExit": False,
                    },
                }
            )

    def startMetalBarChecking(self):

        showText(
            "I seems like this is a simple resource gathering job. Metal bars are used to produce most of the materials needed in a mech.\n\nThe scrap is compacted to metal bars in a machine called scrap compactor\nThe machine is represented by the U\\ character. It processes scrap on the tile to its east and outputs the bars on the tile to its west.\n\nstart by dropping the scrap on the tile east of the machine.\nMove onto the tile and press l to drop items."
        )

        self.scrapQuest.postHandler()
        self.scrapQuest.completed = True

        self.mainChar.addListener(self.checkScrapDropped)

        self.mainChar.addListener(self.checkMetalBars)

        self.miniBase.firstOfficer.basicChatOptions.pop()

        self.barQuest = src.quests.DummyQuest(
            description="create metal bars", creator=self
        )
        self.mainChar.assignQuest(self.barQuest, active=True)

    def checkScrapDropped(self):
        coordinate = (11, 1)
        if coordinate in self.miniBase.itemByCoordinates:
            for item in self.miniBase.itemByCoordinates[coordinate]:
                if isinstance(item, src.items.itemMap["Scrap"]):
                    showText(
                        "That should work. Now activate the scrap compactor to produce a metal bar"
                    )
                    self.mainChar.delListener(self.checkScrapDropped)
                    self.mainChar.addListener(self.checkFirstMetalBar)
                    break

    def checkFirstMetalBar(self):
        coordinate = (9, 1)
        if coordinate in self.miniBase.itemByCoordinates:
            for item in self.miniBase.itemByCoordinates[coordinate]:
                if isinstance(item, src.items.itemMap["MetalBars"]):
                    showText("now go and grab the metal bar you produced")
                    self.mainChar.delListener(self.checkFirstMetalBar)
                    self.mainChar.addListener(self.checkFirstMetalBarFirstPickedUp)

    def checkFirstMetalBarFirstPickedUp(self):
        for item in self.mainChar.inventory:
            if isinstance(item, src.items.itemMap["MetalBars"]):
                showText(
                    "You got that figgured out. Now produce 4 more metal bars and pick them up"
                )
                self.mainChar.delListener(self.checkFirstMetalBarFirstPickedUp)
                break

    def checkMetalBars(self):
        numMetalBars = 0
        for item in self.mainChar.inventory:
            if isinstance(item, src.items.itemMap["MetalBars"]):
                numMetalBars += 1

        if numMetalBars >= 5:
            self.mainChar.delListener(self.checkMetalBars)
            self.barQuest.postHandler()
            self.producedCount = 0
            self.firstTimeImpossibleCraft = True
            self.firstRegularCraft = True
            self.firstProduced = True
            self.queueProduction = True
            self.producedFurnaces = 0
            self.producedGrowthTanks = 0
            self.producedHutches = 0
            self.batchProducing = False
            self.productionSection()
            self.batchFurnaceProducing = False
            self.batchHutchProducing = False
            self.batchGrowthTankProcing = False
            self.fastProduction = False

    def helper_getFilteredProducables(self):
        desiredProducts = [
            src.items.itemMap["GrowthTank"],
            src.items.itemMap["Hutch"],
            src.items.itemMap["Furnace"],
        ]
        filteredProducables = []
        for item in self.helper_getProducables():
            if item in desiredProducts:
                filteredProducables.append(item)
        return filteredProducables

    def helper_getProducables(self):
        producableStuff = [src.items.itemMap["MetalBars"]]
        lastLength = 0
        while lastLength < len(producableStuff):
            lastLength = len(producableStuff)
            for item in self.miniBase.itemsOnFloor:
                if isinstance(item, src.items.itemMap["GameTestingProducer"]):
                    if (
                        item.resource in producableStuff
                        and item.product not in producableStuff
                    ):
                        producableStuff.append(item.product)
        return producableStuff

    def productionSection(self):

        if not len(self.productionQueue) and self.queueProduction:
            showText(
                "that is enough to satisfy the minimal stock requirements. Exceding the minimal requirements will gain you a small reward.\n\nIn this case you will be rewarded with tokens. These tokens allow you to reconfigure the machines you use for production.\nThe production lines are hardly working at all and reconfiguring these machines should resolve that\n\nYour supervisor was not ambitious enough to do this, but i know you are. As you implant i will reward you, when you are done\n\nYou can reconfigure a machine by using it with a token in your inventory. It will reset to a new random state.\nReplace the useless machines until the machines are able to produce\nFurnaces, Growthtanks, Hutches\nstarting from metal bars."
            )
            self.mainChar.addListener(self.checkProductionLine)
            self.queueProduction = False

        if not len(self.productionQueue) and self.batchProducing:
            if (
                self.batchFurnaceProducing
                and not self.batchHutchProducing
                and not self.batchGrowthTankProcing
            ):
                showText(
                    "The first batch is ready. You can optimise your macros in many ways.\nYou can record your macros to buffers from a-z. This way you can store marcos for different actions.\n\nI recommend recording the macro for producing furnaces to f, the macro for producing hutches to h and the macro for producing the growthtanks to g\n\nproduce 10 hutches now."
                )
                for x in range(0, 10):
                    self.productionQueue.append(src.items.itemMap["Hutch"])
                self.batchFurnaceProducing = False
                self.batchHutchProducing = True

            elif (
                not self.batchFurnaceProducing
                and self.batchHutchProducing
                and not self.batchGrowthTankProcing
            ):
                showText(
                    "The second batch is ready. Another trick that may be useful for you is the multiplier. It allows to repeat commmands\n\nYou can use this for example to drop 7 items by pressing 7l . This will be translated to lllllll .\nYou can use this within macros and when calling macros. Press 5_f to run the macro f 5 times.\n\nUse this the produce 10 growth tanks with one macro."
                )
                for x in range(0, 10):
                    self.productionQueue.append(src.items.itemMap["GrowthTank"])
                self.batchHutchProducing = False
                self.batchGrowthTankProcing = True

            elif (
                not self.batchFurnaceProducing
                and not self.batchHutchProducing
                and self.batchGrowthTankProcing
            ):
                showText(
                    "The first order is completed and will be shipped out to the main base. Your supervisor did not get praised for this.\nYou did get a small supply drop. A goo dispenser is supplied for easier survival.\n\nIt seemes the delivery was overdue. There are only few resources spent on this outpost, but productivity is a must.\nRegular deliveries will ensure this output will stay supplied, but nothing more.\n\nSince your supervisor has no ambition to overachieve, this will only ensure your survival.\nIgnore your supervisor and pace up production. As soon this outpost achives noticeable output, we will have more options.\n\nProduce 3 successive deliveries with a production time under 100 ticks each."
                )
                self.batchGrowthTankProcing = False
                self.fastProduction = True
                self.fastProductionStart = 0
            else:
                raise Exception("should not happen")
                return

        if not len(self.productionQueue) and self.fastProduction:
            """
            for x in range(0,10):
                self.productionQueue.append(src.items.itemMap["GrowthTank"])
            for x in range(0,10):
                self.productionQueue.append(src.items.itemMap["Furnace"])
            """
            if not self.fastProductionStart == 0:
                if src.gamestate.gamestate.tick - self.fastProductionStart > 100:
                    showText("it took you %s ticks to complete the order.")
                else:
                    src.gamestate.gamestate.gameWon = True
                    return

            self.fastProductionStart = src.gamestate.gamestate.tick
            for x in range(0, 10):
                self.productionQueue.append(src.items.itemMap["Hutch"])

        self.seed += self.seed % 43

        possibleProducts = [
            src.items.itemMap["GrowthTank"],
            src.items.itemMap["Hutch"],
            src.items.itemMap["Furnace"],
        ]
        if self.queueProduction or self.batchProducing or self.fastProduction:
            self.product = self.productionQueue[0]
            self.productionQueue.remove(self.product)
        else:
            filteredProducts = self.helper_getFilteredProducables()
            self.product = possibleProducts[self.seed % len(possibleProducts)]
            self.seed += self.seed % 37

            src.gamestate.gamestate.mainChar.inventory.append(
                src.items.itemMap["Token"](creator=self)
            )

        producableStuff = self.helper_getProducables()

        description = "produce a " + self.product.type
        if self.batchProducing:
            description += " (use macros)"
        self.produceQuest = src.quests.DummyQuest(
            description="produce a " + self.product.type, creator=self
        )
        self.mainChar.assignQuest(self.produceQuest, active=True)
        if self.product in producableStuff:
            if self.firstRegularCraft:
                showText(
                    "produce a "
                    + self.product.type
                    + ". use the machines below to produce it.\n\nexamine the machines by walking into it and pressing the e key.\nIt will show what the machine produces and what resource is needed to produce.\n\nstart from a metal bar and create interstage products until you produce a "
                    + self.product.type
                )
                self.firstRegularCraft = False
        elif self.firstTimeImpossibleCraft:
            showText(
                "you should produce a "
                + self.product.type
                + " now, but you can not do this directly.\n\nThe machines here are not actually able to produce a "
                + self.product.type
                + " from metal bars. You need to get creative here.\n\nUsually you tried to bend the rules a bit. Try searching the scrap field for a working "
                + self.product.type
            )
            self.firstTimeImpossibleCraft = False
        self.mainChar.addListener(self.checkProduction)

    def checkProductionLine(self):
        filteredProducts = self.helper_getFilteredProducables()
        if len(filteredProducts) == 3:
            showText(
                "The machines are reconfigured now. I promised you are reward. Here it is:\n\nI can help you with the repetive tasks. You need to do something and i make you repeat the movements.\n\nYou can use this to produce items on these machines without thinking about it.\nWe will use this to produce enough items to get noticed by somebody up the command chain.\n\nYour superior will gain the most from this at first, but you need to trust me and do not break any rules again.\n\nYou can start recording the movement by pressing the - key and pressing some other key afterwards. Your movements will be recorded to the second key.\nAn Example: If you press - f for example your movements will be recoded to the f buffer\nTo stop recording press - again.\nTo replay the movement press _ and the key for the buffer you want to replay. Press _ f to replay the movement from the last example.\n\nget familiar with recording macros and then record macros for producing each item. We will need at least 10 furnaces, 10 hutches and 10 growth tanks to fill the whole order.\n\nIt is important for you to use macros and not get bogged down in mundane tasks. We need your creativity for greater things."
            )

            self.batchProducing = True
            for x in range(0, 10):
                self.productionQueue.append(src.items.itemMap["Furnace"])
            self.batchFurnaceProducing = True
            self.mainChar.delListener(self.checkProductionLine)

    def checkProduction(self):

        toRemove = None
        for item in self.mainChar.inventory:
            if isinstance(item, self.product):
                self.producedCount += 1
                toRemove = item
                break
        if toRemove:
            if self.firstProduced:
                showText(
                    "you produced your first item. congratulations. Produce some more and you will have a chance of getting out of here.\n\nThe produced item is removed from your inventory directly. Do not think about this."
                )
                self.firstProduced = False
            self.mainChar.delListener(self.checkProduction)
            self.mainChar.inventory.remove(toRemove)
            self.produceQuest.postHandler()

            self.productionSection()


class RoguelikeStart(BasicPhase):
    def __init__(self, seed=0):
        super().__init__("RoguelikeStart", seed=seed)

    def start(self, seed=0, difficulty=None):
        showText(
            "you traveled to the city #1A23 destroyed by an artisan a century ago.\nAfter arriving at the cities core to inspect the citybuilder you find it destroyed.\n\nThis setback was expected and the contingency plan is to find and activate the citys reserve citybuilder"
        )

        self.mainChar = src.gamestate.gamestate.mainChar
        self.mainChar.xPosition = 15*7+6
        self.mainChar.yPosition = 15*7+7
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addCharacter(
            self.mainChar, self.mainChar.xPosition, self.mainChar.yPosition
        )

        self.seed = seed

        items = []
        architect = src.items.itemMap["ArchitectArtwork"]()
        architect.bolted = False
        architect.godMode = True
        items.append((architect, (15 * 7 + 8, 15 * 7 + 7, 0)))
        currentTerrain.addItems(items)
        architect.generateMaze()
        currentTerrain.removeItem(architect)

        self.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "NaiveMurderQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]
        self.mainChar.personality["autoFlee"] = False
        self.mainChar.personality["abortMacrosOnAttack"] = False
        self.mainChar.personality["autoCounterAttack"] = False


class Testing_1(BasicPhase):
    def __init__(self, seed=0):
        super().__init__("Testing_1", seed=seed)

    """
    place main char
    bad code: superclass call should not be prevented
    """

    def start(self, seed=0, difficulty=None):
        showText(
            "Your current sitiuation is:\n\n\nYour memory has been resetted and you have been dumped here for manual work.\n\nIf you keep getting caught violating order XXI you will be killed.\nIf it were not for your heritage you would be dead a long time ago.\n\nAs your Implant i can only strictly advise against getting caught again."
        )
        say("now move to your assigned workplace.")
        showText(
            "Since you lost your memory again i will feed you the most important data.\n\nYou are represented by the @ character and you are in the wastelands.\n\nTo the east there is a scrap field. You may ignore it for now.\n\nTo your south is a minibase. You are assigned to work there\n\nYou can move by using the w a s d keys or the arrow keys.\n\nnow move to your assigned workplace."
        )

        self.mainChar = src.gamestate.gamestate.mainChar
        self.mainChar.xPosition = 70
        self.mainChar.yPosition = 74
        self.mainChar.terrain = src.gamestate.gamestate.terrain
        src.gamestate.gamestate.terrain.addCharacter(
            self.mainChar, self.mainChar.xPosition, self.mainChar.yPosition
        )

        self.seed = seed

        self.mainChar.addListener(self.checkNearTarget)

        # add basic set of abilities in openworld phase
        self.mainChar.questsDone = []

        self.mainChar.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

        self.miniBase = src.gamestate.gamestate.terrain.miniBase

        self.reportQuest = None

        desiredProducts = [
            src.items.itemMap["GrowthTank"],
            src.items.itemMap["Hutch"],
            src.items.itemMap["Furnace"],
        ]

        numProducts = 0
        while (
            len(self.helper_getFilteredProducables()) not in (1,)
            or not numProducts == 3
        ):
            seed += seed % 42
            src.gamestate.gamestate.terrain.removeRoom(self.miniBase)

            self.miniBase = src.rooms.GameTestingRoom(4, 8, 0, 0, seed=seed)
            src.gamestate.gamestate.terrain.addRoom(self.miniBase)

            itemsFound = []
            for item in self.miniBase.itemsOnFloor:
                if isinstance(item, src.items.itemMap["GameTestingProducer"]):
                    if (
                        item.product in desiredProducts
                        and item.product not in itemsFound
                    ):
                        itemsFound.append(item.product)

            numProducts = len(itemsFound)

        quest = src.quests.EnterRoomQuestMeta(self.miniBase, 3, 3)
        quest.endTrigger = {"container": self, "method": "reportForDuty"}
        # quest.endTrigger = {"container":self,"method":"scrapTest1"}
        self.mainChar.assignQuest(quest, active=True)

        queueOk = False
        while not queueOk:
            productionQueue = [self.helper_getFilteredProducables()[0]]

            counter = 0
            while counter < 3:
                productionQueue.append(desiredProducts[seed % len(desiredProducts)])
                seed += seed % 12 + counter
                counter += 1

            for item in desiredProducts:
                if item not in self.helper_getFilteredProducables():
                    productionQueue.append(item)
                    break

            seed += seed % 37

            queueOk = True
            for item in desiredProducts:
                if item not in productionQueue:
                    queueOk = False

        self.productionQueue = productionQueue

        self.miniBase.firstOfficer.silent = True

        self.dupPrevention = False

    def scrapTest1(self):
        if self.dupPrevention:
            return
        self.dupPrevention = True

        toRemove = []
        for item in src.gamestate.gamestate.mainChar.inventory:
            if isinstance(item, src.items.itemMap["Scrap"]):
                toRemove.append(item)
        for item in toRemove:
            src.gamestate.gamestate.mainChar.inventory.remove(item)

        itemCount = 0
        for item in src.gamestate.gamestate.terrain.itemsOnFloor:
            if isinstance(item, src.items.itemMap["Scrap"]):
                if (
                    (item.xPosition - 1, item.yPosition)
                    in src.gamestate.gamestate.terrain.watershedCoordinates
                    or (item.xPosition + 1, item.yPosition)
                    in src.gamestate.gamestate.terrain.watershedCoordinates
                    or (item.xPosition, item.yPosition - 1)
                    in src.gamestate.gamestate.terrain.watershedCoordinates
                    or (item.xPosition, item.yPosition + 1)
                    in src.gamestate.gamestate.terrain.watershedCoordinates
                ):
                    quest = src.quests.PickupQuestMeta(toPickup=item)
                    if len(src.gamestate.gamestate.mainChar.inventory) < 9:
                        method = "scrapTest1"
                    else:
                        method = "scrapTest2"
                    quest.endTrigger = {"container": self, "method": method}
                    self.mainChar.assignQuest(quest, active=True)
                    break

        self.dupPrevention = False

    def scrapTest2(self):
        quest = src.quests.EnterRoomQuestMeta(self.miniBase, 3, 3)
        quest.endTrigger = {"container": self, "method": "scrapTest1"}
        self.mainChar.assignQuest(quest, active=True)

    def checkNearTarget(self):
        if self.mainChar.xPosition // 15 in (
            4,
            5,
        ) and self.mainChar.yPosition // 15 in (
            8,
            9,
        ):
            self.mainChar.delListener(self.checkNearTarget)
            showText(
                "the minibase you are assigned to work in is to the west.\nenter the room through its door. The door is shown as [].\nopen the door and enter the room. Activate the door to open it.\n\nYou activate items by walking into them and pressing j afterwards"
            )
            say("walk into items and press j to activate them")

    def reportForDuty(self):
        showText(
            "I did not expect that you will start following orders after your memory wipe.\nYou might make it, if you continue to do so.\n\nNow report for duty and work your way out of here.\n\nyou can talk to people by pressing the h key.\nNavigate the chat options by using the w s keys or the arrow keys.\nUse the j or enter key to select dialog options"
        )
        self.reportQuest = src.quests.DummyQuest(
            description="report for duty", creator=self
        )
        self.mainChar.assignQuest(self.reportQuest, active=True)

        self.miniBase.firstOfficer.basicChatOptions.append(
            {
                "dialogName": "I hereby report for duty.",
                "chat": src.chats.ConfigurableChat,
                "params": {
                    "text": "You may serve.\n\nThey did not send someone for some time after my latest subordinate died. I question how they did expect any work getting done here.\n\nStart by gathering some scrap form the scrap field in the east.",
                    "info": [
                        {
                            "type": "text",
                            "text": "Return the scrap to me",
                            "name": "Starting now",
                            "delete": True,
                            "trigger": {"container": self, "method": "startDuty"},
                            "quitAfter": True,
                        }
                    ],
                    "allowExit": False,
                },
            }
        )

    def startDuty(self):
        self.miniBase.firstOfficer.basicChatOptions.pop()
        self.reportQuest.postHandler()
        self.scrapQuest = src.quests.DummyQuest(
            description="gather scrap", creator=self
        )
        self.mainChar.assignQuest(self.scrapQuest, active=True)
        self.mainChar.addListener(self.checkOutside)

    def checkOutside(self):
        if self.mainChar.room is None:
            self.mainChar.delListener(self.checkOutside)
            showText(
                "well that is not the most of productive task, but scrap metal is needed to produce other things.\nGo and grab some scrap.\n\nscrap is shown as *, or .; or %# . Almost the whole area in the east is composed of scrap.\n\nTo pick up items walk onto them or into them and press k. This works like activating items."
            )
            self.mainChar.addListener(self.checkScrapCollected)

    def checkScrapCollected(self):
        numScrapCollected = 0
        for item in self.mainChar.inventory:
            if isinstance(item, src.items.itemMap["Scrap"]):
                numScrapCollected += 1

        if numScrapCollected >= 1:
            showText(
                "you collected some scrap. return to your superviser and you may see what to do now"
            )
            self.mainChar.delListener(self.checkScrapCollected)

            self.miniBase.firstOfficer.basicChatOptions.append(
                {
                    "dialogName": "I collected some scrap.",
                    "chat": src.chats.ConfigurableChat,
                    "params": {
                        "text": "now go and produce some metal bars",
                        "info": [
                            {
                                "type": "text",
                                "text": "Return the scrap to me",
                                "name": "Starting now",
                                "delete": True,
                                "trigger": {
                                    "container": self,
                                    "method": "startMetalBarChecking",
                                },
                                "quitAfter": True,
                            }
                        ],
                        "allowExit": False,
                    },
                }
            )

    def startMetalBarChecking(self):

        showText(
            "I seems like this is a simple resource gathering job. Metal bars are used to produce most of the materials needed in a mech.\n\nThe scrap is compacted to metal bars in a machine called scrap compactor\nThe machine is represented by the U\\ character. It processes scrap on the tile to its east and outputs the bars on the tile to its west.\n\nstart by dropping the scrap on the tile east of the machine.\nMove onto the tile and press l to drop items."
        )

        self.scrapQuest.postHandler()
        self.scrapQuest.completed = True

        self.mainChar.addListener(self.checkScrapDropped)

        self.mainChar.addListener(self.checkMetalBars)

        self.miniBase.firstOfficer.basicChatOptions.pop()

        self.barQuest = src.quests.DummyQuest(
            description="create metal bars", creator=self
        )
        self.mainChar.assignQuest(self.barQuest, active=True)

    def checkScrapDropped(self):
        coordinate = (11, 1)
        if coordinate in self.miniBase.itemByCoordinates:
            for item in self.miniBase.itemByCoordinates[coordinate]:
                if isinstance(item, src.items.itemMap["Scrap"]):
                    showText(
                        "That should work. Now activate the scrap compactor to produce a metal bar"
                    )
                    self.mainChar.delListener(self.checkScrapDropped)
                    self.mainChar.addListener(self.checkFirstMetalBar)
                    break

    def checkFirstMetalBar(self):
        coordinate = (9, 1)
        if coordinate in self.miniBase.itemByCoordinates:
            for item in self.miniBase.itemByCoordinates[coordinate]:
                if isinstance(item, src.items.itemMap["MetalBars"]):
                    showText("now go and grab the metal bar you produced")
                    self.mainChar.delListener(self.checkFirstMetalBar)
                    self.mainChar.addListener(self.checkFirstMetalBarFirstPickedUp)

    def checkFirstMetalBarFirstPickedUp(self):
        for item in self.mainChar.inventory:
            if isinstance(item, src.items.itemMap["MetalBars"]):
                showText(
                    "You got that figgured out. Now produce 4 more metal bars and pick them up"
                )
                self.mainChar.delListener(self.checkFirstMetalBarFirstPickedUp)
                break

    def checkMetalBars(self):
        numMetalBars = 0
        for item in self.mainChar.inventory:
            if isinstance(item, src.items.itemMap["MetalBars"]):
                numMetalBars += 1

        if numMetalBars >= 5:
            self.mainChar.delListener(self.checkMetalBars)
            self.barQuest.postHandler()
            self.producedCount = 0
            self.firstTimeImpossibleCraft = True
            self.firstRegularCraft = True
            self.firstProduced = True
            self.queueProduction = True
            self.producedFurnaces = 0
            self.producedGrowthTanks = 0
            self.producedHutches = 0
            self.batchProducing = False
            self.productionSection()
            self.batchFurnaceProducing = False
            self.batchHutchProducing = False
            self.batchGrowthTankProcing = False
            self.fastProduction = False

    def helper_getFilteredProducables(self):
        desiredProducts = [
            src.items.itemMap["GrowthTank"],
            src.items.itemMap["Hutch"],
            src.items.itemMap["Furnace"],
        ]
        filteredProducables = []
        for item in self.helper_getProducables():
            if item in desiredProducts:
                filteredProducables.append(item)
        return filteredProducables

    def helper_getProducables(self):
        producableStuff = [src.items.itemMap["MetalBars"]]
        lastLength = 0
        while lastLength < len(producableStuff):
            lastLength = len(producableStuff)
            for item in self.miniBase.itemsOnFloor:
                if isinstance(item, src.items.itemMap["GameTestingProducer"]):
                    if (
                        item.resource in producableStuff
                        and item.product not in producableStuff
                    ):
                        producableStuff.append(item.product)
        return producableStuff

    def productionSection(self):

        if not len(self.productionQueue) and self.queueProduction:
            showText(
                "that is enough to satisfy the minimal stock requirements. Exceding the minimal requirements will gain you a small reward.\n\nIn this case you will be rewarded with tokens. These tokens allow you to reconfigure the machines you use for production.\nThe production lines are hardly working at all and reconfiguring these machines should resolve that\n\nYour supervisor was not ambitious enough to do this, but i know you are. As you implant i will reward you, when you are done\n\nYou can reconfigure a machine by using it with a token in your inventory. It will reset to a new random state.\nReplace the useless machines until the machines are able to produce\nFurnaces, Growthtanks, Hutches\nstarting from metal bars."
            )
            self.mainChar.addListener(self.checkProductionLine)
            self.queueProduction = False

        if not len(self.productionQueue) and self.batchProducing:
            if (
                self.batchFurnaceProducing
                and not self.batchHutchProducing
                and not self.batchGrowthTankProcing
            ):
                showText(
                    "The first batch is ready. You can optimise your macros in many ways.\nYou can record your macros to buffers from a-z. This way you can store marcos for different actions.\n\nI recommend recording the macro for producing furnaces to f, the macro for producing hutches to h and the macro for producing the growthtanks to g\n\nproduce 10 hutches now."
                )
                for x in range(0, 10):
                    self.productionQueue.append(src.items.itemMap["Hutch"])
                self.batchFurnaceProducing = False
                self.batchHutchProducing = True

            elif (
                not self.batchFurnaceProducing
                and self.batchHutchProducing
                and not self.batchGrowthTankProcing
            ):
                showText(
                    "The second batch is ready. Another trick that may be useful for you is the multiplier. It allows to repeat commmands\n\nYou can use this for example to drop 7 items by pressing 7l . This will be translated to lllllll .\nYou can use this within macros and when calling macros. Press 5_f to run the macro f 5 times.\n\nUse this the produce 10 growth tanks with one macro."
                )
                for x in range(0, 10):
                    self.productionQueue.append(src.items.itemMap["GrowthTank"])
                self.batchHutchProducing = False
                self.batchGrowthTankProcing = True

            elif (
                not self.batchFurnaceProducing
                and not self.batchHutchProducing
                and self.batchGrowthTankProcing
            ):
                showText(
                    "The first order is completed and will be shipped out to the main base. Your supervisor did not get praised for this.\nYou did get a small supply drop. A goo dispenser is supplied for easier survival.\n\nIt seemes the delivery was overdue. There are only few resources spent on this outpost, but productivity is a must.\nRegular deliveries will ensure this output will stay supplied, but nothing more.\n\nSince your supervisor has no ambition to overachieve, this will only ensure your survival.\nIgnore your supervisor and pace up production. As soon this outpost achives noticeable output, we will have more options.\n\nProduce 3 successive deliveries with a production time under 100 ticks each."
                )
                self.batchGrowthTankProcing = False
                self.fastProduction = True
                self.fastProductionStart = 0
            else:
                raise Exception("should not happen")
                return

        if not len(self.productionQueue) and self.fastProduction:
            """
            for x in range(0,10):
                self.productionQueue.append(src.items.itemMap["GrowthTank"])
            for x in range(0,10):
                self.productionQueue.append(src.items.itemMap["Furnace"])
            """
            if not self.fastProductionStart == 0:
                if src.gamestate.gamestate.tick - self.fastProductionStart > 100:
                    showText("it took you %s ticks to complete the order.")
                else:
                    src.gamestate.gamestate.gameWon = True
                    return

            self.fastProductionStart = src.gamestate.gamestate.tick
            for x in range(0, 10):
                self.productionQueue.append(src.items.itemMap["Hutch"])

        self.seed += self.seed % 43

        possibleProducts = [
            src.items.itemMap["GrowthTank"],
            src.items.itemMap["Hutch"],
            src.items.itemMap["Furnace"],
        ]
        if self.queueProduction or self.batchProducing or self.fastProduction:
            self.product = self.productionQueue[0]
            self.productionQueue.remove(self.product)
        else:
            filteredProducts = self.helper_getFilteredProducables()
            self.product = possibleProducts[self.seed % len(possibleProducts)]
            self.seed += self.seed % 37

            src.gamestate.gamestate.mainChar.inventory.append(
                src.items.itemMap["Token"](creator=self)
            )

        producableStuff = self.helper_getProducables()

        description = "produce a " + self.product.type
        if self.batchProducing:
            description += " (use macros)"
        self.produceQuest = src.quests.DummyQuest(
            description="produce a " + self.product.type, creator=self
        )
        self.mainChar.assignQuest(self.produceQuest, active=True)
        if self.product in producableStuff:
            if self.firstRegularCraft:
                showText(
                    "produce a "
                    + self.product.type
                    + ". use the machines below to produce it.\n\nexamine the machines by walking into it and pressing the e key.\nIt will show what the machine produces and what resource is needed to produce.\n\nstart from a metal bar and create interstage products until you produce a "
                    + self.product.type
                )
                self.firstRegularCraft = False
        elif self.firstTimeImpossibleCraft:
            showText(
                "you should produce a "
                + self.product.type
                + " now, but you can not do this directly.\n\nThe machines here are not actually able to produce a "
                + self.product.type
                + " from metal bars. You need to get creative here.\n\nUsually you tried to bend the rules a bit. Try searching the scrap field for a working "
                + self.product.type
            )
            self.firstTimeImpossibleCraft = False
        self.mainChar.addListener(self.checkProduction)

    def checkProductionLine(self):
        filteredProducts = self.helper_getFilteredProducables()
        if len(filteredProducts) == 3:
            showText(
                "The machines are reconfigured now. I promised you are reward. Here it is:\n\nI can help you with the repetive tasks. You need to do something and i make you repeat the movements.\n\nYou can use this to produce items on these machines without thinking about it.\nWe will use this to produce enough items to get noticed by somebody up the command chain.\n\nYour superior will gain the most from this at first, but you need to trust me and do not break any rules again.\n\nYou can start recording the movement by pressing the - key and pressing some other key afterwards. Your movements will be recorded to the second key.\nAn Example: If you press - f for example your movements will be recoded to the f buffer\nTo stop recording press - again.\nTo replay the movement press _ and the key for the buffer you want to replay. Press _ f to replay the movement from the last example.\n\nget familiar with recording macros and then record macros for producing each item. We will need at least 10 furnaces, 10 hutches and 10 growth tanks to fill the whole order.\n\nIt is important for you to use macros and not get bogged down in mundane tasks. We need your creativity for greater things."
            )

            self.batchProducing = True
            for x in range(0, 10):
                self.productionQueue.append(src.items.itemMap["Furnace"])
            self.batchFurnaceProducing = True
            self.mainChar.delListener(self.checkProductionLine)

    def checkProduction(self):

        toRemove = None
        for item in self.mainChar.inventory:
            if isinstance(item, self.product):
                self.producedCount += 1
                toRemove = item
                break
        if toRemove:
            if self.firstProduced:
                showText(
                    "you produced your first item. congratulations. Produce some more and you will have a chance of getting out of here.\n\nThe produced item is removed from your inventory directly. Do not think about this."
                )
                self.firstProduced = False
            self.mainChar.delListener(self.checkProduction)
            self.mainChar.inventory.remove(toRemove)
            self.produceQuest.postHandler()

            self.productionSection()


###############################################################
#
#    the glue to be able to call the phases from configs etc
#
#    this should be automated some time
#
###############################################################

# bad code: registering here is easy to forget when adding a phase
def registerPhases():
    """
    reference the phases to be able to call them easier
    """

    import src.gamestate

    phasesByName = src.gamestate.phasesByName

    phasesByName["OpenWorld"] = OpenWorld

    phasesByName["Challenge"] = Challenge
    phasesByName["Test"] = Testing_1
    phasesByName["Testing_1"] = Testing_1
    phasesByName["Siege"] = Siege
    phasesByName["Siege2"] = Siege2
    phasesByName["Tutorial"] = Tutorial
    phasesByName["DesertSurvival"] = DesertSurvival
    phasesByName["FactoryDream"] = FactoryDream
    phasesByName["CreativeMode"] = CreativeMode
    phasesByName["Dungeon"] = Dungeon
    phasesByName["WorldBuildingPhase"] = WorldBuildingPhase
    phasesByName["RoguelikeStart"] = RoguelikeStart
    phasesByName["Tour"] = Tour
    phasesByName["BaseBuilding"] = BaseBuilding
    phasesByName["BackToTheRoots"] = BackToTheRoots
    phasesByName["BuildBase"] = BaseBuilding
    phasesByName["PrefabDesign"] = PrefabDesign
    phasesByName["Tutorials"] = Tutorials
    phasesByName["BasicUsageTutorial"] = BasicUsageTutorial
