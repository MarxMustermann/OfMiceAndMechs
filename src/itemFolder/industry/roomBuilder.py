import src
import src.rooms


class RoomBuilder(src.items.Item):
    """
    ingame items to build rooms
    """

    type = "RoomBuilder"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.roomBuilder)
        self.name = "RoomBuilder"
        self.description = "The roombuilder creates rooms from basic items."
        self.usageInfo = """
Place Walls and and Doors around the room builder and activate the room builder to create a room.

The room has to be a rectangle.
"""

    def apply(self, character):
        """
        handle a character trying to build a room
        by trying to build a room

        Parameters:
            character: the character trying to use this item
        """

        if self.xPosition is None:
            character.addMessage("this machine can not be used within rooms")
            return

        if self.container is None:
            character.addMessage("this machine can not be used within rooms")
            return

        wallLeft = False
        for offset in range(6, 7):
            pos = (self.xPosition - offset, self.yPosition,0)
            for item in self.container.getItemByPosition(pos):
                if item.type in ("Wall","Door"):
                    wallLeft = item
                    break
            if wallLeft:
                break
        wallRight = False
        for offset in range(6, 7):
            pos = (self.xPosition + offset, self.yPosition,0)
            for item in self.container.getItemByPosition(pos):
                if item.type in ("Wall","Door"):
                    wallRight = item
                    break
            if wallRight:
                break
        wallTop = False
        for offset in range(6, 7):
            pos = (self.xPosition, self.yPosition - offset,0)
            for item in self.container.getItemByPosition(pos):
                if item.type in ("Wall","Door"):
                    wallTop = item
                    break

            if wallTop:
                break
        wallBottom = False
        for offset in range(6, 7):
            pos = (self.xPosition, self.yPosition + offset,0)
            for item in self.container.getItemByPosition(pos):
                if item.type in ("Wall","Door"):
                    wallBottom = item
                    break
            if wallBottom:
                break

        if not (wallLeft and wallRight and wallTop and wallBottom):
            character.addMessage("no boundaries found")
            return

        roomLeft = self.xPosition - wallLeft.xPosition
        roomRight = wallRight.xPosition - self.xPosition
        roomTop = self.yPosition - wallTop.yPosition
        roomBottom = wallBottom.yPosition - self.yPosition

        if roomLeft + roomRight + 1 > 15:
            character.addMessage("room to big")
            return
        if roomTop + roomBottom + 1 > 15:
            character.addMessage("room to big")
            return

        wallMissing = False
        items = []
        specialItems = []
        doorPos = []
        for x in range(-roomLeft, roomRight + 1):
            pos = (self.xPosition + x, self.yPosition - roomTop,0)
            wallFound = None
            for item in self.container.getItemByPosition(pos):
                if item.type in ("Wall","Door"):
                    wallFound = item
                    if item not in items:
                        items.append(item)
                    if item.type in ("Door",) and item not in specialItems:
                        specialItems.append(item)
                    break
            if not wallFound:
                wallMissing = True
                break
        for y in range(-roomTop, roomBottom + 1):
            pos = (self.xPosition - roomLeft, self.yPosition + y,0)
            wallFound = None
            for item in self.container.getItemByPosition(pos):
                if item.type in ("Wall","Door"):
                    wallFound = item
                    if item not in items:
                        items.append(item)
                    if item.type in ("Door",) and item not in specialItems:
                        specialItems.append(item)
                    break
            if not wallFound:
                wallMissing = True
                break
        for y in range(-roomTop, roomBottom + 1):
            pos = (self.xPosition + roomRight, self.yPosition + y,0)
            wallFound = None
            for item in self.container.getItemByPosition(pos):
                if item.type in ("Wall","Door"):
                    wallFound = item
                    if item not in items:
                        items.append(item)
                    if item.type in ("Door",) and item not in specialItems:
                        specialItems.append(item)
                    break
            if not wallFound:
                wallMissing = True
                break
        for x in range(-roomLeft, roomRight + 1):
            pos = (self.xPosition + x, self.yPosition + roomBottom,0)
            wallFound = None
            for item in self.container.getItemByPosition(pos):
                if item.type in ("Wall","Door"):
                    wallFound = item
                    if item not in items:
                        items.append(item)
                    if item.type in ("Door",) and item not in specialItems:
                        specialItems.append(item)
                    break
            if not wallFound:
                wallMissing = True
                break

        if wallMissing:
            character.addMessage("wall missing")
            return

        for item in specialItems:
            for compareItem in specialItems:
                if item == compareItem:
                    continue
                if abs(item.xPosition - compareItem.xPosition) > 1 or (
                    abs(item.xPosition - compareItem.xPosition) == 1
                    and abs(item.yPosition - compareItem.yPosition) > 0
                ):
                    continue
                if abs(item.yPosition - compareItem.yPosition) > 1 or (
                    abs(item.yPosition - compareItem.yPosition) == 1
                    and abs(item.xPosition - compareItem.xPosition) > 0
                ):
                    continue
                character.addMessage("special items to near to each other")
                return

        oldTerrain = self.container
        for item in specialItems:
            if item == self:
                continue

            oldX = item.xPosition
            oldY = item.yPosition
            item.container.removeItem(item)
            item.xPosition = roomLeft + oldX - self.xPosition
            item.yPosition = roomTop + oldY - self.yPosition
            doorPos.append((roomLeft + oldX - self.xPosition,roomTop + oldY - self.yPosition))

        room = src.rooms.EmptyRoom(
            self.xPosition // 15,
            self.yPosition // 15,
            self.xPosition % 15 - roomLeft,
            self.yPosition % 15 - roomTop,
        )
        room.reconfigure(roomLeft + roomRight + 1, roomTop + roomBottom + 1, items,doorPos=doorPos)
        room.timeIndex = src.gamestate.gamestate.tick

        # auto add the correct connections
        ## close all doors
        for item in room.itemsOnFloor:
            if item.type != "Door":
                continue
            item.walkable = False

        terrain = character.getTerrain()
        bigPos = character.getBigPosition()
        westNeighbours = terrain.getRoomByPosition((bigPos[0]-1,bigPos[1],0))
        if westNeighbours:
            for item in room.getItemByPosition((0,6,0)):
                if item.type != "Door":
                    continue
                item.walkable = True
            for item in westNeighbours[0].getItemByPosition((12,6,0)):
                if item.type != "Door":
                    continue
                item.walkable = True
        eastNeighbours = terrain.getRoomByPosition((bigPos[0]+1,bigPos[1],0))
        if eastNeighbours:
            for item in room.getItemByPosition((12,6,0)):
                if item.type != "Door":
                    continue
                item.walkable = True
            for item in eastNeighbours[0].getItemByPosition((0,6,0)):
                if item.type != "Door":
                    continue
                item.walkable = True
        northNeighbours = terrain.getRoomByPosition((bigPos[0],bigPos[1]-1,0))
        if northNeighbours:
            for item in room.getItemByPosition((6,0,0)):
                if item.type != "Door":
                    continue
                item.walkable = True
            for item in northNeighbours[0].getItemByPosition((6,12,0)):
                if item.type != "Door":
                    continue
                item.walkable = True
        southNeighbours = terrain.getRoomByPosition((bigPos[0],bigPos[1]+1,0))
        if southNeighbours:
            for item in room.getItemByPosition((6,12,0)):
                if item.type != "Door":
                    continue
                item.walkable = True
            for item in southNeighbours[0].getItemByPosition((6,0,0)):
                if item.type != "Door":
                    continue
                item.walkable = True

        xOffset = character.xPosition - self.xPosition
        yOffset = character.yPosition - self.yPosition

        oldTerrain.removeCharacter(character)
        oldTerrain.addRooms([room])
        character.xPosition = roomLeft + xOffset
        character.yPosition = roomTop + yOffset
        room.addCharacter(character, roomLeft + xOffset, roomTop + yOffset)

        basePos = character.getBigPosition()
        self.container.addAnimation((basePos[0]*15+7,basePos[1]*15+7,0),"showchar",35,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"RB")})
        self.container.addAnimation((basePos[0]*15+7,basePos[1]*15+7,0),"showchar",3,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"::")})

        ring1 = [(1,0,0),(1,1,0),(1,-1,0),(0,-1,0),(-1,-1,0),(-1,0,0),(-1,1,0),(0,1,0)]
        for pos in ring1:
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",3,{"char":src.canvas.displayChars.dirt})
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"::")})
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",18,{"char":src.canvas.displayChars.floor})

        ring2 = [(2,0,0),(2,1,0),(2,2,0),(1,2,0),(0,2,0),(-1,2,0),(-2,2,0),(-2,1,0),(-2,0,0),(-2,-1,0),(-2,-2,0),(-1,-2,0),(0,-2,0),(1,-2,0),(2,-2,0),(2,-1,0)]
        for pos in ring2:
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",6,{"char":src.canvas.displayChars.dirt})
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"::")})
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",15,{"char":src.canvas.displayChars.floor})

        ring3 = [(3,0,0),(3,1,0),(3,2,0),(3,3,0),(2,3,0),(1,3,0),(0,3,0),(-1,3,0),(-2,3,0),(-3,3,0),(-3,2,0),(-3,1,0),(-3,0,0),(-3,-1,0),(-3,-2,0),(-3,-3,0),(-2,-3,0),(-1,-3,0),(0,-3,0),(1,-3,0),(2,-3,0),(3,-3,0),(3,-2,0),(3,-1,0)]
        for pos in ring3:
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",9,{"char":src.canvas.displayChars.dirt})
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"::")})
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",12,{"char":src.canvas.displayChars.floor})

        ring4 = [(4,0,0),(4,1,0),(4,2,0),(4,3,0),(4,4,0),(3,4,0),(2,4,0),(1,4,0),(0,4,0),(-1,4,0),(-2,4,0),(-3,4,0),(-4,4,0),(-4,3,0),(-4,2,0),(-4,1,0),(-4,0,0),(-4,-1,0),(-4,-2,0),(-4,-3,0),(-4,-4,0),(-3,-4,0),(-2,-4,0),(-1,-4,0),(0,-4,0),(1,-4,0),(2,-4,0),(3,-4,0),(4,-4,0),(4,-3,0),(4,-2,0),(4,-1,0)]
        for pos in ring4:
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",12,{"char":src.canvas.displayChars.dirt})
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"::")})
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",9,{"char":src.canvas.displayChars.floor})

        ring5 = [(5,0,0),(5,1,0),(5,2,0),(5,3,0),(5,4,0),(5,5,0),(4,5,0),(3,5,0),(2,5,0),(1,5,0),(0,5,0),(-1,5,0),(-2,5,0),(-3,5,0),(-4,5,0),(-5,5,0),(-5,4,0),(-5,3,0),(-5,2,0),(-5,1,0),(-5,0,0),(-5,-1,0),(-5,-2,0),(-5,-3,0),(-5,-4,0),(-5,-5,0),(-4,-5,0),(-3,-5,0),(-2,-5,0),(-1,-5,0),(0,-5,0),(1,-5,0),(2,-5,0),(3,-5,0),(4,-5,0),(5,-5,0),(5,-4,0),(5,-3,0),(5,-2,0),(5,-1,0)]
        for pos in ring5:
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",15,{"char":src.canvas.displayChars.dirt})
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"::")})
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",6,{"char":src.canvas.displayChars.floor})

        ring6 = [(6,0,0),(6,1,0),(6,2,0),(6,3,0),(6,4,0),(6,5,0),(6,6,0),(5,6,0),(4,6,0),(3,6,0),(2,6,0),(1,6,0),(0,6,0),(-1,6,0),(-2,6,0),(-3,6,0),(-4,6,0),(-5,6,0),(-6,6,0),(-6,5,0),(-6,4,0),(-6,3,0),(-6,2,0),(-6,1,0),(-6,0,0),(-6,-1,0),(-6,-2,0),(-6,-3,0),(-6,-4,0),(-6,-5,0),(-6,-6,0),(-5,-6,0),(-4,-6,0),(-3,-6,0),(-2,-6,0),(-1,-6,0),(0,-6,0),(1,-6,0),(2,-6,0),(3,-6,0),(4,-6,0),(5,-6,0),(6,-6,0),(6,-5,0),(6,-4,0),(6,-3,0),(6,-2,0),(6,-1,0)]
        for pos in ring6:
            self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",18,{"char":None})
            if pos[0] == 0 or pos[1] == 0:
                #self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",10,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"[]")})
                pass
            else:
                self.container.addAnimation((basePos[0]*15+7+pos[0],basePos[1]*15+7+pos[1],0),"showchar",10,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"XX")})

        terrain = self.container
        for item in self.container.itemsByBigCoordinate.get(self.getBigPosition(),[])[:]:
            terrain.removeItem(item)

        self.xPosition = roomLeft
        self.yPosition = roomTop

        character.changed("built room",{"character":character,"room":room})

src.items.addType(RoomBuilder)
