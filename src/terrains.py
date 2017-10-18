import src.items as items
import src.rooms as rooms

mainChar = None
messages = None
displayChars = None

class Terrain(object):
	def __init__(self,layout,detailedLayout):
		self.itemsOnFloor = []
		self.characters = []
		self.walkingPath = []
		self.rooms = []

		self.itemByCoordinates = {}
		self.roomByCoordinates = {}

		mapItems = []
		self.detailedLayout = detailedLayout
		lineCounter = 0
		for layoutline in self.detailedLayout.split("\n")[1:]:
			rowCounter = 0
			for char in layoutline:
				if char in (" ",".",",","@"):
					pass
				elif char == "X":
					mapItems.append(items.Wall(rowCounter,lineCounter))
				elif char == "#":
					mapItems.append(items.Pipe(rowCounter,lineCounter))
				elif char == "R":
					pass
				elif char == "O":
					mapItems.append(items.Item(displayChars.clamp_active,rowCounter,lineCounter))
				elif char == "0":
					mapItems.append(items.Item(displayChars.clamp_inactive,rowCounter,lineCounter))
				elif char == "8":
					mapItems.append(items.Chain(rowCounter,lineCounter))
				elif char == "C":
					mapItems.append(items.Winch(rowCounter,lineCounter))
				elif char == "P":
					mapItems.append(items.Pile(rowCounter,lineCounter))
				else:
					mapItems.append(items.Item(displayChars.randomStuff2[((2*rowCounter)+lineCounter)%10],rowCounter,lineCounter))
				rowCounter += 1
			lineCounter += 1

		self.addItems(mapItems)

		roomsOnMap = []
		self.tutorialVat = None
		self.tutorialMachineRoom = None
		lineCounter = 0
		for layoutline in layout.split("\n")[1:]:
			rowCounter = 0
			meta = False
			for char in layoutline:
				if meta:
					meta = False
					continue
				else:
					meta = True
				if char in (" ",".",",","@"):
					pass
				elif char == "X":
					roomsOnMap.append(rooms.MechArmor(rowCounter,lineCounter,0,0))
				elif char == "V":
					room = rooms.Vat2(rowCounter,lineCounter,2,2)
					if not self.tutorialVat:
						self.tutorialVat = room
					roomsOnMap.append(room)
				elif char == "v":
					roomsOnMap.append(rooms.Vat1(rowCounter,lineCounter,2,2))
				elif char == "Q":
					roomsOnMap.append(rooms.InfanteryQuarters(rowCounter,lineCounter,1,2))
				elif char == "r":
					roomsOnMap.append(rooms.Room1(rowCounter,lineCounter,1,2))
				elif char == "M":
					room = rooms.TutorialMachineRoom(rowCounter,lineCounter,4,0)
					if not self.tutorialMachineRoom:
						self.tutorialMachineRoom = room
					roomsOnMap.append(room)
				elif char == "C":
					roomsOnMap.append(rooms.CargoRoom(rowCounter,lineCounter,3,0))
				elif char == "?":
					roomsOnMap.append(rooms.CpuWasterRoom(rowCounter,lineCounter,2,2))
				elif char == "t":
					self.movingRoom = rooms.MiniMech(rowCounter,lineCounter,2,2)
					roomsOnMap.append(self.movingRoom)
				else:
					pass
				rowCounter += 1
			lineCounter += 1

		self.addRooms(roomsOnMap)

		rawWalkingPath = []
		lineCounter = 0
		for line in self.detailedLayout[1:].split("\n"):
			rowCounter = 0
			for char in line:
				if char == ".":
					rawWalkingPath.append((rowCounter,lineCounter))
				rowCounter += 1
			lineCounter += 1

		startWayPoint = rawWalkingPath[0]
		endWayPoint = rawWalkingPath[0]

		self.walkingPath.append(rawWalkingPath[0])
		rawWalkingPath.remove(rawWalkingPath[0])

		while (1==1):
			endWayPoint = self.walkingPath[-1]
			east = (endWayPoint[0]+1,endWayPoint[1])
			west = (endWayPoint[0]-1,endWayPoint[1])
			south = (endWayPoint[0],endWayPoint[1]+1)
			north = (endWayPoint[0],endWayPoint[1]-1)
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

	def addRooms(self,rooms):
		self.rooms.extend(rooms)
		for room in rooms:
			room.terrain = self
			if (room.xPosition,room.yPosition) in self.roomByCoordinates:
				self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
			else:
				self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]


	def addItems(self,items):
		self.itemsOnFloor.extend(items)
		for item in items:
			item.terrain = self
			if (item.xPosition,item.yPosition) in self.itemByCoordinates:
				self.itemByCoordinates[(item.xPosition,item.yPosition)].append(item)
			else:
				self.itemByCoordinates[(item.xPosition,item.yPosition)] = [item]

	def render(self):
		global mapHidden
		if mainChar.room == None:
			mapHidden = False
		else:
			if mainChar.room.open:
				mapHidden = False
			else:
				mapHidden = True

		chars = []
		for i in range(0,250):
			line = []
			for j in range(0,250):
				if not mapHidden:
					line.append(displayChars.floor)
				else:
					line.append(displayChars.void)
			chars.append(line)

		for room in self.rooms:
			if mainChar.room == room:
				room.hidden = False
			else:
				if not mapHidden and room.open:
					room.hidden = False
					room.applySkippedAdvances()
				else:
					room.hidden = True
				
		if not mapHidden:
			for item in self.itemsOnFloor:
				chars[item.yPosition][item.xPosition] = item.display

		for room in self.rooms:
			if mapHidden and room.hidden :
				continue

			renderedRoom = room.render()
			
			xOffset = room.xPosition*15+room.offsetX
			yOffset = room.yPosition*15+room.offsetY

			lineCounter = 0
			for line in renderedRoom:
				rowCounter = 0
				for char in line:
					chars[lineCounter+yOffset][rowCounter+xOffset] = char
					rowCounter += 1
				lineCounter += 1

		if not mapHidden:
			for character in self.characters:
				if character == mainChar:
					if len(mainChar.quests):
						try:
							path = calculatePath(mainChar.xPosition,mainChar.yPosition,mainChar.quests[0].dstX,mainChar.quests[0].dstY,self.walkingPath)
							for item in path[:-1]:
								chars[item[1]][item[0]] = displayChars.pathMarker
						except:
							pass

				chars[character.yPosition][character.xPosition] = character.display

		return chars

	def getAffectedByRoomMovementNorth(self,room,force=1,movementBlock=set()):
		# check for collision
		roomCandidates = []
		bigX = room.xPosition
		bigY = room.yPosition
		possiblePositions = set()
		for i in range(-2,2):
			for j in range(-2,2):
				possiblePositions.add((bigX-i,bigY-j))
		for coordinate in possiblePositions:
			if coordinate in self.roomByCoordinates:
				roomCandidates.extend(self.roomByCoordinates[coordinate])

		roomCollisions = set()
		for roomCandidate in roomCandidates:
			if (room.yPosition*15 + room.offsetY) == (roomCandidate.yPosition*15+roomCandidate.offsetY+roomCandidate.sizeY):
				if (room.xPosition*15+room.offsetX < roomCandidate.xPosition*15+roomCandidate.offsetX+roomCandidate.sizeX) and (room.xPosition*15+room.offsetX+room.sizeX > roomCandidate.xPosition*15+roomCandidate.offsetX):
					roomCollisions.add(roomCandidate)

		for roomCollision in roomCollisions:
			movementBlock.add(roomCollision)
			self.getAffectedByRoomMovementNorth(roomCollision,force=force,movementBlock=movementBlock)

		posX = room.xPosition*15+room.offsetX-1
		maxX = room.xPosition*15+room.offsetX+room.sizeX-1
		while posX < maxX:
			posX += 1
			if (posX,room.yPosition*15+room.offsetY-1) in self.itemByCoordinates:
				movementBlock.update(self.itemByCoordinates[(posX,room.yPosition*15+room.offsetY-1)])

	def moveRoomNorth(self,room,force=1,movementBlock=[]):
		if room.offsetY > -5:
			room.offsetY -= 1
		else:
			room.offsetY = 9
			if (room.xPosition,room.yPosition) in self.roomByCoordinates:
				self.roomByCoordinates[(room.xPosition,room.yPosition)].remove(room)
				if not len(self.roomByCoordinates[(room.xPosition,room.yPosition)]):
					del self.roomByCoordinates[(room.xPosition,room.yPosition)]
			room.yPosition -= 1
			if (room.xPosition,room.yPosition) in self.roomByCoordinates:
				self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
			else:
				self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]

	def getAffectedByRoomMovementSouth(self,room,force=1,movementBlock=set()):
		# check for collision
		roomCandidates = []
		bigX = room.xPosition
		bigY = room.yPosition
		possiblePositions = set()
		for i in range(-2,2):
			for j in range(-2,2):
				possiblePositions.add((bigX-i,bigY-j))
		for coordinate in possiblePositions:
			if coordinate in self.roomByCoordinates:
				roomCandidates.extend(self.roomByCoordinates[coordinate])

		roomCollisions = set()
		for roomCandidate in roomCandidates:
			if (room.yPosition*15 + room.offsetY+room.sizeY) == (roomCandidate.yPosition*15+roomCandidate.offsetY):
				if (room.xPosition*15+room.offsetX < roomCandidate.xPosition*15+roomCandidate.offsetX+roomCandidate.sizeX) and (room.xPosition*15+room.offsetX+room.sizeX > roomCandidate.xPosition*15+roomCandidate.offsetX):
					roomCollisions.add(roomCandidate)

		for roomCollision in roomCollisions:
			movementBlock.add(roomCollision)
			self.getAffectedByRoomMovementSouth(roomCollision,force=force,movementBlock=movementBlock)

		posX = room.xPosition*15+room.offsetX-1
		maxX = room.xPosition*15+room.offsetX+room.sizeX-1
		while posX < maxX:
			posX += 1
			if (posX,room.yPosition*15+room.offsetY+room.sizeY) in self.itemByCoordinates:
				movementBlock.update(self.itemByCoordinates[(posX,room.yPosition*15+room.offsetY+room.sizeY)])

	def moveRoomSouth(self,room,force=1,movementBlock=[]):
		if room.offsetY < 9:
			room.offsetY += 1
		else:
			room.offsetY = -5
			if (room.xPosition,room.yPosition) in self.roomByCoordinates:
				self.roomByCoordinates[(room.xPosition,room.yPosition)].remove(room)
				if not len(self.roomByCoordinates[(room.xPosition,room.yPosition)]):
					del self.roomByCoordinates[(room.xPosition,room.yPosition)]
			room.yPosition += 1
			if (room.xPosition,room.yPosition) in self.roomByCoordinates:
				self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
			else:
				self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]

	def getAffectedByRoomMovementWest(self,room,force=1,movementBlock=set()):
		# check for collision
		roomCandidates = []
		bigX = room.xPosition
		bigY = room.yPosition
		possiblePositions = set()
		for i in range(-2,2):
			for j in range(-2,2):
				possiblePositions.add((bigX-i,bigY-j))
		for coordinate in possiblePositions:
			if coordinate in self.roomByCoordinates:
				roomCandidates.extend(self.roomByCoordinates[coordinate])

		roomCollisions = set()
		for roomCandidate in roomCandidates:
			if (room.xPosition*15 + room.offsetX) == (roomCandidate.xPosition*15+roomCandidate.offsetX+roomCandidate.sizeX):
				if (room.yPosition*15+room.offsetY < roomCandidate.yPosition*15+roomCandidate.offsetY+roomCandidate.sizeY) and (room.yPosition*15+room.offsetY+room.sizeY > roomCandidate.yPosition*15+roomCandidate.offsetY):
					roomCollisions.add(roomCandidate)

		for roomCollision in roomCollisions:
			movementBlock.add(roomCollision)
			self.getAffectedByRoomMovementWest(roomCollision,force=force,movementBlock=movementBlock)

		posY = room.yPosition*15+room.offsetY-1
		maxY = room.yPosition*15+room.offsetY+room.sizeY-1
		while posY < maxY:
			posY += 1
			if (room.xPosition*15+room.offsetX-1,posY) in self.itemByCoordinates:
				movementBlock.update(self.itemByCoordinates[(room.xPosition*15+room.offsetX-1,posY)])

	def moveRoomWest(self,room):
		if room.offsetX > -5:
			room.offsetX -= 1
		else:
			room.offsetX = 9
			if (room.xPosition,room.yPosition) in self.roomByCoordinates:
				self.roomByCoordinates[(room.xPosition,room.yPosition)].remove(room)
				if not len(self.roomByCoordinates[(room.xPosition,room.yPosition)]):
					del self.roomByCoordinates[(room.xPosition,room.yPosition)]
			room.xPosition -= 1
			if (room.xPosition,room.yPosition) in self.roomByCoordinates:
				self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
			else:
				self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]

	def getAffectedByRoomMovementEast(self,room,force=1,movementBlock=set()):
		# check for collision
		roomCandidates = []
		bigX = room.xPosition
		bigY = room.yPosition
		possiblePositions = set()
		for i in range(-2,2):
			for j in range(-2,2):
				possiblePositions.add((bigX-i,bigY-j))
		for coordinate in possiblePositions:
			if coordinate in self.roomByCoordinates:
				roomCandidates.extend(self.roomByCoordinates[coordinate])

		roomCollisions = set()
		for roomCandidate in roomCandidates:
			if (room.xPosition*15 + room.offsetX+ room.sizeX) == (roomCandidate.xPosition*15+roomCandidate.offsetX):
				if (room.yPosition*15+room.offsetY < roomCandidate.yPosition*15+roomCandidate.offsetY+roomCandidate.sizeY) and (room.yPosition*15+room.offsetY+room.sizeY > roomCandidate.yPosition*15+roomCandidate.offsetY):
					roomCollisions.add(roomCandidate)

		for roomCollision in roomCollisions:
			movementBlock.add(roomCollision)
			self.getAffectedByRoomMovementEast(roomCollision,force=force,movementBlock=movementBlock)

		posY = room.yPosition*15+room.offsetY-1
		maxY = room.yPosition*15+room.offsetY+room.sizeY-1
		while posY < maxY:
			posY += 1
			if (room.xPosition*15+room.offsetX+room.sizeX,posY) in self.itemByCoordinates:
				movementBlock.update(self.itemByCoordinates[(room.xPosition*15+room.offsetX+room.sizeX,posY)])


	def moveRoomEast(self,room):
		if room.offsetX < 9:
			room.offsetX += 1
		else:
			room.offsetX = -5
			if (room.xPosition,room.yPosition) in self.roomByCoordinates:
				self.roomByCoordinates[(room.xPosition,room.yPosition)].remove(room)
				if not len(self.roomByCoordinates[(room.xPosition,room.yPosition)]):
					del self.roomByCoordinates[(room.xPosition,room.yPosition)]
			room.xPosition += 1
			if (room.xPosition,room.yPosition) in self.roomByCoordinates:
				self.roomByCoordinates[(room.xPosition,room.yPosition)].append(room)
			else:
				self.roomByCoordinates[(room.xPosition,room.yPosition)] = [room]

class TutorialTerrain(Terrain):
	def __init__(self):

		layout = """
XXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXX
XX??????????????????XX
XX??????????????????XX
XX?? . . . . . . .??XX
XX?? .?????????? .??XX
XX?? .?????????? .??XX
XX?? . . . . . . .??XX
XX??  ??????????  ??XX
XX??  ??????????  ??XX
XX??  ??????????  ??XX
XXXXXXXXXXXXXXXXXXXXXX"""
		layout = """
X X X X X X X X X X X
X X X X X X X X X X X
X V v ? ? ? ? ? v V X
X   . t . . . . . ? X
X ? . M Q r ? ? . ? X
X ? . ? ? ? ? ? . ? X
X C . . . . . . . ? X
X C   C C C C C   ? X
X C   C C C C C t ? X
X X X C C C C C X X X """
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
                  ###  ###        ######                                                                                                     XXXXXXXXX               
               ####O####O####  ####O  O########  O    O   #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # RRRRRRRRRR #  #RRRRRRRRRR#   #RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #ORRRRRRRRRRO# ##RRRRRRRRRR## ##RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # RRRRRRRRRR # #ORRRRRRRRRRO# #ORRRRRRRRRRO#XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # RRRRRRRRRR # # RRRRRRRRRR # ##RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #ORRRRRRRRRRO# # RRRRRRRRRR #  #RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # RRRRRRRRRR # # RRRRRRRRRR # ##RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # RRRRRRRRRR ### RRRRRRRRRR # #ORRRRRRRRRRO#XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #ORRRRRRRRRRO ##ORRRRRRRRRRO# ##RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               ##RRRRRRRRRR# ###RRRRRRRRRR##  #RRRRRRRRRR#####           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
                 RRRRRRRRRR  #  RRRRRRRRRR     RRRRRRRRRR XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               XX  O    O    ####O#   ##O####    O8   O    X                                                                                                         
               XX               ### X  ###        8                                                                                                                  
                  X  O   O          XX     ##     8        X                                                                                                        
               X X RRRRRRRRRR                     8                                                                                    XXXXXXXXXXXXXXX               
                   RRRRRRRRRR#                    8                                                                                    X#           #X               
                   RRRRRRRRRR#                                                                                                         X#           #X               
                   RRRRRRRRRR#                                                                                                         X#           #X               
                   RRRRRRRRRR#                                                                                                         X#           #X               
                   RRRRRRRRRR#                                                                                                         X#           #X               
                   RRRRRRRRRR#                                                                                                         X#           #X               
                   RRRRRRRRRR#                                                                                                         X#           #X               
                   RRRRRRRRRR#                                                                                                         X#           #X               
                   RRRRRRRRRR#                                                                                                         X#           #X               
                   RRRRRRRRRR#                                                                                                         X#           #X               
                   RRRRRRRRRR#                                                                                                         X#           #X               
                   RRRRRRRRRR#                                                                                                         X#           #X               
                XXXX                                                                                                                                                 
                   RRRRRRRRRR#              .............................................................................              X#           #X               
               XXXXXXXXXXXX#XX              .XXXXXXX XXXXXXXXXXXXXX XXXXXXXXXXXXXX XXXXXXXXXXXXXX XXXXXXXXXXXXX XXXXXXXX.              XX            X               
               X                            .              X                                                            .                                            
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#RRRRRRRRRRR#XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               XXXXXXXXXXXX#XX              .XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.              XX            X               
               XXXXXXXXXXXX#XX              .XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.              XX            X               
               X                            .              X                                                            .                                            
               X#           #X              .X#           #XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#           #XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#           #XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X             ..X#           #XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X             .###           #XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X             ..X#           #XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#           #XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#           #XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#           #XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X              .X#           #XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X             ..X#           #XX#           #XX#           #XX#           #XX#           #X.              X#           #X               
               X#           #X             .XX# XPXX   XPX#XX# XPX    XPX#XX# XPX    XPX#XX# XPX    XPX#XX# XPX    XPX#X.              X#           #X               
               XXXXXXXXXXXX#XX             ..XXXXC X XXXC XXXXXXC XXXXXC XXXXXXC  XXXXC XXXXXXC XX XXC XXXXXXC X XXXC XX.              XX            X               
               X#                           .....8......8.......8......8.......8......8.......8......8.......8......8....              X#           #X               
               XX                               ...    ...     ...    ...     ...    ...     ...    ...     ...    ...                 XX            X               
               X#                                                                                                                      X#           #X               
               X#                                                                                                                      X#           #X               
               X#                                                                                                                      X#           #X               
               X#                                                                                                                      X#           #X               
               X#                                                                                                                      X#           #X               
               X#                                                                                                                      X#           #X               
               X#                                                                                                                      X#           #X               
               X#                                                                                                                      X#           #X               
               X#                                                                                                                      X#           #X               
               X#                                                                                                                      X#           #X               
               X#                                                                                                                      X#           #X               
               X#                                                                                                                      X#           #X               
               XXXXXXXXXXXX#                  #              #              #              #              #                            XX            X               
               XXXXXXXXXXXX#                 X#X           XX#X           XX#X           XX#X           XX#X           X               XX            X               
               X                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
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
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
               XXXXXXXXXXXX#                 X#X           XX#X           XX#X           XX#X           XX#X           X               XX            X               
               XXXXXXXXXXXX#                 X#X           #X#X           #X#X           #X#X           #X#X           X               XX            X               
               X                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
               X#                            X#X           XX#X           XX#X           XX#X           XX#X           X               X#           #X               
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
                                             X#X           XX#X           XX#X           XX#X           XX#X           X                                             
"""
		super().__init__(layout,detailedLayout)

