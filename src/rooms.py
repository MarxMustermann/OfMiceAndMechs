"""
eeeeeeend room related code belong here
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
much of this code is currenty not in use and needs to be reintegrated
"""

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
        self.attributesToStore = super().attributesToStore[:]
        self.callbacksToStore = []
        self.objectsToStore = []
        self.tupleDictsToStore = []
        self.tupleListsToStore = []

        super().__init__()

        # initialize attributes
        self.health = 40
        self.desiredPosition = desiredPosition
        self.desiredSteamGeneration = None
        self.layout = layout
        self.hidden = True
        self.itemsOnFloor = []
        self.characters = []
        self.doors = []
        self.xPosition = None
        self.yPosition = None
        self.name = "Room"
        self.open = True
        self.terrain = None
        self.shownQuestmarkerLastRender = False
        self.sizeX = None
        self.sizeY = None
        self.timeIndex = 0
        self.delayedTicks = 0
        self.events = []
        self.floorDisplay = [src.canvas.displayChars.floor]
        self.lastMovementToken = None
        self.chainedTo = []
        self.engineStrength = 0
        self.boilers = []
        self.growthTanks = []
        self.furnaces = []
        self.pipes = []
        self.sprays = []
        self.piles = []
        self.steamGeneration = 0
        self.firstOfficer = None
        self.secondOfficer = None
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.lastRender = None
        self.isContainment = False
        self.listeners = {"default": []}
        self.seed = seed

        # set id
        import uuid

        self.id = uuid.uuid4().hex

        self.itemByCoordinates = {}

        # generate the items the room consists of from definition
        # bad code: lot of redundant code
        self.walkingAccess = []
        lineCounter = 0
        itemsOnFloor = []
        for line in self.layout[1:].split("\n"):
            rowCounter = 0
            for char in line:
                pos = (rowCounter, lineCounter, 0)
                if char in (" ", "."):
                    # skip non items
                    pass
                elif char in ("@",):
                    # add default npcs
                    if (not self.firstOfficer) or (not self.secondOfficer):
                        if not self.firstOfficer:
                            # add first officer
                            npc = src.characters.Character(
                                xPosition=5,
                                yPosition=3,
                                seed=self.xPosition
                                + 2 * self.offsetY
                                + self.offsetX
                                + 2 * self.yPosition,
                            )
                            self.addCharacter(npc, rowCounter, lineCounter)
                            npc.terrain = self.terrain
                            self.firstOfficer = npc
                            quest = src.quests.RoomDuty()
                            npc.assignQuest(quest, active=True)
                        else:
                            # add second officer
                            npc = src.characters.Character(
                                xPosition=6,
                                yPosition=4,
                                seed=self.yPosition
                                + 2 * self.offsetX
                                + self.offsetY
                                + 2 * self.xPosition,
                            )
                            self.addCharacter(npc, rowCounter, lineCounter)
                            npc.terrain = self.terrain
                            self.secondOfficer = npc
                            quest = src.quests.RoomDuty()
                            npc.assignQuest(quest, active=True)
                elif char in ("X", "&"):
                    # add wall
                    itemsOnFloor.append((src.items.itemMap["Wall"](), pos))
                elif char == "$":
                    # add door and mark position as entry point
                    door = src.items.itemMap["Door"]()
                    itemsOnFloor.append((door, pos))
                    self.walkingAccess.append(pos)
                    self.doors.append(door)
                elif char == "P":
                    # add pile and save to list
                    item = src.items.Pile()
                    itemsOnFloor.append((item, pos))
                    self.piles.append(item)
                elif char == "F":
                    # add furnace and save to list
                    item = src.items.Furnace()
                    itemsOnFloor.append((item, pos))
                    self.furnaces.append(item)
                elif char == "#":
                    # add pipe and save to list
                    item = src.items.Pipe()
                    itemsOnFloor.append((item, pos))
                    self.pipes.append(item)
                elif char == "D":
                    # add display
                    item = src.items.RoomControls()
                    itemsOnFloor.append((item, pos))
                elif char == "v":
                    # to be bin
                    item = src.items.Item(display=src.canvas.displayChars.binStorage)
                    itemsOnFloor.append((item, pos))
                elif char == "O":
                    # add pressure Tank
                    item = src.items.Boiler()
                    itemsOnFloor.append((item, pos))
                    self.boilers.append(item)
                elif char == "8":
                    # to be chains
                    item = src.items.Item(display=src.canvas.displayChars.chains)
                    itemsOnFloor.append((item, pos))
                elif char == "I":
                    # to be commlink
                    item = src.items.Commlink()
                    itemsOnFloor.append((item, pos))
                elif char in ["H", "'"]:
                    # add hutch
                    # bad code: handle state some other way
                    mapping = {"H": False, "'": True}
                    src.items.Hutch(activated=mapping[char])
                    itemsOnFloor.append((item, pos))
                elif char == "o":
                    # to be grid
                    item = src.items.Item(display=src.canvas.displayChars.grid)
                    itemsOnFloor.append((item, pos))
                elif char == "a":
                    # to be acid
                    item = src.items.Item(
                        display=src.canvas.displayChars.acids[
                            ((2 * rowCounter) + lineCounter) % 5
                        ]
                    )
                    item.walkable = True
                    itemsOnFloor.append((item, pos))
                elif char == "b":
                    # to be foodstuffs
                    item = src.items.Item(
                        display=src.canvas.displayChars.foodStuffs[
                            ((2 * rowCounter) + lineCounter) % 6
                        ]
                    )
                    itemsOnFloor.append((item, pos))
                elif char == "m":
                    # to be machinery
                    item = src.items.Item(
                        display=src.canvas.displayChars.machineries[
                            ((2 * rowCounter) + lineCounter) % 5
                        ]
                    )
                    itemsOnFloor.append((item, pos))
                elif char == "M":
                    item = src.items.VatMaggot()
                    itemsOnFloor.append((item, pos))
                elif char == "h":
                    # add steam hub
                    item = src.items.Item(display=src.canvas.displayChars.hub)
                    itemsOnFloor.append((item, pos))
                elif char == "i":
                    # add ramp
                    item = src.items.Item(display=src.canvas.displayChars.ramp)
                    itemsOnFloor.append((item, pos))
                elif char in ["q", "r", "s", "t", "u", "z"]:
                    # add special pipe
                    # bad code: pipe connection should be done some other way
                    mapping = {
                        "q": src.canvas.displayChars.pipe_lr,
                        "r": src.canvas.displayChars.pipe_lrd,
                        "s": src.canvas.displayChars.pipe_ld,
                        "t": src.canvas.displayChars.pipe_lu,
                        "u": sr.canvas.displayChars.pipe_ru,
                        "z": src.canvas.displayChars.pipe_ud,
                    }
                    item = src.items.Item(display=mapping[char])
                    item.walkable = True
                    itemsOnFloor.append((item, pos))
                elif char in ["w", "x"]:
                    # add spray
                    # bad code: handle orientation some other way
                    mapping = {"w": "right", "x": "left"}
                    item = src.items.Spray(direction=mapping[char])
                    itemsOnFloor.append((item, pos))
                    self.sprays.append(item)
                elif char == "y":
                    # to be outlet
                    item = src.items.Item(display=src.canvas.displayChars.outlet)
                    itemsOnFloor.append((item, pos))
                elif char == "j":
                    # to be vat snake
                    item = src.items.Item(display=src.canvas.displayChars.vatSnake)
                    itemsOnFloor.append((item, pos))
                elif char == "c":
                    # add corpse
                    item = src.items.Corpse()
                    itemsOnFloor.append((item, pos))
                elif char in ["Ö", "ö"]:
                    # add growth tank
                    # bad code: special chars should not be used in code
                    # bad code: handle state some other way
                    mapping = {"Ö": True, "ö": False}
                    item = src.items.GrowthTank(filled=mapping[char])
                    self.growthTanks.append(item)
                    itemsOnFloor.append((item, pos))
                elif char == "B":
                    # add to be barricade
                    item = src.items.Item(display=src.canvas.displayChars.barricade)
                    item.walkable = True
                    itemsOnFloor.append((item, pos))
                else:
                    # add undefined stuff
                    item = src.items.Item(
                        display=src.canvas.displayChars.randomStuff2[
                            ((2 * rowCounter) + lineCounter) % 10
                        ]
                    )
                    itemsOnFloor.append((item, pos))
                rowCounter += 1
                self.sizeX = rowCounter
            lineCounter += 1
        self.sizeY = lineCounter - 1

        # extract waypoints for default path from layout
        rawWalkingPath = []
        lineCounter = 0
        for line in self.layout[1:].split("\n"):
            rowCounter = 0
            for char in line:
                if char == ".":
                    rawWalkingPath.append((rowCounter, lineCounter))
                rowCounter += 1
            lineCounter += 1

        # start path with first waypoint
        self.walkingPath = []
        startWayPoint = rawWalkingPath[0]
        endWayPoint = rawWalkingPath[0]
        self.walkingPath.append(rawWalkingPath[0])
        rawWalkingPath.remove(rawWalkingPath[0])

        # add remaining waypoints to path
        while 1 == 1:
            # get neighbour positions
            # bad code: should be in position object
            endWayPoint = self.walkingPath[-1]
            east = (endWayPoint[0] + 1, endWayPoint[1])
            west = (endWayPoint[0] - 1, endWayPoint[1])
            south = (endWayPoint[0], endWayPoint[1] + 1)
            north = (endWayPoint[0], endWayPoint[1] - 1)

            # extend path
            if east in rawWalkingPath:
                self.walkingPath.append(east)
                rawWalkingPath.remove(east)
            elif west in rawWalkingPath:
                self.walkingPath.append(west)
                rawWalkingPath.remove(west)
            elif south in rawWalkingPath:
                self.walkingPath.append(south)
                rawWalkingPath.remove(south)
            elif north in rawWalkingPath:
                self.walkingPath.append(north)
                rawWalkingPath.remove(north)
            else:
                break

        # add the items generated earlier
        self.addItems(itemsOnFloor)

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
            ]
        )

    def getPositionWalkable(self,pos):
        items = self.getItemByPosition(pos)
        if len(items) > 15:
            return False
        for item in items:
            if item.walkable == False:
                return False
        return True

    def damage(self):
        """
        damage the room
        """
        self.health -= 1
        if self.itemsOnFloor:
            import random

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

        self.requestRedraw()
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

        # store the substates
        state["objType"] = self.objType

        state["walkingAccess"] = self.walkingAccess

        state["eventIds"] = eventIds
        state["eventStates"] = eventStates
        state["itemIds"] = itemIds
        state["itemStates"] = itemStates
        state["characterIds"] = charIds
        state["characterStates"] = charStates

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

        # update changed chars
        if "changedChars" in state:
            for char in self.characters:
                if char.id in state["changedChars"]:
                    char.setState(state["charStates"][char.id])

        # remove chars
        if "removedChars" in state:
            for char in self.characters[:]:
                if char.id in state["removedChars"]:
                    self.removeCharacter(char)

        # add new chars
        if "newChars" in state:
            for charId in state["newChars"]:
                charState = state["charStates"][charId]
                char = src.characters.Character()
                char.setState(charState)
                src.saveing.loadingRegistry.register(char)
                self.addCharacter(char, charState["xPosition"], charState["yPosition"])

        # add new events
        if "newEvents" in state:
            for eventId in state["newEvents"]:
                eventState = state["eventStates"][eventId]
                event = src.events.getEventFromState(eventState)
                self.addEvent(event)

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
                char = src.characters.Character()
                char.setState(charState)
                src.saveing.loadingRegistry.register(char)
                self.addCharacter(char, charState["xPosition"], charState["yPosition"])

        self.forceRedraw()

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

    def render(self):
        """
        render the room

        Returns:
            the rendered room
        """

        # skip rendering
        # if self.lastRender:
        #    return self.lastRender

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
                        subChars.append(fixedChar)
                    else:
                        subChars.append(
                            self.floorDisplay[
                                (j + i + self.timeIndex * 2) % len(self.floorDisplay)
                            ]
                        )
                chars.append(subChars)

            # draw items
            for item in self.itemsOnFloor:
                try:
                    chars[item.yPosition][item.xPosition] = item.render()
                except:
                    src.logger.debugMessages.append("room drawing failed")

            # draw characters
            for character in self.characters:
                if character.yPosition < len(chars) and character.xPosition < len(
                    chars[character.yPosition]
                ):
                    if not "city" in character.faction or not character.charType == "Character":
                        chars[character.yPosition][character.xPosition] = character.display
                    else:
                        chars[character.yPosition][character.xPosition] = (src.interaction.urwid.AttrSpec("#3f3", "black"), "@ ")
                        if character.faction.endswith("#1"):
                            chars[character.yPosition][character.xPosition][0].fg = "#066"
                        if character.faction.endswith("#2"):
                            chars[character.yPosition][character.xPosition][0].fg = "#006"
                        if character.faction.endswith("#3"):
                            chars[character.yPosition][character.xPosition][0].fg = "#060"
                        if character.faction.endswith("#4"):
                            chars[character.yPosition][character.xPosition][0].fg = "#082"
                        if character.faction.endswith("#5"):
                            chars[character.yPosition][character.xPosition][0].fg = "#028"
                        if character.faction.endswith("#6"):
                            chars[character.yPosition][character.xPosition][0].fg = "#088"
                        if character.faction.endswith("#7"):
                            chars[character.yPosition][character.xPosition][0].fg = "#086"
                        if character.faction.endswith("#8"):
                            chars[character.yPosition][character.xPosition][0].fg = "#068"
                        if character.faction.endswith("#9"):
                            chars[character.yPosition][character.xPosition][0].fg = "#0a0"
                        if character.faction.endswith("#10"):
                            chars[character.yPosition][character.xPosition][0].fg = "#00a"
                        if character.faction.endswith("#11"):
                            chars[character.yPosition][character.xPosition][0].fg = "#0a6"
                        if character.faction.endswith("#12"):
                            chars[character.yPosition][character.xPosition][0].fg = "#06a"
                        if character.faction.endswith("#13"):
                            chars[character.yPosition][character.xPosition][0].fg = "#08a"
                        if character.faction.endswith("#14"):
                            chars[character.yPosition][character.xPosition][0].fg = "#0a6"
                        if character.faction.endswith("#15"):
                            chars[character.yPosition][character.xPosition][0].fg = "#0aa"
                        if character.showThinking:
                            chars[character.yPosition][character.xPosition][0].bg = "#333"
                            character.showThinking = False
                        if character.showGotCommand:
                            chars[character.yPosition][character.xPosition][0].bg = "#fff"
                            character.showGotCommand = False
                        if character.showGaveCommand:
                            chars[character.yPosition][character.xPosition][0].bg = "#855"
                            character.showGaveCommand = False
                else:
                    src.logger.debugMessages.append(
                        "chracter is rendered outside of room"
                    )

            """
            # draw quest markers
            # bad code: should be an overlay
            if src.gamestate.gamestate.mainChar.room == self:
                if len(src.gamestate.gamestate.mainChar.quests):
                    # show the questmarker every second turn for blinking effect
                    if not self.shownQuestmarkerLastRender:
                        self.shownQuestmarkerLastRender = True

                        # mark the target of each quest
                        # bad code: does not work with meta quests
                        for quest in src.gamestate.gamestate.mainChar.quests:
                            if not quest.active:
                                continue

                            # mark secondary quest targets using background colour
                            try:
                                import urwid

                                display = chars[quest.dstY][quest.dstX]
                                chars[quest.dstY][
                                    quest.dstX
                                ] = src.canvas.displayChars.questTargetMarker
                                if isinstance(display, int):
                                    display = src.canvas.displayChars.indexedMapping[
                                        display
                                    ]
                                if isinstance(display, str):
                                    display = (
                                        urwid.AttrSpec("default", "black"),
                                        display,
                                    )
                                chars[quest.dstY][quest.dstX] = (
                                    urwid.AttrSpec(display[0].foreground, "#323"),
                                    display[1],
                                )
                            except:
                                pass

                            # mark primary quest target with the target marker
                            try:
                                chars[src.gamestate.gamestate.mainChar.quests[0].dstY][
                                    src.gamestate.gamestate.mainChar.quests[0].dstX
                                ] = src.canvas.displayChars.questTargetMarker
                            except:
                                pass

                        # highlight the path to the quest target using background color
                        try:
                            path = self.calculatePath(
                                src.gamestate.gamestate.mainChar.xPosition,
                                src.gamestate.gamestate.mainChar.yPosition,
                                src.gamestate.gamestate.mainChar.quests[0].dstX,
                                src.gamestate.gamestate.mainChar.quests[0].dstY,
                                self.walkingPath,
                            )
                            for item in path:
                                import urwid

                                display = chars[item[1]][item[0]]
                                if isinstance(display, int):
                                    display = src.canvas.displayChars.indexedMapping[
                                        display
                                    ]
                                if isinstance(display, str):
                                    display = (
                                        urwid.AttrSpec("default", "black"),
                                        display,
                                    )
                                chars[item[1]][item[0]] = (
                                    urwid.AttrSpec(display[0].foreground, "#333"),
                                    display[1],
                                )
                        except:
                            pass
                    #  don't show the questmarker every second turn for blinking effect
                    else:
                        self.shownQuestmarkerLastRender = False
            """

            # draw main char
            if src.gamestate.gamestate.mainChar in self.characters:
                if src.gamestate.gamestate.mainChar.yPosition < len(
                    chars
                ) and src.gamestate.gamestate.mainChar.xPosition < len(
                    chars[src.gamestate.gamestate.mainChar.yPosition]
                ):
                    """
                    chars[src.gamestate.gamestate.mainChar.yPosition][
                        src.gamestate.gamestate.mainChar.xPosition
                    ] = src.gamestate.gamestate.mainChar.display
                    """
                    chars[src.gamestate.gamestate.mainChar.yPosition][src.gamestate.gamestate.mainChar.xPosition] = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@ ")
                else:
                    src.logger.debugMessages.append(
                        "chracter is rendered outside of room"
                    )

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

        # cache rendering result
        self.lastRender = chars

        return chars

    # bad code: game is always redrawing
    def forceRedraw(self):
        """
        drop rendering cache
        """

        self.lastRender = None

    # bad code: game is always redrawing
    def requestRedraw(self):
        """
        maybe drop rendering cache
        """

        # if not self.hidden:
        if 1 == 1:
            self.lastRender = None

    def addCharacter(self, character, x, y, noRegister=False):
        """
        teleport character into the room

        Parameters:
            character: the character to teleport
            x: the x coordiate to teleport to
            y: the y coordiate to teleport to
        """

        self.characters.append(character)
        character.room = self
        character.xPosition = x
        character.yPosition = y
        character.path = []
        self.changed("entered room", character)
        if not noRegister:
            src.interaction.multi_chars.add(character)

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

    def addItem(self, item, pos):
        """
        add a item to the room

        Parameters:
            item: the item to add
            pos: the position to add the item on
        """

        self.addItems([(item, pos)])

    def addItems(self, items):
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

            item.container = self
            item.setPosition(pos)

            if pos in self.itemByCoordinates:
                self.itemByCoordinates[pos].insert(0, item)
            else:
                self.itemByCoordinates[pos] = [item]

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
        elif direction == "north":
            newYPos -= 1
        elif direction == "west":
            newXPos -= 1
        elif direction == "east":
            newXPos += 1
        else:
            src.logger.debugMessages.append("invalid movement direction")

        newPosition = (newXPos, newYPos, 0)

        itemList = self.terrain.getItemByPosition(newPosition)
        for item in itemList:
            if not item.walkable:
                return item

        if len(itemList) > 15:
            return itemList[0]

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
                if not item.walkable:
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

    # obsolete: not really used anymore
    def applySkippedAdvances(self):
        """
        advance the room to current tick
        """

        while self.delayedTicks > 0:
            for character in self.characters:
                character.advance()
            self.delayedTicks -= 1

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

    def advance(self):
        """
        advance the room one step
        """

        # change own state
        self.timeIndex += 1
        self.requestRedraw()

        # log events that were not handled properly
        while self.events and self.timeIndex > self.events[0].tick:
            event = self.events[0]
            src.logger.debugMessages.append(
                "something went wrong and event" + str(event) + "was skipped"
            )
            self.events.remove(event)

        # handle events
        while self.events and self.timeIndex == self.events[0].tick:
            event = self.events[0]
            event.handleEvent()
            self.events.remove(event)

        # do next step new
        # bad code: sneakily disabled the mechanism for delaying calculations
        if not self.hidden or 1 == 1:
            # redo delayed calculation
            if self.delayedTicks > 0:
                self.applySkippedAdvances()

            # advance each character
            for character in self.characters:
                character.advance()
        # do next step later
        else:
            self.delayedTicks += 1

    # bad code: should do something or be deleted
    def calculatePathMap(self):
        """
        dummy to prevent crashes
        """
        pass

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
        self.roomLayout = """
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
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
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
        self.doors[0].walkable = True

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

        self.roomLayout = """
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
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.doors[0].walkable = True

        healingstation = src.items.itemMap["HealingStation"]()
        corpseShredder = src.items.itemMap["CorpseShredder"]()
        corpse = src.items.itemMap["Corpse"]()
        corpse.charges = 300
        sunScreen = src.items.itemMap["SunScreen"]()
        vial = src.items.itemMap["Vial"]()
        import random

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

        self.roomLayout = """
XXX
X.$
XXX
"""
        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
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

class DungeonRoom(Room):
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
        import urwid

        self.floorDisplay = [
            (
                urwid.AttrSpec("#00" + str(10 - depth), "black"),
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
            if isinstance(item, src.items.StaticMover):
                if item.energy > 1:
                    newPos = [item.xPosition, item.yPosition]
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

                    if blocked:
                        newPos = [item.xPosition, item.yPosition]
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
                            item.xPosition = newPos[0]
                            item.yPosition = newPos[1]
                            self.addItems([item])

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


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# rooms below the point are not in use and need to be reintegrated
# this will require heavy rewrites, so please ignore unless you plan to rewrite
# the last few lines of this file are in use

"""
the machine room used in the tutorial
bad pattern: should be abstracted
bad code: name and classname do not agree
"""


class TutorialMachineRoom(Room):
    objType = "TutorialMachineRoom"

    """
    create room and add special items
    """

    def __init__(
        self, xPosition=0, yPosition=1, offsetX=4, offsetY=0, desiredPosition=None
    ):
        roomLayout = """
X#XX$XXX#X
X#Pv vID#X
X#......#X
X .@@  . X
X .HHHH. X
X ...... X
XFFFFFFFFX
XOOOOOOOOX
X#########
XXXXXXXXXX
"""
        super().__init__(
            roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.name = "Boilerroom"

        # generate special items
        self.lever1 = src.items.Lever(1, 5, "engine control")
        self.lever2 = src.items.Lever(8, 5, "boarding alarm")
        coalPile1 = src.items.Pile(8, 3, "coal Pile1", src.items.Coal)
        coalPile2 = src.items.Pile(8, 4, "coal Pile2", src.items.Coal)
        coalPile3 = src.items.Pile(1, 3, "coal Pile1", src.items.Coal)
        coalPile4 = src.items.Pile(1, 4, "coal Pile2", src.items.Coal)

        # actually add items
        self.addItems(
            [self.lever1, self.lever2, coalPile1, coalPile2, coalPile3, coalPile4]
        )

        self.furnaceQuest = None

    """
    move from training to mocked up day to day activity
    bad code: this should happen in story
    """

    def endTraining(self):

        """
        event for changing the requirements regulary
        """

        class ChangeRequirements(object):

            """
            state initialization
            """

            def __init__(subself, tick):
                subself.tick = tick
                self.loop = [0, 1, 2, 7, 4, 3, 5, 6]

            """
            change the requirement and shedule next event
            """

            def handleEvent(subself):
                # change the requirement
                index = self.loop.index(self.desiredSteamGeneration)
                index += 1
                if index < len(self.loop):
                    src.logger.debugMessages.append(
                        "*comlink*: changed orders. please generate "
                        + str(self.loop[index])
                        + " power"
                    )
                    self.desiredSteamGeneration = self.loop[index]
                else:
                    self.desiredSteamGeneration = self.loop[0]

                # schedule more changes
                self.changed()
                self.addEvent(ChangeRequirements(self.timeIndex + 50))

        # add production requirement and schedule changes
        self.desiredSteamGeneration = 0
        self.changed()
        self.addEvent(ChangeRequirements(self.timeIndex + 20))

    """
    handle changed steam production/demand
    """

    def changed(self, tag="default", info=None):
        super().changed(tag, info)

        # notify vat
        # bad code: vat should listen
        if self.terrain:
            self.terrain.tutorialVatProcessing.recalculate()

        # bad code: should hav an else branch
        if self.desiredSteamGeneration:
            # reset quest for firing the furnaces
            if not self.desiredSteamGeneration == self.steamGeneration:
                # reset order for firing the furnaces
                if self.secondOfficer:
                    if self.furnaceQuest:
                        self.furnaceQuest.deactivate()
                        self.furnaceQuest.postHandler()
                    self.furnaceQuest = src.quests.KeepFurnacesFiredMeta(
                        self.furnaces[: self.desiredSteamGeneration]
                    )
                    self.secondOfficer.assignQuest(self.furnaceQuest, active=True)
            # acknowledge success
            else:
                # bad pattern: tone is way too happy
                src.logger.debugMessages.append(
                    "we did it! "
                    + str(self.desiredSteamGeneration)
                    + " instead of "
                    + str(self.steamGeneration)
                )


"""
a room to waste cpu power. used for performance testing
bad code: does not actually work
"""


class CpuWasterRoom(Room):
    objType = "CpuWasterRoom"

    """
    create room and add patroling npcs
    """

    def __init__(self, xPosition=0, yPosition=0, offsetX=0, offsetY=0):
        self.roomLayout = """
XX$XXXXXXX
Xv vD????X
X?......PX
X?.PPPP.PX
X?.????.#X
X?.???P.#X
X?.?X??.#X
X?......#X
X? XXXXX#X
XXXXXXXXXX
"""
        super().__init__(
            self.roomLayout,
            xPosition,
            yPosition,
            offsetX,
            offsetY,
            desiredPosition=None,
        )
        self.name = "CpuWasterRoom"

        """
        add a patrolling npc
        """

        def addNPC(x, y):
            # generate quests
            # bad code: replace with patrol quest since it's actually bugging
            quest1 = src.quests.MoveQuestMeta(self, 2, 2)
            quest2 = src.quests.MoveQuestMeta(self, 2, 7)
            quest3 = src.quests.MoveQuestMeta(self, 7, 7)
            quest4 = src.quests.MoveQuestMeta(self, 7, 2)
            quest1.followUp = quest2
            quest2.followUp = quest3
            quest3.followUp = quest4

            # add npc
            npc = src.characters.Character(
                xPosition=x,
                yPosition=y,
                seed=self.yPosition + 3 * x + self.offsetY + 4 * y,
            )
            self.addCharacter(npc, x, y)
            npc.room = self
            npc.assignQuest(quest1)
            return npc

        # add a bunch of npcs
        addNPC(2, 2)
        addNPC(3, 2)
        addNPC(4, 2)
        addNPC(5, 2)
        addNPC(6, 2)
        addNPC(7, 2)
        addNPC(7, 3)
        addNPC(7, 4)
        addNPC(7, 5)
        addNPC(7, 6)


"""
the living space for soldiers
"""


class InfanteryQuarters(Room):
    objType = "InfanteryQuarters"

    """
    create room
    """

    def __init__(
        self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, desiredPosition=None
    ):
        self.roomLayout = """
XX$X&&XXXXX
XX PPPPPPXX
X@.......DX
X'.''@''.IX
X'.'' ''.|X
X'.'' ''.|X
X'.'' ''.IX
X .......DX
XXXXXXXXXXX
"""
        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.name = "Infanteryquarters"

        # make personal military personal
        self.firstOfficer.isMilitary = True
        self.secondOfficer.isMilitary = True
        self.onMission = False

        # set up monitoring for doors
        for item in self.itemsOnFloor:

            # ignore non doors
            if not isinstance(item, src.items.Door):
                continue

            thisRoundsItem = item  # nontrivial: this forces a different namespace each run of the loop

            """
            scold non military personal opening the door and close it again
            """

            def handleDoorOpened():

                # ensure the rooms personal doesn't scold itself
                # bad code: doesn't actually check who opens the door
                if self.onMission:
                    return

                # only to something if door is open
                if not thisRoundsItem.walkable:
                    return

                # scold/punish the player
                # bad code: assumes the player opened the door
                src.gamestate.gamestate.mainChar.addMessage(
                    self.firstOfficer.name
                    + "@"
                    + self.secondOfficer.name
                    + ": close the door"
                )
                src.gamestate.gamestate.mainChar.revokeReputation(
                    amount=5, reason="disturbing a military area"
                )
                src.gamestate.gamestate.mainChar.addMessage(
                    self.firstOfficer.name + ": military area. Do not enter."
                )

                # make second officer close the door and return to start position
                quest = src.quests.MoveQuestMeta(self, 5, 3)
                self.secondOfficer.assignQuest(quest, active=True)
                quest = src.quests.ActivateQuestMeta(thisRoundsItem)
                self.secondOfficer.assignQuest(quest, active=True)

            # start watching door
            item.addListener(handleDoorOpened)

        """
        kill non miltary personal entering the room
        """

        def enforceMilitaryRestriction(character):
            # do nothing if character is military
            if character.isMilitary:
                return

            # make second officer kill the intruder
            quest = src.quests.MurderQuest(character)
            self.secondOfficer.assignQuest(quest, active=True)

            # show fluff
            character.addMessage(
                self.firstOfficer.name
                + "@"
                + self.secondOfficer.name
                + ": perimeter breached. neutralize threat."
            )

            # punish player
            character.revokeReputation(amount=100, reason="breaching a military area")

            """
            stop running after character left the room
            """

            def abort(characterLeaving):
                # check it the target left the room
                if not characterLeaving == character:
                    return

                # show fluff
                character.addMessage(
                    self.firstOfficer.name
                    + "@"
                    + self.secondOfficer.name
                    + ": stop persuit. return to position."
                )

                # remove self from listeners
                self.delListener(abort, "left room")

                # remove kill quest
                # bad code: actually just removes the first quest
                quest = self.secondOfficer.quests[0]
                quest.deactivate()
                self.secondOfficer.quests.remove(quest)

                # make officer move back to position
                quest = src.quests.MoveQuestMeta(self, 5, 3)
                self.secondOfficer.assignQuest(quest, active=True)

            # make second officer kill character
            quest = src.quests.MurderQuest(character)
            self.secondOfficer.assignQuest(quest, active=True)

            # try make character kill self
            quest = src.quests.MurderQuest(character)
            character.assignQuest(quest, active=True)

            # watch for character leaving the room
            self.addListener(abort, "left room")

        # watch for character entering the room
        self.addListener(enforceMilitaryRestriction, "entered room")

    """
    kill characters wandering the terrain without floor permit
    """

    def enforceFloorPermit(self, character):
        # do nothing if character has floor permit
        if character.hasFloorPermit:
            return

        # show fluff
        # bad code: produces an announcement for each room
        character.addMessage("O2 military please enforce floor permit")

        # make second officer move back to position after kill
        quest = src.quests.MoveQuestMeta(self, 5, 3)
        self.secondOfficer.assignQuest(quest, active=True)

        # make second officer kill character
        quest = src.quests.MurderQuest(character)
        self.secondOfficer.assignQuest(quest, active=True)

        # try to make second kill self
        quest = src.quests.MurderQuest(character)
        character.assignQuest(quest, active=True)
        self.onMission = True


"""
the room where raw goo is processed into eatable form
bad code: has no actual function yet
"""


class VatProcessing(Room):
    objType = "VatProcessing"

    """
    create room and add special item
    """

    def __init__(
        self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, desiredPosition=None
    ):
        self.roomLayout = """
XXXXXXXXXX
XaaaaaaaaX
#prqqrqqsX
XazayzayzX
XauwauwxtX
XaaayaayaX
#psBBBBBBX
Xmhm@...DX
Xmmmv.v.IX
XXXXX$XXXX
"""
        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )

        # add special items
        self.gooDispenser = src.items.GooDispenser(6, 7)
        self.addItems([self.gooDispenser])
        self.name = "vat processing"

        firstOfficerDialog = {
            "dialogName": "Do you need some help?",
            "chat": src.chats.ConfigurableChat,
            "params": {
                "text": "yes. I regulary have to request new goo Flasks, since the workers sometimes drop them. Collect them for me.",
                "info": [],
            },
        }
        firstOfficerDialog["params"]["info"].append(
            {
                "name": "I have a goo flask for you",
                "text": "gret. Give it to me",
                "type": "text",
                "trigger": {"container": self, "method": "removeGooFlask"},
            }
        )
        self.firstOfficer.basicChatOptions.append(firstOfficerDialog)

    def removeGooFlask(self):
        toRemove = None
        for item in src.gamestate.gamestate.mainChar.inventory:
            if isinstance(item, src.items.GooFlask):
                toRemove = item
        if toRemove:
            src.gamestate.gamestate.mainChar.inventory.remove(toRemove)
            src.gamestate.gamestate.mainChar.awardReputation(
                amount=1, reason="supplying a Goo Flask"
            )

    """
    recalculate sprayer state
    bad code: sprayer should be listening
    """

    def recalculate(self):
        for spray in self.sprays:
            spray.recalculate()


"""
the room where organic material is fermented to raw goo
bad code: has no actual function yet
"""


class VatFermenting(Room):
    objType = "VatFermenting"

    """
    create room and set some state
    """

    def __init__(
        self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, desiredPosition=None
    ):
        self.roomLayout = """
XXXXXXXXXX
X  Mb jjjX
XM ......X
X b.b bb.X
X ..Mc b.X
XM.b  jM.X
X ..Mb b.X
X@b......X
## ..Mv ##
XXXXX$XXXX
"""
        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.isContainment = True
        self.floorDisplay = src.canvas.displayChars.acids
        self.name = "Vat fermenting"


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
        self.roomLayout = """
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
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
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
        self.roomLayout = """
XX$XXX
XD..@X
X  . X
XOF.PX
Xmm.PX
XXXXXX
"""
        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
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
        self.roomLayout = """
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
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
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
        self.roomLayout = """
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
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
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
a lab for behaviour testing
bad code: is basically not implemented yet
bad code: is misused as a target/source for transportation jobs
"""


class ChallengeRoom(Room):
    objType = "ChallengeRoom"

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
        self.roomLayout = """
XXXXXXXXXX
X XX  @  X
XXXX.... X
X XX.  . X
XXXX.  . X
X XX.  . X
XXXX.... X
X XX     X
XXXX   @ X
X        X
X        X
X        X
$        X
XXXXXXXXXX
"""
        super().__init__(
            self.roomLayout,
            xPosition,
            yPosition,
            offsetX,
            offsetY,
            desiredPosition,
            seed=seed,
        )

        # bad code: the markers are not used anywhere
        self.bean = src.items.MarkerBean(4, 2)
        beanPile = src.items.Pile(4, 1, "markerPile", src.items.MarkerBean)
        self.addItems([self.bean, beanPile])

        self.name = "Challenge"

        # unbolt all items in the room
        for item in self.itemsOnFloor:
            if item.xPosition == 0 or item.yPosition == 0:
                continue
            if item.xPosition == self.sizeX - 1 or item.yPosition == self.sizeY - 1:
                continue
            item.bolted = False

        self.firstOfficer.basicChatOptions.append(
            {
                "dialogName": "I need to leave this room, can you help?",
                "chat": src.chats.ConfigurableChat,
                "params": {"text": "yes", "info": []},
            }
        )
        self.secondOfficer.basicChatOptions.append(
            {
                "dialogName": "I need to leave this room, can you help?",
                "chat": src.chats.ConfigurableChat,
                "params": {"text": "I dont know how to help you with this", "info": []},
            }
        )

        firstOfficerDialog = {
            "dialogName": "Do you need more equipment?",
            "chat": src.chats.ConfigurableChat,
            "params": {"text": "yes", "info": []},
        }
        firstOfficerDialog["params"]["info"].append(
            {
                "name": "I want to use my tokens",
                "text": "Done",
                "type": "text",
                "trigger": {"container": self, "method": "removeTokensFirstOfficer"},
            }
        )
        self.firstOfficer.basicChatOptions.append(firstOfficerDialog)

        secondOfficerDialog = {
            "dialogName": "Do you need more equipment?",
            "chat": src.chats.ConfigurableChat,
            "params": {"text": "yes", "info": []},
        }

        self.secondOfficerRemovesPipes = False
        self.secondOfficerRemovesGooFlasks = False
        self.secondOfficerRemovesTokens = False

        self.secondOfficerRemovesPipes = True
        if seed % 3 == 2 or seed % 7 == 0:
            self.secondOfficerRemovesGooFlasks = True
        if seed % 2 == 0 or seed % 5 == 2:
            self.secondOfficerRemovesTokens = True

        if self.secondOfficerRemovesPipes:
            secondOfficerDialog["params"]["info"].append(
                {
                    "name": "Please take my pipes",
                    "text": "Offer accepted",
                    "type": "text",
                    "trigger": {
                        "container": self,
                        "method": "removePipesSecondOfficer",
                    },
                }
            )
        if self.secondOfficerRemovesGooFlasks:
            secondOfficerDialog["params"]["info"].append(
                {
                    "name": "Please take my goo flasks",
                    "text": "Offer accepted",
                    "type": "text",
                    "trigger": {
                        "container": self,
                        "method": "removeGooFlaskSecondOfficer",
                    },
                }
            )
        if self.secondOfficerRemovesTokens:
            secondOfficerDialog["params"]["info"].append(
                {
                    "name": "I want to use my tokens",
                    "text": "Done",
                    "type": "text",
                    "trigger": {
                        "container": self,
                        "method": "removeTokensSecondOfficer",
                    },
                }
            )
        secondOfficerDialog["params"]["info"].append(
            {
                "name": "Take anything you like",
                "text": "Offer accepted",
                "type": "text",
                "trigger": {
                    "container": self,
                    "method": "removeEverythingSecondOfficer",
                },
            }
        )
        self.secondOfficer.basicChatOptions.append(secondOfficerDialog)

        items = []
        yPosition = 1
        item = src.items.Furnace(1, yPosition)
        items.append(item)
        yPosition += 2
        if seed % 5 == 3:
            item = src.items.Furnace(1, yPosition)
            items.append(item)
            yPosition += 2
        if seed % 3 == 1:
            item = src.items.Furnace(1, yPosition)
            items.append(item)
            yPosition += 2
        if seed % 2 == 1:
            item = src.items.Furnace(1, yPosition)
            items.append(item)
            yPosition += 2
        self.addItems(items)

        positions = []
        self.labyrinthWalls = []
        counter = 0
        xPosition = 5
        yPosition = 3
        numItems = 15 + seed % 17
        while counter < numItems:
            xPosition = 1 + (counter * 2 + seed + yPosition) % 20 % 8
            yPosition = 9 + (counter + seed + xPosition) % 17 % 4

            if counter in [2, 5]:
                item = src.items.GooFlask(xPosition, yPosition)
                item.charges = 1
            if (xPosition, yPosition) in positions:
                seed = seed + 1
                continue
            else:
                positions.append((xPosition, yPosition))
            if counter in [1]:
                item = src.items.GooFlask(xPosition, yPosition)
                item.charges = 1
            elif counter % 5 == 1:
                if counter % 3 == 0:
                    token = src.items.Token(xPosition, yPosition)
                    self.addItems([token])
                item = src.items.Pipe(xPosition, yPosition)
            else:
                if counter % 7 == 5:
                    token = src.items.Token(xPosition, yPosition)
                    self.addItems([token])
                item = src.items.Wall(xPosition, yPosition)
            item.bolted = False
            self.labyrinthWalls.append(item)
            counter += 1
        self.addItems(self.labyrinthWalls)

        numItems = seed % 9
        counter = 0
        while counter < numItems:
            item = src.items.GooFlask(None, None)
            self.secondOfficer.inventory.append(item)
            counter += 1

    def removePipesSecondOfficer(self):
        toRemove = []
        for item in src.gamestate.gamestate.mainChar.inventory:
            if isinstance(item, src.items.Pipe):
                toRemove.append(item)
        for item in toRemove:
            if len(self.secondOfficer.inventory) < 10:
                src.gamestate.gamestate.mainChar.inventory.remove(item)
                self.secondOfficer.inventory.append(item)

    def removeGooFlaskSecondOfficer(self):
        toRemove = []
        for item in src.gamestate.gamestate.mainChar.inventory:
            if isinstance(item, src.items.GooFlask):
                toRemove.append(item)
        for item in toRemove:
            if len(self.secondOfficer.inventory) < 10:
                src.gamestate.gamestate.mainChar.inventory.remove(item)
                self.secondOfficer.inventory.append(item)

    def removeTokensFirstOfficer(self):
        toRemove = []
        numTokens = 0
        for item in src.gamestate.gamestate.mainChar.inventory:
            if isinstance(item, src.items.Token):
                toRemove.append(item)
                numTokens += 1
        for item in toRemove:
            if len(self.firstOfficer.inventory) < 10:
                src.gamestate.gamestate.mainChar.inventory.remove(item)
                self.firstOfficer.inventory.append(item)

    def removeTokensSecondOfficer(self):
        toRemove = []
        numTokens = 0
        for item in src.gamestate.gamestate.mainChar.inventory:
            if isinstance(item, src.items.Token):
                toRemove.append(item)
                numTokens += 1
        for item in src.gamestate.gamestate.mainChar.inventory:
            if numTokens == 0:
                break
            if isinstance(item, src.items.Wall):
                toRemove.append(item)
                numTokens -= 1
        for item in toRemove:
            if len(self.secondOfficer.inventory) < 10:
                src.gamestate.gamestate.mainChar.inventory.remove(item)
                self.secondOfficer.inventory.append(item)

    def removeEverythingSecondOfficer(self):
        if self.secondOfficerRemovesPipes:
            self.removePipesSecondOfficer()
        if self.secondOfficerRemovesGooFlasks:
            self.removeGooFlaskSecondOfficer()
        if self.secondOfficerRemovesTokens:
            self.removeTokensSecondOfficer()


"""
a lab for behaviour testing
bad code: is basically not implemented yet
bad code: is misused as a target/source for transportation jobs
"""


class LabRoom(Room):
    objType = "LabRoom"

    """
    create room and add special items
    """

    def __init__(
        self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, desiredPosition=None
    ):
        self.roomLayout = """
XXXXXXXXXX
X     @@ X
X ...... X
X .    . X
X .    . X
$ .    . X
X .    . X
X ...... X
X        X
X########X
XXXXXXXXXX
XOOOOOOOOX
XFFFFFFFFX
XXXXXXXXXX
"""
        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )

        # bad code: the markers are not used anywhere
        bean = src.items.MarkerBean(1, 2)
        beanPile = src.items.Pile(1, 1, "markerPile", src.items.MarkerBean)
        self.addItems([bean, beanPile])

        self.name = "Lab"

        # unbolt all items in the room
        for item in self.itemsOnFloor:
            if item.xPosition == 0 or item.yPosition == 0:
                continue
            if item.xPosition == self.sizeX - 1 or item.yPosition == self.sizeY - 1:
                continue
            item.bolted = False


"""
cargo storage for tightly packing items
"""


class CargoRoom(Room):
    objType = "CargoRoom"

    """
    create room, set storage order and fill with items
    """

    def __init__(
        self,
        xPosition=0,
        yPosition=0,
        offsetX=0,
        offsetY=0,
        desiredPosition=None,
        itemTypes=[],
        amount=80,
        seed=0,
    ):
        self.roomLayout = """
XXXXXXXXXX
X        X
X       .$
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
XXXXXXXXXX
"""
        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.floorDisplay = [src.canvas.displayChars.nonWalkableUnkown]
        self.name = "CargoRoom"
        self.discovered = False

        # generate items with the supplied item types
        self.storedItems = []
        counter = 0
        length = len(itemTypes)
        for i in range(1, amount):
            i = i + i % 3 + i % 10 * 2 + seed
            if i % 2:
                counter += 1
            elif i % 4:
                counter += 2
            elif i % 8:
                counter += 3
            else:
                counter += 4
            self.storedItems.append(itemTypes[counter % length]())

        if seed % 5 == 3:
            xPosition = 1 + seed // 3 % (self.sizeX - 2)
            yPosition = 1 + seed // 3 % (self.sizeY - 2)
            item = src.items.GooFlask()
            item.xPosition = xPosition
            item.yPosition = yPosition
            self.addItems([item])
        if seed % 5 == 3:
            xPosition = 1 + seed // 6 % (self.sizeX - 2)
            yPosition = 1 + seed // 6 % (self.sizeY - 2)
            item = src.items.GooFlask()
            item.xPosition = xPosition
            item.yPosition = yPosition
            self.addItems([item])
        if seed % 2 == 1:
            xPosition = 1 + seed // 1 % (self.sizeX - 2)
            yPosition = 1 + seed // 1 % (self.sizeY - 2)
            item = src.items.GooFlask()
            item.xPosition = xPosition
            item.yPosition = yPosition
            self.addItems([item])

        npc = src.characters.Character(
                xPosition=4, yPosition=4, seed=self.yPosition + self.offsetY + 4 * 12
        )

        # determine in what order storage space should be used
        counter = 0
        self.storageSpace = []
        for j in range(1, 2):
            for i in range(1, self.sizeX - 1):
                self.storageSpace.append((i, j))
        j = self.sizeY - 2
        while j > 1:
            for i in range(1, self.sizeX - 1):
                self.storageSpace.append((i, j))
            j -= 1

        # map items to storage spaces
        counter = 0
        for item in self.storedItems:
            item.xPosition = self.storageSpace[counter][0]
            item.yPosition = self.storageSpace[counter][1]
            item.mayContainMice = True
            item.bolted = False
            counter += 1

        # add mice inhabiting the room on about every fifth room
        if (
            amount < 70
            and (self.xPosition + yPosition * 2 - offsetX - offsetY + seed) % 2 == 0
        ):
            # place mice
            mice = []
            mousePositions = [(2, 2), (2, 4), (4, 2), (4, 4), (7, 3)]
            for mousePosition in mousePositions:
                mouse = src.characters.Mouse()
                self.addCharacter(mouse, mousePosition[0], mousePosition[1])
                mice.append(mouse)

            """
            kill characters entering the room
            bad code: should be a quest
            """

            def killInvader(character):
                for mouse in mice:
                    quest = src.quests.MurderQuest(character)
                    mouse.assignQuest(quest, active=True)
                """
                stop hunting characters that left the room
                """

                def vanish(characterLeaving):
                    # check whether the correct character left the room
                    if not character == characterLeaving:
                        return

                    counter = 0
                    for mouse in mice:
                        # stop hunting the character
                        # bad code: assumes first quest is kill quest
                        mouse.quests[0].deactivate()
                        mouse.quests.remove(mouse.quests[0])

                        # move back to position
                        quest = src.quests.MoveQuestMeta(
                            self, mousePositions[counter][0], mousePositions[counter][1]
                        )
                        mouse.assignQuest(quest, active=True)
                        counter += 1

                # watch for characters leaving the room
                self.addListener(vanish, "left room")

            # watch for characters entering the room
            self.addListener(killInvader, "entered room")

            def foundNest(character):
                if not character == src.gamestate.gamestate.mainChar:
                    return
                if not self.discovered:
                    self.terrain.huntersLodge.firstOfficer.basicChatOptions[-1][
                        "params"
                    ]["info"].append(
                        {
                            "name": "i discovered a nest in a cargo room.",
                            "text": "thanks for the report",
                            "type": "text",
                            "trigger": {
                                "container": self.terrain.huntersLodge,
                                "method": "rewardNestFind",
                                "params": {"room": self},
                            },
                        }
                    )
                    self.discovered = True

            self.addListener(foundNest, "entered room")
            for item in self.itemsOnFloor:
                # ignore non doors
                if not isinstance(item, src.items.Door):
                    continue

                item.addListener(foundNest, "activated")

        # actually add the items
        self.addItems(self.storedItems)


"""
storage for storing items in an accessible way
"""


class StorageRoom(Room):
    objType = "StorageRoom"

    """
    create room, set storage order 
    """

    def __init__(
        self,
        xPosition=None,
        yPosition=None,
        offsetX=None,
        offsetY=None,
        desiredPosition=None,
    ):
        self.roomLayout = """
XXXXXXXXXX
X        X
X........$
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
XXXXXXXXXX
"""
        self.storedItems = []
        self.storageSpace = []

        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.floorDisplay = [src.canvas.displayChars.nonWalkableUnkown]
        self.name = "StorageRoom"

        # determine what positions should be used for storage
        counter = 0
        for j in range(1, 2):
            for i in range(1, self.sizeX - 1):
                self.storageSpace.append((i, j))
        i = self.sizeX - 2
        offset = 2
        while i > 1:
            for j in range(3, self.sizeY - 1):
                self.storageSpace.append((i, j))
            i -= offset
            if offset == 1:
                offset = 2
            else:
                offset = 1

        # map items on storage space
        # bad code: no items to place
        counter = 0
        for item in self.storedItems:
            item.xPosition = self.storageSpace[counter][0]
            item.yPosition = self.storageSpace[counter][1]
            item.bolted = False
            counter += 1

        # actually add the items
        self.addItems(self.storedItems)

    """
    use specialised pathfinding
    bad code: doesn't work properly
    """

    def calculatePath(self, x, y, dstX, dstY, walkingPath):
        # handle impossible state
        if dstY is None or dstX is None:
            src.logger.debugMessages.append("pathfinding without target")
            return []

        path = []

        # go to secondary path
        if y not in (1, 2) and x not in (2, 5, 8, 3, 6):
            if x in (2, 5, 8):
                x = x - 1
            elif x in (3, 6):
                x = x + 1
            path.append((x, y))

        # go to main path
        while y < 2:
            y = y + 1
            path.append((x, y))
        while y > 2:
            y = y - 1
            path.append((x, y))

        # go main path to secondary path
        tmpDstX = dstX
        if dstX in (2, 5, 8, 3, 6) and dstY not in (1, 2):
            if dstX in (2, 5, 8):
                tmpDstX = dstX - 1
            elif dstX in (3, 6):
                tmpDstX = dstX + 1
        while x < tmpDstX:
            x = x + 1
            path.append((x, y))
        while x > tmpDstX:
            x = x - 1
            path.append((x, y))

        # go to end of secondary path
        while y < dstY:
            y = y + 1
            path.append((x, y))
        while y > dstY:
            y = y - 1
            path.append((x, y))

        # go to end of path
        while x < dstX:
            x = x + 1
            path.append((x, y))
        while x > dstX:
            x = x - 1
            path.append((x, y))
        import src.gameMath as gameMath

        return gameMath.removeLoops(path)

    """
    add items and manage storage spaces
    """

    def addItems(self, items):
        super().addItems(items)
        for item in items:
            pos = (item.xPosition, item.yPosition)
            if pos in self.storageSpace:
                self.storedItems.append(item)
                self.storageSpace.remove(pos)

    """
    remove item and manage storage spaces
    """

    def removeItem(self, item):
        if item in self.storedItems:
            self.storedItems.remove(item)
            pos = (item.xPosition, item.yPosition)
            self.storageSpace.append(pos)
        super().removeItem(item)


"""
the room where characters are grown and born
"""


class WakeUpRoom(Room):
    objType = "WakeUpRoom"

    """
    create room and add special items
    """

    def __init__(
        self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, desiredPosition=None
    ):
        self.roomLayout = """
XXXXXXXX
Xö    vX
XÖ ... $
XÖ . .vX
XÖ . .@X
XÖ . . X
XÖ . . X
XÖ . . X
XÖ ... X
XÖ     X
XXXXXXXX
"""
        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.name = "WakeUpRoom"

        # generate special items
        self.lever1 = src.items.Lever(3, 1, "training lever")
        self.objectDispenser = src.items.OjectDispenser(4, 1)
        self.gooDispenser = src.items.GooDispenser(5, 9)
        self.furnace = src.items.Furnace(4, 9)
        self.pile = src.items.Pile(6, 9)

        """
        create goo flask
        """

        def activateDispenser(dispenser):
            self.objectDispenser.dispenseObject()

        # connect lever
        self.lever1.activateAction = activateDispenser

        # actually add items
        self.addItems(
            [
                self.lever1,
                self.gooDispenser,
                self.objectDispenser,
                self.furnace,
                self.pile,
            ]
        )

        # watch growth tanks and door
        # bad code: should be a quest
        for item in self.itemsOnFloor:
            if isinstance(item, src.items.GrowthTank):

                def forceNewnamespace(
                    var,
                ):  # HACK: brute force approach to get a new namespace
                    def callHandler(char):
                        self.handleUnexpectedGrowthTankActivation(char, var)

                    return callHandler

                item.addListener(forceNewnamespace(item), "activated")
            if isinstance(item, src.items.Door):
                item.addListener(self.handleDoorOpening, "activated")

        # start spawning hoppers periodically
        self.addEvent(
            src.events.EndQuestEvent(
                8000, {"container": self, "method": "spawnNewHopper"}
            )
        )

    """
    warn character about leaving the room
    """

    def handleDoorOpening(self, character):
        # should be a guard
        if self.firstOfficer and not character.hasFloorPermit:
            character.addMessage(
                self.firstOfficer.name
                + ": moving through this door will be your death."
            )
            character.revokeReputation(amount=1, reason="beeing impatient")

    """
    move player to vat
    """

    def handleUnexpectedGrowthTankActivation(self, character, item):
        # bad pattern; player only function
        if not character == src.gamestate.gamestate.mainChar:
            return

        # only act if there is somebody to act
        if not self.firstOfficer:
            return

        if not item.filled:
            return

        # scold player
        character.addMessage(
            self.firstOfficer.name + ": Now will have to take care of this body."
        )
        character.addMessage(
            self.firstOfficer.name
            + ": Please move on to your next assignment immediatly."
        )

        # remove all quests
        for quest in src.gamestate.gamestate.mainChar.quests:
            quest.deactivate()
        src.gamestate.gamestate.mainChar.quests = []

        # cancel cinematics
        # bad code: should happen in a more structured way
        import src.cinematics

        src.cinematics.cinematicQueue = []

        # give floor permit
        character.hasFloorPermit = True

        # start vat phase
        import src.story

        phase = src.story.VatPhase()
        phase.start()

    """
    periodically spawn new hoppers
    """

    def spawnNewHopper(self):
        # do nothing if there is nobody to do anything
        if not self.firstOfficer:
            return

        # eject player from growth tank
        character = None
        for item in self.itemsOnFloor:
            if isinstance(item, src.items.GrowthTank):
                if item.filled:
                    character = item.eject()
                    break

        # abort if no player was generated
        if not character:
            return

        # add character as hopper
        # bad pattern: should be a story or quest
        character.wakeUp()
        character.hasFloorPermit = True
        self.terrain.waitingRoom.addAsHopper(character)

        # schedule next spawn
        self.addEvent(
            src.events.EndQuestEvent(
                src.gamestate.gamestate.tick + 10000,
                {"container": self, "method": "spawnNewHopper"},
            )
        )


"""
the room where hoppers wait for jobs
"""


class WaitingRoom(Room):
    objType = "WaitingRoom"

    """
    create room and add hoppers
    """

    def __init__(
        self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, desiredPosition=None
    ):
        self.roomLayout = """
XXXXXXXXXXX
X         X
X  .....  X
X  .   .  X
X  . @ .  $
X  . @ . IX
X  ..... DX
X         X
X         X
XXXXXXXXXXX
"""
        self.quests = []
        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.name = "WaitingRoom"
        self.hoppers = []

        # add hoppers
        npc = src.characters.Character(
                xPosition=4, yPosition=4, seed=self.yPosition + self.offsetY + 4 * 12
        )
        self.hoppers.append(npc)
        self.addCharacter(npc, 2, 2)
        npc = src.characters.Character(
                xPosition=4,
                yPosition=5,
                seed=self.yPosition + self.offsetY + 4 * 23 + 30,
        )
        self.hoppers.append(npc)
        self.addCharacter(npc, 2, 3)

        self.trainingItems = []
        item = src.items.Wall(1, 1)
        item.bolted = False
        self.trainingItems.append(item)
        item = src.items.Pipe(9, 1)
        item.bolted = False
        self.trainingItems.append(item)
        self.addItems(self.trainingItems)

        # assign hopper duty to hoppers
        for hopper in self.hoppers:
            self.addAsHopper(hopper)
            hopper.initialState = hopper.getState()

    """
    add a character as hopper
    """

    def addAsHopper(self, hopper):
        quest = src.quests.HopperDuty(self)
        hopper.assignQuest(quest, active=True)
        hopper.addListener(self.addRescueQuest, "fallen unconcious")
        hopper.addListener(self.disposeOfCorpse, "died")

    """
    rescue an unconcious hopper
    """

    def addRescueQuest(self, character):
        quest = src.quests.WakeUpQuest(character)
        quest.reputationReward = 2
        self.quests.append(quest)

    """
    dispose of a dead hoppers corpse
    bad pattern: picking the corpse up and pretending nothing happend is not enough
    """

    def disposeOfCorpse(self, info):
        quest = src.quests.PickupQuestMeta(info["corpse"])
        quest.reputationReward = 1
        self.quests.append(quest)

    """
    set internal state from dictionary
    """

    def setState(self, state):
        super().setState(state)

        self.quests = []
        for questId in state["quests"]["ids"]:
            self.quests.append(
                src.quests.getQuestFromState(state["quests"]["states"][questId])
            )

    """
    get state as dictionary
    """

    def getState(self):
        state = super().getState()

        state["quests"] = {"ids": [], "states": {}}
        for quest in self.quests:
            state["quests"]["ids"].append(quest.id)
            state["quests"]["states"][quest.id] = quest.getState()

        return state


"""
a dummy for the mechs command centre
bad code: dummy only
"""


class MechCommand(Room):
    objType = "MechCommand"

    """
    set basic attributes
    """

    def __init__(
        self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, desiredPosition=None
    ):
        self.roomLayout = """
XXXXX$XXXXX
XI        X
XI .....  X
XD .   .  X
XD .@@ .  X
XD .III.  X
XD .DDD.  X
XI .....  X
XI        X
XXXXXXXXXXX
"""
        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.name = "Mech Command Centre"

        self.firstOfficer.name = "Cpt. " + self.firstOfficer.name

        firstOfficerDialog = {
            "dialogName": "Tell me more about the Commandchain",
            "chat": src.chats.ConfigurableChat,
            "params": {
                "text": "I am the Captain and control everything that happens on this mech.\n%s is my second in command\n%s is handling logistics\n%s is coordinating the hopper\n%s is head of the military"
                % ("", "", "", ""),
                "info": [],
            },
        }
        self.firstOfficer.basicChatOptions.append(firstOfficerDialog)
        self.firstOfficer.basicChatOptions.append(
            {"dialogName": "I want to be captain", "chat": src.chats.CaptainChat}
        )
        self.firstOfficer.basicChatOptions.append(
            {
                "dialogName": "I want to be your second in command",
                "chat": src.chats.CaptainChat2,
            }
        )

        npcA = src.characters.Character(
            name="A",
            xPosition=3,
            yPosition=9,
            seed=self.xPosition + 2 * self.offsetY + self.offsetX + 2 * self.yPosition,
        )
        self.addCharacter(npcA, 2, 8)
        npcB = src.characters.Character(
            name="B",
            xPosition=4,
            yPosition=9,
            seed=self.xPosition + 2 * self.offsetY + self.offsetX + 2 * self.yPosition,
        )
        self.addCharacter(npcB, 3, 8)
        npcC = src.characters.Character(
            name="C",
            xPosition=5,
            yPosition=3,
            seed=self.xPosition + 2 * self.offsetY + self.offsetX + 2 * self.yPosition,
        )
        self.addCharacter(npcC, 4, 8)
        npcD = src.characters.Character(
            name="D",
            xPosition=5,
            yPosition=3,
            seed=self.xPosition + 2 * self.offsetY + self.offsetX + 2 * self.yPosition,
        )
        self.addCharacter(npcD, 5, 8)
        npcE = src.characters.Character(
            name="E",
            xPosition=5,
            yPosition=3,
            seed=self.xPosition + 2 * self.offsetY + self.offsetX + 2 * self.yPosition,
        )
        self.addCharacter(npcE, 6, 8)

        import random

        factions = [npcA, npcB, npcC, npcD, npcE]
        for faction in factions:
            faction.minRep = random.randint(1, 60)
            faction.maxAliance = random.randint(1, 4)
            faction.repGain = random.randint(1, 40)
            numExcludes = random.randint(1, 4)
            factionCopy = factions[:]
            factionCopy.remove(faction)
            faction.excludes = []
            for i in range(0, numExcludes):
                chosen = random.choice(factionCopy)
                factionCopy.remove(chosen)
                faction.excludes.append(chosen)

            faction.basicChatOptions.append(
                {
                    "dialogName": "what are the requirements for an aliance?",
                    "chat": src.chats.FactionChat1,
                }
            )
            faction.basicChatOptions.append(
                {"dialogName": "Let us form an aliance", "chat": src.chats.FactionChat2}
            )


"""
the place for production of tools and items
"""


class MetalWorkshop(Room):
    objType = "MetalWorkshop"

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
        self.roomLayout = """
XXXXXXXXXXX
XP        X
XP .....  X
XP .   .  X
XP . @ .  X
XP .   .  X
XP .....  X
XP        X
XP        X
XXXXX$XXXXX
"""
        self.quests = []
        super().__init__(
            self.roomLayout,
            xPosition,
            yPosition,
            offsetX,
            offsetY,
            desiredPosition,
            seed=seed,
        )
        self.name = "MetalWorkshop"

        # add production machines
        self.artwork = src.items.ProductionArtwork(4, 1)
        self.compactor = src.items.ScrapCompactor(6, 1)
        self.addItems([self.artwork, self.compactor])

        # add some produced items
        self.producedItems = []
        item = src.items.Wall(9, 4)
        item.bolted = False
        self.producedItems.append(item)
        item = src.items.Wall(9, 6)
        item.bolted = False
        self.producedItems.append(item)
        item = src.items.Wall(9, 3)
        item.bolted = False
        self.producedItems.append(item)
        item = src.items.Wall(9, 7)
        item.bolted = False
        self.producedItems.append(item)
        item = src.items.Wall(9, 2)
        item.bolted = False
        self.producedItems.append(item)
        item = src.items.Wall(9, 8)
        item.bolted = False
        self.producedItems.append(item)
        self.addItems(self.producedItems)

        firstOfficerDialog = {
            "dialogName": "Do you need some help?",
            "chat": src.chats.ConfigurableChat,
            "params": {"text": "no", "info": []},
        }
        if seed % 5 == 0:
            firstOfficerDialog["params"]["info"].append(
                {
                    "name": "Please give me reputation anyway.",
                    "text": "Ok",
                    "type": "text",
                    "trigger": {"container": self, "method": "dispenseFreeReputation"},
                }
            )
        else:
            firstOfficerDialog["params"]["info"].append(
                {
                    "name": "Please give me reputation anyway.",
                    "text": "no",
                    "type": "text",
                }
            )
        self.firstOfficer.basicChatOptions.append(firstOfficerDialog)

    def dispenseFreeReputation(self):
        src.gamestate.gamestate.mainChar.reputation += 100


"""
"""


class HuntersLodge(Room):
    objType = "HuntersLodge"

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
        self.roomLayout = """
XXXXXXXXXXX
X         X
X  .....  X
X  .   .  X
X  . @ .  X
X  .   .  X
X  .....  X
X         X
X         X
XXXXX$XXXXX
"""
        self.quests = []
        super().__init__(
            self.roomLayout,
            xPosition,
            yPosition,
            offsetX,
            offsetY,
            desiredPosition,
            seed=seed,
        )
        self.name = "HuntersLodge"

        firstOfficerDialog = {
            "dialogName": "Do you need some help?",
            "chat": src.chats.ConfigurableChat,
            "params": {
                "text": "indeed. Anybody reporting mice nests will be rewarded",
                "info": [],
            },
        }
        self.firstOfficer.basicChatOptions.append(firstOfficerDialog)

    def rewardNestFind(self, params):
        src.gamestate.gamestate.mainChar.awardReputation(
            amount=10, reason="reporting a nest"
        )
        toRemove = None
        for option in self.firstOfficer.basicChatOptions[-1]["params"]["info"]:
            if (
                "trigger" in option
                and option["trigger"]["method"] == "rewardNestFind"
                and option["trigger"]["params"] == params
            ):
                toRemove = option
                break
        if toRemove:
            self.firstOfficer.basicChatOptions[-1]["params"]["info"].remove(toRemove)

        self.firstOfficer.basicChatOptions[-1]["params"]["info"].append(
            {
                "name": "i want to exterminate a mice nest",
                "text": "do so",
                "type": "text",
                "trigger": {
                    "container": self.terrain.huntersLodge,
                    "method": "killMiceNest",
                    "params": {"room": params["room"]},
                },
            }
        )

    def killMiceNest(self, params):
        for mouse in params["room"].characters:
            quest = src.quests.MurderQuest(toKill=mouse)
            src.gamestate.gamestate.mainChar.assignQuest(quest, active=True)
        src.gamestate.gamestate.mainChar.revokeReputation(
            amount=20, reason=" for balancing"
        )

"""
a room in the process of beeing constructed. The room itself exists but no items within
"""


class ConstructionSite(Room):
    objType = "ConstructionSite"

    """
    create room and plan construction
    """

    def __init__(
        self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, desiredPosition=None
    ):
        self.roomLayout = """
XXXXXXXXXXX
X         X
X  .....  X
X  .   .  X
X  .   .  X
X  .   .  X
X  .....  X
X    @    X
X         X
XXXXX$XXXXX
"""
        self.desiredRoomlayout = """
XXXXXXXXXXX
X########XX
XXX.....##X
X#X.   .X#X
X#X. @ .##X
X#X.   .#XX
X#X.....##X
X#XXX XXX#X
X#### ####X
XXXXX$XXXXX
"""
        super().__init__(
            self.roomLayout, xPosition, yPosition, offsetX, offsetY, desiredPosition
        )
        self.name = "Construction Site"

        # get a map of items that need to be placed
        itemsToPlace = {}
        x = -1
        for line in self.desiredRoomlayout.split("\n"):
            if x in (-1, 0, 9):
                x += 1
                continue
            y = 0
            for char in line:
                if y in (0, 10):
                    y += 1
                    continue
                if char == "#":
                    itemsToPlace[(x, y)] = src.items.Pipe
                if char == "X":
                    itemsToPlace[(x, y)] = src.items.Wall
                y += 1
            x += 1

        # add markers for items
        itemstoAdd = []
        for (position, itemType) in itemsToPlace.items():
            item = src.items.MarkerBean(position[1], position[0])
            item.apply(self.firstOfficer)
            itemstoAdd.append(item)
        self.addItems(itemstoAdd)

        buildorder = []
        # task north-west corner
        x = 0
        while x < self.sizeX // 2:
            y = 0
            while y < self.sizeY // 2:
                buildorder.append((x, y))
                y += 1
            x += 1

        # task south-west corner
        x = self.sizeX
        while x >= self.sizeX // 2:
            y = 0
            while y < self.sizeY // 2:
                buildorder.append((x, y))
                y += 1
            x -= 1

        # task south-east corner
        x = self.sizeX
        while x >= self.sizeX // 2:
            y = self.sizeY
            while y >= self.sizeY // 2:
                buildorder.append((x, y))
                y -= 1
            x -= 1

        # task north-east corner
        x = 0
        while x < self.sizeX // 2:
            y = self.sizeY
            while y >= self.sizeY // 2:
                buildorder.append((x, y))
                y -= 1
            x += 1

        # bad code: building in the middle of the room is NIY

        # sort items in build order
        self.itemsInBuildOrder = []
        for position in buildorder:
            if position in itemsToPlace:
                self.itemsInBuildOrder.append((position, itemsToPlace[position]))
        self.itemsInBuildOrder.reverse()



"""
smart scrap storage
"""


class ScrapStorage(Room):
    objType = "ScrapStorage"

    """
    create room
    """

    def __init__(self, xPosition=0, yPosition=0, offsetX=0, offsetY=0, seed=0):
        self.roomLayout = """
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
        super().__init__(self.roomLayout, xPosition, yPosition, offsetX, offsetY)
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
    "TutorialMachineRoom": TutorialMachineRoom,
    "CpuWasterRoom": CpuWasterRoom,
    "InfanteryQuarters": InfanteryQuarters,
    "VatFermenting": VatFermenting,
    "VatProcessing": VatProcessing,
    "ChallengeRoom": ChallengeRoom,
    "LabRoom": LabRoom,
    "MechArmor": MechArmor,
    "MiniMech": MiniMech,
    "MiniBase": MiniBase,
    "MiniBase2": MiniBase2,
    "CargoRoom": CargoRoom,
    "StorageRoom": StorageRoom,
    "WakeUpRoom": WakeUpRoom,
    "WaitingRoom": WaitingRoom,
    "MechCommand": MechCommand,
    "MetalWorkshop": MetalWorkshop,
    "HuntersLodge": HuntersLodge,
    "EmptyRoom": EmptyRoom,
    "ConstructionSite": ConstructionSite,
    "GameTestingRoom": GameTestingRoom,
    "ScrapStorage": ScrapStorage,
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
