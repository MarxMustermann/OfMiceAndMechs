
# import basic libs
import json

# import basic internal libs
import src.items
import src.quests
import src.saveing
import src.events
import src.canvas
import src.logger
import src.chats
import src.gameMath
import src.characters
import src.gamestate
import random

# bad code: too many attributes
# obsolete: lots of old code needs a cleanup
class Room(src.saveing.Saveable):
    """
    the base class for all rooms
    """

    # bad code: the position of the room should not be in the constructor
    # obsolete: most parameters for rooms are oblsolete actually
    def __init__(
        self,
        layout="",
        xPosition=0,
        yPosition=0,
        offsetX=0,
        offsetY=0,
        desiredPosition=None,
        seed=0,
    ):
        """
        initialise internal state

        Parameters:
            layout: the room layout
            xPosition: the x position of the room in big coordinates
            yPosition: the y position of the 
            offsetX: the x offset from the position in big coordinates
            offsetY: the y offset from the position in big coordinates
            desiredPosition: the desired position for the room
            seed: the rng seed

        """
        self.walkingSpace = set()
        self.inputSlots = []
        self.outputSlots = []
        self.buildSites = []
        self.storageSlots = []
        self.floorPlan = {}
        self.sources = []
        self.tag = None
        self.animations = []

        super().__init__()

        self.container = None

        # initialize attributes
        self.health = 40
        self.hidden = True
        self.itemsOnFloor = []
        self.characters = []
        self.doors = []
        self.xPosition = None
        self.yPosition = None
        self.name = "Room"
        self.open = True
        self.terrain = None
        self.sizeX = None
        self.sizeY = None
        self.timeIndex = 0
        self.events = []
        self.floorDisplay = [src.canvas.displayChars.floor]
        self.chainedTo = []
        self.engineStrength = 0
        self.boilers = []
        self.furnaces = []
        self.steamGeneration = 0
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.isContainment = False
        self.listeners = {"default": []}
        self.seed = seed
        self.displayChar = (src.interaction.urwid.AttrSpec("#343", "black"), "RR")

        self.sizeX = 0
        self.sizeY = 0


        # set id
        import uuid

        self.id = uuid.uuid4().hex

        self.itemByCoordinates = {}

        # set meta information for saving
        self.attributesToStore.extend(
            [
                "yPosition",
                "xPosition",
                "offsetX",
                "offsetY",
                "objType",
                "sizeX",
                "sizeY",
                "walkingAccess",
                "open",
                "engineStrength",
                "steamGeneration",
                "isContainment",
                "timeIndex",
                "floorPlan",
                "name",
                "seed",
                "health",
                "hidden",
            ]
        )

        self.objectsToStore.extend(
                [
                    "container"
                ]
        )

        self.ignoreAttributes = []
        self.ignoreAttributes.extend([
            "events",
            "itemsOnFloor",
            "characters",
            "walkingSpace",
            "inputSlots",
            "outputSlots",
            "storageSlots",
            "buildSites",
            "sources",
            "objType",
            "walkingAccess",
            "terrain",
            "floorDisplay",
            "displayChar",
            "itemByCoordinates",
            "listeners",
            ])

        self.objectListsToStore.extend([
            "doors",
            "boilers",
            "furnaces",
            ])

    def getItemsByType(self,itemType, needsBolted = False):
        result = []
        for item in self.itemsOnFloor:
            if needsBolted and not item.bolted:
                continue
            if not item.type == itemType:
                continue
            result.append(item)
        return result

    def addAnimation(self,coordinate,animationType,duration,extraInfo):
        self.animations.append([coordinate,animationType,duration,extraInfo])

    def addBuildSite(self,position,specification,extraInfo=None):
        if extraInfo == None:
            extraInfo = {}
        self.buildSites.append((position,specification,extraInfo))

    def addOutputSlot(self,position,itemType,extraInfo=None):
        if extraInfo == None:
            extraInfo = {}
        self.outputSlots.append((position,itemType,extraInfo))

    def addInputSlot(self,position,itemType,extraInfo=None):
        if extraInfo == None:
            extraInfo = {}
        self.inputSlots.append((position,itemType,extraInfo))

    def addStorageSlot(self,position,itemType,extraInfo=None):
        if extraInfo == None:
            extraInfo = {}
        self.storageSlots.append((position,itemType,extraInfo))

    def addRandomItems(self):
        for inputSlot in self.inputSlots:
            if not inputSlot[1]:
                continue
            if inputSlot[1] == "Scrap":
                item = src.items.itemMap[inputSlot[1]](amount=5)
                item.bolted = False
                self.addItem(item,inputSlot[0])
                continue
            
            item = src.items.itemMap[inputSlot[1]]()
            item.bolted = False
            self.addItem(item,inputSlot[0])

        for outputSlot in self.outputSlots:
            if not outputSlot[1]:
                continue
            
            for i in range(1,5):
                item = src.items.itemMap[outputSlot[1]]()
                item.bolted = False
                self.addItem(item,outputSlot[0])

    def getNonEmptyOutputslots(self,itemType=None):
        result = []
        for outputSlot in self.outputSlots:
            if itemType and not outputSlot[1] == itemType:
                continue

            items = self.getItemByPosition(outputSlot[0])
            if not items:
                continue

            if itemType and not items[-1].type == itemType:
                continue

            result.append(outputSlot)

        for storageSlot in self.storageSlots:
            if itemType and not storageSlot[1] == None and not storageSlot[1] == itemType:
                continue

            items = self.getItemByPosition(storageSlot[0])
            if not items:
                continue

            if itemType and not items[-1].type == itemType:
                continue

            result.append(storageSlot)

        return result

    def getEmptyInputslots(self,itemType=None,allowAny=False):
        result = []
        for inputSlot in self.inputSlots:
            if (itemType and not inputSlot[1] == itemType) and (not allowAny or  not inputSlot[1] == None):
                continue

            items = self.getItemByPosition(inputSlot[0])
            if not items:
                result.append(inputSlot)
                continue

            if (itemType and not items[-1].type == itemType):
                continue

            if items[-1].type == "Scrap":
                if items[-1].amount < 15:
                    result.append(inputSlot)
                continue

            if not items[-1].walkable:
                continue

            maxAmount = inputSlot[2].get("maxAmount")
            if not maxAmount:
                maxAmount = 20

            if len(items) < maxAmount:
                result.append(inputSlot)

        for storageSlot in self.storageSlots:
            if (itemType and not storageSlot[1] == itemType) and (not allowAny or  not storageSlot[1] == None):
                continue
            
            items = self.getItemByPosition(storageSlot[0])
            if not items:
                result.append(storageSlot)
                continue

            if (itemType and not items[-1].type == itemType):
                continue

            if items[-1].type == "Scrap":
                if items[-1].amount < 15:
                    result.append(storageSlot)
                continue

            if not items[-1].walkable:
                continue

            maxAmount = storageSlot[2].get("maxAmount")
            if not maxAmount:
                maxAmount = 20

            if len(items) < maxAmount:
                result.append(storageSlot)

        return result

    def getPosition(self):
        return (self.xPosition,self.yPosition,0)

    def getPathCommandTile(self,startPos,targetPos,avoidItems=None,localRandom=None,tryHard=False,ignoreEndBlocked=False,path=None,character=None):
        if path == None:
            path = self.getPathTile(startPos,targetPos,avoidItems,localRandom,tryHard,ignoreEndBlocked=ignoreEndBlocked,character=character)

        command = ""
        movementMap = {(1,0):"d",(-1,0):"a",(0,1):"s",(0,-1):"w"}
        if path:
            for offset in path:
                command += movementMap[offset]
        return (command,path)

    def getPathTile(self,startPos,targetPos,avoidItems=None,localRandom=None,tryHard=False,ignoreEndBlocked=False,character=None):
        if not avoidItems:
            avoidItems = []
        if not localRandom:
            localRandom = random

        costMap = {startPos:0}
        lastPos = startPos
        toCheck = []
        nextPos = startPos
        paths = {startPos:[]}

        counter = 0
        while counter < 200:
            counter += 1
            
            if not nextPos:
                if not toCheck:
                    return []
                pos = localRandom.choice(toCheck)
                toCheck.remove(pos)
            else:
                pos = nextPos
            nextPos = None
            currentCost = costMap[pos]

            neutralOffsets = []
            goodOffsets = []
            badOffsets = []
            if targetPos[0] > pos[0]:
                goodOffsets.append((+1,0))
                badOffsets.append((-1,0))
            elif targetPos[0] < pos[0]:
                goodOffsets.append((-1,0))
                badOffsets.append((+1,0))
            else:
                neutralOffsets.append((-1,0))
                neutralOffsets.append((+1,0))

            if targetPos[1] > pos[1]:
                goodOffsets.append((0,+1))
                badOffsets.append((0,-1))
            elif targetPos[1] < pos[1]:
                goodOffsets.append((0,-1))
                badOffsets.append((0,+1))
            else:
                neutralOffsets.append((0,+1))
                neutralOffsets.append((0,-1))

            localRandom.shuffle(goodOffsets)
            localRandom.shuffle(neutralOffsets)
            localRandom.shuffle(badOffsets)
            offsets = badOffsets+neutralOffsets+goodOffsets

            while offsets:
                offset = offsets.pop()
                newPos = (pos[0]+offset[0],pos[1]+offset[1],pos[2])

                if newPos[0] > 13 or newPos[1] > 13 or newPos[0] < 0 or newPos[1] < 0:
                    continue

                if not self.getPositionWalkable((newPos[0],newPos[1],newPos[2]),character=character) and (not ignoreEndBlocked or not newPos == targetPos):
                    continue

                if not costMap.get(newPos) == None:
                    continue

                costMap[newPos] = currentCost+1
                paths[newPos] = paths[pos]+[offset]

                if not nextPos:
                    nextPos = newPos
                else:
                    toCheck.append(newPos)

            if nextPos == targetPos:
                break

        return paths.get(targetPos)

    def getPositionWalkable(self,pos,character=None):
        items = self.getItemByPosition(pos)
        if len(items) > 15:
            return False
        for item in items:
            if not character:
                if item.walkable == False:
                    return False
            else:
                if not character.getItemWalkable(item):
                    return False
        return True

    def damage(self):
        """
        damage the room
        """
        self.health -= 1
        if self.itemsOnFloor:
            item = random.choice(self.itemsOnFloor)
            if (
                item.yPosition == 0
                or item.yPosition == 0
                or item.xPosition == self.sizeX
                or item.yPosition == self.sizeY
            ) and (item.xPosition, item.yPosition) not in self.walkingAccess:
                self.open = True
                self.walkingAccess.append((item.xPosition, item.yPosition))
            random.choice(self.itemsOnFloor).destroy()
        if self.health == 0:
            self.terrain.removeRoom(self)

            toAdd = []
            for item in self.itemsOnFloor:
                item.bolted = False
                toAdd.append((item,(self.xPosition * 15 + self.offsetX,self.yPosition * 15 + self.offsetY,0)))
            for character in self.characters:
                character.xPosition += self.xPosition * 15 + self.offsetX
                character.yPosition += self.yPosition * 15 + self.offsetY
                self.terrain.addCharacter(
                    character, character.xPosition, character.yPosition
                )
            self.terrain.addItems(toAdd)

            self.xPosition = 0
            self.yPosition = 0

    # bad code: should be in extra class
    def addListener(self, listenFunction, tag="default"):
        """
        register a callbak to be run when something changes about the room

        Parameters:
            listenFunction: the callback
            tag: a filter for the changes to be notified about
        """

        if tag not in self.listeners:
            self.listeners[tag] = []

        if listenFunction not in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    # bad code: should be in extra class
    def delListener(self, listenFunction, tag="default"):
        """
        deregistering for notifications

        Parameters:
            listenFunction: the callback to call on change
            tag: a filter or reducing the amount of notifications
        """

        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        if not self.listeners[tag]:
            del self.listeners[tag]

    def getItemByPosition(self, position):
        """
        get items that are on a specific position

        Parameters:
            position: the position the fetch the items for
        """

        try:
            return self.itemByCoordinates[position]
        except:
            return []

    # bad code: probably misnamed
    # bad code: should be in extra class
    def changed(self, tag="default", info=None):
        """
        send notifications about this room having changed

        Parameters:
            tag: a tag for filtering notifications
            info: additional info
        """

        if not tag == "default":
            if tag not in self.listeners:
                return

            for listenFunction in self.listeners[tag]:
                listenFunction(info)
        for listenFunction in self.listeners["default"]:
            listenFunction()

        self.engineStrength = 250 * self.steamGeneration

    def getState(self):
        """
        get semi serialised room state

        Returns:
            the semi serialised state
        """

        state = super().getState()

        # get states from lists
        eventIds = []
        eventStates = {}
        for event in self.events:
            eventIds.append(event.id)
            eventStates[event.id] = event.getState()
        itemIds = []
        itemStates = {}
        for item in self.itemsOnFloor:
            itemIds.append(item.id)
            itemStates[item.id] = item.getState()
        charIds = []
        charStates = {}
        for character in self.characters:
            charIds.append(character.id)
            charStates[character.id] = character.getState()

        try:
            toRemove = None
            for charId in charIds:
                if charId == src.gamestate.gamestate.mainChar.id:
                    toRemove = charId
            if toRemove:
                charIds.remove(toRemove)
        except:
            pass

        state["walkingSpace"] = list(self.walkingSpace)
        state["inputSlots"] = []
        for inputSlot in self.inputSlots:
            state["inputSlots"].append([list(inputSlot[0]),inputSlot[1],inputSlot[2]])
        state["outputSlots"] = []
        for outputSlot in self.outputSlots:
            state["outputSlots"].append([list(outputSlot[0]),outputSlot[1],outputSlot[2]])
        state["storageSlots"] = []
        for storageSlot in self.storageSlots:
            state["storageSlots"].append([list(storageSlot[0]),storageSlot[1],storageSlot[2]])
        state["buildSites"] = []
        for buildSite in self.buildSites:
            state["buildSites"].append([list(buildSite[0]),buildSite[1]])
        state["sources"] = []
        for source in self.sources:
            state["sources"].append([list(source[0]),source[1]])

        # store the substates
        state["objType"] = self.objType

        state["walkingAccess"] = self.walkingAccess

        state["eventIds"] = eventIds
        state["eventStates"] = eventStates
        state["itemIds"] = itemIds
        state["itemStates"] = itemStates
        state["characterIds"] = charIds
        state["characterStates"] = charStates

        convertedListeners = {}
        if self.listeners:
            for (key,value) in self.listeners.items():
                if value:
                    1/0
                else:
                    convertedListeners[key] = value
        state["listeners"] = convertedListeners

        return state

    # bad code: incomplete
    def setState(self, state):
        """
        construct state from semi serialised form
        
        Parameters:
            state: the semi serialised state
        """

        if "timeIndex" in state:
            self.timeIndex = state["timeIndex"]

        # move room to correct position
        xPosition = None
        yPosition = None
        if "xPosition" in state and "yPosition" not in state:
            xPosition = state["xPosition"]
            yPosition = self.yPosition
        if "xPosition" in state and "yPosition" not in state:
            xPosition = self.xPosition
            yPosition = state["yPosition"]
        if "xPosition" in state and "yPosition" in state:
            xPosition = state["xPosition"]
            yPosition = state["yPosition"]

        if not xPosition is None and not yPosition is None:
            self.terrain.teleportRoom(self, (xPosition, yPosition))

        super().setState(state)

        self.walkingSpace = set()
        for walkingSpace in state["walkingSpace"]:
            self.walkingSpace.add(tuple(walkingSpace))
        self.inputSlots = []
        for inputSlot in state["inputSlots"]:
            self.inputSlots.append((tuple(inputSlot[0]),inputSlot[1],inputSlot[2]))
        self.outputSlots = []
        for outputSlot in state["outputSlots"]:
            self.outputSlots.append((tuple(outputSlot[0]),outputSlot[1],outputSlot[2]))
        self.storageSlots = []
        for storageSlot in state["storageSlots"]:
            self.storageSlots.append((tuple(storageSlot[0]),storageSlot[1],storageSlot[2]))
        self.buildSites = []
        for buildSites in state["buildSites"]:
            self.buildSites.append((tuple(buildSites[0]),buildSites[1]))
        self.sources = []
        for sources in state["sources"]:
            self.sources.append((tuple(sources[0]),sources[1]))


        self.walkingAccess = []
        for item in state["walkingAccess"]:
            self.walkingAccess.append((item[0], item[1]))

        if "itemIds" in state:
            for item in self.itemsOnFloor[:]:
                self.removeItem(item)
            for itemId in state["itemIds"]:
                itemState = state["itemStates"][itemId]
                item = src.items.getItemFromState(itemState)
                self.addItem(item, item.getPosition())

        if "eventIds" in state:
            for eventId in state["eventIds"]:
                eventState = state["eventStates"][eventId]
                event = src.events.getEventFromState(eventState)
                self.addEvent(event)

        if "characterIds" in state:
            for charId in state["characterIds"]:
                charState = state["characterStates"][charId]
                if "xPosition" not in charState or "yPosition" not in charState:
                    continue
                char = src.characters.getCharacterFromState(charState)
                self.characters.append(char)

        if "listeners" in state:
            convertedListeners = {}
            if self.listeners:
                for (key,value) in self.listeners.items():
                    if value:
                        1/0
                    else:
                        convertedListeners[key] = value
            self.listeners = convertedListeners

    def getCharactersOnPosition(self,position):
        out = []
        for character in self.characters:
            if character.getPosition() == position:
                out.append(character)
        return out

    def getEnemiesOnTile(self,character,pos=None):
        if not pos:
            pos = character.getBigPosition()

        out = []
        otherChars = self.characters
        for otherChar in otherChars:
            if character.faction == otherChar.faction:
               continue
            out.append(otherChar)

        return out

    def getResistance(self):
        """
        get physical resistance against beeing moved

        Returns:
            the resistance
        """

        return self.sizeX * self.sizeY


    # bad code: this method seems to be very specialised/kind of useless
    def openDoors(self):
        """
        open all doors of the room
        """

        for door in self.doors:
            door.open()
            self.open = True

    # bad code: this method seems to be very specialised/kind of useless
    def closeDoors(self):
        """
        close all doors of the room
        """

        for door in self.doors:
            door.close()
            self.open = False

    # bad code: should have proper pathfinding
    # obsolete: not really used anymore
    def findPath(self, start, end):
        """
        forward naive path calculation
        """

        return self.calculatePath(start[0], start[1], end[0], end[1], self.walkingPath)

    def calculatePath(self, x, y, dstX, dstY, walkingPath):
        """
        calculate a path based on a preset path
        Parameters:
            x: the start x position
            y: the start y position
            dstX: the end x position
            dstY: the end y position
            walkingPath: the precalculated paths
        Returns:
            the generated path
        """

        path = src.gameMath.calculatePath(x, y, dstX, dstY, walkingPath)
        return path

    def handleAddActionSelection(self,extraInfo):

        quest = src.quests.RunCommand(command=extraInfo["selected"])
        quest.autoSolve = True
        quest.activate()
        quest.assignToCharacter(src.gamestate.gamestate.mainChar)
        src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)

        quest = src.quests.GoToPosition(targetPosition=(src.gamestate.gamestate.dragState["start"]["pos"]))
        quest.autoSolve = True
        quest.activate()
        quest.assignToCharacter(src.gamestate.gamestate.mainChar)
        src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)

        src.gamestate.gamestate.mainChar.runCommandString("~")

        src.gamestate.gamestate.dragState = {}

    def handleFloorClick(self,extraInfo):
        if not src.gamestate.gamestate.mainChar.quests:
            return

        event = extraInfo["event"]

        if isinstance(event,src.interaction.tcod.event.MouseButtonDown):
            #src.gamestate.gamestate.mainChar.addMessage("should start draggin")
            src.gamestate.gamestate.mainChar.runCommandString("~")
            src.gamestate.gamestate.dragState = {}
            src.gamestate.gamestate.dragState["start"] = {"container":self,"pos":extraInfo["pos"]}
            return
        else:
            src.gamestate.gamestate.dragState["end"] = {"container":self,"pos":extraInfo["pos"]}

        dragState = src.gamestate.gamestate.dragState
        src.gamestate.gamestate.dragState = {}
        #src.gamestate.gamestate.mainChar.addMessage("should stop draggin")

        if dragState["end"]["container"] == self:
            quest = src.quests.GoToPosition(targetPosition=(dragState["end"]["pos"]))
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            src.gamestate.gamestate.mainChar.runCommandString("~")
        else:
            quest = src.quests.GoToPosition(targetPosition=(dragState["end"]["pos"]))
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            quest = src.quests.GoToTile(targetPosition=(self.xPosition,self.yPosition,0))
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            src.gamestate.gamestate.mainChar.runCommandString("~")

        if dragState["start"]["container"] == self:
            quest = src.quests.GoToPosition(targetPosition=(dragState["start"]["pos"]))
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            src.gamestate.gamestate.mainChar.runCommandString("~")
        else:
            quest = src.quests.GoToPosition(targetPosition=(dragState["start"]["pos"]))
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            quest = src.quests.GoToTile(targetPosition=(self.xPosition,self.yPosition,0))
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            src.gamestate.gamestate.mainChar.runCommandString("~")

    def getItemByType(self,itemType):
        for item in self.itemsOnFloor:
            if item.type == itemType:
                return item
        return None

    def render(self):
        """
        render the room

        Returns:
            the rendered room
        """

        # render room
        if not self.hidden or src.gamestate.gamestate.mainChar.room == self:
            # fill the area with floor tiles
            chars = []
            fixedChar = None
            if len(self.floorDisplay) == 1:
                fixedChar = self.floorDisplay[0]
            for i in range(0, self.sizeY):
                subChars = []
                for j in range(0, self.sizeX):
                    if fixedChar:
                        subChars.append(src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": (j,i,0)}},content=fixedChar))
                    else:
                        subChars.append(
                            self.floorDisplay[
                                (j + i + self.timeIndex * 2) % len(self.floorDisplay)
                            ]
                        )
                chars.append(subChars)

            # draw path
            for pos in self.walkingSpace:
                display = (src.interaction.urwid.AttrSpec("#888", "black"), "::")
                chars[pos[1]][pos[0]] = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": pos}},content=display)

            for entry in self.inputSlots:
                pos = entry[0]
                display= (src.interaction.urwid.AttrSpec("#f88", "black"), "::")
                chars[pos[1]][pos[0]] = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": pos}},content=display)

            for entry in self.outputSlots:
                pos = entry[0]
                display = (src.interaction.urwid.AttrSpec("#88f", "black"), "::")
                chars[pos[1]][pos[0]] = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": pos}},content=display)

            for entry in self.storageSlots:
                pos = entry[0]
                display = (src.interaction.urwid.AttrSpec("#fff", "black"), "::")
                chars[pos[1]][pos[0]] = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": pos}},content=display)

            for entry in self.buildSites:
                pos = entry[0]
                display = (src.interaction.urwid.AttrSpec("#88f", "black"), ";;")
                chars[pos[1]][pos[0]] = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": pos}},content=display)

            # draw items
            for item in self.itemsOnFloor:
                try:
                    display = item.render()
                    chars[item.yPosition][item.xPosition] = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": (item.xPosition,item.yPosition,0)}},content=display)
                except:
                    src.logger.debugMessages.append("room drawing failed")

            # draw characters
            viewChar = src.gamestate.gamestate.mainChar.personality["viewChar"]
            viewColour = src.gamestate.gamestate.mainChar.personality["viewColour"]

            foundMainchar = None
            for character in self.characters:
                if character == src.gamestate.gamestate.mainChar:
                    foundMainchar = character
                if character.yPosition < len(chars) and character.xPosition < len(
                    chars[character.yPosition]
                ):
                    if not "city" in character.faction or not character.charType in ("Character","Ghul"):
                        chars[character.yPosition][character.xPosition] = character.display
                    else:
                        if viewChar == "rank":
                            if not isinstance(character,src.characters.Ghul):
                                char = "@"+str(character.rank)
                            else:
                                char = "@x"
                        elif viewChar == "health":
                            health = str(character.health//(character.maxHealth//10))
                            if health == "10":
                                health = "|"
                            char = "@"+health
                        elif viewChar == "name":
                            if not isinstance(character,src.characters.Ghul):
                                char = character.name[0]+character.name.split(" ")[1][0]
                            else:
                                char = "Gu"
                        elif viewChar == "faction":
                            char = "@"+character.faction[-1]
                        elif viewChar == "activity":
                            if not isinstance(character,src.characters.Ghul):
                                postfix = " "

                                if character.isStaff:
                                    prefix = "S"
                                elif not character.quests:
                                    prefix = "I"
                                elif character.quests[0].type == "BeUsefull":
                                    prefix = "U"
                                else:
                                    prefix = "@"

                                """
                                activeQuest = character.getActiveQuest()
                                if activeQuest:
                                    postfix = activeQuest.shortCode
                                """
                                subQuest = None
                                if character.quests and character.quests[0].type == "BeUsefull":
                                    if character.quests[0].subQuests:
                                        postfix = character.quests[0].subQuests[0].shortCode
                                    else:
                                        postfix = " "

                                char = prefix+postfix
                            else:
                                char = "G "
                        else:
                            char = "@ "

                        color = "#fff"
                        if viewColour == "activity":
                            if not isinstance(character,src.characters.Ghul):
                                if character.isStaff:
                                    color = "#0f0"
                                elif not character.quests:
                                    color = "#f00"
                                elif character.quests[0].type == "BeUsefull":
                                    color = "#00f"
                                else:
                                    color = "#333"
                            else:
                                color = "#fff"
                        if viewColour == "rank":
                            color = "#fff"
                            if character.rank == 3:
                                color = "#0f0"
                            if character.rank == 4:
                                color = "#3f0"
                            if character.rank == 5:
                                color = "#480"
                            if character.rank == 6:
                                color = "#662"
                        if viewColour == "health":
                            color = "#fff"
                            health = character.health//(character.maxHealth//14)
                            if health == 0:
                                color = "#f00"
                            if health == 1:
                                color = "#e10"
                            if health == 2:
                                color = "#d20"
                            if health == 3:
                                color = "#c30"
                            if health == 4:
                                color = "#b40"
                            if health == 5:
                                color = "#a50"
                            if health == 6:
                                color = "#960"
                            if health == 7:
                                color = "#870"
                            if health == 8:
                                color = "#780"
                            if health == 9:
                                color = "#690"
                            if health == 10:
                                color = "#5a0"
                            if health == 11:
                                color = "#4b0"
                            if health == 12:
                                color = "#3c0"
                            if health == 13:
                                color = "#2d0"
                            if health == 14:
                                color = "#1e0"
                            if health == 15:
                                color = "#0f0"
                        if viewColour == "faction":
                            if character.faction.endswith("#1"):
                                color = "#066"
                            elif character.faction.endswith("#2"):
                                color = "#006"
                            elif character.faction.endswith("#3"):
                                color = "#060"
                            elif character.faction.endswith("#4"):
                                color = "#082"
                            elif character.faction.endswith("#5"):
                                color = "#028"
                            elif character.faction.endswith("#6"):
                                color = "#088"
                            elif character.faction.endswith("#7"):
                                color = "#086"
                            elif character.faction.endswith("#8"):
                                color = "#068"
                            elif character.faction.endswith("#9"):
                                color = "#0a0"
                            elif character.faction.endswith("#10"):
                                color = "#00a"
                            elif character.faction.endswith("#11"):
                                color = "#0a6"
                            elif character.faction.endswith("#12"):
                                color = "#06a"
                            elif character.faction.endswith("#13"):
                                color = "#08a"
                            elif character.faction.endswith("#14"):
                                color = "#0a6"
                            elif character.faction.endswith("#15"):
                                color = "#0aa"
                            else:
                                color = "#3f3"
                        if viewColour == "name":
                            colormap = {
                                    "A":"#aaa",
                                    "B":"#3aa",
                                    "C":"#00a",
                                    "D":"#fa4",
                                    "E":"#0af",
                                    "F":"#44a",
                                    "G":"#dfa",
                                    "H":"#0fa",
                                    "I":"#0a4",
                                    "J":"#4fa",
                                    "K":"#08a",
                                    "L":"#ea8",
                                    "M":"#37a",
                                    "N":"#3f8",
                                    "O":"#a4f",
                                    "P":"#0aa",
                                    "Q":"#8aa",
                                    "R":"#0a8",
                                    "S":"#a2a",
                                    "T":"#6af",
                                    "U":"#5ea",
                                    "V":"#0a5",
                                    "W":"#4af",
                                    "X":"#daa",
                                    "Y":"#1aa",
                                    "Z":"#03a",
                                    }
                            color = colormap.get(character.name[0])
                            if not color:
                                color = "#3f3"

                        chars[character.yPosition][character.xPosition] = (src.interaction.urwid.AttrSpec(color, "black"), char)

                        if character.showThinking:
                            chars[character.yPosition][character.xPosition][0].bg = "#333"
                            character.showThinking = False
                        if character.showGotCommand:
                            chars[character.yPosition][character.xPosition][0].bg = "#fff"
                            character.showGotCommand = False
                        if character.showGaveCommand:
                            chars[character.yPosition][character.xPosition][0].bg = "#855"
                            character.showGaveCommand = False
                    if foundMainchar:
                        activeQuest = foundMainchar.getActiveQuest()
                        if activeQuest:
                            for marker in activeQuest.getQuestMarkersSmall(foundMainchar):
                                pos = marker[0]
                                try:
                                    display = chars[pos[1]][pos[0]]
                                except:
                                    continue

                                actionMeta = None
                                if isinstance(display,src.interaction.ActionMeta):
                                    actionMeta = display
                                    display = display.content

                                if isinstance(display,int):
                                    display = src.canvas.displayChars.indexedMapping[display]
                                if isinstance(display,str):
                                    display = (src.interaction.urwid.AttrSpec("#fff","black"),display)

                                if hasattr(display[0],"fg"):
                                    display = (src.interaction.urwid.AttrSpec(display[0].fg,"#555"),display[1])
                                else:
                                    if not isinstance(display[0],tuple):
                                        display = (src.interaction.urwid.AttrSpec(display[0].foreground,"#555"),display[1])

                                if actionMeta:
                                    actionMeta.content = display
                                    display = actionMeta

                                chars[pos[1]][pos[0]] = display
                else:
                    src.logger.debugMessages.append(
                        "chracter is rendered outside of room"
                    )

            # draw main char
            if src.gamestate.gamestate.mainChar in self.characters:
                if src.gamestate.gamestate.mainChar.yPosition < len(
                    chars
                ) and src.gamestate.gamestate.mainChar.xPosition < len(
                    chars[src.gamestate.gamestate.mainChar.yPosition]
                ):
                    chars[src.gamestate.gamestate.mainChar.yPosition][src.gamestate.gamestate.mainChar.xPosition] = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@ ")
                else:
                    src.logger.debugMessages.append(
                        "chracter is rendered outside of room"
                    )

            usedAnimationSlots = set()
            for animation in self.animations[:]:
                (pos,animationType,duration,extraInfo) = animation

                if pos in usedAnimationSlots:
                    continue
                usedAnimationSlots.add(pos)

                if animationType == "attack":
                    if duration > 75:
                        display = "XX"
                    elif duration > 50:
                        display = "xX"
                    elif duration > 25:
                        display = "xx"
                    elif duration > 10:
                        display = ".x"
                    else:
                        display = ".."
                    try:
                        chars[pos[1]][pos[0]] = display
                    except:
                        continue

                    if duration > 10:
                        animation[2] -= 10
                    else:
                        self.animations.remove(animation)
                elif animationType in ("hurt","shielded",):
                    display = "++"
                    if animationType == "hurt":
                        display = (src.interaction.urwid.AttrSpec("#fff","#f00"),display)
                    if animationType == "shielded":
                        display = (src.interaction.urwid.AttrSpec("#fff","#555"),display)
                    try:
                        chars[pos[1]][pos[0]] = display
                    except:
                        continue

                    if duration > 10:
                        animation[2] -= 10
                        if animationType == "hurt":
                            distance = int(5*(duration/extraInfo["health"])+1)
                            xDistance = random.randint(-distance,distance)
                            offset = (xDistance,random.choice([distance-abs(xDistance),-(distance-abs(xDistance))]))
                            newPos = (animation[0][0]+offset[0],animation[0][1]+offset[1],animation[0][2])
                            self.addAnimation(newPos,"splatter",int(10*(duration/extraInfo["maxHealth"]))+1,{"mainChar":extraInfo["mainChar"]})
                    else:
                        self.animations.remove(animation)
                elif animationType in ("splatter",):
                    if not "display" in extraInfo:
                        letters = ["*","+",".",",","'","~"]
                        character = random.choice(letters)+random.choice(letters)
                        extraInfo["display"] = character
                    display = extraInfo["display"]
                    display = (src.interaction.urwid.AttrSpec("#000","#600"),display)
                    if extraInfo["mainChar"]:
                        display = "!!"
                        display = (src.interaction.urwid.AttrSpec("#fff","#f00"),display)
                    try:
                        chars[pos[1]][pos[0]] = display
                    except:
                        continue
                    animation[2] -= 1
                    if duration < 1:
                        self.animations.remove(animation)
                elif animationType in ("scrapChange",):
                    letters = ["*","+","#",";","%"]
                    character = random.choice(letters)+random.choice(letters)
                    display = character
                    display = (src.interaction.urwid.AttrSpec("#740","#000"),display)

                    try:
                        chars[pos[1]][pos[0]] = display
                    except:
                        continue
                    animation[2] -= 1

                    if duration < 1:
                        self.animations.remove(animation)
                elif animationType in ("explosion",):
                    display = "##"
                    display = (src.interaction.urwid.AttrSpec(["#fa0","#f00"][duration%2],["#f00","#fa0"][duration%2],),display)

                    try:
                        chars[pos[1]][pos[0]] = display
                    except:
                        continue
                    animation[2] -= 1

                    if duration < 1:
                        self.animations.remove(animation)
                elif animationType in ("showchar",):
                    display = extraInfo["char"]

                    try:
                        chars[pos[1]][pos[0]] = display
                    except:
                        continue
                    animation[2] -= 1

                    if duration < 1:
                        self.animations.remove(animation)
                elif animationType in ("charsequence",):
                    display = extraInfo["chars"][len(extraInfo["chars"])-1-duration]

                    try:
                        chars[pos[1]][pos[0]] = display
                    except:
                        continue
                    animation[2] -= 1

                    if duration < 1:
                        self.animations.remove(animation)
                elif animationType in ("smoke",):
                    display = (src.interaction.urwid.AttrSpec("#555", "black"), "##")

                    try:
                        chars[pos[1]][pos[0]] = display
                    except:
                        continue

                    direction = random.choice([(1,0,0),(0,1,0),(-1,0,0),(1,0,0),])

                    animation[2] -= 1
                    

                    self.animations.remove(animation)
                    if duration > 0:
                        self.addAnimation((animation[0][0]+direction[0],animation[0][1]+direction[1],animation[0][2]+direction[2],),animation[1],animation[2],extraInfo)
                else:
                    display = "??"
                    chars[pos[1]][pos[0]] = display
                    #self.animations.remove(animation)

            if src.gamestate.gamestate.dragState:
                if src.gamestate.gamestate.dragState["start"]["container"] == self:
                    pos = src.gamestate.gamestate.dragState["start"]["pos"]
                    try:
                        chars[pos[1]][pos[0]-2] = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": pos}},content="XX")
                        chars[pos[1]][pos[0]-1] = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": pos}},content="XX")
                        chars[pos[1]][pos[0]] = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": pos}},content="XX")
                        chars[pos[1]][pos[0]+1] = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": pos}},content="XX")
                        chars[pos[1]][pos[0]+2] = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": pos}},content="XX")

                        chars[pos[1]-1][pos[0]-2] = src.interaction.ActionMeta(payload={"container":self,"method":"handleAddActionSelection","params": {"selected":"e"}},content="ee")
                        chars[pos[1]-1][pos[0]-1] = src.interaction.ActionMeta(payload={"container":self,"method":"handleAddActionSelection","params": {"selected":"j"}},content="jj")
                        chars[pos[1]-1][pos[0]] = src.interaction.ActionMeta(payload={"container":self,"method":"handleAddActionSelection","params": {"selected":"k"}},content="kk")
                        chars[pos[1]-1][pos[0]+1] = src.interaction.ActionMeta(payload={"container":self,"method":"handleAddActionSelection","params": {"selected":"l"}},content="ll")
                        chars[pos[1]-1][pos[0]+2] = src.interaction.ActionMeta(payload={"container":self,"method":"handleAddActionSelection","params": {"selected":"."}},content="..")
                    except:
                        pass

        # show dummy of the room
        else:
            # fill the rooms inside with invisibility char
            chars = []
            for i in range(0, self.sizeY):
                subChars = []
                for j in range(0, self.sizeX):
                    subChars.append(src.canvas.displayChars.invisibleRoom)
                chars.append(subChars)

            # render rooms outline
            for item in self.itemsOnFloor:
                if (
                    item.xPosition == 0
                    or item.xPosition == self.sizeX - 1
                    or item.yPosition == 0
                    or item.yPosition == self.sizeY - 1
                ):
                    chars[item.yPosition][item.xPosition] = item.render()

        return chars

    def addCharacter(self, character, x, y, noRegister=False, forceRegister=False):
        """
        teleport character into the room

        Parameters:
            character: the character to teleport
            x: the x coordiate to teleport to
            y: the y coordiate to teleport to
        """

        self.characters.append(character)
        character.room = self
        #character.terrain = None
        character.xPosition = x
        character.yPosition = y
        character.path = []
        self.changed("entered room", character)

    def removeCharacter(self, character):
        """
        teleport character out of the room

        Parameters:
            character: the character to teleport
        """

        self.changed("left room", character)
        character.changed("left room", self)
        self.characters.remove(character)
        character.room = None

    def addItem(self, item, pos, actor=None):
        """
        add a item to the room

        Parameters:
            item: the item to add
            pos: the position to add the item on
        """

        self.addItems([(item, pos)], actor=actor)

    def addItems(self, items, actor=None):
        """
        add items to the room

        Parameters:
            items: a list containing a tuples of a item and its position
        """

        # add the items to the item list
        for itemPair in items:
            self.itemsOnFloor.append(itemPair[0])

        # add the items to the easy access map
        for itemPair in items:
            item = itemPair[0]
            pos = tuple(itemPair[1])

            if item.type == "Boiler":
                self.boilers.append(item)
            if item.type == "Furnace":
                self.furnaces.append(item)
            if item.type == "Scrap":
                itemList = self.itemByCoordinates.get(pos)
                if itemList and itemList[-1].type == "Scrap":
                    itemList[-1].amount += item.amount
                    continue

            item.container = self
            item.setPosition(pos)

            if pos in self.itemByCoordinates:
                self.itemByCoordinates[pos].insert(0, item)
            else:
                self.itemByCoordinates[pos] = [item]

            for buildSite in self.buildSites:
                if pos == buildSite[0] and item.type == buildSite[1]:
                    self.buildSites.remove(buildSite)
                    item.bolted = True
                    if buildSite[2].get("commands"):
                        src.gamestate.gamestate.mainChar.addMessage("set commands for:")
                        if not item.commands:
                            item.commands = {}
                        item.commands.update(buildSite[2].get("commands"))
                    if buildSite[2].get("settings"):
                        if not item.commands:
                            item.settings = {}
                        item.settings.update(buildSite[2].get("settings"))


    def removeItem(self, item):
        """
        remove item from the room

        Parameters:
            item: the item to remove
        """

        # remove items from easy access map
        itemList = self.getItemByPosition(item.getPosition())
        if item in itemList:
            itemList.remove(item)

            if not itemList:
                del self.itemByCoordinates[item.getPosition()]

        # remove item from the list of items
        if item in self.itemsOnFloor:
            self.itemsOnFloor.remove(item)

        item.xPosition = None
        item.zPosition = None
        item.yPosition = None
        item.container = None

        self.changed("removed item",self)

    def removeItems(self, items):
        """
        remove items from the room

        Parameters:
            items: a list of items to remove
        """

        for item in items:
            self.removeItem(item)

    # obsolete: not sure if used anymore
    def clearCoordinate(self, position):
        """
        remove all items from a spot in the room

        Parameters:
            position: the position to remove the items from
        """

        self.removeItems(self.getItemByPosition(position))

    def moveDirection(
        self, direction, force=1, initialMovement=True, movementBlock=set()
    ):
        """
        move the room a step into some direction

        Parameters:
            direction: the direction to move the room
            force: how much energy is behind the movement
            initialMovement: lag indicating if this is the first movement
            movementBlock: a tracker (list) of things to move.
        """

        # move items the room collided with
        # bad code: crashes when moved items were destroyed already
        if initialMovement:
            # collect the things that would be affected by the movement
            movementBlock = set()
            movementBlock.add(self)
            self.getAffectedByMovementDirection(
                direction, force=force, movementBlock=movementBlock
            )

            # calculate total resistance against being moved
            totalResistance = 0
            for thing in movementBlock:
                totalResistance += thing.getResistance()

            # refuse to move
            if totalResistance > force:
                src.logger.debugMessages.append("*CLUNK*")
                return

            # move affected items
            for thing in movementBlock:
                if not thing == self:
                    thing.moveDirection(direction, initialMovement=False)

        # actually move the room
        self.terrain.moveRoomDirection(direction, self)
        src.logger.debugMessages.append("*RUMBLE*")

    def getAffectedByMovementDirection(self, direction, force=1, movementBlock=set()):
        """
        get the things that would be affected by a room movement

        Parameters:
            direction: the direction to move the room
            force: how much energy is behind the movement
            movementBlock: a tracker (list) of things to move.
        Returns:
            a list of things affected by the movement
        """


        # gather things that would be affected on terrain level
        self.terrain.getAffectedByRoomMovementDirection(
            self, direction, force=force, movementBlock=movementBlock
        )

        # gather things chained to the room
        for thing in self.chainedTo:
            if thing not in movementBlock:
                movementBlock.add(thing)
                thing.getAffectedByMovementDirection(
                    direction, force=force, movementBlock=movementBlock
                )

        return movementBlock

    def moveCharacterDirection(self, character, direction):
        """
        move a character into some direction within or out of a room

        Parameters:
            character: the character to move
            direction: the direction to move the character
        """

        # check whether movement is contained in the room
        innerRoomMovement = True
        if direction == "south" and character.yPosition == self.sizeY - 1:
            innerRoomMovement = False
        elif direction == "north" and not character.yPosition:
            innerRoomMovement = False
        elif direction == "west" and not character.xPosition:
            innerRoomMovement = False
        elif direction == "east" and character.xPosition == self.sizeX - 1:
            innerRoomMovement = False

        # move inside the room
        if innerRoomMovement:
            # move character
            newPosition = [
                character.xPosition,
                character.yPosition,
                character.zPosition,
            ]
            if direction == "south":
                newPosition[1] += 1
            elif direction == "north":
                newPosition[1] -= 1
            elif direction == "west":
                newPosition[0] -= 1
            elif direction == "east":
                newPosition[0] += 1
            else:
                src.logger.debugMessages.append("invalid movement direction")


            for other in self.characters:
                if other == character:
                    continue

                if not tuple(newPosition) == other.getPosition():
                    continue

                if character.faction == "player" and other.faction == "player":
                    continue
                if character.faction.startswith("city"):
                    if character.faction == other.faction:
                        continue
                if character.faction == other.faction:
                    continue

                character.collidedWith(other)
                other.collidedWith(character)
                return

            return self.moveCharacter(character, tuple(newPosition))

        # move onto terrain
        if not character.room.yPosition:
            character.addMessage("you cannot move through the static")
            return

        newYPos = (
            character.yPosition + character.room.yPosition * 15 + character.room.offsetY
        )
        newXPos = (
            character.xPosition + character.room.xPosition * 15 + character.room.offsetX
        )
        if direction == "south":
            newYPos += 1
            character.runCommandString("s")
        elif direction == "north":
            newYPos -= 1
            character.runCommandString("w")
        elif direction == "west":
            newXPos -= 1
            character.runCommandString("a")
        elif direction == "east":
            newXPos += 1
            character.runCommandString("d")
        else:
            src.logger.debugMessages.append("invalid movement direction")

        newPosition = (newXPos, newYPos, 0)

        itemList = self.terrain.getItemByPosition(newPosition)
        for item in itemList:
            if not character.getItemWalkable(item):
                return item

        if len(itemList) > 15:
            return itemList[0]

        if character in self.characters:
            self.removeCharacter(character)
        self.terrain.addCharacter(character, newXPos, newYPos)
        return

    def moveCharacter(self, character, newPosition):
        """
        move a character to a new position within room

        Parameters:
            character: the character to move
            newPosition: the position to move the character to
        Returns:
            return item if the character collided with an item
        """

        # check if target position can be walked on
        triggeringItems = []

        if newPosition in self.itemByCoordinates:
            for item in self.itemByCoordinates[newPosition]:
                if item.hasStepOnAction:
                    triggeringItems.append(item)
                if not character.getItemWalkable(item):
                    return item

            if len(self.itemByCoordinates[newPosition]) > 15:
                return self.itemByCoordinates[newPosition][0]

        for item in triggeringItems:
            item.stepedOn(character)

        # teleport character to new position
        character.xPosition = newPosition[0]
        character.yPosition = newPosition[1]

        character.changed()
        return None

    # bad code: should be in extra class
    def addEvent(self, event):
        """
        add an event to internal structure

        Parameters:
            event: the event to add
        """

        index = 0
        for existingEvent in self.events:
            if event.tick < existingEvent.tick:
                break
            index += 1
        self.events.insert(index, event)

    # bad code: should be in extra class
    def removeEvent(self, event):
        """
        remove an event from internal structure

        Parameters:
            event: the event to remove
        """

        self.events.remove(event)

    # bad code: should be in extra class
    # bad code: this is no real good use case
    # obsolete: not used anymore
    def removeEventsByType(self, eventType):
        """
        remove events of a certain type from internal structure
        """

        for event in self.events:
            if type(event) == eventType:
                self.events.remove(event)

    def advance(self,advanceMacros=False):
        """
        advance the room one step
        """

        # change own state
        self.timeIndex += 1
        self.animations = []

        # advance each character
        for character in self.characters:
            character.advance(advanceMacros=advanceMacros)

        # log events that were not handled properly
        while self.events and self.events[0].tick <= src.gamestate.gamestate.tick:
            event = self.events[0]
            if event.tick < src.gamestate.gamestate.tick:
                1/0

            event.handleEvent()
            self.events.remove(event)

    # bad code: should do something or be deleted
    def calculatePathMap(self):
        """
        dummy to prevent crashes
        """
        pass

    def getDistance(self,position):
        return abs(self.xPosition-position[0])+abs(self.yPosition-position[1])

class MiniBase(Room):
    """
    a room sized base for small off mech missions
    """

    objType = "MiniBase"

    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
        seed=0,
    ):
        """
        create room and add special items

        Parameters:
            layout: the room layout
            xPosition: the x position of the room in big coordinates
            yPosition: the y position of the 
            offsetX: the x offset from the position in big coordinates
            offsetY: the y offset from the position in big coordinates
            desiredPosition: the desired position for the room
            seed: the rng seed
        """

        # obsolete: the room layout is practically never used
        roomLayout = """
XXXXXXXXXXXXX
X     .     X
X     .     X
X           X
X           X
X           X
X           $
X           X
X           X
X           X
X           X
X           X
XXXXXXXXXXXXX
"""
        super().__init__(
            roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )

        itemsToAdd = []
        self.artwork = src.items.itemMap["ProductionArtwork"]()
        itemsToAdd.append((self.artwork,(4,1,0)))
        self.compactor = src.items.itemMap["ScrapCompactor"]()
        itemsToAdd.append((self.compactor,(8,1,0)))
        flask1 = src.items.itemMap["GooFlask"]()
        flask1.uses = 100
        itemsToAdd.append((flask1,(10,2,0)))
        flask2 = src.items.itemMap["GooFlask"]()
        flask2.uses = 100
        itemsToAdd.append((flask2,(10,3,0)))
        flask3 = src.items.itemMap["GooFlask"]()
        flask3.uses = 100
        itemsToAdd.append((flask3,(10,4,0)))

        self.machinemachine = src.items.itemMap["MachineMachine"]()
        itemsToAdd.append((self.machinemachine,(4,4,0)))

        self.infoScreen = src.items.itemMap["AutoTutor"]()
        itemsToAdd.append((self.infoScreen,(4,9,0)))

        self.bluePrinter = src.items.itemMap["BluePrinter"]()
        itemsToAdd.append((self.bluePrinter,(8,9,0)))

        self.machine = src.items.itemMap["Machine"]()
        self.machine.setToProduce("Sheet")
        itemsToAdd.append((self.machine,(7,8,0)))

        self.addItems(itemsToAdd)

        itemsToAdd = []
        itemsToAdd.append((src.items.itemMap["MetalBars"](),(3, 1, 0)))
        itemsToAdd.append((src.items.itemMap["MetalBars"](),(7, 9, 0)))
        itemsToAdd.append((src.items.itemMap["MetalBars"](),(9, 1, 0)))
        itemsToAdd.append((src.items.itemMap["MetalBars"](),(3, 4, 0)))
        itemsToAdd.append((src.items.itemMap["Scrap"](),(7, 1, 0)))
        itemsToAdd.append((src.items.itemMap["Connector"](),(7, 9, 0)))
        bluePrint = src.items.itemMap["BluePrint"]()
        bluePrint.setToProduce("Sheet")
        bluePrint.bolted = False
        itemsToAdd.append((bluePrint,(9, 9, 0)))
        bluePrint = src.items.itemMap["BluePrint"]()
        bluePrint.setToProduce("Radiator")
        bluePrint.bolted = False
        itemsToAdd.append((bluePrint,(9, 9, 0)))
        bluePrint = src.items.itemMap["BluePrint"]()
        bluePrint.setToProduce("Mount")
        bluePrint.bolted = False
        itemsToAdd.append((bluePrint,(9, 9, 0)))
        bluePrint = src.items.itemMap["BluePrint"]()
        bluePrint.setToProduce("Stripe")
        bluePrint.bolted = False
        itemsToAdd.append((bluePrint,(9, 9, 0)))
        bluePrint = src.items.itemMap["BluePrint"]()
        bluePrint.setToProduce("Bolt")
        bluePrint.bolted = False
        itemsToAdd.append((bluePrint,(9, 9, 0)))
        bluePrint = src.items.itemMap["BluePrint"]()
        bluePrint.setToProduce("Rod")
        bluePrint.bolted = False
        itemsToAdd.append((bluePrint,(4, 3, 0)))
        self.addItems(itemsToAdd)

        self.sizeX = 13
        self.sizeY = 13
        self.walkingAccess = []

        for item in self.doors:
            item.walkable = True

class MiniBase2(Room):
    """
    a room sized base for small off mech missions
    varyation for survival map
    """

    objType = "MiniBase2"

    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
        seed=0,
    ):
        """
        create room and add special items

        Parameters:
            layout: the room layout
            xPosition: the x position of the room in big coordinates
            yPosition: the y position of the 
            offsetX: the x offset from the position in big coordinates
            offsetY: the y offset from the position in big coordinates
            desiredPosition: the desired position for the room
            seed: the rng seed
        """

        roomLayout = """
XXXXXXXXXXX
X         X
X         X
X         X
X         X
X  .......$
X         X
X         X
X         X
X         X
XXXXXXXXXXX
"""
        super().__init__(
            roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.walkingAccess = []

        healingstation = src.items.itemMap["HealingStation"]()
        corpseShredder = src.items.itemMap["CorpseShredder"]()
        corpse = src.items.itemMap["Corpse"]()
        corpse.charges = 300
        sunScreen = src.items.itemMap["SunScreen"]()
        vial = src.items.itemMap["Vial"]()

        vial.uses = random.randint(0, 10)
        self.addItems([(healingstation,(4,1,0)), (sunScreen,(5,5,0)), (vial,(7,3,0)), (corpseShredder,(4,8,0)), (corpse,(3,8,0))])

class EmptyRoom(Room):
    """
    a empty room
    """

    objType = "EmptyRoom"

    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
        bio=False,
    ):
        """
        create room and add special items

        Parameters:
            layout: the room layout
            xPosition: the x position of the room in big coordinates
            yPosition: the y position of the 
            offsetX: the x offset from the position in big coordinates
            offsetY: the y offset from the position in big coordinates
            desiredPosition: the desired position for the room
            seed: the rng seed
        """

        roomLayout = """
XXX
X.$
XXX
"""
        super().__init__(
            roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.bio = bio

        if self.bio:
            self.floorDisplay = [
                src.canvas.displayChars.moss,
                src.canvas.displayChars.moss,
                src.canvas.displayChars.sprout,
                src.canvas.displayChars.moss,
                src.canvas.displayChars.moss,
                src.canvas.displayChars.sprout2,
            ]

        self.name = "room"

        self.attributesToStore.extend(["bio"])

        self.staff = []
        self.duties = ["resource fetching","hauling","clearing","scratch checking","resource gathering","guarding","painting","machine placing"]

        self.displayChar = (src.interaction.urwid.AttrSpec("#556", "black"), "ER")
        self.sources = []

    def spawnPlaned(self):
        if self.floorPlan:
            if "inputSlots" in self.floorPlan:
                self.inputSlots.extend(self.floorPlan["inputSlots"])
            if "outputSlots" in self.floorPlan:
                self.outputSlots.extend(self.floorPlan["outputSlots"])
            if "storageSlots" in self.floorPlan:
                self.storageSlots.extend(self.floorPlan["storageSlots"])
            if "buildSites" in self.floorPlan:
                for buildSite in self.floorPlan["buildSites"]:
                    if buildSite[2].get("command"):
                        buildSite[2]["command"] = "".join(buildSite[2]["command"])
                    self.buildSites.append(buildSite)
            if "walkingSpace" in self.floorPlan:
                self.walkingSpace.update(self.floorPlan["walkingSpace"])
            self.floorPlan = None
            return

        if self.buildSites:
            for buildSite in self.buildSites[:]:
                item = src.items.itemMap[buildSite[1]]()
                if item.type == "Command":
                    item.command = "".join(buildSite[2].get("command"))
                if buildSite[2].get("commands"):
                    item.commands = buildSite[2].get("commands")
                if buildSite[2].get("settings"):
                    item.settings = buildSite[2].get("settings")
                self.addItem(item,buildSite[0])
            return

    def spawnGhuls(self,character):
        for item in self.itemsOnFloor:
            if item.bolted and item.type == "CorpseAnimator":
                item.filled = True
                item.apply(character)

    def resetDirect(self):
        self.inputSlots = []
        self.outputSlots = []
        self.storageSlots = []
        self.buildSites = []
        self.walkingSpace = {(0,6),(6,0),(12,6),(6,12)}

        for item in self.itemsOnFloor[:]:
            if item.xPosition == 0 or item.yPosition == 0:
                continue
            if item.xPosition == 12 or item.yPosition == 12:
                continue
            self.removeItem(item)

    def doBasicSetup(self):
        self.addPathCross()

    def addPathCross(self):
        for x in range(1,12):
            self.walkingSpace.add((x,6,0))
        for y in range(1,12):
            self.walkingSpace.add((6,y,0))

    def reconfigure(self, sizeX=3, sizeY=3, items=[], bio=False, doorPos=[]):
        """
        change the size of the room

        Parameters:
            sizeX: the size of the room
            sizeY: the size of the room
            items: the items the room should have afterwards
            bio: flag to switch between man made or grown room
            doorPos: a list of door positions
        """

        items = []

        self.sizeX = sizeX
        self.sizeY = sizeY

        if not items:
            if not doorPos:
                doorPos.append([(sizeX - 1, sizeY // 2)])

            for x in (0, sizeX - 1):
                for y in range(0, sizeY):
                    if (x, y) in doorPos:
                        item = src.items.itemMap["Door"]()
                        item.walkable = True
                        items.append((item, (x, y, 0)))
                    else:
                        items.append((src.items.itemMap["Wall"](), (x, y, 0)))

            for x in range(1, sizeX - 1):
                for y in (0, sizeY - 1):
                    if (x, y) in doorPos:
                        item = src.items.itemMap["Door"]()
                        item.walkable = True
                        items.append((item, (x, y, 0)))
                    else:
                        items.append((src.items.itemMap["Wall"](), (x, y, 0)))

        self.itemsOnFloor = []
        self.itemByCoordinates = {}
        self.addItems(items)

        self.walkingAccess = []
        for itemPair in items:
            item = itemPair[0]
            if item.type == "Door" or item.type == "Chute":
                self.walkingAccess.append((item.xPosition, item.yPosition))
                self.walkingSpace.add((item.xPosition,item.yPosition,0))

    def setState(self, state):
        """
        load state from semi-serialised state
        also ensure the walking access is loaded

        Parameters:
            state: the state to load
        """

        super().setState(state)

        try:
            self.walkingAccess = []
            for access in state["walkingAccess"]:
                self.walkingAccess.append((access[0], access[1]))
        except:
            self.walkingAccess = []

"""
class GrowRoom(EmptyRoom):
"""

class StorageRoom(EmptyRoom):
    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
        bio=False,
    ):
        super().__init__(xPosition,yPosition,offsetX,offsetY,desiredPosition,bio)
        self.displayChar = (src.interaction.urwid.AttrSpec("#556", "black"), "SG")

        self.objType = "StorageRoom"

    def doBasicSetup(self):
        super().doBasicSetup()

    def addStorageSquare(self,offset,itemType=None,inputSquare=False,outputSquare=False):
        for x in (1,3,5,):
            for y in range(1,6):
                if inputSquare:
                    self.addInputSlot((x+offset[0],y+offset[1],0),itemType)
                elif outputSquare:
                    self.addOutputSlot((x+offset[0],y+offset[1],0),itemType)
                else:
                    self.addStorageSlot((x+offset[0],y+offset[1],0),itemType)
        for x in (2,4,):
            for y in range(1,6):
                self.walkingSpace.add((x+offset[0],y+offset[1],0))

class WorkshopRoom(EmptyRoom):

    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
        bio=False,
    ):
        super().__init__(xPosition,yPosition,offsetX,offsetY,desiredPosition,bio)
        self.displayChar = (src.interaction.urwid.AttrSpec("#556", "black"), "WP")

        self.objType = "WorkshopRoom"
        self.staff = []
        self.duties = ["resource fetching","hauling","clearing","scratch checking","resource gathering","guarding","painting","machine placing"]

    def doBasicSetup(self):
        super().doBasicSetup()

    def addGhulSquare(self,offset,corpseInInventory=True):
        if not "walkingSpace" in self.floorPlan:
            self.floorPlan["walkingSpace"] = set()
        if not "buildSites" in self.floorPlan:
            self.floorPlan["buildSites"] = []
        if not "inputSlots" in self.floorPlan:
            self.floorPlan["inputSlots"] = []
        if not "outputSlots" in self.floorPlan:
            self.floorPlan["outputSlots"] = []

        for x in range(1,6):
            self.floorPlan["walkingSpace"].add((x+offset[0],3+offset[1],0))

        self.floorPlan["inputSlots"].append(((1+offset[0],4+offset[1],0),"Corpse",{"maxAmount":2}))
        self.floorPlan["buildSites"].append(((2+offset[0],4+offset[1],0),"CorpseAnimator",{}))

        if corpseInInventory:
            command = "d"+10*"Kd"+"j"
        else:
            command = "d"+"j"
        self.floorPlan["buildSites"].append(((3+offset[0],4+offset[1],0),"Command",{"extraName":"initialise ghul","command":command}))

        if corpseInInventory:
            command = ""
        else:
            command = "JdJd"
        command += "sdjawwaajjddsj"
        self.floorPlan["buildSites"].append(((4+offset[0],4+offset[1],0),"Command",{"extraName":"repeat command line","command":command}))

        command = "aj"*4+"4d"
        self.floorPlan["buildSites"].append(((5+offset[0],5+offset[1],0),"Command",{"extraName":"run command line","command":command}))
        self.floorPlan["inputSlots"].append(((5+offset[0],4+offset[1],0),"Corpse",{"maxAmount":2}))

        self.floorPlan["buildSites"].append(((2+offset[0],3+offset[1],0),"ScratchPlate",{"commands":{"noscratch":"jjaKsdJsJs"},"settings":{"scratchThreashold":1000}}))

    def addWorkshopSquare(self,offset,machines=None):
        if not "walkingSpace" in self.floorPlan:
            self.floorPlan["walkingSpace"] = set()
        if not "buildSites" in self.floorPlan:
            self.floorPlan["buildSites"] = []
        if not "inputSlots" in self.floorPlan:
            self.floorPlan["inputSlots"] = []
        if not "outputSlots" in self.floorPlan:
            self.floorPlan["outputSlots"] = []

        for y in (2,4,):
            for x in range(1,6):
                self.floorPlan["walkingSpace"].add((x+offset[0],y+offset[1],0))

        machineCounter = 0
        for machine in machines:
            rowheight = machineCounter*2+1

            neededItems = src.items.rawMaterialLookup.get(machine)
            if not neededItems:
                neededItems = ["MetalBars"]

            if len(neededItems) > 1:
                1/0
            elif neededItems[0] == "MetalBars":
                self.floorPlan["inputSlots"].append(((1+offset[0],rowheight+offset[1],0),"Scrap",{}))
                self.floorPlan["buildSites"].append(((2+offset[0],rowheight+offset[1],0),"ScrapCompactor",{}))
            else:
                subMachine = neededItems[0]
                item = src.items.itemMap["Machine"]()
                item.setToProduce(subMachine)
                item.charges = 0
                self.addItem(item,(2+offset[0],rowheight+offset[1],0))

                subNeededItems = src.items.rawMaterialLookup.get(subMachine)
                if not subNeededItems:
                    subNeededItems = ["MetalBars"]

                if len(subNeededItems) > 1:
                    1/0
                self.floorPlan["inputSlots"].append(((1+offset[0],rowheight+offset[1],0),subNeededItems[0],{}))

            self.floorPlan["inputSlots"].append(((3+offset[0],rowheight+offset[1],0),neededItems[0],{}))
            item = src.items.itemMap["Machine"]()
            item.setToProduce(machine)
            item.charges = 0
            self.addItem(item,(4+offset[0],rowheight+offset[1],0))
            self.floorPlan["outputSlots"].append(((5+offset[0],rowheight+offset[1],0),machine,{}))

            machineCounter += 1
            neededItems = src.items.rawMaterialLookup.get(machine)

    def addBigWorkshopSquare(self,offset,machines=None):
        for x in range(1,6):
            self.walkingSpace.add((x+offset[0],3+offset[1],0))
        for position in ((1,2),(1,1),(2,1),(4,1),(5,1),(5,2),(5,4),(5,5),(4,5),(2,5),(1,5),(1,4)):
            self.walkingSpace.add((position[0]+offset[0],position[1]+offset[1],0))

        machineCounter = 0
        for machine in machines:
            item = src.items.itemMap["Machine"]()
            item.setToProduce(machine)
            item.charges = 0
            pos = (3,2,0)
            if machineCounter == 1:
                pos = (3,4,0)
            self.addItem(item,(pos[0]+offset[0],pos[1]+offset[1],0))

            neededItems = src.items.rawMaterialLookup.get(machine)
            if not neededItems:
                neededItems = ["MetalBars"]

            if len(neededItems) > 2:
                1/0

            pos = (3,1,0)
            if machineCounter == 1:
                pos = (3,5,0)
            self.addInputSlot((pos[0]+offset[0],pos[1]+offset[1],0),neededItems[0])

            if len(neededItems) > 1:
                pos = (2,2,0)
                if machineCounter == 1:
                    pos = (2,4,0)
                self.addInputSlot((pos[0]+offset[0],pos[1]+offset[1],0),neededItems[1])

            pos = (4,2,0)
            if machineCounter == 1:
                pos = (4,4,0)
            self.addOutputSlot((pos[0]+offset[0],pos[1]+offset[1],0),machine)

            machineCounter += 1

class ComandCenter(EmptyRoom):

    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
        bio=False,
    ):
        super().__init__(xPosition,yPosition,offsetX,offsetY,desiredPosition,bio)
        self.displayChar = (src.interaction.urwid.AttrSpec("#556", "black"), "CC")

        self.rooms = []
        self.workshopRooms = []
        self.emptyRooms = []
        self.storageRooms = []

        self.walkingSpace = set()
        self.objType = "ComandCenter"

        self.objectListsToStore.append("rooms")

class TeleporterRoom(EmptyRoom):
    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
        bio=False,
    ):
        super().__init__(xPosition,yPosition,offsetX,offsetY,desiredPosition,bio)
        self.displayChar = (src.interaction.urwid.AttrSpec("#3d3", "black"), "TT")

    def reconfigure(self, sizeX=3, sizeY=3, items=[], bio=False, doorPos=[]):
        super().reconfigure(sizeX,sizeY,items,bio,doorPos)

        teleporterArtwork = src.items.itemMap["TeleporterArtwork"]()
        self.addItem(teleporterArtwork,(6,6,0))

class TempleRoom(EmptyRoom):

    chargeStrength = 1
    faction = "Temple"
    objType = "TempleRoom"

    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
        bio=False,
    ):
        super().__init__(xPosition,yPosition,offsetX,offsetY,desiredPosition,bio)
        self.displayChar = (src.interaction.urwid.AttrSpec("#fff", "black"), "§§")

        self.staff = []
        self.duties = []

    def reconfigure(self, sizeX=3, sizeY=3, items=[], bio=False, doorPos=[]):
        super().reconfigure(sizeX,sizeY,items,bio,doorPos)

        for x in range(1,12):
            for y in range(1,12):
                self.walkingSpace.add((x,y,0))

class TrapRoom(EmptyRoom):

    chargeStrength = 1
    faction = "Trap"
    objType = "TrapRoom"

    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
        bio=False,
    ):
        super().__init__(xPosition,yPosition,offsetX,offsetY,desiredPosition,bio)
        self.displayChar = (src.interaction.urwid.AttrSpec("#3d3", "black"), "/\\")

        self.attributesToStore.extend(["faction","chargeStrength","maxElectricalCharges","electricalCharges"])
        self.staff = []
        self.duties = ["clearing","trap setting","guarding","painting"]

        self.electricalCharges = 90
        self.maxElectricalCharges = 250

    def needsCharges(self):
        return  self.electricalCharges < self.maxElectricalCharges

    def changeCharges(self,delta):
        self.electricalCharges += delta
        if self.electricalCharges < 0:
            self.electricalCharges = 0
        if self.electricalCharges > self.maxElectricalCharges:
            self.electricalCharges = self.maxElectricalCharges

    def moveCharacterDirection(self, character, direction):
        oldPos = character.getPosition()

        item = super().moveCharacterDirection(character, direction)

        newPos = character.getPosition()

        if not oldPos == newPos and character.container == self:
            if self.electricalCharges > 0 and not character.faction == self.faction:
                if not self.itemByCoordinates.get(newPos): # don't do damage on filled tiles
                    damage = self.chargeStrength

                    self.addAnimation(character.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "%%")]})
                    self.addAnimation(character.getPosition(),"smoke",damage,{})

                    character.hurt(damage,reason="the floor shocks you")
                    self.electricalCharges -= 1
                    character.awardReputation(amount=2,reason="discharging a trap room",carryOver=True)

                    if src.gamestate.gamestate.mainChar in self.characters:
                        pass
                        """
                        sound = src.interaction.pygame2.mixer.Sound('../Downloads/electroShock.ogg')
                        if src.gamestate.gamestate.mainChar == character:
                            src.interaction.pygame2.mixer.Channel(6).play(sound)
                        else:
                            sound.set_volume(0.5)
                            src.interaction.pygame2.mixer.Channel(6).play(sound)
                        """

        return item

    def reconfigure(self, sizeX=3, sizeY=3, items=[], bio=False, doorPos=[]):
        super().reconfigure(sizeX,sizeY,items,bio,doorPos)

        shocker = src.items.itemMap["Shocker"]()
        self.addItem(shocker,(2,2,0))
        shocker = src.items.itemMap["Shocker"]()
        self.addItem(shocker,(10,2,0))
        shocker = src.items.itemMap["Shocker"]()
        self.addItem(shocker,(2,10,0))
        shocker = src.items.itemMap["Shocker"]()
        self.addItem(shocker,(10,10,0))

        for x in range(1,12):
            for y in range(1,12):
                self.walkingSpace.add((x,y,0))

    def addItems(self, items, actor=None):
        for itemPair in items:
            if self.electricalCharges > 0 and not self.getItemByPosition(itemPair[1]):
                self.electricalCharges -= 1
                if isinstance(actor,src.characters.Character) and not actor.dead:
                    if actor.faction == self.faction:
                        actor.revokeReputation(amount=2,reason="discharging a trap room",carryOver=True)
                    else:
                        actor.awardReputation(amount=2,reason="discharging a trap room",carryOver=True)
                if actor:
                    self.addAnimation(itemPair[1],"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "%%")]})

        super().addItems(items, actor=actor)

class DungeonRoom(Room):
    objType = "DungeonRoom"

    def __init__(
        self,
        ):
        """
        """
        layout = """
           
           
           
           
    .      
           
           
           
           
"""

        super().__init__(
            layout=layout,
            xPosition=0,
            yPosition=0,
            offsetX=0,
            offsetY=0,
            desiredPosition=None,
        )


class StaticRoom(EmptyRoom):
    """
    the rooms used in dungeons
    """
    objType = "StaticRoom"

    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
        depth=1,
    ):
        """
        create room and add special items

        Parameters:
            xPosition: the x position of the room in big coordinates
            yPosition: the y position of the 
            offsetX: the x offset from the position in big coordinates
            offsetY: the y offset from the position in big coordinates
            desiredPosition: the desired position for the room
            depth: the level of this dungeon room
        """
        super().__init__(
            xPosition=xPosition,
            yPosition=yPosition,
            offsetX=offsetX,
            offsetY=offsetY,
            desiredPosition=desiredPosition,
            bio=False,
        )

        self.depth = depth

        self.floorDisplay = [
            (
                src.interaction.urwid.AttrSpec("#00" + str(10 - depth), "black"),
                [".", ",", ":", ";"][depth // 4 % 4] + [".", ",", ":", ";"][depth % 4],
            )
        ]

    # bad code: ugly hack that causes issues
    def moveCharacterDirection(self, character, direction):
        """
        move a character into a direction
        also do collusion detecion between chars
        also advance the room 

        Parameters:
            character: the character to move
            direction: the direction to move the charecter into
        """

        item = super().moveCharacterDirection(character=character, direction=direction)

        self.evolve(character)

        for other in self.characters:
            if other == character:
                continue

            if not (
                character.xPosition == other.xPosition
                and character.yPosition == other.yPosition
                and character.zPosition == other.zPosition
            ):
                continue

            character.collidedWith(other)
            other.collidedWith(character)

        return item

    def evolve(self, character):
        """
        progress the rooms state

        Parameters:
            the character triggering the change
        """

        for character in self.characters:
            character.satiation -= self.depth
            if character.satiation < 1 and not character.godMode:
                character.die()

        for item in self.itemsOnFloor[:]:
            if isinstance(item, src.items.itemMap["StaticMover"]):
                if item.energy > 1:
                    newPos = [item.xPosition, item.yPosition,0]
                    skip = False
                    if character.xPosition < item.xPosition:
                        newPos[0] -= 1
                        skip = True
                    if character.xPosition > item.xPosition:
                        newPos[0] += 1
                        skip = True

                    blocked = False
                    if (
                        newPos[0],
                        newPos[1],
                        0
                    ) in self.itemByCoordinates and self.itemByCoordinates[
                        (newPos[0], newPos[1],0)
                    ]:
                        blocked = True
                    for character in self.characters:
                        if (
                            character.xPosition == newPos[0]
                            and character.yPosition == newPos[1]
                        ):
                            blocked = True
                            character.satiation -= 50
                            item.energy += 5
                            if character.satiation < 1 and not character.godMode:
                                character.die()

                    if blocked:
                        newPos = [item.xPosition, item.yPosition,0]
                        skip = False
                        blocked = False

                    if not skip:
                        if character.yPosition < item.yPosition:
                            newPos[1] -= 1
                        if character.yPosition > item.yPosition:
                            newPos[1] += 1

                    blocked = False
                    if (
                        newPos[0],
                        newPos[1],
                    ) in self.itemByCoordinates and self.itemByCoordinates[
                        (newPos[0], newPos[1])
                    ]:
                        blocked = True
                    for character in self.characters:
                        if (
                            character.xPosition == newPos[0]
                            and character.yPosition == newPos[1]
                        ):
                            blocked = True
                            character.satiation -= 50
                            item.energy += 5
                            if character.satiation < 1 and not character.godMode:
                                character.die()

                    if not blocked:
                        if item.energy:
                            item.energy -= 2
                            self.removeItem(item)
                            self.addItem(item,newPos)

                if (
                    character.yPosition == item.yPosition
                    and abs(character.xPosition - item.xPosition) == 1
                ) or (
                    character.xPosition == item.xPosition
                    and abs(character.yPosition - item.yPosition) == 1
                ):
                    character.satiation -= 10
                    item.energy += 2
                    if character.satiation < 1 and not character.godMode:
                        character.die()

                if (
                    character.yPosition == item.yPosition
                    and abs(character.xPosition - item.xPosition) == 2
                ) or (
                    character.xPosition == item.xPosition
                    and abs(character.yPosition - item.yPosition) == 2
                ):
                    character.satiation -= 5
                    item.energy += 1
                    if character.satiation < 1 and not character.godMode:
                        character.die()
        pass

"""
the armor plates of a mech
"""


class MechArmor(Room):
    objType = "MechArmor"

    """
    create room
    """

    def __init__(
        self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, desiredPosition=None
    ):
        roomLayout = """
XXXXXXXXXXXXXXX
XX X X X X X XX
X X X X X X X X
XXXXXXXXXXXXXXX
XX X X X X X XX
XXXXXXXXXXXXXXX
XX X X X X X XX
X X X X X X X X
XXXXXXXXXXXXXXX
XX X X X X X XX
X X X X X X X X
XXXXXXXXXXXXXXX
XX X X X X X XX
X X X X.X X X.X
XXXXXXX$XXXXXXX
"""
        super().__init__(
            roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.floorDisplay = [src.canvas.displayChars.nonWalkableUnkown]
        self.name = "MechArmor"


"""
a mini mech to drive around with. including boiler and coal storage and furnace fireing npc
"""


class MiniMech(Room):
    objType = "MiniMech"

    """
    create the room and add the npc
    """

    def __init__(
        self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, desiredPosition=None
    ):
        roomLayout = """
XX$XXX
XD..@X
X  . X
XOF.PX
Xmm.PX
XXXXXX
"""
        self.sizeX = 6
        self.sizeY = 6
        super().__init__(
            roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.floorDisplay = [src.canvas.displayChars.nonWalkableUnkown]
        self.engineStrength = 0
        self.name = "MiniMech"

        # add npc
        self.npc = src.characters.Character(
            xPosition=3,
            yPosition=3,
            seed=self.yPosition + 3 * 3 + self.offsetY + 4 * 12,
        )
        self.addCharacter(self.npc, 3, 3)
        self.npc.room = self

        quest = None

        # add dialog options
        self.npc.basicChatOptions.append(
            {"dialogName": "fire the furnaces", "chat": src.chats.StartChat}
        )

    """
    recalculate engine strength
    bad code: should be recalculate
    """

    def changed(self, tag="default", info=None):
        super().changed(tag, info)
        self.engineStrength = 250 * self.steamGeneration

"""
a room to test gameplay concepts
bad code: serves no real function yet
"""


class TutorialMiniBase(Room):
    objType = "TutorialMiniBase"

    """
    create room and add special items
    """

    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
        seed=0,
    ):
        roomLayout = """
XXXXXXXXXXXXX
X           X
X           X
X           X
X .........@X
X .       .vX
X .       ..$
X .        vX
X ......... X
X           X
X           X
X           X
X           X
X           X
X           X
XXXXXXXXXXXXX
"""
        super().__init__(
            roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        itemList = []
        exclude1 = [src.items.Scrap]
        exclude2 = [src.items.Corpse]
        itemList.append(src.items.ScrapCompactor(10, 1))

        machine = src.items.Machine(3, 2, seed=seed)
        machine.setToProduce("Sheet")
        itemList.append(machine)

        machine = src.items.Machine(6, 2, seed=seed)
        machine.setToProduce("Radiator")
        itemList.append(machine)

        machine = src.items.Machine(9, 2, seed=seed)
        machine.setToProduce("Mount")
        itemList.append(machine)

        machine = src.items.Machine(3, 4, seed=seed)
        machine.setToProduce("Stripe")
        itemList.append(machine)

        machine = src.items.Machine(3, 4, seed=seed)
        machine.setToProduce("Bolt")
        itemList.append(machine)

        machine = src.items.Machine(3, 4, seed=seed)
        machine.setToProduce("Rod")
        itemList.append(machine)

        """
        itemList.append(src.items.GameTestingProducer(3,12,seed=seed, possibleSources=[src.items.MetalBars],possibleResults=[src.items.Wall]))
        itemList.append(src.items.GameTestingProducer(6,12,seed=seed, possibleSources=[src.items.MetalBars],possibleResults=[src.items.Door]))
        itemList.append(src.items.GameTestingProducer(9,12,seed=seed, possibleSources=[src.items.MetalBars],possibleResults=[src.items.RoomControls]))

        itemList.append(src.items.GameTestingProducer(3,13,seed=seed, possibleSources=[src.items.MetalBars],possibleResults=[src.items.Boiler]))
        itemList.append(src.items.GameTestingProducer(6,13,seed=seed, possibleSources=[src.items.MetalBars],possibleResults=[src.items.Pile]))
        itemList.append(src.items.GameTestingProducer(9,13,seed=seed, possibleSources=[src.items.MetalBars],possibleResults=[src.items.Furnace]))

        l1Items = [src.items.Sheet,src.items.Rod,src.items.Sheet,src.items.Mount,src.items.Stripe,src.items.Bolt,src.items.Radiator]
        y = 0
        while y < 2:
            x = 0
            while x < 3:
                itemList.append(src.items.GameTestingProducer(3+x*3,2+y,seed=seed, possibleSources=[src.items.MetalBars]*5+l1Items,possibleResults=l1Items))
                x += 1
                seed += 13
            y += 1
            seed += seed%7

        l2Items = [src.items.Tank,src.items.Heater,src.items.Connector,src.items.Pusher,src.items.Puller,src.items.GooFlask]
        y = 0
        while y < 3:
            x = 0
            while x < 3:
                itemList.append(src.items.GameTestingProducer(3+x*3,5+y,seed=seed, possibleSources=l1Items+l2Items, possibleResults=l2Items))
                x += 1
                seed += 13
            y += 1
            seed += seed%7

        l3Items = [src.items.GrowthTank,src.items.Hutch,src.items.Furnace]
        y = 0
        while y < 2:
            x = 0
            while x < 3:
                itemList.append(src.items.GameTestingProducer(3+x*3,9+y,seed=seed, possibleSources=l2Items, possibleResults=l3Items))
                x += 1
                seed += 13
            y += 1
            seed += seed%7
        """

        self.addItems(itemList)
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)


"""
a room to test gameplay concepts
bad code: serves no real function yet
"""


class GameTestingRoom(Room):
    objType = "GameTestingRoom"

    """
    create room and add special items
    """

    def __init__(
        self,
        xPosition=0,
        yPosition=0,
        offsetX=0,
        offsetY=0,
        desiredPosition=None,
        seed=0,
    ):
        roomLayout = """
XXXXXXXXXXXXX
X           X
X           X
X           X
X .........@X
X .       .vX
X .       ..$
X .        vX
X ......... X
X           X
X           X
X           X
X           X
X           X
X           X
XXXXXXXXXXXXX
"""
        super().__init__(
            roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        itemList = []
        exclude1 = [src.items.Scrap]
        exclude2 = [src.items.Corpse]
        itemList.append(src.items.ScrapCompactor(10, 1))

        itemList.append(
            src.items.GameTestingProducer(
                3,
                12,
                seed=seed,
                possibleSources=[src.items.MetalBars],
                possibleResults=[src.items.Wall],
            )
        )
        itemList.append(
            src.items.GameTestingProducer(
                6,
                12,
                seed=seed,
                possibleSources=[src.items.MetalBars],
                possibleResults=[src.items.Door],
            )
        )
        itemList.append(
            src.items.GameTestingProducer(
                9,
                12,
                seed=seed,
                possibleSources=[src.items.MetalBars],
                possibleResults=[src.items.RoomControls],
            )
        )

        itemList.append(
            src.items.GameTestingProducer(
                3,
                13,
                seed=seed,
                possibleSources=[src.items.MetalBars],
                possibleResults=[src.items.Boiler],
            )
        )
        itemList.append(
            src.items.GameTestingProducer(
                6,
                13,
                seed=seed,
                possibleSources=[src.items.MetalBars],
                possibleResults=[src.items.Pile],
            )
        )
        itemList.append(
            src.items.GameTestingProducer(
                9,
                13,
                seed=seed,
                possibleSources=[src.items.MetalBars],
                possibleResults=[src.items.Furnace],
            )
        )

        l1Items = [
            src.items.Sheet,
            src.items.Rod,
            src.items.Sheet,
            src.items.Mount,
            src.items.Stripe,
            src.items.Bolt,
            src.items.Radiator,
        ]
        y = 0
        while y < 2:
            x = 0
            while x < 3:
                itemList.append(
                    src.items.GameTestingProducer(
                        3 + x * 3,
                        2 + y,
                        seed=seed,
                        possibleSources=[src.items.MetalBars] * 5 + l1Items,
                        possibleResults=l1Items,
                    )
                )
                x += 1
                seed += 13
            y += 1
            seed += seed % 7

        l2Items = [
            src.items.Tank,
            src.items.Heater,
            src.items.Connector,
            src.items.Pusher,
            src.items.Puller,
            src.items.GooFlask,
        ]
        y = 0
        while y < 3:
            x = 0
            while x < 3:
                itemList.append(
                    src.items.GameTestingProducer(
                        3 + x * 3,
                        5 + y,
                        seed=seed,
                        possibleSources=l1Items + l2Items,
                        possibleResults=l2Items,
                    )
                )
                x += 1
                seed += 13
            y += 1
            seed += seed % 7

        l3Items = [src.items.GrowthTank, src.items.Hutch, src.items.Furnace]
        y = 0
        while y < 2:
            x = 0
            while x < 3:
                itemList.append(
                    src.items.GameTestingProducer(
                        3 + x * 3,
                        9 + y,
                        seed=seed,
                        possibleSources=l2Items,
                        possibleResults=l3Items,
                    )
                )
                x += 1
                seed += 13
            y += 1
            seed += seed % 7

        self.addItems(itemList)


"""
smart scrap storage
"""


class ScrapStorage(Room):
    objType = "ScrapStorage"

    """
    create room
    """

    def __init__(self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, seed=0):
        roomLayout = """
XXXXXXXXXXXXX
X           X
X           X
X           X
X           X
X           X
X          .$
X           X
X           X
X           X
X           X
X           X
XXXXXXXXXXXXX
"""
        super().__init__(roomLayout, xPosition, yPosition, offsetX, offsetY)
        self.floorDisplay = [src.canvas.displayChars.nonWalkableUnkown]
        self.name = "ScrapStorage"
        self.scrapStored = 0

        # add markers for items
        item = src.items.ScrapCommander(11, 6)
        self.scrapCommander = item
        self.addItems([item])

        self.setScrapAmount(1678)

    def setScrapAmount(self, amount):
        numFields = amount // 20
        fullRows = numFields // 11

        scrapPiles = []
        for x in range(1, fullRows + 1):
            for y in range(1, 12):
                item = src.items.itemMap["Scrap"](x, y, amount=20)
                scrapPiles.append(item)
        self.scrapCommander.numScrapStored = 20 * 11 * fullRows
        self.addItems(scrapPiles)


# mapping from strings to all rooms
# should be extendable
roomMap = {
    "MechArmor": MechArmor,
    "MiniMech": MiniMech,
    "MiniBase": MiniBase,
    "MiniBase2": MiniBase2,
    "StorageRoom": StorageRoom,
    "EmptyRoom": EmptyRoom,
    "GameTestingRoom": GameTestingRoom,
    "ScrapStorage": ScrapStorage,
    "TrapRoom": TrapRoom,
    "TeleporterRoom": TeleporterRoom,
    "TempleRoom": TempleRoom,
    "WorkshopRoom": WorkshopRoom,
    "ComandCenter": ComandCenter,
}


def getRoomFromState(state, terrain=None):
    """
    get item instances from semiserialised state

    Parameters:
        state: the state to set
        terrain: a terrain to place the room on
    """

    room = roomMap[state["objType"]](
        state["xPosition"], state["yPosition"], state["offsetX"], state["offsetY"]
    )
    room.terrain = terrain
    room.setState(state)
    src.saveing.loadingRegistry.register(room)
    return room
