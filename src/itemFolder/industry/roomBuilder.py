import src

'''
'''
class RoomBuilder(src.items.Item):
    type = "RoomBuilder"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="RoomBuilder",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.roomBuilder,xPosition,yPosition,name=name,creator=creator)

    '''
    map player controls to room movement 
    '''
    def apply(self,character):
        if self.room:
            character.addMessage("this machine can not be used within rooms")
            return

        if self.xPosition == None:
            character.addMessage("this machine can not be used within rooms")
            return

        if self.terrain == None:
            character.addMessage("this machine can not be used within rooms")
            return

        wallLeft = False
        for offset in range(1,15):
            pos = (self.xPosition-offset,self.yPosition)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallLeft = item
                        break
            if wallLeft:
                break
        wallRight = False
        for offset in range(1,15):
            pos = (self.xPosition+offset,self.yPosition)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallRight = item
                        break
            if wallRight:
                break
        wallTop = False
        for offset in range(1,15):
            pos = (self.xPosition,self.yPosition-offset)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallTop = item
                        break

            if wallTop:
                break
        wallBottom = False
        for offset in range(1,15):
            pos = (self.xPosition,self.yPosition+offset)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallBottom = item
                        break
            if wallBottom:
                break

        if not ( wallLeft and wallRight and wallTop and wallBottom) :
            character.addMessage("no boundaries found")
            return

        roomLeft = self.xPosition-wallLeft.xPosition
        roomRight = wallRight.xPosition-self.xPosition
        roomTop = self.yPosition-wallTop.yPosition
        roomBottom = wallBottom.yPosition-self.yPosition

        if roomLeft+roomRight+1 > 15:
            character.addMessage("room to big")
            return
        if roomTop+roomBottom+1 > 15:
            character.addMessage("room to big")
            return

        wallMissing = False
        items = []
        specialItems = []
        for x in range(-roomLeft,roomRight+1):
            pos = (self.xPosition+x,self.yPosition-roomTop)
            wallFound = None
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
                                specialItems.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for y in range(-roomTop,roomBottom+1):
            pos = (self.xPosition-roomLeft,self.yPosition+y)
            wallFound = None
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
                                specialItems.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for y in range(-roomTop,roomBottom+1):
            pos = (self.xPosition+roomRight,self.yPosition+y)
            wallFound = None
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
                                specialItems.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for x in range(-roomLeft,roomRight+1):
            pos = (self.xPosition+x,self.yPosition+roomBottom)
            wallFound = None
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
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
                if abs(item.xPosition-compareItem.xPosition) > 1 or (abs(item.xPosition-compareItem.xPosition) == 1 and abs(item.yPosition-compareItem.yPosition) > 0):
                    continue
                if abs(item.yPosition-compareItem.yPosition) > 1 or (abs(item.yPosition-compareItem.yPosition) == 1 and abs(item.xPosition-compareItem.xPosition) > 0):
                    continue
                character.addMessage("special items to near to each other")
                return

        import src.rooms
        oldTerrain = self.terrain
        for item in items:
            if item == self:
                continue

            oldX = item.xPosition
            oldY = item.yPosition
            item.container.removeItem(item)
            item.xPosition = roomLeft+oldX-self.xPosition
            item.yPosition = roomTop+oldY-self.yPosition
        room = src.rooms.EmptyRoom(self.xPosition//15,self.yPosition//15,self.xPosition%15-roomLeft,self.yPosition%15-roomTop,creator=self)
        room.reconfigure(roomLeft+roomRight+1,roomTop+roomBottom+1,items)


        xOffset = character.xPosition-self.xPosition
        yOffset = character.yPosition-self.yPosition

        oldTerrain.removeCharacter(character)
        oldTerrain.addRooms([room])
        character.xPosition = roomLeft+xOffset
        character.yPosition = roomTop+yOffset
        room.addCharacter(character,roomLeft+xOffset,roomTop+yOffset)

        self.terrain.removeItem(self)

        self.xPosition = roomLeft
        self.yPosition = roomTop
        self.room = None
        self.terrain = None
        room.addItems([self])

    def getLongInfo(self):
        text = """
item: RoomBuilder

description:
The roombuilder creates rooms from basic items.

Place Walls and and Doors around the room builder and activate the room builder to create a room.

The room has to be a rectangle.

"""
        return text

src.items.addType(RoomBuilder)
