import items 
import quests

Character = None
mainChar = None
characters = None
messages = None
calculatePath = None

class Room(object):
	def __init__(self,layout):
		self.layout = layout
		self.hidden = True
		self.itemsOnFloor = []
		self.characters = []
		self.doors = []
		self.xPosition = None
		self.yPosition = None
		self.name = "Room"
		self.open = False
		self.terrain = None

		self.itemByCoordinates = {}

		self.walkingAccess = []
		lineCounter = 0
		itemsOnFloor = []
		for line in self.layout[1:].split("\n"):
			rowCounter = 0
			for char in line:
				if char in (" ",".","@"):
					pass
				elif char == "X":
					itemsOnFloor.append(items.Wall(rowCounter,lineCounter))
				elif char == "$":
					door = items.Door(rowCounter,lineCounter)
					itemsOnFloor.append(door)
					self.walkingAccess.append((rowCounter,lineCounter))
					self.doors.append(door)
				elif char == "#":
					itemsOnFloor.append(items.Pipe(rowCounter,lineCounter))
				else:
					itemsOnFloor.append(items.Item("[]",rowCounter,lineCounter))
				rowCounter += 1
			lineCounter += 1

		rawWalkingPath = []
		lineCounter = 0
		for line in self.layout[1:].split("\n"):
			rowCounter = 0
			for char in line:
				if char == ".":
					rawWalkingPath.append((rowCounter,lineCounter))
				rowCounter += 1
			lineCounter += 1

		self.walkingPath = []
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

		self.addItems(itemsOnFloor)

	def openDoors(self):
		for door in self.doors:
			door.open()
			self.open = True

	def closeDoors(self):
		for door in self.doors:
			door.close()
			self.open = False

	def render(self):
		if not self.hidden:
			chars = []
			for i in range(0,10):
				subChars = []
				for j in range(0,10):
					subChars.append("⛚ ")
				chars.append(subChars)

			if mainChar.room == self:
				if len(characters[0].quests):
					try:
						chars[characters[0].quests[0].dstY][characters[0].quests[0].dstX] = "xX"
						path = calculatePath(characters[0].xPosition,characters[0].yPosition,characters[0].quests[0].dstX,characters[0].quests[0].dstY,self.walkingPath)
						for item in path:
							chars[item[1]][item[0]] = "xx"
					except:
						pass
			
			for item in self.itemsOnFloor:
				chars[item.yPosition][item.xPosition] = item.display

			for character in self.characters:
				chars[character.yPosition][character.xPosition] = character.display
			if mainChar.room == self:
				chars[mainChar.yPosition][mainChar.xPosition] = mainChar.display
		else:
			chars = []
			for i in range(0,10):
				subChars = []
				for j in range(0,10):
					subChars.append("⼞")
				chars.append(subChars)

			for item in self.itemsOnFloor:
				if item.xPosition == 0 or item.xPosition == 9 or item.yPosition == 0 or item.yPosition == 9:
					chars[item.yPosition][item.xPosition] = item.display

		return chars

	def addCharacter(self,character,x,y):
		self.characters.append(character)
		character.room = self
		character.xPosition = x
		character.yPosition = y

	def removeCharacter(self,character):
		self.characters.remove(character)
		character.room = None

	def addItems(self,items):
		self.itemsOnFloor.extend(items)
		for item in items:
			item.room = self
			self.itemByCoordinates[(item.xPosition,item.yPosition)] = item

	def moveCharacterWest(self,character):
		newPosition = (character.xPosition-1,character.yPosition)
		return self.moveCharacter(character,newPosition)

	def moveCharacterEast(self,character):
		newPosition = (character.xPosition+1,character.yPosition)
		return self.moveCharacter(character,newPosition)

	def moveCharacterNorth(self,character):
		if not character.yPosition:
			newYPos = character.yPosition+character.room.yPosition*15+character.room.offsetY-1
			newXPos = character.xPosition+character.room.xPosition*15+character.room.offsetX
			character.xPosition = newXPos
			character.yPosition = newYPos
			self.removeCharacter(character)
			self.terrain.characters.append(character)
			character.terrain = self.terrain
			character.changed()
			return

		newPosition = (character.xPosition,character.yPosition-1)
		return self.moveCharacter(character,newPosition)

	def moveCharacterSouth(self,character):
		if character.yPosition == 9:
			newYPos = character.yPosition+character.room.yPosition*15+character.room.offsetY+1
			newXPos = character.xPosition+character.room.xPosition*15+character.room.offsetX
			character.xPosition = newXPos
			character.yPosition = newYPos
			self.removeCharacter(character)
			self.terrain.characters.append(character)
			character.terrain = self.terrain
			character.changed()
			return

		newPosition = (character.xPosition,character.yPosition+1)
		return self.moveCharacter(character,newPosition)

	def moveCharacter(self,character,newPosition):
		if newPosition in self.itemByCoordinates:
			item  = self.itemByCoordinates[newPosition]
			if not item.walkable:
				return item
			else:
				character.xPosition = newPosition[0]
				character.yPosition = newPosition[1]
		character.xPosition = newPosition[0]
		character.yPosition = newPosition[1]
		character.changed()
		return None
	
class Room1(Room):
	def __init__(self):
		self.roomLayout = """
XXXXXXXXXX
X#-------X
X#......-X
X#.- --.-X
X#.   -.-X
X#.----.-X
XB.BBBB.BX
X ...... X
XMMM MMMMX
XXXX$XXXXX
"""
		super().__init__(self.roomLayout)
		self.name = "Vat"
		self.offsetX = 2
		self.offsetY = 2
		self.xPosition = 0
		self.yPosition = 0

class Room2(Room):
	def __init__(self):
		self.roomMeta = """
"""
		roomLayout = """
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX

XXX↓X↓↓X↓X
X  #8## #X
X  #8## #X
X  #8##8#X
X  # ## #X
X  # ##8#X
X  #8## #X
X  #8## #X
X  #8## #X
XXX↓X↓↓↓↓X

XXXXXXXXXX
X        X
X        X
X  88##8 X
X  #8##8 X
X  88##8 X
X   8    X
X        X
X        X
XXXXXXXXXX

XXXXHXXXXX
X@Iv vID#X
X@      #X
X@ 8#OF PX
X@ ##OF PX
XB 8#OF PX
XB |DI  PX
XB      #X
XPPPPPID#X
XXXXXXXXXX
"""
		roomLayout = """
XXXX$XXXXX
X@ v vID#X
X@......#X
X@.8#OF.PX
X@.##OF.PX
XB.8#OF.PX
XB.|DI .PX
XB......#X
XPPPP ID#X
XXXXXXXXXX
"""
		super().__init__(roomLayout)
		self.name = "Boilerroom"
		self.offsetX = 3
		self.offsetY = 0
		self.xPosition = 0
		self.yPosition = 1

		self.lever1 = items.Lever(3,6,"engine control")
		self.lever2 = items.Lever(1,2,"boarding alarm")

		coalPile1 = items.Pile(8,3,"coal Pile1",items.Coal)
		coalPile2 = items.Pile(8,4,"coal Pile2",items.Coal)
		coalPile3 = items.Pile(8,5,"coal Pile3",items.Coal)
		coalPile4 = items.Pile(8,6,"coal Pile4",items.Coal)
		self.furnace = items.Furnace(6,6,"Furnace")
		furnaceDisplay = items.Display(8,8,"Furnace monitoring")

		self.addItems([self.lever1,self.lever2,coalPile1,coalPile2,coalPile3,coalPile4,self.furnace,furnaceDisplay])

		quest0 = quests.ActivateQuest(self.lever1)
		quest1 = quests.MoveQuest(self,2,2)
		quest2 = quests.MoveQuest(self,2,7)
		quest3 = quests.MoveQuest(self,7,7)
		quest4 = quests.MoveQuest(self,7,2)
		quest0.followUp = quest1
		quest1.followUp = quest2
		quest2.followUp = quest3
		quest3.followUp = quest4
		quest4.followUp = quest1
		npc = Character("Ⓛ ",2,1,name="Erwin von Libwig")
		self.addCharacter(npc,2,1)
		npc.assignQuest(quest0)

		lever2 = self.lever2
		def lever2action(self):
			deactivateLeaverQuest = quests.ActivateQuest(lever2,desiredActive=False)
			npc.assignQuest(deactivateLeaverQuest,active=True)
		self.lever2.activateAction = lever2action

class Room3(Room):
	def __init__(self):
		self.roomLayout = """
XXXXXXXXXX
X????????X
X?......?X
X?.X#X?.?X
XP.?#??.?X
XP.X#X?.?X
X?.X#  .?X
X?......?X
X??? ????X
XXXX$XXXXX
"""
		super().__init__(self.roomLayout)
		self.offsetX = 2
		self.offsetY = 2
		self.xPosition = 1
		self.yPosition = 0

class Room4(Room):
	def __init__(self):
		self.roomLayout = """
XX$XXXXXXX
X? ??????X
X?......PX
X?.????.PX
X?.????.#X
X?.???P.#X
X?.?X??.#X
X?......#X
X? ?????#X
XXXXXXXXXX
"""
		super().__init__(self.roomLayout)
		self.offsetX = 2
		self.offsetY = 2
		self.xPosition = 1
		self.yPosition = 1
