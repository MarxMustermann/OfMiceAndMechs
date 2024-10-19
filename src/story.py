"""
story code and story related code belongs here
most thing should be abstracted and converted to a game mechanism later

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
most of this code is currently not in use and needs to be reintegrated
"""

import copy
import json
import logging
import random

import requests

import src.canvas
import src.chats
import src.cinematics
import src.events
import src.gamestate
import src.interaction
import src.quests
import src.rooms

logger = logging.getLogger(__name__)
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

#########################################################################
#
#     building block phases
#
#########################################################################

class BasicPhase:
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
        super().__init__()
        self.name = name
        self.seed = seed

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


    def callIndirect(self, callback, extraParams=None):
        """
        call a callback that is stored in a savable format

        Parameters:
            callback: the callback to call
            extraParams: some additional parameters
        """

        if extraParams is None:
            extraParams = {}
        if not isinstance(callback, dict):
            # bad code: direct function calls are deprecated, but not completely removed
            callback()
        else:
            if "container" not in callback:
                return
            container = callback["container"]
            function = getattr(container, callback["method"])

            if "params" in callback:
                callback["params"].update(extraParams)
                function(callback["params"])
            else:
                function()

class PrefabDesign(BasicPhase):

    def __init__(self, seed=0):
        super().__init__("PrefabDesign", seed=seed)

        self.stats = {}
        self.floorPlan = None

    def advance(self):
        self.askAction()

    def runFloorplanGeneration(self):
        self.floorPlan = self.generateFloorPlan()
        self.saveFloorPlan(self.floorPlan)
        self.spawnRooms(self.floorPlan)

    def addFloorPlan(self):
        if not self.floorPlan:
            return

        converted = self.convertFloorPlanToDict(self.floorPlan)

        try:
            # register the save
            with open("gamestate/globalInfo.json") as globalInfoFile:
                rawState = json.loads(globalInfoFile.read())
        except:
            rawState = {"saves": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],"customPrefabs":[]}

        rawState["customPrefabs"].append(converted)

        with open("gamestate/globalInfo.json", "w") as globalInfoFile:
            json.dump(rawState,globalInfoFile)

        submenu = src.menuFolder.TextMenu.TextMenu("""
the floorplan is available in basebuilder mode and main game now""")

    def askAction(self):
        options = [("generateFloorPlan", "generate floor plan"), ("simulateUsage", "simulate usage"), ("submitFloorPlan", "submit floor plan"), ("addFloorPlan", "add floor plan to loadable prefabs"),("donateFloorPlan", "donate floor plan")]
        submenu = src.menuFolder.SelectionMenu.SelectionMenu(
            "what do you want to do?", options,
        )
        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu
        src.gamestate.gamestate.mainChar.macroState["submenue"].followUp = {
            "container": self,
            "method": "runAction",
            "params": {}
        }

    def runAction(self,extraParams):
        if "selection" not in extraParams:
            return

        if extraParams["selection"] == "generateFloorPlan":
            self.runFloorplanGeneration()
        if extraParams["selection"] == "simulateUsage":
            self.simulateUsage()
        if extraParams["selection"] == "addFloorPlan":
            self.addFloorPlan()
        if extraParams["selection"] == "donateFloorPlan":
            self.donateFloorPlan()

    def donateFloorPlan(self):
        options = [("yes", "Yes"), ("no", "No")]
        submenu = src.menuFolder.SelectionMenu.SelectionMenu(
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
        for x in range(13):
            for y in (0,12):
                blockedPositions.append((x,y,0))
        for y in range(13):
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

            if pos is None:
                src.gamestate.gamestate.mainChar.addMessage("no room to place scrap compactor")
                return None

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

            if pos is None:
                src.gamestate.gamestate.mainChar.addMessage("no room to place corpse animator")
                return None

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


            if pos is None:
                src.gamestate.gamestate.mainChar.addMessage("no room to place corpse stockpile")
                return None

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


            if pos is None:
                src.gamestate.gamestate.mainChar.addMessage("no room to place scratch plate")
                return None

            scratchPlatePositions.append(pos)

            placedScratchPlate = True
            blockedPositions.append(pos)

            buildSite = (pos,"ScratchPlate",{})
            floorPlan["buildSites"].append(buildSite)
            scratchPlate = buildSite

        if "commands" not in scratchPlate[2]:
            feedingPos = (corpseStockpilePositions[0][0],corpseStockpilePositions[0][1]-1,corpseStockpilePositions[0][2])
            scratchPlatePos = (scratchPlatePositions[0][0],scratchPlatePositions[0][1],scratchPlatePositions[0][2])
            corpseAnimatorPos = (corpseAnimatorPositions[0][0]+1,corpseAnimatorPositions[0][1],corpseAnimatorPositions[0][2])

            pathToFeeder = self.toBuildRoomClone3.getPathCommandTile(scratchPlatePos,feedingPos)[0]
            pathToAnimator = self.toBuildRoomClone3.getPathCommandTile(feedingPos,corpseAnimatorPos)[0]
            pathToStart = self.toBuildRoomClone3.getPathCommandTile(corpseAnimatorPos,scratchPlatePos)[0]
            scratchPlate[2]["commands"] = {"noscratch":"jj"+pathToFeeder+"Ks"+pathToAnimator+"JaJa"+pathToStart}

        if "settings" not in scratchPlate[2]:
            scratchPlate[2]["settings"] = {"scratchThreashold":1000}

        for corpseAnimatorPos in corpseAnimatorPositions:
            commandPos = (corpseAnimatorPos[0]+1,corpseAnimatorPos[1],corpseAnimatorPos[2])
            if commandPos not in commandPositions:
                command = ""
                lastPos = commandPos
                for compactorPos in scrapCompactorPositions:
                    newPos = (compactorPos[0],compactorPos[1]-1,compactorPos[2])
                    (moveComand,path) = self.toBuildRoomClone3.getPathCommandTile(lastPos,newPos)
                    if path:
                        command += moveComand+"Js"
                        lastPos = newPos
                    else:
                        newPos = (compactorPos[0],compactorPos[1]+1,compactorPos[2])
                        (moveComand,path) = self.toBuildRoomClone3.getPathCommandTile(lastPos,newPos)
                        if path:
                            command += moveComand+"Jw"
                            lastPos = newPos
                        else:
                            src.gamestate.gamestate.mainChar.addMessage(f"could not generate path to Scrap compactor on {compactorPos}")

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
                if "walkingSpace" in floorPlan and pos in floorPlan["walkingSpace"]:
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
        self.toBuildRoomClone.spawnGhouls(src.gamestate.gamestate.mainChar)


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
        self.toBuildRoomClone4.spawnGhouls(src.gamestate.gamestate.mainChar)

        self.spawnMaintanenceNPCs(self.toBuildRoomClone4)

        self.stats["current"]["1500"] = {"produced":0}

        for _i in range(1500):
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
        self.toBuildRoomClone6.spawnGhouls(src.gamestate.gamestate.mainChar)

        self.spawnMaintanenceNPCs(self.toBuildRoomClone6)

        self.stats["current"]["15000"] = {"produced":0}

        for _i in range(15000):
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
        self.toBuildRoomClone5.spawnGhouls(src.gamestate.gamestate.mainChar)

        self.spawnMaintanenceNPCs()
        self.maintananceLoop()

        ticksPerBar = 15000/self.stats["current"]["15000"]["produced"]
        submenu = src.menuFolder.TextMenu.TextMenu(f"""
your room produces a MetalBar every {ticksPerBar} ticks on average.""")

        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

    def spawnMaintanenceNPCs(self,room=None):
        if not room:
            room = self.toBuildRoomClone5

        charCount = 0
        for character in room.characters:
            if isinstance(character,src.characters.characterMap["Ghoul"]):
                continue
            charCount += 1

        if charCount < 5:
            character = src.characters.Character(3,3)
            character.runCommandString("*********")
            room.addCharacter(character,0,6)
            for _i in range(10):
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
            for _i in range(10):
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

            quest = src.quests.questMap["FetchItems"](targetPosition=(room.xPosition,room.yPosition,0),toCollect="MetalBars")
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
        if room is None:
            room = self.toBuildRoomClone5

        for npc in room.characters[:]:
            if isinstance(npc,src.characters.characterMap["Ghoul"]):
                continue
            if len(npc.quests) > 1:
                continue
            if npc.xPosition != 0 or npc.yPosition != 6:
                continue

            if room == self.toBuildRoomClone4:
                for item in npc.inventory:
                    if item.type != "MetalBars":
                        continue
                    self.stats["current"]["1500"]["produced"] += 1
            if room == self.toBuildRoomClone6:
                for item in npc.inventory:
                    if item.type != "MetalBars":
                        continue
                    self.stats["current"]["15000"]["produced"] += 1
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
                for _i in range(1,10):
                    item = src.items.itemMap["Corpse"]()
                    storageRoom.addItem(item,(x,y,0))
                    item.bolted = False

        for x in range(1,6):
            for y in range(1,6):
                for _i in range(1,10):
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
                for _i in range(1,10):
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

class MainGame(BasicPhase):
    """
    """

    def __init__(self, seed=0,preselection=None):
        """
        set up super class

        Parameters:
            seed: rng seed
        """

        self.preselection = preselection
        super().__init__("MainGame", seed=seed)

    def get_free_position(self,tag):
        pos = random.choice(self.available_positions)
        self.available_positions.remove(pos)

        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        currentTerrain.tag = tag

        return pos

    def start(self, seed=0, difficulty=None):
        """
        set up terrain and spawn main character

        Parameters:
            seed: rng seed
        """

        self.epochLength = 15*15*15
        self.factionCounter = 1

        self.specialItemMap = {}
        self.available_positions = []
        for x in range(1,14):
            for y in range(1,14):
                self.available_positions.append((x,y))

        for pos in ((1,1),(13,1),(1,13),(13,13)):
            currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
            currentTerrain.tag = "corner terrain"
            self.available_positions.remove(pos)
            self.setUpShrine(pos)

        pos = (7,7)
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        currentTerrain.tag = "center terrain"
        self.setUpShrine(pos)

        self.difficulty = difficulty

        self.dungeonCrawlInfos = []

        # reserve center position for throne room
        self.available_positions.remove((7,7))

        self.preselection = "Story"

        difficultyModifier = 1
        if self.difficulty == "tutorial":
            difficultyModifier = 0.5
        if self.difficulty == "easy":
            difficultyModifier = 0.5
        if self.difficulty == "difficult":
            difficultyModifier = 2

        src.gamestate.gamestate.difficulty = self.difficulty

        numDungeons = 7
        if self.difficulty == "tutorial":
            numDungeons = 2

        dungeonPositions = []
        dungeon_counter = 0
        while dungeon_counter < numDungeons:
            dungeonPositions.append(self.get_free_position("dungeon"))
            dungeon_counter += 1

        if self.difficulty == "tutorial":
            self.setUpGlassHeartDungeon(dungeonPositions[0],1,1*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[1],2,1.5*difficultyModifier)
        elif self.difficulty == "difficult":
            gods = [1,2,3,4,5,6,7]
            random.shuffle(gods)
            self.setUpGlassHeartDungeon(dungeonPositions[0],gods[0],1*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[1],gods[1],1.5*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[2],gods[2],2*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[3],gods[3],2.5*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[4],gods[4],3*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[5],gods[5],3.5*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[6],gods[6],4*difficultyModifier)
        else:
            self.setUpGlassHeartDungeon(dungeonPositions[0],1,1*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[1],2,1.5*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[2],3,2*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[3],4,2.5*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[4],5,3*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[5],6,3.5*difficultyModifier)
            self.setUpGlassHeartDungeon(dungeonPositions[6],7,4*difficultyModifier)

            dungeonPositions.append(self.get_free_position("dungeon2"))

        self.sternsBasePosition = self.get_free_position("sterns base")
        self.setUpSternsBase(self.sternsBasePosition)

        for _i in range(1,20):
            self.get_free_position("nothingness")

        for _i in range(1,40):
            self.setUpShrine(self.get_free_position("shrine"))

        for _i in range(1,15):
            self.setUpFactoryRemains(self.get_free_position("factory"))

        for _i in range(1,2):
            for itemID in [1,2,3,4,5,6,7]:
                self.setUpStatueRoom(self.get_free_position("statue room"),itemID)
            
        if self.preselection == "Story":
            self.dungeonCrawlInfos.append(self.createStoryStart())
            self.activeStory = self.dungeonCrawlInfos[0]

        mainChar = self.activeStory["mainChar"]
        src.gamestate.gamestate.mainChar = mainChar
        mainChar.addListener(self.mainCharacterDeath,"died")

        self.wavecounterUI = {"type":"text","offset":(72,5), "text":"wavecounter"}
        src.gamestate.gamestate.uiElements.append(self.wavecounterUI)

        if self.difficulty == "tutorial":
            mainChar.maxHealth *= 2
            mainChar.health *= 2
        if self.difficulty == "easy":
            mainChar.maxHealth *= 2
            mainChar.health *= 2
        if self.difficulty == "difficult":
            mainChar.maxHealth = int(mainChar.maxHealth*0.5)
            mainChar.health = int(mainChar.health*0.5)

        if not self.difficulty == "tutorial":
            questMenu = src.menuFolder.QuestMenu.QuestMenu(mainChar)
            questMenu.sidebared = True
            mainChar.rememberedMenu.append(questMenu)

        messagesMenu = src.menuFolder.MessagesMenu.MessagesMenu(mainChar)
        mainChar.rememberedMenu2.append(messagesMenu)
        mainChar.disableCommandsOnPlus = True
        mainChar.autoExpandQuests2 = True

        print("len(self.available_positions)")
        print(len(self.available_positions))

        while self.available_positions:
            self.setUpRuin(self.get_free_position("ruin"))

        self.numRounds = 1
        self.startRound()

        self.checkDead()


        containerQuest = src.quests.questMap["ReachOutStory"]()
        containerQuest.assignToCharacter(src.gamestate.gamestate.mainChar)
        containerQuest.activate()
        containerQuest.endTrigger = {"container": self, "method": "openedQuests"}
        src.gamestate.gamestate.mainChar.quests.append(containerQuest)

        src.gamestate.gamestate.mainChar.messages = []

        src.interaction.showRunIntro()
        self.kickoff()

    def mainCharacterDeath(self,extraParam):
        if not src.gamestate.gamestate.mainChar.dead:
            return
        else:
            src.StateFolder.death.Death(extraParam)

    def kickoff(self):
        if self.activeStory["type"] == "story start":
            if len(self.activeStory["mainChar"].messages) == 0:
                text = """
You.
You see walls made out of solid steel
and feel the touch of the cold hard floor.
The room is filled with various items.
You recognise your hostile suroundings and
try to remember how you got here ..."""
                self.activeStory["mainChar"].messages.insert(0,(text))
                self.activeStory["failedReintegration"] = True
            self.activeStory["mainChar"].messages.insert(0,("""until the explosions fully wake you."""))
            self.activeStory["sternsContraption"].startMeltdown()

    def gotEpochReward(self,extraParam):
        if self.difficulty == "tutorial" and "NPC" in extraParam["rewardType"]:
            try:
                self.showed_npc_respawn_info
            except:
                self.showed_npc_respawn_info = False

            if not self.showed_npc_respawn_info:
                text = """
You spawned a NPC. The NPC will do some work on the base,
but that is not why the NPC is so important.

The NPC basically acts as an extra life.
If you have no NPCs the game is permadeath.
This means you die and the game ends.

If you die and have NPCs in your base,
you will take control over one of those NPCs.
So now you can die and respawn afterwards until you run out of NPCs.

Now claim the other GlassHearts to win the game.
Use the other GlassStatues (GG) to teleport to dungeons.
Then go and claim their heart.

You should start with the GlassStatue on the top right.
That GlassStatue leads to the next easiest dungeon.
"""
                submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                self.activeStory["mainChar"].macroState["submenue"] = submenu
                self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                self.activeStory["mainChar"].addMessage(text)

                self.showed_npc_respawn_info = True

        if self.difficulty == "medium":
            pass

    def deliveredSpecialItem(self,extraParam):
        if self.difficulty == "tutorial":
            try:
                self.showed_glass_heart_info
            except:
                self.showed_glass_heart_info = False

            if not self.showed_glass_heart_info:
                text = """
You claimed ownership of a GlassHeart.
This means you are one step closer to win the game.
You need to control all GlassHearts to win the game.

You also get some mana as a reward.
Use that to spawn a NPC. That is pretty important actually.

Use the leftmost Shrine (\\/) to wish for a NPC.
What the NPC does does not matter on easy.
"""
                submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                self.activeStory["mainChar"].macroState["submenue"] = submenu
                self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                self.activeStory["mainChar"].addMessage(text)

                self.showed_glass_heart_info = True
                return

            try:
                self.showed_glass_heart_info2
            except:
                self.showed_glass_heart_info2 = False

            if not self.showed_glass_heart_info2:
                text = """
You claimed ownership of the second GlassHeart.
On easy this means that you collected all GlassHearts.

Now there is only one step left to do.
Use the Throne (TT) in the middle of the Temple to win the game.
"""
                submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                self.activeStory["mainChar"].macroState["submenue"] = submenu
                self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                self.activeStory["mainChar"].addMessage(text)

                self.showed_glass_heart_info2 = True
                return

            '''
            numGlassHearts = 0
            for god,godData in src.gamestate.gamestate.gods.items():
                if godData["lastHeartPos"] == (self.activeStory["mainChar"].getTerrain().xPosition,self.activeStory["mainChar"].getTerrain().yPosition):
                    numGlassHearts += 1

            if numGlassHearts == 7:
                text = """
You claimed all GlassHearts.

And when you are done then try medium difficulty, much more will be explained there.
"""
                submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                self.activeStory["mainChar"].macroState["submenue"] = submenu
                self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                self.activeStory["mainChar"].addMessage(text)

                self.showed_glass_heart_info2 = True
                return
            '''

    def changedTerrain(self,extraParam):
        item = extraParam["character"]

        if self.difficulty == "tutorial":
            try:
                self.showedBaseInfo
            except:
                self.showedBaseInfo = False

            if not self.showedBaseInfo:
                    text = """
You returned to your base. The base is your home.
It is a small base, but it has a temple.
Bring the GlassHeart to your temple.

Use the GlassStatue marked as (kk) to claim the GlassHeart as yours.
When the GlassHeart is properly set it will show as KK.
"""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedBaseInfo = True

        if self.difficulty == ("medium","easy",):
            try:
                self.showedBaseInfo
            except:
                self.showedBaseInfo = False

            if not self.showedBaseInfo:
                    text = """
You returned to your base. The base is your home.
Just like in easy difficulty the base has a temple,
but on medium difficulty you have to make use of the base.

Remember the Bolts you need to be able to shooot at enemies?
Your base can produce those while you do other things.

To get basic production active you need the following NPCs:

a resource gatherer
a scrap hammerer
a metal worker"""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedBaseInfo = True

    def itemPickedUp(self,extraParam):
        item = extraParam[1]

        if self.difficulty == "tutorial":
            try:
                self.showedGlassHeartInfo
            except:
                self.showedGlassHeartInfo = False

            if not self.showedGlassHeartInfo:
                if item.type == "SpecialItem":
                    text = """
You picked up the GlassHeart.
Now return to your base to put the GlassHeart to use.

To return back to the base use the Shrine (\\/).
Select the "teleport home" option to get back to base."""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
    """)
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedGlassHeartInfo = True
                    return
        if self.difficulty == ("medium","easy",):
            try:
                self.showedGlassHeartInfo
            except:
                self.showedGlassHeartInfo = False

            if not self.showedGlassHeartInfo:
                if item.type == "SpecialItem":
                    text = """
You picked up the GlassHeart.
Until you bring set it into a GlassStatue again you are cursed.

Your movement speed is halfed, so running from enemies is much harder.
Bring the GlassHeart back to your base to lift that curse."""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
    """)
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedGlassHeartInfo = True
                    return
            try:
                self.showedVialInfo
            except:
                self.showedVialInfo = False

            if not self.showedVialInfo:
                if item.type == "Vial":
                    text = """
You picked up a Vial.
Vials can be used to heal yourself.

You can use the Vial directly to heal, but there is a easier way.
Use the advanced interaction menu (J) to heal once (h) or heal fully (H).
For this you have to have a healing item like the Vial in you inventory.

The less health you have the stronger the Vials healing effect.
"""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
    """)
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedVialInfo = True
                    return

            try:
                self.showedGooFlaskInfo
            except:
                self.showedGooFlaskInfo = False

            if not self.showedGooFlaskInfo:
                if item.type == "GooFlask":
                    text = """
You picked up a Goo Flask.
Their primary use as food source is not important right now.
You have a GooFlask equipped and should have thaousands of moves left.

A completely full GooFlask is very valuable, because it helps spawning new NPCs.
Have a GooFlask in your inventory when wishing for a NPC and you will use less mana.
The GooFlask is destroyed in the progress though.

So bring it with you to be able to spawn one NPC cheaper.
"""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
    """)
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedGooFlaskInfo = True
                    return

    def enteredRoom(self,extraParam):
        newRoom = extraParam[1]

        if self.difficulty == "tutorial":
            try:
                self.showedEnemyWarning
            except:
                self.showedEnemyWarning = False

            if not self.showedEnemyWarning:
                foundEnemies = False
                for otherChar in newRoom.characters:
                    if otherChar.faction == extraParam[0].faction:
                        continue
                    foundEnemies = True

                if foundEnemies:
                    text = """
There are enemies in the room.
Enemies are shown with a red background.
Fight the enemies by bumping into them.

There are more complex fighting systems,
but you won't need them on easy difficulty."""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedEnemyWarning = True
                    return

            try:
                self.showedLandMineWarning
            except:
                self.showedLandMineWarning = False

            if not self.showedLandMineWarning:
                foundLandMine = False
                for item in newRoom.itemsOnFloor:
                    if item.type != "LandMine":
                        continue
                    foundLandMine = True

                if foundLandMine:
                    text = """
This room contains LandMines.
Active LandMines are shown as red "_~".

Try not to step onto them and avoid standing next to them."""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedLandMineWarning = True
                    return

            try:
                self.showedStatueExtractInfo
            except:
                self.showedStatueExtractInfo = False

            if not self.showedStatueExtractInfo:
                foundFilledStatue = False
                for item in newRoom.itemsOnFloor:
                    if item.type != "GlassStatue":
                        continue
                    if not item.hasItem:
                        continue
                    foundFilledStatue = True

                if foundFilledStatue:
                    text = """
You reached the central chamber of a dungeon.

Use the GlassStatue to extract the GlassHeart from the GlassStatue (KK).
Pick up the GlassHeart (!!) afterwards.

press ? after closing this menu to see what keys you need to use.
"""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedStatueExtractInfo = True
                    return

        if self.difficulty == ("medium","easy",):
            foundEnemies = False
            for otherChar in newRoom.characters:
                if otherChar.faction == extraParam[0].faction:
                    continue
                foundEnemies = True

            foundLandMine = False
            for item in newRoom.itemsOnFloor:
                if item.type != "LandMine":
                    continue
                foundLandMine = True

            foundStopStatue = False
            for item in newRoom.itemsOnFloor:
                if item.type != "StopStatue":
                    continue
                foundStopStatue = True

            try:
                self.showedExtraLoot
            except:
                self.showedExtraLoot = False

            if not self.showedExtraLoot:
                foundFilledStatue = False
                for item in newRoom.itemsOnFloor:
                    if item.type != "GlassStatue":
                        continue
                    if not item.hasItem:
                        continue
                    foundFilledStatue = True

                if foundFilledStatue:
                    text = """
You reached the central chamber of the dungeon.
Keep in mind that the GlassHeart is not the only reward in this room.

Remember to take the additional items with you.
"""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedExtraLoot = True
                    return

            if foundEnemies:
                try:
                    self.showedAdvanceCombatInfo
                except:
                    self.showedAdvanceCombatInfo = False

                if not self.showedAdvanceCombatInfo:
                    text = """
One big difference is that you are weaker and the enemies are stronger.
This means you can still kill them by bumping into them,
but the enemies can realistically kill you.

If you bump into the enemies using WASD you can do special attacks.
Those do much more damage, but often cause exhaustion.
If you have more than 10 exhaustion then you get penalities.

To reduce your exhaustion press .
"""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedAdvanceCombatInfo = True
                    return

                try:
                    self.showedRangedCombatInfo
                except:
                    self.showedRangedCombatInfo = False

                if not self.showedRangedCombatInfo:
                    text = """
Another thing you can to is to used ranged combat.

The ranged combat allows you to fire bolts by pressing f.
As long as you have Bolts in your inventory, you can shoot in straight lines.
Each shot will consume a Bolt.
"""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedRangedCombatInfo = True
                    return

                if foundLandMine:
                    try:
                        self.showedLandMineLuringInfo
                    except:
                        self.showedLandMineLuringInfo = False

                    if not self.showedLandMineLuringInfo:
                        text = """
Another thing you can to is to kite enemies into LandMines.

It usually kills the enemies and they often step into them.
I can hurt you quite a lot, too. So remember to keep a distance.


"""
                        submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                        self.activeStory["mainChar"].macroState["submenue"] = submenu
                        self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                        self.activeStory["mainChar"].addMessage(text)

                        self.showedLandMineLuringInfo = True
                        return

                try:
                    self.showedBaitInfo
                except:
                    self.showedBaitInfo = False

                if not self.showedBaitInfo:
                    text = """
Another thing you can to is to bait/kite enemies

When you enter and leave a room sometimes enemies will chase you.
You can use this to divide enemy groups and kite enemies into traps.
"""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedBaitInfo = True
                    return

                try:
                    self.showedWaitInfo
                except:
                    self.showedWaitInfo = False

                if not self.showedWaitInfo:
                    text = """
Another thing you can to is to wait to heal.

When time passes you slowly heal, so you can just wait
The more hurt you are the faster you heal.
So this works best when you are near dead.
"""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedWaitInfo = True
                    return

            if foundStopStatue:
                try:
                    self.showedStopStatueInfo
                except:
                    self.showedStopStatueInfo = False

                if not self.showedStopStatueInfo:
                    text = """
Some rooms in the dungeons have a StopStatue (OO) item.
This item allows to destroy statues in the same room,
but destroys the item itself.

If you can reach and use it without getting killed,
it is a very fast and HP saving way to clear a room.
"""
                    submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                    self.activeStory["mainChar"].macroState["submenue"] = submenu
                    self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                    self.activeStory["mainChar"].addMessage(text)

                    self.showedStopStatueInfo = True
                    return

            if not foundEnemies:
                if foundLandMine:
                    try:
                        self.showedLandMineCollectingInfo
                    except:
                        self.showedLandMineCollectingInfo = False

                    if not self.showedLandMineCollectingInfo:
                        text = """
You not only can lure enemies into LandMines,
but you can also disarm and move Landmines.

Press C to do a complex action on a Landmine.
This will disable the LandMine and it will be shown white.
Then you can pick it up and place it somewhere else.
Use C again to rearm the LandMine.

That way you can build your own traps and lure the enemies into them.
Be carefull though disarming a LandMine takes a long time,
this can easily kill you if enemies are nearby.

You can also pick up active LandMines,
but they are likely to explode when disturbed.
"""
                        submenu = src.menuFolder.TextMenu.TextMenu(text+"""

= press esc to close this menu =
""")
                        self.activeStory["mainChar"].macroState["submenue"] = submenu
                        self.activeStory["mainChar"].runCommandString("~",nativeKey=True)
                        self.activeStory["mainChar"].addMessage(text)

                        self.showedLandMineCollectingInfo = True
                        return

    def setUpDungeon(self,pos):
        #set up dungeons
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.godMode = True
        currentTerrain.addItem(item,(1,1,0))

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

        glassHeart = src.items.itemMap["GlassHeart"]()
        mainRoom.addItem(glassHeart,(6,6,0))

    def setUpThroneDungeon(self,pos):
        #set up dungeons
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.godMode = True
        currentTerrain.addItem(item,(1,1,0))

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

        glassHeart = src.items.itemMap["Throne"]()
        mainRoom.addItem(glassHeart,(6,6,0))

        for x in range(1,14):
            for y in range(1,14):
                if x == 7 and y == 7:
                    continue

                enemy = src.characters.characterMap["Monster"](4,4)
                enemy.health = 30
                enemy.baseDamage = 7
                enemy.maxHealth = 30
                enemy.godMode = True
                enemy.movementSpeed = 0.8

                quest = src.quests.questMap["SecureTile"](toSecure=(x,y,0))
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                currentTerrain.addCharacter(enemy, x*15+7, y*15+7)

                for _i in range(random.randint(0,3)):
                    for _j in range(2):
                        scrap = src.items.itemMap["Scrap"](amount=20)
                        currentTerrain.addItem(scrap,(x*15+random.randint(1,12),y*15+random.randint(1,12),0))

    def setUpStatueRoom(self,pos,itemID=None):
        if itemID is None:
            itemID = random.choice([1,2,3,4,5,6,7])

        # get basic info
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        currentTerrain.tag = "statue room"

        # set up helper item to spawn stuff
        # bad code: spawning stuff should be in a "magic" class or similar
        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.godMode = True
        currentTerrain.addItem(item,(1,1,0))

        # create the basic room
        room = architect.doAddRoom(
                {
                       "coordinate": (7,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )

        # add random amount of loot 
        statue = src.items.itemMap["GlassStatue"](itemID=itemID)
        statue.charges = 5
        room.addItem(statue,(6,6,0))

    def setUpSternsBase(self,pos):
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        currentTerrain.tag = "sterns base"

        thisFactionId = self.factionCounter
        faction = f"city #{thisFactionId}"
        self.factionCounter += 1

        # set up helper item to spawn stuff
        # bad code: spawning stuff should be in a "magic" class or similar
        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.godMode = True
        currentTerrain.addItem(item,(1,1,0))

        ####
        # create the control room
        ##

        # create the basic room
        mainRoom = architect.doAddRoom(
                {
                       "coordinate": (7,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 6,12 12,6",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )

        # place anvil
        anvilPos = (10,2,0)
        machinemachine = src.items.itemMap["Anvil"]()
        mainRoom.addItem(machinemachine,(anvilPos[0],anvilPos[1],0))
        mainRoom.addInputSlot((anvilPos[0]-1,anvilPos[1],0),"Scrap")
        mainRoom.addInputSlot((anvilPos[0]+1,anvilPos[1],0),"Scrap")
        mainRoom.addOutputSlot((anvilPos[0],anvilPos[1]-1,0),None)
        mainRoom.walkingSpace.add((anvilPos[0],anvilPos[1]+1,0))

        # place metal working bench
        metalWorkBenchPos = (8,3,0)
        machinemachine = src.items.itemMap["MetalWorkingBench"]()
        mainRoom.addItem(machinemachine,(metalWorkBenchPos[0],metalWorkBenchPos[1],0))
        mainRoom.addInputSlot((metalWorkBenchPos[0]+1,metalWorkBenchPos[1],0),"MetalBars")
        mainRoom.addOutputSlot((metalWorkBenchPos[0],metalWorkBenchPos[1]-1,0),None)
        mainRoom.addOutputSlot((metalWorkBenchPos[0],metalWorkBenchPos[1]+1,0),None)
        mainRoom.walkingSpace.add((metalWorkBenchPos[0]-1,metalWorkBenchPos[1],0))

        # add walking space cross
        for y in range(1,12):
            mainRoom.walkingSpace.add((6,y,0))
        for x in range(1,6):
            mainRoom.walkingSpace.add((x,6,0))

        # add storage section
        mainRoom.walkingSpace.add((11,6,0))
        for y in (11,9,8,6):
            for x in range(7,12):
                if (x,y) == (11,6):
                    continue
                mainRoom.addStorageSlot((x,y,0),None,{})
                if y == 11:
                    scrap = src.items.itemMap["Scrap"](amount=20)
                    mainRoom.addItem(scrap,(x,y,0))
                if y == 9 and x in (8,9,10,):
                    flask = src.items.itemMap["GooFlask"]()
                    flask.uses = 100
                    mainRoom.addItem(flask,(x,y,0))

        # add walking space in storage section
        for y in (10,7,5):
            for x in range(7,12):
                mainRoom.walkingSpace.add((x,y,0))
        for y in (8,11):
            for x in range(1,7):
                mainRoom.walkingSpace.add((x,y,0))

        for x in range(2,6):
            mainRoom.walkingSpace.add((x,3,0))

        # add items
        painter = src.items.itemMap["Painter"]()
        mainRoom.addItem(painter,(7,8,0))

        # add mini wall production
        mainRoom.addInputSlot((1,7,0),"MetalBars")
        manufacturingTable = src.items.itemMap["ManufacturingTable"]()
        manufacturingTable.bolted = True
        manufacturingTable.toProduce = "Rod"
        mainRoom.addItem(manufacturingTable,(2,7,0))
        mainRoom.addStorageSlot((3,7,0),"Rod",{"desiredState":"filled"})
        manufacturingTable = src.items.itemMap["ManufacturingTable"]()
        manufacturingTable.bolted = True
        manufacturingTable.toProduce = "Frame"
        mainRoom.addItem(manufacturingTable,(4,7,0))
        mainRoom.addStorageSlot((5,7,0),"Frame",{"desiredState":"filled"})
        mainRoom.addInputSlot((1,10,0),"Frame",None)
        manufacturingTable = src.items.itemMap["ManufacturingTable"]()
        manufacturingTable.bolted = True
        manufacturingTable.toProduce = "Case"
        mainRoom.addItem(manufacturingTable,(2,10,0))
        mainRoom.addStorageSlot((3,10,0),"Case",{"desiredState":"filled"})
        mainRoom.addInputSlot((4,9,0),"MetalBars")
        manufacturingTable = src.items.itemMap["ManufacturingTable"]()
        manufacturingTable.bolted = True
        manufacturingTable.toProduce = "Wall"
        mainRoom.addItem(manufacturingTable,(4,10,0))
        mainRoom.addStorageSlot((5,10,0),"Wall")

        # add scrap compactor
        mainRoom.addInputSlot((1,9,0),"Scrap")
        scrapCompactor = src.items.itemMap["ScrapCompactor"]()
        scrapCompactor.bolted = True
        mainRoom.addItem(scrapCompactor,(2,9,0))
        mainRoom.addStorageSlot((3,9,0),"MetalBars",None)

        # add management items
        cityPlaner = src.items.itemMap["CityPlaner"]()
        cityPlaner.bolted = True
        mainRoom.addItem(cityPlaner,(2,2,0))
        promoter = src.items.itemMap["Promoter"]()
        promoter.bolted = True
        mainRoom.addItem(promoter,(4,2,0))
        dutyArtwork = src.items.itemMap["DutyArtwork"]()
        dutyArtwork.bolted = True
        mainRoom.addItem(dutyArtwork,(2,4,0))
        siegeManager = src.items.itemMap["SiegeManager"]()
        siegeManager.bolted = True
        mainRoom.addItem(siegeManager,(4,4,0))
        siegeManager.handleTick()

        # spawn npc
        actualCharacter = src.characters.Character()
        sword = src.items.itemMap["Sword"]()
        sword.baseDamage = 10
        actualCharacter.weapon = sword
        actualCharacter.faction = faction
        mainRoom.addCharacter(actualCharacter,5,5)

        # make npc protect the room
        quest = src.quests.questMap["SecureTile"](toSecure=mainRoom.getPosition())
        quest.autoSolve = True
        quest.assignToCharacter(actualCharacter)
        quest.activate()
        actualCharacter.quests.append(quest)

        ####
        # create manufacturing hall
        ##
        manufacturingHall = architect.doAddRoom(
                {
                       "coordinate": (8,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )
        for item in manufacturingHall.itemsOnFloor:
            if item.type != "Door":
                continue
            if item.getPosition() == (0,6,0):
                continue
            item.walkable = False

        ####
        # create storage room
        ##

        #8,8

        ####
        # create spawn room
        ##
        spawnRoom = architect.doAddRoom(
                {
                       "coordinate": (7,8),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )
        for item in spawnRoom.itemsOnFloor:
            if item.type != "Door":
                continue
            if item.getPosition() == (6,0,0):
                continue
            item.walkable = False

        factionChanger = src.items.itemMap["FactionSetter"]()
        factionChanger.faction = faction
        spawnRoom.addItem(factionChanger,(5,3,0))

        for y in range(1,10):
            spawnRoom.walkingSpace.add((6,y,0))
        for x in range(1,12):
            for y in (9,4,):
                if x == 6:
                    continue
                spawnRoom.walkingSpace.add((x,y,0))

        integrator = src.items.itemMap["Integrator"]()
        spawnRoom.addItem(integrator,(7,3,0))

        spawnRoom.addStorageSlot((2,3,0),"GooFlask",{"desiredState":"filled"})
        growthTank = src.items.itemMap["GrowthTank"]()
        spawnRoom.addItem(growthTank,(3,3,0))

        command = src.items.itemMap["Command"]()
        command.command = list("dj")+["enter"]+list("sdddJwaaaw")
        spawnRoom.addItem(command,(4,3,0))

        flask = src.items.itemMap["GooFlask"]()
        flask.uses = 100
        spawnRoom.addItem(flask,(2,3,0))

        spawnRoom.addStorageSlot((10,8,0),"Flask",{"desiredState":"filled"})

        throneRoom = architect.doAddRoom(
                {
                       "coordinate": (7,6),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )
        throneRoom.tag = "temple"
        for item in throneRoom.itemsOnFloor:
            if item.type != "Door":
                continue
            if item.getPosition() == (6,12,0):
                continue
            item.walkable = False
        throneRoom.priority = 5

        for x in (2,10,):
            for y in range(1,12):
                throneRoom.walkingSpace.add((x,y,0))
        for x in range(3,10):
            for y in (3,6,):
                throneRoom.walkingSpace.add((x,y,0))
        for x in range(5,8):
            for y in range(7,12):
                if (x,y) in ((6,9),(6,8),(6,10)):
                    continue
                throneRoom.walkingSpace.add((x,y,0))

        for godId in range(1,8):
            shrine = src.items.itemMap["Shrine"]()
            shrine.god = godId
            throneRoom.addItem(shrine,(godId+2,2,0))

            statue = src.items.itemMap["GlassStatue"]()
            statue.itemID = godId
            statue.charges = 4
            throneRoom.addItem(statue,(godId+2,5,0))

            throneRoom.addInputSlot((godId+2,4,0),src.gamestate.gamestate.gods[godId]["sacrifice"][0],{})

        throne = src.items.itemMap["Throne"]()
        throne.bolted = True
        throneRoom.addItem(throne,(6,8,0))
        dutyBeacon = src.items.itemMap["DutyBeacon"]()
        dutyBeacon.bolted = True
        throneRoom.addItem(dutyBeacon,(6,9,0))
        throneRoom.addItem(src.items.itemMap["Regenerator"](), (6, 10, 0))


        for basePos in [(1,2,0),(11,2,0),(1,10,0),(11,10,0)]:
            motionSensor = src.items.itemMap["MotionSensor"]()
            motionSensor.target = (basePos[0],basePos[1],basePos[2])
            throneRoom.addItem(motionSensor,(basePos[0],basePos[1]-1,basePos[2]))
            motionSensor.boltAction(None)
            motionSensor.faction = faction
            shocktower = src.items.itemMap["ShockTower"]()
            throneRoom.addItem(shocktower,(basePos[0],basePos[1],basePos[2]))
            throneRoom.addInputSlot((basePos[0],basePos[1]+1,basePos[2]),"LightningRod")

            for i in range(1,10):
                lightningRod = src.items.itemMap["LightningRod"]()
                throneRoom.addItem(lightningRod,(basePos[0],basePos[1]+1,basePos[2]))

            if basePos == (1,2,0):
                shocktower.charges = 10

        trapRoom1 = architect.doAddRoom(
                {
                       "coordinate": (6,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 12,6",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )

        sword = src.items.itemMap["Sword"]()
        sword.baseDamage = 15
        if self.difficulty == "easy":
            sword.baseDamage = 25
        if self.difficulty == "difficult":
            sword.baseDamage = 10
        sword.bolted = False
        trapRoom1.addItem(sword,(11,3,0))
        armor = src.items.itemMap["Armor"]()
        armor.armorValue = 3
        if self.difficulty == "easy":
            armor.armorValue = 5
        if self.difficulty == "difficult":
            armor.armorValue = 1
        armor.bolted = False
        trapRoom1.addItem(armor,(11,4,0))

        sword = src.items.itemMap["Sword"]()
        sword.baseDamage = 15
        if self.difficulty == "easy":
            sword.baseDamage = 25
        if self.difficulty == "difficult":
            sword.baseDamage = 10
        sword.bolted = False
        trapRoom1.addItem(sword,(11,1,0))
        armor = src.items.itemMap["Armor"]()
        armor.armorValue = 3
        if self.difficulty == "easy":
            armor.armorValue = 5
        if self.difficulty == "difficult":
            armor.armorValue = 1
        armor.bolted = False
        trapRoom1.addItem(armor,(11,2,0))

        coalBurner = src.items.itemMap["CoalBurner"]()
        coalBurner.bolted = True
        trapRoom1.addItem(coalBurner,(11,8,0))

        trapRoom1.addInputSlot((11,9,0),"MoldFeed",{})
        moldFeed = src.items.itemMap["MoldFeed"]()
        trapRoom1.addItem(moldFeed,(11,9,0))
        moldFeed = src.items.itemMap["MoldFeed"]()
        trapRoom1.addItem(moldFeed,(11,9,0))
        moldFeed = src.items.itemMap["MoldFeed"]()
        trapRoom1.addItem(moldFeed,(11,9,0))
        moldFeed = src.items.itemMap["MoldFeed"]()
        trapRoom1.addItem(moldFeed,(11,9,0))
        moldFeed = src.items.itemMap["MoldFeed"]()
        trapRoom1.addItem(moldFeed,(11,9,0))
        moldFeed = src.items.itemMap["MoldFeed"]()
        trapRoom1.addItem(moldFeed,(11,9,0))
        moldFeed = src.items.itemMap["MoldFeed"]()
        trapRoom1.addItem(moldFeed,(11,9,0))

        for x in range(1,12):
            for y in range(2,11):
                if (x,y) in ((11,9),(11,8)):
                    continue
                trapRoom1.walkingSpace.add((x,y,0))

        # added ghoul automation for harvesting
        corpseAnimator = src.items.itemMap["CorpseAnimator"]()
        corpseAnimator.bolted = True
        trapRoom1.addItem(corpseAnimator,(2,1,0))
        command = src.items.itemMap["Command"]()
        command.bolted = True
        command.command = ""
        command.command += "5s5a6a" # move to traproom center
        command.command += "14sj" # activate field
        command.command += "13sj" # activate field
        command.command += "13aj" # activate field
        command.command += "13wj" # activate field
        command.command += "13wj" # activate field
        command.command += "13d" # move to traproom center
        command.command += "11d5w" # move to traproom center
        command.command += "s"+"dLw"*8 # fill output stockpiles
        command.command += "8aw" # return to start position
        command.repeat = True
        trapRoom1.addItem(command,(3,1,0))
        trapRoom1.addInputSlot((1,1,0),"Corpse")
        for x in range(4,12):
            trapRoom1.addOutputSlot((x,1,0),None)


        # added ghoul automation for trap room clearing
        corpseAnimator = src.items.itemMap["CorpseAnimator"]()
        corpseAnimator.bolted = True
        trapRoom1.addItem(corpseAnimator,(2,11,0))
        command = src.items.itemMap["Command"]()
        command.bolted = True
        command.command = ""
        command.command += "5w5a6a" # move to traproom center
        command.command += "Kdd"*5+"5a" # clear east line 
        command.command += "Kaa"*5+"5d" # clear west line
        command.command += "Kss"*5+"5w" # clear south line
        command.command += "Kww"*5+"5s" # clear north line
        command.command += "6d"+"5d5s" # return to start position
        command.command += "w"+"dLs"*8 # fill output stockpiles
        command.command += "8as" # return to start position
        command.command += "100." # wait
        command.repeat = True
        trapRoom1.addItem(command,(3,11,0))
        trapRoom1.addInputSlot((1,11,0),"Corpse")
        for x in range(4,12):
            trapRoom1.addOutputSlot((x,11,0),None)

        ###############################################
        ###
        ##  add the trap room
        #

        # add the actual room
        trapRoom2 = architect.doAddRoom(
                {
                       "coordinate": (5,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )

        # add walking space in the center
        trapRoom2.addWalkingSpace((6,6,0))

        # add north-south trap line
        for y in (1,2,3,4,5,7,8,9,10,11):
            triggerPlate = src.items.itemMap["TriggerPlate"]()
            triggerPlate.faction = faction
            triggerPlate.bolted = True
            trapRoom2.addItem(triggerPlate,(6,y,0))
            trapRoom2.addWalkingSpace((6,y,0))
            for x in (5,7):
                rodTower = src.items.itemMap["RodTower"]()
                trapRoom2.addItem(rodTower,(x,y,0))
                triggerPlate.targets.append((x,y,0))

        # add west-east trap line
        for x in (1,2,3,4,5,7,8,9,10,11):
            triggerPlate = src.items.itemMap["TriggerPlate"]()
            triggerPlate.faction = faction
            triggerPlate.bolted = True
            trapRoom2.addItem(triggerPlate,(x,6,0))
            trapRoom2.addWalkingSpace((x,6,0))
            for y in (5,7):
                if x not in (5,7,):
                    rodTower = src.items.itemMap["RodTower"]()
                    trapRoom2.addItem(rodTower,(x,y,0))
                triggerPlate.targets.append((x,y,0))

        # block some of the trap
        for pos in ((1,6,0),(2,6,0),(6,1,0),(6,2,0),(6,11,0),(6,10,0)):
            moldFeed = src.items.itemMap["MoldFeed"]()
            trapRoom2.addItem(moldFeed,pos)

        ###############################################
        ###
        ##  load hardcoded placements
        #

        labPosition = (6,10,0)
        labPositionExit = (6,9,0)
        specialSpots = [(4,6,0),(4,8,0),(3,10,0),(3,7,0),(5,8,0),(7,9,0)]
        moldTiles = [(2,9,0),(5,9,0),(5,8,0),(4,9,0),(4,8,0),(4,7,0)]
        farmPlotTiles = [(5,9,0),(5,8,0),(4,9,0),(4,8,0),(4,7,0)]
        fightingSpots = [(6,5,0),(1,8,0),(2,10,0),(6,8,0),(9,8,0),(10,6,0),(9,5,0),(7,5,0),(3,8,0),(3,6,0)]
        wallTiles = [(4,3,0),(2,3,0),(2,2,0),(5,2,0),(6,3,0),(8,1,0),(10,3,0),(11,4,0),(12,4,0),(11,8,0),(11,11,0),(12,11,0),(11,12,0),(10,13,0),(9,12,0),(7,12,0),]
        snatcherNests = [(4,12,0),(8,3,0),]

        ###############################################
        ###
        ##  add the lab/starter room
        #

        # add the actual room
        startRoom = architect.doAddRoom(
                {
                       "coordinate": labPosition,
                       "roomType": "EmptyRoom",
                       "doors": "6,0",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )
        startRoom.tag = "sternslab"

        # add vial just outside the lab
        vial = src.items.itemMap["Vial"]()
        vial.uses = 2
        currentTerrain.addItem(vial, (labPositionExit[0]*15+3,labPositionExit[1]*15+4,0))
        vial = src.items.itemMap["Vial"]()
        vial.uses = 1
        currentTerrain.addItem(vial, (labPositionExit[0]*15+8,labPositionExit[1]*15+2,0))
        
        # add decoration for flavour
        for pos in [(6,1,0),(6,2,0),(6,3,0),(6,4,0),(6,5,0), 
                    (5,5,0),(4,5,0),(4,6,0),(4,7,0),(4,8,0),(5,8,0),(6,8,0),(7,8,0),(8,8,0),(8,7,0),(8,6,0),(8,5,0),(7,5,0)]:
            startRoom.addWalkingSpace(pos)
        for pos in [(5,6,0),(7,6,0),(5,7,0),(6,7,0),(7,7,0),
                    (9,9,0),(10,9,0),(8,9,0),(9,8,0),(9,10,0),
                    (3,9,0),(2,9,0),(4,9,0),(3,8,0),(3,10,0),
                    (9,3,0),(9,2,0),(9,4,0),(8,3,0),(10,3,0),
                    (3,3,0),(4,3,0),(2,3,0),(3,2,0),(3,4,0),]:
            item = src.items.itemMap["Contraption"]()
            item.display = "OT"
            startRoom.addItem(item,pos)

        ###############################################
        ###
        ##  add terrain details
        #

        # scatter walls
        for x in range(1,14):
            for y in range(1,14):
                if (x,y) in ((3,11),):
                    continue
                if currentTerrain.itemsByBigCoordinate.get((x,y,0),[]):
                    continue
                if currentTerrain.charactersByTile.get((x,y),[]):
                    continue
                if (x,y,0) in specialSpots:
                    continue
                if (x,y,0) in moldTiles:
                    continue
                if (x,y,0) in snatcherNests:
                    continue
                if (x,y,0) in moldTiles:
                    continue
                if (x,y,0) in fightingSpots:
                    continue
                for i in range(1,random.randint(1,4)):
                    wall = src.items.itemMap["Wall"]()
                    wall.bolted = False
                    currentTerrain.addItem(wall,(15*x+random.randint(2,11),15*y+random.randint(2,11),0))

        # place initial fighting spots
        for fightingSpot in fightingSpots:

            # add reward
            vial = src.items.itemMap["Vial"]()
            vial.uses = 5
            currentTerrain.addItem(vial,(15*fightingSpot[0]+random.randint(2,11),15*fightingSpot[1]+random.randint(2,11),0))
        
            # add enemy
            enemy = src.characters.characterMap["Spiderling"]()
            enemy.faction = "insects"
            quest = src.quests.questMap["SecureTile"](toSecure=fightingSpot,alwaysHuntDown=True,wandering = True)
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)
            currentTerrain.addCharacter(enemy,fightingSpot[0]*15+random.randint(3,12),fightingSpot[1]*15+random.randint(3,12))

        # spawn wall spots
        for wallTile in wallTiles:

            # add walls
            wallSpots = []
            for x in range(1,14):
                for y in (1,13):
                    if x == 7:
                        continue
                    wallSpots.append((x,y,0))
            for x in (1,13):
                for y in range(2,13):
                    if y == 7:
                        continue
                    wallSpots.append((x,y,0))
            for wallSpot in wallSpots:
                item = src.items.itemMap["Wall"]()
                currentTerrain.addItem(item,(15*wallTile[0]+wallSpot[0],15*wallTile[1]+wallSpot[1],0))

            # add enemies
            for _i in range(0,random.randint(1,5)):
                enemy = src.characters.characterMap["Monster"]()
                enemy.faction = "insects"
                enemy.baseDamage = 6
                quest = src.quests.questMap["SecureTile"](toSecure=wallTile)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)
                currentTerrain.addCharacter(enemy,wallTile[0]*15+random.randint(3,12),wallTile[1]*15+random.randint(3,12))

        # add mold spots
        for moldTile in moldTiles:
            if moldTile in farmPlotTiles:
                autoFarmer = src.items.itemMap["AutoFarmer"]()
                currentTerrain.addItem(autoFarmer,(15*moldTile[0]+7,15*moldTile[1]+7,0))
                for x in range(1,15):
                    if x == 7:
                        continue
                    paving = src.items.itemMap["Paving"]()
                    paving.bolted = True
                    currentTerrain.addItem(paving,(15*moldTile[0]+x,15*moldTile[1]+7,0))
                for y in range(1,15):
                    if y == 7:
                        continue
                    paving = src.items.itemMap["Paving"]()
                    paving.bolted = True
                    currentTerrain.addItem(paving,(15*moldTile[0]+7,15*moldTile[1]+y,0))


            for i in range(1,random.randint(5,10)):
                pos = (random.randint(1,13),random.randint(1,13),0)
                if pos[0] == 7 or pos[1] == 7:
                    continue
                mold = src.items.itemMap["Mold"]()
                currentTerrain.addItem(mold,(15*moldTile[0]+pos[0],15*moldTile[1]+pos[1],0))
                mold.startSpawn()

        # add snatcher nest
        for snatcherNest in snatcherNests:

            # add enemies
            for _i in range(0,random.randint(1,15)):
                enemy = src.characters.characterMap["Snatcher"]()
                enemy.faction = "insects"

                quest = src.quests.questMap["SecureTile"](toSecure=snatcherNest,lifetime=300, wandering=True)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                quest = src.quests.questMap["ClearTerrain"](outsideOnly=True)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                enemy.quests.append(quest)

                currentTerrain.addCharacter(enemy,snatcherNest[0]*15+random.randint(3,12),snatcherNest[1]*15+random.randint(3,12))


        """
        # scatter cocoons
        for x in range(1,14):
            for y in range(1,14):
                if (x,y) in ((3,11),):
                    continue
                if currentTerrain.itemsByBigCoordinate.get((x,y,0),[]):
                    continue
                if currentTerrain.charactersByTile.get((x,y),[]):
                    continue
                if (x,y,0) in specialSpots:
                    continue
                for i in range(1,4):
                    coocon = src.items.itemMap["Cocoon"]()
                    currentTerrain.addItem(coocon,(15*x+random.randint(2,11),15*y+random.randint(2,11),0))
        """

    def setUpFactoryRemains(self,pos):
        # get basic info
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        currentTerrain.tag = "abbandoned Factory"

        # set up helper item to spawn stuff
        # bad code: spawning stuff should be in a "magic" class or similar
        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.godMode = True
        currentTerrain.addItem(item,(1,1,0))

        # create the basic room
        room = architect.doAddRoom(
                {
                       "coordinate": (7,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )

        # add random amount of loot 
        positions = [(4,9,0),(3,3,0),(9,4,0),(2,11,0),(11,11,0),(6,6,0),(5,4,0),(6,9,0),(8,9,0)]
        random.shuffle(positions)
        production_candidates = ["Sword","Armor","Wall","Case","Frame","Rod","Sheet","Bolt","Flask","Tank"]
        to_produce = random.choice(production_candidates)
        for _i in range(1,random.randint(2,8)):
            pos = positions.pop()
            machine = src.items.itemMap["Machine"]()
            machine.setToProduce(to_produce)
            room.addItem(machine,pos)

    def setUpShrine(self,pos):
        # get basic info
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        currentTerrain.tag = "shrine"

        # set up helper item to spawn stuff
        # bad code: spawning stuff should be in a "magic" class or similar
        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.godMode = True
        currentTerrain.addItem(item,(1,1,0))

        # create the basic room
        room = architect.doAddRoom(
                {
                       "coordinate": (7,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )

        # add random amount of loot 
        mana_crystal = src.items.itemMap["Shrine"]()
        room.addItem(mana_crystal,(6,6,0))

    def setUpRuin(self,pos):
        # get basic info
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]

        # set up helper item to spawn stuff
        # bad code: spawning stuff should be in a "magic" class or similar
        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.godMode = True
        currentTerrain.addItem(item,(1,1,0))

        # create the basic room
        room = architect.doAddRoom(
                {
                       "coordinate": (7,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )

        # decide between mixed or pure loot room
        loot_types = ["ScrapCompactor","MetalBars","Vial","MoldFeed","Bolt","Flask","GooFlask","Rod","Sword","Scrap","ManufacturingTable"]
        if random.random() > 0.5:
            loot_types = [random.choice(loot_types)]

        # add random amount of loot 
        for i in range(0,random.randint(1,6)):
            # add loot
            if random.random() < 0.5:
                mana_crystal = src.items.itemMap["ManaCrystal"]()
                room.addItem(mana_crystal,(6,6,0))
            else:
                positions = [(3,8,0),(2,2,0),(11,4,0),(6,11,0),(13,11,0),(5,5,0)]
                item = src.items.itemMap[random.choice(loot_types)]()
                if item.type == "GooFlask":
                    item.uses = 100
                if item.type == "Vial":
                    item.uses = 10
                room.addItem(item,random.choice(positions))

            # give one free loot
            if i == 0:
                continue

            # add monster
            pos = (random.randint(1,11),random.randint(1,11),0)
            statue = src.characters.characterMap["Statue"]()
            statue.godMode = True
            quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition())
            quest.autoSolve = True
            quest.assignToCharacter(statue)
            quest.activate()
            statue.quests.append(quest)
            room.addCharacter(statue, pos[0], pos[1])

    def setUpGlassHeartDungeon(self,pos,itemID,multiplier):
        # bad code: should be named function: setUpGod
        # generate a random sacrifice requirement
        sacrificeCandidates = [
                ("Scrap",30),
                ("Wall",6),
                ("ScrapCompactor",8),
                ("MetalBars", 20),
                ("Vial", 3),
                ("GooFlask", 5),
                ("Rod", 15),
                ("Bolt", 15),
                ("Tank", 15),
                ("Case", 10),
                ("Frame", 12),
                ("Corpse", 1),
                ("MoldFeed", 10),
                ("LightningRod", 5),
                ("Sheet", 15),
                ]
        sacrificeRequirement = random.choice(sacrificeCandidates)

        # overwrite sacrifice requirement on easy
        if self.difficulty == "easy":
            if itemID == 1:
                sacrificeRequirement = ("Scrap",1)
            if itemID == 2:
                sacrificeRequirement = ("MetalBars",1)
            if itemID == 3:
                sacrificeRequirement = ("Rod",1)
            if itemID == 4:
                sacrificeRequirement = ("Frame",1)
            if itemID == 5:
                sacrificeRequirement = ("MoldFeed",1)
            if itemID == 6:
                sacrificeRequirement = ("Bolt",1)
            if itemID == 7:
                sacrificeRequirement = ("Sword",1)

        # create the god
        src.gamestate.gamestate.gods[itemID] = {
                "name":f"god{itemID}","mana":200,"home":pos,"lastHeartPos":pos,"sacrifice":sacrificeRequirement
            }
        if itemID == 1:
            src.gamestate.gamestate.gods[itemID]["roomRewardMapByTerrain"] = {}



        # get basic info
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]

        # set up helper item to spawn stuff
        # bad code: spawning stuff should be in a "magic" class or similar
        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.godMode = True
        currentTerrain.addItem(item,(1,1,0))

        # set mana level
        currentTerrain.mana = 9
        if self.difficulty == "easy":
            currentTerrain.mana = 10
        if self.difficulty == "medium":
            currentTerrain.mana = 4
        if self.difficulty == "difficult":
            currentTerrain.mana = 0

        # add center chamber
        mainRoom = architect.doAddRoom(
                {
                       "coordinate": (7,7),
                       "roomType": "EmptyRoom",
                       "doors": None,
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )

        # set up meta information about dungeon
        mainPath = [(7,7)]
        rooms = []
        currentRing = 0

        # set branching factor
        extraRooms = []
        numExtraRooms = 2
        if self.difficulty == "tutorial":
            numExtraRooms = 0

        # set targeted length of the main path
        targetLen = 10
        if self.difficulty == "tutorial":
            targetLen = 5

        # add entry point to central chamber from random direction
        possibleDirections = [(-1,0),(1,0),(0,-1),(0,1)]
        direction = random.choice(possibleDirections)
        nextMainRoomPos = (mainPath[0][0]+direction[0],mainPath[0][1]+direction[1])

        # add rooms until desired room length is reached
        while len(mainPath) < targetLen:
            # add an extra room (room not on main path)
            if currentRing:
                for i in range(1,1+numExtraRooms):
                    possiblePostions = []
                    for x in range(7-currentRing,7+currentRing+1):
                        for y in range(7-currentRing,7+currentRing+1):
                            possiblePostions.append((x,y))

                    random.shuffle(possiblePostions)

                    addedRoom = False
                    for extraPos in possiblePostions:
                        if extraPos == nextMainRoomPos:
                            continue
                        if currentTerrain.getRoomByPosition(extraPos):
                            continue
                        possibleNeighbourDirections = [(-1,0),(1,0),(0,-1),(0,1)]
                        hasNeighbour = False
                        neighbourPos = None
                        for direction in possibleNeighbourDirections:
                            testPos = (extraPos[0]+direction[0],extraPos[1]+direction[1])
                            if testPos == (7,7):
                                continue
                            if not testPos in mainPath:
                                continue
                            neighbourPos = testPos
                            hasNeighbour = True
                            break

                        if not hasNeighbour:
                            continue

                        print(f"extra at {extraPos}")
                        room = architect.doAddRoom(
                                {
                                       "coordinate": extraPos,
                                       "roomType": "EmptyRoom",
                                       "doors":None,
                                       "offset": [1,1],
                                   "size": [13, 13],
                                },
                                None,
                           )
                        addedRoom = True

                        neighbourRoom = currentTerrain.getRoomByPosition(neighbourPos)[0]
                        if direction == (1,0):
                            room.addDoor("east")
                            neighbourRoom.addDoor("west")
                        if direction == (-1,0):
                            room.addDoor("west")
                            neighbourRoom.addDoor("east")
                        if direction == (0,1):
                            room.addDoor("south")
                            neighbourRoom.addDoor("north")
                        if direction == (0,-1):
                            room.addDoor("north")
                            neighbourRoom.addDoor("south")

                        extraRooms.append(room)
                        break

                    if not addedRoom:
                        for extraPos in possiblePostions:
                            if extraPos == nextMainRoomPos:
                                continue
                            if currentTerrain.getRoomByPosition(extraPos):
                                continue
                            possibleNeighbourDirections = [(-1,0),(1,0),(0,-1),(0,1)]
                            hasNeighbour = False
                            for direction in possibleNeighbourDirections:
                                neighbourRoom = currentTerrain.getRoomByPosition((extraPos[0]+direction[0],extraPos[1]+direction[1]))
                                if not neighbourRoom:
                                    continue
                                neighbourRoom = neighbourRoom[0]
                                hasNeighbour = True
                                break

                            if not hasNeighbour:
                                continue

                            print(f"extra at {extraPos}")
                            room = architect.doAddRoom(
                                    {
                                           "coordinate": extraPos,
                                           "roomType": "EmptyRoom",
                                           "doors":None,
                                           "offset": [1,1],
                                       "size": [13, 13],
                                    },
                                    None,
                               )

                            if direction == (1,0):
                                room.addDoor("east")
                                neighbourRoom.addDoor("west")
                            if direction == (-1,0):
                                room.addDoor("west")
                                neighbourRoom.addDoor("east")
                            if direction == (0,1):
                                room.addDoor("south")
                                neighbourRoom.addDoor("north")
                            if direction == (0,-1):
                                room.addDoor("north")
                                neighbourRoom.addDoor("south")

                            extraRooms.append(room)
                            break

            # spawn room on main path
            pos = nextMainRoomPos
            room = architect.doAddRoom(
                    {
                           "coordinate": pos,
                           "roomType": "EmptyRoom",
                           "doors":None,
                           "offset": [1,1],
                           "size": [13, 13],
                    },
                    None,
               )
            print(f"room at {pos}")

            attachmentRoom = currentTerrain.getRoomByPosition(mainPath[-1])[0]
            if mainPath[-1][0] < pos[0]:
                room.addDoor("west")
                attachmentRoom.addDoor("east")
            if mainPath[-1][0] > pos[0]:
                room.addDoor("east")
                attachmentRoom.addDoor("west")
            if mainPath[-1][1] < pos[1]:
                room.addDoor("north")
                attachmentRoom.addDoor("south")
            if mainPath[-1][1] > pos[1]:
                room.addDoor("south")
                attachmentRoom.addDoor("north")
            rooms.append(room)
            mainPath.append(pos)

            # calculate next position
            currentRing = max(abs(pos[0]-7),abs(pos[1]-7))
            possibleDirections = [(-1,0),(1,0),(0,-1),(0,1)]
            candidatePositions = []
            for direction in possibleDirections:
                possiblePosition = (pos[0]+direction[0],pos[1]+direction[1])
                if currentTerrain.getRoomByPosition(possiblePosition):
                    continue
                nextRing = max(abs(possiblePosition[0]-7),abs(possiblePosition[1]-7))
                if nextRing < currentRing:
                    continue
                elif nextRing == currentRing:
                    candidatePositions.append(possiblePosition)
                    candidatePositions.append(possiblePosition)
                    candidatePositions.append(possiblePosition)
                    #candidatePositions.append(possiblePosition)
                    #candidatePositions.append(possiblePosition)
                else:
                    candidatePositions.append(possiblePosition)

            # handle invalid state (by crashing and burning, lol)
            if not candidatePositions:
                1/0

            # schedule next room to add
            nextMainRoomPos = random.choice(candidatePositions)

        # add entry room
        attachmentRoom = rooms[-1]
        if mainPath[-1][0] < nextMainRoomPos[0]:
            attachmentRoom.addDoor("east")
        if mainPath[-1][0] > nextMainRoomPos[0]:
            attachmentRoom.addDoor("west")
        if mainPath[-1][1] < nextMainRoomPos[1]:
            attachmentRoom.addDoor("south")
        if mainPath[-1][1] > nextMainRoomPos[1]:
            attachmentRoom.addDoor("north")
        rooms.append(room)
        mainPath.append(pos)

        # spawn monsters on main path
        runModifier = (random.random()-0.5)*0.5
        logger.info(f"runmodifer dungeon {itemID}: {runModifier}")
        counter = 0
        for room in reversed(rooms[:-2]):

            if counter == 0:
                counter += 1
                continue

            for _i in range(1):
                pos = (random.randint(1,11),random.randint(1,11),0)
                statue = src.characters.characterMap["Statue"](4,4,multiplier = multiplier,runModifier = runModifier)
                quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition())
                quest.autoSolve = True
                quest.assignToCharacter(statue)
                quest.activate()
                statue.quests.append(quest)

                room.addCharacter(statue, pos[0], pos[1])

            for _i in range(counter-1):
                pos = (random.randint(1,11),random.randint(1,11),0)
                statuette = src.characters.characterMap["Statuette"](4,4,multiplier = multiplier,runModifier = runModifier)

                quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition())
                quest.autoSolve = True
                quest.assignToCharacter(statuette)
                quest.activate()
                statuette.quests.append(quest)

                room.addCharacter(statuette, pos[0], pos[1])

            counter += 1

        # spawn monsters on dead ends
        for room in reversed(extraRooms):
            for _i in range(1):
                pos = (random.randint(1,11),random.randint(1,11),0)
                statue = src.characters.characterMap["Statue"](4,4,multiplier = multiplier,runModifier = runModifier)

                quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition())
                quest.autoSolve = True
                quest.assignToCharacter(statue)
                quest.activate()
                statue.quests.append(quest)

                room.addCharacter(statue, pos[0], pos[1])

            for _i in range(random.randint(3,8)):
                pos = (random.randint(1,11),random.randint(1,11),0)
                statuette = src.characters.characterMap["Statuette"](4,4,multiplier = multiplier,runModifier = runModifier)

                quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition())
                quest.autoSolve = True
                quest.assignToCharacter(statuette)
                quest.activate()
                statuette.quests.append(quest)

                room.addCharacter(statuette, pos[0], pos[1])

            while random.random() > 0.5:
                item = src.items.itemMap["Bolt"]()
                room.addItem(item,(random.randint(1,11),random.randint(1,11),0))

            if random.random() > 0.5:
                item = src.items.itemMap["MoldFeed"]()
                room.addItem(item,(random.randint(1,11),random.randint(1,11),0))

        # spawn special items
        endIndex = len(rooms)-3
        counter = 0
        for room in rooms+extraRooms:
            if counter == endIndex:
                item = src.items.itemMap["CoalBurner"]()
                room.addItem(item,(6,6,0))

            if self.difficulty != "difficult":
                if counter == endIndex+1:
                    item = src.items.itemMap["Shrine"]()
                    item.god = itemID
                    room.addItem(item,(6,6,0))

            if counter < endIndex or counter > endIndex+2:
                if random.random() > 0.5:
                    item = src.items.itemMap["StopStatue"]()
                    room.addItem(item,(6,6,0))

                    position = [(5,5,0),(5,6,0),(5,7,0),(6,5,0),(6,7,0)]
                    for pos in position:
                        item = src.items.itemMap["Wall"]()
                        room.addItem(item,pos)

            if not self.difficulty == "easy":
                """
                if counter < endIndex-2 or counter > endIndex+2:
                    if random.random() > 0.5:
                        for _i in range(random.randint(2,6)):
                            item = src.items.itemMap["LandMine"]()
                            room.addItem(item,(random.randint(1,11),random.randint(1,11),0))
                """

            counter += 1

        # spawn content of central chamber
        glassHeart = src.items.itemMap["GlassStatue"]()
        glassHeart.hasItem = True
        glassHeart.itemID = itemID
        mainRoom.addItem(glassHeart,(6,6,0))
        vial = src.items.itemMap["Vial"]()
        vial.uses = 10
        mainRoom.addItem(vial,(5,6,0))
        flask = src.items.itemMap["GooFlask"]()
        flask.uses = 100
        mainRoom.addItem(flask,(6,5,0))
        item = src.items.itemMap["Shrine"]()
        item.god = itemID
        mainRoom.addItem(item,(6,2,0))

        # add monsters outside of the dungeon
        for x in range(1,13):
            for y in range(1,13):
                if currentTerrain.getRoomByPosition((x,y,0)):
                    continue
                if random.random() < 0.7:
                    continue
                if x <= 9 and x >= 5:
                    continue
                if y <= 9 and y >= 5:
                    continue

                pos = (random.randint(1,11),random.randint(1,11),0)

                enemy = src.characters.characterMap["Monster"](4,4)
                enemy.baseDamage = 2+multiplier
                enemy.maxHealth = 20*multiplier
                enemy.health = enemy.maxHealth
                enemy.godMode = True
                enemy.movementSpeed = 1.1-random.random()/4

                quest = src.quests.questMap["SecureTile"](toSecure=(x,y,0))
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                currentTerrain.addCharacter(enemy, x*15+pos[0], y*15+pos[1])

    def roguelike_baseLeaderDeath(self,extraParam):
        text = ""

        character = extraParam["character"]
        faction = character.faction

        homePos = (character.registers["HOMETx"],character.registers["HOMETy"],0)
        homeTerrain = src.gamestate.gamestate.terrainMap[homePos[1]][homePos[0]]

        candidates = homeTerrain.characters[:]
        for room in homeTerrain.rooms:
            candidates.extend(room.characters)

        for candidate in candidates:
            if candidate == character:
                continue
            if candidate.faction != character.faction:
                continue
            if isinstance(candidate,src.characters.characterMap["Ghoul"]):
                continue
            candidate.runCommandString("~",clear=True)
            for quest in candidate.quests[:]:
                #quest.fail("taken over NPC")
                quest.autoSolve = False

            if self.difficulty == "tutorial":
                if candidate.maxHealth < character.maxHealth:
                    candidate.maxHealth = character.maxHealth
                    candidate.health = candidate.maxHealth
                candidate.baseDamage = character.baseDamage
                candidate.attackSpeed = character.attackSpeed
                candidate.movementSpeed = character.movementSpeed
                if not candidate.weapon:
                    weapon = src.items.itemMap["Sword"]()
                    weapon.baseDamage = 10
                    candidate.weapon = weapon

                if not candidate.armor:
                    armor = src.items.itemMap["Armor"]()
                    armor.armorValue = 1
                    candidate.armor = armor

            if self.difficulty == "difficult":
                candidate.health = int(candidate.health/2)
                candidate.maxHealth = int(candidate.maxHealth/2)
            candidate.addListener(self.roguelike_baseLeaderDeath,"died_pre")

            if character == src.gamestate.gamestate.mainChar:
                text += f"The last bit of your life force leaves and you die.\n"
                text += f"But something else leaves your implant as well.\n"
                text += f"It takes over another clone from your base.\n"
                text += f"\n- press enter to respawn -"
                src.interaction.showInterruptText(text)

                candidate.autoExpandQuests = src.gamestate.gamestate.mainChar.autoExpandQuests
                candidate.autoExpandQuests2 = src.gamestate.gamestate.mainChar.autoExpandQuests2
                candidate.disableCommandsOnPlus = src.gamestate.gamestate.mainChar.disableCommandsOnPlus
                candidate.personality = src.gamestate.gamestate.mainChar.personality
                candidate.duties = src.gamestate.gamestate.mainChar.duties
                candidate.dutyPriorities = src.gamestate.gamestate.mainChar.dutyPriorities

                src.gamestate.gamestate.mainChar = candidate

                questMenu = src.menuFolder.QuestMenu.QuestMenu(candidate)
                questMenu.sidebared = True
                candidate.rememberedMenu.append(questMenu)
                messagesMenu = src.menuFolder.MessagesMenu.MessagesMenu(candidate)
                candidate.rememberedMenu2.append(messagesMenu)
                inventoryMenu = src.menuFolder.InventoryMenu.InventoryMenu(candidate)
                inventoryMenu.sidebared = True
                candidate.rememberedMenu2.append(inventoryMenu)
                combatMenu = src.menuFolder.CombatInfoMenu.CombatInfoMenu(candidate)
                combatMenu.sidebared = True
                candidate.rememberedMenu.insert(0,combatMenu)

            for quest in candidate.quests[:]:
                quest.fail("aborted")
            candidate.quests = []
            self.reachImplant()
            self.activeStory["mainChar"] = candidate
            candidate.rank = 6

            candidate.addListener(self.enteredRoom,"entered room")
            candidate.addListener(self.itemPickedUp,"itemPickedUp")
            candidate.addListener(self.changedTerrain,"changedTerrain")
            candidate.addListener(self.deliveredSpecialItem,"deliveredSpecialItem")
            candidate.addListener(self.gotEpochReward,"got epoch reward")
            return

    def createStoryStart(self):
        homeTerrain = src.gamestate.gamestate.terrainMap[self.sternsBasePosition[1]][self.sternsBasePosition[0]]

        mainChar = src.characters.Character()
        mainChar.flask = src.items.itemMap["GooFlask"]()
        mainChar.flask.uses = 100
        mainChar.duties = ["praying","city planning","clone spawning",]
        mainChar.rank = 6
        mainChar.timeTaken = 1
        mainChar.runCommandString(".",nativeKey=True)

        mainChar.personality["viewChar"] = "name"
        mainChar.personality["viewColour"] = "name"

        thisFactionId = self.factionCounter
        mainChar.faction = f"city #{thisFactionId}"
        self.factionCounter += 1

        vial = src.items.itemMap["Vial"]()
        vial.uses = 1
        mainChar.inventory.append(vial)

        mainChar.registers["HOMETx"] = self.sternsBasePosition[0]
        mainChar.registers["HOMETy"] = self.sternsBasePosition[1]
        mainChar.registers["HOMEx"] = 7
        mainChar.registers["HOMEy"] = 7

        mainChar.personality["autoFlee"] = False
        mainChar.personality["abortMacrosOnAttack"] = False
        mainChar.personality["autoCounterAttack"] = False
        mainChar.addListener(self.roguelike_baseLeaderDeath,"died_pre")

        storyStartInfo = {}
        storyStartInfo["terrain"] = homeTerrain
        storyStartInfo["mainChar"] = mainChar
        storyStartInfo["type"] = "story start"

        startRoom = None
        for room in homeTerrain.rooms:
            if not room.tag == "sternslab":
                continue
            startRoom = room
        startRoom.addCharacter(mainChar,6,5)

        contraption = src.items.itemMap["SternsContraption"]()
        startRoom.addItem(contraption,(6,6,0))
        storyStartInfo["sternsContraption"] = contraption

        return storyStartInfo

    def openedQuests(self):
        if self.activeStory["type"] == "dungeon crawl":
            self.openedQuestsDungeonCrawl()
            return
        if self.activeStory["type"] == "travel":
            self.openedQuestsTravel()
            return
        if self.activeStory["type"] == "story start":
            self.openedQuestsStory()
            return
        1/0

    def openedQuestsStory(self):
        mainChar = self.activeStory["mainChar"]
        homeTerrain = src.gamestate.gamestate.terrainMap[mainChar.registers["HOMETy"]][mainChar.registers["HOMETx"]]
        
        # flee initial room
        if mainChar.container.tag == "sternslab":
            quest = src.quests.questMap["EscapeLab"]()
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            quest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        # heal
        # triggers at any time
        if mainChar.health < mainChar.maxHealth - 10:

            if len(mainChar.rememberedMenu2) < 2:
                inventoryMenu = src.menuFolder.InventoryMenu.InventoryMenu(mainChar)
                inventoryMenu.sidebared = True
                mainChar.rememberedMenu2.append(inventoryMenu)

            for item in mainChar.inventory:
                if item.type != "Vial":
                    continue
                if not item.uses:
                    continue
                quest = src.quests.questMap["TreatWounds"]()
                quest.assignToCharacter(mainChar)
                quest.activate()
                mainChar.assignQuest(quest,active=True)
                quest.endTrigger = {"container": self, "method": "reachImplant"}
                return

        # pick up nearby vials
        if mainChar.getFreeInventorySpace() > 0:
            if src.quests.questMap["TreatWounds"].getTileVials(mainChar):
                quest = src.quests.questMap["TreatWounds"]()
                quest.assignToCharacter(mainChar)
                quest.activate()
                mainChar.assignQuest(quest,active=True)
                quest.endTrigger = {"container": self, "method": "reachImplant"}
                return

        # assimilate into base
        if mainChar.faction != "city #1":
            terrain = mainChar.getTerrain()

            # grab nearby vial
            if mainChar.getBigPosition() == (6,9,0):
                vialTile = (6,8,0)

                # check for enemies on vial tile
                hasEnemy = False
                for character in terrain.charactersByTile.get(vialTile,[]):
                    if character.faction == mainChar.faction:
                        continue
                    hasEnemy = True

                # check for vial on vial tile
                hasVial = False
                rooms = terrain.getRoomByPosition(vialTile)
                if rooms:
                    items = rooms[0].itemsOnFloor
                else:
                    items = terrain.itemsByBigCoordinate.get(vialTile,[])
                for item in items:
                    if not item.type == "Vial":
                        continue
                    if not item.uses > 0:
                        continue
                    hasVial = True

                # fight for vial from tile
                if hasVial and hasEnemy:
                    quest = src.quests.questMap["SecureTile"](toSecure=vialTile,endWhenCleared=True,reason="be able to fetch the Vial from that tile",story="You reach out to your implant and it answers:\n\nThere is a Corpse and a Vial on the tile to the north.")
                    quest.assignToCharacter(mainChar)
                    quest.activate()
                    mainChar.assignQuest(quest,active=True)
                    quest.endTrigger = {"container": self, "method": "reachImplant"}
                    return

                # go to vial from tile
                if hasVial:
                    quest = src.quests.questMap["GoToTile"](targetPosition=vialTile,reason="be able to fetch the Vial from that tile",story="You reach out to your implant and it answers:\n\nThere is a Vial on the tile to the north.")
                    quest.assignToCharacter(mainChar)
                    quest.activate()
                    mainChar.assignQuest(quest,active=True)
                    quest.endTrigger = {"container": self, "method": "reachImplant"}
                    return

            # get to control room
            if not (mainChar.getBigPosition() in [(7,7,0),(7,8,0)]):
                quest = src.quests.questMap["ReachSafety"]()
                quest.assignToCharacter(mainChar)
                quest.activate()
                mainChar.assignQuest(quest,active=True)
                quest.endTrigger = {"container": self, "method": "reachImplant"}
                return

            # steal faction id
            quest = src.quests.questMap["ResetFaction"]()
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            quest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        # check for hunters
        hunterCount = 0
        ghulCount = 0
        for character in homeTerrain.characters:
            if character.charType == "Hunter":
                hunterCount += 1
            if character.charType == "Ghoul":
                ghulCount += 1
        for room in homeTerrain.rooms:

            for character in room.characters:
                if character.charType == "Hunter":
                    hunterCount += 1
                if character.charType == "Ghoul":
                    ghulCount += 1

        # keep trap rooms clean
        if not ghulCount:
            room = homeTerrain.getRoomByPosition((5,7,0))[0]
            for walkingSpace in room.walkingSpace:
                items = room.getItemByPosition(walkingSpace)
                for item in items:
                    if item.bolted:
                        continue

                    if not hunterCount:
                        # spawn trap cleaning ghul
                        quest = src.quests.questMap["SpawnGhul"]()
                        quest.assignToCharacter(mainChar)
                        quest.activate()
                        mainChar.assignQuest(quest,active=True)
                        quest.endTrigger = {"container": self, "method": "reachImplant"}
                        return

                    # clear room yourself
                    quest = src.quests.questMap["ClearTile"](description="clean up trap room",targetPosition=room.getPosition(),reason="clean the trap room.\n\nThe trap room relies on TriggerPlates to work.\nThose only work, if there are no items ontop of them.\nRestore the defence by removing the enemies remains.\nAvoid any enemies entering the trap room while you work",story="You reach out to your implant and it answers:\n\nThe main defenses of the base is the trap room,\nit needs to be cleaned to ensure it works correctly.")
                    quest.assignToCharacter(mainChar)
                    quest.activate()
                    mainChar.assignQuest(quest,active=True)
                    quest.endTrigger = {"container": self, "method": "reachImplant"}
                    return

        # wait out hunters
        if hunterCount:
            quest = src.quests.questMap["SecureTile"](toSecure=(6,7,0),endWhenCleared=False,reason="ensure no Hunters get into the base",story="You reach out to your implant and it answers:\n\nThere are still Hunters out there trying to kill you.\nIf you stay inside, they will get caught up in the Traproom.",lifetime=100,description="wait out Hunters")
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            quest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        # get the players environment
        terrain = mainChar.getTerrain()

        # ensure basic equipment
        if not mainChar.armor:
            for room in terrain.rooms:
                if room.getNonEmptyOutputslots(itemType="Armor",allowStorage=True,allowDesiredFilled=True):
                    quest = src.quests.questMap["Equip"](description="equip",reason="be able to defend yourself",story="You reach out to implant and it answers:\n")
                    quest.assignToCharacter(mainChar)
                    quest.activate()
                    mainChar.assignQuest(quest,active=True)
                    quest.endTrigger = {"container": self, "method": "reachImplant"}
                    return
        if not mainChar.weapon:
            for room in terrain.rooms:
                if room.getNonEmptyOutputslots(itemType="Sword",allowStorage=True,allowDesiredFilled=True):
                    quest = src.quests.questMap["Equip"](description="equip",reason="be able to defend yourself",story="You reach out to implant and it answers:\n")
                    quest.assignToCharacter(mainChar)
                    quest.activate()
                    mainChar.assignQuest(quest,active=True)
                    quest.endTrigger = {"container": self, "method": "reachImplant"}
                    return

        # count the number of enemies/allies
        npcCount = 0
        enemyCount = 0
        snatcherCount = 0
        for character in terrain.characters:
            if character.faction != "city #1":
                enemyCount += 1
                if character.charType == "Snatcher":
                    snatcherCount += 1
            else:
                if character.charType == "Ghoul":
                    continue
                npcCount += 1
        for room in terrain.rooms:
            for character in room.characters:
                if character.faction != "city #1":
                    enemyCount += 1
                else:
                    if character.charType == "Ghoul":
                        continue
                    npcCount += 1

        # kill snatchers
        if snatcherCount:
            quest = src.quests.questMap["SecureTile"](toSecure=(5,6,0),endWhenCleared=False,reason="confront the Snatchers",story="You reach out to your implant and it answers:\n\nThe base itself is safe now, but there are Snatchers out there.\nThey will try to swarm and kill everyone that goes outside.",lifetime=100)
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            quest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        # ensure there is a backup NPC
        if npcCount < 2:
            terrain = character.getTerrain()
            items = terrain.getRoomByPosition((7,8,0))[0].getItemByPosition((2,3,0))
            for item in items:
                if item.type != "GooFlask":
                    continue
                if item.uses < 100:
                    continue

                quest = src.quests.questMap["SpawnClone"]()
                quest.assignToCharacter(mainChar)
                quest.activate()
                mainChar.assignQuest(quest,active=True)
                quest.endTrigger = {"container": self, "method": "reachImplant"}
                return

        # ensure healing for the clones
        terrain = mainChar.getTerrain()
        for room in terrain.rooms:
            regenerator = room.getItemByType("Regenerator",needsBolted=True)
            if regenerator and not regenerator.activated:
                quest = src.quests.questMap["ActivateRegenerator"]()
                quest.assignToCharacter(mainChar)
                quest.activate()
                mainChar.assignQuest(quest,active=True)
                quest.endTrigger = {"container": self, "method": "reachImplant"}
                return

        # check for spider lairs
        terrain = mainChar.getTerrain()
        targets_found = []
        specialSpiderBlockersFound = []
        for x in range(1,14):
            for y in range(1,14):
                numSpiders = 0
                numSpiderlings = 0

                for otherChar in terrain.charactersByTile.get((x,y,0),[]):
                    if otherChar.charType == "Spider":
                        numSpiders += 1
                    if otherChar.charType == "Spiderling":
                        numSpiderlings += 1

                if numSpiders:
                    targets_found.append(("spider",(x,y,0),numSpiders))
                    pos = (5,8,0)
                    if (x,y,0) == pos:
                        specialSpiderBlockersFound = [pos]
                if numSpiderlings:
                    targets_found.append(("spiderling",(x,y,0),numSpiderlings))
        
        if targets_found:
            # clear first spider spot
            if specialSpiderBlockersFound:
                quest = src.quests.questMap["BaitSpiders"](targetPositionBig=specialSpiderBlockersFound[0])
                quest.assignToCharacter(mainChar)
                quest.activate()
                mainChar.assignQuest(quest,active=True)
                quest.endTrigger = {"container": self, "method": "reachImplant"}
                return

            # select target
            target = random.choice(targets_found)

            # clear spiders
            if target[0] == "spider":
                spider_lair_pos = target[1]
                    
                quest = src.quests.questMap["BaitSpiders"](targetPositionBig=spider_lair_pos)
                quest.assignToCharacter(mainChar)
                quest.activate()
                mainChar.assignQuest(quest,active=True)
                quest.endTrigger = {"container": self, "method": "reachImplant"}
                return

            # clear spiderlings
            if target[0] == "spiderling":
                spider_lair_pos = target[1]
                    
                quest = src.quests.questMap["SecureTile"](toSecure=spider_lair_pos,endWhenCleared=True)
                quest.assignToCharacter(mainChar)
                quest.activate()
                mainChar.assignQuest(quest,active=True)
                quest.endTrigger = {"container": self, "method": "reachImplant"}
                return

        # remove all enemies from terrain
        if enemyCount > 0:
            quest = src.quests.questMap["ClearTerrain"]()
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            quest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        # get promoted to base commander
        if mainChar.rank > 2:
            quest = src.quests.questMap["GetPromotion"](targetRank=mainChar.rank-1,reason="gain the rank of a base commmander")
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            quest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        # collect all glass heart
        for (godId,god) in src.gamestate.gamestate.gods.items():
            if (god["lastHeartPos"][0] == mainChar.registers["HOMETx"] and god["lastHeartPos"][1] == mainChar.registers["HOMETy"]):
                continue

            quest = src.quests.questMap["CollectGlassHearts"]()
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            quest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        # ascend to be supreme leader
        if mainChar.rank != 1:
            quest = src.quests.questMap["Ascend"]()
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            return

    def openedQuestsTravel(self):
        mainChar = self.activeStory["mainChar"]
        quest = src.quests.questMap["GoHome"]()
        quest.assignToCharacter(mainChar)
        quest.activate()
        mainChar.assignQuest(quest,active=True)
        quest.endTrigger = {"container": self, "method": "reachImplant"}

    def openedQuestsDungeonCrawl(self):
        mainChar = self.activeStory["mainChar"]

        terrain = self.activeStory["terrain"]
        pos = (terrain.xPosition,terrain.yPosition,0)

        god = src.gamestate.gamestate.gods[1]
        if god["home"] == god["lastHeartPos"]:
            storyText = """
You reach out to your implant and it answers:
It reminds you that have to fetch the glass heart from this dungeon.

The information popups will try to give you some rough directions about what you should be doing.
Not every interaction will be explained by popup, though.
Press ? and examine items for more information.

There is a lot to explain and the game has pretty complex systems.
This quest system is build to help you out with the details.
It will show you keys to press on the left side of the screen.
Press those keys when you are stuck.

Those keys are automatically generated and not optimal.
Once you understand things try to find better solutions.
"""
            quest = src.quests.questMap["DelveDungeon"](targetTerrain=pos,storyText=storyText)
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            quest.endTrigger = {"container": self, "method": "reachImplant"}
        else:
            quest = src.quests.questMap["BeUsefull"]()
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            quest.endTrigger = {"container": self, "method": "reachImplant"}

    def reachImplant(self):
        containerQuest = src.quests.questMap["ReachOutStory"]()
        src.gamestate.gamestate.mainChar.quests.append(containerQuest)
        containerQuest.activate()
        containerQuest.assignToCharacter(src.gamestate.gamestate.mainChar)
        src.gamestate.gamestate.mainChar.addMessage("reach out to implant by pressing q")
        containerQuest.endTrigger = {"container": self, "method": "openedQuests"}

    def checkDead(self):

        text = "epoch: {} tick: {}".format(src.gamestate.gamestate.tick//self.epochLength+1,src.gamestate.gamestate.tick%self.epochLength)
        self.wavecounterUI["text"] = "epoch: {} tick: {}".format(src.gamestate.gamestate.tick//self.epochLength+1,src.gamestate.gamestate.tick%self.epochLength)
        self.wavecounterUI["offset"] = (82-len(text)//2,5)

        if src.gamestate.gamestate.mainChar.dead:
            src.gamestate.gamestate.uiElements = [
                    {"type":"text","offset":(15,10), "text":"you were killed while holding against the siege"},
                    {"type":"text","offset":(15,12), "text":"you suvived {} ticks. That means wave no {} got you".format(src.gamestate.gamestate.tick,src.gamestate.gamestate.tick//1000+1,)},
                    ]
        else:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
            event.setCallback({"container": self, "method": "checkDead"})
            currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
            currentTerrain.addEvent(event)

    def startRound(self):

        self.numRounds += 1

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + self.epochLength)
        event.setCallback({"container": self, "method": "startRound"})

        terrain = src.gamestate.gamestate.terrainMap[7][7]
        terrain.addEvent(event)

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

    phasesByName["MainGame"] = MainGame
    phasesByName["PrefabDesign"] = PrefabDesign
