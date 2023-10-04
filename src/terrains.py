"""
terrains and terrain related code belongs here
"""

import copy
import logging
import random

import numpy as np
import tcod

import src.canvas
import src.events
import src.gameMath
import src.gamestate
import src.items
import src.overlays
import src.quests
import src.rooms

logger = logging.getLogger(__name__)

# bad code: is basically used nowhere
class Coordinate:
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

class Terrain:
    """
    the base class for terrains
    """

    def __init__(
        self,
        seed=0,
        noContent=False,
    ):
        """
        set up internal state

        Parameters:
            seed: rng seed
            noContent: flag to generate terrain empty
        """

        self.noPlacementTiles = []
        self.scrapFields = []
        self.forests = []
        self.collectionSpots = []
        self.ignoreAttributes = []
        self.pathCache = {}
        self.mana = 0
        self.manaRegen = 1
        self.maxMana = 10

        super().__init__()

        self.isRoom = False
        # store terrain content
        self.characters = []
        self.charactersByTile = {}
        self.rooms = []
        self.roomByMap = {}
        self.floordisplay = src.canvas.displayChars.floor
        self.itemsByCoordinate = {}
        self.itemsByBigCoordinate = {}
        self.roomByCoordinates = {}
        self.listeners = {"default": []}
        self.initialSeed = seed
        self.seed = seed
        self.events = []
        self.biomeInfo = {"moisture": 1}
        self.hidden = True
        self.minimapOverride = {(7,7,0):"CC"}
        self.animations = []
        self.pathfinderCache = {}

        self.moistureMap = {}
        moisture = self.biomeInfo["moisture"]
        for x in range(1,14):
            for y in range(1,14):
                self.moistureMap[(x,y,0)] = moisture

        # container for categories of rooms for easy access
        # bad code: should be abstracted
        roomsOnMap = []

        self.xPosition = None
        self.yPosition = None
        self.zPosition = None

        self.lastRender = None

    def callIndirect(self, callback, extraParams={}):
        """
        call a callback that is stored in a savable format

        Parameters:
            callback: the callback to call
            extraParams: some additional parameters
        """

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

    def getPosition(self):
        return (self.xPosition,self.yPosition,0)

    def addAnimation(self,coordinate,animationType,duration,extraInfo):
        if self != src.gamestate.gamestate.mainChar.getTerrain():
            return
        if src.interaction.noFlicker:
            return
        self.animations.append([coordinate,animationType,duration,extraInfo])

    def getRoomsByTag(self,tag):
        result = []
        for room in self.rooms:
            if room.tag != tag:
                continue
            result.append(room)
        return result

    def getRoomsByType(self,roomType):
        result = []
        for room in self.rooms:
            if not isinstance(room,roomType):
                continue
            result.append(room)
        return result

    def getCharactersOnPosition(self,position):
        out = []
        for character in self.characters:
            if character.getPosition() == position:
                out.append(character)
        return out

    def handleFloorClick(self,extraInfo):
        if not src.gamestate.gamestate.mainChar.quests:
            return

        charPos = (src.gamestate.gamestate.mainChar.xPosition//15,src.gamestate.gamestate.mainChar.yPosition//15,0)
        newPos = (extraInfo["pos"][0]//15,extraInfo["pos"][1]//15,0)
        smallNewPos = (extraInfo["pos"][0]%15,extraInfo["pos"][1]%15,0)

        if src.gamestate.gamestate.mainChar.container == self and charPos == newPos:
            quest = src.quests.questMap["GoToPosition"](targetPosition=smallNewPos)
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            src.gamestate.gamestate.mainChar.runCommandString("~")
        else:
            quest = src.quests.questMap["GoToPosition"](targetPosition=smallNewPos)
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            quest = src.quests.questMap["GoToTile"](targetPosition=newPos)
            quest.autoSolve = True
            quest.activate()
            quest.assignToCharacter(src.gamestate.gamestate.mainChar)
            src.gamestate.gamestate.mainChar.quests[0].addQuest(quest)
            src.gamestate.gamestate.mainChar.runCommandString("~")

    def advanceCharacters(self):
        for character in self.characters:
            character.advance()

    def advanceRoom(self):
        for room in self.rooms:
            room.advance()

    def advanceBiomes(self):
        if src.gamestate.gamestate.tick%(15*15) == 0:
            moisture = self.biomeInfo["moisture"]
            for x in range(1,14):
                for y in range(1,14):
                    self.moistureMap[(x,y,0)] = moisture

    def handleEvents(self):
        while (
            self.events
            and self.events[0].tick <= src.gamestate.gamestate.tick
        ):
            event = self.events[0]
            if event.tick < src.gamestate.gamestate.tick:
                1/0
            event.handleEvent()
            self.events.remove(event)

    def advance(self):
        self.lastRender = None

        self.advanceCharacters()
        self.advanceRoom()
        self.advanceBiomes()
        self.handleEvents()

        if src.gamestate.gamestate.tick%(15*15*15) == 0:
            self.mana = 0

            increaseAmount = min(self.manaRegen,self.maxMana-self.mana)
            self.mana += increaseAmount

    def randomAddItems(self, items):
        for item in items:
            pos = (random.randint(15,210),random.randint(15,210),0)

            while (pos[0]//15,pos[1]//15) in self.noPlacementTiles:
                pos = (random.randint(15,210),random.randint(15,210),0)

            self.addItem(item, pos)

    def damage(self):
        pass

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

    def getRoomByPosition(self, position):
        return self.roomByCoordinates.get((position[0],position[1]),[])

    def getNearbyItems(self, character):
        return self.itemsByBigCoordinate.get(character.getBigPosition(),[])[:]

    def shiftPosition(self,position):
        smallX = position[0] % 15
        smallY = position[1] % 15
        if smallX == 0:
            if smallY < 7:
                position = (position[0] + 1, position[1] + 1, position[2])
            elif smallY > 7:
                position = (position[0] + 1, position[1] - 1, position[2])
        if smallX == 14:
            if smallY < 7:
                position = (position[0] - 1, position[1] + 1, position[2])
            elif smallY > 7:
                position = (position[0] - 1, position[1] - 1, position[2])
        if smallY == 0:
            if smallX < 7:
                position = (position[0] + 1, position[1] + 1, position[2])
            elif smallX > 7:
                position = (position[0] - 1, position[1] + 1, position[2])
        if smallY == 14:
            if smallX < 7:
                position = (position[0] + 1, position[1] - 1, position[2])
            elif smallX > 7:
                position = (position[0] - 1, position[1] - 1, position[2])
        return position

    def getItemByPosition(self, position):
        position = self.shiftPosition(position)

        """
        get items on a specific position

        Parameters:
            position: the position to get items from
        Returns:
            the list of items on that position
        """
        return self.itemsByCoordinate.get(position,[])

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

        if tag != "default":
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

        oldBigPos = character.getBigPosition()
        try:
            self.charactersByTile[oldBigPos].remove(character)
        except:
            pass

        while character in self.characters:
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
                    if not char.getItemWalkable(item):
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
            char.timeTaken += char.movementSpeed

            # teleport the character into the room
            room.addCharacter(char, localisedEntry[0], localisedEntry[1])

            oldBigPos = char.getBigPosition()
            while char in self.charactersByTile[oldBigPos]:
                self.charactersByTile[oldBigPos].remove(char)

            if not char.terrain:
                return
            try:
                char.terrain.characters.remove(char)
            except:
                char.addMessage("fail,fail,fail")

            char.changed("entered room", (char, room, direction))
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
            return

        char.container.addAnimation(char.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "#000"), "  ")})
        if direction == "west":
            if char.yPosition % 15 == 0 or char.yPosition % 15 == 14:
                return
            if char.xPosition % 15 == 1:
                if char.yPosition % 15 < 7:
                    direction = "south"
                    char.container.addAnimation(char.getPosition(offset=(-1,1,0)),"charsequence",1,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##"),None]})
                elif char.yPosition % 15 > 7:
                    direction = "north"
                    char.container.addAnimation(char.getPosition(offset=(-1,-1,0)),"charsequence",1,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##"),None]})
                else:
                    if char.xPosition == 16 and 1==0:
                        return
                    else:
                        # char.stasis = True
                        char.runCommandString("aa")
                        char.container.addAnimation(char.getPosition(offset=(-2,0,0)),"charsequence",0,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##")]})
                        pass
                char.addMessage("a force field pushes you")
                char.container.addAnimation(char.getPosition(offset=(-1,0,0)),"charsequence",0,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##")]})

            if char.xPosition % 15 == 14:
                char.changed("changedTile")
                self.removeItems(self.getItemByPosition((char.xPosition-1,char.yPosition,char.zPosition)))

            if char.xPosition % 15 == 0:
                oldBigPos = char.getBigPosition()
                if char in self.charactersByTile[oldBigPos]:
                    self.charactersByTile[oldBigPos].remove(char)
                bigPos = char.getBigPosition((-1,0,0))
                if not bigPos in self.charactersByTile:
                    self.charactersByTile[bigPos] = []
                self.charactersByTile[bigPos].append(char)
        elif direction == "east":
            if char.yPosition % 15 == 0 or char.yPosition % 15 == 14:
                return
            if char.xPosition % 15 == 13:
                if char.yPosition % 15 < 7:
                    direction = "south"
                    char.container.addAnimation(char.getPosition(offset=(1,1,0)),"charsequence",1,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##"),None]})
                elif char.yPosition % 15 > 7:
                    direction = "north"
                    char.container.addAnimation(char.getPosition(offset=(1,-1,0)),"charsequence",1,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##"),None]})
                else:
                    if char.xPosition == 15 * 14 - 2 and 1==0:
                        return
                    else:
                        # char.stasis = True
                        char.runCommandString("dd")
                        char.container.addAnimation(char.getPosition(offset=(2,0,0)),"charsequence",0,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##")]})
                        pass
                char.addMessage("a force field pushes you")
                char.container.addAnimation(char.getPosition(offset=(1,0,0)),"charsequence",0,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##")]})
            if char.xPosition % 15 == 0:
                char.changed("changedTile")
                self.removeItems(self.getItemByPosition((char.xPosition+1,char.yPosition,char.zPosition)))

            if char.xPosition % 15 == 14:
                oldBigPos = char.getBigPosition()
                try:
                    self.charactersByTile[oldBigPos].remove(char)
                except:
                    pass
                bigPos = char.getBigPosition(offset=(1,0,0))
                if not bigPos in self.charactersByTile:
                    self.charactersByTile[bigPos] = []
                self.charactersByTile[bigPos].append(char)
        elif direction == "north":
            if char.xPosition % 15 == 0 or char.xPosition % 15 == 14:
                return
            if char.yPosition % 15 == 1:
                if char.xPosition % 15 < 7:
                    direction = "east"
                    char.container.addAnimation(char.getPosition(offset=(1,-1,0)),"charsequence",1,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##"),None]})
                elif char.xPosition % 15 > 7:
                    direction = "west"
                    char.container.addAnimation(char.getPosition(offset=(-1,-1,0)),"charsequence",1,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##"),None]})
                else:
                    if char.yPosition == 16 and 1==0:
                        return
                    else:
                        # char.stasis = True
                        char.runCommandString("ww")
                        char.container.addAnimation(char.getPosition(offset=(0,-2,0)),"charsequence",0,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##")]})
                        pass
                char.addMessage("a force field pushes you")
                char.container.addAnimation(char.getPosition(offset=(0,-1,0)),"charsequence",0,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##")]})
            if char.yPosition % 15 == 14:
                char.changed("changedTile")
                self.removeItems(self.getItemByPosition((char.xPosition,char.yPosition-1,char.zPosition)))

            if char.yPosition % 15 == 0:
                oldBigPos = char.getBigPosition()
                if char in self.charactersByTile[oldBigPos]:
                    self.charactersByTile[oldBigPos].remove(char)
                bigPos = char.getBigPosition(offset=(0,-1,0))
                if not bigPos in self.charactersByTile:
                    self.charactersByTile[bigPos] = []

                self.charactersByTile[bigPos].append(char)
        elif direction == "south":
            if char.xPosition % 15 == 0 or char.xPosition % 15 == 14:
                return
            if char.yPosition % 15 == 13:
                if char.xPosition % 15 < 7:
                    direction = "east"
                    char.container.addAnimation(char.getPosition(offset=(1,1,0)),"charsequence",1,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##"),None]})
                elif char.xPosition % 15 > 7:
                    direction = "west"
                    char.container.addAnimation(char.getPosition(offset=(-1,1,0)),"charsequence",1,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##"),None]})
                else:
                    if char.yPosition == 15 * 14 - 2 and 1 == 0:
                        return
                    else:
                        # char.stasis = True
                        char.runCommandString("ss")
                        char.container.addAnimation(char.getPosition(offset=(0,2,0)),"charsequence",0,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##")]})
                        pass
                char.addMessage("a force field pushes you")
                char.container.addAnimation(char.getPosition(offset=(0,1,0)),"charsequence",0,{"chars":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "##")]})
            if char.yPosition % 15 == 0:
                char.changed("changedTile")
                self.removeItems(self.getItemByPosition((char.xPosition,char.yPosition+1,char.zPosition)))

            if char.yPosition % 15 == 14:
                oldBigPos = char.getBigPosition()
                if char in self.charactersByTile[oldBigPos]:
                    self.charactersByTile[oldBigPos].remove(char)
                bigPos = char.getBigPosition(offset=(0,1,0))
                if not bigPos in self.charactersByTile:
                    self.charactersByTile[bigPos] = []
                self.charactersByTile[bigPos].append(char)

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
        roomCandidates = char.terrain.roomByCoordinates.get((bigX, bigY),[])

        # check if character has entered a room
        hadRoomInteraction = False
        for room in roomCandidates:
            # check north
            if direction == "north":
                # check if the character crossed the edge of the room
                if room.yPosition * 15 + room.offsetY + room.sizeY == char.yPosition and (
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
                if room.yPosition * 15 + room.offsetY == char.yPosition + 1 and (
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
                if room.xPosition * 15 + room.offsetX == char.xPosition + 1 and (
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
                if room.xPosition * 15 + room.offsetX + room.sizeX == char.xPosition and (
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
                if item and not char.getItemWalkable(item):
                    # print some info
                    char.addMessage("You cannot walk there")
                    # char.addMessage("press "+commandChars.activate+" to apply")
                    # if noAdvanceGame == False:
                    #    header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))

                    # remember the item for interaction and abort
                    foundItem = item

                if item.isStepOnActive:
                    stepOnActiveItems.append(item)
            if not foundItem and len(foundItems) >= 15:
                char.addMessage("the floor is too full to walk there")
                # char.addMessage("press "+commandChars.activate+" to apply")
                # if noAdvanceGame == False:
                #    header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))

                # remember the item for interaction and abort
                foundItem = foundItems[0]

            if foundItem:
                foundItem = foundItems[0]

            for other in self.charactersByTile.get((bigX, bigY, 0),[]):
                if other == char:
                    continue

                if destCoord != other.getPosition():
                    continue

                if char.faction == "player" and other.faction == "player":
                    continue

                if char.faction.startswith("city") and char.faction == other.faction:
                    continue

                if char.faction == other.faction:
                    continue

                char.messages.append("*thump*")
                char.collidedWith(other,actor=char)
                other.collidedWith(char,actor=char)
                return

            # move the character
            if not foundItem:

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

                    char.addMessage(f"you moved from terrain {pos[0]}/{pos[1]} to terrain {pos[0]}/{pos[1]-1}")

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

                    char.addMessage(f"you moved from terrain {pos[0]}/{pos[1]} to terrain {pos[0]}/{pos[1]+1}")

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

                    char.addMessage(f"you moved from terrain {pos[0]}/{pos[1]} to terrain {pos[0]-1}/{pos[1]}")

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

                    char.addMessage(f"you moved from terrain {pos[0]}/{pos[1]} to terrain {pos[0]+1}/{pos[1]}")

                    self.removeCharacter(char)
                    newTerrain.addCharacter(char,2,char.yPosition)

                    if char == src.gamestate.gamestate.mainChar:
                        src.gamestate.gamestate.terrain = newTerrain

                char.changed("moved", (char, direction))
                char.timeTaken += char.movementSpeed
                for item in stepOnActiveItems:
                    item.doStepOnAction(char)

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

    def getPath(self,startPos,targetPos,localRandom=None,tryHard=False,character=None):
        if not localRandom:
            localRandom = random

        targetPos[2]
        startPos[2]

        if startPos == targetPos:
            return []

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

            if character:
                for offset in goodOffsets[:]:
                    foundEnemy = False
                    newPos = (pos[0]+offset[0],pos[1]+offset[1],pos[2])
                    for otherCharacter in self.charactersByTile.get(newPos,[]):
                        if otherCharacter.faction == character.faction:
                            continue
                        foundEnemy = True
                        break
                    if foundEnemy:
                        goodOffsets.remove(offset)
                        badOffsets.append(offset)

                for offset in neutralOffsets[:]:
                    foundEnemy = False
                    newPos = (pos[0]+offset[0],pos[1]+offset[1],pos[2])
                    for otherCharacter in self.charactersByTile.get(newPos,[]):
                        if otherCharacter.faction == character.faction:
                            continue
                        foundEnemy = True
                        break
                    if foundEnemy:
                        neutralOffsets.remove(offset)
                        badOffsets.append(offset)

            #localRandom.shuffle(goodOffsets)
            #localRandom.shuffle(neutralOffsets)
            #localRandom.shuffle(badOffsets)
            offsets = badOffsets+neutralOffsets+goodOffsets

            while offsets:
                offset = offsets.pop()
                newPos = (pos[0]+offset[0],pos[1]+offset[1],pos[2])

                if newPos[0] > 13 or newPos[1] > 13 or newPos[0] < 1 or newPos[1] < 1:
                    continue

                if costMap.get(newPos) != None:
                    continue

                if newPos != targetPos and newPos in self.scrapFields:
                    continue
                items = self.getItemByPosition((newPos[0]*15+7,newPos[1]*15+7,0))
                if newPos != targetPos and items and items[0].type == "RoomBuilder":
                    continue

                passable = False

                oldRoom = self.getRoomByPosition(pos)
                if oldRoom:
                    oldRoom = oldRoom[0]

                newRoom = self.getRoomByPosition(newPos)
                if newRoom:
                    newRoom = newRoom[0]

                if offset == (0,+1) and (not newRoom or newRoom.getPositionWalkable((6,0,0),character=character)) and (not oldRoom or oldRoom.getPositionWalkable((6,12,0),character=character)):
                    passable = True
                if offset == (0,-1) and (not newRoom or newRoom.getPositionWalkable((6,12,0),character=character)) and (not oldRoom or oldRoom.getPositionWalkable((6,0,0 ),character=character)):
                    passable = True
                if offset == (+1,0) and (not newRoom or newRoom.getPositionWalkable((0,6,0),character=character)) and (not oldRoom or oldRoom.getPositionWalkable((12,6,0),character=character)):
                    passable = True
                if offset == (-1,0) and (not newRoom or newRoom.getPositionWalkable((12,6,0),character=character)) and (not oldRoom or oldRoom.getPositionWalkable((0,6,0 ),character=character)):
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

    def getPathCommandTile(self,tilePos,startPos,targetPos,tryHard=False,avoidItems=None,localRandom=None,ignoreEndBlocked=None,character=None,clearing=False):
        path = self.getPathTile_test(tilePos,startPos,targetPos,tryHard,avoidItems,localRandom,ignoreEndBlocked=ignoreEndBlocked,character=character,clearing=clearing)
        #path = self.getPathTile(tilePos,startPos,targetPos,tryHard,avoidItems,localRandom,ignoreEndBlocked=ignoreEndBlocked,character=character)

        command = ""
        movementMap = {(1,0):"d",(-1,0):"a",(0,1):"s",(0,-1):"w"}
        if path:
            pos = list(character.getPosition())
            for offset in path:
                pos[0] += offset[0]
                pos[1] += offset[1]

                items = self.getItemByPosition(tuple(pos))
                if items and items[0].type == "Bush":
                    command += "J"+movementMap[offset]

                command += movementMap[offset]
        return (command,path)

    def isPathSane(self,character):
        if not self.path:
            return False

        pos = list(character.getPosition())
        for step in self.path:
            pos[0] += step[0]
            pos[1] += step[1]

            if tuple(pos) == self.targetPosition:
                return True

        return False

    def getPathTile_test(self,tilePos,startPos,targetPos,tryHard=False,avoidItems=None,localRandom=None,ignoreEndBlocked=None,character=None,clearing=False):
        """
        path = self.pathCache.get((tilePos,startPos,targetPos))
        if path:
            pos = list(startPos)
            for step in path:
                pos[0] += step[0]
                pos[1] += step[1]

                if not self.getPositionWalkable((pos[0]+15*tilePos[0],pos[1]+15*tilePos[1],0),character=character):
                    path = []
                    del self.pathCache[(tilePos,startPos,targetPos)]
                    break
            if path:
                return path[:]
        """

        pathfinder = self.pathfinderCache.get(tilePos)
        if not pathfinder or ignoreEndBlocked or clearing:
            tileMap = []
            for x in range(15):
                tileMap.append([])
                for y in range(15):
                    if x in (0,14,) or y in (0,14):
                        tileMap[x].append(0)
                    else:
                        tileMap[x].append(5)
            tileMap[0][7] = 1
            tileMap[7][0] = 1
            tileMap[14][7] = 1
            tileMap[7][14] = 1

            for y in range(1,14):
                for x in range(1,14):
                    items = self.getItemByPosition((x+15*tilePos[0],y+15*tilePos[1],0))
                    if items:
                        tileMap[x][y] = 20

            for y in range(1,14):
                for x in range(1,14):
                     if not self.getPositionWalkable((x+15*tilePos[0],y+15*tilePos[1],0),character=character):
                        tileMap[x][y] = 0
                        if clearing:
                            tileMap[x][y] = 100

            for y in range(1,14):
                for x in range(1,14):
                    items = self.getItemByPosition((x+15*tilePos[0],y+15*tilePos[1],0))
                    if items and items[0].type == "Bush":
                        tileMap[x][y] = 127
            if ignoreEndBlocked or clearing:
                tileMap[targetPos[0]][targetPos[1]] = 1

            cost = np.array(tileMap, dtype=np.int8)
            tcod.path.AStar(cost,diagonal = 0)
            pathfinder = tcod.path.AStar(cost,diagonal = 0)
        path = pathfinder.get_path(startPos[0],startPos[1],targetPos[0],targetPos[1])

        if not ignoreEndBlocked:
            self.pathfinderCache[tilePos] = pathfinder

        moves = []
        lastStep = startPos
        for step in path:
            moves.append((step[0]-lastStep[0],step[1]-lastStep[1]))
            lastStep = step

        """
        self.pathCache[(tilePos,startPos,targetPos)] = moves[:]
        """

        return moves

    def getPathTile(self,tilePos,startPos,targetPos,tryHard=False,avoidItems=None,localRandom=None,ignoreEndBlocked=None,character=None):
        """
        path = self.pathCache.get((tilePos,startPos,targetPos))
        if path:
            pos = list(startPos)
            for step in path:
                pos[0] += step[0]
                pos[1] += step[1]

                if not self.getPositionWalkable((pos[0]+15*tilePos[0],pos[1]+15*tilePos[1],0),character=character):
                    path = []
                    del self.pathCache[(tilePos,startPos,targetPos)]
                    break
            if path:
                return path[:]
        """

        tileMap = []
        for x in range(15):
            tileMap.append([])
            for y in range(15):
                if x in (0,14,) or y in (0,14):
                    tileMap[x].append(0)
                else:
                    tileMap[x].append(5)
        tileMap[0][7] = 1
        tileMap[7][0] = 1
        tileMap[14][7] = 1
        tileMap[7][14] = 1

        for y in range(1,14):
            for x in range(1,14):
                items = self.getItemByPosition((x+15*tilePos[0],y+15*tilePos[1],0))
                if items:
                    tileMap[x][y] = 20

        for y in range(1,14):
            for x in range(1,14):
                 if not self.getPositionWalkable((x+15*tilePos[0],y+15*tilePos[1],0),character=character):
                    tileMap[x][y] = 0

        for y in range(1,14):
            for x in range(1,14):
                items = self.getItemByPosition((x+15*tilePos[0],y+15*tilePos[1],0))
                if items and items[0].type == "Bush":
                    tileMap[x][y] = 127

        cost = np.array(tileMap, dtype=np.int8)
        tcod.path.AStar(cost,diagonal = 0)
        pathfinder = tcod.path.AStar(cost,diagonal = 0)
        path = pathfinder.get_path(startPos[0],startPos[1],targetPos[0],targetPos[1])

        moves = []
        lastStep = startPos
        for step in path:
            moves.append((step[0]-lastStep[0],step[1]-lastStep[1]))
            lastStep = step

        """
        self.pathCache[(tilePos,startPos,targetPos)] = moves[:]
        """

        return moves

    def getPathTile_old(self,tilePos,startPos,targetPos,tryHard=False,avoidItems=None,localRandom=None,ignoreEndBlocked=None,character=None):

        path = self.pathCache.get((tilePos,startPos,targetPos))
        if path:
            return path

        if not avoidItems:
            avoidItems = []
        if not localRandom:
            localRandom = random

        costMap = {startPos:0}
        lastPos = startPos
        toCheck = []
        nextPos = startPos
        paths = {startPos:[]}
        blockedPositions = set()

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

            #localRandom.shuffle(goodOffsets)
            #localRandom.shuffle(neutralOffsets)
            #localRandom.shuffle(badOffsets)
            offsets = badOffsets+neutralOffsets+goodOffsets

            while offsets:
                offset = offsets.pop()
                newPos = (pos[0]+offset[0],pos[1]+offset[1],pos[2])

                if newPos[0] > 13 or newPos[1] > 13 or newPos[0] < 1 or newPos[1] < 1:
                    continue

                if costMap.get(newPos) != None:
                    continue

                if newPos in blockedPositions and (not ignoreEndBlocked or newPos != targetPos):
                    continue

                if not self.getPositionWalkable((newPos[0]+tilePos[0]*15,newPos[1]+tilePos[1]*15,newPos[2]+tilePos[2]*15),character):
                    blockedPositions.add(newPos)
                    if (not ignoreEndBlocked or newPos != targetPos):
                        continue

                if not tryHard:
                    if character and character.stepsOnMines == False:
                        items = self.getItemByPosition((newPos[0]+tilePos[0]*15,newPos[1]+tilePos[1]*15,newPos[2]+tilePos[2]*15))
                        if items and items[0].type == "LandMine":
                            blockedPositions.add(newPos)
                            continue


                costMap[newPos] = currentCost+1
                paths[newPos] = paths[pos]+[offset]

                if not nextPos:
                    nextPos = newPos
                else:
                    toCheck.append(newPos)

            if nextPos == targetPos:
                break

        self.pathCache[(tilePos,startPos,targetPos)] = paths.get(targetPos)

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

        bigPos = character.getBigPosition()
        if not bigPos in self.charactersByTile:
            self.charactersByTile[bigPos] = []
        self.charactersByTile[bigPos].append(character)

        character.changed()
        self.changed("entered terrain", character)

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

        if item.xPosition:
            bigPos = (item.xPosition//15,item.yPosition//15,item.zPosition//15)
            if bigPos in self.pathfinderCache:
                del self.pathfinderCache[bigPos]

            self.itemsByBigCoordinate[bigPos].remove(item)

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

            bigPos = (position[0]//15,position[1]//15,position[2]//15)
            if bigPos in self.pathfinderCache:
                del self.pathfinderCache[bigPos]

            if bigPos in self.itemsByBigCoordinate:
                self.itemsByBigCoordinate[bigPos].append(item)
            else:
                self.itemsByBigCoordinate[bigPos] = [item]

            if position in self.itemsByCoordinate:
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
            for _i in range(coordinateOffset[0]-size[0]):
                line = []
                for __j in range(size[1]):
                    line.append(src.canvas.displayChars.void)

        for _i in range(250):
            line = []

            if coordinateOffset[1] < 0:
                for _j in range(-coordinateOffset[1]):
                    line.append(src.canvas.displayChars.void)

            for _j in range(250):
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

    def getEnemiesOnTile(self,character,pos=None):
        if not pos:
            pos = character.getBigPosition()

        if pos == (0,0,0):
            return []

        out = []
        otherChars = self.charactersByTile.get(pos,[])
        for otherChar in otherChars:
            if character == otherChar:
               continue
            if character.faction == otherChar.faction:
               continue
            if otherChar.dead:
               continue
            if pos != otherChar.getBigPosition():
               continue
            out.append(otherChar)

        for room in self.getRoomByPosition(pos):
            for character in room.characters:
                if character == otherChar:
                   continue
                if character.faction == otherChar.faction:
                   continue
                if otherChar.dead:
                   continue
                if pos != otherChar.getBigPosition():
                   continue
                out.append(otherChar)

        return out

    def render(self,size=None,coordinateOffset=(0,0)):
        """
        render the terrain and its contents

        Returns:
            the rendered terrain
        """

        if not self.lastRender:
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
            for x in range(225):
                if (x < coordinateOffset[1] or x > coordinateOffset[1]+size[1]):
                    continue

                for y in range(16):
                    if not (y < coordinateOffset[0] or y > coordinateOffset[0]+size[0]):
                        chars[y-coordinateOffset[0]][x-coordinateOffset[1]] = src.canvas.displayChars.forceField
                    if not (y+14*15-1 < coordinateOffset[0] or y+14*15-1 > coordinateOffset[0]+size[0]):
                        chars[y-coordinateOffset[0] + 14 * 15 - 1][x-coordinateOffset[1]] = src.canvas.displayChars.forceField

            for y in range(225):
                if (y < coordinateOffset[0] or y > coordinateOffset[0]+size[0]):
                    continue

                for x in range(16):
                    if not (x < coordinateOffset[1] or x > coordinateOffset[1]+size[1]):
                        try:
                            chars[y-coordinateOffset[0]][x-coordinateOffset[1]] = src.canvas.displayChars.forceField
                        except:
                            raise Exception(f"{coordinateOffset[0]} {coordinateOffset[1]}")
                    if not (x + 14 * 15 - 1 < coordinateOffset[1] or x + 14 * 15 - 1 > coordinateOffset[1]+size[1]):
                        chars[y-coordinateOffset[0]][x-coordinateOffset[1] + 14 * 15 - 1] = src.canvas.displayChars.forceField

            # show/hide rooms
            for room in self.rooms:
                if src.gamestate.gamestate.mainChar.room == room:
                    room.hidden = False
                else:
                    if not mapHidden and room.open and room.hidden:
                        room.hidden = False
                    else:
                        room.hidden = True

            for bigX in range(14):
                if bigX*15 < coordinateOffset[1]-15 or bigX*15 > coordinateOffset[1]+size[1]+15:
                    continue

                for bigY in range(14):
                    if bigY*15 < coordinateOffset[0]-15 or bigY*15 > coordinateOffset[0]+size[0]+15:
                        continue

                    for x in range(15):
                        for y in range(15):

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
                    if item.zPosition != src.gamestate.gamestate.mainChar.zPosition:
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

            #for quest in src.gamestate.gamestate.mainChar.getActiveQuests():
            quest = src.gamestate.gamestate.mainChar.getActiveQuest()
            if quest:
                for marker in quest.getQuestMarkersSmall(src.gamestate.gamestate.mainChar,renderForTile=True):
                    pos = marker[0]
                    pos = (pos[0]-coordinateOffset[1],pos[1]-coordinateOffset[0])
                    if pos[0] < 0:
                        continue
                    if pos[1] < 0:
                        continue
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
            #self.lastRender = copy.deepcopy(chars)
        else:
            chars = copy.deepcopy(self.lastRender)

        usedAnimationSlots = set()
        for animation in self.animations[:]:
            (pos,animationType,duration,extraInfo) = animation
            pos = (pos[0]-coordinateOffset[1],pos[1]-coordinateOffset[0])
            if pos[0] < 0 or pos[1] < 0 or pos[0] > size[0] or pos[1] > size[1]:
                self.animations.remove(animation)
                continue

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
                chars[pos[1]][pos[0]] = display

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
                chars[pos[1]][pos[0]] = display

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
                chars[pos[1]][pos[0]] = display
                animation[2] -= 1

                if duration < 1:
                    self.animations.remove(animation)
            elif animationType in ("scrapChange",):
                letters = ["*","+","#",";","%"]
                character = random.choice(letters)+random.choice(letters)
                display = character
                display = (src.interaction.urwid.AttrSpec("#740","#000"),display)

                chars[pos[1]][pos[0]] = display
                animation[2] -= 1

                if duration < 1:
                    self.animations.remove(animation)
            elif animationType in ("explosion",):
                display = "##"
                display = (src.interaction.urwid.AttrSpec(["#fa0","#f00"][duration%2],["#f00","#fa0"][duration%2],),display)

                chars[pos[1]][pos[0]] = display
                animation[2] -= 1

                if duration < 1:
                    self.animations.remove(animation)
            elif animationType in ("showchar",):
                display = extraInfo["char"]

                if display:
                    chars[pos[1]][pos[0]] = display
                animation[2] -= 1

                if duration < 1:
                    self.animations.remove(animation)
            elif animationType in ("charsequence",):
                display = extraInfo["chars"][len(extraInfo["chars"])-1-duration]

                try:
                    if display:
                        chars[pos[1]][pos[0]] = display
                except:
                    pass
                animation[2] -= 1

                if duration < 1:
                    self.animations.remove(animation)
            else:
                display = "??"
                chars[pos[1]][pos[0]] = display
                #self.animations.remove(animation)


        return chars

    def renderTiles(self):
        chars = []
        for y in range(15):
            chars.append([])
            for x in range(15):
                if y == 0 or x == 0 or y == 14 or x == 14:
                    chars[y].append(src.canvas.displayChars.forceField)
                else:
                    chars[y].append(src.canvas.displayChars.dirt)

        for room in self.rooms:
            color = "#334"
            chars[room.yPosition][room.xPosition] = room.displayChar

        homePos = (src.gamestate.gamestate.mainChar.registers.get("HOMEx"),src.gamestate.gamestate.mainChar.registers.get("HOMEy"))
        homePosTerrain = (src.gamestate.gamestate.mainChar.registers.get("HOMETx"),src.gamestate.gamestate.mainChar.registers.get("HOMETy"),0)
        if homePosTerrain == src.gamestate.gamestate.mainChar.getTerrainPosition() and homePos[0] and homePos[1]:
            chars[homePos[1]][homePos[0]] = "HH"

        for scrapField in self.scrapFields:
            chars[scrapField[1]][scrapField[0]] = "ss"

        for forest in self.forests:
            chars[forest[1]][forest[0]] = "ff"

        for collectionSpot in self.collectionSpots:
            chars[collectionSpot[1]][collectionSpot[0]] = "cs"

        for (k,v) in self.minimapOverride.items():
            chars[k[1]][k[0]] = v

        for x in range(1,14):
            for y in range(1,14):
                foundEnemy = False
                otherCharacters = self.charactersByTile.get((x,y,0),[])
                for otherCharacter in otherCharacters:
                    if otherCharacter.faction == src.gamestate.gamestate.mainChar.faction:
                        continue
                    foundEnemy = True
                if foundEnemy:
                    pos = (x,y)
                    try:
                        display = chars[pos[1]][pos[0]]
                    except:
                        continue

                    if isinstance(display,int):
                        display = src.canvas.displayChars.indexedMapping[display]
                    if isinstance(display,str):
                        display = (src.interaction.urwid.AttrSpec("#fff","black"),display)

                    color = "#722"
                    if hasattr(display[0],"fg"):
                        display = (src.interaction.urwid.AttrSpec(display[0].fg,color),display[1])
                    else:
                        display = (src.interaction.urwid.AttrSpec(display[0].foreground,color),display[1])

                    chars[pos[1]][pos[0]] = display

        quest = src.gamestate.gamestate.mainChar.getActiveQuest()
        if quest:
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

        for subordinate in src.gamestate.gamestate.mainChar.subordinates:
            if subordinate.getTerrain() != self:
                continue
            displayChar = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@s")
            pos = subordinate.getBigPosition()
            chars[pos[1]][pos[0]] = displayChar

        displayChar = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@ ")
        if isinstance(src.gamestate.gamestate.mainChar.container,src.rooms.Room):
            chars[src.gamestate.gamestate.mainChar.container.yPosition][src.gamestate.gamestate.mainChar.container.xPosition] = displayChar
        else:
            chars[src.gamestate.gamestate.mainChar.yPosition//15][src.gamestate.gamestate.mainChar.xPosition//15] = displayChar

        if src.gamestate.gamestate.mainChar.macroState.get("submenue"):
            for marker in src.gamestate.gamestate.mainChar.macroState["submenue"].getQuestMarkersTile(src.gamestate.gamestate.mainChar):
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
                ) and (
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
                ) and (
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
                ) and (
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
                ) and (
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
                logger.debug("invalid movement direction: %s", direction)

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
                    0
                ) in self.itemsByCoordinate:
                    movementBlock.update(
                        self.itemsByCoordinate[
                            (posX, room.yPosition * 15 + room.offsetY - 1,0)
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
                    0
                ) in self.itemsByCoordinate:
                    movementBlock.update(
                        self.itemsByCoordinate[
                            (posX, room.yPosition * 15 + room.offsetY + room.sizeY,0)
                        ]
                    )
        elif direction == "west":
            posY = room.yPosition * 15 + room.offsetY - 1
            maxY = room.yPosition * 15 + room.offsetY + room.sizeY - 1
            while posY < maxY:
                pos = ( room.xPosition * 15 + room.offsetX - 1, posY, 0)
                posY += 1
                if self.itemsByCoordinate.get(pos,[]):
                    movementBlock.update(
                        self.itemsByCoordinate[pos]
                    )
        elif direction == "east":
            posY = room.yPosition * 15 + room.offsetY - 1
            maxY = room.yPosition * 15 + room.offsetY + room.sizeY - 1
            while posY < maxY:
                posY += 1
                if (
                    room.xPosition * 15 + room.offsetX + room.sizeX,
                    posY,
                    0
                ) in self.itemsByCoordinate:
                    movementBlock.update(
                        self.itemsByCoordinate[
                            (room.xPosition * 15 + room.offsetX + room.sizeX, posY,0)
                        ]
                    )
        else:
            logger.debug("invalid movement direction: %s", direction)

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
        if oldPosition in self.roomByCoordinates and room in self.roomByCoordinates[oldPosition]:
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

        while start != end:
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
            displayChar = f"{src.gamestate.gamestate.mainChar.zPosition}"
        if src.gamestate.gamestate.mainChar.zPosition > 0:
            displayChar = f"+{src.gamestate.gamestate.mainChar.zPosition}"

        chars = []
        for _i in range(-coordinateOffset[0]):
            line = []
            chars.append(line)

        for i in range(15*15):
            line = []

            if i < coordinateOffset[0] or i > coordinateOffset[0]+size[0]:
                continue

            for _j in range(-coordinateOffset[1]):
                line.append(src.canvas.displayChars.void)

            for j in range(15*15):

                if coordinateOffset: # game runs horrible without this flag
                    if j < coordinateOffset[1] or j > coordinateOffset[1]+size[1]:
                        continue

                if not self.hidden:
                    display = displayChar
                    #display = src.interaction.ActionMeta(payload={"container":self,"method":"handleFloorClick","params": {"pos": (j,i)}},content=display)
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


        self.isRoom = False
        super().__init__(
            seed=seed,
            noContent=noContent,
        )

        if not noContent:
            # add a few items scattered around
            dekoItems = []
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
                        dekoItems.append((item, (x, y, 0)))
            self.addItems(dekoItems)

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
        layout = """\
_____________
_____________
_____________
_____________
_____________
_____________
_____________
_____________
_____._______
____C._______
_____________
_____________
_____________
_____________
_____________"""

        super().__init__(
            seed=seed, noContent=noContent
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
                    while position is None or position in excludes:
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
                        if counter % (5 * 3) != 0:
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
            for _i in range(coordinateOffset[0]-size[0]):
                line = []
                for j in range(size[1]):
                    if j < coordinateOffset[1] or j > coordinateOffset[1]+size[1]:
                        continue

                    line.append(src.canvas.displayChars.void)

        for _i in range(250):
            line = []

            if coordinateOffset[1] < 0:
                for _j in range(-coordinateOffset[1]):
                    line.append(src.canvas.displayChars.void)

            for j in range(250):
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

        super().__init__(
            seed=seed, noContent=noContent
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
        for _i in range(1, 30):
            self.itemPool.append([src.items.itemMap["Sheet"](),[0,0,0]])
            case = src.items.itemMap["Case"]()
            case.bolted = False
            self.itemPool.append([case,[0,0,0]])
            self.itemPool.append([src.items.itemMap["Vial"](),[0,0,0]])
            corpse = src.items.itemMap["Corpse"]()
            corpse.charges = random.randint(100, 300)
            self.itemPool.append([corpse,[0,0,0]])
        for _i in range(1, 200):
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

        self.doSandStorm()
        self.randomizeHeatmap()

    def randomizeHeatmap(self):
        """
        make random tiles dispense heat damage
        """

        # save heatmap for tiles
        import random

        self.heatmap = []
        for x in range(15):
            self.heatmap.append([])
            for y in range(15):
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
            for _i in range(coordinateOffset[0]-size[0]):
                line = []
                for _j in range(size[1]):
                    line.append(src.canvas.displayChars.void)

        for i in range(15*15):
            line = []
            if i < coordinateOffset[0] or i > coordinateOffset[0]+size[0]:
                continue

            if coordinateOffset[1] < 0:
                for _j in range(-coordinateOffset[1]):
                    line.append(src.canvas.displayChars.void)

            for j in range(15*15):
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
        for i in range(250):
            line = []
            for j in range(250):
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

        for _i in range(10):
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

        for _i in range(10):
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
        cityBuilder.setConnectionsFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,7),"selection":"w"},noFurtherInteraction=True)
        cityBuilder.setConnectionsFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,7),"selection":"a"},noFurtherInteraction=True)
        cityBuilder.setConnectionsFromMap({"character":src.gamestate.gamestate.mainChar,"coordinate":(7,7),"selection":"d"},noFurtherInteraction=True)
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
            for _i in range(4):
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

            for _i in range(level):
                enemy = src.characters.Monster()
                room.addCharacter(enemy,random.randint(2,13),random.randint(2,13))
                enemy.macroState["macros"]["g"] = ["g","g","_","g"]
                enemy.health = 100+3*level
                enemy.baseDamage = 10+level
                enemy.runCommandString("_g")

            for _i in range(2**level):
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

        super().__init__(
            seed=seed, noContent=noContent
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
        self.addRooms([self.wakeUpRoom])

        super().__init__(
            seed=seed, noContent=noContent
        )

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

# mapping from strings to all items
# should be extendable
terrainMap = {
    "Nothingness": Nothingness,
    "GameplayTest": GameplayTest,
    "ScrapField": ScrapField,
    "Desert": Desert,
    "Ruin": Ruin,
    "Base": Base,
    "Base2": Base2,
}
