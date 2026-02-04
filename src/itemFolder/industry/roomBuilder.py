import src

import random

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
        self.description = "Creates rooms from basic items."
        self.usageInfo = """
Place Walls and and Doors around the room builder and activate the room builder to create a room.

The room has to be a rectangle.
"""

    def get_missing_items(self):
        """
        get information on what items still need to be placed
        """
        # set up helper variables
        big_pos = self.getBigPosition()
        terrain = self.getTerrain()
        if terrain == None:
            return None

        # get missing items
        missing_items = []
        for x in range(1,14):
            for y in range(1,14):
                if x not in (1,13,) and y not in (1,13,):
                    continue
                item_type = "Wall"
                if x == 7 or y == 7:
                    item_type = "Door"
                pos = (big_pos[0]*15+x,big_pos[1]*15+y,0)
                found_items = terrain.getItemByPosition(pos)
                if len(found_items) == 1 and found_items[0].type == item_type:
                    continue
                missing_items.append((item_type,pos))
        return missing_items

    def apply(self, character):
        """
        handle a character trying to build a room
        by trying to build a room

        Parameters:
            character: the character trying to use this item
        """

        if self.xPosition is None or self.container is None or self.container.isRoom:
            character.addMessage("this machine can only be used in open terrain")
            return

        if (self.xPosition%15, self.yPosition%15, 0) != (7,7,0):
            text = "the room builder needs to be placed in the middle of the tile.\n\n required position: (7,7,0)"
            character.showTextMenu(text)
            character.addMessage(text)
            return

        # abort if items are missing
        missing_items = self.get_missing_items()
        if missing_items:

            # set up basic text
            text = ["Could not build room, there are items missing:\n\n"]

            # add graphical representation to text
            map_view = []
            base_position = (self.xPosition//15*15,self.yPosition//15*15,0)
            for y in range(1,14):
                for x in range(1,14):
                    display = "  "
                    color = "#666"
                    if y in (1,13) or x in (1,13):
                        if y == 7 or x == 7:
                            display = "[]"
                            items = self.container.getItemByPosition((x+base_position[0],y+base_position[1],0))
                            if (not len(items) == 1) or (not items[0].type == "Door"):
                                color = "#e22"
                        else:
                            display = "XX"
                            items = self.container.getItemByPosition((x+base_position[0],y+base_position[1],0))
                            if (not len(items) == 1) or (not items[0].type == "Wall"):
                                color = "#e22"
                    elif (x,y) == (7,7):
                        display = "RB"
                    map_view.append((src.interaction.urwid.AttrSpec(color,"#000"), display))
                map_view.append("\n")
            text.append(map_view)
            text.append("\n")

            # add list to text
            for entry in missing_items:
                text.append(f"{entry[0]}: ")
                text.append(f"({entry[1][0]%15}, {entry[1][1]%15}, {entry[1][2]%15})")
                text.append(f"\n")

            # show text to the user
            character.showTextMenu(text)
            return

        # find room edges
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

        # check room dimensions
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

        # check if there are items where the room outlines are
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

        # actually spawn the new room
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

        # get helper info
        terrain = character.getTerrain()
        bigPos = character.getBigPosition()

        # check if there is a neigbouring trap room
        has_connected_traproom_neighbour = False
        traproomOffset = None
        connected_neigbour_traproom = None
        neigbour_traprooms = []
        offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
        for offset in offsets:
            rooms = terrain.getRoomByPosition((bigPos[0]+offset[0],bigPos[1]+offset[1],0))
            if not rooms:
                continue
            if not rooms[0].tag or not (rooms[0].tag.lower() in ("traproom", "entryroom","trapsupport")):
                continue

            neigbour_traprooms.append(rooms[0])

            if offset == (1,0,0):
                if rooms[0].getPositionWalkable((0,6,0)):
                    has_connected_traproom_neighbour = True
            if offset == (-1,0,0):
                if rooms[0].getPositionWalkable((12,6,0)):
                    has_connected_traproom_neighbour = True
            if offset == (0,1,0):
                if rooms[0].getPositionWalkable((6,0,0)):
                    has_connected_traproom_neighbour = True
            if offset == (0,-1,0):
                if rooms[0].getPositionWalkable((6,12,0)):
                    has_connected_traproom_neighbour = True

            if has_connected_traproom_neighbour:
                traproomOffset = offset
                connected_neigbour_traproom = rooms[0]
                break

        if has_connected_traproom_neighbour:
            # open new trap room doors
            offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
            for offset in offsets:
                if offset != traproomOffset:
                    rooms = terrain.getRoomByPosition((bigPos[0]+offset[0],bigPos[1]+offset[1],0))
                    if rooms:
                        continue

                if offset == (1,0,0):
                    for item in room.getItemByPosition((12,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                if offset == (-1,0,0):
                    for item in room.getItemByPosition((0,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                if offset == (0,1,0):
                    for item in room.getItemByPosition((6,12,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                if offset == (0,-1,0):
                    for item in room.getItemByPosition((6,0,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True

            # close old traprooms doors
            neigbourTraproomPos = connected_neigbour_traproom.getPosition()
            offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
            for offset in offsets:
                rooms = terrain.getRoomByPosition((neigbourTraproomPos[0]+offset[0],neigbourTraproomPos[1]+offset[1],0))
                if rooms:
                    continue

                if offset == (-traproomOffset[0],-traproomOffset[1],-traproomOffset[2]):
                    continue

                if offset == (1,0,0):
                    for item in connected_neigbour_traproom.getItemByPosition((12,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = False
                if offset == (-1,0,0):
                    for item in connected_neigbour_traproom.getItemByPosition((0,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = False
                if offset == (0,1,0):
                    for item in connected_neigbour_traproom.getItemByPosition((6,12,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = False
                if offset == (0,-1,0):
                    for item in connected_neigbour_traproom.getItemByPosition((6,0,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = False

            # set new room as entry room
            room.tag = "entryRoom"

            # add alarm bell
            alarmBell = src.items.itemMap["AlarmBell"]()
            alarmBell.bolted = True
            room.addItem(alarmBell,(3,3,0))
            room.alarm = True


        if not has_connected_traproom_neighbour:
            if not neigbour_traprooms:
                westNeighbours = terrain.getRoomByPosition((bigPos[0]-1,bigPos[1],0))
                if westNeighbours and not (westNeighbours[0].tag and (westNeighbours[0].tag.lower() in ("traproom", "entryroom","trapsupport"))):
                    for item in room.getItemByPosition((0,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                    for item in westNeighbours[0].getItemByPosition((12,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                eastNeighbours = terrain.getRoomByPosition((bigPos[0]+1,bigPos[1],0))
                if eastNeighbours and not (eastNeighbours[0].tag and (eastNeighbours[0].tag.lower() in ("traproom", "entryroom","trapsupport"))):
                    for item in room.getItemByPosition((12,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                    for item in eastNeighbours[0].getItemByPosition((0,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                northNeighbours = terrain.getRoomByPosition((bigPos[0],bigPos[1]-1,0))
                if northNeighbours and not (northNeighbours[0].tag and (northNeighbours[0].tag.lower() in ("traproom", "entryroom","trapsupport"))):
                    for item in room.getItemByPosition((6,0,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                    for item in northNeighbours[0].getItemByPosition((6,12,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                southNeighbours = terrain.getRoomByPosition((bigPos[0],bigPos[1]+1,0))
                if southNeighbours and not (southNeighbours[0].tag and (southNeighbours[0].tag.lower() in ("traproom", "entryroom","trapsupport"))):
                    for item in room.getItemByPosition((6,12,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                    for item in southNeighbours[0].getItemByPosition((6,0,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
            else:
                neighbour = random.choice(neigbour_traprooms)
                if neighbour.xPosition < room.xPosition:
                    for item in room.getItemByPosition((0,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                    for item in neighbour.getItemByPosition((12,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                if neighbour.xPosition > room.xPosition:
                    for item in room.getItemByPosition((12,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                    for item in neighbour.getItemByPosition((0,6,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                if neighbour.yPosition < room.yPosition:
                    for item in room.getItemByPosition((6,0,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                    for item in neighbour.getItemByPosition((6,12,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                if neighbour.yPosition > room.yPosition:
                    for item in room.getItemByPosition((6,12,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True
                    for item in neighbour.getItemByPosition((6,0,0)):
                        if item.type != "Door":
                            continue
                        item.walkable = True

                room.tag = "trapSupport"

                # add alarm bell
                alarmBell = src.items.itemMap["AlarmBell"]()
                alarmBell.bolted = True
                room.addItem(alarmBell,(3,3,0))
                room.alarm = True

        # add newly generated room
        oldTerrain.addRooms([room])

        # set up animations
        for character_to_move in self.getTerrain().getCharactersOnTile(self.getBigPosition())[:]:
            xOffset = character_to_move.xPosition - self.xPosition
            yOffset = character_to_move.yPosition - self.yPosition

            oldTerrain.removeCharacter(character_to_move)
            character_to_move.xPosition = roomLeft + xOffset
            character_to_move.yPosition = roomTop + yOffset
            room.addCharacter(character_to_move, roomLeft + xOffset, roomTop + yOffset)

        # move characters into the room
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
