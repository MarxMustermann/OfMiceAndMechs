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

    def start(self, seed=0):
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
        self.mainCharXPosition = None
        self.mainCharYPosition = None
        self.mainCharRoom = None
        self.requiresMainCharRoomFirstOfficer = True
        self.requiresMainCharRoomSecondOfficer = True
        self.mainCharQuestList = []
        # bad code: these positions were convenient but should be removed
        self.firstOfficerXPosition = 4
        self.firstOfficerYPosition = 3
        self.secondOfficerXPosition = 5
        self.secondOfficerYPosition = 3
        self.name = name
        self.seed = seed

        # register with dummy id
        self.id = name

        self.attributesToStore.append("name")

    def start(self, seed=0):
        """
        set up and start to run this game phase
        """

        # set state
        src.gamestate.gamestate.currentPhase = self
        self.tick = src.gamestate.gamestate.tick
        self.seed = seed

        # place main character
        if self.mainCharRoom:
            if not (
                src.gamestate.gamestate.mainChar.room
                or src.gamestate.gamestate.mainChar.terrain
            ):
                if self.mainCharXPosition and self.mainCharYPosition:
                    self.mainCharRoom.addCharacter(
                        src.gamestate.gamestate.mainChar,
                        self.mainCharXPosition,
                        self.mainCharYPosition,
                    )
                else:
                    if (
                        src.gamestate.gamestate.mainChar.xPosition is None
                        or src.gamestate.gamestate.mainChar.yPosition is None
                    ):
                        self.mainCharRoom.addCharacter(
                            src.gamestate.gamestate.mainChar, 3, 3
                        )

        # create first officer
        if self.requiresMainCharRoomFirstOfficer:
            if not self.mainCharRoom.firstOfficer:
                self.mainCharRoom.firstOfficer = characters.Character(
                    xPosition=4, yPosition=3, seed=src.gamestate.gamestate.tick + 2
                )
                self.mainCharRoom.addCharacter(
                    self.mainCharRoom.firstOfficer,
                    self.firstOfficerXPosition,
                    self.firstOfficerYPosition,
                )
            self.mainCharRoom.firstOfficer.reputation = 1000

        # create second officer
        if self.requiresMainCharRoomSecondOfficer:
            if not self.mainCharRoom.secondOfficer:
                self.mainCharRoom.secondOfficer = characters.Character(
                    xPosition=4, yPosition=3, seed=src.gamestate.gamestate.tick + 4
                )
                self.mainCharRoom.addCharacter(
                    self.mainCharRoom.secondOfficer,
                    self.secondOfficerXPosition,
                    self.secondOfficerYPosition,
                )
            self.mainCharRoom.secondOfficer.reputation = 100

    def assignPlayerQuests(self):
        """
        helper function to properly hook player quests
        """

        # do nothing without quests
        if not self.mainCharQuestList:
            return

        # chain quests
        lastQuest = self.mainCharQuestList[0]
        for item in self.mainCharQuestList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        self.mainCharQuestList[-1].followup = None

        # chain last quest to the phases teardown
        self.mainCharQuestList[-1].endTrigger = {"container": self, "method": "end"}

        # assign the first quest
        src.gamestate.gamestate.mainChar.assignQuest(self.mainCharQuestList[0])

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
    def start(self, seed=0):
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
        self.mainCharRoom = challengeRoom
        self.mainCharRoom.addCharacter(src.gamestate.gamestate.mainChar, 4, 4)

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
    def start(self, seed=0):
        """
        start phase by placing main char
        """

        src.cinematics.showCinematic("staring open world Scenario.")

        # place character in wakeup room
        if src.gamestate.gamestate.terrain.wakeUpRoom:
            self.mainCharRoom = src.gamestate.gamestate.terrain.wakeUpRoom
            self.mainCharRoom.addCharacter(src.gamestate.gamestate.mainChar, 2, 4)
        # place character on terrain
        else:
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

    def start(self, seed=0):
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

    def start(self,seed=None):
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
        firstName = random.choice([
                "Siegfried","Ernst","Alfred","Herrmann","Friedrich","Helmut","Karl","Gunnar","Berthold","Dietrich",
                "Friedhelm","Horst","Edmund","Wilhelm","Albert","Johann","Herbert","Bertram","Hans","Jochen","Ludwig",
                "Raimund","Thorsten","Ulrich","Veit","Lutz","Anton","Alwin","Sigmund","Kurt","Heidrun","Elfriede",
                "Gunhilde","Hildegard","Gudrun","Gertrude","Brunhilde","Adelheid","Sieglinde","Kunigunde","Herta",
                "Frieda","Ursula","Katharina","Johanna","Clara","Isolde","Hermine","Berta","Gisela","Lina","Irmgard",
                "Marlene","Mathilde","Monika","Frieda","Gerlinde","Rita","Clementine","Brigitte","Adalbert","Jörg",
                "Moritz","Maximillian","Gundula","Renate","Udo","Fritz","Susanne","Guido"])

        mainNameCore = random.choice([
                "Berg","Stahl","Hammer","Kraut","Barren","Eichen","Sieben","Eisen","Bären","Hunde","Ketten","Felsen",
                "Feuer","Glut",
                ])

        postfix = random.choice([
                "brecher","wurst","schmidt","maier","bach","burg","treu","kraft","schmied","hans","schimmel",
                "hauer","schläger","feind","kranz","fels",
                ])

        npc.name = firstName+" "+mainNameCore+postfix

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

    def start(self, seed=0):
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

            jobArtwork = src.items.itemMap["JobArtwork"]()

            mainRoom.addItem(architect,(3,1,0))
            mainRoom.addItem(jobArtwork,(4,1,0))

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

    def start(self, seed=0):
        """
            basic usage: movement + basic UI + item management
            fighting: some explanaition on fighting + arena?
            industry: how things are produced
            ghuls: how to use ghuls and commands
        """
        options = [("BasicUsageTutorial", "basic usage"), ("FightingTutorial", "fighting"),("BackToTheRoots","start main game")]
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

        if extraInfo["tutorialToStart"] == "BackToTheRoots":
            nextPhase = BackToTheRoots()
            nextPhase.start()
            return

        if extraInfo["tutorialToStart"] == "BasicUsageTutorial":
            nextPhase = BasicUsageTutorial()
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

class BasicUsageTutorial(BasicPhase):
    """
    """

    def __init__(self, seed=0):
        super().__init__("BasicUsageTutorial", seed=seed)

    def start(self, seed=0):
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

        submenu = src.interaction.TextMenu(text)
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
        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

        mainChar.addListener(self.checkTutorialHelpClosed, "closedHelp")

    def checkTutorialHelpClosed(self):
        self.tutorialExplainMovement()
        mainChar = src.gamestate.gamestate.mainChar
        mainChar.delListener(self.checkTutorialHelpClosed, "closedHelp")
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
        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        self.tutorialCheckMovement({"count":0,"lastPos":list(mainChar.getPosition())})

        mainChar.runCommandString(".",nativeKey=True)

    def tutorialCheckMovement(self,extraInfo=None):
        mainChar = src.gamestate.gamestate.mainChar

        if not tuple(extraInfo["lastPos"]) == mainChar.getPosition():
            extraInfo["count"] += 1
        extraInfo["lastPos"] = list(mainChar.getPosition())

        if extraInfo["count"] < 15:
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
 x for the message log

press space to continue with dropping items.
        """

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
other important interaction methods a are activating and examining items.

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
        submenu = src.interaction.InputMenu("Enter the code:")
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
To solve this the game offers you to dock menus to the left and right of the game map.

To do this you first open the inventory menu.
Then you click the < arrow of the subwindow or press left_shift + ESC to dock the window to the left.
Clicking the > arrow of the subwindow or pressing right_shift + ESC will dock the window to the right.

please dock the inventory and fill it with 10 items to see how it works
"""

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)

        characterPos = mainChar.getPosition()
        baseX = characterPos[0]//15
        baseY = characterPos[1]//15

        for i in range(0,30):
            scrap = src.items.itemMap["Scrap"](amount=1)
            mainChar.container.addItem(scrap,(baseX*15+random.randint(1,11),baseY*15+random.randint(1,11),0))

        self.checkDocking()

    def checkDocking(self):
        mainChar = src.gamestate.gamestate.mainChar

        if (mainChar.rememberedMenu or mainChar.rememberedMenu2) and len(mainChar.inventory) > 9:
            self.tutorialExplainUndocking()
            return
        else:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "checkDocking"})
            mainChar.container.addEvent(event)

    def tutorialExplainUndocking(self):

        text = """
One last but pretty important thing and you are done with the tutorial.

to undock menus click the < or > arrow of the docked menu nor
press left shift + ESC to undock left or
press right shift + ESC to undock right

undock and close all menus to continue
"""

        submenu = src.interaction.TextMenu(text)
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.runCommandString(".",nativeKey=True)

        self.checkUndocking()

    def checkUndocking(self):
        mainChar = src.gamestate.gamestate.mainChar

        if not (mainChar.rememberedMenu or mainChar.rememberedMenu2):
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

    def start(self, seed=0):
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
        src.gamestate.gamestate.mainChar.faction = "city test"

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

        jobArtwork = src.items.itemMap["JobArtwork"]()
        mainRoom.addItem(jobArtwork, (1, 3, 0))

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

    def start(self, seed=0):
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
    def start(self, seed=0):
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

        # place character in wakeup room
        if currentTerrain.wakeUpRoom:
            self.mainCharRoom = currentTerrain.wakeUpRoom
            self.mainCharRoom.addCharacter(src.gamestate.gamestate.mainChar, 2, 4)
        # place character on terrain
        else:
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

    def start(self, seed=0):
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

    def start(self, seed=0):

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

    def start(self, seed=0):
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

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# despite the effort sunk into the story, all of the phases below are obsolete
# and will need to be rewritten. The don't even run currently.
# ignore them
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

###############################################################################
#
#    these are the tutorial phases. The story phases are tweaked heavily regarding to cutscenes and timing
#
#    no experiments here!
#    half arsed solutions are still welcome here but that should end when this reaches prototype
#
################################################################################

################################################################################
#
#     The interaction between the implant before until birth
#
#     this should be a lot of fluff and guide the player into the game
#
################################################################################


"""
show some fluff messages and enforce learning how to use a selection
"""


class BrainTestingPhase(BasicPhase):
    """
    straightforward state initialization
    """

    def __init__(self, seed=0):
        super().__init__("BrainTesting", seed=seed)

    """
    show some messages and place trigger
    bad code: closely married to urwid
    """

    def start(self, seed=0):
        if src.gamestate.gamestate.successSeed > 0:
            self.end()
            return
        import urwid

        # show fluff
        showText(
            [
                """
     initializing subject ...................................... """,
                (urwid.AttrSpec("#2f2", "default"), "done"),
                """

     testing subject with random input 

     NyGUf8fDJO
     g215e4Za8U
     EpiSdpeNuV
     7vqnf7ASAO
     azZ1tESXGR
     sR6jzKMBv3
     eGAxLZCXXi
     DW9H6uAW8R
     dk8R9BXMfa
     Ttbt9kp2wZ

     checking subjects brain patterns .......................... """,
                (urwid.AttrSpec("#2f2", "default"), "OK"),
                """

     testing subjects responsivity
""",
            ],
            scrolling=True,
        )

        # show info that will be referenced later
        showText(
            [
                """
     got response
     responsivity .............................................. """,
                (urwid.AttrSpec("#2f2", "default"), "OK"),
                """

     inititializing implant .................................... """,
                (urwid.AttrSpec("#2f2", "default"), "done"),
                """

     checking implant .......................................... """,
                (urwid.AttrSpec("#2f2", "default"), "OK"),
                """

     send test information

     1.) Your name is """
                + src.gamestate.gamestate.mainChar.name
                + """
     2.) A Pipe is used to transfer fluids
     3.) rust - Rust is the oxide of iron. Rust is the most common form of corrosion
""",
            ],
            scrolling=True,
        )

        # show fluff
        showText(
            """
     checking stored information

     entering interactive mode .................................
        """,
            autocontinue=True,
            scrolling=True,
        )

        # add trigger for correct and wrong answers
        options = [
            ("nok", "Karl Weinberg"),
            ("ok", src.gamestate.gamestate.mainChar.name),
            ("nok", "Susanne Kreismann"),
        ]
        text = "\nplease answer the question:\n\nwhat is your name?"
        cinematic = src.cinematics.SelectionCinematic(text, options, default="ok")
        cinematic.followUps = {
            "ok": {"container": self, "method": "askSecondQuestion"},
            "nok": {"container": self, "method": "infoFail"},
        }
        self.cinematic = cinematic
        src.cinematics.cinematicQueue.append(cinematic)

    """
    show fluff and fail phase
    """

    def infoFail(self):
        import urwid

        showText(
            [
                "information storage ....................................... ",
                (urwid.AttrSpec("#f22", "default"), "NOT OK"),
                "                                        ",
            ],
            autocontinue=True,
            trigger={"container": self, "method": "fail"},
            scrolling=True,
        )
        return

    """
    ask question and place trigger
    """

    def askSecondQuestion(self):
        options = [
            ("ok", "A Pipe is used to transfer fluids"),
            ("nok", "A Grate is used to transfer fluids"),
            ("nok", "A Hutch is used to transfer fluids"),
        ]
        text = "\nplease select the true statement:\n\n"
        cinematic = src.cinematics.SelectionCinematic(text, options)
        cinematic.followUps = {
            "ok": {"container": self, "method": "askThirdQuestion"},
            "nok": {"container": self, "method": "infoFail"},
        }
        self.cinematic = cinematic
        src.cinematics.cinematicQueue.append(cinematic)

    """
    ask question and place trigger
    """

    def askThirdQuestion(self):
        options = [
            (
                "ok",
                "Rust is the oxide of iron. Rust is the most common form of corrosion",
            ),
            ("nok", "Rust is the oxide of iron. Corrosion in form of Rust is common"),
            ("nok", "*deny answer*"),
        ]
        text = "\nplease repeat the definition of rust\n\n"
        cinematic = src.cinematics.SelectionCinematic(text, options)
        cinematic.followUps = {
            "ok": {"container": self, "method": "flashInformation"},
            "nok": {"container": self, "method": "infoFail"},
        }
        self.cinematic = cinematic
        src.cinematics.cinematicQueue.append(cinematic)

    """
    show fluff info with effect and place trigger
    """

    def flashInformation(self):
        import urwid

        # set bogus information
        # bad code: this information should be a config
        definitions = {}
        definitions["pipe"] = "A Pipe is used to transfer fluids"
        definitions["wall"] = "A Wall is a non passable building element"
        definitions["door"] = "A Door is a moveable facility used to close a Opening"
        definitions["door"] = "A Lever is a tangent Device used to operate Something"
        definitions[
            "Flask"
        ] = "A Flask, better known as Flachman is a Container used to store Fluids"
        definitions["Coal"] = "Coal is a dark sedimentary Rock used to generate Engergy"
        definitions["Furnace"] = "A Furnace is a Device used to produce Heat"
        definitions["Boiler"] = "A Boiler is a Device used to heat Fluids"
        definitions[
            "GrowthTank"
        ] = "A GrowthTank is a Container used to grow new operation Units"
        definitions[
            "Hutch"
        ] = "A Hutch is a hollowed closable Container used to sleep in"
        definitions["Wrench "] = "A Wrench is a Tool used to tighten or loosen a Screw"
        definitions[
            "Screw"
        ] = "A Screw is a cylindric Element with a Thread used to connect Components"
        definitions["Goo"] = "Goo is the common Food"
        definitions["GooFlask"] = "A GooFlask is a Container used to transport Goo"
        definitions[
            "Goo Dispenser"
        ] = "A GooDispenser is a Machine which does dispose Goo"
        definitions[
            "Grate"
        ] = "A Grate is a horizontal flat Facility which is permeable and used to close an Opening"
        definitions["Corpse"] = "A Corpse is the Remain of a human Body"
        definitions[
            "UnconciousBody"
        ] = "A UnconciousBody is a Person which is not able to move and does not react"
        definitions["Pile"] = "A Container used to store Items like Coal"
        definitions["Acid"] = "Acid is used to produce Goo"
        definitions[
            "Floor"
        ] = "A Floor is a horizontal Construction at the Bottom of a Room or Building"
        definitions["BinStorage"] = "A Bin is a Container used to store Items"
        definitions["Chain"] = "A Chain is made of consecutive linked MetalRings"
        definitions[
            "Grid"
        ] = "A Grid is a vertical flat Facility which is mermeable and used to close an Opening"
        definitions["FoodStuffs"] = "FoodStuffs can be used as an alternative for Goo"
        definitions[
            "Machine"
        ] = "A Machine is a Mechanism used to execute Work automatically"
        definitions["Hub"] = "A Hub is a Facility to distribute Media like Steam"
        definitions["Steam"] = "Steam is a Medium made of Water and Heat"
        definitions[
            "Ramp"
        ] = "A Ramp is a horizontal Construction with a Gradient which is used to move between different Levels"
        definitions[
            "VatSnake"
        ] = "A VatSnake is an Animal that lives between the Remains in the Vat"
        definitions["Outlet"] = "An Outlet is used to distribute or dispense Media"
        definitions["Barricade"] = "A Barricade prohibits movement"
        definitions[
            "Clamp"
        ] = "A Clamp is a Facility used to pick up or grasp something"
        definitions[
            "Winch"
        ] = "A Winch is a Facility to support Movement of Items by using a Chain"
        definitions["Scrap"] = "A Scrap is a Piece of Metal"
        definitions["MetalBar"] = "A Metal Bar is a standatized Piece of Metal"

        # show fluff
        showText(
            [
                """ 
     information storage ....................................... """,
                (urwid.AttrSpec("#2f2", "default"), "OK"),
                """
     setting up knowledge base

""",
            ],
            autocontinue=True,
            scrolling=True,
        )

        cinematic = src.cinematics.InformationTransfer(definitions)
        src.cinematics.cinematicQueue.append(cinematic)

        # show fluff (write copy to messages to have this show up during zoom)
        src.gamestate.gamestate.mainChar.addMessage(
            "initializing metabolism ..................................... done"
        )
        src.gamestate.gamestate.mainChar.addMessage(
            "initializing motion control ................................. done"
        )
        src.gamestate.gamestate.mainChar.addMessage(
            "initializing sensory organs ................................. done"
        )
        src.gamestate.gamestate.mainChar.addMessage("transfer control to implant")

        # show fluff
        showText(
            [
                """
     initializing metabolism ..................................... """,
                (urwid.AttrSpec("#2f2", "default"), "done"),
                """
     initializing motion control ................................. """,
                (urwid.AttrSpec("#2f2", "default"), "done"),
                """
     initializing sensory organs ................................. """,
                (urwid.AttrSpec("#2f2", "default"), "done"),
                """
     transfer control to implant""",
            ],
            autocontinue=True,
            scrolling=True,
        )

        # zoom out and end phase
        cinematic = src.cinematics.MessageZoomCinematic()
        cinematic.endTrigger = {"container": self, "method": "end"}
        src.cinematics.cinematicQueue.append(cinematic)

    """
    call next phase
    """

    def end(self):
        nextPhase = WakeUpPhase()
        if src.gamestate.gamestate.successSeed < 1:
            src.gamestate.gamestate.successSeed += 1
        nextPhase.start()

    """
    kill the player
    """

    def fail(self):
        # kill player
        src.gamestate.gamestate.mainChar.dead = True
        src.gamestate.gamestate.mainChar.deathReason = "reset of neural network due to inability to store information\nPrevent this by answering the questions correctly"
        src.gamestate.gamestate.successSeed = 0

        # show fluff
        showText(
            """
     aborting initialization
     resetting neural network ....................................""",
            autocontinue=True,
            trigger={"container": self, "method": "forceExit"},
            scrolling=True,
        )

    """
    exit game
    bad code: urwid specific code
    """

    def forceExit(self):
        import urwid

        raise urwid.ExitMainLoop()


"""
show the main char waking up
"""


class WakeUpPhase(BasicPhase):
    """
    basic state initialization
    """

    def __init__(self, seed=0):
        super().__init__("WakeUpPhase", seed=seed)

    """
    show some fluff and place trigger
    """

    def start(self, seed=0):
        # place characters
        self.mainCharXPosition = 1
        self.mainCharYPosition = 4
        self.firstOfficerXPosition = 6
        self.firstOfficerYPosition = 4
        self.requiresMainCharRoomFirstOfficer = True
        self.requiresMainCharRoomSecondOfficer = False

        # start timer for tracking performance
        src.gamestate.gamestate.mainChar.tutorialStart = src.gamestate.gamestate.tick

        # make main char hungry and naked
        src.gamestate.gamestate.mainChar.satiation = 400
        src.gamestate.gamestate.mainChar.inventory = []
        # bad code: purging a characters quests should be a method
        for quest in src.gamestate.gamestate.mainChar.quests:
            quest.deactivate()
        src.gamestate.gamestate.mainChar.quests = []

        # set the wake up room as play area
        # bad code: should be set elsewhere
        self.mainCharRoom = src.gamestate.gamestate.terrain.wakeUpRoom

        super().start(seed=seed)

        # hide main char from map
        if src.gamestate.gamestate.mainChar in self.mainCharRoom.characters:
            self.mainCharRoom.characters.remove(src.gamestate.gamestate.mainChar)
        src.gamestate.gamestate.mainChar.terrain = None

        # select npc
        self.npc = self.mainCharRoom.firstOfficer

        # show fluff
        showGame(2)
        showMessage("implant has taken control")
        showMessage("please press %s" % config.commandChars.wait)
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowGameCinematic(1, tickSpan=None)
        )
        showMessage(
            """you will be represented by the """
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.main_char]
            + " Character,  "
            + self.npc.name
            + " is represented by the "
            + src.canvas.displayChars.indexedMapping[self.npc.display]
            + """ Character."""
        )
        showMessage("please press %s" % config.commandChars.wait)
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowGameCinematic(1, tickSpan=None)
        )
        showMessage("please prepare to be ejected")
        showGame(2)
        showMessage("note that you will be unable to move until implant imprinting")
        showGame(6)
        showMessage("ejecting now")
        showGame(2)
        showMessage("*ting*")
        showGame(1)
        showMessage("*screetch*")

        # add trigger
        showGame(1, trigger={"container": self, "method": "playerEject"})

    """
    spawn players body and place trigger
    """

    def playerEject(self):
        # add players body
        src.gamestate.gamestate.terrain.wakeUpRoom.itemByCoordinates[(1, 4)][0].eject(
            src.gamestate.gamestate.mainChar
        )

        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer

        # show fluff
        showMessage("*schurp**splat*")
        showGame(2)
        showMessage("please wait for assistance")
        showGame(2)
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 3, 4
        )
        showQuest(quest, firstOfficer)
        say(
            "I AM " + firstOfficer.name.upper() + " AND I DEMAND YOUR SERVICE.",
            firstOfficer,
        )

        # add serve quest
        quest = src.quests.Serve(firstOfficer)
        src.gamestate.gamestate.mainChar.serveQuest = quest
        src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)

        # show fluff
        showGame(1)
        showMessage("implant imprinted - setup complete")
        showGame(4)
        say("wake up, " + src.gamestate.gamestate.mainChar.name, firstOfficer)
        showGame(3)
        say("WAKE UP.", firstOfficer)
        showGame(2)
        say("WAKE UP.", firstOfficer)
        showMessage("*kicks " + src.gamestate.gamestate.mainChar.name + "*")

        # show fluff
        showGame(3, trigger={"container": self, "method": "addPlayer"})

    """
    add the player and place triggers
    """

    def addPlayer(self):
        src.gamestate.gamestate.mainChar.wakeUp()

        # redraw
        src.interaction.loop.set_alarm_in(0.1, src.interaction.callShow_or_exit, ".")

        # wrap up
        self.end()

    """
    start next phase
    """

    def end(self):
        phase = BasicMovementTraining()
        phase.start(seed=self.seed)
        src.gamestate.gamestate.successSeed += 1

    """
    set internal state from dictionary
    """

    def setState(self, state):
        super().setState(state)

        # bad code: knowingly breaking state instead of setting a camera focus
        if (
            not src.gamestate.gamestate.mainChar.room
            and not src.gamestate.gamestate.mainChar.terrain
        ):
            src.gamestate.gamestate.terrain.wakeUpRoom.addCharacter(
                src.gamestate.gamestate.mainChar, 3, 3
            )

            if (
                src.gamestate.gamestate.mainChar
                in src.gamestate.gamestate.terrain.wakeUpRoom.characters
            ):
                src.gamestate.gamestate.terrain.wakeUpRoom.characters.remove(
                    src.gamestate.gamestate.mainChar
                )
            src.gamestate.gamestate.mainChar.terrain = None


################################################################################
#
#    The testing/tutorial phases
#
#    ideally these phases should force the player how rudementary use of the controls.
#    This should be done by explaining first and then preventing progress until the
#    player proves capability.
#
################################################################################

"""
explain and test basic movement and interaction
"""


class BasicMovementTraining(BasicPhase):

    """
    basic state initialization
    """

    def __init__(self, seed=0):
        super().__init__("BasicMovementTraining", seed=seed)
        self.didFurnaces = False

    """
    make the player move around and place triggers
    """

    def start(self, seed=0):
        # minimal setup
        self.mainCharXPosition = 2
        self.mainCharYPosition = 4
        self.requiresMainCharRoomFirstOfficer = True
        self.requiresMainCharRoomSecondOfficer = False
        self.mainCharRoom = src.gamestate.gamestate.terrain.wakeUpRoom

        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer

        # smooth over missing info
        # bad code: should not be necessary
        if not hasattr(src.gamestate.gamestate.mainChar, "tutorialStart"):
            src.gamestate.gamestate.mainChar.tutorialStart = (
                src.gamestate.gamestate.tick - 100
            )

        # smooth over missing info
        # bad code: should not be necessary
        if not hasattr(src.gamestate.gamestate.mainChar, "serveQuest"):
            quest = src.quests.Serve(firstOfficer)
            src.gamestate.gamestate.mainChar.serveQuest = quest
            src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)

        super().start(seed=seed)

        # show instructions
        say(
            "you are not missing no big parts and passed the first checks", firstOfficer
        )
        say("next you need to prove you are able to follow orders", firstOfficer)
        say("follow me, please", firstOfficer)
        showText(
            [
                """
 welcome to the trainingsenvironment.

 please follow the orders """
                + firstOfficer.name
                + """ gives you.

 dialog and other information are shown in the infobox on the top right like this:

     """
                + src.canvas.displayChars.indexedMapping[firstOfficer.display]
                + """: you are not missing no big parts and passed the first checks
     """
                + src.canvas.displayChars.indexedMapping[firstOfficer.display]
                + """: next you need to prove you are able to follow orders
     """
                + src.canvas.displayChars.indexedMapping[firstOfficer.display]
                + """: follow me, please
     
 you are represented by the """,
                src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.main_char
                ],
                " Character,  ",
                firstOfficer.name,
                " is represented by the ",
                src.canvas.displayChars.indexedMapping[firstOfficer.display],
                """ Character. 

 you can move using the keyboard. 

 * press """,
                config.commandChars.move_north,
                """ to move up/north
 * press """,
                config.commandChars.move_west,
                """ to move left/west
 * press """,
                config.commandChars.move_south,
                """ to move down/south
 * press """,
                config.commandChars.move_east,
                """ to move right/east

 Your target is marked by """
                + src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.questTargetMarker
                ][1]
                + """ and a path to your target is highlighted. You may follow this path or find your own way""",
            ]
        )
        showGame(1)

        # ask the player to follow npc
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 4, 4
        )
        showQuest(quest, firstOfficer)
        showMessage(
            "the current quest destination is shown as: "
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.questTargetMarker
            ][1]
        )
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 3, 4
        )
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 5, 4
        )
        showQuest(quest, firstOfficer)
        say("follow me, please", firstOfficer)
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 4, 4
        )
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 6, 7
        )
        showQuest(quest, firstOfficer)
        say("follow me, please", firstOfficer)
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 5, 7
        )
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )

        # ask player to move around
        say("now prove that you are able to walk on your own", firstOfficer)
        say("move to the designated target, please", firstOfficer)
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 2, 7
        )
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )
        say("move to the designated target, please", firstOfficer)
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 4, 3
        )
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )
        say("move to the designated target, please", firstOfficer)
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 6, 6
        )
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )
        say("great. You seemed be able to coordinate yourself", firstOfficer)
        showGame(1)
        say("you look thirsty, go and get some goo to drink", firstOfficer)

        # ask player to move to the lever
        showGame(2)
        say("move over to the lever now", firstOfficer)
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 3, 2
        )
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )

        import urwid

        # show instructions
        showText(
            [
                """
    you can activate levers by moving onto the lever and then pressing """
                + config.commandChars.activate
                + """\n
    Here is how to do this:\n\nImagine you are standing next to a lever

    """,
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                """
    """,
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.lever_notPulled
                ],
                "U\\",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                """
    """,
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.main_char
                ],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                """

   press """
                + config.commandChars.move_north
                + """ to move onto the lever and press """
                + config.commandChars.activate
                + """ to activate the lever.
   After pulling the lever a flask should apear like this:

   """,
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                """
   """,
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.main_char
                ],
                "U\\",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                """
   """,
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                (urwid.AttrSpec("#3f3", "black"), "ò="),
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                """

   now, go and pull the lever
""",
            ]
        )
        showMessage(
            "you can activate levers by moving onto the lever and then pressing "
            + config.commandChars.activate
        )

        # ask player to pull the lever and add trigger
        say("activate the lever", firstOfficer)
        quest = src.quests.ActivateQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom.lever1
        )
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            trigger={"container": self, "method": "fetchDrink"},
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )

    """
    make the main char fetch the bottle
    """

    def fetchDrink(self):
        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer
        drink = src.gamestate.gamestate.terrain.wakeUpRoom.itemsOnFloor[-1]

        # show instructions
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer
        msg = (
            """
    you produced yourself a goo flask. It looks like this: ò= when full and like this: ò- when half empty. You may pick up your flask now. The machine should have dumped it on the floor near you.
        
    you can pick up items by moving onto them and pressing """
            + config.commandChars.pickUp
            + """. 

    your inventory can hold 10 items and can be accessed by pressing """
            + config.commandChars.show_inventory
            + """.

    usually everyone carries at least a flask of goo. You need to drink at least every 1000 ticks by pressing """
            + config.commandChars.drink
            + """ 

    """
        )
        showText(msg)
        showMessage(
            """you can pick up items by moving onto them and pressing """
            + config.commandChars.pickUp
            + """."""
        )
        say("well done, go and fetch your drink", firstOfficer)

        # ask the player to pick up the flask
        quest = src.quests.PickupQuestMeta(drink)
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            trigger={"container": self, "method": "drinkStuff"},
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )

    """
    make the main char drink and direct the player to a chat
    """

    def drinkStuff(self):
        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer
        src.gamestate.gamestate.mainChar.assignQuest(src.quests.SurviveQuest())

        # show instructions
        say(
            "great. Drink from the flask you just fetched and come over for a quick talk.",
            firstOfficer,
        )
        msg = (
            "you can drink using "
            + config.commandChars.drink
            + ". If you do not drink for 1000 ticks you will starve"
        )
        showMessage(msg)

        # ask the player to drink and return
        quest = src.quests.DrinkQuest()
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 6, 6
        )
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )

        say(msg, firstOfficer)
        text = "I see you are in working order. Do you have any injuries?"
        options = [("no", "No"), ("yes", "Yes")]
        cinematic = src.cinematics.SelectionCinematic(text, options)
        cinematic.followUps = {
            "no": {"container": self, "method": "notinjured"},
            "yes": {"container": self, "method": "injured2Question"},
        }
        src.cinematics.cinematicQueue.append(cinematic)

    def injured2Question(self):
        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer

        text = "I will issue a complaint to have the growth tank fixed.\n\nDo you think you will be able to work?"
        options = [("yes", "Yes"), ("no", "No")]
        cinematic = src.cinematics.SelectionCinematic(text, options)
        cinematic.followUps = {
            "yes": {"container": self, "method": "notinjured"},
            "no": {"container": self, "method": "injuredToVat"},
        }
        src.cinematics.cinematicQueue.append(cinematic)

    def injuredToVat(self):
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer
        msg = "Then it is best to dispose of you sooner than later. Thanks for the honesty, please start vat duty now"
        say(msg, firstOfficer)
        showText("     " + msg)
        src.gamestate.gamestate.mainChar.hasFloorPermit = True
        VatPhase().start(seed=self.seed)

    def notinjured(self):
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer
        msg = "great. You passed the basic tests. You are a candidate for the hopper duty."
        msg2 = "Until the selection process is completed, your duty is to assist me."
        msg3 = "Reset the lever first and then talk to me for more jobs"
        say(msg, firstOfficer)
        say(msg2, firstOfficer)
        say(msg3, firstOfficer)
        showText("     " + msg + "\n\n     " + msg2 + "\n\n     " + msg3)
        quest = src.quests.ActivateQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom.lever1
        )
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            trigger={"container": self, "method": "chatter"},
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )

    def chatter(self):
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer

        msg = (
            "you can talk to people by pressing "
            + config.commandChars.hail
            + " and selecting the person to talk to."
        )
        showMessage(msg)
        showText(
            """

    after dooing a task talk to your superior and check back for new tasks.

    """
            + msg
            + """
    """
        )

        # add chat options
        firstOfficer.basicChatOptions.append(
            {
                "dialogName": "I did the task. Are there more things to do?",
                "chat": src.chats.TutorialSpeechTest,
                "params": {"firstOfficer": firstOfficer, "phase": self},
            }
        )
        firstOfficer.basicChatOptions.append(
            {
                "dialogName": "What are these machines in this room?",
                "chat": src.chats.FurnaceChat,
                "params": {
                    "firstOfficer": firstOfficer,
                    "phase": self,
                    "terrain": src.gamestate.gamestate.terrain,
                },
            }
        )

    """
    make the player fire a furnace. no triggers placed
    """

    def fireFurnaces(self):

        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer
        furnace = src.gamestate.gamestate.terrain.wakeUpRoom.furnace

        # reward player
        src.gamestate.gamestate.mainChar.awardReputation(
            amount=2, reason="getting extra training"
        )

        # show fluff
        showText(
            "you are in luck. The furnace is for training and you are free to use it.\n\nYou need something to burn in the furnace first, so fetch some coal from the pile and then you can light the furnace.\nIt will stop burning after some ticks so keeping a fire burning can get quite tricky sometimes"
        )

        # show instructions
        showText(
            [
                """Here is an example on how to do this:\n\nImagine you are standing next to a pile of coal

""",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canavs.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                """
""",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.main_char
                ],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                """
""",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.furnace_inactive
                ],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.pile],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                """
""",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                """

take a piece of coal by pressing """
                + config.commandChars.move_south
                + """ to walk against the pile and activating it by pressing """
                + config.commandChars.activate
                + """ immediatly afterwards.

You may press """
                + config.commandChars.show_inventory
                + """ to confirm you have a piece of coal in your inventory.

To activate the furnace press """
                + config.commandChars.move_west
                + """ to move next to it, press s to walk against it and press """
                + config.commandChars.activate
                + """ immediatly afterwards to activate it.

The furnace should be fired now and if you check your inventory afterwards you will see that
you have on piece of coal less than before.""",
            ]
        )

        # ask the player to fire a furnace
        self.didFurnaces = True
        say("go on and fire the furnace", firstOfficer)
        quest = src.quests.FireFurnaceMeta(furnace)
        showQuest(
            quest,
            src.gamestate.gamestate.mainChar,
            container=src.gamestate.gamestate.mainChar.serveQuest,
        )

    """
    abort the optional furnace fireing and place trigger
    """

    def noFurnaceFirering(self):

        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer
        src.gamestate.gamestate.mainChar.revokeReputation(
            amount=1, reason="not getting extra training"
        )

        # place trigger
        showText(
            "i understand. The burns are somewhat unpleasant",
            trigger={"container": self, "method": "iamready"},
        )

    """
    make the player examine things
    """

    def examineStuff(self):
        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer

        # show fluff
        showText(
            [
                """
    examine the room and learn to find your way around, please

    Here is an example on how to do this:\n\nWalk onto or against the items you want to examine and press e directly afterwards to examine something.\nImagine you are standing next to a lever:

""",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                """
""",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.lever_notPulled
                ],
                src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.main_char
                ],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                """
""",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                """

To examine the lever you have to press """
                + config.commandChars.move_west
                + """ to move onto the lever and then press """
                + config.commandChars.examine
                + """ to examine it.

Imagine a situation where you want to examine an object you can not walk onto something:

""",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                """
""",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.furnace_inactive
                ],
                src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.main_char
                ],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.floor],
                """
""",
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall],
                """

In this case you still have to press """
                + config.commandChars.move_west
                + """ to walk against the object and the press """
                + config.commandChars.examine
                + """ directly afterwards to examine it.
""",
            ]
        )
        showMessage(
            "walk onto or into something and press e directly afterwards to examine something"
        )

        # add examine quest
        quest = src.quests.ExamineQuest()
        quest.endTrigger = {"container": self, "method": "addGrowthTankRefill"}
        src.gamestate.gamestate.mainChar.serveQuest.addQuest(quest)

    def addGrowthTankRefill(self):
        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer

        firstOfficer.basicChatOptions.append(
            {
                "dialogName": "I did the task. Are there more things to do?",
                "chat": src.chats.GrowthTankRefillChat,
                "params": {"firstOfficer": firstOfficer, "phase": self},
            }
        )

    def doTask1(self):
        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer

        quest = src.quests.FillGrowthTankMeta(
            growthTank=src.gamestate.gamestate.terrain.wakeUpRoom.growthTanks[0]
        )
        quest.endTrigger = {"container": self, "method": "doTask2"}
        src.gamestate.gamestate.mainChar.serveQuest.addQuest(quest)

    def doTask2(self):
        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer

        quest = src.quests.FillGrowthTankMeta(
            growthTank=src.gamestate.gamestate.terrain.wakeUpRoom.growthTanks[3]
        )
        quest.endTrigger = {"container": self, "method": "iamready"}
        src.gamestate.gamestate.mainChar.serveQuest.addQuest(quest)

    """
    wait till expected completion time has passed
    """

    def iamready(self):

        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer

        timeTaken = (
            src.gamestate.gamestate.tick
            - src.gamestate.gamestate.mainChar.tutorialStart
        )
        normTime = 500

        # make the player wait till norm completion time
        #
        # if timeTaken < normTime/2:
        #    msg1 = "You work fast. You did the tasks in less then half of the norm completion time."
        #    msg2 = "You will not work as a hopper, you will continue to serve under me."
        #    msg3 = "The order for a hopper still has to be fulfilled."
        #    msg4 = "please activate one of the growth tanks"
        #    text = "\n"+msg1+"\n"+msg2+"\n\n"+msg3+"\n"+msg4+"\n"

        #    showText(text)
        #    say(msg1,firstOfficer)
        #    say(msg2,firstOfficer)
        #    say(msg3,firstOfficer)
        #    say(msg4,firstOfficer)

        #    return

        # show evaluation
        text = (
            "you completed the tests and it is time to take on your duty. You will no longer server under my command, but under "
            + src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer.name
            + " as a hopper.\n\nSo please go to the waiting room and report for room duty.\n\nThe waiting room is the next room to the north. Simply go there speak to "
            + src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer.name
            + " and confirm that you are reporting for duty.\nYou will get instruction on how to proceed afterwards.\n\n"
        )
        if self.didFurnaces:
            text += "A word of advice from my part:\nYou are able to just not report for duty, but you have to expect to die alone.\nAlso staying on a mech with expired permit will get the guards attention pretty fast.\nSo just follow your orders and work hard, so you will be giving the orders."
        showText(text, rusty=True)
        for line in text.split("\n"):
            if line == "":
                continue
            say(line, firstOfficer)

        # get time needed
        text = (
            "it took you "
            + str(timeTaken)
            + " ticks to complete the tests. The norm completion time is 500 ticks.\n\n"
        )

        # scold the player for taking to long
        if timeTaken > normTime:
            text += "you better speed up and stop wasting time.\n\n"
            showText(text)
            self.trainingCompleted()
            src.gamestate.gamestate.mainChar.revokeReputation(
                amount=2, reason="not completing test in time"
            )
        else:
            text += (
                "We are "
                + str(normTime - timeTaken)
                + " ticks ahead of plan. This means your floor permit is not valid yet. Please wait for "
                + str(normTime - timeTaken)
                + " ticks.\n\nNoncompliance will result in a kill order to the military. Military zones and movement restrictions are security and therefore high priority.\n\nIn order to not waste time, feel free to ask questions in the meantime.\n"
            )
            quest = src.quests.WaitQuest(lifetime=normTime - timeTaken)
            showText(text)
            quest.endTrigger = {"container": self, "method": "trainingCompleted"}
            src.gamestate.gamestate.mainChar.serveQuest.addQuest(quest)

            # reward player
            src.gamestate.gamestate.mainChar.awardReputation(
                amount=1, reason="completing test in time"
            )

    """
    wrap up
    """

    def trainingCompleted(self):

        # alias attributes
        firstOfficer = src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer

        # make player mode to the next room
        # bad pattern: this should be part of the next phase
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.wakeUpRoom, 5, 1
        )
        firstOfficer.assignQuest(quest, active=True)

        # move npc to default position
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.waitingRoom, 9, 4
        )
        src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)
        src.gamestate.gamestate.mainChar.hasFloorPermit = True

        # trigger final wrap up
        quest.endTrigger = {"container": self, "method": "end"}

    """
    start next phase
    """

    def end(self):
        phase = FindWork()
        phase.start(seed=self.seed)


#######################################################
#
#      the old tutorial, needs cleanup and reintegration
#
#######################################################

"""
explain how to steam generation works and give a demonstration
"""


class BoilerRoomWelcome(BasicPhase):
    """
    straightforward state initialization
    """

    def __init__(self, seed=0):
        super().__init__("BoilerRoomWelcome", seed=seed)

    """
    set up a basic intro
    bad code: many inline functions
    """

    def start(self, seed=0):
        # alias attributes
        self.mainCharRoom = src.gamestate.gamestate.terrain.tutorialMachineRoom

        super().start(seed=seed)

        # move player to machine room if the player isn't there yet
        if not (
            src.gamestate.gamestate.mainChar.room
            and src.gamestate.gamestate.mainChar.room
            == src.gamestate.gamestate.terrain.tutorialMachineRoom
        ):
            self.mainCharQuestList.append(
                src.quests.EnterRoomQuestMeta(
                    src.gamestate.gamestate.terrain.tutorialMachineRoom,
                    startCinematics="please goto the Machineroom",
                )
            )

        # properly hook the players quests
        self.assignPlayerQuests()

        # start the action
        self.doBasicSchooling()

    """
    start next sub phase
    """

    def wrapUpBasicSchooling(self):
        src.gamestate.gamestate.mainChar.gotBasicSchooling = True
        self.doSteamengineExplaination()

    """
    greet player and trigger next function
    """

    def doBasicSchooling(self):
        if not src.gamestate.gamestate.mainChar.gotBasicSchooling:
            # show greeting one time
            src.cinematics.showCinematic(
                "welcome to the boiler room\n\nplease, try to learn fast.\n\nParticipants with low Evaluationscores will be given suitable Assignments in the Vats"
            )
            cinematic = src.cinematics.ShowGameCinematic(1)
            cinematic.endTrigger = self.wrapUpBasicSchooling
            src.cinematics.cinematicQueue.append(cinematic)
        else:
            # start next step
            self.doSteamengineExplaination()

    """
    start next sub phase
    """

    def wrapUpSteamengineExplaination(self):
        self.doCoalDelivery()

    """
    explain how the steam engine work and continue
    """

    def doSteamengineExplaination(self):
        # explain how the room works
        src.cinematics.showCinematic(
            "on the southern Side of the Room you see the Steamgenerators. A Steamgenerator might look like this:\n\n"
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.void][1]
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.pipe][1]
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.boiler_inactive
            ][1]
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.furnace_inactive
            ][1]
            + "\n"
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.pipe][1]
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.pipe][1]
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.boiler_inactive
            ][1]
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.furnace_inactive
            ][1]
            + "\n"
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.void][1]
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.pipe][1]
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.boiler_active
            ][1]
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.furnace_active
            ][1]
            + "\n\nit consist of Furnaces marked by "
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.furnace_inactive
            ][1]
            + " or "
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.furnace_active
            ][1]
            + " that heat the Water in the Boilers "
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.boiler_inactive
            ][1]
            + " till it boils. a Boiler with boiling Water will be shown as "
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.boiler_active
            ][1]
            + ".\n\nthe Steam is transfered to the Pipes marked with "
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.pipe][1]
            + " and used to power the Ships Mechanics and Weapons\n\nDesign of Generators are often quite unique. try to recognize the Genrators in this Room and press "
            + config.commandChars.wait
            + ""
        )

        src.cinematics.cinematicQueue.append(src.cinematics.ShowGameCinematic(1))
        src.cinematics.showCinematic(
            "the Furnaces burn Coal shown as "
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.coal][1]
            + " . if a Furnace is burning Coal, it is shown as "
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.furnace_active
            ][1]
            + " and shown as "
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.furnace_inactive
            ][1]
            + " if not.\n\nthe Coal is stored in Piles shown as "
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.pile][1]
            + ". the Coalpiles are on the right Side of the Room and are filled through the Pipes when needed."
        )

        # start next step
        cinematic = src.cinematics.ShowGameCinematic(
            0
        )  # bad code: this cinematic is a hack
        cinematic.endTrigger = self.wrapUpSteamengineExplaination
        src.cinematics.cinematicQueue.append(cinematic)

    """
    advance the game
    """

    def advance(self):
        src.interaction.loop.set_alarm_in(0.1, src.interaction.callShow_or_exit, ".")

    """
    start next sub phase
    """

    def wrapUpCoalDelivery(self):
        self.doFurnaceFirering()

    """
    fake a coal delivery
    """

    def doCoalDelivery(self):

        # show fluff
        src.cinematics.showCinematic(
            "Since a Coaldelivery is incoming anyway. please wait and pay Attention.\n\ni will count down the Ticks in the Messagebox now"
        )

        """
        the event for faking a coal delivery
        bad code: should be gone or in events.py
        """

        class CoalRefillEvent(src.events.Event):
            """
            basic state initialization
            """

            def __init__(subself, tick, creator=None, seed=0):
                super().__init__(tick, creator=creator, seed=seed)
                subself.tick = tick

            """
            add coal
            """

            def handleEvent(subself):
                # show fluff
                src.gamestate.gamestate.mainChar.addMessage("*rumbling*")
                src.gamestate.gamestate.mainChar.addMessage("*rumbling*")
                src.gamestate.gamestate.mainChar.addMessage(
                    "*smoke and dust on Coalpiles and neighbourng Fields*"
                )
                src.gamestate.gamestate.mainChar.addMessage(
                    "*a chunk of Coal drops onto the floor*"
                )
                src.gamestate.gamestate.mainChar.addMessage("*smoke clears*")

                # add delivered items (including mouse)
                self.mainCharRoom.addItems([src.items.itemMap["Coal"](7, 5)])
                self.mainCharRoom.addCharacter(characters.Mouse(), 6, 5)

        # add the coal delivery
        self.mainCharRoom.addEvent(
            CoalRefillEvent(
                src.gamestate.gamestate.tick + 11,
            )
        )

        # count down to the coal delivery
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowGameCinematic(1, tickSpan=1)
        )
        src.cinematics.cinematicQueue.append(src.cinematics.ShowMessageCinematic("8"))
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowGameCinematic(1, tickSpan=1)
        )
        src.cinematics.cinematicQueue.append(src.cinematics.ShowMessageCinematic("7"))
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowMessageCinematic(
                "by the Way: the Piles on the lower End of the Room are Storage for Replacementparts and you can sleep in the Hutches n the middle of the Room shown as "
                + src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.hutch_free
                ][1]
                + " or "
                + src.canvas.displayChars.indexedMapping[
                    src.canvas.displayChars.hutch_occupied
                ][1]
            )
        )
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowGameCinematic(1, tickSpan=1)
        )
        src.cinematics.cinematicQueue.append(src.cinematics.ShowMessageCinematic("6"))
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowGameCinematic(1, tickSpan=1)
        )
        src.cinematics.cinematicQueue.append(src.cinematics.ShowMessageCinematic("5"))
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowGameCinematic(1, tickSpan=1)
        )
        src.cinematics.cinematicQueue.append(src.cinematics.ShowMessageCinematic("4"))
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowGameCinematic(1, tickSpan=1)
        )
        src.cinematics.cinematicQueue.append(src.cinematics.ShowMessageCinematic("3"))
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowGameCinematic(1, tickSpan=1)
        )
        src.cinematics.cinematicQueue.append(src.cinematics.ShowMessageCinematic("2"))
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowGameCinematic(1, tickSpan=1)
        )
        src.cinematics.cinematicQueue.append(src.cinematics.ShowMessageCinematic("1"))
        cinematic = src.cinematics.ShowGameCinematic(1, tickSpan=1)

        cinematic.endTrigger = self.advance
        src.cinematics.cinematicQueue.append(cinematic)
        src.cinematics.cinematicQueue.append(
            src.cinematics.ShowMessageCinematic("Coaldelivery now")
        )
        cinematic = src.cinematics.ShowGameCinematic(2)
        cinematic.endTrigger = self.wrapUpCoalDelivery
        src.cinematics.cinematicQueue.append(cinematic)

    """
    start next step
    """

    def wrapUpFurnaceFirering(self):
        self.doWrapUp()

    """
    make a npc fire a furnace 
    """

    def doFurnaceFirering(self):
        # show fluff
        src.cinematics.showCinematic(
            "your cohabitants in this Room are:\n '"
            + self.mainCharRoom.firstOfficer.name
            + "' ("
            + src.canvas.displayChars.indexedMapping[
                self.mainCharRoom.firstOfficer.display
            ][1]
            + ") is this Rooms 'Raumleiter' and therefore responsible for proper Steamgeneration in this Room\n '"
            + self.mainCharRoom.secondOfficer.name
            + "' ("
            + src.canvas.displayChars.indexedMapping[
                self.mainCharRoom.secondOfficer.display
            ][1]
            + ") was dispatched to support '"
            + self.mainCharRoom.firstOfficer.name
            + "' and is his Subordinate\n\nyou will likely report to '"
            + self.mainCharRoom.firstOfficer.name
            + "' later. please try to find them on the display and press "
            + config.commandChars.wait
        )
        src.cinematics.cinematicQueue.append(src.cinematics.ShowGameCinematic(1))
        src.cinematics.showCinematic(
            self.mainCharRoom.secondOfficer.name
            + " will demonstrate how to fire a furnace now.\n\nwatch and learn."
        )

        """
        add the quests for firering a furnace
        """

        class AddQuestEvent(src.events.Event):
            """
            straightforward state initialization
            """

            def __init__(subself, tick, creator=None):
                super().__init__(tick, creator=creator)
                subself.tick = tick

            """
            add quests for firing a furnace
            """

            def handleEvent(subself):
                quest = src.quests.FireFurnaceMeta(self.mainCharRoom.furnaces[2])
                self.mainCharRoom.secondOfficer.assignQuest(quest, active=True)

        """
        event for showing a message
        bad code: should be abstracted
        """

        class ShowMessageEvent(src.events.Event):
            """
            straightforward state initialization
            """

            def __init__(subself, tick, creator=None):
                super().__init__(tick, creator=creator)
                subself.tick = tick

            """
            show the message
            """

            def handleEvent(subself):
                src.gamestate.gamestate.mainChar.addMessage(
                    "*"
                    + self.mainCharRoom.secondOfficer.name
                    + ", please fire the Furnace now*"
                )

        # set up the events
        self.mainCharRoom.addEvent(ShowMessageEvent(src.gamestate.gamestate.tick + 1))
        self.mainCharRoom.addEvent(AddQuestEvent(src.gamestate.gamestate.tick + 2))
        cinematic = src.cinematics.ShowGameCinematic(
            22, tickSpan=1
        )  # bad code: should be showQuest to prevent having a fixed timing

        cinematic.endTrigger = self.wrapUpFurnaceFirering
        src.cinematics.cinematicQueue.append(cinematic)

    """
    show some info and start next phase
    """

    def doWrapUp(self):

        # show some information
        src.cinematics.showCinematic(
            "there are other Items in the Room that may or may not be important for you. Here is the full List for you to review:\n\n Bin ("
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.binStorage
            ][1]
            + "): Used for storing Things intended to be transported further\n Pile ("
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.pile][1]
            + "): a Pile of Things\n Door ("
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.door_opened
            ][1]
            + " or "
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.door_closed
            ][1]
            + "): you can move through it when open\n Lever ("
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.lever_notPulled
            ][1]
            + " or "
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.lever_pulled
            ][1]
            + "): a simple Man-Machineinterface\n Furnace ("
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.furnace_inactive
            ][1]
            + "): used to generate heat burning Things\n Display ("
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.display][1]
            + "): a complicated Machine-Maninterface\n Wall ("
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.wall][1]
            + "): ensures the structural Integrity of basically any Structure\n Pipe ("
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.pipe][1]
            + "): transports Liquids, Pseudoliquids and Gasses\n Coal ("
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.coal][1]
            + "): a piece of Coal, quite usefull actually\n Boiler ("
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.boiler_inactive
            ][1]
            + " or "
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.boiler_active
            ][1]
            + "): generates Steam using Water and and Heat\n Chains ("
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.chains][1]
            + "): some Chains dangling about. sometimes used as Man-Machineinterface or for Climbing\n Comlink ("
            + src.canvas.displayChars.indexedMapping[src.canvas.displayChars.commLink][
                1
            ]
            + "): a Pipe based Voicetransportationsystem that allows Communication with other Rooms\n Hutch ("
            + src.canvas.displayChars.indexedMapping[
                src.canvas.displayChars.hutch_free
            ][1]
            + "): a comfy and safe Place to sleep and eat"
        )

        """
        event for starting the next phase
        """

        class StartNextPhaseEvent(src.events.Event):
            """
            straightforward state initialization
            """

            def __init__(subself, tick, creator=None):
                super().__init__(tick, creator=creator)
                subself.tick = tick

            """
            start next phase
            """

            def handleEvent(subself):
                self.end()

        # schedule the wrap up
        self.mainCharRoom.addEvent(
            StartNextPhaseEvent(src.gamestate.gamestate.tick + 1)
        )

    """
    start next phase
    """

    def end(self):
        src.cinematics.showCinematic(
            "please try to remember the Information. The lesson will now continue with Movement."
        )
        phase2 = BoilerRoomInteractionTraining()
        phase2.start(self.seed)


"""
teach basic interaction
"""


class BoilerRoomInteractionTraining(BasicPhase):
    """
    straightforward state initialization
    """

    def __init__(self, seed=0):
        super().__init__("BoilerRoomInteractionTraining", seed=seed)

    """
    explain interaction and make the player apply lessons
    """

    def start(self, seed=0):
        self.mainCharRoom = src.gamestate.gamestate.terrain.tutorialMachineRoom

        super().start(seed=seed)

        # make the player make a simple move
        questList = []
        questList.append(
            src.quests.MoveQuestMeta(
                self.mainCharRoom,
                5,
                5,
                startCinematics="Movement can be tricky sometimes so please make yourself comfortable with the controls.\n\nyou can move in 4 Directions along the x and y Axis. the z Axis is not supported yet. diagonal Movements are not supported since they do not exist.\n\nthe basic Movementcommands are:\n "
                + config.commandChars.move_north
                + "=up\n "
                + config.commandChars.move_east
                + "=right\n "
                + config.commandChars.move_south
                + "=down\n "
                + config.commandChars.move_west
                + "=right\n\nplease move to the designated Target. the Implant will mark your Way",
            )
        )

        # make the player move around
        if not src.gamestate.gamestate.mainChar.gotMovementSchooling:
            quest = src.quests.MoveQuestMeta(self.mainCharRoom, 4, 3)

            def setPlayerState():
                src.gamestate.gamestate.mainChar.gotMovementSchooling = True

            quest.endTrigger = setPlayerState
            questList.append(quest)
            questList.append(
                src.quests.MoveQuestMeta(
                    self.mainCharRoom,
                    3,
                    3,
                    startCinematics="thats enough. move back to waiting position",
                )
            )

        # make the player examine the map
        if not src.gamestate.gamestate.mainChar.gotExamineSchooling:
            quest = src.quests.MoveQuestMeta(self.mainCharRoom, 4, 3)

            def setPlayerState():
                src.gamestate.gamestate.mainChar.gotExamineSchooling = True

            quest.endTrigger = setPlayerState
            questList.append(quest)
            questList.append(
                src.quests.MoveQuestMeta(
                    self.mainCharRoom,
                    3,
                    3,
                    startCinematics="Move back to Waitingposition",
                )
            )

        # explain interaction
        if not src.gamestate.gamestate.mainChar.gotInteractionSchooling:
            quest = src.quests.CollectQuestMeta(
                startCinematics="next on my Checklist is to explain the Interaction with your Environment.\n\nthe basic Interationcommands are:\n\n "
                + config.commandChars.activate
                + "=activate/apply\n "
                + config.commandChars.examine
                + "=examine\n "
                + config.commandChars.pickUp
                + "=pick up\n "
                + config.commandChars.drop
                + "=drop\n\nsee this Piles of Coal marked with ӫ on the right Side and left Side of the Room.\n\nwhenever you bump into an Item that is to big to be walked on, you will promted for giving an extra Interactioncommand. i'll give you an Example:\n\n ΩΩ＠ӫӫ\n\n pressing "
                + config.commandChars.move_west
                + " and "
                + config.commandChars.activate
                + " would result in Activation of the Furnace\n pressing "
                + config.commandChars.move_east
                + " and "
                + config.commandChars.activate
                + " would result in Activation of the Pile\n pressing "
                + config.commandChars.move_west
                + " and "
                + config.commandChars.examine
                + " would result make you examine the Furnace\n pressing "
                + config.commandChars.move_east
                + " and "
                + config.commandChars.examine
                + " would result make you examine the Pile\n\nplease grab yourself some Coal from a pile by bumping into it and pressing j afterwards."
            )
            """
            start new sub phase
            """

            def setPlayerState():
                src.gamestate.gamestate.mainChar.gotInteractionSchooling = True

            quest.endTrigger = setPlayerState
            questList.append(quest)
        else:
            # bad code: assumption of the player having failed the test is not always true
            quest = src.quests.CollectQuestMeta(
                startCinematics="Since you failed the Test last time i will quickly reiterate the interaction commands.\n\nthe basic Interationcommands are:\n\n "
                + config.commandChars.activate
                + "=activate/apply\n "
                + config.commandChars.examine
                + "=examine\n "
                + config.commandChars.pickUp
                + "=pick up\n "
                + config.commandChars.drop
                + "=drop\n\nmove over or walk into items and then press the interaction button to be able to interact with it."
            )
            questList.append(quest)

        # make the character fire the furnace
        questList.append(
            src.quests.ActivateQuestMeta(
                self.mainCharRoom.furnaces[0],
                startCinematics="now go and fire the top most Furnace.",
            )
        )
        questList.append(
            src.quests.MoveQuestMeta(
                self.mainCharRoom,
                3,
                3,
                startCinematics="please pick up the Coal on the Floor. \n\nyou won't see a whole Year of Service leaving burnable Material next to a Furnace",
            )
        )
        questList.append(
            src.quests.MoveQuestMeta(
                self.mainCharRoom,
                3,
                3,
                startCinematics="please move back to the waiting position",
            )
        )

        # chain quests
        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None
        questList[-1].endTrigger = {"container": self, "method": "end"}

        # assign first quest
        src.gamestate.gamestate.mainChar.assignQuest(questList[0], active=True)

    """
    start next phase
    """

    def end(self):
        src.cinematics.showCinematic(
            "you recieved your Preparatorytraining. Time for the Test."
        )
        phase = FurnaceCompetition()
        phase.start(seed=self.seed)


"""
do a furnace firering competition 
"""


class FurnaceCompetition(BasicPhase):
    """
    straightforward state initialization
    """

    def __init__(self, seed=0):
        super().__init__("FurnaceCompetition", seed=seed)

    """
    run the competition
    """

    def start(self, seed=0):
        self.mainCharRoom = src.gamestate.gamestate.terrain.tutorialMachineRoom

        super().start(seed=seed)

        src.cinematics.showCinematic(
            "during the Test Messages and new Task will be shown on the Buttom of the Screen. start now."
        )

        # track competition results
        self.mainCharFurnaceIndex = 0
        self.npcFurnaceIndex = 0

        """
        make the main char stop their turn
        bad code: basically the same structure within the function as around it
        """

        def endMainChar():
            # stop current quests
            # bad code: deactivating all quests is too much
            src.cinematics.showCinematic("stop.")
            for quest in src.gamestate.gamestate.mainChar.quests:
                quest.deactivate()
            src.gamestate.gamestate.mainChar.quests = []

            # clear state
            self.mainCharRoom.removeEventsByType(AnotherOne)
            src.gamestate.gamestate.mainChar.assignQuest(
                src.quests.MoveQuestMeta(
                    self.mainCharRoom,
                    3,
                    3,
                    startCinematics="please move back to the waiting position",
                )
            )

            # let the npc prepare itself
            src.gamestate.gamestate.mainChar.addMessage("your turn Ludwig")
            questList = [src.quests.FillPocketsQuest()]

            # chain quests
            lastQuest = questList[0]
            for item in questList[1:]:
                lastQuest.followUp = item
                lastQuest = item
            questList[-1].followup = None

            """
            event to make the npc fire another furnace
            """

            class AnotherOneNpc(src.events.Event):
                """
                straightforward state initialization
                """

                def __init__(subself, tick, index, creator=None):
                    super().__init__(tick, creator=creator)
                    subself.tick = tick
                    subself.furnaceIndex = index

                """
                add another furnace for the npc to fire
                """

                def handleEvent(subself):
                    self.mainCharRoom.secondOfficer.assignQuest(
                        src.quests.KeepFurnaceFiredMeta(
                            self.mainCharRoom.furnaces[subself.furnaceIndex],
                            failTrigger=self.end,
                        ),
                        active=True,
                    )
                    newIndex = subself.furnaceIndex + 1
                    self.npcFurnaceIndex = subself.furnaceIndex
                    if newIndex < 8:
                        self.mainCharRoom.secondOfficer.assignQuest(
                            src.quests.FireFurnaceMeta(
                                self.mainCharRoom.furnaces[newIndex]
                            ),
                            active=True,
                        )
                        self.mainCharRoom.addEvent(
                            AnotherOneNpc(
                                src.gamestate.gamestate.tick
                                + src.gamestate.gamestate.tick % 20
                                + 10,
                                newIndex,
                                creator=self,
                            )
                        )

            # remember event type to be able to remove it later
            self.anotherOneNpc = AnotherOneNpc

            """
            the event for waiting for a clean start and making the npc start
            """

            class WaitForClearStartNpc(src.events.Event):
                """
                straightforward state initialization
                """

                def __init__(subself, tick, index, creator=None):
                    super().__init__(tick, creator=creator)
                    subself.tick = tick

                """
                wait for a clean start and make the npc start their part of the competition
                """

                def handleEvent(subself):
                    # check whether the boilers cooled down
                    boilerStillBoiling = False
                    for boiler in self.mainCharRoom.boilers:
                        if boiler.isBoiling:
                            boilerStillBoiling = True

                    if boilerStillBoiling:
                        # wait some more
                        self.mainCharRoom.addEvent(
                            WaitForClearStartNpc(
                                src.gamestate.gamestate.tick + 2, 0, creator=self
                            )
                        )
                    else:
                        # make the npc start
                        src.cinematics.showCinematic("Liebweg start now.")
                        self.mainCharRoom.secondOfficer.assignQuest(
                            src.quests.FireFurnaceMeta(self.mainCharRoom.furnaces[0]),
                            active=True,
                        )
                        self.mainCharRoom.addEvent(
                            AnotherOneNpc(
                                src.gamestate.gamestate.tick + 10, 0, creator=self
                            )
                        )

            """
            kickstart the npcs part of the competition
            """

            def startCompetitionNpc():
                self.mainCharRoom.addEvent(
                    WaitForClearStartNpc(
                        src.gamestate.gamestate.tick + 2, 0, creator=self
                    )
                )

            questList[-1].endTrigger = startCompetitionNpc
            self.mainCharRoom.secondOfficer.assignQuest(questList[0], active=True)

        """
        event to make the player fire another furnace
        """

        class AnotherOne(src.events.Event):
            """
            straightforward state initialization
            """

            def __init__(subself, tick, index, creator=None):
                super().__init__(tick, creator=creator)
                subself.tick = tick
                subself.furnaceIndex = index

            """
            add another furnace for the player to fire
            """

            def handleEvent(subself):
                src.gamestate.gamestate.mainChar.assignQuest(
                    src.quests.KeepFurnaceFiredMeta(
                        self.mainCharRoom.furnaces[subself.furnaceIndex],
                        failTrigger=endMainChar,
                    )
                )
                newIndex = subself.furnaceIndex + 1
                self.mainCharFurnaceIndex = subself.furnaceIndex
                if newIndex < 8:
                    src.gamestate.gamestate.mainChar.assignQuest(
                        src.quests.FireFurnaceMeta(self.mainCharRoom.furnaces[newIndex])
                    )
                    self.mainCharRoom.addEvent(
                        AnotherOne(
                            src.gamestate.gamestate.tick
                            + src.gamestate.gamestate.tick % 20
                            + 5,
                            newIndex,
                        )
                    )

        """
        the event for waiting for a clean start and making the player start
        """

        class WaitForClearStart(src.events.Event):
            """
            straightforward state initialization
            """

            def __init__(subself, tick, index, creator=None):
                super().__init__(tick, creator=creator)
                subself.tick = tick

            """
            wait for a clean start and make the player start their part of the competition
            """

            def handleEvent(subself):

                # check whether the boilers cooled down
                boilerStillBoiling = False
                for boiler in self.mainCharRoom.boilers:
                    if boiler.isBoiling:
                        boilerStillBoiling = True

                # wait some more
                if boilerStillBoiling:
                    self.mainCharRoom.addEvent(
                        WaitForClearStart(src.gamestate.gamestate.tick + 2, 0)
                    )

                # make the player start
                else:
                    src.cinematics.showCinematic("start now.")
                    src.gamestate.gamestate.mainChar.assignQuest(
                        src.quests.FireFurnaceMeta(self.mainCharRoom.furnaces[0])
                    )
                    self.mainCharRoom.addEvent(
                        AnotherOne(src.gamestate.gamestate.tick + 10, 0)
                    )

        """
        kickstart the players part of the competition
        """

        def startCompetitionPlayer():
            src.cinematics.showCinematic("wait for the furnaces to burn out.")
            self.mainCharRoom.addEvent(
                WaitForClearStart(src.gamestate.gamestate.tick + 2, 0)
            )

        startCompetitionPlayer()

    """
    evaluate results and branch phases
    """

    def end(self):
        # show score
        src.gamestate.gamestate.mainChar.addMessage(
            "your Score: " + str(self.mainCharFurnaceIndex)
        )
        src.gamestate.gamestate.mainChar.addMessage(
            "Liebweg Score: " + str(self.npcFurnaceIndex)
        )

        # disable npcs quest
        for quest in self.mainCharRoom.secondOfficer.quests:
            quest.deactivate()
        self.mainCharRoom.secondOfficer.quests = []
        self.mainCharRoom.removeEventsByType(self.anotherOneNpc)
        src.gamestate.gamestate.mainChar.assignQuest(
            src.quests.MoveQuestMeta(
                self.mainCharRoom,
                3,
                3,
                startCinematics="please move back to the waiting position",
            )
        )

        # start appropriate phase
        if self.npcFurnaceIndex >= self.mainCharFurnaceIndex:
            src.cinematics.showCinematic(
                "considering your Score until now moving you directly to your proper assignment is the most efficent Way for you to proceed."
            )
            nextPhase = VatPhase()
        elif self.mainCharFurnaceIndex == 7:
            src.cinematics.showCinematic(
                "you passed the Test. in fact you passed the Test with a perfect Score. you will be valuable"
            )
            nextPhase = LabPhase()
        else:
            src.cinematics.showCinematic(
                "you passed the Test. \n\nyour Score: "
                + str(self.mainCharFurnaceIndex)
                + "\nLiebwegs Score: "
                + str(self.npcFurnaceIndex)
            )
            nextPhase = MachineRoomPhase()
        nextPhase.start(self.seed)

# obsolete: all of this stuff is still obsolete, sry

################################################################################
#
#    these are the room phases. The room phases are the midgame content of the to be prototype
#
#    ideally these phases should server to teach the player about how the game, a mech and the hierarchy progression works.
#    There should be some events and cutscenes thrown in to not have a sudden drop of cutscene frequency between tutorial and the actual game
#
################################################################################

"""
do opportunity work as hopper until a permanent position was found
"""


class FindWork(BasicPhase):
    """
    basic state initialization
    """

    def __init__(self, seed=0):
        self.cycleQuestIndex = 0
        super().__init__("FindWork", seed=seed)
        self.attributesToStore.extend(["cycleQuestIndex"])
        loadingRegistry.register(self)
        self.initialState = self.getState()
        self.mainCharRoom = src.gamestate.gamestate.terrain.waitingRoom

    """
    create selection and place triggers
    """

    def start(self, seed=0):
        self.mainCharRoom = src.gamestate.gamestate.terrain.waitingRoom

        super().start(seed=seed)

        # create selection
        options = [("yes", "Yes"), ("no", "No")]
        text = "you look like a fresh one. Were you sent to report for duty?"
        cinematic = src.cinematics.SelectionCinematic(text, options)
        cinematic.followUps = {
            "yes": {"container": self, "method": "getIntroInstant"},
            "no": {"container": self, "method": "tmpFail"},
        }
        self.cinematic = cinematic
        src.cinematics.cinematicQueue.append(cinematic)

    """
    show fluff and show intro
    """

    def getIntroInstant(self):
        showText("great, I needed to replace a hopper that was eaten by mice")
        self.acknowledgeTransfer()

    """
    show intro and trigger teardown
    """

    def acknowledgeTransfer(self):
        showText(
            "I hereby confirm the transfer and welcome you as crew on the Falkenbaum.\n\nYou will serve as an hopper under my command nominally. This means you will make yourself useful and prove your worth.\n\nI often have tasks to relay, but try not to stay idle even when i do not have tasks for you. Just ask around and see if somebody needs help"
        )
        options = [
            ("yes", "yes"),
            ("no", "no"),
        ]
        cinematic = src.cinematics.SelectionCinematic(
            "Do you understand these instructions?", options
        )
        cinematic.followUps = {
            "yes": {"container": self, "method": "skipInto"},
            "no": {"container": self, "method": "getIntro"},
        }
        src.cinematics.cinematicQueue.append(cinematic)

    def skipInto(self):
        showText(
            "Remeber to report back, your worth will be counted in a mtick.",
            trigger={"container": self, "method": "end"},
        )

    def getIntro(self):
        showText(
            "Admiting fault is no fault in itself. Here is a quick rundown of you duties:\n\n\n*) talk to my subordinate "
            + src.gamestate.gamestate.terrain.waitingRoom.secondOfficer.name
            + " and ask if you can do something. Usually you will be tasked with carrying things from one place to another.\n\n*) carry out the task given to you. The task are mundane, but you need to proof yourself before you can be trusted with more valuable tasks.\n\n*) report back to my subordinate "
            + src.gamestate.gamestate.terrain.waitingRoom.secondOfficer.name
            + " and collect your reward. Your reward consists of reputation.\n\n*) repeat until you will be called to proof your worth. If you proven yourself worthwhile you may continue or recieve special tasks. If you loose all your reputation you will be disposed of"
        )
        mainChar.awardReputation(amount=1, reason="admitting fault")
        showText(
            "You are invited to ask me for more information, if you need more instructions. I usually coordinate the hoppers from here.\n\nRemeber to report back, your worth will be counted in a mtick.",
            trigger={"container": self, "method": "end"},
        )
        self.firstOfficersDialog = [
            {
                "type": "text",
                "text": "My duty is ensure this mech is running smoothly. Task that are not done in the specialised facilities are relayed to me and my hoppers complete these tasks.",
                "name": "what are your duties?",
            },
            {
                "type": "text",
                "text": "This is nothing you need to know",
                "name": "what is an artisan?",
                "delete": True,
            },
            {
                "type": "text",
                "text": "Work hard and you will get other tasks.\n\nCome back and ask me for a job when you have more than 10 reputation",
                "name": "I want to do more than carrying furniture around",
            },
            {
                "type": "sub",
                "text": "what do want to know about",
                "sub": [
                    {
                        "type": "text",
                        "text": "You loose reputation over time, this is because dooing your part is expected and you have to exceed the expectations to gain repuation",
                        "name": "why is my reputation falling sometimes?",
                    },
                    {
                        "type": "text",
                        "text": "If you fail, your task may not be completed. This mech depends on us dooing our part. Nobody knows what may happen, if you fail to do your part\n\nIf you fail to meet the expectations, will loose reputation. The more important the task is the more reputation you will loose. Failure does happen, but repeated failure will earn you vat duty fast",
                        "name": "what does happen, if i do not complete a task in time?",
                    },
                    {
                        "type": "text",
                        "text": "This is not their failure, but yours",
                        "name": "The other hopper leaving no jobs for me to do",
                    },
                    {
                        "type": "text",
                        "text": "The Falkenbaum is a training mech after all. Completing tasks for training does not gain you reputation, so it is preferable to complete actual work",
                        "name": "Why transport furniture back and forth?",
                        "delete": True,
                    },
                ],
                "name": "Please explain how the hopper job works in detail.",
            },
            {
                "type": "text",
                "text": "I will assign simple training tasks to you. You will recieve a token each time you complete a training task.\n\nCollect 4 tokens by completing 4 tasks\n\nTalk to me when you are ready to start a trainings task",
                "name": "Please train me",
                "delete": True,
                "trigger": {
                    "container": self,
                    "method": "getSimpleReputationGathering",
                },
            },
        ]
        src.gamestate.gamestate.terrain.waitingRoom.firstOfficer.basicChatOptions.append(
            {
                "dialogName": "I need more information about the hopper duty",
                "chat": src.chats.ConfigurableChat,
                "params": {
                    "text": "what do you need to know more about?",
                    "info": self.firstOfficersDialog,
                },
            }
        )

    def getSimpleReputationGathering(self):
        self.firstOfficersDialog.append(
            {
                "type": "text",
                "text": "please move the wall section in the west of the room and return to me\n\nYou will be rewarded one token for completing the task\n\nThe implant will show you the path to the wall section and where to place it\n\ntalk to me again after completing your task to get another task",
                "name": "give me the task to train me",
                "delete": True,
                "trigger": {"container": self, "method": "doSimpleReputationGathering"},
            }
        )

    def doSimpleReputationGathering(self):
        item = src.gamestate.gamestate.terrain.waitingRoom.trainingItems[0]
        newPosition = (src.gamestate.gamestate.terrain.waitingRoom, 1, 8)
        if item.xPosition == 1 and item.yPosition == 8:
            newPosition = (src.gamestate.gamestate.terrain.waitingRoom, 1, 1)
        quest = src.quests.TransportQuest(item, newPosition, creator=self)
        quest.endTrigger = {
            "container": self,
            "method": "completeSimpeReputationGathering",
        }
        src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)

    def completeSimpeReputationGathering(self):
        src.gamestate.gamestate.mainChar.inventory.append(
            src.items.itemMap["Token"](creator=self)
        )
        src.gamestate.gamestate.mainChar.addMessage(
            "you recieved 1 token for completing a trainings task"
        )
        numTokens = 0
        for item in src.gamestate.gamestate.mainChar.inventory:
            if item.type == "Token":
                numTokens += 1

        if numTokens < 4:
            quest = src.quests.MoveQuestMeta(
                src.gamestate.gamestate.terrain.waitingRoom, 6, 4, creator=self
            )
            quest.endTrigger = {
                "container": self,
                "method": "getSimpleReputationGathering",
            }
            src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)
            return

        skippedTokens = 0
        removedTokens = 0
        for item in src.gamestate.gamestate.mainChar.inventory[:]:
            if item.type == "Token":
                if skippedTokens < 2:
                    continue
                    skippedTokens += 1
                removedTokens += 1
                src.gamestate.gamestate.mainChar.inventory.remove(item)
        src.gamestate.gamestate.mainChar.addMessage(
            "%i tokens were removed from you since you compled the first training"
        )
        src.gamestate.gamestate.mainChar.revokeReputation(
            fraction=3, reason="needing to be trained"
        )
        src.gamestate.gamestate.mainChar.awardReputation(
            amount=2, reason="completing the first training"
        )

        self.firstOfficersDialog.append(
            {
                "type": "text",
                "text": "I will assign simple training tasks to you, like i did in the training.\n\nThis time you have can choose between 2 tasks and i will take a token from you each time you ask for a task.\n\nComplete enough tasks to gather 6 tokens",
                "name": "Please train me further",
                "delete": True,
                "trigger": {
                    "container": self,
                    "method": "setupSelectiveReputationGathering",
                },
            }
        )

    def setupSelectiveReputationGathering(self):
        self.getSelectiveReputationGatheringUsefull()
        self.getSelectiveReputationGatheringUseless()

    def getSelectiveReputationGatheringUsefull(self):
        self.firstOfficersDialog.append(
            {
                "type": "text",
                "text": "please move the wall section in the west of the room to the south-west of the room.\n\nYou will be rewarded with 1 token for completing the task",
                "name": "give me the task to move the wall",
                "delete": True,
                "trigger": {
                    "container": self,
                    "method": "doSelectiveReputationGatheringUsefull",
                },
            }
        )

    def getSelectiveReputationGatheringUseless(self):
        self.firstOfficersDialog.append(
            {
                "type": "text",
                "text": "please move the pipe section in the east of the room to the south-east of the room.\n\nYou will not be rewarded for completing the task",
                "name": "give me the task to move the pipe",
                "delete": True,
                "trigger": {
                    "container": self,
                    "method": "doSelectiveReputationGatheringUseless",
                },
            }
        )

    def doSelectiveReputationGatheringUsefull(self):
        item = src.gamestate.gamestate.terrain.waitingRoom.trainingItems[1]
        newPosition = (src.gamestate.gamestate.terrain.waitingRoom, 7, 8)
        if item.xPosition == 7 and item.yPosition == 8:
            newPosition = (src.gamestate.gamestate.terrain.waitingRoom, 8, 1)
        quest = src.quests.TransportQuest(item, newPosition, creator=self)
        quest.endTrigger = {
            "container": self,
            "method": "completeSelectiveReputationGatheringUsefull",
        }
        src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)

    def doSelectiveReputationGatheringUseless(self):
        item = src.gamestate.gamestate.terrain.waitingRoom.trainingItems[0]
        newPosition = (src.gamestate.gamestate.terrain.waitingRoom, 1, 8)
        if item.xPosition == 1 and item.yPosition == 8:
            newPosition = (src.gamestate.gamestate.terrain.waitingRoom, 1, 1)
        quest = src.quests.TransportQuest(item, newPosition, creator=self)
        quest.endTrigger = {
            "container": self,
            "method": "completeSelectiveReputationGatheringUseless",
        }
        src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)

    def completeSelectiveReputationGatheringUseless(self):
        src.gamestate.gamestate.mainChar.addMessage(
            "you recieved no tokens for completing a task"
        )
        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.waitingRoom, 6, 4, creator=self
        )
        quest.endTrigger = {
            "container": self,
            "method": "getSelectiveReputationGatheringUseless",
        }
        src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)

    def completeSelectiveReputationGatheringUsefull(self):
        src.gamestate.gamestate.mainChar.inventory.append(
            src.items.itemMap["Token"](creator=self)
        )
        src.gamestate.gamestate.mainChar.addMessage(
            "you recieved 1 token for completing a task"
        )
        numTokens = 0
        for item in src.gamestate.gamestate.mainChar.inventory:
            if item.type == "Token":
                numTokens += 1

        if numTokens < 6:
            quest = src.quests.MoveQuestMeta(
                src.gamestate.gamestate.terrain.waitingRoom, 6, 4, creator=self
            )
            quest.endTrigger = {
                "container": self,
                "method": "getSelectiveReputationGatheringUsefull",
            }
            src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)
            return

        for item in src.gamestate.gamestate.mainChar.inventory[:]:
            if item.type == "Token":
                src.gamestate.gamestate.mainChar.inventory.remove(item)
        src.gamestate.gamestate.mainChar.addMessage(
            "your tokens were removed from you since you compled the second training"
        )

        src.gamestate.gamestate.mainChar.revokeReputation(
            fraction=3, reason="needing to be trained"
        )
        src.gamestate.gamestate.mainChar.rewardReputation(
            amount=2, reason="completing the first training"
        )

        self.firstOfficersDialog.append(
            {
                "type": "text",
                "text": "I offer to teach you some things. I won't repeat lessons. I can teach you:\n\n* how to gather scrap more effective\n* how to complete your work easier\n* how to be more usefull",
                "follow": [
                    {
                        "type": "text",
                        "text": "Usually you have to pick up more than one piece of scrap. Your task is to collect all these pieces of scrap so do not walk back and forth for each item, but take more than one piece of scrap each time.",
                        "name": "teach me how to gather scrap more effective",
                        "delete": True,
                    },
                    {
                        "type": "text",
                        "text": "You can use your implant to take control and complete your task by pressing + or *.\nThe implants solutions for your tasks are often below expectation so do not let the implant take control completely and think when needed",
                        "name": "teach me how to complete my work easier",
                        "delete": True,
                    },
                    {
                        "type": "text",
                        "text": "Do not do the task ment only to keep you busy. Select the tasks that are valued most and you will be the most useful",
                        "name": "teach me how to be more useful",
                        "delete": True,
                    },
                ],
                "name": "Please teach me more",
                "delete": True,
            }
        )

    """
    drop the player out of the command chain and place trigger for return
    """

    def tmpFail(self):
        # show fluff
        say("go on then.")
        showText("go on then.")

        # add option to reenter the command chain
        src.gamestate.gamestate.terrain.waitingRoom.firstOfficer.basicChatOptions.append(
            {
                "dialogName": "I want to report for duty",
                "chat": src.chats.ReReport,
                "params": {"phase": self},
            }
        )

    """
    make the player do some tasks until allowing advancement elsewhere
    bad code: very chaotic. probably needs to be split up and partially rewritten
    bad pattern: mostly player only code
    """

    def end(self):
        src.gamestate.gamestate.terrain.waitingRoom.addAsHopper(
            src.gamestate.gamestate.mainChar
        )

        self.didStoreCargo = False

        """
        check reputation and punish/reward player
        """

        class ProofOfWorth(src.events.Event):
            """
            basic state initialization
            """

            def __init__(subself, tick, char, toCancel=[], creator=None):
                super().__init__(tick, creator=creator)
                subself.tick = tick
                subself.char = char
                subself.toCancel = toCancel

            """
            call player to the waiting room and give a short speech
            """

            def handleEvent(subself):
                # cancel current quests
                # bad code: canceling destroys the ongoing process, pausing might be better
                for quest in subself.toCancel:
                    quest.deactivate()
                    src.gamestate.gamestate.mainChar.quests.remove(quest)

                # call the player for the speech
                quest = src.quests.MoveQuestMeta(self.mainCharRoom, 6, 5, lifetime=300)
                quest.endTrigger = {"container": subself, "method": "meeting"}
                """
                kill player failing to apear for performance evaluation
                """

                def fail():
                    src.gamestate.gamestate.mainChar.addMessage(
                        "*alarm* non rensponsive personal detected. possible artisan. dispatch kill squads *alarm*"
                    )

                    # send out death squads
                    for room in src.gamestate.gamestate.terrain.militaryRooms:
                        quest = src.quests.MurderQuest(src.gamestate.gamestate.mainChar)
                        src.gamestate.gamestate.mainChar.revokeReputation(
                            amount=1000, reason="failing to show up for evaluation"
                        )
                        room.secondOfficer.assignQuest(quest, active=True)
                        room.onMission = True

                quest.fail = fail
                src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)

            """
            fake a meeting with the player superordinate
            """

            def meeting(subself):
                # do a normal meeting
                if (
                    src.gamestate.gamestate.mainChar.reputation < 15
                    or self.didStoreCargo
                ):
                    # check if player has the lowest reputation
                    lowestReputation = True
                    for hopper in src.gamestate.gamestate.terrain.waitingRoom.hoppers:
                        if (
                            hopper.reputation
                            < src.gamestate.gamestate.mainChar.reputation
                        ):
                            lowestReputation = False

                    showText("Time to prove your worth.")
                    if src.gamestate.gamestate.mainChar.reputation <= 0:
                        # punish player for low performance near to killing player
                        showText(
                            "You currently have no recieps on you. Please report to vat duty.",
                            trigger={"container": subself, "method": "startVatPhase"},
                        )
                    elif (
                        lowestReputation
                        and len(src.gamestate.gamestate.terrain.waitingRoom.hoppers) > 3
                    ):
                        showText(
                            "I have too many hoppers working here and you do the least work. Please report to vat duty.",
                            trigger={"container": subself, "method": "startVatPhase"},
                        )
                    elif src.gamestate.gamestate.mainChar.reputation > 5:
                        # do nothing on ok performance
                        showText(
                            "great work. Keep on and maybe you will be one of us officers"
                        )
                    else:
                        # applaud the player on good performance
                        showText("I see you did some work. Carry on")

                    # decrease reputation so the player will be forced to work continuously or to save up reputation
                    src.gamestate.gamestate.mainChar.revokeReputation(
                        amount=3
                        + (2 * len(src.gamestate.gamestate.mainChar.subordinates)),
                        reason="failing to show up for evaluation",
                    )
                    self.mainCharRoom.addEvent(
                        ProofOfWorth(
                            src.gamestate.gamestate.tick + (15 * 15 * 15), subself.char
                        )
                    )

                # assign a special quest
                else:
                    src.gamestate.gamestate.mainChar.awardReputation(
                        amount=5, reason="getting a special order"
                    )
                    # add the quest
                    showText(
                        "logistics command orders us to move some of the cargo in the long term store to accesible storage.\n3 rooms are to be cleared. One room needs to be cleared within 150 ticks\nThis requires the coordinated effort of the hoppers here. Since "
                        + subself.char.name
                        + " did well to far, "
                        + subself.char.name
                        + " will be given the lead.\nThis will be extra to the current workload"
                    )
                    quest = src.quests.HandleDelivery(
                        [src.gamestate.gamestate.terrain.tutorialCargoRooms[4]],
                        [
                            src.gamestate.gamestate.terrain.tutorialStorageRooms[1],
                            src.gamestate.gamestate.terrain.tutorialStorageRooms[3],
                            src.gamestate.gamestate.terrain.tutorialStorageRooms[5],
                        ],
                    )
                    quest.endTrigger = {
                        "container": self,
                        "method": "subordinateHandover",
                    }
                    src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)

                    # add subordinates
                    for hopper in src.gamestate.gamestate.terrain.waitingRoom.hoppers:
                        # ignore bad candidates
                        if hopper == subself.char:
                            continue
                        if hopper in src.gamestate.gamestate.mainChar.subordinates:
                            continue
                        if hopper.dead:
                            continue

                        # add subordinate
                        src.gamestate.gamestate.mainChar.subordinates.append(hopper)

            """
            trigger failure phase
            """

            def startVatPhase(subself):
                phase = VatPhase()
                phase.start(self.seed)

        """
        return subordinates to waiting room
        """

        def subordinateHandover(self):
            for hopper in src.gamestate.gamestate.terrain.waitingRoom.hoppers:
                if hopper in src.gamestate.gamestate.mainChar.subordinates:
                    if hopper.dead:
                        # punish player if subordinate is returned dead
                        src.gamestate.gamestate.mainChar.addMessage(
                            hopper.name + " died. that is unfortunate"
                        )
                        src.gamestate.gamestate.mainChar.revokeReputation(
                            amount=100, reason="not returning a subordinate"
                        )
                    src.gamestate.gamestate.mainChar.subordinates.remove(hopper)
            self.addRoomConstruction()

        """
        helper function to make the main char build a room
        """

        def addRoomConstruction(self):
            for room in src.gamestate.gamestate.terrain.rooms:
                if isinstance(room, rooms.ConstructionSite):
                    constructionSite = room
                    break
            quest = src.quests.ConstructRoom(
                constructionSite, src.gamestate.gamestate.terrain.tutorialStorageRooms
            )
            src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)

        # add events to keep loose control
        self.mainCharRoom.addEvent(
            ProofOfWorth(
                src.gamestate.gamestate.tick + (15 * 15 * 15),
                src.gamestate.gamestate.mainChar,
            )
        )

        # add quest to pool
        quest = src.quests.ClearRubble()
        quest.reputationReward = 3
        src.gamestate.gamestate.terrain.waitingRoom.quests.append(quest)

        self.cycleQuestIndex = 0

        # start series of quests that were looped to keep the system active
        self.addNewCircleQuest()

        # add the dialog for getting a job
        src.gamestate.gamestate.terrain.waitingRoom.firstOfficer.basicChatOptions.append(
            {
                "dialogName": "Can you use some help?",
                "chat": src.chats.JobChatFirst,
                "params": {
                    "mainChar": src.gamestate.gamestate.mainChar,
                    "terrain": src.gamestate.gamestate.terrain,
                    "hopperDutyQuest": src.gamestate.gamestate.mainChar.quests[0],
                },
            }
        )
        src.gamestate.gamestate.terrain.waitingRoom.secondOfficer.basicChatOptions.append(
            {
                "dialogName": "Can you use some help?",
                "chat": src.chats.JobChatSecond,
                "params": {
                    "mainChar": src.gamestate.gamestate.mainChar,
                    "terrain": src.gamestate.gamestate.terrain,
                    "hopperDutyQuest": src.gamestate.gamestate.mainChar.quests[0],
                },
            }
        )
        src.gamestate.gamestate.terrain.wakeUpRoom.firstOfficer.basicChatOptions.append(
            {
                "dialogName": "Can you use some help?",
                "chat": src.chats.JobChatFirst,
                "params": {
                    "mainChar": src.gamestate.gamestate.mainChar,
                    "terrain": src.gamestate.gamestate.terrain,
                    "hopperDutyQuest": src.gamestate.gamestate.mainChar.quests[0],
                },
            }
        )
        src.gamestate.gamestate.terrain.tutorialMachineRoom.firstOfficer.basicChatOptions.append(
            {
                "dialogName": "Can you use some help?",
                "chat": src.chats.JobChatFirst,
                "params": {
                    "mainChar": src.gamestate.gamestate.mainChar,
                    "terrain": src.gamestate.gamestate.terrain,
                    "hopperDutyQuest": src.gamestate.gamestate.mainChar.quests[0],
                },
            }
        )

    """
    quest to carry stuff and trigger adding a new quest afterwards
    """

    def addNewCircleQuest(self):

        # set up the list of items to transport
        labCoordinateList = [(2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
        shopCoordinateList = [(9, 2), (9, 7), (9, 3), (9, 6), (9, 4), (9, 5)]

        # reset counter when at the end
        if (
            self.cycleQuestIndex
            > 2 * len(src.gamestate.gamestate.terrain.metalWorkshop.producedItems) - 2
        ):
            self.cycleQuestIndex = 0

        # move items to the lab
        if self.cycleQuestIndex < len(
            src.gamestate.gamestate.terrain.metalWorkshop.producedItems
        ):
            pos = labCoordinateList[self.cycleQuestIndex]
            room = src.gamestate.gamestate.terrain.tutorialLab
            index = self.cycleQuestIndex

        # move items to the metal workshop
        else:
            pos = shopCoordinateList[
                self.cycleQuestIndex
                - len(src.gamestate.gamestate.terrain.metalWorkshop.producedItems)
            ]
            room = src.gamestate.gamestate.terrain.metalWorkshop
            index = (
                -(
                    self.cycleQuestIndex
                    - len(src.gamestate.gamestate.terrain.metalWorkshop.producedItems)
                )
                - 1
            )

        # add the quest to queue
        quest = src.quests.TransportQuest(
            src.gamestate.gamestate.terrain.metalWorkshop.producedItems[index],
            (room, pos[0], pos[1]),
        )
        quest.endTrigger = {"container": self, "method": "addNewCircleQuest"}
        quest.reputationReward = 0
        src.gamestate.gamestate.terrain.waitingRoom.quests.append(quest)

        # increase the quest counter
        self.cycleQuestIndex += 1


"""
dummmy for the lab phase
should serve as puzzle/testing area
"""


class LabPhase(BasicPhase):
    """
    straightforward state initialization
    """

    def __init__(self, seed=0):
        super().__init__("LabPhase", seed=seed)

    """
    make a dummy movement and switch phase
    """

    def start(self, seed=0):
        self.mainCharRoom = src.gamestate.gamestate.terrain.tutorialLab

        super().start(seed=seed)

        # do a dummy action
        questList = []
        questList.append(
            src.quests.MoveQuestMeta(
                self.mainCharRoom,
                3,
                3,
                startCinematics="please move to the waiting position",
            )
        )

        # chain quests
        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None
        questList[-1].endTrigger = {"container": self, "method": "end"}

        # assign player quest
        src.gamestate.gamestate.mainChar.assignQuest(questList[0])

    """
    move on to next phase
    """

    def end(self):
        src.cinematics.showCinematic("we are done with the tests. return to work")
        BoilerRoomInteractionTraining().start(self.seed)


"""
dummy for the vat phase
should serve as punishment for player with option to escape
bad pattern: has no known way of escaping
"""


class VatPhase(BasicPhase):
    """
    straightforward state initialization
    """

    def __init__(self, seed=0):
        super().__init__("VatPhase", seed=seed)

    """
    do a dummy action and switch phase
    """

    def start(self, seed=0):
        self.mainCharRoom = src.gamestate.gamestate.terrain.tutorialVat

        super().start(seed=seed)

        # remove all player quests
        for quest in src.gamestate.gamestate.mainChar.quests:
            quest.deactivate()
        src.gamestate.gamestate.mainChar.quests = []

        quest = src.quests.MoveQuestMeta(
            src.gamestate.gamestate.terrain.tutorialVat, 3, 3, lifetime=500
        )

        """
        kill characters not moving into the vat
        """

        def fail():
            src.gamestate.gamestate.mainChar.addMessage(
                "*alarm* refusal to honour vat assignemnt detected. likely artisan. Dispatch kill squads *alarm*"
            )
            for room in src.gamestate.gamestate.terrain.militaryRooms:
                quest = src.quests.MurderQuest(src.gamestate.gamestate.mainChar)
                src.gamestate.gamestate.mainChar.revokeReputation(
                    amount=1000, reason="not starting vat duty"
                )
                room.secondOfficer.assignQuest(quest, active=True)
                room.onMission = True

        quest.fail = fail
        quest.endTrigger = {"container": self, "method": "revokeFloorPermit"}

        # assign player quest
        src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)

    """
    take away floor permit to make escape harder
    """

    def revokeFloorPermit(self):
        src.gamestate.gamestate.mainChar.hasFloorPermit = False

    """
    move on to next phase
    """

    def end(self):
        src.cinematics.showCinematic(
            "you seem to be able to follow orders after all. you may go back to your training."
        )
        BoilerRoomInteractionTraining().start(seed=self.seed)


"""
dummy for the machine room phase
should serve to train maintanance
"""


class MachineRoomPhase(BasicPhase):
    """
    straightforward state initialization
    """

    def __init__(self, seed=0):
        super().__init__("MachineRoomPhase", seed=seed)

    """
    switch completely to free play
    """

    def start(self, seed=0):
        self.mainCharRoom = src.gamestate.gamestate.terrain.tutorialMachineRoom
        self.requiresMainCharRoomSecondOfficer = False

        super().start(seed=seed)

        src.gamestate.gamestate.terrain.tutorialMachineRoom.secondOfficer = (
            src.gamestate.gamestate.mainChar
        )

        # assign task and hand over
        src.gamestate.gamestate.terrain.tutorialMachineRoom.endTraining()

        # do a dummy action
        questList = []
        questList.append(
            src.quests.MoveQuestMeta(
                src.gamestate.gamestate.terrain.tutorialMachineRoom,
                3,
                3,
                startCinematics="time to do some actual work. report to "
                + src.gamestate.gamestate.terrain.tutorialMachineRoom.firstOfficer.name,
            )
        )

        # chain quests
        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None

        # assign player quest
        src.gamestate.gamestate.mainChar.assignQuest(questList[0])


    """
    win the game
    """

    def end(self):
        src.gamestate.gamestate.gameWon = True


"""
the phase is intended to give the player access to the true gameworld without manipulations

this phase should be left as blank as possible
"""


class Tutorial(BasicPhase):
    def __init__(self, seed=0):
        super().__init__("Tutorial", seed=seed)

    """
    place main char
    bad code: superclass call should not be prevented
    """

    def start(self, seed=0):
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

    def start(self, seed=0):
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

    def start(self, seed=0):
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

    phasesByName["VatPhase"] = VatPhase
    phasesByName["MachineRoomPhase"] = MachineRoomPhase
    phasesByName["LabPhase"] = LabPhase
    phasesByName["BoilerRoomWelcome"] = BoilerRoomWelcome
    phasesByName["BoilerRoomInteractionTraining"] = BoilerRoomInteractionTraining
    phasesByName["FurnaceCompetition"] = FurnaceCompetition
    phasesByName["WakeUpPhase"] = WakeUpPhase
    phasesByName["BrainTesting"] = BrainTestingPhase
    phasesByName["BasicMovementTraining"] = BasicMovementTraining
    phasesByName["FindWork"] = FindWork
    phasesByName["Challenge"] = Challenge
    phasesByName["Test"] = Testing_1
    phasesByName["Testing_1"] = Testing_1
    phasesByName["Siege"] = Siege
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
