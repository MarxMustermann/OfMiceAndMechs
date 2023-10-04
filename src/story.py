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
        submenu = src.interaction.TextMenu(f"""
your room produces a MetalBar every {ticksPerBar} ticks on average.""")

        src.gamestate.gamestate.mainChar.macroState["submenue"] = submenu

    def spawnMaintanenceNPCs(self,room=None):
        if not room:
            room = self.toBuildRoomClone5

        charCount = 0
        for character in room.characters:
            if isinstance(character,src.characters.Ghoul):
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
            if isinstance(npc,src.characters.Ghoul):
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
        if src.gamestate.gamestate.mainChar.health != 100:
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

            quest = src.quests.questMap["SecureTile"](toSecure=charPos)
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

    def start(self, seed=0, difficulty=None):
        """
        set up terrain and spawn main character

        Parameters:
            seed: rng seed
        """

        self.epochLength = 15*15*15
        self.factionCounter = 1

        self.specialItemMap = {}

        self.difficulty = difficulty
        self.productionBaseInfos = []
        positions = [(7,6,0),(7,8,0),(6,7,0),(8,7,0),(7,7,0),(8,8,0)]
        positions = [(2,2,0),(2,3,0),(2,4,0),(2,5,0),(2,6,0),(2,7,0),(12,12,0)]
        #self.productionBaseInfos.append(self.createProductiondBase(positions.pop()))

        self.siegedBaseInfos = []
        #self.siegedBaseInfos.append(self.createSiegedBase(positions.pop()))

        self.raidBaseInfos = []
        #self.raidBaseInfos.append(self.createRaidBase(positions.pop()))

        self.colonyBaseInfos = []
        #self.colonyBaseInfos.append(self.createColonyBase(positions.pop()))

        self.colonyBaseInfos2 = []
        #self.colonyBaseInfos.append(self.createColonyBase(positions.pop()))

        if self.preselection == "Siege":
            self.siegedBaseInfos.append(self.createSiegedBase(positions.pop()))
            self.activeStory = random.choice(self.siegedBaseInfos)
        elif self.preselection == "Production":
            self.productionBaseInfos.append(self.createProductionBase(positions.pop()))
            self.activeStory = random.choice(self.productionBaseInfos)
        elif self.preselection == "Raid":
            self.raidBaseInfos.append(self.createRaidBase(positions.pop()))
            self.activeStory = random.choice(self.raidBaseInfos)
        else:
            self.colonyBaseInfos2.append(self.createColonyBase2((6,6),mainCharBase=True))
            self.colonyBaseInfos2.append(self.createColonyBase2((8,6)))
            #self.siegedBaseInfos.append(self.createSiegedBase((6,6)))

            #self.colonyBaseInfos2.append(self.createColonyBase2((4,4)))
            #self.colonyBaseInfos2.append(self.createColonyBase2((4,5)))
            #self.colonyBaseInfos2.append(self.createColonyBase2((4,6)))
            #self.colonyBaseInfos2.append(self.createColonyBase2((4,7)))
            #self.colonyBaseInfos2.append(self.createColonyBase2((4,8)))

            #self.colonyBaseInfos2.append(self.createColonyBase2((3,4)))
            #self.colonyBaseInfos2.append(self.createColonyBase2((3,5)))
            #self.colonyBaseInfos2.append(self.createColonyBase2((3,6)))
            #self.colonyBaseInfos2.append(self.createColonyBase2((3,7)))
            #self.colonyBaseInfos2.append(self.createColonyBase2((3,8)))

            #self.colonyBaseInfos2.append(self.createColonyBase2((2,4)))
            #self.colonyBaseInfos2.append(self.createColonyBase2((2,5)))
            #self.colonyBaseInfos2.append(self.createColonyBase2((2,6)))

            #self.setUpThroneDungeon((7,7))
            self.setUpGlassHeartDungeon((7,6),3,1)
            self.setUpGlassHeartDungeon((7,5),4,1)
            self.setUpGlassHeartDungeon((7,4),5,2)
            self.setUpGlassHeartDungeon((7,3),6,2)
            self.setUpGlassHeartDungeon((7,2),7,3)
            self.setUpGlassHeartDungeon((7,7),2,3)
            self.setUpGlassHeartDungeon((7,8),1,4)
            self.activeStory = self.colonyBaseInfos2[0]
            """
        else:
            self.colonyBaseInfos.append(self.createColonyBase((6,7),mainCharBase=True))
            self.colonyBaseInfos.append(self.createColonyBase((5,7)))
            self.setUpThroneDungeon((7,7))
            self.activeStory = self.colonyBaseInfos[0]
        """

        for story in self.productionBaseInfos+self.siegedBaseInfos+self.raidBaseInfos:
            story["epochArtwork"].setSpecialItemMap(self.specialItemMap)

        mainChar = self.activeStory["mainChar"]
        src.gamestate.gamestate.mainChar = mainChar
        mainChar.addListener(self.mainCharacterDeath,"died")

        self.wavecounterUI = {"type":"text","offset":(72,5), "text":"wavecounter"}
        src.gamestate.gamestate.uiElements.append(self.wavecounterUI)

        questMenu = src.interaction.QuestMenu(mainChar)
        questMenu.sidebared = True
        mainChar.rememberedMenu.append(questMenu)
        messagesMenu = src.interaction.MessagesMenu(mainChar)
        mainChar.rememberedMenu2.append(messagesMenu)
        inventoryMenu = src.interaction.InventoryMenu(mainChar)
        inventoryMenu.sidebared = True
        mainChar.rememberedMenu2.append(inventoryMenu)

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
        if self.activeStory["type"] == "colonyBase":
            text = f"""
    You died.

    you were playing the scenario: {self.activeStory["type"]}

    - press enter to continue -
"""
        else:
            text = f"""
    You died.

    you were playing the scenario: {self.activeStory["type"]}

    - press enter to continue -
"""
        src.interaction.showInterruptText(text)

        if self.activeStory["type"] == "colonyBase":
            characterPool = []
            terrain = self.activeStory["terrain"]
            characterPool.extend(terrain.characters)

            for room in terrain.rooms:
                characterPool.extend(room.characters)

            for character in characterPool[:]:
                if character.faction != self.activeStory["mainChar"].faction:
                    characterPool.remove(character)
                    continue
                if isinstance(character,src.characters.Ghoul):
                    characterPool.remove(character)
                    continue
                if not character.rank:
                    characterPool.remove(character)
                    continue

            if not characterPool:
                text = """
    no remainder of your faction found. You lost the game.

    - press enter to exit the game -
"""
                src.interaction.showInterruptText(text)
                raise SystemExit()

            text = """
    You respawn as another member of your faction.
"""
            src.interaction.showInterruptText(text)

            newChar = random.choice(characterPool)
            src.gamestate.gamestate.mainChar = newChar
            newChar.addListener(self.mainCharacterDeath,"died")

            newChar.runCommandString("",clear=True)
            for quest in newChar.quests:
                quest.autoSolve = False
            newChar.disableCommandsOnPlus = True
        else:
            raise SystemExit()

    def kickoff(self):
        if self.activeStory["type"] == "siegedBase":
            self.activeStory["mainChar"].messages.insert(0,("""until the explosions fully wake you."""))
        elif self.activeStory["type"] == "raidBase":
            self.activeStory["mainChar"].messages.insert(0,("""until you notice eneryone looking at you expectingly."""))
        elif self.activeStory["type"] == "colonyBase":
            if len(self.activeStory["mainChar"].messages) == 0:
                text = """
You.
You see walls made out of solid steel
and feel the touch of the cold hard floor.
The room is filled with various items.
You recognise your hostile suroundings and
try to remember how you got here ..."""
                self.activeStory["mainChar"].messages.insert(0,(text))
            self.activeStory["mainChar"].messages.insert(0,("""until you remember that you are supposed to set up a new base."""))
        elif self.activeStory["type"] == "productionBase":
            self.kickoffProduction()
        else:
            pass

    def kickoffProduction(self):
        self.activeStory["playerActivatedEpochArtwork"] = False
        self.activeStory["mainChar"].messages.insert(0,("""but see nothing that could directly harm you."""))

        for character in self.activeStory["terrain"].characters[:]:
            if character != self.activeStory["mainChar"]:
                character.die(reason="sudden death")

        for room in self.activeStory["terrain"].rooms:
            if isinstance(room, src.rooms.TrapRoom):
                room.electricalCharges = 0
            for character in room.characters[:]:
                if character != self.activeStory["mainChar"]:
                    character.die(reason="sudden death")
            for item in room.itemsOnFloor[:]:
                if item.bolted:
                    continue
                room.removeItem(item)

    def advanceProductionBase(self,state):
        """
        personnelArtwork = state["personnelArtwork"]
        mainChar = state["mainChar"]

        amountNPCs = 2
        personnelArtwork.charges += amountNPCs*2
        for i in range(0,amountNPCs):
            npc = personnelArtwork.spawnIndependentClone(mainChar)
        """

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

                enemy = src.characters.Monster(4,4)
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

    def setUpGlassHeartDungeon(self,pos,itemID,multiplier):
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
                       "doors": "6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )

        rooms = []
        room = architect.doAddRoom(
                {
                       "coordinate": (7,8),
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
                       "coordinate": (8,8),
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
                       "coordinate": (8,7),
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
                       "coordinate": (8,6),
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
                       "coordinate": (7,6),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 12,6",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )
        rooms.append(room)
        room = architect.doAddRoom(
                {
                       "coordinate": (6,6),
                       "roomType": "EmptyRoom",
                       "doors": "6,12 12,6",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )
        rooms.append(room)
        room = architect.doAddRoom(
                {
                       "coordinate": (6,7),
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
                       "coordinate": (5,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 12,6",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )
        rooms.append(room)
        room = architect.doAddRoom(
                {
                       "coordinate": (4,7),
                       "roomType": "EmptyRoom",
                       "doors": "0,6 12,6",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None,
           )
        rooms.append(room)

        counter = 0
        for room in reversed(rooms):
            #for i in range(1,2+counter//3):
            for _i in range(1,2):
                pos = (random.randint(1,11),random.randint(1,11),0)

                enemy = src.characters.Monster(4,4)
                enemy.baseDamage = 5+multiplier
                enemy.maxHealth = (20+10*counter)*multiplier
                enemy.health = enemy.maxHealth
                enemy.godMode = True
                enemy.movementSpeed = 1.3-0.1*multiplier
                enemy.charType = "Statue"

                quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition())
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                room.addCharacter(enemy, pos[0], pos[1])
            counter += 1

        glassHeart = src.items.itemMap["GlassStatue"]()
        glassHeart.hasItem = True
        glassHeart.itemID = itemID
        mainRoom.addItem(glassHeart,(6,6,0))

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

                enemy = src.characters.Monster(4,4)
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


    def createColonyBase(self,pos,mainCharBase=False):
        mainChar = src.characters.Character()
        if mainCharBase:
            mainChar.disableCommandsOnPlus = True
        mainChar.questsDone = [
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
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

        if not mainCharBase:
            quest = src.quests.questMap["BeUsefull"]()
            #quest = src.quests.questMap["ExtendBase"]()
            quest.autoSolve = True
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            mainChar.foodPerRound = 1

        thisFactionId = self.factionCounter
        mainChar.faction = f"city #{thisFactionId}"
        mainChar.registers["HOMEx"] = 7
        mainChar.registers["HOMEy"] = 7
        mainChar.registers["HOMETx"] = pos[0]
        mainChar.registers["HOMETy"] = pos[1]
        mainChar.foodPerRound = 1
        mainChar.personality["viewChar"] = "name"
        mainChar.personality["viewColour"] = "name"
        self.factionCounter += 1
        colonyBaseInfo = {"type":"colonyBase"}
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        colonyBaseInfo["terrain"] = currentTerrain
        colonyBaseInfo["mainChar"] = mainChar

        if mainCharBase:
            mainChar.personality["autoFlee"] = False
            mainChar.personality["abortMacrosOnAttack"] = False
            mainChar.personality["autoCounterAttack"] = False

        mainChar.flask = src.items.itemMap["GooFlask"]()
        mainChar.flask.uses = 100
        mainChar.duties = ["city planning","clone spawning","questing","painting","machine placing","room building","metal working","machining","hauling","resource fetching","scrap hammering","resource gathering","machine operation"]
        if mainCharBase:
            mainChar.duties.insert(0,"tutorial")

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

        mainRoom.addCharacter(
            mainChar, 6, 6
        )

        item = src.items.itemMap["SpecialItemSlot"]()
        item.itemID = 1
        if mainCharBase:
            item.hasItem = True
        mainRoom.addItem(item,(1,3,0))
        item = src.items.itemMap["SpecialItemSlot"]()
        if not mainCharBase:
            item.hasItem = True
        item.itemID = 2
        mainRoom.addItem(item,(2,3,0))

        #epochArtwork = src.items.itemMap["EpochArtwork"](self.epochLength,rewardSet="colony")
        #colonyBaseInfo["epochArtwork"] = epochArtwork
        #epochArtwork.leader = mainChar
        #epochArtwork.epochSurvivedRewardAmount = 0
        #epochArtwork.changeCharges(60)
        #mainRoom.addItem(epochArtwork,(3,3,0))
        mainChar.rank = 3
        """
        quest = src.quests.questMap["EpochQuest"]()
        mainChar.assignQuest(quest,active=True)

        #cityBuilder = src.items.itemMap["CityBuilder2"]()
        #cityBuilder.architect = architect
        #mainRoom.addItem(cityBuilder,(7,1,0))
        #cityBuilder.registerRoom(mainRoom)

        """

        dutyArtwork = src.items.itemMap["DutyArtwork"]()
        mainRoom.addItem(dutyArtwork,(5,1,0))

        anvilPos = (10,2,0)
        machinemachine = src.items.itemMap["Anvil"]()
        mainRoom.addItem(machinemachine,(anvilPos[0],anvilPos[1],0))
        mainRoom.addInputSlot((anvilPos[0]-1,anvilPos[1],0),"Scrap")
        mainRoom.addInputSlot((anvilPos[0]+1,anvilPos[1],0),"Scrap")
        mainRoom.addOutputSlot((anvilPos[0],anvilPos[1]-1,0),None)
        mainRoom.walkingSpace.add((anvilPos[0],anvilPos[1]+1,0))

        metalWorkBenchPos = (8,3,0)
        machinemachine = src.items.itemMap["MetalWorkingBench"]()
        mainRoom.addItem(machinemachine,(metalWorkBenchPos[0],metalWorkBenchPos[1],0))
        mainRoom.addInputSlot((metalWorkBenchPos[0]+1,metalWorkBenchPos[1],0),"MetalBars")
        mainRoom.addOutputSlot((metalWorkBenchPos[0],metalWorkBenchPos[1]-1,0),None)
        mainRoom.addOutputSlot((metalWorkBenchPos[0],metalWorkBenchPos[1]+1,0),None)
        mainRoom.walkingSpace.add((metalWorkBenchPos[0]-1,metalWorkBenchPos[1],0))

        anvilPos = (9,5,0)
        machinemachine = src.items.itemMap["MachiningTable"]()
        mainRoom.addItem(machinemachine,(anvilPos[0],anvilPos[1],0))
        mainRoom.addInputSlot((anvilPos[0]-1,anvilPos[1],0),"MetalBars")
        mainRoom.addInputSlot((anvilPos[0]+1,anvilPos[1],0),"MetalBars")
        mainRoom.addOutputSlot((anvilPos[0],anvilPos[1]-1,0),None)
        mainRoom.walkingSpace.add((anvilPos[0],anvilPos[1]+1,0))

        for y in (7,9,11):
            for x in range(7,12):
                mainRoom.addStorageSlot((x,y,0),None)
            for x in range(1,6):
                mainRoom.addStorageSlot((x,y,0),None)

        for y in (11,9,):
            for x in range(7,12):
                item = src.items.itemMap["Wall"]()
                item.bolted = False
                mainRoom.addItem(item,(x,y,0))
            for x in range(1,6):
                item = src.items.itemMap["Wall"]()
                item.bolted = False
                mainRoom.addItem(item,(x,y,0))

        item = src.items.itemMap["Door"]()
        item.bolted = False
        mainRoom.addItem(item,(1,7,0))
        item = src.items.itemMap["Door"]()
        item.bolted = False
        mainRoom.addItem(item,(2,7,0))
        item = src.items.itemMap["Door"]()
        item.bolted = False
        mainRoom.addItem(item,(3,7,0))
        item = src.items.itemMap["Door"]()
        item.bolted = False
        mainRoom.addItem(item,(4,7,0))
        item = src.items.itemMap["RoomBuilder"]()
        item.bolted = False
        mainRoom.addItem(item,(5,7,0))

        for x in range(1,6):
            mainRoom.walkingSpace.add((x,10,0))
        for x in range(7,12):
            mainRoom.walkingSpace.add((x,10,0))

        for x in range(1,6):
            mainRoom.walkingSpace.add((x,6,0))
        for x in range(7,12):
            mainRoom.walkingSpace.add((x,6,0))
        mainRoom.walkingSpace.add((5,3,0))
        mainRoom.walkingSpace.add((4,3,0))
        mainRoom.walkingSpace.add((4,2,0))
        mainRoom.walkingSpace.add((3,2,0))
        mainRoom.walkingSpace.add((2,2,0))
        mainRoom.walkingSpace.add((1,2,0))
        mainRoom.walkingSpace.add((4,4,0))
        mainRoom.walkingSpace.add((3,4,0))
        mainRoom.walkingSpace.add((2,4,0))
        mainRoom.walkingSpace.add((1,4,0))
        mainRoom.walkingSpace.add((7,5,0))
        mainRoom.walkingSpace.add((7,4,0))
        mainRoom.walkingSpace.add((7,2,0))
        mainRoom.walkingSpace.add((7,1,0))
        mainRoom.walkingSpace.add((8,1,0))
        mainRoom.walkingSpace.add((9,1,0))
        mainRoom.walkingSpace.add((11,5,0))
        mainRoom.walkingSpace.add((11,4,0))
        mainRoom.walkingSpace.add((11,3,0))
        mainRoom.walkingSpace.add((10,4,0))

        for y in range(1,12):
            mainRoom.walkingSpace.add((6,y,0))

        # scatter items around
        for _i in range(20):
            item = src.items.itemMap["ScrapCompactor"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(75):
            item = src.items.itemMap["Case"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(200):
            item = src.items.itemMap["MetalBars"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(25):
            item = src.items.itemMap["Frame"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(25):
            item = src.items.itemMap["Rod"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(50):
            item = src.items.itemMap["Wall"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(50):
            item = src.items.itemMap["Wall"]()
            item.bolted = False
            pos = (random.randint(15*5,15*10),random.randint(15*5,15*10),0)
            currentTerrain.addItem(item,pos)
        for _i in range(10):
            bigPos = None
            for _j in range(10):
                pos = (random.randint(1,13),random.randint(1,13),0)
                if (pos[0] < 11 and pos[0] > 4) and (pos[1] < 11 and pos[1] > 4):
                    continue
                bigPos = pos
                break

            if not bigPos:
                break

            for _j in range(20):
                item = src.items.itemMap["Wall"]()
                item.bolted = False
                pos = (random.randint(bigPos[0]*15+1,bigPos[0]*15+14),random.randint(bigPos[1]*15+1,bigPos[1]*15+14),0)
                currentTerrain.addItem(item,pos)

            enemy = src.characters.Monster(4,4)
            enemy.health = 20
            enemy.baseDamage = 5
            enemy.maxHealth = 20
            enemy.godMode = True
            enemy.movementSpeed = 0.8

            quest = src.quests.questMap["SecureTile"](toSecure=(bigPos[0],bigPos[1],0))
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

            currentTerrain.addCharacter(enemy, bigPos[0]*15+7, bigPos[1]*15+7)

        for bigPos in [(4,4,0),(10,4,0),(4,10,0),(10,10,0)]:
            for _i in range(20):
                item = src.items.itemMap["Wall"]()
                item.bolted = False
                pos = (random.randint(bigPos[0]*15+1,bigPos[0]*15+14),random.randint(bigPos[1]*15+1,bigPos[1]*15+14),0)
                currentTerrain.addItem(item,pos)

            enemy = src.characters.Monster(4,4)
            enemy.health = 20
            enemy.baseDamage = 5
            enemy.maxHealth = 20
            enemy.godMode = True
            enemy.movementSpeed = 0.8

            quest = src.quests.questMap["SecureTile"](toSecure=(bigPos[0],bigPos[1],0))
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

            currentTerrain.addCharacter(enemy, bigPos[0]*15+7, bigPos[1]*15+7)

        for _i in range(40):
            item = src.items.itemMap["Door"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)

        for pos in ((6,7,0),(7,6,0),(8,7,0),(7,8,0)):
            architect.doClearField(pos[0], pos[1])

        # spawn enemies
        for x in range(1,14):
            for y in range(1,14):
                if (x < 12 and x > 2) and (y < 12 and y > 2):
                    continue

                enemy = src.characters.Monster(4,4)
                enemy.health = 20
                enemy.baseDamage = 5
                enemy.maxHealth = 20
                enemy.godMode = True
                enemy.movementSpeed = 0.8

                quest = src.quests.questMap["SecureTile"](toSecure=(x,y,0))
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                currentTerrain.addCharacter(enemy, x*15+7, y*15+7)

        pos = random.choice([(6,6,0),(8,6,0),(8,8,0),(6,8,0)])
        architect.doClearField(pos[0], pos[1])
        tree = src.items.itemMap["Tree"]()
        tree.numMaggots = tree.maxMaggot
        currentTerrain.addItem(tree,(pos[0]*15+7,pos[1]*15+7,0))
        currentTerrain.forests.append(pos)

        positions = [(7,4),(8,5),(9,6),(10,7),(9,8),(8,9),(7,10),(6,9),(5,8),(5,6),(6,5),(7,4)]
        positions = [random.choice(positions)]
        for pos in positions:
            architect.doClearField(pos[0], pos[1])
            architect.doAddScrapfield(pos[0], pos[1], 100,leavePath=True)

        positions = [(7,6),(6,7),(7,8),(8,7),]
        positions = [random.choice(positions)]
        for pos in positions:
            architect.doClearField(pos[0], pos[1])
            architect.doAddScrapfield(pos[0], pos[1], 20,leavePath=True)

        itemsToRemove = []
        for x in range(1,14):
            for y in range(1,14):
                clearPositions = [(7,1,0),(7,2,0),(1,7,0),(2,7,0),(7,13,0),(7,12,0),(13,7,0),(12,7,0)]
                for clearPosition in clearPositions:
                    itemsToRemove.extend(currentTerrain.getItemByPosition((x*15+clearPosition[0],y*15+clearPosition[1],0)))
        currentTerrain.removeItems(itemsToRemove)

        return colonyBaseInfo

    def createColony_baseLeaderDeath(self,extraParam):
        faction = extraParam["character"].faction
        if faction == src.gamestate.gamestate.mainChar.faction:
            text = f"The leader of your faction {faction} died"
            src.interaction.showInterruptText(text)

        for colonyBaseInfo in self.colonyBaseInfos2:
            if colonyBaseInfo["mainChar"] != extraParam["character"]:
                continue

            candidates = []
            candidates.extend(colonyBaseInfo["terrain"].characters)
            for room in colonyBaseInfo["terrain"].rooms:
                candidates.extend(room.characters)

            for candidate in candidates[:]:
                if candidate.dead:
                    candidates.remove(candidate)
                    continue
                if candidate.health == 0:
                    candidates.remove(candidate)
                    continue
                if candidate.faction != faction:
                    candidates.remove(candidate)
                    continue
                if candidate == extraParam["character"]:
                    candidates.remove(candidate)
                    continue

            bestCandidate = None
            for candidate in candidates:
                if not bestCandidate:
                    bestCandidate = candidate

                if candidate.reputation > bestCandidate.reputation:
                    bestCandidate = candidate

            if not bestCandidate:
                text = "the faction was wiped out"
                src.interaction.showInterruptText(text)
                return

            if faction == src.gamestate.gamestate.mainChar.faction:
                text = f"{bestCandidate.name} takes over"
                src.interaction.showInterruptText(text)
            if bestCandidate == src.gamestate.gamestate.mainChar:
                text = "you take over"
                src.interaction.showInterruptText(text)

            for subordinate in colonyBaseInfo["mainChar"].subordinates:
                if subordinate == bestCandidate:
                    continue
                subordinate.superior = bestCandidate
                bestCandidate.subordinates.append(subordinate)

            if not bestCandidate.rank:
                bestCandidate.rank = 6
            bestCandidate.duties = ["praying","city planning","clone spawning","questing","painting","machine placing","room building","metal working","machining","hauling","resource fetching","scrap hammering","resource gathering","machine operation"]
            bestCandidate.addListener(self.createColony_baseLeaderDeath,"died_pre")
            colonyBaseInfo["mainChar"] = bestCandidate

            for quest in bestCandidate.quests:
                quest.fail()
            bestCandidate.quests = []

            quest = src.quests.questMap["BeUsefull"]()
            quest.autoSolve = True
            quest.assignToCharacter(bestCandidate)
            quest.activate()
            bestCandidate.assignQuest(quest,active=True)
            bestCandidate.foodPerRound = 1
            bestCandidate.superior = None

    def createColonyBase2(self,pos,mainCharBase=False):
        mainChar = src.characters.Character()
        mainChar.addListener(self.createColony_baseLeaderDeath,"died_pre")
        if mainCharBase:
            mainChar.disableCommandsOnPlus = True
        mainChar.questsDone = [
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
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

        if not mainCharBase:
            quest = src.quests.questMap["BeUsefull"]()
            #quest = src.quests.questMap["ExtendBase"]()
            quest.autoSolve = True
            quest.assignToCharacter(mainChar)
            quest.activate()
            mainChar.assignQuest(quest,active=True)
            mainChar.foodPerRound = 1

        thisFactionId = self.factionCounter
        mainChar.faction = f"city #{thisFactionId}"
        mainChar.registers["HOMEx"] = 7
        mainChar.registers["HOMEy"] = 7
        mainChar.registers["HOMETx"] = pos[0]
        mainChar.registers["HOMETy"] = pos[1]
        mainChar.foodPerRound = 1
        mainChar.personality["viewChar"] = "name"
        mainChar.personality["viewColour"] = "name"
        self.factionCounter += 1
        colonyBaseInfo = {"type":"colonyBase"}
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        currentTerrain.maxMana = 100
        currentTerrain.manaRegen = 5
        currentTerrain.mana = 60
        colonyBaseInfo["terrain"] = currentTerrain
        colonyBaseInfo["mainChar"] = mainChar

        if mainCharBase:
            mainChar.personality["autoFlee"] = False
            mainChar.personality["abortMacrosOnAttack"] = False
            mainChar.personality["autoCounterAttack"] = False

        mainChar.flask = src.items.itemMap["GooFlask"]()
        mainChar.flask.uses = 100
        mainChar.duties = ["praying","city planning","clone spawning","questing","painting","machine placing","room building","metal working","hauling","resource fetching","scrap hammering","resource gathering","machine operation"]

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
        """
        testRoom = architect.doAddRoom(
                {
                       "coordinate": (6,7),
                       "roomType": "EmptyRoom",
                       "doors": "2,4",
                       "offset": [1,1],
                       "size": [5, 5],
                },
                None,
            )
        roomControls = src.items.itemMap["RoomControls"]()
        testRoom.addItem(roomControls,(1,1,0))
        testRoom.engineStrength = 100
        testRoom2 = architect.doAddRoom(
                {
                       "coordinate": (5,7),
                       "roomType": "EmptyRoom",
                       "doors": "2,4",
                       "offset": [1,1],
                       "size": [5, 5],
                },
                None,
            )
        """

        mainRoom.addCharacter(
            mainChar, 6, 6
        )

        #epochArtwork = src.items.itemMap["EpochArtwork"](self.epochLength,rewardSet="colony")
        #colonyBaseInfo["epochArtwork"] = epochArtwork
        #epochArtwork.leader = mainChar
        #epochArtwork.epochSurvivedRewardAmount = 0
        #epochArtwork.changeCharges(60)
        #mainRoom.addItem(epochArtwork,(3,1,0))
        mainChar.rank = 6
        """
        quest = src.quests.questMap["EpochQuest"]()
        mainChar.assignQuest(quest,active=True)

        #cityBuilder = src.items.itemMap["CityBuilder2"]()
        #cityBuilder.architect = architect
        #mainRoom.addItem(cityBuilder,(7,1,0))
        #cityBuilder.registerRoom(mainRoom)
        """

        dutyArtwork = src.items.itemMap["DutyArtwork"]()
        mainRoom.addItem(dutyArtwork,(5,1,0))

        shrine = src.items.itemMap["Shrine"](god=1)
        mainRoom.addItem(shrine,(1,1,0))

        shrine = src.items.itemMap["Shrine"](god=2)
        mainRoom.addItem(shrine,(2,1,0))

        personnelArtwork = src.items.itemMap["PersonnelArtwork"]()
        personnelArtwork.charges = 10
        mainRoom.addItem(personnelArtwork,(1,8,0))

        anvilPos = (10,2,0)
        machinemachine = src.items.itemMap["Anvil"]()
        mainRoom.addItem(machinemachine,(anvilPos[0],anvilPos[1],0))
        mainRoom.addInputSlot((anvilPos[0]-1,anvilPos[1],0),"Scrap")
        mainRoom.addInputSlot((anvilPos[0]+1,anvilPos[1],0),"Scrap")
        mainRoom.addOutputSlot((anvilPos[0],anvilPos[1]-1,0),None)
        mainRoom.walkingSpace.add((anvilPos[0],anvilPos[1]+1,0))

        metalWorkBenchPos = (8,3,0)
        machinemachine = src.items.itemMap["MetalWorkingBench"]()
        mainRoom.addItem(machinemachine,(metalWorkBenchPos[0],metalWorkBenchPos[1],0))
        mainRoom.addInputSlot((metalWorkBenchPos[0]+1,metalWorkBenchPos[1],0),"MetalBars")
        mainRoom.addOutputSlot((metalWorkBenchPos[0],metalWorkBenchPos[1]-1,0),None)
        mainRoom.addOutputSlot((metalWorkBenchPos[0],metalWorkBenchPos[1]+1,0),None)
        mainRoom.walkingSpace.add((metalWorkBenchPos[0]-1,metalWorkBenchPos[1],0))

        anvilPos = (9,5,0)
        machinemachine = src.items.itemMap["MachiningTable"]()
        mainRoom.addItem(machinemachine,(anvilPos[0],anvilPos[1],0))
        mainRoom.addInputSlot((anvilPos[0]-1,anvilPos[1],0),"MetalBars")
        mainRoom.addInputSlot((anvilPos[0]+1,anvilPos[1],0),"MetalBars")
        mainRoom.addOutputSlot((anvilPos[0],anvilPos[1]-1,0),None)
        mainRoom.walkingSpace.add((anvilPos[0],anvilPos[1]+1,0))

        for y in (7,9,11):
            if y != 7:
                for x in range(7,12):
                    mainRoom.addStorageSlot((x,y,0),None)
            for x in range(1,6):
                mainRoom.addStorageSlot((x,y,0),None)

        for y in (11,9,):
            for x in range(7,12):
                item = src.items.itemMap["Wall"]()
                item.bolted = False
                mainRoom.addItem(item,(x,y,0))
            for x in range(1,6):
                item = src.items.itemMap["Wall"]()
                item.bolted = False
                mainRoom.addItem(item,(x,y,0))

        item = src.items.itemMap["Door"]()
        item.bolted = False
        mainRoom.addItem(item,(1,7,0))
        item = src.items.itemMap["Door"]()
        item.bolted = False
        mainRoom.addItem(item,(2,7,0))
        item = src.items.itemMap["Door"]()
        item.bolted = False
        mainRoom.addItem(item,(3,7,0))
        item = src.items.itemMap["Door"]()
        item.bolted = False
        mainRoom.addItem(item,(4,7,0))
        item = src.items.itemMap["RoomBuilder"]()
        item.bolted = False
        mainRoom.addItem(item,(5,7,0))

        item = src.items.itemMap["ProductionArtwork"]()
        item.bolted = True
        item.charges = 1
        mainRoom.addItem(item,(4,3,0))

        item = src.items.itemMap["MachineMachine"]()
        item.bolted = True
        mainRoom.addItem(item,(4,5,0))

        item = src.items.itemMap["BluePrinter"]()
        item.bolted = True
        mainRoom.addItem(item,(2,4,0))

        for x in range(1,6):
            mainRoom.walkingSpace.add((x,10,0))
        for x in range(7,12):
            mainRoom.walkingSpace.add((x,10,0))

        for x in range(1,6):
            mainRoom.walkingSpace.add((x,6,0))
        for x in range(7,12):
            mainRoom.walkingSpace.add((x,6,0))
        mainRoom.walkingSpace.add((5,2,0))
        mainRoom.walkingSpace.add((4,2,0))
        mainRoom.walkingSpace.add((3,2,0))
        mainRoom.walkingSpace.add((2,2,0))
        mainRoom.walkingSpace.add((1,2,0))
        mainRoom.walkingSpace.add((7,5,0))
        mainRoom.walkingSpace.add((7,4,0))
        mainRoom.walkingSpace.add((7,2,0))
        mainRoom.walkingSpace.add((7,1,0))
        mainRoom.walkingSpace.add((8,1,0))
        mainRoom.walkingSpace.add((9,1,0))
        mainRoom.walkingSpace.add((11,5,0))
        mainRoom.walkingSpace.add((11,4,0))
        mainRoom.walkingSpace.add((11,3,0))
        mainRoom.walkingSpace.add((10,4,0))

        for y in range(1,12):
            mainRoom.walkingSpace.add((6,y,0))

        # scatter items around
        for _i in range(20):
            item = src.items.itemMap["ScrapCompactor"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(75):
            item = src.items.itemMap["Case"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(200):
            item = src.items.itemMap["MetalBars"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(25):
            item = src.items.itemMap["Frame"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(25):
            item = src.items.itemMap["Rod"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(50):
            item = src.items.itemMap["Wall"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(40):
            item = src.items.itemMap["Door"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for i in range(10):
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)

            if i < 2:
                item = src.items.itemMap["Vial"]()
                item.bolted = False
                currentTerrain.addItem(item,pos)
            if i < 4:
                item = src.items.itemMap["Armor"]()
                item.bolted = False
                currentTerrain.addItem(item,pos)
            if i < 6:
                item = src.items.itemMap["Sword"]()
                item.bolted = False
                currentTerrain.addItem(item,pos)
            if i < 8:
                item = src.items.itemMap["GooFlask"]()
                item.bolted = False
                currentTerrain.addItem(item,pos)

            item = src.items.itemMap["Corpse"]()
            item.bolted = False
            currentTerrain.addItem(item,pos)

        for _i in range(4):
            item = src.items.itemMap["Sword"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(4):
            item = src.items.itemMap["Armor"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(10):
            item = src.items.itemMap["Vial"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)
        for _i in range(10):
            item = src.items.itemMap["GooFlask"]()
            item.bolted = False
            pos = (random.randint(15,15*13),random.randint(15,15*13),0)
            currentTerrain.addItem(item,pos)

        for _i in range(20):
            bigPos = None
            for _j in range(10):
                pos = (random.randint(1,13),random.randint(1,13),0)
                if (pos[0] < 11 and pos[0] > 4) and (pos[1] < 11 and pos[1] > 4):
                    continue
                bigPos = pos
                break

            if not bigPos:
                break

            for _i in range(20):
                item = src.items.itemMap["Wall"]()
                item.bolted = False
                pos = (random.randint(bigPos[0]*15+1,bigPos[0]*15+14),random.randint(bigPos[1]*15+1,bigPos[1]*15+14),0)
                currentTerrain.addItem(item,pos)

            for _i in range(3):
                enemy = src.characters.Monster(4,4)
                enemy.health = 20
                enemy.baseDamage = 5
                enemy.maxHealth = 20
                enemy.godMode = True
                enemy.movementSpeed = 0.8

                quest = src.quests.questMap["SecureTile"](toSecure=(bigPos[0],bigPos[1],0))
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                currentTerrain.addCharacter(enemy, bigPos[0]*15+random.randint(1,13), bigPos[1]*15+random.randint(1,13))

        for pos in ((6,7,0),(7,6,0),(8,7,0),(7,8,0)):
            architect.doClearField(pos[0], pos[1])

        """
        # spawn enemies
        for x in range(1,14):
            for y in range(1,14):
                if (x < 9 and x > 5) and (y < 9 and y > 5):
                    continue

                if random.random() < 0.6:
                    continue

                enemy = src.characters.Monster(4,4)
                enemy.health = 28
                enemy.baseDamage = 7
                enemy.maxHealth = 28
                enemy.godMode = True
                enemy.movementSpeed = 0.8

                quest = src.quests.questMap["SecureTile"](toSecure=(x,y,0))
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                currentTerrain.addCharacter(enemy, x*15+7, y*15+7)
        """

        pos = random.choice([(6,6,0),(8,6,0),(8,8,0),(6,8,0)])
        architect.doClearField(pos[0], pos[1])
        tree = src.items.itemMap["Tree"]()
        tree.numMaggots = tree.maxMaggot
        currentTerrain.addItem(tree,(pos[0]*15+7,pos[1]*15+7,0))
        currentTerrain.forests.append(pos)

        positions = [(7,4),(8,5),(9,6),(10,7),(9,8),(8,9),(7,10),(6,9),(5,8),(5,6),(6,5),(7,4)]
        positions = [random.choice(positions)]
        for pos in positions:
            architect.doClearField(pos[0], pos[1])
            architect.doAddScrapfield(pos[0], pos[1], 100,leavePath=True)

        positions = [(7,6),(6,7),(7,8),(8,7),]
        positions = [random.choice(positions)]
        for pos in positions:
            architect.doClearField(pos[0], pos[1])
            architect.doAddScrapfield(pos[0], pos[1], 20,leavePath=True)

        itemsToRemove = []
        for x in range(1,14):
            for y in range(1,14):
                clearPositions = [(7,1,0),(7,2,0),(1,7,0),(2,7,0),(7,13,0),(7,12,0),(13,7,0),(12,7,0)]
                for clearPosition in clearPositions:
                    itemsToRemove.extend(currentTerrain.getItemByPosition((x*15+clearPosition[0],y*15+clearPosition[1],0)))
        currentTerrain.removeItems(itemsToRemove)

        return colonyBaseInfo


    def createProductionBase(self,pos):
        mainChar = src.characters.Character()
        # add basic set of abilities in openworld phase
        mainChar.questsDone = [
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
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]
        thisFactionId = self.factionCounter
        mainChar.faction = f"city #{thisFactionId}"
        mainChar.registers["HOMEx"] = 7
        mainChar.registers["HOMEy"] = 7
        mainChar.registers["HOMETx"] = pos[0]
        mainChar.registers["HOMETy"] = pos[1]
        self.factionCounter += 1
        productionBaseInfo = {"type":"productionBase"}
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        productionBaseInfo["terrain"] = currentTerrain
        productionBaseInfo["mainChar"] = mainChar

        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.bolted = False
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
        mainRoom.storageRooms = []

        epochArtwork = src.items.itemMap["EpochArtwork"](self.epochLength)
        productionBaseInfo["epochArtwork"] = epochArtwork
        mainRoom.addItem(epochArtwork,(6,6,0))

        cityBuilder = src.items.itemMap["CityBuilder2"]()
        cityBuilder.architect = architect
        mainRoom.addItem(cityBuilder,(7,1,0))
        cityBuilder.registerRoom(mainRoom)

        farm = cityBuilder.addFarmFromMap({"coordinate":(2,2),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"
        farm.addCharacter(
            mainChar, 6,6
        )
        farm = cityBuilder.addFarmFromMap({"coordinate":(5,2),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"
        farm = cityBuilder.addFarmFromMap({"coordinate":(2,5),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"
        farm = cityBuilder.addFarmFromMap({"coordinate":(12,12),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"
        farm = cityBuilder.addFarmFromMap({"coordinate":(9,12),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"
        farm = cityBuilder.addFarmFromMap({"coordinate":(12,9),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"
        farm = cityBuilder.addFarmFromMap({"coordinate":(2,12),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"
        farm = cityBuilder.addFarmFromMap({"coordinate":(5,12),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"
        farm = cityBuilder.addFarmFromMap({"coordinate":(2,9),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"
        farm = cityBuilder.addFarmFromMap({"coordinate":(12,2),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"
        farm = cityBuilder.addFarmFromMap({"coordinate":(12,5),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"
        farm = cityBuilder.addFarmFromMap({"coordinate":(9,2),"character":mainChar},forceSpawn=10)
        farm.tag = "farm"

        questArtwork = src.items.itemMap["QuestArtwork"]()
        mainRoom.addItem(questArtwork,(1,3,0))

        personnelArtwork = src.items.itemMap["PersonnelArtwork"]()
        productionBaseInfo["personnelArtwork"] = personnelArtwork
        personnelArtwork.faction = mainChar.faction
        mainRoom.addItem(personnelArtwork,(9,1,0))

        assimilator = src.items.itemMap["Assimilator"]()
        self.assimilator = assimilator
        mainRoom.addItem(assimilator,(11,5,0))

        basicTrainer = src.items.itemMap["BasicTrainer"]()
        self.basicTrainer = basicTrainer
        mainRoom.addItem(basicTrainer,(11,7,0))

        cityInfo = cityBuilder.spawnCity(mainChar)

        temple = cityInfo["temple"]

        for item in temple.itemsOnFloor:
            if item.type != "SpecialItemSlot":
                continue
            if item.itemID == thisFactionId:
                item.hasItem = True
                self.specialItemMap[item.itemID] = pos

        return productionBaseInfo

    def createRaidBase(self,pos):
        raidBaseInfo = {"type":"raidBase"}

        mainChar = src.characters.Character()
        # add basic set of abilities in openworld phase
        mainChar.questsDone = [
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
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]
        thisFactionId = self.factionCounter
        mainChar.faction = f"city #{thisFactionId}"
        mainChar.registers["HOMEx"] = 7
        mainChar.registers["HOMEy"] = 7
        mainChar.registers["HOMETx"] = pos[0]
        mainChar.registers["HOMETy"] = pos[1]
        mainChar.rank = 3
        self.factionCounter += 1
        raidBaseInfo["mainChar"] = mainChar
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        raidBaseInfo["terrain"] = currentTerrain

        item = src.items.itemMap["Scrap"](amount=1)
        mainChar.inventory.append(item)
        item = src.items.itemMap["Scrap"](amount=1)
        mainChar.inventory.append(item)

        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.bolted = False
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
        mainRoom.storageRooms = []

        mainRoom.addCharacter(
            mainChar, 3, 3
        )

        cityBuilder = src.items.itemMap["CityBuilder2"]()
        cityBuilder.architect = architect
        mainRoom.addItem(cityBuilder,(7,1,0))
        cityBuilder.registerRoom(mainRoom)

        cityData = cityBuilder.spawnCity(mainChar)
        cityBuilder.addTeleporterRoomFromMap({"coordinate":(7,4,0),"character":mainChar})
        temple = cityData["temple"]

        for item in temple.itemsOnFloor:
            if item.type != "SpecialItemSlot":
                continue
            if item.itemID == thisFactionId:
                item.hasItem = True
                self.specialItemMap[item.itemID] = pos

        epochArtwork = src.items.itemMap["EpochArtwork"](self.epochLength)
        raidBaseInfo["epochArtwork"] = epochArtwork
        mainRoom.addItem(epochArtwork,(6,6,0))

        return raidBaseInfo


    def createSiegedBase(self,pos):

        siegedBaseInfo = {"type":"siegedBase"}

        mainChar = src.characters.Character()
        thisFactionId = self.factionCounter
        mainChar.faction = f"city #{thisFactionId}"
        mainChar.registers["HOMEx"] = 7
        mainChar.registers["HOMEy"] = 7
        mainChar.registers["HOMETx"] = pos[0]
        mainChar.registers["HOMETy"] = pos[1]
        self.factionCounter += 1
        siegedBaseInfo["mainChar"] = mainChar
        currentTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        siegedBaseInfo["terrain"] = currentTerrain

        siegedBaseInfo["playerActivatedEpochArtwork"] = False

        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.bolted = False
        item.godMode = True
        currentTerrain.addItem(item,(1,1,0))

        numGuards = 10
        baseHealth = 100
        siegedBaseInfo["baseMovementSpeed"] = 0.8
        self.baseMovementSpeed = 0.8
        if self.difficulty == "easy":
            numGuards = 5
            baseHealth = 25
            siegedBaseInfo["baseMovementSpeed"] = 1.1
        if self.difficulty == "difficult":
            numGuards = 30
            baseHealth = 200
            siegedBaseInfo["baseMovementSpeed"] = 0.5

        # add basic set of abilities in openworld phase
        mainChar.questsDone = [
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
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]
        mainChar.macroState["macros"]["j"] = ["J", "f"]

        mainChar.baseDamage = 10
        mainChar.health = 100
        mainChar.maxHealth = 100
        if self.difficulty == "easy":
            mainChar.baseDamage = 15
            mainChar.health = 200
            mainChar.maxHealth = 200
        if self.difficulty == "difficult":
            mainChar.baseDamage = 5
            mainChar.health = 50
            mainChar.maxHealth = 50

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

        spawnRoomPos = random.choice([(6,13),(6,12),(6,11),(7,12),(7,11)])
        spawnRoom = architect.doAddRoom(
                {
                       "coordinate": spawnRoomPos,
                       "roomType": "EmptyRoom",
                       "doors": "0,6 6,0 12,6 6,12",
                       "offset": [1,1],
                       "size": [13, 13],
                },
                None)
        spawnRoom.tag = "cargo"

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

        #for i in range(1,20):
        #    spawnRoom.damage()

        spawnRoom.addCharacter(
            mainChar, 6, 6
        )

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
            farm = cityBuilder.addFarmFromMap({"coordinate":farmPos,"character":mainChar},forceSpawn=10)
            for x in range(3,10):
                gooFlask = src.items.itemMap["GooFlask"]()
                gooFlask.uses = 100
                farm.addItem(gooFlask,(x,1,0))
            for _i in range(1,30):
                farm.damage()
            farm.tag = "farm"

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

            for _i in range(1,20):
                treasureRoom.damage()

            for _i in range(1,25):
                item = src.items.itemMap[itemType]()
                #treasureRoom.addItem(item,(1,1,0))
            for _i in range(1,25):
                item = src.items.itemMap[itemType]()
                #treasureRoom.addItem(item,(2,1,0))
            for _i in range(1,25):
                item = src.items.itemMap[itemType]()
                #treasureRoom.addItem(item,(3,1,0))

            for _i in range(random.randint(11,17),random.randint(18,25)):
                enemy = src.characters.Monster(4,4)
                enemy.health = 10*i
                enemy.baseDamage = i
                enemy.faction = "invader"
                enemy.godMode = True
                treasureRoom.addCharacter(enemy, random.randint(2,11), random.randint(2,11))

                quest = src.quests.questMap["SecureTile"](toSecure=treasureRoom.getPosition())
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

        #addTreasureRoom((3,3),"Sword")
        #addTreasureRoom((11,11),"Armor")
        #addTreasureRoom((3,11),"Rod")
        #addTreasureRoom((11,3),"MetalBars")

        cityData = cityBuilder.spawnCity(mainChar)
        temple = cityData["temple"]

        for item in temple.itemsOnFloor:
            if item.type != "SpecialItemSlot":
                continue
            if item.itemID == thisFactionId:
                item.hasItem = True
                self.specialItemMap[item.itemID] = pos

        staffArtwork = src.items.itemMap["StaffArtwork"]()
        mainRoom.addItem(staffArtwork,(1,1,0))

        dutyArtwork = src.items.itemMap["DutyArtwork"]()
        mainRoom.addItem(dutyArtwork,(5,1,0))

        orderArtwork = src.items.itemMap["OrderArtwork"]()
        mainRoom.addItem(orderArtwork,(3,1,0))

        #produtionArtwork = src.items.itemMap["ProductionArtwork"]()
        #mainRoom.addItem(produtionArtwork,(3,11,0))

        personnelArtwork = src.items.itemMap["PersonnelArtwork"]()
        siegedBaseInfo["personnelArtwork"] = personnelArtwork
        self.personnelArtwork = personnelArtwork
        personnelArtwork.faction = mainChar.faction
        mainRoom.addItem(personnelArtwork,(9,1,0))

        questArtwork = src.items.itemMap["QuestArtwork"]()
        mainRoom.addItem(questArtwork,(1,3,0))

        orderArtwork.assignQuest({"character":mainChar,"questType":"cancel","groupType":"all","amount":0})
        orderArtwork.assignQuest({"character":mainChar,"questType":"BeUsefull","groupType":"rank 6","amount":0})

        epochArtwork = src.items.itemMap["EpochArtwork"](self.epochLength)
        epochArtwork.lastNumSpawners = 0
        siegedBaseInfo["epochArtwork"] = epochArtwork
        mainRoom.addItem(epochArtwork,(6,6,0))

        healingEffect = 50
        healthIncrease = 20
        baseDamageEffect = 2
        if self.difficulty == "easy":
            healingEffect = 100
            healthIncrease = 30
            baseDamageEffect = 3
        if self.difficulty == "difficult":
            healingEffect = 25
            healthIncrease = 10
            baseDamageEffect = 1
        assimilator = src.items.itemMap["Assimilator"](healingEffect=healingEffect,healthIncrease=healthIncrease,baseDamageEffect=baseDamageEffect)
        siegedBaseInfo["assimilator"] = assimilator
        mainRoom.addItem(assimilator,(11,5,0))

        basicTrainer = src.items.itemMap["BasicTrainer"]()
        siegedBaseInfo["basicTrainer"] = basicTrainer
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

        #orderArtwork = src.items.itemMap["BluePrintingArtwork"]()
        #mainRoom.addItem(orderArtwork,(9,1,0))

        hiveStyles = ["simple","empty","attackHeavy","healthHeavy","single"]
        if self.difficulty == "easy":
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
            room.tag = "hive"

            hiveStyle = hiveStyles.pop()

            if hiveStyle == "empty":
                pass
            elif hiveStyle == "simple":
                for _i in range(1,10):
                    enemy = src.characters.Monster(4,4)
                    enemy.godMode = True
                    enemy.health = 100
                    enemy.baseDamage = 10
                    enemy.faction = "invader"
                    room.addCharacter(enemy,random.randint(2,11),random.randint(2,11))

                    quest = src.quests.questMap["SecureTile"](toSecure=pos)
                    quest.autoSolve = True
                    quest.assignToCharacter(enemy)
                    quest.activate()
                    enemy.quests.append(quest)
            elif hiveStyle == "attackHeavy":
                for _i in range(1,10):
                    enemy = src.characters.Monster(4,4)
                    enemy.godMode = True
                    enemy.health = 10
                    enemy.baseDamage = 30
                    enemy.faction = "invader"
                    room.addCharacter(enemy,random.randint(2,11),random.randint(2,11))

                    quest = src.quests.questMap["SecureTile"](toSecure=pos)
                    quest.autoSolve = True
                    quest.assignToCharacter(enemy)
                    quest.activate()
                    enemy.quests.append(quest)
            elif hiveStyle == "healthHeavy":
                for _i in range(1,10):
                    enemy = src.characters.Monster(4,4)
                    enemy.godMode = True
                    enemy.health = 400
                    enemy.baseDamage = 6
                    enemy.faction = "invader"
                    room.addCharacter(enemy,random.randint(2,11),random.randint(2,11))

                    quest = src.quests.questMap["SecureTile"](toSecure=pos)
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

                quest = src.quests.questMap["SecureTile"](toSecure=pos)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)
            else:
                1/0

            neighbours = [(pos[0]-1,pos[1]),(pos[0]+1,pos[1]),(pos[0],pos[1]-1),(pos[0],pos[1]+1)]
            fillMaterial = ["EncrustedBush","Bush","Sprout2"]
            if self.difficulty == "easy":
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
            if farmPlot not in tmpList:
                continue
            fillMaterial = ["Bush","Bush","EncrustedBush"]
            if self.difficulty == "easy":
                fillMaterial = ["Bush","Bush","Sprout2"]
            architect.doSpawnItems(farmPlot[0],farmPlot[1],fillMaterial,20,repeat=10)

        for farmPlot in farmPlots:
            architect.doFillWith(farmPlot[0],farmPlot[1],["Mold","Mold","Sprout","Mold","Sprout2"])

        for farmPlot in farmPlots:
            if farmPlot in hivePositions:
                continue

            if self.difficulty == "easy":
                amount = int(random.random()*4)+1
            elif self.difficulty == "difficult":
                amount = int(random.random()*8)+3
            else:
                amount = int(random.random()*6)+2

            for _i in range(1,amount):
                enemy = src.characters.Monster(4,4)
                enemy.godMode = True
                enemy.health = baseHealth*4
                enemy.baseDamage = 7
                enemy.faction = "invader"
                enemy.tag = "hiveGuard"
                enemy.specialDisplay = "O-"
                currentTerrain.addCharacter(enemy,farmPlot[0]*15+random.randint(2,11),farmPlot[1]*15+random.randint(2,11))

                quest = src.quests.questMap["SecureTile"](toSecure=farmPlot)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

        blockerRingPositions = [(7,4,0),(6,5,0)]
        for pos in blockerRingPositions:
            for _i in range(3):
                enemy = src.characters.Monster(4,4)
                enemy.godMode = True
                enemy.health = 100
                enemy.baseDamage = 5
                currentTerrain.addCharacter(enemy, 15*pos[0]+random.randint(2,11), 15*pos[1]+random.randint(2,11))
                enemy.specialDisplay = "{-"
                enemy.faction = "invader"
                enemy.tag = "blocker"

                quest = src.quests.questMap["SecureTile"](toSecure=pos)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

        for x in range(1,14):
            for y in range(1,14):
                if (x,y) == (8,5):
                    continue

                if (x,y) in farmPlots:
                    continue

                if currentTerrain.getRoomByPosition((x,y)):
                    continue

                for _i in range(1,2):
                    mold = src.items.itemMap["Mold"]()
                    mold.dead = True
                    currentTerrain.addItem(mold,(15*x+random.randint(1,13),15*y+random.randint(1,13),0))

                placedMines = False

                if random.random() > 0.5 or (x,y) in blockerRingPositions:
                    placedMines = True
                    for _i in range(1,2+random.randint(1,5)):
                        offsetX = random.randint(1,13)
                        offsetY = random.randint(1,13)

                        xPos = 15*x+offsetX
                        yPos = 15*y+offsetY

                        if currentTerrain.getItemByPosition((xPos,yPos,0)):
                            continue

                        landmine = src.items.itemMap["LandMine"]()
                        currentTerrain.addItem(landmine,(xPos,yPos,0))

                for _i in range(1,5+random.randint(1,20)):
                    offsetX = random.randint(1,13)
                    offsetY = random.randint(1,13)

                    xPos = 15*x+offsetX
                    yPos = 15*y+offsetY

                    if currentTerrain.getItemByPosition((xPos,yPos,0)):
                        continue

                    if self.difficulty != "easy" and placedMines:
                        landmine = src.items.itemMap["LandMine"]()
                        currentTerrain.addItem(landmine,(xPos,yPos,0))

                    scrap = src.items.itemMap["Scrap"](amount=random.randint(1,13))
                    currentTerrain.addItem(scrap,(xPos,yPos,0))

                spawnChance = 0.2
                maxNumSpawns = 3
                if self.difficulty == "easy":
                    spawnChance = 0.05
                    maxNumSpawns = 2
                if self.difficulty == "difficult":
                    spawnChance = 0.5
                    maxNumSpawns = 5

                if random.random() < spawnChance and (x,y) not in blockerRingPositions and (x,y) not in farmPlots:
                    if (x <= 5 and (y <= 5 or y >= 9)) or (x >= 9 and (y <= 5 or y >= 9)):
                        continue
                    for _j in range(random.randint(1,maxNumSpawns)):
                        enemy = src.characters.Monster(4,4)
                        enemy.godMode = True
                        enemy.health = 15
                        enemy.baseDamage = 12
                        enemy.movementSpeed = siegedBaseInfo["baseMovementSpeed"]
                        pos = (15*x+random.randint(2,11), 15*y+random.randint(2,11))
                        currentTerrain.addCharacter(enemy, pos[0],pos[1])
                        enemy.specialDisplay = "ss"
                        enemy.faction = "invader"
                        enemy.tag = "lurker"

                        quest = src.quests.questMap["SecureTile"](toSecure=(x,y,0))
                        quest.autoSolve = True
                        quest.assignToCharacter(enemy)
                        quest.activate()
                        enemy.quests.append(quest)

        numChasers = 12
        if self.difficulty == "easy":
            numChasers = 5
        if self.difficulty == "difficult":
            numChasers = 20

        for i in range(1,numChasers):
            enemy = src.characters.Monster(4,4)
            enemy.godMode = True
            enemy.health = baseHealth//10*i
            enemy.baseDamage = 10*10
            currentTerrain.addCharacter(enemy, 15*8+random.randint(2,11), 15*13+random.randint(2,11))
            enemy.specialDisplay = "[-"
            enemy.faction = "invader"

            quest = src.quests.questMap["SecureTile"](toSecure=spawnRoom.getPosition(),endWhenCleared=True)
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            enemy.quests.append(quest)
            quest.activate()

            quest = src.quests.questMap["Huntdown"](target=mainChar,lifetime=500)
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            enemy.quests.append(quest)
            quest.activate()

            quest = src.quests.questMap["ClearTerrain"]()
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            enemy.quests.append(quest)
            quest.activate()

        if self.difficulty == "easy":
            toClear = [(7,1),(7,13),(1,7),(13,7)]
            for bigX in range(14):
                for bigY in range(14):
                    for (x,y) in toClear:
                        currentTerrain.removeItems(currentTerrain.getItemByPosition((bigX*15+x,bigY*15+y,0)))

        waypoints = [(5,10),(9,10),(9,4),(5,4)]
        if self.difficulty != "easy":
            for _i in range(1,10):
                waypoints = waypoints[1:]+[waypoints[0]]

                enemy = src.characters.Monster(4,4)
                enemy.godMode = True
                enemy.health = baseHealth*2
                enemy.baseDamage = 7
                enemy.movementSpeed = siegedBaseInfo["baseMovementSpeed"]
                currentTerrain.addCharacter(enemy, 15*waypoints[0][0]+random.randint(2,11), 15*waypoints[0][1]+random.randint(2,11))
                enemy.specialDisplay = "X-"
                enemy.faction = "invader"
                enemy.tag = "patrol"

                quest = src.quests.questMap["PatrolQuest"](waypoints=waypoints)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

        waypoints = [(5,4),(9,4),(9,10),(5,10)]
        for _i in range(1,10):
            waypoints = waypoints[1:]+[waypoints[0]]

            enemy = src.characters.Monster(4,4)
            enemy.godMode = True
            enemy.health = baseHealth*2
            enemy.baseDamage = 7
            currentTerrain.addCharacter(enemy, 15*waypoints[0][0]+random.randint(2,11), 15*waypoints[0][1]+random.randint(2,11))
            enemy.movementSpeed = siegedBaseInfo["baseMovementSpeed"]
            enemy.specialDisplay = "X-"
            enemy.faction = "invader"
            enemy.tag = "patrol"

            quest = src.quests.questMap["PatrolQuest"](waypoints=waypoints)
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

        self.personnelArtwork.charges += 6
        npc = self.personnelArtwork.spawnIndependentWorker(src.gamestate.gamestate.mainChar)
        npc = self.personnelArtwork.spawnIndependentWorker(src.gamestate.gamestate.mainChar)
        npc = self.personnelArtwork.spawnIndependentWorker(src.gamestate.gamestate.mainChar)

        return siegedBaseInfo

    def openedQuests(self):
        if self.activeStory["type"] == "siegedBase":
            self.openedQuestsSieged()
            return
        if self.activeStory["type"] == "raidBase":
            self.openedQuestsRaid()
            return
        if self.activeStory["type"] == "productionBase":
            self.openedQuestsProduction()
            return
        if self.activeStory["type"] == "colonyBase":
            self.openedQuestsColonyBase()
            return
        1/0

    def openedQuestsColonyBase(self):
        mainChar = self.activeStory["mainChar"]
        #containerQuest = src.quests.questMap["ExtendBase"]()
        storyText = """
You reach out to your implant and it answers:

Your task is to set up a base.
For this purpose you were given the colony core and its machines.
The whole process can be somewhat complicated, but you have guidance in this task.

This quest system will help you by breaking up the task.
You will get very detailed instructions, but you do not have to follow them closely.
The EpochArtwork will reward you for progress.

"""
        #containerQuest = src.quests.questMap["EpochQuest"](storyText=storyText)
        #containerQuest = src.quests.questMap["ExtendBase"]()
        containerQuest = src.quests.questMap["BeUsefull"](reason="""build the base.\n\n
Follow the instructions on the left side of the screen.
This should get you up and running in no time""")
        mainChar.quests.append(containerQuest)
        containerQuest.assignToCharacter(mainChar)
        containerQuest.activate()
        containerQuest.endTrigger = {"container": self, "method": "reachImplant"}

    def openedQuestsRaid(self):
        mainChar = self.activeStory["mainChar"]
        if mainChar.armor is None or mainChar.weapon is None:
            containerQuest = src.quests.questMap["Equip"]()
            mainChar.quests.append(containerQuest)
            containerQuest.assignToCharacter(mainChar)
            containerQuest.activate()
            containerQuest.generateSubquests(mainChar)
            containerQuest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        containerQuest = src.quests.questMap["EpochQuest"]()
        mainChar.quests.append(containerQuest)
        containerQuest.assignToCharacter(mainChar)
        containerQuest.activate()
        containerQuest.generateSubquests(mainChar)
        containerQuest.endTrigger = {"container": self, "method": "reachImplant"}
        return

    def openedQuestsProduction(self):
        mainChar = self.activeStory["mainChar"]
        pos = mainChar.getBigPosition()
        rooms = mainChar.getTerrain().getRoomByPosition(pos)
        if not rooms:
            storyText = """
There is a base in the center of this terrain.
Go there to find out what is happening here.
So far nothing suggests trouble on the way.

The entry of the base is located to the north of the base.
Enter the base that way."""
            containerQuest = src.quests.questMap["ReachBase"](storyText=storyText)
            mainChar.quests.append(containerQuest)
            containerQuest.assignToCharacter(mainChar)
            containerQuest.activate()
            containerQuest.generateSubquests(mainChar)
            containerQuest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        if rooms[0].tag == "farm":
            offset = (1,0,0)
            direction = "east"
            mainChar.addMessage("press z to see the movement keys")
            mainChar.addMessage("leave room to the "+direction)
            containerQuest = src.quests.questMap["InitialLeaveRoomStory"](description="leave room to the "+direction,targetPosition=mainChar.getBigPosition(offset=offset),direction=direction)
            mainChar.quests.append(containerQuest)
            containerQuest.assignToCharacter(mainChar)
            containerQuest.activate()
            containerQuest.generatePath(mainChar)
            containerQuest.generateSubquests(mainChar)
            containerQuest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        if not mainChar.registers.get("baseCommander"):
            storyText = """
You reached the base. The trap rooms are not charged and there are no other signs of activity.

This may be a bad thing.
Find the commander of this base to find out what is happening."""
            containerQuest = src.quests.questMap["ActivateEpochArtwork"](epochArtwork=self.activeStory["epochArtwork"],storyText=storyText)
            mainChar.quests.append(containerQuest)
            containerQuest.assignToCharacter(mainChar)
            containerQuest.activate()
            containerQuest.generateSubquests(mainChar)
            containerQuest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        storyText = """
There is no commander. That explains the inactivity.

This is a bit of a bad thing.
You are safe and you wont starve.
But you will be unable to leave.

You are in no hurry, but there is only one choice.
Integrate as the only worker into the base.
When you rise in rank you will be able to build a way out of here."""
        containerQuest = src.quests.questMap["TakeOverBase"](description="join base",storyText=storyText)
        mainChar.quests.append(containerQuest)
        containerQuest.assignToCharacter(mainChar)
        containerQuest.activate()
        containerQuest.generateSubquests(mainChar)

    def openedQuestsSieged(self):
        mainChar = self.activeStory["mainChar"]
        pos = mainChar.getBigPosition()
        rooms = mainChar.getTerrain().getRoomByPosition(pos)
        if not rooms:
            containerQuest = src.quests.questMap["ReachBase"]()
            mainChar.quests.append(containerQuest)
            containerQuest.assignToCharacter(mainChar)
            containerQuest.activate()
            containerQuest.generateSubquests(mainChar)
            containerQuest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        if rooms[0].tag == "cargo":
            offset = (-1,0,0)
            direction = "west"
            if mainChar.getBigPosition()[0] == 6:
                offset = (0,-1,0)
                direction = "north"
            mainChar.addMessage("press z to see the movement keys")
            mainChar.addMessage("flee room to the "+direction)
            containerQuest = src.quests.questMap["EscapeAmbushStory"](description="flee room "+direction,targetPosition=mainChar.getBigPosition(offset=offset),direction=direction)
            mainChar.quests.append(containerQuest)
            containerQuest.assignToCharacter(mainChar)
            containerQuest.activate()
            containerQuest.generatePath(mainChar)
            containerQuest.generateSubquests(mainChar)
            containerQuest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        if not mainChar.registers.get("baseCommander"):
            containerQuest = src.quests.questMap["ActivateEpochArtwork"](epochArtwork=self.activeStory["epochArtwork"])
            mainChar.quests.append(containerQuest)
            containerQuest.assignToCharacter(mainChar)
            containerQuest.activate()
            containerQuest.generateSubquests(mainChar)
            containerQuest.endTrigger = {"container": self, "method": "reachImplant"}
            return

        containerQuest = src.quests.questMap["TakeOverBase"](description="join base")
        mainChar.quests.append(containerQuest)
        containerQuest.assignToCharacter(mainChar)
        containerQuest.activate()
        containerQuest.generateSubquests(mainChar)

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
        for productionBaseInfo in self.productionBaseInfos:
            self.advanceProductionBase(productionBaseInfo)

        for siegedBaseInfo in self.siegedBaseInfos:
            self.advanceSiegedBase(siegedBaseInfo)

        for colonyBaseInfo in self.colonyBaseInfos:
            self.advanceColonyBase(colonyBaseInfo)

        for colonyBaseInfo in self.colonyBaseInfos2:
            self.advanceColonyBase2(colonyBaseInfo)

        self.numRounds += 1

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + self.epochLength)
        event.setCallback({"container": self, "method": "startRound"})

        terrain = src.gamestate.gamestate.terrainMap[7][7]
        terrain.addEvent(event)

    def advanceColonyBase(self,state):
        pass

    def advanceColonyBase2(self,state):
        terrain = state["terrain"]

        hasSpecialItems = []
        for room in terrain.rooms:
            specialItemSlots = room.getItemsByType("SpecialItemSlot")
            for specialItemSlot in specialItemSlots:
                if not specialItemSlot.hasItem:
                    continue
                hasSpecialItems.append(specialItemSlot)

        room = random.choice(terrain.rooms)

        '''
        if not src.gamestate.gamestate.tick < 100:
            if state["mainChar"] == src.gamestate.gamestate.mainChar:
                text = f"""
An epoch has passed. You currently control {len(hasSpecialItems)} special items.
You are rewarded with the following:

"""

                if not len(hasSpecialItems):
                    text += """
no reward.

"""

                if len(hasSpecialItems):
                    npc = src.characters.Character()
                    npc.questsDone = [
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
                        "WaitQuest" "NaiveDropQuest",
                        "NaiveDropQuest",
                        "DropQuestMeta",
                    ]

                    npc.faction = state["mainChar"].faction
                    #npc.rank = 6
                    room.addCharacter(npc,6,6)
                    npc.flask = src.items.itemMap["GooFlask"]()
                    npc.flask.uses = 100

                    npc.duties = []
                    duty = random.choice(("resource gathering","machine operation","hauling","resource fetching","maggot gathering","cleaning","machine placing","room building","scavenging"))
                    #duty = random.choice(("maggot gathering",))
                    npc.duties.append(duty)
                    npc.registers["HOMEx"] = 7
                    npc.registers["HOMEy"] = 7
                    npc.registers["HOMETx"] = terrain.xPosition
                    npc.registers["HOMETy"] = terrain.yPosition

                    npc.personality["autoFlee"] = False
                    npc.personality["abortMacrosOnAttack"] = False
                    npc.personality["autoCounterAttack"] = False

                    quest = src.quests.questMap["BeUsefull"](strict=True)
                    #quest = src.quests.questMap["ExtendBase"]()
                    quest.autoSolve = True
                    quest.assignToCharacter(npc)
                    quest.activate()
                    npc.assignQuest(quest,active=True)
                    npc.foodPerRound = 1

                    text += f"""
1 burned in clone named {npc.name} with duty {duty},
for controlling at least 1 special item.

"""

                text += """
press enter to continue"""
                src.interaction.showInterruptText(text)
        '''

        '''
        if not src.gamestate.gamestate.tick < 100:
            if state["mainChar"] == src.gamestate.gamestate.mainChar:
                text = f"""
An epoch has passed. You currently control {len(hasSpecialItems)} special items.
You are cursed with the following:

"""

                if not len(hasSpecialItems):
                    text += """
no curse.

"""
                if len(hasSpecialItems):
                    for j in range(4):
                        bigPos = (random.randint(1,13),random.randint(1,13),0)
                        numEnemies = 3

                        for i in range(numEnemies):
                            enemy = src.characters.Monster(4,4)
                            enemy.health = 20
                            enemy.baseDamage = 5
                            enemy.maxHealth = 20
                            enemy.godMode = True
                            enemy.movementSpeed = 0.8

                            quest = src.quests.questMap["SecureTile"](toSecure=(bigPos[0],bigPos[1],0))
                            quest.autoSolve = True
                            quest.assignToCharacter(enemy)
                            quest.activate()
                            enemy.quests.append(quest)

                            rooms = terrain.getRoomByPosition(bigPos)
                            if rooms:
                                rooms[0].addCharacter(enemy,6,6)
                            else:
                                terrain.addCharacter(enemy,15*bigPos[0]+random.randint(1,13),15*bigPos[1]+random.randint(1,13))

                    text += """
4 groups of insects appear, waiting for careless victim,
for controlling at least 1 glass heart.

"""

                numSpectres = 0
                for specialItemSlot in hasSpecialItems:
                    if not specialItemSlot.itemID in (3,4,5,6,7,):
                        continue

                    spectreHome = (7,7+2-specialItemSlot.itemID)

                    numEnemies = (specialItemSlot.itemID-2)**2
                    numSpectres += numEnemies

                    for i in range(numEnemies):
                        bigPos = (random.randint(1,13),random.randint(1,13),0)
                        enemy = src.characters.Monster(6,6)
                        enemy.health = 200
                        enemy.baseDamage = 10
                        enemy.faction = "spectre"
                        enemy.tag = "spectre"
                        enemy.movementSpeed = 2
                        enemy.registers["HOMETx"] = spectreHome[0]
                        enemy.registers["HOMETy"] = spectreHome[1]
                        enemy.registers["HOMEx"] = 7
                        enemy.registers["HOMEy"] = 7
                        rooms = terrain.getRoomByPosition(bigPos)
                        if rooms:
                            rooms[0].addCharacter(enemy,6,6)
                        else:
                            terrain.addCharacter(enemy,15*bigPos[0]+7,15*bigPos[1]+7)

                        quest = src.quests.questMap["DelveDungeon"](targetTerrain=(terrain.xPosition,terrain.yPosition,0),itemID=specialItemSlot.itemID)
                        quest.autoSolve = True
                        quest.assignToCharacter(enemy)
                        quest.activate()
                        enemy.quests.append(quest)

                        quest = src.quests.questMap["GoHome"]()
                        quest.autoSolve = True
                        quest.assignToCharacter(enemy)
                        quest.activate()
                        enemy.quests.append(quest)

                        quest = src.quests.questMap["Vanish"]()
                        quest.autoSolve = True
                        quest.assignToCharacter(enemy)
                        quest.activate()
                        enemy.quests.append(quest)

                        #src.gamestate.gamestate.mainChar = enemy

                if numSpectres:
                    text += f"""
{numSpectres} static spectres apeared, craving to reclaim their glass heart,
for controlling at least 1 special item.

"""

                text += """
press enter to continue"""
                src.interaction.showInterruptText(text)
        '''

    def advanceSiegedBase(self,state):
        terrain = state["terrain"]

        remainingEnemyCounter = 0
        for character in terrain.characters:
            if character.tag != "wave":
                continue
            remainingEnemyCounter += 1

        for room in terrain.rooms:
            for character in room.characters:
                if character.tag != "wave":
                    continue
                remainingEnemyCounter += 1

        """
        counter = 0
        while counter < remainingEnemyCounter:
            if terrain.rooms:
                room = random.choice(terrain.rooms)
                room.damage()
            counter += 1
        """

        """
        if not self.numRounds == 1:
            self.personnelArtwork.charges += 2
            npc = self.personnelArtwork.spawnIndependentFighter(src.gamestate.gamestate.mainChar)
            npc = self.personnelArtwork.spawnIndependentWorker(src.gamestate.gamestate.mainChar)
        """

        if src.gamestate.gamestate.mainChar.rank != 3:
            if not state["epochArtwork"].leader or state["pochArtwork"].leader.dead:
                state["epochArtwork"].dispenseEpochRewards({"rewardType":"autoSpend"})

        counter = 0

        spawnerRooms = []
        for room in terrain.rooms:
            for item in room.getItemByPosition((6,6,0)):
                if item.type == "MonsterSpawner":
                    spawnerRooms.append(room)

        if not spawnerRooms:
            return

        monsterStartRoom = random.choice(spawnerRooms)
        """
        while counter < remainingEnemyCounter:
            enemy = src.characters.Monster(6,6)
            enemy.faction = "invader"
            enemy.tag = "wave"
            enemy.specialDisplay = "<c"
            monsterStartRoom.addCharacter(enemy, 6, 6)

            quest = src.quests.questMap["DestroyRooms"]()
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

            counter += 1
        """

        #numMonsters = 1
        #if self.numRounds > 8:
        #    numMonsters = self.numRounds-8
        numMonsters = self.numRounds+remainingEnemyCounter

        if self.difficulty == "easy" and self.numRounds < 3:
            numMonsters = 0
        if self.difficulty == "medium" and self.numRounds == 1:
            numMonsters = 0

        for i in range(numMonsters):
            enemy = src.characters.Monster(6,6)
            enemy.health = 10*(i%10+1)
            enemy.baseDamage = (i%10+1)
            enemy.faction = "invader"
            enemy.tag = "wave"
            monsterStartRoom.addCharacter(enemy, 6, 6)
            enemy.movementSpeed = random.random()+0.5

            quest = src.quests.questMap["ClearTerrain"]()
            quest.autoSolve = True
            quest.assignToCharacter(enemy)
            quest.activate()
            enemy.quests.append(quest)

        numLurkers = 10
        if self.difficulty != "easy":
            numLurkers = 5
        if self.difficulty != "difficult":
            numLurkers = 20

        numLurkers = int(numLurkers*random.random()*2)
        for _i in range(numLurkers):
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
            enemy.movementSpeed = state["baseMovementSpeed"]
            monsterStartRoom.addCharacter(enemy, 6, 6)
            enemy.specialDisplay = "ss"
            enemy.faction = "invader"
            enemy.tag = "lurker"

            quest = src.quests.questMap["SecureTile"](toSecure=(x,y,0))
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(enemy)
            enemy.quests.append(quest)

class MainGameSieged(MainGame):
    def __init__(self, seed=0):
        super().__init__(seed,"Siege")

class MainGameProduction(MainGame):
    def __init__(self, seed=0):
        super().__init__(seed,"Production")

class MainGameRaid(MainGame):
    def __init__(self, seed=0):
        super().__init__(seed,"Raid")

class MainGameArena2(BasicPhase):
    def __init__(self, seed=0):
        super().__init__("Arena2", seed=seed)

        """
        """

        self.arenaStage = 0

    def start(self, seed=0, difficulty=None):
        mainChar = src.characters.Character()
        # add basic set of abilities in openworld phase
        mainChar.questsDone = [
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
            "WaitQuest" "NaiveDropQuest",
            "NaiveDropQuest",
            "DropQuestMeta",
        ]

        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addCharacter(mainChar,15*7+7,15*7+7)

        src.gamestate.gamestate.mainChar = mainChar

        combatMenu = src.interaction.CombatInfoMenu(mainChar)
        combatMenu.sidebared = True
        mainChar.rememberedMenu.append(combatMenu)
        messagesMenu = src.interaction.MessagesMenu(mainChar)
        mainChar.rememberedMenu2.append(messagesMenu)

        for x in range(1,13):
            for y in range(1,13):
                if x == 7 and y == 7:
                    continue

                enemy = src.characters.Monster(4,4)
                enemy.health = 100
                enemy.baseDamage = 10
                enemy.maxHealth = 100
                enemy.godMode = True
                enemy.movementSpeed = 0.8

                quest = src.quests.questMap["SecureTile"](toSecure=(x,y,0))
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                currentTerrain.addCharacter(enemy, x*15+7, y*15+7)

                for _i in range(random.randint(0,3)):
                    for _k in range(2):
                        scrap = src.items.itemMap["Scrap"](amount=20)
                        currentTerrain.addItem(scrap,(x*15+random.randint(1,12),y*15+random.randint(1,12),0))

        """
        item = src.items.itemMap["ArenaArtwork"]()
        currentTerrain.addItem(item,(7*15+5,7*15+5,0))
        """
        mainChar.personality["autoFlee"] = False
        mainChar.personality["abortMacrosOnAttack"] = False
        mainChar.personality["autoCounterAttack"] = False

        mainChar.baseDamage = 10

        self.mainChar = mainChar
        self.numCharacters = len(currentTerrain.characters)
        self.startRound()

        self.highScore = None

        src.interaction.showInterruptText("""

            Welcome to the Arena!

  Show your mastery of combat skills by killing enemies.
  The less health you loose the higher your score.

  After killing an enemy your health will be restored and your score will be shown.

           =    basic  combat    =

  Do normal attacks against enemies by walking into them.
  For example you need to press d to attack an enemy to your right.

  Every attack hits and both you and the enemies do 10 damage and have 100 HP.
  Basic combat is fully deterministic.

  So whoever hits first, wins and hits 10 times.
  The oponent dies and hits 9 times.

           =   special attacks   =

  You can do special attacks to get an advantage over basic combat
  Press shift while attacking to do a special attack.
  For example you need to press D to attack an enemy to your right.

  You will presented with a choice of special attacks with different stats.
  Most special attacks will increase your exhaustion.
  If you have more than 10 exhaustion damage you only deal half damage.
  You can reduce your exhaustion by 10 by skipping a turn by pressing .

  Remember that all attack keys are movement keys, too.
  So don't attack empty spaces or your character will move.

           =    the challenge    =

  My personal best is losing 40 HP to defeat an enemy.
  See if you can beat that!

""")

    def startRound(self):
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
        event.setCallback({"container": self, "method": "startRound"})

        terrain = src.gamestate.gamestate.terrainMap[7][7]

        for _i in range(self.numCharacters-len(terrain.characters)):
            if self.mainChar.dead:
                continue

            newHighScore = False
            if not self.highScore or self.mainChar.maxHealth-self.mainChar.health < self.highScore:
                newHighScore = True
                self.highScore = self.mainChar.maxHealth-self.mainChar.health

            text = f"""
you killed an enemy. You lost {self.mainChar.maxHealth-self.mainChar.health} health doing this.
"""
            if newHighScore:
                text += """
This is your new best.
"""
            else:
                text += f"""
you best is losing {self.highScore} health.
"""

            src.interaction.showInterruptText(text)
            self.mainChar.heal(100,reason="killing an enemy")
        self.numCharacters = len(terrain.characters)
        terrain.addEvent(event)

class MainGameArena(BasicPhase):
    def __init__(self, seed=0):
        super().__init__("Arena", seed=seed)

    def start(self, seed=0, difficulty=None):
        """
        """

        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]

        item = src.items.itemMap["ArchitectArtwork"]()
        architect = item
        item.godMode = True
        currentTerrain.addItem(item,(1,1,0))

        mainRoom = src.rooms.EmptyRoom(None,None,None,None)
        mainRoom.reconfigure(13, 13, doorPos=[(12,6),(6,12),(0,6),(6,0)])
        mainRoom.hidden = False
        mainRoom.xPosition = 7
        mainRoom.yPosition = 7
        mainRoom.offsetX = 1
        mainRoom.offsetY = 1
        currentTerrain.addRoom(mainRoom)

        mainChar = src.characters.Character()
        mainChar.faction = "cityTest"
        mainRoom.addCharacter(
            mainChar, 6, 6
        )
        src.gamestate.gamestate.mainChar = mainChar

        anvilPos = (10,2,0)
        machinemachine = src.items.itemMap["Anvil"]()
        mainRoom.addItem(machinemachine,(anvilPos[0],anvilPos[1],0))
        mainRoom.addInputSlot((anvilPos[0]-1,anvilPos[1],0),"Scrap")
        mainRoom.addInputSlot((anvilPos[0]+1,anvilPos[1],0),"Scrap")
        mainRoom.addOutputSlot((anvilPos[0],anvilPos[1]-1,0),None)
        mainRoom.walkingSpace.add((anvilPos[0],anvilPos[1]+1,0))

        metalWorkBenchPos = (8,3,0)
        machinemachine = src.items.itemMap["MetalWorkingBench"]()
        mainRoom.addItem(machinemachine,(metalWorkBenchPos[0],metalWorkBenchPos[1],0))
        mainRoom.addInputSlot((metalWorkBenchPos[0]+1,metalWorkBenchPos[1],0),"MetalBars")
        mainRoom.addOutputSlot((metalWorkBenchPos[0],metalWorkBenchPos[1]-1,0),None)
        mainRoom.addOutputSlot((metalWorkBenchPos[0],metalWorkBenchPos[1]+1,0),None)
        mainRoom.walkingSpace.add((metalWorkBenchPos[0]-1,metalWorkBenchPos[1],0))

        anvilPos = (9,5,0)
        machinemachine = src.items.itemMap["MachiningTable"]()
        mainRoom.addItem(machinemachine,(anvilPos[0],anvilPos[1],0))
        mainRoom.addInputSlot((anvilPos[0]-1,anvilPos[1],0),"MetalBars")
        mainRoom.addInputSlot((anvilPos[0]+1,anvilPos[1],0),"MetalBars")
        mainRoom.addOutputSlot((anvilPos[0],anvilPos[1]-1,0),None)
        mainRoom.walkingSpace.add((anvilPos[0],anvilPos[1]+1,0))

        epochArtwork = src.items.itemMap["EpochArtwork"](500,rewardSet="colony")
        epochArtwork.epochSurvivedRewardAmount = 0
        epochArtwork.changeCharges(600)
        mainRoom.addItem(epochArtwork,(3,1,0))
        """
        quest = src.quests.questMap["EpochQuest"]()
        mainChar.assignQuest(quest,active=True)

        #cityBuilder = src.items.itemMap["CityBuilder2"]()
        #cityBuilder.architect = architect
        #mainRoom.addItem(cityBuilder,(7,1,0))
        #cityBuilder.registerRoom(mainRoom)
        """

        dutyArtwork = src.items.itemMap["DutyArtwork"]()
        mainRoom.addItem(dutyArtwork,(5,1,0))

        cityPlaner = src.items.itemMap["CityPlaner"]()
        cityPlaner.bolted = True
        mainRoom.addItem(cityPlaner,(4,1,0))

        item = src.items.itemMap["ProductionArtwork"]()
        item.bolted = True
        item.charges = 1
        mainRoom.addItem(item,(4,3,0))

        item = src.items.itemMap["MachineMachine"]()
        item.bolted = True
        mainRoom.addItem(item,(4,5,0))

        item = src.items.itemMap["BluePrinter"]()
        item.bolted = True
        mainRoom.addItem(item,(2,4,0))

        item = src.items.itemMap["SpecialItemSlot"]()
        item.itemID = 1
        item.hasItem = True
        mainRoom.addItem(item,(1,1,0))
        item = src.items.itemMap["SpecialItemSlot"]()
        item.itemID = 2
        mainRoom.addItem(item,(2,1,0))
        for i in range(5):
            item = src.items.itemMap["SpecialItemSlot"]()
            item.hasItem = False
            item.itemID = 3+i
            mainRoom.addItem(item,(7+i,7,0))

            for x in range(1,6):
                mainRoom.walkingSpace.add((x,10,0))
            for x in range(7,12):
                mainRoom.walkingSpace.add((x,10,0))

            for x in range(1,6):
                mainRoom.walkingSpace.add((x,6,0))
            for x in range(7,12):
                mainRoom.walkingSpace.add((x,6,0))
            mainRoom.walkingSpace.add((5,2,0))
            mainRoom.walkingSpace.add((4,2,0))
            mainRoom.walkingSpace.add((3,2,0))
            mainRoom.walkingSpace.add((2,2,0))
            mainRoom.walkingSpace.add((1,2,0))
            mainRoom.walkingSpace.add((7,5,0))
            mainRoom.walkingSpace.add((7,4,0))
            mainRoom.walkingSpace.add((7,2,0))
            mainRoom.walkingSpace.add((7,1,0))
            mainRoom.walkingSpace.add((8,1,0))
            mainRoom.walkingSpace.add((9,1,0))
            mainRoom.walkingSpace.add((11,5,0))
            mainRoom.walkingSpace.add((11,4,0))
            mainRoom.walkingSpace.add((11,3,0))
            mainRoom.walkingSpace.add((10,4,0))

            for y in range(1,12):
                mainRoom.walkingSpace.add((6,y,0))

            for y in (7,9,11):
                if y != 7:
                    for x in range(7,12):
                        mainRoom.addStorageSlot((x,y,0),None)
                for x in range(1,6):
                    mainRoom.addStorageSlot((x,y,0),None)

        pos = (8,6,0)
        architect.doClearField(pos[0], pos[1])
        tree = src.items.itemMap["Tree"]()
        tree.numMaggots = tree.maxMaggot
        currentTerrain.addItem(tree,(pos[0]*15+7,pos[1]*15+7,0))
        currentTerrain.forests.append(pos)

        architect.doAddScrapfield(6, 7, 280, leavePath=True)

        room = src.rooms.EmptyRoom(None,None,None,None)
        room.reconfigure(13, 13, doorPos=[(12,6),(6,12),(0,6),(6,0)])
        room.hidden = False
        room.xPosition = 8
        room.yPosition = 7
        room.offsetX = 1
        room.offsetY = 1
        currentTerrain.addRoom(room)
        cityPlaner.setFloorplanFromMap({"character":mainChar,"type":"storage","coordinate":(8,7)})

        room = src.rooms.EmptyRoom(None,None,None,None)
        room.reconfigure(13, 13, doorPos=[(12,6),(6,12),(0,6),(6,0)])
        room.hidden = False
        room.xPosition = 7
        room.yPosition = 6
        room.offsetX = 1
        room.offsetY = 1
        currentTerrain.addRoom(room)
        cityPlaner.setFloorplanFromMap({"character":mainChar,"type":"gooProcessing","coordinate":(7,6)})

        room = src.rooms.EmptyRoom(None,None,None,None)
        room.reconfigure(13, 13, doorPos=[(12,6),(6,12),(0,6),(6,0)])
        room.hidden = False
        room.xPosition = 6
        room.yPosition = 6
        room.offsetX = 1
        room.offsetY = 1
        currentTerrain.addRoom(room)
        cityPlaner.setFloorplanFromMap({"character":mainChar,"type":"scrapCompactor","coordinate":(6,6)})

        room = src.rooms.EmptyRoom(None,None,None,None)
        room.reconfigure(13, 13, doorPos=[(12,6),(6,12),(0,6),(6,0)])
        room.hidden = False
        room.xPosition = 6
        room.yPosition = 8
        room.offsetX = 1
        room.offsetY = 1
        currentTerrain.addRoom(room)
        cityPlaner.setFloorplanFromMap({"character":mainChar,"type":"weaponProduction","coordinate":(6,8)})

        room = src.rooms.EmptyRoom(None,None,None,None)
        room.reconfigure(13, 13, doorPos=[(12,6),(6,12),(0,6),(6,0)])
        room.hidden = False
        room.xPosition = 7
        room.yPosition = 8
        room.offsetX = 1
        room.offsetY = 1
        currentTerrain.addRoom(room)

        room = src.rooms.EmptyRoom(None,None,None,None)
        room.reconfigure(13, 13, doorPos=[(12,6),(6,12),(0,6),(6,0)])
        room.hidden = False
        room.xPosition = 8
        room.yPosition = 8
        room.offsetX = 1
        room.offsetY = 1
        currentTerrain.addRoom(room)
        cityPlaner.setFloorplanFromMap({"character":mainChar,"type":"smokingRoom","coordinate":(8,8)})

        for room in currentTerrain.rooms:
           if not room.floorPlan:
               continue
           for walkingSpaceInfo in room.floorPlan.get("walkingSpace",[]):
                room.walkingSpace.add(walkingSpaceInfo)
           for storageSlotInfo in room.floorPlan.get("storageSlots",[]):
                room.addStorageSlot(storageSlotInfo[0],storageSlotInfo[1],storageSlotInfo[2])
           for inputSlotInfo in room.floorPlan.get("inputSlots",[]):
                if not len(inputSlotInfo) > 2:
                    inputSlotInfo = (inputSlotInfo[0],inputSlotInfo[1],{})
                room.addInputSlot(inputSlotInfo[0],inputSlotInfo[1],inputSlotInfo[2])
           for outputSlotInfo in room.floorPlan.get("outputSlots",[]):
                if not len(outputSlotInfo) > 2:
                    outputSlotInfo = (outputSlotInfo[0],outputSlotInfo[1],{})
                room.addOutputSlot(outputSlotInfo[0],outputSlotInfo[1],outputSlotInfo[2])
           for buildSite in room.floorPlan.get("buildSites",[]):
               item = src.items.itemMap[buildSite[1]]()
               room.addItem(item,buildSite[0])
               if buildSite[1] == "Machine":
                   item.setToProduce(buildSite[2]["toProduce"])
           room.floorPlan = None

        cityPlaner.setFloorplanFromMap({"character":mainChar,"type":"basicRoombuildingItemsProduction","coordinate":(7,8)})
        for room in currentTerrain.rooms:
            if not room.floorPlan:
                continue
            for walkingSpaceInfo in room.floorPlan.get("walkingSpace",[]):
                room.walkingSpace.add(walkingSpaceInfo)
            if "walkingSpace" in room.floorPlan:
                del room.floorPlan["walkingSpace"]

        epochArtwork.leader = mainChar

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("resource gathering")
        quest = src.quests.questMap["BeUsefull"]()
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("resource gathering")
        quest = src.quests.questMap["BeUsefullOnTile"](targetPosition=(6,6,0))
        quest.autoSolve = True
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("resource gathering")
        quest = src.quests.questMap["BeUsefullOnTile"](targetPosition=(6,8,0))
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("machine operation")
        quest = src.quests.questMap["BeUsefullOnTile"](targetPosition=(6,6,0))
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("machine operation")
        quest = src.quests.questMap["BeUsefullOnTile"](targetPosition=(6,8,0))
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        for pos in [(6,6,0),(6,8,0)]:
            room = currentTerrain.getRoomByPosition(pos)[0]
            for inputSlot in room.inputSlots:
                if inputSlot[1] != "Scrap":
                    continue
                room.addItem(src.items.itemMap["Scrap"](amount=1),inputSlot[0])

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("resource fetching")
        quest = src.quests.questMap["BeUsefull"]()
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("hauling")
        quest = src.quests.questMap["BeUsefull"]()
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("maggot gathering")
        quest = src.quests.questMap["BeUsefull"]()
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("metal working")
        quest = src.quests.questMap["BeUsefull"]()
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("scrap hammering")
        quest = src.quests.questMap["BeUsefull"]()
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("machining")
        quest = src.quests.questMap["BeUsefull"]()
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("painting")
        quest = src.quests.questMap["BeUsefullOnTile"](targetPosition=(7,8,0))
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("machine placing")
        quest = src.quests.questMap["BeUsefull"]()
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7
        src.gamestate.gamestate.mainChar = char

        char = src.characters.Character()
        mainRoom.addCharacter( char, 6, 6 )
        char.faction = mainChar.faction
        char.duties.append("machine operation")
        quest = src.quests.questMap["BeUsefullOnTile"](targetPosition=(7,6,0))
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()
        char.assignQuest(quest,active=True)
        char.registers["HOMEx"] = 7
        char.registers["HOMEy"] = 7
        char.registers["HOMETx"] = 7
        char.registers["HOMETy"] = 7

        room = currentTerrain.getRoomByPosition((8,7,0))[0]
        room.addItem(src.items.itemMap["MoldFeed"](),(1,1,0))
        room.addItem(src.items.itemMap["MoldFeed"](),(2,1,0))
        room.addItem(src.items.itemMap["MoldFeed"](),(3,1,0))
        room.addItem(src.items.itemMap["MoldFeed"](),(4,1,0))
        room.addItem(src.items.itemMap["MoldFeed"](),(5,1,0))
        room.addItem(src.items.itemMap["Stripe"](),(1,3,0))
        room.addItem(src.items.itemMap["Stripe"](),(2,3,0))
        room.addItem(src.items.itemMap["Bolt"](),(3,3,0))
        room.addItem(src.items.itemMap["Bolt"](),(4,3,0))
        room.addItem(src.items.itemMap["Painter"](),(5,3,0))
        item = src.items.itemMap["ScrapCompactor"]()
        item.bolted = False
        room.addItem(item,(7,1,0))
        item = src.items.itemMap["ScrapCompactor"]()
        item.bolted = False
        room.addItem(item,(8,1,0))
        item = src.items.itemMap["ScrapCompactor"]()
        item.bolted = False
        room.addItem(item,(9,1,0))
        item = src.items.itemMap["ScrapCompactor"]()
        item.bolted = False
        room.addItem(item,(10,1,0))
        item = src.items.itemMap["ScrapCompactor"]()
        item.bolted = False
        room.addItem(item,(11,1,0))

        item = src.items.itemMap["Machine"]()
        item.setToProduce("RoomBuilder")
        item.bolted = False
        room.addItem(item,(11,3,0))
        item = src.items.itemMap["Machine"]()
        item.setToProduce("RoomBuilder")
        item.bolted = False
        room.addItem(item,(10,3,0))
        item = src.items.itemMap["Machine"]()
        item.setToProduce("Door")
        item.bolted = False
        room.addItem(item,(9,3,0))
        item = src.items.itemMap["Machine"]()
        item.setToProduce("Door")
        item.bolted = False
        room.addItem(item,(8,3,0))
        item = src.items.itemMap["Machine"]()
        item.setToProduce("Door")
        item.bolted = False
        room.addItem(item,(7,3,0))

        mainChar.macroState["submenue"] = None

    def startRound(self):
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 1)
        event.setCallback({"container": self, "method": "startRound"})

        terrain = src.gamestate.gamestate.terrainMap[7][7]

        for _i in range(self.numCharacters-len(terrain.characters)):
            if self.mainChar.dead:
                continue

            newHighScore = False
            if not self.highScore or self.mainChar.maxHealth-self.mainChar.health < self.highScore:
                newHighScore = True
                self.highScore = self.mainChar.maxHealth-self.mainChar.health

            text = f"""
you killed an enemy. You lost {self.mainChar.maxHealth-self.mainChar.health} health doing this.
"""
            if newHighScore:
                text += """
This is your new best.
"""
            else:
                text += f"""
you best is losing {self.highScore} health.
"""

            src.interaction.showInterruptText(text)
            self.mainChar.heal(100,reason="killing an enemy")
        self.numCharacters = len(terrain.characters)
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
                    for _i in range(amount):
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
            or numProducts != 3
        ):
            seed += seed % 42
            src.gamestate.gamestate.terrain.removeRoom(self.miniBase)

            self.miniBase = src.rooms.TutorialMiniBase(4, 8, 0, 0, seed=seed)
            src.gamestate.gamestate.terrain.addRoom(self.miniBase)

            itemsFound = []
            for item in self.miniBase.itemsOnFloor:
                if isinstance(item, src.items.itemMap["GameTestingProducer"]) and (
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
            if isinstance(item, src.items.itemMap["Scrap"]) and (
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
                if isinstance(item, src.items.itemMap["GameTestingProducer"]) and (
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
                for _i in range(10):
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
                for _i in range(10):
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
            if self.fastProductionStart != 0:
                if src.gamestate.gamestate.tick - self.fastProductionStart > 100:
                    showText("it took you %s ticks to complete the order.")
                else:
                    src.gamestate.gamestate.gameWon = True
                    return

            self.fastProductionStart = src.gamestate.gamestate.tick
            for _i in range(10):
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
            for _i in range(10):
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

    phasesByName["Siege"] = Siege
    phasesByName["MainGame"] = MainGame
    phasesByName["MainGameSieged"] = MainGameSieged
    phasesByName["MainGameProduction"] = MainGameProduction
    phasesByName["MainGameRaid"] = MainGameRaid
    phasesByName["MainGameArena"] = MainGameArena
    phasesByName["MainGameArena2"] = MainGameArena2
    phasesByName["Tutorial"] = Tutorial
    phasesByName["PrefabDesign"] = PrefabDesign
