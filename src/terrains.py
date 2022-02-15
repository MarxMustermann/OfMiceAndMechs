"""
terrains and terrain related code belongs here
"""

# import basic libs
import json
import array
import random

# import basic internal libs
import src.items
import src.rooms
import src.overlays
import src.gameMath
import src.saveing
import src.canvas
import src.logger
import src.quests
import src.events
import src.gamestate

# bad code: is basically used nowhere
class Coordinate(object):
    """
    a abstracted coordinate.
    """
    
    def __init__(self, x, y):
        """
        set up internal state

        Parameters:
            x: x coordinate
            y: y coordinate
        """

        self.x = x
        self.y = y

class Terrain(src.saveing.Saveable):
    """
    the base class for terrains
    """

    def __init__(
        self,
        layout="",
        detailedLayout="",
        seed=0,
        noPaths=False,
        noContent=False,
    ):
        """
        set up internal state

        Parameters:
            layout: the terrains room layout
            detailedLayout: the terrains item layout
            seed: rng seed
            noPaths: flag to calculate no paths
            noContent: flag to generate terrain empty
        """

        self.noPlacementTiles = []
        self.scrapFields = []

        super().__init__()

        self.noPaths = noPaths

        # store terrain content
        # self.itemsOnFloor = []
        self.characters = []
        self.rooms = []
        self.floordisplay = src.canvas.displayChars.floor
        self.itemsByCoordinate = {}
        self.roomByCoordinates = {}
        self.listeners = {"default": []}
        self.initialSeed = seed
        self.seed = seed
        self.events = []
        self.biomeInfo = {"wet": 2}
        self.hidden = True

        # set id
        import uuid

        self.id = uuid.uuid4().hex

        # misc state
        self.overlay = None
        self.alarm = False

        if not noContent:
            # add items
            # bad code: repetitive code
            mapItems = []
            self.detailedLayout = detailedLayout
            lineCounter = 0
            for layoutline in self.detailedLayout.split("\n")[1:]:
                rowCounter = 0
                for char in layoutline:
                    if char in (" ", ".", ",", "@"):
                        pass
                    elif char == "X":
                        mapItems.append(
                            (src.items.itemMap["Wall"],(rowCounter, lineCounter,0))
                        )
                    elif char == "#":
                        mapItems.append(
                            (src.items.itemMap["Pipe"],(rowCounter, lineCounter,0))
                        )
                    elif char == "R":
                        pass
                    elif char == "O":
                        mapItems.append(
                            (src.items.itemMap["Item"](src.canvas.displayChars.clamp_active),
                                (rowCounter,lineCounter,0)
                            )
                        )
                    elif char == "0":
                        mapItems.append(
                            (
                            src.items.itemMap["Item"](src.canvas.displayChars.clamp_inactive),
                                (rowCounter,lineCounter,0)
                            )
                        )
                    elif char == "8":
                        mapItems.append(
                            (
                                src.items.itemMap["Chain"](),
                                (rowCounter, lineCounter, 0)
                            )
                        )
                    elif char == "C":
                        mapItems.append(
                            (
                                src.items.itemMap["Winch"](),
                                (rowCounter, lineCounter, 0)
                            )
                        )
                    elif char == "P":
                        mapItems.append(
                            (
                                src.items.itemMap["Pile"](),
                                (rowCounter, lineCounter, 0)
                            )
                        )
                    else:
                        mapItems.append(
                            (
                                src.items.itemMap["Item"](
                                    src.canvas.displayChars.randomStuff2[
                                        ((2 * rowCounter) + lineCounter) % 10
                                    ]),
                                (rowCounter, lineCounter, 0)
                            )
                        )
                    rowCounter += 1
                lineCounter += 1
            self.addItems(mapItems)

        # container for categories of rooms for easy access
        # bad code: should be abstracted
        roomsOnMap = []
        self.tutorialVat = None
        self.tutorialVatProcessing = None
        self.tutorialMachineRoom = None
        self.tutorialLab = None
        self.challengeRooms = []
        self.tutorialCargoRooms = []
        self.tutorialStorageRooms = []
        self.miniMechs = []
        self.wakeUpRoom = None
        self.militaryRooms = []

        # nodes for pathfinding
        self.watershedStart = []
        self.superNodes = {}

        if not noContent:
            # add rooms
            # bad code: this should be abstracted
            # bad code: repetitive code
            # bad code: watershed coordinates should not be set here
            lineCounter = 0
            for layoutline in layout.split("\n")[1:]:
                rowCounter = 0
                for char in layoutline:
                    if char in (".", ",", " ", "t"):
                        # add starting points for pathfinding
                        self.watershedStart.extend(
                            [
                                (rowCounter * 15 + 1, lineCounter * 15 + 1),
                                (rowCounter * 15 + 13, lineCounter * 15 + 1),
                                (rowCounter * 15 + 1, lineCounter * 15 + 13),
                                (rowCounter * 15 + 13, lineCounter * 15 + 13),
                            ]
                        )
                        if char in ("."):
                            # add starting point for higher level pathfinding
                            self.superNodes[(rowCounter, lineCounter)] = (
                                rowCounter * 15 + 1,
                                lineCounter * 15 + 1,
                            )

                    if char in (".", ",", " "):
                        # ignore paths
                        pass
                    elif char == "X":
                        # add armor plating
                        roomsOnMap.append(
                            src.rooms.MechArmor(
                                rowCounter, lineCounter, 0, 0
                            )
                        )
                    elif char == "V":
                        # add vat and save first reference
                        room = src.rooms.VatFermenting(
                            rowCounter, lineCounter, 2, 2
                        )
                        if not self.tutorialVat:
                            self.tutorialVat = room
                        roomsOnMap.append(room)
                    elif char == "v":
                        # add vat and save first reference
                        room = src.rooms.VatProcessing(
                            rowCounter, lineCounter, 2, 2
                        )
                        if not self.tutorialVatProcessing:
                            self.tutorialVatProcessing = room
                        roomsOnMap.append(room)
                    elif char == "Q":
                        # add room and add to room list
                        room = src.rooms.InfanteryQuarters(
                            rowCounter, lineCounter, 1, 2
                        )
                        roomsOnMap.append(room)
                        self.militaryRooms.append(room)

                        # add terrain wide listener
                        self.addListener(room.enforceFloorPermit, "entered terrain")
                    elif char == "w":
                        # add room and add to room list
                        room = src.rooms.WaitingRoom(
                            rowCounter, lineCounter, 1, 2
                        )
                        self.waitingRoom = room
                        roomsOnMap.append(room)
                    elif char == "M":
                        # add room and add to room list
                        room = src.rooms.TutorialMachineRoom(
                            rowCounter, lineCounter, 4, 1
                        )
                        if not self.tutorialMachineRoom:
                            self.tutorialMachineRoom = room
                        roomsOnMap.append(room)
                    elif char == "L":
                        # add room and add to room list
                        room = src.rooms.LabRoom(
                            rowCounter, lineCounter, 1, 1
                        )
                        if not self.tutorialLab:
                            self.tutorialLab = room
                        roomsOnMap.append(room)
                    elif char == "l":
                        # add room and add to room list
                        room = src.rooms.ChallengeRoom(
                            rowCounter,
                            lineCounter,
                            3,
                            1,
                            seed=seed + rowCounter - 3 * lineCounter,
                        )
                        self.challengeRooms.append(room)
                        roomsOnMap.append(room)
                    elif char == "C":
                        # generate pseudo random content type
                        itemTypes = [src.items.itemMap["Wall"], src.items.itemMap["Pipe"]]
                        amount = 40
                        if not (rowCounter + seed) % 2:
                            itemTypes.append(src.items.itemMap["Lever"])
                            amount += 10
                        if not (rowCounter + seed) % 3:
                            itemTypes.append(src.items.itemMap["Furnace"])
                            amount += 15
                        if not (rowCounter + seed) % 4:
                            itemTypes.append(src.items.itemMap["Chain"])
                            amount += 20
                        if not (rowCounter + seed) % 5:
                            itemTypes.append(src.items.itemMap["Hutch"])
                            amount += 7
                        if not (rowCounter + seed) % 6:
                            itemTypes.append(src.items.itemMap["GrowthTank"])
                            amount += 8
                        if not (lineCounter + seed) % 2:
                            itemTypes.append(src.items.itemMap["Door"])
                            amount += 15
                        if not (lineCounter + seed) % 3:
                            itemTypes.append(src.items.itemMap["Boiler"])
                            amount += 10
                        if not (lineCounter + seed) % 4:
                            itemTypes.append(src.items.itemMap["Winch"])
                            amount += 7
                        if not (lineCounter + seed) % 5:
                            itemTypes.append(src.items.itemMap["RoomControls"])
                            amount += 7
                        if not (lineCounter + seed) % 6:
                            itemTypes.append(src.items.itemMap["Commlink"])
                            amount += 7
                        if not itemTypes:
                            itemTypes = [
                                src.items.itemMap["Pipe"],
                                src.items.itemMap["Wall"],
                                src.items.itemMap["Furnace"],
                                src.items.itemMap["Boiler"],
                            ]
                            amount += 30
                        while amount > 80:
                            amount -= seed % 40 + 1

                        # add room and add to room list
                        room = src.rooms.CargoRoom(
                            rowCounter,
                            lineCounter,
                            3,
                            0,
                            itemTypes=itemTypes,
                            amount=amount,
                            seed=seed + 2 * rowCounter + 5 * lineCounter // 7,
                        )
                        self.tutorialCargoRooms.append(room)
                        roomsOnMap.append(room)
                    elif char == "h":
                        # add room and add to room list
                        room = src.rooms.HuntersLodge(
                            rowCounter, lineCounter, 3, 0
                        )
                        self.huntersLodge = room
                        roomsOnMap.append(room)
                    elif char == "U":
                        # add room and add to room list
                        room = src.rooms.StorageRoom(
                            rowCounter, lineCounter, 3, 0
                        )
                        self.tutorialStorageRooms.append(room)
                    elif char == "?":
                        # add room and add to room list
                        roomsOnMap.append(
                            src.rooms.CpuWasterRoom(
                                rowCounter, lineCounter, 2, 2
                            )
                        )
                    elif char == "t":
                        # add room and add to room list
                        miniMech = src.rooms.MiniMech(
                            rowCounter, lineCounter, 2, 2
                        )
                        self.miniMechs.append(miniMech)
                        roomsOnMap.append(miniMech)
                    elif char == "W":
                        # add room and add to room list
                        wakeUpRoom = src.rooms.WakeUpRoom(
                            rowCounter, lineCounter, 1, 1
                        )
                        self.wakeUpRoom = wakeUpRoom
                        roomsOnMap.append(wakeUpRoom)
                    elif char == "m":
                        # add room and add to room list
                        room = src.rooms.MetalWorkshop(
                            rowCounter,
                            lineCounter,
                            1,
                            1,
                            seed=seed + 3 * rowCounter + 2 * lineCounter // 8,
                        )
                        self.metalWorkshop = room
                        roomsOnMap.append(room)
                    elif char == "b":
                        # add room and add to room list
                        room = src.rooms.ConstructionSite(
                            rowCounter, lineCounter, 1, 1
                        )
                        roomsOnMap.append(room)
                    elif char == "K":
                        # add room and add to room list
                        room = src.rooms.MechCommand(
                            rowCounter, lineCounter, 1, 1
                        )
                        roomsOnMap.append(room)
                    else:
                        # add starting points for pathfinding
                        self.watershedStart.append(
                            (rowCounter * 15 + 7, lineCounter * 15 + 7)
                        )
                        pass
                    rowCounter += 1
                lineCounter += 1

            # actually add the rooms to the map
            self.addRooms(roomsOnMap)

        # set meta information for saving
        self.attributesToStore.extend(
            [
                "yPosition",
                "xPosition",
            ]
        )
        self.tupleListsToStore.append("scrapFields")

    def handleFloorClick(self,extraInfo):
        if not src.gamestate.gamestate.mainChar.quests:
            return

        print("handleFloorClick")
        print(extraInfo)

        charPos = (src.gamestate.gamestate.mainChar.xPosition//15,src.gamestate.gamestate.mainChar.yPosition//15,0)
        newPos = (extraInfo["pos"][0]//15,extraInfo["pos"][1]//15,0)
        smallNewPos = (extraInfo["pos"][0]%15,extraInfo["pos"][1]%15,0)

        if src.gamestate.gamestate.mainChar.container == self and charPos == newPos:
            quest = src.quests.GoToPosition(targetPosition=smallNewPos)
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            src.gamestate.gamestate.mainChar.runCommandString("~")
        else:
            quest = src.quests.GoToPosition(targetPosition=smallNewPos)
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            quest = src.quests.GoToTile(targetPosition=newPos)
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            src.gamestate.gamestate.mainChar.runCommandString("~")

    def advance(self):
        for character in self.characters:
            character.advance()

        for room in self.rooms:
            room.advance()

        while (
            self.events
            and self.events[0].tick <= src.gamestate.gamestate.tick
        ):
            event = self.events[0]
            if event.tick < src.gamestate.gamestate.tick:
                1/0
            event.handleEvent()
            self.events.remove(event)

    def randomAddItems(self, items):
        for item in items:
            pos = (random.randint(15,210),random.randint(15,210),0)

            while (pos[0]//15,pos[1]//15) in self.noPlacementTiles:
                pos = (random.randint(15,210),random.randint(15,210),0)
                
            self.addItem(item, pos)

    def damage(self):
        pass

    def getPositionWalkable(self,pos):
        items = self.getItemByPosition(pos)
        if len(items) > 15:
            return False
        for item in items:
            if item.walkable == False:
                return False
        return True

    def getRoomByPosition(self, position):
        foundRooms = []
        for room in self.rooms:
            if room.xPosition == position[0] and room.yPosition == position[1]:
                foundRooms.append(room)
        return foundRooms

    def getItemByPosition(self, position):
        """
        get items on a specific position

        Parameters:
            position: the position to get items from
        Returns:
            the list of items on that position
        """

        if position[0] % 15 == 0:
            if position[1] % 15 < 7:
                position = (position[0] + 1, position[1] + 1, position[2])
            elif position[1] % 15 > 7:
                position = (position[0] + 1, position[1] - 1, position[2])
        if position[0] % 15 == 14:
            if position[1] % 15 < 7:
                position = (position[0] - 1, position[1] + 1, position[2])
            elif position[1] % 15 > 7:
                position = (position[0] - 1, position[1] - 1, position[2])
        if position[1] % 15 == 0:
            if position[0] % 15 < 7:
                position = (position[0] + 1, position[1] + 1, position[2])
            elif position[0] % 15 > 7:
                position = (position[0] - 1, position[1] + 1, position[2])
        if position[1] % 15 == 14:
            if position[0] % 15 < 7:
                position = (position[0] + 1, position[1] - 1, position[2])
            elif position[0] % 15 > 7:
                position = (position[0] - 1, position[1] - 1, position[2])

        try:
            return self.itemsByCoordinate[(position[0], position[1], position[2])]
        except KeyError:
            return []

    # bad code: story specific code
    # obolete: used only by obsolete story
    def runner1(self):
        """
        make a npc run around
        """

        room = None
        for room in self.rooms:
            if isinstance(room, src.rooms.VatFermenting):
                break
        if room:
            quest = src.quests.MoveQuestMeta(room, 5, 8, creator=self)
            quest.endTrigger = {"container": self, "method": "runner2"}
            self.runner.assignQuest(quest, active=True)

    # bad code: story specific code
    # obolete: used only by obsolete story
    def runner2(self):
        """
        make a npc run around
        """

        for room in reversed(self.rooms):
            if isinstance(room, src.rooms.VatFermenting):
                break
        quest = src.quests.MoveQuestMeta(room, 5, 8, creator=self)
        quest.endTrigger = {"container": self, "method": "runner1"}
        self.runner.assignQuest(quest, active=True)

    # bad code: should be an extra class
    def addListener(self, listenFunction, tag="default"):
        """
        register a callback to be called on the terrain changing

        Parameters:
            listenFunction: the callback to register
            tag: filter to only listen for some changes
        """

        if tag not in self.listeners:
            self.listeners[tag] = []

        if listenFunction not in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    def delListener(self, listenFunction, tag="default"):
        """
        deregister a callback to be called on the terrain changing

        Parameters:
            listenFunction: the callback to deregister
            tag: filter to only listen for some changes
        """

        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        if not self.listeners[tag]:
            del self.listeners[tag]

    def changed(self, tag="default", info=None):
        """
        sending notifications to thing listening 

        Parameters:
            tag: filter to only listen for some changes
            info: additional information
        """

        if not tag == "default":
            if tag not in self.listeners:
                return

            for listenFunction in self.listeners[tag]:
                listenFunction(info)
        for listenFunction in self.listeners["default"]:
            listenFunction()

    def removeCharacter(self, character):
        """
        remove a character from the terrain

        Parameters:
            character: the character to remove
        """

        if character in self.characters:
            self.characters.remove(character)
        character.room = None
        character.terrain = None

    def enterLocalised(self, char, room, localisedEntry, direction):
        """
        move a character into a room

        Parameters:
            room: the room to enter
            localisedEntry: the position to enter the room
        """

        # get the entry point in room coordinates
        if localisedEntry in room.walkingAccess or 1==1:
            if localisedEntry in room.itemByCoordinates:
                # check if the entry point is blocked (by a door)
                for item in room.itemByCoordinates[localisedEntry]:

                    # handle collisions
                    if not item.walkable:
                        # print some info
                        if isinstance(item, src.items.itemMap["Door"]):
                            char.addMessage("you need to open the door first")
                        else:
                            char.addMessage("the entry is blocked")
                        # char.addMessage("press "+commandChars.activate+" to apply")
                        # if noAdvanceGame == False:
                        #    header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))

                        # remember the item for interaction and abort
                        return item

                if len(room.itemByCoordinates[localisedEntry]) >= 15:
                    char.addMessage("the entry is blocked by items.")
                    # char.addMessage("press "+commandChars.activate+" to apply")
                    # if noAdvanceGame == False:
                    #    header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))
                    return room.itemByCoordinates[localisedEntry][0]

            char.changed("moved", (char, direction))
            char.changed("entered room", (char, room, direction))

            # teleport the character into the room
            room.addCharacter(char, localisedEntry[0], localisedEntry[1])
            if not char.terrain:
                return
            try:
                char.terrain.characters.remove(char)
            except:
                char.addMessage("fail,fail,fail")

            return

        # do not move player into the room
        else:
            char.addMessage("you cannot move there")

    def moveCharacterDirection(self, char, direction):
        """
        move a character into a direction

        Parameters:
            char: the character to move
            direction: the direction to move the character in
        """

        if not char.terrain:
            return
        if not (char.xPosition and char.yPosition):
            print("nopos")
            return

        if direction == "west":
            if char.yPosition % 15 == 0 or char.yPosition % 15 == 14:
                return
            if char.xPosition % 15 == 1:
                if char.yPosition % 15 < 7:
                    direction = "south"
                elif char.yPosition % 15 > 7:
                    direction = "north"
                else:
                    if char.xPosition == 16 and 1==0:
                        return
                    else:
                        # char.stasis = True
                        char.runCommandString("aa")
                        pass
                char.addMessage("a force field pushes you")

            if char.xPosition % 15 == 14:
                char.changed("changedTile")
                self.removeItems(self.getItemByPosition((char.xPosition-1,char.yPosition,char.zPosition)))
        elif direction == "east":
            if char.yPosition % 15 == 0 or char.yPosition % 15 == 14:
                return
            if char.xPosition % 15 == 13:
                if char.yPosition % 15 < 7:
                    direction = "south"
                elif char.yPosition % 15 > 7:
                    direction = "north"
                else:
                    if char.xPosition == 15 * 14 - 2 and 1==0:
                        return
                    else:
                        # char.stasis = True
                        char.runCommandString("dd")
                        pass
                char.addMessage("a force field pushes you")
            if char.xPosition % 15 == 0:
                char.changed("changedTile")
                self.removeItems(self.getItemByPosition((char.xPosition+1,char.yPosition,char.zPosition)))
        elif direction == "north":
            if char.xPosition % 15 == 0 or char.xPosition % 15 == 14:
                return
            if char.yPosition % 15 == 1:
                if char.xPosition % 15 < 7:
                    direction = "east"
                elif char.xPosition % 15 > 7:
                    direction = "west"
                else:
                    if char.yPosition == 16 and 1==0:
                        return
                    else:
                        # char.stasis = True
                        char.runCommandString("ww")
                        pass
                char.addMessage("a force field pushes you")
            if char.yPosition % 15 == 14:
                char.changed("changedTile")
                self.removeItems(self.getItemByPosition((char.xPosition,char.yPosition-1,char.zPosition)))
        elif direction == "south":
            if char.xPosition % 15 == 0 or char.xPosition % 15 == 14:
                return
            if char.yPosition % 15 == 13:
                if char.xPosition % 15 < 7:
                    direction = "east"
                elif char.xPosition % 15 > 7:
                    direction = "west"
                else:
                    if char.yPosition == 15 * 14 - 2 and 1 == 0:
                        return
                    else:
                        # char.stasis = True
                        char.runCommandString("ss")
                        pass
                char.addMessage("a force field pushes you")
            if char.yPosition % 15 == 0:
                char.changed("changedTile")
                #while self.getItemByPosition((char.xPosition,char.yPosition+1,char.zPosition)):
                self.removeItems(self.getItemByPosition((char.xPosition,char.yPosition+1,char.zPosition)))
        """
        if char.xPosition % 15 in (0, 14) and direction in ("north", "south"):
            return
        if char.yPosition % 15 in (0, 14) and direction in ("east", "west"):
            return
        """

        # gather the rooms the character might have entered
        if direction == "north":
            bigX = char.xPosition // 15
            bigY = (char.yPosition - 1) // 15
        elif direction == "south":
            bigX = char.xPosition // 15
            bigY = (char.yPosition + 1) // 15
        elif direction == "east":
            bigX = (char.xPosition + 1) // 15
            bigY = char.yPosition // 15
        elif direction == "west":
            bigX = char.xPosition // 15
            bigY = (char.yPosition - 1) // 15

        # gather the rooms the player might step into
        roomCandidates = []
        for coordinate in [
            (bigX, bigY),
            (bigX, bigY + 1),
            (bigX + 1, bigY + 1),
            (bigX + 1, bigY),
            (bigX + 1, bigY - 1),
            (bigX, bigY - 1),
            (bigX - 1, bigY - 1),
            (bigX - 1, bigY),
            (bigX - 1, bigY + 1),
            (bigX - 2, bigY),
            (bigX - 2, bigY - 1),
            (bigX - 2, bigY - 2),
            (bigX - 1, bigY - 2),
            (bigX, bigY - 2),
            (bigX + 1, bigY - 2),
            (bigX + 2, bigY - 2),
            (bigX + 2, bigY - 1),
            (bigX + 2, bigY),
            (bigX + 2, bigY - 1),
            (bigX + 2, bigY - 2),
            (bigX + 1, bigY - 2),
            (bigX, bigY - 2),
            (bigX - 1, bigY - 2),
            (bigX - 2, bigY - 2),
            (bigX - 1, bigY - 2),
        ]:
            if coordinate in char.terrain.roomByCoordinates:
                for room in char.terrain.roomByCoordinates[coordinate]:
                    if room not in roomCandidates:
                        roomCandidates.append(room)

        # check if character has entered a room
        hadRoomInteraction = False
        for room in roomCandidates:
            # check north
            if direction == "north":
                # check if the character crossed the edge of the room
                if room.yPosition * 15 + room.offsetY + room.sizeY == char.yPosition:
                    if (
                        room.xPosition * 15 + room.offsetX - 1 < char.xPosition
                        and room.xPosition * 15 + room.offsetX + room.sizeX
                        > char.xPosition
                    ):
                        # get the entry point in room coordinates
                        hadRoomInteraction = True
                        localisedEntry = (
                            char.xPosition % 15 - room.offsetX,
                            char.yPosition % 15 - room.offsetY - 1,
                            0,
                        )
                        if localisedEntry[1] == -1:
                            localisedEntry = (localisedEntry[0], room.sizeY - 1,0)

            # check south
            elif direction == "south":
                # check if the character crossed the edge of the room
                if room.yPosition * 15 + room.offsetY == char.yPosition + 1:
                    if (
                        room.xPosition * 15 + room.offsetX - 1 < char.xPosition
                        and room.xPosition * 15 + room.offsetX + room.sizeX
                        > char.xPosition
                    ):
                        # get the entry point in room coordinates
                        hadRoomInteraction = True
                        localisedEntry = (
                            (char.xPosition - room.offsetX) % 15,
                            (char.yPosition - room.offsetY + 1) % 15,
                            0
                        )

            # check east
            elif direction == "east":
                # check if the character crossed the edge of the room
                if room.xPosition * 15 + room.offsetX == char.xPosition + 1:
                    if (
                        room.yPosition * 15 + room.offsetY < char.yPosition + 1
                        and room.yPosition * 15 + room.offsetY + room.sizeY
                        > char.yPosition
                    ):
                        # get the entry point in room coordinates
                        hadRoomInteraction = True
                        localisedEntry = (
                            (char.xPosition - room.offsetX + 1) % 15,
                            (char.yPosition - room.offsetY) % 15,
                            0
                        )

            # check west
            elif direction == "west":
                # check if the character crossed the edge of the room
                if room.xPosition * 15 + room.offsetX + room.sizeX == char.xPosition:
                    if (
                        room.yPosition * 15 + room.offsetY < char.yPosition + 1
                        and room.yPosition * 15 + room.offsetY + room.sizeY
                        > char.yPosition
                    ):
                        # get the entry point in room coordinates
                        hadRoomInteraction = True
                        localisedEntry = (
                            (char.xPosition - room.offsetX - 1) % 15,
                            (char.yPosition - room.offsetY) % 15,
                            0,
                        )

            # move player into the room
            if hadRoomInteraction:
                item = self.enterLocalised(char, room, localisedEntry, direction)
                if item:
                    return item

                break

        # handle walking without room interaction
        if not hadRoomInteraction:
            # get the items on the destination coordinate
            if direction == "north":
                destCoord = (char.xPosition, char.yPosition - 1, char.zPosition)
            elif direction == "south":
                destCoord = (char.xPosition, char.yPosition + 1, char.zPosition)
            elif direction == "east":
                destCoord = (char.xPosition + 1, char.yPosition, char.zPosition)
            elif direction == "west":
                destCoord = (char.xPosition - 1, char.yPosition, char.zPosition)

            foundItems = char.terrain.getItemByPosition(destCoord)

            # check for items blocking the move to the destination coordinate
            foundItem = None
            stepOnActiveItems = []
            item = None
            for item in foundItems:
                if item and not item.walkable:
                    # print some info
                    char.addMessage("You cannot walk there")
                    # char.addMessage("press "+commandChars.activate+" to apply")
                    # if noAdvanceGame == False:
                    #    header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))

                    # remember the item for interaction and abort
                    foundItem = item

                if item.isStepOnActive:
                    stepOnActiveItems.append(item)
            if not foundItem:
                if len(foundItems) >= 15:
                    char.addMessage("the floor is too full to walk there")
                    # char.addMessage("press "+commandChars.activate+" to apply")
                    # if noAdvanceGame == False:
                    #    header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))

                    # remember the item for interaction and abort
                    foundItem = foundItems[0]

            if foundItem:
                foundItem = foundItems[0]

            for other in self.characters:
                if other == char:
                    continue

                if not destCoord == other.getPosition():
                    continue

                if char.faction == "player" and other.faction == "player":
                    continue

                if char.faction.startswith("city"):
                    if char.faction == other.faction:
                        continue

                char.messages.append("*thump*")
                char.collidedWith(other,actor=char)
                other.collidedWith(char,actor=char)
                return

            # move the character
            if not foundItem:

                for item in stepOnActiveItems:
                    item.doStepOnAction(char)
                if direction == "north":
                    char.yPosition -= 1
                elif direction == "south":
                    char.yPosition += 1
                elif direction == "east":
                    char.xPosition += 1
                elif direction == "west":
                    char.xPosition -= 1

                if char.yPosition < 1:
                    y = 0

                    pos = None
                    for row in src.gamestate.gamestate.terrainMap:
                        x = 0
                        for terrain in row:
                            if terrain == self:
                                pos = (x,y)
                            x += 1
                        y +=1


                    try:
                        newTerrain = src.gamestate.gamestate.terrainMap[pos[1]-1][pos[0]]
                    except:
                        return

                    char.addMessage("you moved from terrain %s/%s to terrain %s/%s"%(pos[0],pos[1],pos[0],pos[1]-1,))

                    self.removeCharacter(char)
                    newTerrain.addCharacter(char,char.xPosition,15*15-2)

                    if char == src.gamestate.gamestate.mainChar:
                        src.gamestate.gamestate.terrain = newTerrain

                if char.yPosition > 223:
                    y = 0

                    pos = None
                    for row in src.gamestate.gamestate.terrainMap:
                        x = 0
                        for terrain in row:
                            if terrain == self:
                                pos = (x,y)
                            x += 1
                        y +=1

                    try:
                        newTerrain = src.gamestate.gamestate.terrainMap[pos[1]+1][pos[0]]
                    except:
                        return

                    char.addMessage("you moved from terrain %s/%s to terrain %s/%s"%(pos[0],pos[1],pos[0],pos[1]+1,))

                    self.removeCharacter(char)
                    newTerrain.addCharacter(char,char.xPosition,2)

                    if char == src.gamestate.gamestate.mainChar:
                        src.gamestate.gamestate.terrain = newTerrain

                if char.xPosition < 1:
                    y = 0

                    pos = None
                    for row in src.gamestate.gamestate.terrainMap:
                        x = 0
                        for terrain in row:
                            if terrain == self:
                                pos = (x,y)
                            x += 1
                        y +=1

                    try:
                        newTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]-1]
                    except:
                        return

                    char.addMessage("you moved from terrain %s/%s to terrain %s/%s"%(pos[0],pos[1],pos[0]-1,pos[1],))

                    self.removeCharacter(char)
                    newTerrain.addCharacter(char,15*15-2,char.yPosition)

                    if char == src.gamestate.gamestate.mainChar:
                        src.gamestate.gamestate.terrain = newTerrain

                if char.xPosition > 223:
                    y = 0

                    pos = None
                    for row in src.gamestate.gamestate.terrainMap:
                        x = 0
                        for terrain in row:
                            if terrain == self:
                                pos = (x,y)
                            x += 1
                        y +=1

                    try:
                        newTerrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]+1]
                    except:
                        return

                    char.addMessage("you moved from terrain %s/%s to terrain %s/%s"%(pos[0],pos[1],pos[0]+1,pos[1],))

                    self.removeCharacter(char)
                    newTerrain.addCharacter(char,2,char.yPosition)

                    if char == src.gamestate.gamestate.mainChar:
                        src.gamestate.gamestate.terrain = newTerrain


                char.changed("moved", (char, direction))

            return foundItem

    def getPathCommand(self,startPos,targetPos,localRandom=None,tryHard=False):
        path = self.getPath(startPos,targetPos,localRandom,tryHard)

        command = ""
        movementMap = {(1,0):"15d",(-1,0):"15a",(0,1):"15s",(0,-1):"15w"}
        if path:
            for offset in path:
                command += movementMap[offset]
        else:
            return "..."
        return command

    def getPath(self,startPos,targetPos,localRandom=None,tryHard=False):
        if not localRandom:
            localRandom = random

        costMap = {startPos:0}
        lastPos = startPos
        toCheck = []
        nextPos = startPos
        paths = {startPos:[]}

        counter = 0
        while counter < 100:
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

                if newPos[0] > 13 or newPos[1] > 13 or newPos[0] < 1 or newPos[1] < 1:
                    continue

                if not costMap.get(newPos) == None:
                    continue

                if not newPos == targetPos and newPos in self.scrapFields:
                    continue

                passable = False

                oldRoom = self.getRoomByPosition(pos)
                if oldRoom:
                    oldRoom = oldRoom[0]

                newRoom = self.getRoomByPosition(newPos)
                if newRoom:
                    newRoom = newRoom[0]

                if offset == (0,+1) and (not newRoom or newRoom.getPositionWalkable((6,0,0) )) and (not oldRoom or oldRoom.getPositionWalkable((6,12,0))):
                    passable = True
                if offset == (0,-1) and (not newRoom or newRoom.getPositionWalkable((6,12,0))) and (not oldRoom or oldRoom.getPositionWalkable((6,0,0 ))):
                    passable = True
                if offset == (+1,0) and (not newRoom or newRoom.getPositionWalkable((0,6,0) )) and (not oldRoom or oldRoom.getPositionWalkable((12,6,0))):
                    passable = True
                if offset == (-1,0) and (not newRoom or newRoom.getPositionWalkable((12,6,0))) and (not oldRoom or oldRoom.getPositionWalkable((0,6,0 ))):
                    passable = True

                if not passable:
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

    def getPathCommandTile(self,tilePos,startPos,targetPos,tryHard=False,avoidItems=None,localRandom=None,ignoreEndBlocked=None):
        path = self.getPathTile(tilePos,startPos,targetPos,tryHard,avoidItems,localRandom,ignoreEndBlocked=ignoreEndBlocked)

        command = ""
        movementMap = {(1,0):"d",(-1,0):"a",(0,1):"s",(0,-1):"w"}
        if path:
            for offset in path:
                command += movementMap[offset]
        return (command,path)


    def getPathTile(self,tilePos,startPos,targetPos,tryHard=False,avoidItems=None,localRandom=None,ignoreEndBlocked=None):
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

                if newPos[0] > 13 or newPos[1] > 13 or newPos[0] < 1 or newPos[1] < 1:
                    continue

                if not self.getPositionWalkable((newPos[0]+tilePos[0]*15,newPos[1]+tilePos[1]*15,newPos[2]+tilePos[2]*15)) and not newPos == targetPos:
                    continue

                if not tryHard:
                    items = self.getItemByPosition((newPos[0]+tilePos[0]*15,newPos[1]+tilePos[1]*15,newPos[2]+tilePos[2]*15))
                    if items and items[0].type == "LandMine":
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

    def addCharacter(self, character, x, y):
        """
        add a character to the terrain

        Parameters:
            character: the character to add
            x: the x position to add the character on
            y: the y position to add the character on
        """

        self.characters.append(character)
        character.terrain = self
        character.room = None
        character.xPosition = x
        character.yPosition = y
        character.changed()
        self.changed("entered terrain", character)
        src.interaction.new_chars.add(character)

    # obsolete: debugging code for obsolete code
    # bad code: is part visual debugging and partially looking nice, it still has to be integrated properly
    # bad code: urwid specific code
    # bad code: is an overlay
    def addWatershedOverlay(self, chars):
        """
        paint the information for the pathfinding

        Parameters:
            chars: the current rendering to extend
        """

        import urwid

        # define colors for the sections
        colors = [
            "#fff",
            "#ff0",
            "#f0f",
            "#0ff",
            "#f00",
            "#0f0",
            "#00f",
            "#55f",
            "#f55",
            "#5f5",
            "#055",
            "#505",
            "#550",
        ]
        colorByType = {}

        # determine the section the player is in
        mainCharPair = None
        if src.gamestate.gamestate.mainChar.terrain:
            mainCharPair = self.watershedCoordinates[
                (
                    src.gamestate.gamestate.mainChar.xPosition,
                    src.gamestate.gamestate.mainChar.yPosition,
                )
            ][0]

        # assign the colors to the sections
        counter = 0
        for item in self.watershedStart:
            colorByType[item] = colors[counter % len(colors)]
            counter += 1

        # encode the distance to node as string and show instead of the normal terrain
        for coordinate, value in self.watershedCoordinates.items():
            if value[1] < 10:
                display = "0" + str(value[1])
            else:
                display = str(value[1])

            if mainCharPair == value[0]:
                chars[coordinate[1]][coordinate[0]] = (
                    urwid.AttrSpec("#333", "default"),
                    display,
                )
            else:
                chars[coordinate[1]][coordinate[0]] = (
                    urwid.AttrSpec(colorByType[value[0]], "default"),
                    display,
                )

        # mark the paths between nodes
        counter = 3
        for dualPair, path in self.foundPaths.items():
            for coordinate in path:
                if dualPair in self.applicablePaths:
                    chars[coordinate[1]][coordinate[0]] = (
                        urwid.AttrSpec("#888", "default"),
                        "XX",
                    )
                else:
                    chars[coordinate[1]][coordinate[0]] = (
                        urwid.AttrSpec(colors[counter % len(colors)], "default"),
                        "XX",
                    )
            counter += 1

        # show pathfinding to next node
        for newCoordinate, counter in self.obseveredCoordinates.items():
            if counter < 10:
                display = "0" + str(counter)
            else:
                display = str(counter)
            chars[newCoordinate[1]][newCoordinate[0]] = (
                urwid.AttrSpec("#888", "default"),
                display,
            )

        chars[src.gamestate.gamestate.mainChar.yPosition][
            src.gamestate.gamestate.mainChar.xPosition
        ] = src.gamestate.gamestate.mainChar.display

    # obsolete: pathfinding is not really used right now
    def findPath(self, start, end):
        """
        find path between start and end coordinates
        """

        # clear pathfinding state
        self.applicablePaths = {}
        self.obseveredCoordinates = {}

        # get start node
        if start not in self.watershedCoordinates:
            return
        startPair = self.watershedCoordinates[start][0]

        # get paths that can be taken from start node
        for dualPair, path in self.foundPaths.items():
            if startPair in dualPair:
                self.applicablePaths[dualPair] = path

        # get super node for start node
        if startPair not in self.watershedSuperCoordinates:
            return
        startSuper = self.watershedSuperCoordinates[startPair]

        # find path to any point an a path leading to the start node
        entryPoint = self.mark([start])
        if not entryPoint:
            return

        # get path from start position to start node
        startCoordinate = Coordinate(entryPoint[0][0], entryPoint[0][1])
        startNode = entryPoint[1][1]
        pathToStartNode = self.foundPaths[entryPoint[1]][
            self.foundPaths[entryPoint[1]].index((startCoordinate.x, startCoordinate.y))
            + 1 :
        ]

        # clear pathfinding state
        self.applicablePaths = {}
        self.obseveredCoordinates = {}

        # get end node
        ends = (
            end,
            (end[0] - 1, end[1]),
            (end[0] + 1, end[1]),
            (end[0], end[1] - 1),
            (end[0], end[1] + 1),
        )
        found = False
        for end in ends:
            if end in self.watershedCoordinates:
                found = True
                break

        if not found:
            src.logger.debugMessages.append("did not find end in watershedCoordinates")
            return
        endPair = self.watershedCoordinates[end][0]

        # get paths that can be taken from end node
        for dualPair, path in self.foundPaths.items():
            if endPair in dualPair:
                self.applicablePaths[dualPair] = path

        # get super node for end node
        if endPair not in self.watershedSuperCoordinates:
            return
        endSuper = self.watershedSuperCoordinates[endPair]

        # find path to any point an a path leading to the end node
        exitPoint = self.mark([end])
        if not exitPoint:
            src.logger.debugMessages.append("did not find exit point")
            return

        # get path from end position to end node
        endCoordinate = Coordinate(exitPoint[0][0], exitPoint[0][1])
        endNode = exitPoint[1][0]
        pathToEndNode = self.foundPaths[exitPoint[1]][
            1 : self.foundPaths[exitPoint[1]].index((endCoordinate.x, endCoordinate.y))
            + 1
        ]

        # find path from start node to end node
        path = []

        # find path from node to node using the supernodes
        if not startSuper[0] == endSuper[0]:
            if endSuper[0] in self.watershedSuperNodeMap[startSuper[0]]:
                path = self.foundSuperPathsComplete[(startSuper[0], endSuper[0])]
            else:
                path = (
                    self.foundSuperPathsComplete[
                        (startSuper[0], self.watershedSuperNodeMap[startSuper[0]][0])
                    ]
                    + self.foundSuperPathsComplete[
                        (self.watershedSuperNodeMap[startSuper[0]][0], endSuper[0])
                    ]
                )
            path = (
                pathToStartNode
                + self.findWayNodeBased(
                    Coordinate(entryPoint[1][1][0], entryPoint[1][1][1]),
                    Coordinate(startSuper[0][0], startSuper[0][1]),
                )
                + path
            )
            path = (
                path
                + self.findWayNodeBased(
                    Coordinate(endSuper[0][0], endSuper[0][1]),
                    Coordinate(endNode[0], endNode[1]),
                )
                + pathToEndNode
            )
        # find path directly from node to node
        else:
            path = (
                pathToStartNode
                + self.findWayNodeBased(
                    Coordinate(startNode[0], startNode[1]),
                    Coordinate(endNode[0], endNode[1]),
                )
                + pathToEndNode
            )

        # stitch together the path
        if not entryPoint[2][0] == start:
            entryPoint[2].reverse()
        path = entryPoint[2] + path + exitPoint[2][1:]

        # return cleaned up path
        return src.gameMath.removeLoops(path)

    # bad code: simliar to the other pathfinding
    # obsolete: part of the obsolete pathfinding
    def markWalkBack(
        self, coordinate, obseveredCoordinates, pathToEntry, counter=0, limit=1000
    ):
        """
        construct the path to a coordinate by walking backwards from this coordinate back to the starting point

        Parameters:
            coordinate: current coordinate
            obseveredCoordinates: coordinates checked already
            pathToEntry: path gathered so far
            counter: how many iterations were done so far
            limit: rating of the previous try
        """

        # add current coordinate
        pathToEntry.append((coordinate[0], coordinate[1]))

        found = None

        # go back to position with lowest moves to start position
        for newCoordinate in [
            (coordinate[0] - 1, coordinate[1]),
            (coordinate[0], coordinate[1] - 1),
            (coordinate[0] + 1, coordinate[1]),
            (coordinate[0], coordinate[1] + 1),
        ]:
            if newCoordinate not in obseveredCoordinates:
                continue
            if obseveredCoordinates[newCoordinate] >= limit:
                continue
            if (not found) or (
                obseveredCoordinates[found] < obseveredCoordinates[newCoordinate]
            ):
                found = newCoordinate

        # walk back till start
        if found:
            self.markWalkBack(
                found,
                obseveredCoordinates,
                pathToEntry,
                counter + 1,
                obseveredCoordinates[found],
            )

    # osolete: part of the unused pahfinding
    def mark(self, coordinates, counter=0, obseveredCoordinates={}):
        """
        find path to the nearest entry point to a path

        Parameters:
            coordinates: coordinates to check from
            counter: how many tries were done so far
            obseveredCoordinates: coordinates already checked
        """

        # limit recursion depth
        if counter > 30:
            return

        newCoordinates = []
        # increase radius around current position
        if not counter == 0:
            for coordinate in coordinates:
                for newCoordinate in [
                    (coordinate[0] - 1, coordinate[1]),
                    (coordinate[0], coordinate[1] - 1),
                    (coordinate[0] + 1, coordinate[1]),
                    (coordinate[0], coordinate[1] + 1),
                ]:
                    if newCoordinate in self.nonMovablecoordinates:
                        continue
                    if newCoordinate in self.obseveredCoordinates:
                        continue
                    newCoordinates.append(newCoordinate)
        # start from current position
        else:
            newCoordinates.append(coordinates[0])

        # check for intersections with a path
        for newCoordinate in newCoordinates:
            self.obseveredCoordinates[newCoordinate] = counter
            for dualPair, path in self.applicablePaths.items():
                if newCoordinate in path:
                    # get path by walking back to the start
                    pathToEntry = []
                    self.markWalkBack(
                        newCoordinate, self.obseveredCoordinates, pathToEntry
                    )
                    return (newCoordinate, dualPair, pathToEntry)

        # continue increasing the radius until path was intersected
        if newCoordinates:
            return self.mark(newCoordinates, counter + 1, obseveredCoordinates)

    def findWayNodeBased(self, start, end):
        """
        find path between start and end nodes using precalculated paths between nodes

        Parameters:
            start: the start node
            end: the end node

        Returns:
            the path found
        """

        index = 0
        nodeMap = {}
        neighbourNodes = []

        # start with start node
        startNode = (start.x, start.y)
        neighbourNodes.append(startNode)
        nodeMap[startNode] = (None, 0)

        # abort because start node is end node
        if startNode == (end.x, end.y):
            lastNode = startNode

        # mode to neighbour nodes till end node is reached
        else:
            lastNode = None
            counter = 1
            while not lastNode:
                for neighbourNode in neighbourNodes[:]:
                    for watershedNode in self.watershedNodeMap[neighbourNode]:
                        if watershedNode not in neighbourNodes:
                            neighbourNodes.append(watershedNode)
                            nodeMap[watershedNode] = (neighbourNode, counter)
                        if watershedNode == (end.x, end.y):
                            lastNode = watershedNode
                            break
                counter += 1

                if counter == 20:
                    raise Exception(
                        "unable to find end node from "
                        + str(start.x)
                        + " / "
                        + str(start.y)
                        + " to "
                        + str(end.x)
                        + " / "
                        + str(end.y)
                    )

        # walk back to start node and stitch together path
        outPath = []
        if lastNode:
            while nodeMap[lastNode][0]:
                extension = []
                if (lastNode, nodeMap[lastNode][0]) in self.foundPaths:
                    extension = self.foundPaths[(lastNode, nodeMap[lastNode][0])][:-1]
                    extension = list(reversed(extension))
                else:
                    extension = self.foundPaths[(nodeMap[lastNode][0], lastNode)][1:]
                outPath = extension + outPath
                lastNode = nodeMap[lastNode][0]

        return outPath

    def addRooms(self, rooms):
        """
        add rooms to terrain and add them to internal datastructures

        Parameters:
            rooms: the rooms to add
        """

        self.rooms.extend(rooms)
        for room in rooms:
            room.terrain = self
            room.container = self
            if (room.xPosition, room.yPosition) in self.roomByCoordinates:
                self.roomByCoordinates[(room.xPosition, room.yPosition)].append(room)
            else:
                self.roomByCoordinates[(room.xPosition, room.yPosition)] = [room]

    def removeItem(self, item, recalculate=True):
        """
        remove item from terrain

        Parameters:
            item: the item to remove
            recalculate: flag to prevent recalculatio of the pathfinding
        """

        pos = (item.xPosition, item.yPosition, item.zPosition)

        try:
            itemList = self.getItemByPosition(pos)
            itemList.remove(item)
        except:
            pass

        item.xPosition = None
        item.zPosition = None
        item.yPosition = None
        item.container = None

    def removeItems(self, items, recalcuate=True):
        """
        remove items from terrain

        Parameters:
            items: the items to remove
            recalculate: flag to prevent recalculatio of the pathfinding
        """

        for item in items[:]:
            self.removeItem(item, recalculate=False)

    def addItem(self, item, pos, actor=None):
        """
        add item to terrain

        Parameters:
            item: the item to add
            pos: the position to add the item to
        """

        self.addItems([(item, pos)],actor=actor)

    def addItems(self, items, recalculate=True, actor=None):
        """
        add items to terrain and add them to internal datastructures

        Parameters:
            items: a list of tuples containing an item and the position to add it
        """

        recalc = False
        for itemPair in items:
            item = itemPair[0]
            item.container = self

            if not item.walkable:
                recalc = True

            position = tuple(itemPair[1])
            if position[0] % 15 == 0:
                if position[1] % 15 < 7:
                    position = (position[0] + 1, position[1] + 1, position[2])
                elif position[1] % 15 > 7:
                    position = (position[0] + 1, position[1] - 1, position[2])
                else:
                    position = (position[0] + 1, position[1] , position[2])
            if position[0] % 15 == 14:
                if position[1] % 15 < 7:
                    position = (position[0] - 1, position[1] + 1, position[2])
                elif position[1] % 15 > 7:
                    position = (position[0] - 1, position[1] - 1, position[2])
                else:
                    position = (position[0] - 1, position[1] , position[2])
            if position[1] % 15 == 0:
                if position[0] % 15 < 7:
                    position = (position[0] + 1, position[1] + 1, position[2])
                elif position[0] % 15 > 7:
                    position = (position[0] - 1, position[1] + 1, position[2])
                else:
                    position = (position[0] , position[1] + 1, position[2])
            if position[1] % 15 == 14:
                if position[0] % 15 < 7:
                    position = (position[0] + 1, position[1] - 1, position[2])
                elif position[0] % 15 > 7:
                    position = (position[0] - 1, position[1] - 1, position[2])
                else:
                    position = (position[0] , position[1] - 1, position[2])

            item.xPosition = position[0]
            item.yPosition = position[1]
            item.zPosition = position[2]

            if position in self.itemsByCoordinate:
                if len(self.itemsByCoordinate[position]) > 20:
                    print("stack of %s items found on %s"%(len(self.itemsByCoordinate[position]),position,))

                self.itemsByCoordinate[position].insert(0, item)
            else:
                self.itemsByCoordinate[position] = [item]

    def paintFloor(self,size=None,coordinateOffset=None):
        """
        draw the floor

        Returns:
            the rendered floor
        """

        if not self.hidden:
            displayChar = self.floordisplay
        else:
            displayChar = src.canvas.displayChars.void

        chars = []

        if size[0] > coordinateOffset[0]:
            for i in range(0,coordinateOffset[0]-size[0]):
                line = []
                for j in range(0, size[1]):
                    line.append(src.canvas.displayChars.void)

        for i in range(0, 250):
            line = []

            if coordinateOffset[1] < 0:
                for j in range(0,-coordinateOffset[1]):
                    line.append(src.canvas.displayChars.void)

            for j in range(0, 250):
                line.append(displayChar)
            chars.append(line)
        return chars

    def getNearbyRooms(self, pos):
        """
        get nearby rooms

        Parameters:
            pos: the position to get nearby rooms for
        Returns:
            a list of nearby rooms
        """
        
        roomCandidates = []
        possiblePositions = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                possiblePositions.add((pos[0] - i, pos[1] - j))
        for coordinate in possiblePositions:
            if coordinate in self.roomByCoordinates:
                roomCandidates.extend(self.roomByCoordinates[coordinate])

        return roomCandidates

    def getRoomsOnFineCoordinate(self, pos):
        """
        get rooms on a coordinate

        Parameters:
            pos: the coordinate to check if there is a room on it
        """

        rooms = []
        for room in self.getNearbyRooms((pos[0] // 15, pos[1] // 15)):
            if (
                room.xPosition * 15 + room.offsetX < pos[0]
                and room.xPosition * 15 + room.offsetX + room.sizeX > pos[0]
                and room.yPosition * 15 + room.offsetY < pos[1]
                and room.yPosition * 15 + room.offsetY + room.sizeY > pos[1]
            ):

                rooms.append(room)
        return rooms

    def render(self,size=None,coordinateOffset=(0,0)):
        """
        render the terrain and its contents

        Returns:
            the rendered terrain
        """

        # hide/show map
        global mapHidden
        if src.gamestate.gamestate.mainChar.room is None:
            mapHidden = False
        else:
            if src.gamestate.gamestate.mainChar.room.open:
                mapHidden = False
            else:
                mapHidden = True
        # mapHidden = False
        self.hidden = mapHidden

        # paint floor
        chars = self.paintFloor(size=size,coordinateOffset=coordinateOffset)
        for x in range(0, 225):
            if (x < coordinateOffset[1] or x > coordinateOffset[1]+size[1]):
                continue

            for y in range(0, 16):
                if not ((y < coordinateOffset[0] or y > coordinateOffset[0]+size[0])):
                    chars[y-coordinateOffset[0]][x-coordinateOffset[1]] = src.canvas.displayChars.forceField
                if not ((y+14*15-1 < coordinateOffset[0] or y+14*15-1 > coordinateOffset[0]+size[0])):
                    chars[y-coordinateOffset[0] + 14 * 15 - 1][x-coordinateOffset[1]] = src.canvas.displayChars.forceField

        for y in range(0, 225):
            if (y < coordinateOffset[0] or y > coordinateOffset[0]+size[0]):
                continue

            for x in range(0, 16):
                if not (x < coordinateOffset[1] or x > coordinateOffset[1]+size[1]):
                    try:
                        chars[y-coordinateOffset[0]][x-coordinateOffset[1]] = src.canvas.displayChars.forceField
                    except:
                        raise Exception("%s %s"%(coordinateOffset[0],coordinateOffset[1]))
                if not (x + 14 * 15 - 1 < coordinateOffset[1] or x + 14 * 15 - 1 > coordinateOffset[1]+size[1]):
                    chars[y-coordinateOffset[0]][x-coordinateOffset[1] + 14 * 15 - 1] = src.canvas.displayChars.forceField

        # show/hide rooms
        for room in self.rooms:
            if src.gamestate.gamestate.mainChar.room == room:
                room.hidden = False
            else:
                if not mapHidden and room.open and room.hidden:
                    room.hidden = False
                    room.applySkippedAdvances()  # ensure the rooms state is up to date
                else:
                    room.hidden = True

        for bigX in range(0, 14):
            if bigX*15 < coordinateOffset[1]-15 or bigX*15 > coordinateOffset[1]+size[1]+15:
                continue

            for bigY in range(0, 14):
                if bigY*15 < coordinateOffset[0]-15 or bigY*15 > coordinateOffset[0]+size[0]+15:
                    continue

                for x in range(0, 15):
                    for y in range(0, 15):

                        if x == 7 or y == 7:
                            continue

                        if not (bigX*15+x < coordinateOffset[1] or bigX*15+x > coordinateOffset[1]+size[1] or
                                bigY*15 < coordinateOffset[0] or bigY*15 > coordinateOffset[0]+size[0]):
                            chars[bigY * 15 + 0 - coordinateOffset[0]][
                                bigX * 15 + x - coordinateOffset[1]
                            ] = src.canvas.displayChars.forceField

                        if not (bigX*15+x < coordinateOffset[1] or bigX*15+x > coordinateOffset[1]+size[1] or
                                bigY*15+14 < coordinateOffset[0] or bigY*15+14 > coordinateOffset[0]+size[0]):
                            chars[bigY * 15 + 14 - coordinateOffset[0]][
                                bigX * 15 + x - coordinateOffset[1]
                            ] = src.canvas.displayChars.forceField

                        if not (bigX*15 < coordinateOffset[1] or bigX*15 > coordinateOffset[1]+size[1] or
                                bigY*15+y < coordinateOffset[0] or bigY*15+y > coordinateOffset[0]+size[0]):
                            chars[bigY * 15 + y - coordinateOffset[0]][
                                bigX * 15 + 0 - coordinateOffset[1]
                            ] = src.canvas.displayChars.forceField

                        if not (bigX*15+14 < coordinateOffset[1] or bigX*15+14 > coordinateOffset[1]+size[1] or
                                bigY*15+y < coordinateOffset[0] or bigY*15+y > coordinateOffset[0]+size[0]):
                            chars[bigY * 15 + y - coordinateOffset[0]][
                                bigX * 15 + 14 - coordinateOffset[1]
                            ] = src.canvas.displayChars.forceField

        # calculate room visibility
        if not mapHidden:
            # get players position in tiles (15*15 segments)
            pos = None
            if src.gamestate.gamestate.mainChar.room is None:
                pos = (
                    src.gamestate.gamestate.mainChar.xPosition // 15,
                    src.gamestate.gamestate.mainChar.yPosition // 15,
                )
            else:
                pos = (
                    src.gamestate.gamestate.mainChar.room.xPosition,
                    src.gamestate.gamestate.mainChar.yPosition,
                )

            # get rooms near the player
            roomCandidates = self.getNearbyRooms(pos)

            # show rooms near the player
            for room in roomCandidates:
                if room.open:
                    room.hidden = False
                    room.applySkippedAdvances()  # ensure the rooms state is up to date

        # draw items on map
        if not mapHidden:
            for entry in self.itemsByCoordinate.values():
                if not entry:
                    continue
                item = entry[0]
                if not item.xPosition or not item.yPosition:
                    continue

                if (item.xPosition < coordinateOffset[1] or item.xPosition > coordinateOffset[1]+size[1] or
                    item.yPosition < coordinateOffset[0] or item.yPosition > coordinateOffset[0]+size[0]):
                   continue

                if not (item.yPosition and item.xPosition):
                    continue
                if not (item.zPosition == src.gamestate.gamestate.mainChar.zPosition):
                    continue

                try:
                    chars[item.yPosition-coordinateOffset[0]][item.xPosition-coordinateOffset[1]] = item.render()
                except:
                    pass

        # render each room
        for room in self.rooms:

            # skip hidden rooms
            # if mapHidden and room.hidden:
            #    continue
            if src.gamestate.gamestate.mainChar not in room.characters:
                room.hidden = True
            room.hidden = False

            # get the render for the room
            renderedRoom = room.render()

            # pace rendered room on rendered terrain
            xOffset = room.xPosition * 15 + room.offsetX
            yOffset = room.yPosition * 15 + room.offsetY
            lineCounter = 0
            for line in renderedRoom:
                rowCounter = 0
                for char in line:
                    if (rowCounter + xOffset < coordinateOffset[1] or rowCounter + xOffset > coordinateOffset[1]+size[1] or
                            lineCounter + yOffset < coordinateOffset[0] or lineCounter + yOffset > coordinateOffset[0]+size[0]):
                        rowCounter += 1
                        continue
                    chars[lineCounter + yOffset - coordinateOffset[0]][rowCounter + xOffset-coordinateOffset[1]] = char
                    rowCounter += 1
                lineCounter += 1

        # add overlays
        if not mapHidden:
            # src.overlays.QuestMarkerOverlay().apply(chars,src.gamestate.gamestate.mainChar,src.canvas.displayChars)
            src.overlays.NPCsOverlay().apply(chars, self,size=size,coordinateOffset=coordinateOffset)
            src.overlays.MainCharOverlay().apply(
                chars, src.gamestate.gamestate.mainChar,size=size,coordinateOffset=coordinateOffset
            )

        # add special overlay
        if self.overlay:
            self.overlay(chars)

        for quest in src.gamestate.gamestate.mainChar.getActiveQuests():
            for marker in quest.getQuestMarkersSmall(src.gamestate.gamestate.mainChar):
                pos = marker[0]
                pos = (src.gamestate.gamestate.mainChar.xPosition-2,src.gamestate.gamestate.mainChar.yPosition)
                pos = (pos[0]+coordinateOffset[1],pos[1]+coordinateOffset[0])
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

                if isinstance(display[0],tuple):
                    continue

                if hasattr(display[0],"fg"):
                    display = (src.interaction.urwid.AttrSpec(display[0].fg,"#555"),display[1])
                else:
                    display = (src.interaction.urwid.AttrSpec(display[0].foreground,"#555"),display[1])

                if actionMeta:
                    actionMeta.content = display
                    display = actionMeta

                chars[pos[1]][pos[0]] = display
            pass

        return chars

    def renderTiles(self):
        chars = []
        for y in range(0,15):
            chars.append([])
            for x in range(0,15):
                if y == 0 or x == 0 or y == 14 or x == 14:
                    chars[y].append(src.canvas.displayChars.forceField)
                else:
                    chars[y].append(src.canvas.displayChars.dirt)

        for room in self.rooms:
            color = "#334"
            chars[room.yPosition][room.xPosition] = room.displayChar

        homePos = (src.gamestate.gamestate.mainChar.registers.get("HOMEx"),src.gamestate.gamestate.mainChar.registers.get("HOMEy"))
        if homePos[0] and homePos[1]:
            chars[homePos[1]][homePos[0]] = "HH"

        for quest in src.gamestate.gamestate.mainChar.getActiveQuests():
            for marker in quest.getQuestMarkersTile(src.gamestate.gamestate.mainChar):
                pos = marker[0]
                try:
                    display = chars[pos[1]][pos[0]]
                except:
                    continue

                if isinstance(display,int):
                    display = src.canvas.displayChars.indexedMapping[display]
                if isinstance(display,str):
                    display = (src.interaction.urwid.AttrSpec("#fff","black"),display)

                if marker[1] == "target":
                    color = "#fff"
                else:
                    color = "#555"
                if hasattr(display[0],"fg"):
                    display = (src.interaction.urwid.AttrSpec(display[0].fg,color),display[1])
                else:
                    display = (src.interaction.urwid.AttrSpec(display[0].foreground,color),display[1])

                chars[pos[1]][pos[0]] = display
            pass

        for scrapField in self.scrapFields:
             chars[scrapField[1]][scrapField[0]] = "ss"

        displayChar = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@ ")
        if isinstance(src.gamestate.gamestate.mainChar.container,src.rooms.Room):
            chars[src.gamestate.gamestate.mainChar.container.yPosition][src.gamestate.gamestate.mainChar.container.xPosition] = displayChar
        else:
            chars[src.gamestate.gamestate.mainChar.yPosition//15][src.gamestate.gamestate.mainChar.xPosition//15] = displayChar

        return chars

    def getAffectedByRoomMovementDirection(
        self, room, direction, force=1, movementBlock=set()
    ):
        """
        get things that would be affected if a room would move

        Parameters:
            room: the room to move
            direction: the direction to move the room in
            force: how much force is behind the movement
            movementBlock: the thing affected by the movement
        """

        # determine rooms that the room could collide with
        roomCandidates = []
        bigX = room.xPosition
        bigY = room.yPosition
        possiblePositions = set()
        for i in range(-2, 2):
            for j in range(-2, 2):
                possiblePositions.add((bigX - i, bigY - j))
        for coordinate in possiblePositions:
            if coordinate in self.roomByCoordinates:
                roomCandidates.extend(self.roomByCoordinates[coordinate])

        # get the rooms the room actually collides with
        roomCollisions = set()
        for roomCandidate in roomCandidates:
            if direction == "north":
                if (room.yPosition * 15 + room.offsetY) == (
                    roomCandidate.yPosition * 15
                    + roomCandidate.offsetY
                    + roomCandidate.sizeY
                ):
                    if (
                        room.xPosition * 15 + room.offsetX
                        < roomCandidate.xPosition * 15
                        + roomCandidate.offsetX
                        + roomCandidate.sizeX
                    ) and (
                        room.xPosition * 15 + room.offsetX + room.sizeX
                        > roomCandidate.xPosition * 15 + roomCandidate.offsetX
                    ):
                        roomCollisions.add(roomCandidate)
            elif direction == "south":
                if (room.yPosition * 15 + room.offsetY + room.sizeY) == (
                    roomCandidate.yPosition * 15 + roomCandidate.offsetY
                ):
                    if (
                        room.xPosition * 15 + room.offsetX
                        < roomCandidate.xPosition * 15
                        + roomCandidate.offsetX
                        + roomCandidate.sizeX
                    ) and (
                        room.xPosition * 15 + room.offsetX + room.sizeX
                        > roomCandidate.xPosition * 15 + roomCandidate.offsetX
                    ):
                        roomCollisions.add(roomCandidate)
            elif direction == "west":
                if (room.xPosition * 15 + room.offsetX) == (
                    roomCandidate.xPosition * 15
                    + roomCandidate.offsetX
                    + roomCandidate.sizeX
                ):
                    if (
                        room.yPosition * 15 + room.offsetY
                        < roomCandidate.yPosition * 15
                        + roomCandidate.offsetY
                        + roomCandidate.sizeY
                    ) and (
                        room.yPosition * 15 + room.offsetY + room.sizeY
                        > roomCandidate.yPosition * 15 + roomCandidate.offsetY
                    ):
                        roomCollisions.add(roomCandidate)
            elif direction == "east":
                if (room.xPosition * 15 + room.offsetX + room.sizeX) == (
                    roomCandidate.xPosition * 15 + roomCandidate.offsetX
                ):
                    if (
                        room.yPosition * 15 + room.offsetY
                        < roomCandidate.yPosition * 15
                        + roomCandidate.offsetY
                        + roomCandidate.sizeY
                    ) and (
                        room.yPosition * 15 + room.offsetY + room.sizeY
                        > roomCandidate.yPosition * 15 + roomCandidate.offsetY
                    ):
                        roomCollisions.add(roomCandidate)
            else:
                src.logger.debugMessages.append(
                    "invalid movement direction: " + str(direction)
                )

        # get collisions from the pushed rooms recursively
        for roomCollision in roomCollisions:
            movementBlock.add(roomCollision)
            self.getAffectedByRoomMovementDirection(
                roomCollision, direction, force=force, movementBlock=movementBlock
            )

        # add affected items
        if direction == "north":
            posX = room.xPosition * 15 + room.offsetX - 1
            maxX = room.xPosition * 15 + room.offsetX + room.sizeX - 1
            while posX < maxX:
                posX += 1
                if (
                    posX,
                    room.yPosition * 15 + room.offsetY - 1,
                ) in self.itemByCoordinates:
                    movementBlock.update(
                        self.itemByCoordinates[
                            (posX, room.yPosition * 15 + room.offsetY - 1)
                        ]
                    )
        elif direction == "south":
            posX = room.xPosition * 15 + room.offsetX - 1
            maxX = room.xPosition * 15 + room.offsetX + room.sizeX - 1
            while posX < maxX:
                posX += 1
                if (
                    posX,
                    room.yPosition * 15 + room.offsetY + room.sizeY,
                ) in self.itemByCoordinates:
                    movementBlock.update(
                        self.itemByCoordinates[
                            (posX, room.yPosition * 15 + room.offsetY + room.sizeY)
                        ]
                    )
        elif direction == "west":
            posY = room.yPosition * 15 + room.offsetY - 1
            maxY = room.yPosition * 15 + room.offsetY + room.sizeY - 1
            while posY < maxY:
                posY += 1
                if (
                    room.xPosition * 15 + room.offsetX - 1,
                    posY,
                ) in self.itemByCoordinates:
                    movementBlock.update(
                        self.itemByCoordinates[
                            (room.xPosition * 15 + room.offsetX - 1, posY)
                        ]
                    )
        elif direction == "east":
            posY = room.yPosition * 15 + room.offsetY - 1
            maxY = room.yPosition * 15 + room.offsetY + room.sizeY - 1
            while posY < maxY:
                posY += 1
                if (
                    room.xPosition * 15 + room.offsetX + room.sizeX,
                    posY,
                ) in self.itemByCoordinates:
                    movementBlock.update(
                        self.itemByCoordinates[
                            (room.xPosition * 15 + room.offsetX + room.sizeX, posY)
                        ]
                    )
        else:
            src.logger.debugMessages.append(
                "invalid movement direction: " + str(direction)
            )

    def moveRoomDirection(self, direction, room, force=1, movementBlock=[]):
        """
        actually move a room trough the terrain

        Parameters:
            direction: the direction to move the room in
            room: the room to move
            force: how much force is behind the movement
            movementBlock: the thing affected by the movement
        """

        # move the room
        if direction == "north":
            # naively move the room within current tile
            if room.offsetY > -5:
                room.offsetY -= 1
            # remove room from current tile
            else:
                room.offsetY = 9
                self.removeRoom(room)
                room.yPosition -= 1
                self.addRoom(room)
        elif direction == "south":
            # naively move the room within current tile
            if room.offsetY < 9:
                room.offsetY += 1
            # remove room from current tile
            else:
                room.offsetY = -5
                self.removeRoom(room)
                room.yPosition += 1
                self.addRoom(room)
        elif direction == "east":
            # naively move the room within current tile
            if room.offsetX < 9:
                room.offsetX += 1
            # remove room from current tile
            else:
                room.offsetX = -5
                self.removeRoom(room)
                room.xPosition += 1
                self.addRoom(room)
        elif direction == "west":
            # naively move the room within current tile
            if room.offsetX > -5:
                room.offsetX -= 1
            # remove room from current tile
            else:
                room.offsetX = 9
                self.removeRoom(room)
                room.xPosition -= 1
                self.addRoom(room)

        if room.xPosition < 0:
            src.gamestate.gamestate.mainChar.addMessage("switch to")
            terrain = src.gamestate.gamestate.terrainMap[self.yPosition][
                self.xPosition - 1
            ]
            room.terrain = terrain
            self.removeRoom(room)
            terrain.addRoom(room)
            room.xPosition = 15
        if room.yPosition < 0:
            src.gamestate.gamestate.mainChar.addMessage("switch to")
            terrain = src.gamestate.gamestate.terrainMap[self.yPosition - 1][
                self.xPosition
            ]
            room.terrain = terrain
            self.removeRoom(room)
            terrain.addRoom(room)
            room.yPosition = 15
        if room.xPosition > 15:
            src.gamestate.gamestate.mainChar.addMessage("switch to")
            terrain = src.gamestate.gamestate.terrainMap[self.yPosition][
                self.xPosition + 1
            ]
            room.terrain = terrain
            self.removeRoom(room)
            terrain.addRoom(room)
            room.xPosition = 0
        if room.yPosition > 15:
            src.gamestate.gamestate.mainChar.addMessage("switch to")
            terrain = src.gamestate.gamestate.terrainMap[self.yPosition + 1][
                self.xPosition
            ]
            room.terrain = terrain
            self.removeRoom(room)
            terrain.addRoom(room)
            room.yPosition = 0

        # kill characters driven over by the room
        for char in self.characters:
            if (
                char.xPosition > room.xPosition * 15 + room.offsetX
                and char.xPosition < room.xPosition * 15 + room.offsetX + room.sizeX
                and char.yPosition > room.yPosition * 15 + room.offsetY
                and char.yPosition < room.yPosition * 15 + room.offsetY + room.sizeY
            ):
                char.die()

    def removeRoom(self, room):
        """
        remove a room from terrain

        Parameters:
            room: the room to remove
        """

        self.rooms.remove(room)

        if (room.xPosition, room.yPosition) in self.roomByCoordinates:
            self.roomByCoordinates[(room.xPosition, room.yPosition)].remove(room)
            if not len(self.roomByCoordinates[(room.xPosition, room.yPosition)]):
                del self.roomByCoordinates[(room.xPosition, room.yPosition)]

    def addRoom(self, room):
        """
        add a room to the terrain

        Parameters:
            room: the room to add
        """

        room.terrain = self
        room.container = self
        self.rooms.append(room)

        if (room.xPosition, room.yPosition) in self.roomByCoordinates:
            self.roomByCoordinates[(room.xPosition, room.yPosition)].append(room)
        else:
            self.roomByCoordinates[(room.xPosition, room.yPosition)] = [room]

    def teleportRoom(self, room, newPosition):
        """
        teleport a room to another position

        Parameters:
            room: to room to teleport
            newPosition: the position to teleport the room to
        """

        # remove room from old position
        oldPosition = (room.xPosition, room.yPosition)
        if oldPosition in self.roomByCoordinates:
            if room in self.roomByCoordinates[oldPosition]:
                self.roomByCoordinates[oldPosition].remove(room)
                if not len(self.roomByCoordinates[oldPosition]):
                    del self.roomByCoordinates[oldPosition]

        # add room to new position
        if newPosition in self.roomByCoordinates:
            self.roomByCoordinates[newPosition].append(room)
        else:
            self.roomByCoordinates[newPosition] = [room]
        room.xPosition = newPosition[0]
        room.yPosition = newPosition[1]

    # bad code: should be in saveable
    def setState(self, state):
        """
        set state from dict

        Parameters:
            state: the state to set
            tick: obsolete, ignore
        """
        super().setState(state)

        for roomId in state["roomIds"]:
            room = src.rooms.getRoomFromState(state["roomStates"][roomId], terrain=self)
            self.addRoom(room)

        for eventId in state["eventIds"]:
            eventState = state["eventStates"][eventId]
            event = src.events.getEventFromState(eventState)
            self.addEvent(event)

        for charId in state["characterIds"]:
            charState = state["characterStates"][charId]
            char = src.characters.getCharacterFromState(charState)
            char.terrain = self
            char.room = None
            self.addCharacter(char, charState["xPosition"], charState["yPosition"])

        addItems = []
        for itemId in state["itemIds"]:
            itemState = state["itemStates"][itemId]
            item = src.items.getItemFromState(itemState)
            addItems.append((item, item.getPosition()))
        self.addItems(addItems)

    # bad code: should be in saveable
    def getState(self):
        """
        get state as dict

        Returns:
            semi serialised state
        """

        roomIds = []
        roomStates = {}
        for room in self.rooms:
            roomIds.append(room.id)
            roomStates[room.id] = room.getState()

        itemsOnFloor = []
        for entry in self.itemsByCoordinate.values():
            itemsOnFloor.extend(reversed(entry))
        itemIds = []
        itemStates = {}
        for item in itemsOnFloor:
            itemIds.append(item.id)
            itemStates[item.id] = item.getState()

        exclude = []
        if src.gamestate.gamestate.mainChar:
            exclude.append(src.gamestate.gamestate.mainChar.id)
        characterIds = []
        characterStates = {}
        for character in self.characters:
            if character == src.gamestate.gamestate.mainChar:
                continue
            characterIds.append(character.id)
            characterStates[character.id] = character.getState()

        eventIds = []
        eventStates = {}
        for event in self.events:
            eventIds.append(event.id)
            eventStates[event.id] = event.getState()

        # generate state
        result = super().getState()
        result.update({
            "objType": self.objType,
            "roomIds": roomIds,
            "roomStates": roomStates,
            "itemIds": itemIds,
            "itemStates": itemStates,
            "characterIds": characterIds,
            "characterStates": characterStates,
            "initialSeed": self.initialSeed,
            "eventIds": eventIds,
            "eventStates": eventStates,
        })
        return result

    # bad code: should be in extra class
    def addEvent(self, event):
        """
        add an event to internal structure

        Parameters:
            event: th event to add
        """

        index = 0
        start = 0
        end = len(self.events)

        import random

        while not start == end:
            pivot = (start + end) // 2
            compareEvent = self.events[pivot]
            if compareEvent.tick < event.tick:
                start = pivot + 1
            elif compareEvent.tick == event.tick:
                start = pivot
                end = pivot
                break
            else:
                end = pivot
        self.events.insert(start, event)



class EmptyTerrain(Terrain):
    """
    a empty terrain
    """

    objType = "EmptyTerrain"

class Nothingness(Terrain):
    """
    a almost empty terrain
    """

    objType = "Nothingness"

    def paintFloor(self,size=None,coordinateOffset=None):
        """
        paint floor with minimal variation to ease perception of movement

        Returns:
            the painted floor
        """

        displayChar = self.floordisplay
        if src.gamestate.gamestate.mainChar.zPosition < 0:
            displayChar = "%s" % (src.gamestate.gamestate.mainChar.zPosition,)
        if src.gamestate.gamestate.mainChar.zPosition > 0:
            displayChar = "+%s" % (src.gamestate.gamestate.mainChar.zPosition,)

        chars = []
        for i in range(0,-coordinateOffset[0]):
            line = []
            chars.append(line)

        for i in range(0, 15*15):
            line = []

            if i < coordinateOffset[0] or i > coordinateOffset[0]+size[0]:
                continue

            for j in range(0,-coordinateOffset[1]):
                line.append(src.canvas.displayChars.void)

            for j in range(0, 15*15):

                if coordinateOffset: # game runs horrible without this flag
                    if j < coordinateOffset[1] or j > coordinateOffset[1]+size[1]:
                        continue

                if not self.hidden:
                    display = displayChar
                    display = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": (j,i)}},content=display)
                    line.append(display)
                else:
                    line.append(src.canvas.displayChars.void)
            chars.append(line)

        return chars

    def __init__(self, seed=0, noContent=False):
        """
        state initialization

        Parameters:
            seed: rng seed
            noContent: flag to prevent adding content
        """


        # leave layout empty
        layout = """
        """
        detailedLayout = """
        """

        super().__init__(
            layout,
            detailedLayout,
            seed=seed,
            noPaths=True,
            noContent=noContent,
        )

        if not noContent:
            # add a few items scattered around
            self.dekoItems = []
            for x in range(15, 210):
                for y in range(15, 210):
                    item = None
                    if not x % 23 and not y % 35 and not (x + y) % 5:
                        item = src.items.itemMap["Scrap"](amount=1)
                    if not x % 57 and not y % 22 and not (x + y) % 3:
                        item = src.items.itemMap["Scrap"](amount=3)
                    if not x % 19 and not y % 27 and not (x + y) % 4:
                        item = src.items.itemMap["Scrap"](amount=10)
                    if item:
                        self.dekoItems.append((item, (x, y, 0)))
            self.addItems(self.dekoItems)

        self.floordisplay = src.canvas.displayChars.dirt

# obsolete: should be removed
class GameplayTest(Terrain):
    """
    a gameplay test
    """

    objType = "GameplayTest"

    def __init__(self, seed=0, noContent=False):
        """
        state initialization
        
        Parameters:
            seed: rng seed
            noContent: flag to generate no content
        """

        # add only a few scattered intact rooms
        layout = """
             
             
             
             
             
             
             
             
     .       
    C.       
             
             
             
             
             
        """
        layout = """
        """
        detailedLayout = """
        """

        super().__init__(
            layout, detailedLayout, seed=seed, noContent=noContent
        )

        self.floordisplay = src.canvas.displayChars.dirt

        if not noContent:
            """
            add field of thick scrap
            """

            def addPseudoRandomScrap(maxItems, xRange, yRange, seed=0):
                excludes = {}

                counter = 0
                maxOffsetX = xRange[1] - xRange[0]
                maxOffsetY = yRange[1] - yRange[0]
                while counter < maxItems:

                    position = None
                    while position is None or position in excludes.keys():
                        position = (
                            xRange[0] + seed % maxOffsetX,
                            yRange[0] + seed // (maxItems * 2) % maxOffsetY,
                        )
                        seed += 1

                    excludes[position] = seed % 20

                    seed += seed % 105
                    counter += 1

                counter = 0
                for (key, thickness) in excludes.items():
                    noScrap = False
                    if counter % 5 == 0:
                        if (
                            key[0] // 15 >= 7
                            and key[1] // 15 == 7
                            or (key[0] // 15, key[1] // 15)
                            in ((7, 7), (7, 6), (7, 8), (8, 7), (8, 6), (8, 8))
                        ):
                            continue
                        if key[0] % 15 in (0, 14) or key[1] % 15 in (0, 14):
                            continue
                        if not counter % (5 * 3) == 0:
                            l1types = [
                                src.items.itemMap["Sheet"],
                                src.items.itemMap["Rod"],
                                src.items.itemMap["Sheet"],
                                src.items.itemMap["Mount"],
                                src.items.itemMap["Stripe"],
                                src.items.itemMap["Bolt"],
                                src.items.itemMap["Radiator"],
                            ]
                            self.scrapItems.append(
                                (
                                    l1types[seed % len(l1types)](),
                                    (key[0], key[1], 0),
                                )
                            )
                        else:
                            l2types = [
                                src.items.itemMap["Tank"],
                                src.items.itemMap["Heater"],
                                src.items.itemMap["Connector"],
                                src.items.itemMap["Pusher"],
                                src.items.itemMap["Puller"],
                                src.items.itemMap["GooFlask"],
                                src.items.itemMap["Frame"],
                            ]
                            self.scrapItems.append(
                                (
                                    l2types[seed % len(l2types)](),
                                    (key[0], key[1], 0),
                                )
                            )

                        if seed % 15:
                            noScrap = False
                        else:
                            noScrap = True

                        seed += seed % 37

                    if not noScrap:
                        item = src.items.itemMap["Scrap"](thickness)
                        item.mayContainMice = False
                        self.scrapItems.append((item,( key[0], key[1], 0)))

                    seed += seed % 13
                    counter += 1

            def addPseudoRandomThing(xRange, yRange, modulos, itemType):
                """
                add field of items

                Parameters:
                    xRange: the range of x Positions to cover
                    xRange: the range of y Positions to cover
                    modulos: kind of a rng seed
                    itemType: the kind of thing to add
                """

                for x in range(xRange[0], xRange[1]):
                    for y in range(yRange[0], yRange[1]):
                        # skip pseudorandomly
                        if (
                            x % modulos[0]
                            and y % modulos[1]
                            or (not x % modulos[2] and not x % modulos[3])
                            or x % modulos[4]
                            or not y % modulos[5]
                        ):
                            continue
                        if (x // 15, y // 15) in (
                            (6, 6),
                            (6, 7),
                            (6, 8),
                            (7, 7),
                            (7, 6),
                            (7, 8),
                            (8, 7),
                            (8, 6),
                            (8, 8),
                            (11, 7),
                            (10, 7),
                            (9, 7),
                        ):
                            continue

                        # add scrap
                        self.scrapItems.append((itemType(),(x, y, 0)))

            self.scrapItems = []

            # add scrap
            fieldThickness = seed // 3 % 20
            x = 45
            while x < 180:
                y = 45
                while y < 180:
                    seed += seed % 35
                    if (
                        x in (45, 165)
                        or y in (45, 165)
                        or ((x, y) in ((90, 90), (90, 105), (90, 120)))
                    ):
                        maxItems = (8 * 8) - seed % 10 - fieldThickness
                    elif x >= 75 and x <= 135 and y >= 75 and y <= 135:
                        maxItems = (12 * 12) - seed % 20 - fieldThickness
                    else:
                        maxItems = (15 * 15) - seed % 30 - fieldThickness
                    addPseudoRandomScrap(maxItems, (x, x + 15), (y, y + 15), seed)

                    y += 15
                x += 15
            self.addItems(self.scrapItems)

            self.scrapItems = []

            # add other objects
            addPseudoRandomThing(
                (45, 170), (45, 170), (23, 7, 2, 3, 2, 4), src.items.itemMap["Wall"]
            )
            seed += seed % 35
            addPseudoRandomThing(
                (45, 170), (45, 170), (13, 15, 3, 5, 3, 2), src.items.itemMap["Pipe"]
            )

            toRemove = []
            for item in self.scrapItems:
                subItems = self.getItemByPosition( item[1] )
                for subItem in subItems:
                    toRemove.append(subItem)

            self.addItems(self.scrapItems)

            """
            x = 157
            for y in range(97,129):
                toRemove.extend(self.getItemByPosition((x,y)))
            """

            for item in toRemove:
                self.removeItem(item, recalculate=False)

            seed += seed % 23
            furnace = (
                src.items.itemMap["Furnace"](),
                (90 + seed % 78, 90 + (seed * 5) % 78, 0),
            )
            furnace[0].bolted = False
            seed += seed % 42
            hutch = (
                src.items.itemMap["Hutch"](),
                (90 + seed % 78, 90 + (seed * 5) % 78, 0),
            )
            hutch[0].bolted = False
            seed += seed % 65
            growthTank = (
                src.items.itemMap["GrowthTank"](),
                (90 + seed % 78, 90 + (seed * 5) % 78, 0),
            )
            growthTank[0].bolted = False
            extraItems = [furnace, hutch, growthTank]
            self.addItems(extraItems)

            # add base of operations
            # add base of operations
            self.miniBase = src.rooms.MiniBase(7, 7, 1, 1, seed=seed)
            self.addRooms([self.miniBase])
            # 3,8

            extraItems = []

            # tree = src.items.Tree(67,93,creator=self)
            # extraItems.append(tree)
            # tree = src.items.Tree(103,64,creator=self)
            # extraItems.append(tree)
            # tree = src.items.Tree(80,25,creator=self)
            # extraItems.append(tree)
            # tree = src.items.Tree(125,74,creator=self)
            # extraItems.append(tree)
            # tree = src.items.Tree(15,14,creator=self)
            # extraItems.append(tree)

            # coalMine = src.items.CoalMine(50,112,creator=self)
            # extraItems.append(coalMine)

            self.addItems(extraItems)

            toRemove = []
            for x in range(124, 131):
                for y in range(124, 131):
                    subItems = self.getItemByPosition((x, y, 0))
                    for subItem in subItems:
                        toRemove.append(subItem)

            for item in toRemove:
                self.removeItem(item, recalculate=False)

    def paintFloor(self,size=None,coordinateOffset=None):
        """
        paint floor with minimal variation to ease perception of movement

        Returns:
            the painted floor
        """

        chars = []

        if size[0] > coordinateOffset[0]:
            for i in range(0,coordinateOffset[0]-size[0]):
                line = []
                for j in range(0, size[1]):
                    if j < coordinateOffset[1] or j > coordinateOffset[1]+size[1]:
                        continue

                    line.append(src.canvas.displayChars.void)

        for i in range(0, 250):
            line = []

            if coordinateOffset[1] < 0:
                for j in range(0,-coordinateOffset[1]):
                    line.append(src.canvas.displayChars.void)

            for j in range(0, 250):
                if j < coordinateOffset[1] or j > coordinateOffset[1]+size[1]:
                    continue

                if not self.hidden:
                    line.append(self.floordisplay)
                else:
                    line.append(src.canvas.displayChars.void)
            chars.append(line)
        return chars

class Desert(Terrain):
    """
    a desert map
    """

    objType = "Desert"

    """
    state initialization
    """

    def __init__(self, seed=0, noContent=False):
        """
        state initialization
        
        Parameters:
            seed: rng seed
            noContent: flag to generate no content
        """

        import random

        # add only a few scattered intact rooms
        layout = """
             
             
             
             
             
             
             
             
     .       
    C.       
             
             
             
             
             
        """
        layout = """
        """
        detailedLayout = """
        """

        super().__init__(
            layout, detailedLayout, seed=seed, noContent=noContent
        )

        self.itemPool = []
        self.itemPool.append([src.items.itemMap["SunScreen"](),[0,0,0]])
        self.itemPool.append([src.items.itemMap["SunScreen"](),[0,0,0]])
        self.itemPool.append([src.items.itemMap["SunScreen"](),[0,0,0]])
        machine = src.items.itemMap["Machine"]()
        machine.setToProduce("Rod")
        machine.bolted = False
        self.itemPool.append([machine,[0,0,0]])
        machine = src.items.itemMap["Machine"]()
        machine.setToProduce("Rod")
        machine.bolted = False
        self.itemPool.append([machine,[0,0,0]])
        machine = src.items.itemMap["Machine"]()
        machine.setToProduce("Rod")
        machine.bolted = False
        self.itemPool.append([machine,[0,0,0]])
        machine = src.items.itemMap["Machine"]()
        machine.setToProduce("Rod")
        machine.bolted = False
        self.itemPool.append([machine,[0,0,0]])
        machine = src.items.itemMap["Machine"]()
        machine.setToProduce("Rod")
        machine.bolted = False
        self.itemPool.append([machine,[0,0,0]])
        machine = src.items.itemMap["Machine"]()
        machine.setToProduce("Sheet")
        machine.bolted = False
        self.itemPool.append([machine,[0,0,0]])
        machine = src.items.itemMap["Machine"]()
        machine.setToProduce("Sheet")
        machine.bolted = False
        self.itemPool.append([machine,[0,0,0]])
        machine = src.items.itemMap["Machine"]()
        for i in range(1, 30):
            self.itemPool.append([src.items.itemMap["Sheet"](),[0,0,0]])
            case = src.items.itemMap["Case"]()
            case.bolted = False
            self.itemPool.append([case,[0,0,0]])
            self.itemPool.append([src.items.itemMap["Vial"](),[0,0,0]])
            corpse = src.items.itemMap["Corpse"]()
            corpse.charges = random.randint(100, 300)
            self.itemPool.append([corpse,[0,0,0]])
        for i in range(1, 200):
            self.itemPool.append([src.items.itemMap["Coal"](),[0,0,0]])
            self.itemPool.append([src.items.itemMap["MetalBars"](),[0,0,0]])
            self.itemPool.append([src.items.itemMap["Rod"](),[0,0,0]])
            self.itemPool.append([src.items.itemMap["Scrap"](amount=1),[0,0,0]])
            self.itemPool.append([src.items.itemMap["Scrap"](amount=1),[0,0,0]])
            self.itemPool.append([src.items.itemMap["Scrap"](amount=1),[0,0,0]])

        random.shuffle(self.itemPool)
        for item in self.itemPool:
            while 1:
                x = random.randint(1, 225)
                y = random.randint(1, 225)

                if x % 15 in (0, 14) or y % 15 in (0, 14):
                    continue

                item[1][0] = x
                item[1][1] = y
                break

        waterCondenser = src.items.itemMap["WaterCondenser"]()
        waterCondenser.lastUsage = -10000
        self.addItem(waterCondenser,(6 * 15 + 6, 7 * 15 + 6,0))
        waterCondenser = src.items.itemMap["WaterCondenser"]()
        waterCondenser.lastUsage = -10000
        self.addItem(waterCondenser,(86 * 15 + 6, 7 * 15 + 8,0))
        waterCondenser = src.items.itemMap["WaterCondenser"]()
        waterCondenser.lastUsage = -10000
        self.addItem(waterCondenser,(6 * 15 + 8, 7 * 15 + 6,0))
        waterCondenser = src.items.itemMap["WaterCondenser"]()
        waterCondenser.lastUsage = -10000
        self.addItem(waterCondenser,(6 * 15 + 8, 7 * 15 + 8,0))

        # add base of operations
        self.miniBase = src.rooms.MiniBase2(3, 7, 2, 2, seed=seed)
        self.addRooms([self.miniBase])

        # save internal state
        self.initialState = self.getState()

        self.doSandStorm()
        self.randomizeHeatmap()

    def randomizeHeatmap(self):
        """
        make random tiles dispense heat damage
        """

        # save heatmap for tiles
        import random

        self.heatmap = []
        for x in range(0, 15):
            self.heatmap.append([])
            for y in range(0, 15):
                self.heatmap[x].append(0)
                self.heatmap[x][y] = random.randint(1, 5)

    def doSandStorm(self):
        """
        shuffle items around
        """

        import random

        counter = 0
        toMove = []
        for (position, items) in self.itemsByCoordinate.items():
            for item in items:
                if item.bolted:
                    continue
                self.removeItem(item)
                if counter % 2 == 0:
                    toMove.append(item)
                else:
                    self.itemPool.append((item,position))
                counter += 1

        cutOff = len(self.itemPool) // 10
        toAdd = self.itemPool[:cutOff]
        self.itemPool = self.itemPool[cutOff:]

        for item in toMove:
            x = item.xPosition + random.randint(-1, 1)
            y = item.yPosition + random.randint(-1, 1)
            if x % 15 not in (0, 14) and y % 15 not in (0, 14):
                item.xPosition = x
                item.yPosition = y

        for item in toAdd[: len(toAdd) // 2]:
            x = random.randint(16, 209)
            if x % 15 not in (0, 14):
                item[1][0] = x
            y = random.randint(16, 209)
            if y % 15 not in (0, 14):
                item[1][1] = y
        self.addItems(toAdd)

    def paintFloor(self,size=None,coordinateOffset=None):
        """
        draw the floor

        Returns:
            the rendered floor
        """

        if not self.hidden:
            displayChar = self.floordisplay
        else:
            displayChar = src.canvas.displayChars.void

        desertTiles = [
            (src.interaction.urwid.AttrSpec("#0c2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#2c2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#4c2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#8c2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#ac2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#cc2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#fc2", "black"), "::"),
        ]

        chars = []
        if size[0] > coordinateOffset[0]:
            for i in range(0,coordinateOffset[0]-size[0]):
                line = []
                for j in range(0, size[1]):
                    line.append(src.canvas.displayChars.void)

        for i in range(0, 15*15):
            line = []
            if i < coordinateOffset[0] or i > coordinateOffset[0]+size[0]:
                continue

            if coordinateOffset[1] < 0:
                for j in range(0,-coordinateOffset[1]):
                    line.append(src.canvas.displayChars.void)

            for j in range(0, 15*15):
                if coordinateOffset: # game runs horrible without this flag
                    if j < coordinateOffset[1] or j > coordinateOffset[1]+size[1]:
                        continue

                try:
                    #line.append(desertTiles[self.heatmap[(j+coordinateOffset[1]) // 15][(i+coordinateOffset[k]) // 15]])
                    line.append(desertTiles[self.heatmap[j // 15][i // 15]])
                except:
                    line.append(src.canvas.displayChars.void)
            chars.append(line)
        return chars

    def paintFloor2(self,size=None,coordinateOffset=None):
        """
        paint floor with minimal variation to ease perception of movement

        Returns:
            the painted floor
        """

        desertTiles = [
            (src.interaction.urwid.AttrSpec("#0c2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#2c2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#4c2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#8c2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#ac2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#cc2", "black"), "::"),
            (src.interaction.urwid.AttrSpec("#fc2", "black"), "::"),
        ]

        chars = []
        for i in range(0, 250):
            line = []
            for j in range(0, 250):
                if not self.hidden:
                    try:
                        line.append(desertTiles[self.heatmap[j // 15][i // 15]])
                    except:
                        line.append(src.canvas.displayChars.void)
                else:
                    line.append(src.canvas.displayChars.void)
            chars.append(line)
        return chars

    def moveCharacterDirection(self, char, direction):
        """
        move a character into a direction
        dispense heat damage on hot tiles

        Parameters:
            char: the character to move
            direction: the direction to move the character in
        """

        heatDamage = (
            self.heatmap[char.xPosition // 15][char.yPosition // 15]
            - char.heatResistance
        )
        if heatDamage > 0:
            char.addMessage("The sun burns your skin")
            char.hurt(heatDamage, reason="sunburn")
        return super().moveCharacterDirection(char, direction)


class Base(Nothingness):

    objType = "Base"

    def __init__(self, seed=0, noContent=False):
        super().__init__(
            seed=seed, noContent=noContent
        )

        architect = src.items.itemMap["ArchitectArtwork"]()
        self.addItem(architect,(1,1,0))

        mainRoom = architect.doAddRoom({
                 "coordinate": (7,7),
                 "roomType": "EmptyRoom",
                 "doors": "0,6 6,0 12,6 6,12",
                 "offset": [1,1],
                 "size": [13, 13],
                },
            None,
            )

        architect.doAddScrapfield(9, 7, 280)

        cityBuilder = src.items.itemMap["CityBuilder2"]()
        cityBuilder.bolted = True
        cityBuilder.godMode = True
        cityBuilder.architect = architect
        cityBuilder.scrapFields = self.scrapFields
        for scrapField in cityBuilder.scrapFields:
            mainRoom.sources.append((scrapField,"Scrap"))
        mainRoom.addItem(cityBuilder, (6, 6, 0))

        tradingArtwork = src.items.itemMap["TradingArtwork2"]()
        cityBuilder.bolted = True
        mainRoom.addItem(tradingArtwork, (9, 9, 0))
        tradingArtwork.configure(src.gamestate.gamestate.mainChar)

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

        cityBuilder.addScrapCompactorFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,7),"type":"random"},instaSpawn=True)
        cityBuilder.addScrapCompactorFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,6),"type":"random"},instaSpawn=True)
        cityBuilder.addScrapCompactorFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,8),"type":"random"},instaSpawn=True)
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,8)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,6)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(6,8)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(6,7)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(6,6)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,5)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,9)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(5,7)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(9,5)})
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.spawnRank3(src.gamestate.gamestate.mainChar)
        cityBuilder.spawnRank4(src.gamestate.gamestate.mainChar)
        cityBuilder.spawnRank5(src.gamestate.gamestate.mainChar)
        cityBuilder.spawnRank6(src.gamestate.gamestate.mainChar)

class Base2(Nothingness):

    objType = "Base2"

    def __init__(self, seed=0, noContent=False):
        super().__init__(
            seed=seed, noContent=noContent
        )

        architect = src.items.itemMap["ArchitectArtwork"]()
        self.addItem(architect,(1,1,0))

        mainRoom = architect.doAddRoom({
                 "coordinate": (7,7),
                 "roomType": "EmptyRoom",
                 "doors": "0,6 6,0 12,6 6,12",
                 "offset": [1,1],
                 "size": [13, 13],
                },
            None,
            )

        architect.doAddScrapfield(8, 5, 280)

        cityBuilder = src.items.itemMap["CityBuilder2"]()
        cityBuilder.bolted = True
        cityBuilder.godMode = True
        cityBuilder.architect = architect
        cityBuilder.scrapFields = self.scrapFields
        for scrapField in cityBuilder.scrapFields:
            mainRoom.sources.append((scrapField,"Scrap"))
        mainRoom.addItem(cityBuilder, (1, 5, 0))

        tradingArtwork = src.items.itemMap["TradingArtwork2"]()
        cityBuilder.bolted = True
        mainRoom.addItem(tradingArtwork, (1, 9, 0))
        tradingArtwork.configure(src.gamestate.gamestate.mainChar)

        mainRoom.addInputSlot((5,11,0),"Scrap")
        mainRoom.addInputSlot((4,11,0),"Scrap")
        mainRoom.addInputSlot((3,11,0),"MetalBars")

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
        mainRoom.walkingSpace.add((5,10,0))
        mainRoom.walkingSpace.add((4,10,0))
        mainRoom.walkingSpace.add((3,10,0))

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
        mainRoom.storageRooms = []

        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,7)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(6,7)})
        cityBuilder.addProductionLine1(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine2(src.gamestate.gamestate.mainChar,instaSpawn=True)

        cityBuilder.addTrapRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(6,6)})
        cityBuilder.addTrapRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,6)})
        cityBuilder.addTrapRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,6)})

        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(6,8)})
        cityBuilder.addProductionLine3(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,8)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,8)})
        cityBuilder.addProductionLine1(src.gamestate.gamestate.mainChar,instaSpawn=True)

        cityBuilder.addStorageRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(6,9)},instaSpawn=True)
        cityBuilder.addScrapCompactorFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,9),"type":"random"},instaSpawn=True)
        cityBuilder.addTeleporterRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,9)})

        cityBuilder.setConnectionsFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,6),"selection":"w"},noFurtherInteraction=True)
        cityBuilder.setConnectionsFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,6),"selection":"s"},noFurtherInteraction=True)
        cityBuilder.setConnectionsFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,7),"selection":"w"},noFurtherInteraction=True)
        cityBuilder.setConnectionsFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,7),"selection":"a"},noFurtherInteraction=True)
        cityBuilder.setConnectionsFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,7),"selection":"d"},noFurtherInteraction=True)
        cityBuilder.setConnectionsFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(6,7),"selection":"d"},noFurtherInteraction=True)
        cityBuilder.setConnectionsFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,7),"selection":"a"},noFurtherInteraction=True)
        """
        cityBuilder.addScrapCompactorFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,7),"type":"random"},instaSpawn=True)
        cityBuilder.addScrapCompactorFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,6),"type":"random"},instaSpawn=True)
        cityBuilder.addScrapCompactorFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(8,8),"type":"random"},instaSpawn=True)
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(6,8)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(6,7)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(6,6)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,5)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,9)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(5,7)})
        cityBuilder.addWorkshopRoomFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(9,5)})
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.addProductionLine(src.gamestate.gamestate.mainChar,instaSpawn=True)
        cityBuilder.spawnRank3(src.gamestate.gamestate.mainChar)
        cityBuilder.spawnRank4(src.gamestate.gamestate.mainChar)
        cityBuilder.spawnRank5(src.gamestate.gamestate.mainChar)
        cityBuilder.spawnRank6(src.gamestate.gamestate.mainChar)
        """

class Ruin(Base):
    objType = "Ruin"

    def __init__(self, seed=0, noContent=False):
        super().__init__(
            seed=seed, noContent=noContent
        )

        mainRoom = self.getRoomByPosition((7,7,0))[0]
        for item in mainRoom.itemsOnFloor:
            item.destroy()

        for room in self.rooms:
            for i in range(0,4):
                room.damage()

        for character in self.characters[:]:
            character.die(reason="explosion")

        for room in self.rooms:
            for character in room.characters[:]:
                character.die(reason="explosion")
            for item in room.itemsOnFloor[:]:
                item.charges = 0
                item.bolted = False
                if random.random() > 0.3:
                    item.destroy()

        for room in self.rooms:
            level = 3-(abs(room.yPosition-7)+abs(room.xPosition-7))
            if level < 0:
                continue

            for i in range(0,level):
                enemy = src.characters.Monster()
                room.addCharacter(enemy,random.randint(2,13),random.randint(2,13))
                enemy.macroState["macros"]["g"] = ["g","g","_","g"]
                enemy.health = 100+3*level
                enemy.baseDamage = 10+level
                enemy.runCommandString("_g")

            for i in range(0,2**level):
                room.addItem(src.items.itemMap["GlassCrystal"](),(random.randint(2,13),random.randint(2,13),0))

class ScrapField(Terrain):
    """
    big pile of scrap
    """

    objType = "ScrapField"

    """
    state initialization
    """

    def __init__(self, seed=0, noContent=False):
        """
        state initialization
        
        Parameters:
            seed: rng seed
            noContent: flag to generate no content
        """

        # add only a few scattered intact rooms
        layout = """


  U  U 
U  U 
     U
  U  U

        """
        detailedLayout = """
        """
        super().__init__(
            layout, detailedLayout, seed=seed, noContent=noContent
        )

        self.floordisplay = src.canvas.displayChars.dirt

        def addPseudoRandomScrap(counter, xRange, yRange, skips):
            """
            add field of thick scrap

            Parameters:
                counter: rng seed
                xRange: range of x coordinates to cover
                yRange: range of y coordinates to cover
                skips: positions to leave empty
            Returns:
                rng seed
            """

            for x in range(xRange[0], xRange[1]):
                for y in range(yRange[0], yRange[1]):
                    # skip pseudorandomly
                    toSkip = False
                    for skip in skips:
                        if not x % skip[0] and not y % skip[1]:
                            toSkip = True
                            break
                    if toSkip:
                        continue

                    # add scrap
                    self.scrapItems.append(
                        (src.items.itemMap["Scrap"](counter),(x, y, 0))
                    )
                    counter += 1
                    if counter == 16:
                        counter = 1
            return counter

        def addPseudoRandomThin(xRange, yRange, modulos, itemType):
            """
            add field of items

            Parameters:
                xRange: range of x coordinates to cover
                yRange: range of y coordinates to cover
                modulos: rng seed
                itemType: what to add
            """

            for x in range(xRange[0], xRange[1]):
                for y in range(yRange[0], yRange[1]):
                    # skip pseudorandomly
                    if (
                        x % modulos[0]
                        and y % modulos[1]
                        or (not x % modulos[2] and not x % modulos[3])
                        or x % modulos[4]
                        or not y % modulos[5]
                    ):
                        continue

                    # add scrap
                    self.scrapItems.append((itemType(),(x, y, 0)))

        self.scrapItems = []

        # add scrap
        counter = 3
        counter = addPseudoRandomScrap(
            counter, (20, 30), (30, 110), ((2, 3), (3, 2), (4, 5), (5, 4))
        )

        counter = 3
        counter = addPseudoRandomScrap(
            counter, (20, 30), (30, 110), ((2, 3), (3, 2), (4, 5), (5, 4))
        )
        counter = addPseudoRandomScrap(
            counter, (20, 120), (20, 30), ((2, 3), (3, 2), (4, 5), (5, 4))
        )
        counter = addPseudoRandomScrap(
            counter, (110, 120), (30, 110), ((2, 3), (3, 2), (4, 5), (5, 4))
        )
        counter = addPseudoRandomScrap(
            counter, (20, 120), (110, 120), ((2, 3), (3, 2), (4, 5), (5, 4))
        )
        counter = addPseudoRandomScrap(
            counter, (30, 110), (30, 110), ((2, 7), (5, 3), (23, 2), (13, 9), (5, 17))
        )

        # add other objects
        addPseudoRandomThin((30, 110), (30, 110), (23, 7, 2, 3, 2, 4), src.items.itemMap["Wall"])
        addPseudoRandomThin((30, 110), (30, 110), (13, 15, 3, 5, 3, 2), src.items.itemMap["Pipe"])

        self.addItems(self.scrapItems)

        # add base of operations
        self.wakeUpRoom = src.rooms.MiniBase(0, 4, 0, 0)
        self.addRooms([self.wakeUpRoom])

class TutorialTerrain(Terrain):
    """
    the tutorial mech
    """

    objType = "TutorialTerrain"

    def __init__(self, seed=0, noContent=False):
        """
        state initialization
        
        Parameters:
            seed: rng seed
            noContent: flag to generate no content
        """

        self.toTransport = []

        # the layout for the mech
        layout = """
XlllllllllX
XXXXXXXXXXX
XVv?b?Q?vVX
XO.t    .OX
Xw MQKhl LX
XW Q???Q mX
XU.     .UX
XU CCCCC UX
XU CCCCCtUX
XXXCCCCCXXX """
        detailedLayout = """
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                     
               X                                           X                                                                                                         
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#           #X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               XXXXXXXXXXXX#XX               XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX            X               
                  ###  ###                                                                                                                   XXXXXXXXX               
               ####O####O####      O  O       ################           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # R          #   R        R    #R        R #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #O          O#  O             ##           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #            # ##          O  #O          O#XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #            # #              ##           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #O          O# #               #           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #            # #              ##          ##XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #            ####             #O          OXXX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #O          O#  O          O  ##           XXX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               ##          ##  X              #           XXX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #X         RX####R        R   ##R        R                XXXXXXXXXXXXXX XXXXXXXXXXXXXX XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               #X          XXXX###### ########XXXX8  O                                                                                              X               
               #X             XXXXXXX XXXXXXXXX   8                                                                                                  X               
               #XXXXXXXXXX  X                     8                                                                                                  X              
               ############ #X                    8                                                                                   XXXXXXXX  XXXXXX              
               XXXXXXXXXXX  #X                    8                                                                                    X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                            #X                                                                                                         X#X          #X               
                           ##X                                                                                                         X#X          #X               
               XXXXXXXXXXX   X                                                                                                         X#X                           
               #############                                                                                                           X#X          #X               
               XXXXXXXXXXXXXXX               X#####    #######            XX             XX             XX             X               X#X           X               
               X          X                  X   R        R#X#           #XX#           #XX#           #XX#           #X               X#X                           
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#                            X             #X#           #XX#           #XX#           #XX#           #X                            #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             #X#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X   R        RXX#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#           XX               X             XX#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#      X    XX               X             XX#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#      X    XX               X             XX#           #XX#           #XX#           #XX#           #X               X#X          #X               
               X#XXXXXXX    XX               XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               XXX           X               
               X#########   #X               XX           XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX           XX               XXX           X               
               XXXXXXXXX    #X       X       X#           #XX#           #XX#           #XX#           #XX#           #X       X         X                           
               X#      X    #X  X   XXX   X  X#           #XX#           #XX#           #XX#           #XX#           #X  X   XXX   X  X            #X               
               X#           #X XXX  XXX  XXX X#           #XX#           #XX#           #XX#           #XX#           #X XXX  XXX  XXX X#X          #X               
               X#      X    #X  XX   X    X  X#           #XX#           #XX#           #XX#           #XX#           #X  X    X   XX  X#X          #X               
               X#      X    #XXXXXXX   XXXXXXX#           #XX#           #XX#           #XX#           #XX#           #XXXXXXX   XXXXXXX#           #X               
               X#      X    #XX X XXX XXX X XX#           #XX#           #XX#           #XX#           #XX#           #XX X XXX XXX X XX#           #X               
               X#      X    #XXXXXXX   XXXXXXX#           #XX#           #XX#           #XX#           #XX#           #XXXXXXX   XXXXXXX#           #X               
               X#      X    #X  X    X    X  X#           #XX#           #XX#           #XX#           #XX#           #X  X    X    X  X#           #X               
               X#      X    #X XXX  XXX  XXX X#           #XX#           #XX#           #XX#           #XX#           #X XXX  XXX  XXX X#           #X               
               X#      X    #X  X   XXX   X  X#           #XX#           #XX#           #XX#           #XX#           #X  X   XXX   X  X#           #X               
               XXXXXXXXX    #X       X       X#           #XX#           #XX#           #XX#           #XX#           #X       X                    #X               
               X#############X               X#           #XX#           #XX#           #XX#           #XX#           #X               X#           #X               
               X#XXXXXXX    #X               X# XPXX   XP #XX# XPX    XPX#XX# XPX    XPX#XX# XPX    XPX#XX# XPX    XPX#X               X#           #X               
               XXXXXXXXXXXX  X               XXXXC X XXXC XXXXXXC  XXXXC XXXXXXC  XXXXC XXXXXXC XX XXC XXXXXXC X XXXC XX               XX            X               
               X#XXXXXXXXXXX                     8      8       8      8       8      8       8      8       8      8                  X#            X               
               XX          X                                            .                                                              XX            X               
               X#                                                                                                                      X#            X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               X#          X                                                                                                           X#           #X               
               XXXXXXXXXXXX#                  #              #              #              #              #                            XX            X               
               XXXXXXXXXXXX#                 X#X           XX#X           XX#X           XX#X           XX#X           X               XX            X               
               X                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#            X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               XXXXXXXXXXXX#                 X#X           XX#X           XX#X           XX#X           XX#X           X               XX            X               
               XXXXXXXXXXXX#                 X#X           #X#X           #X#X           #X#X           #X#X           X               XX            X               
               X                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#            X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#x           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               XXXXXXXXXXXX#XX               X#X           XX#X           XX#X           XX#X           XX#X           X               XX            X               
                                             X#X           #X#X           #X#X           #X#X           #X#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
                                             X#XXXXXXXXXXXXXX#XXXXXXXXXXXXXX#XXXXXXXXXXXXXX#XXXXXXXXXXXXXX#XXXXXXXXXXXXX                                             
"""
        super().__init__(
            layout, detailedLayout, seed=seed, noContent=noContent
        )

        # add some tasks to keep npc busy
        self.toTransport = []
        roomsIndices = [0, 1, 2, 3, 5, 6]
        roadBlocks = []
        for index in reversed(roomsIndices):
            room = self.tutorialCargoRooms[index]
            for item in room.storedItems:
                self.toTransport.append((room, (item.xPosition, item.yPosition)))

        # add more transport tasks to keep npcs busy
        x = 12
        while x > 8:
            y = 1
            while y < 9:
                self.toTransport.append((self.tutorialLab, (y, x)))
                y += 1
            x -= 1

        # add some tasks to keep npc busy
        #self.addStorageQuest()

        # add scrap to be cleaned up
        self.scrapItems = [
            (src.items.itemMap["Scrap"](3),(20, 52,0)),
            (src.items.itemMap["Scrap"](3),(19, 53,0)),
            (src.items.itemMap["Scrap"](3),(20, 51,0)),
            (src.items.itemMap["Scrap"](3),(18, 49,0)),
            (src.items.itemMap["Scrap"](3),(21, 53,0)),
            (src.items.itemMap["Scrap"](3),(19, 49,0)),
            (src.items.itemMap["Scrap"](3),(20, 48,0)),
            (src.items.itemMap["Scrap"](3),(18, 50,0)),
            (src.items.itemMap["Scrap"](3),(18, 51,0)),
        ]
        self.addItems(self.scrapItems)

        # move roadblock periodically
        self.waitingRoom.addEvent(
            src.events.EndQuestEvent(
                4000, {"container": self, "method": "addRoadblock"}
            )
        )

    def addStorageQuest(self):
        """
        add quest to move something from the lab to storage
        """

        if not self.toTransport:
            return

        task = self.toTransport.pop()

        # select target room
        roomIndices = [1, 0, 2, 5, 4]
        room = None
        for index in roomIndices:
            if self.tutorialStorageRooms[index].storageSpace:
                room = self.tutorialStorageRooms[index]
                break
        if not room:
            return

        # add quest to waiting room
        quest = src.quests.MoveToStorage(
            [task[0].itemByCoordinates[task[1]][0]], room, creator=self, lifetime=400
        )
        quest.reputationReward = 1
        quest.endTrigger = {"container": self, "method": "addStorageQuest"}
        self.waitingRoom.quests.append(quest)

    def addRoadblock(self):
        """
        add roadblock
        """

        room = self.tutorialCargoRooms[8]
        item = room.storedItems[-1]
        outerQuest = src.quests.MetaQuestSequence([], creator=self)
        innerQuest = src.quests.TransportQuest(item, (None, 127, 81), creator=self)

        # bad code: should happen somewhere else
        def moveAway():
            """
            move character off the placed item
            """

            outerQuest.character.yPosition -= 1

        innerQuest.endTrigger = moveAway
        outerQuest.addQuest(innerQuest)
        self.waitingRoom.quests.append(outerQuest)
        self.waitingRoom.addEvent(
            src.events.EndQuestEvent(
                src.gamestate.gamestate.tick + 4000,
                {"container": self, "method": "moveRoadblockToLeft"},
                creator=self,
            )
        )

    # bad code: should be more abstracted
    def moveRoadblockToLeft(self):
        """
        move roadblock to the left of the map
        """

        # abort if roadblock is missing
        if (127, 81) not in self.itemByCoordinates:
            return

        item = self.itemByCoordinates[(127, 81)][0]
        outerQuest = src.quests.MetaQuestSequence([], creator=self)
        innerQuest = src.quests.TransportQuest(item, (None, 37, 81), creator=self)

        def moveAway():
            """
            move character off the placed item
            """

            outerQuest.character.yPosition -= 1

        innerQuest.endTrigger = moveAway
        outerQuest.addQuest(innerQuest)
        self.waitingRoom.quests.append(outerQuest)
        self.waitingRoom.addEvent(
            src.events.EndQuestEvent(
                src.gamestate.gamestate.tick + 4000,
                {"container": self, "method": "moveRoadblockToRight"},
                creator=self,
            )
        )

    def moveRoadblockToRight(self):
        """
        move roadblock to the left of the map
        """

        # abort if roadblock is missing
        if (37, 81) not in self.itemByCoordinates:
            return

        item = self.itemByCoordinates[(37, 81)][0]
        outerQuest = src.quests.MetaQuestSequence([], creator=self)
        innerQuest = src.quests.TransportQuest(item, (None, 127, 81), creator=self)

        def moveAway():
            """
            move character off the placed item
            """

            outerQuest.character.yPosition -= 1

        innerQuest.endTrigger = moveAway
        outerQuest.addQuest(innerQuest)
        self.waitingRoom.quests.append(outerQuest)
        self.waitingRoom.addEvent(
            src.events.EndQuestEvent(
                src.gamestate.gamestate.tick + 4000,
                {"container": self, "method": "moveRoadblockToLeft"},
                creator=self,
            )
        )


# mapping from strings to all items
# should be extendable
terrainMap = {
    "TutorialTerrain": TutorialTerrain,
    "Nothingness": Nothingness,
    "GameplayTest": GameplayTest,
    "ScrapField": ScrapField,
    "Desert": Desert,
    "Ruin": Ruin,
    "Base": Base,
    "Base2": Base2,
}

def getTerrainFromState(state):
    """
    get item instances from dict state

    Parameters:
        state: the state to set
    Returns:
        the generated terrain
    """

    terrain = terrainMap[state["objType"]](
        seed=state["initialSeed"], noContent=True
    )
    terrain.setState(state)
    terrain.id = state["id"]
    src.saveing.loadingRegistry.register(terrain)
    return terrain
