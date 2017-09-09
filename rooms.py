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
		self.itemsOnFloor = []
		self.characters = []
		self.doors = []

		self.walkingAccess = []

		lineCounter = 0
		for line in self.layout[1:].split("\n"):
			rowCounter = 0
			for char in line:
				if char == "X":
					self.itemsOnFloor.append(items.Wall(rowCounter,lineCounter))
				if char == "$":
					door = items.Door(rowCounter,lineCounter)
					self.itemsOnFloor.append(door)
					self.walkingAccess.append((rowCounter,lineCounter))
					self.doors.append(door)
				rowCounter += 1
			lineCounter += 1

	def openDoors(self):
		for door in self.doors:
			door.open()

	def closeDoors(self):
		for door in self.doors:
			door.close()

	def render(self):
		chars = []
		for i in range(0,10):
			subChars = []
			for j in range(0,10):
				subChars.append(" ")
			chars.append(subChars)

		if mainChar.room == self:
			if len(characters[0].quests):
				try:
					chars[characters[0].quests[0].dstY][characters[0].quests[0].dstX] = "X"

					path = calculatePath(characters[0].xPosition,characters[0].yPosition,characters[0].quests[0].dstX,characters[0].quests[0].dstY)
					for item in path:
						chars[item[1]][item[0]] = "x"
				except:
					pass
		
		for item in self.itemsOnFloor:
			chars[item.yPosition][item.xPosition] = item.display

		for character in self.characters:
			chars[character.yPosition][character.xPosition] = character.display
		if mainChar.room == self:
			chars[mainChar.yPosition][mainChar.xPosition] = mainChar.display

		lines = []
		for lineChars in chars:
			lines.append("".join(lineChars))

		return "\n".join(lines)

	def addCharacter(self,character,x,y):
		self.characters.append(character)
		character.room = self
		character.xPosition = x
		character.yPosition = y

	def removeCharacter(self,character):
		self.characters.remove(character)
		character.room = None

class Room1(Room):
	def __init__(self):
		self.roomLayout = """
XXXXXXXXXX
X        X
X        X
X        X
X        X
X        X
X        X
X        X
X        X
XXXX$XXXXX
"""
		super().__init__(self.roomLayout)
		self.offsetX = 2
		self.offsetY = 2
		self.Xpos = 0
		self.Ypos = 0

class Room2(Room):
	def __init__(self):
		self.roomLayout = """
XXXX$XXXXX
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
		super().__init__(self.roomLayout)
		self.offsetX = 3
		self.offsetY = 0
		self.Xpos = 0
		self.Ypos = 0

		self.lever1 = items.Lever(3,6,"engine control")
		self.lever2 = items.Lever(1,2,"boarding alarm")

		coalPile1 = items.Pile(8,3,"coal Pile1",items.Coal)
		coalPile2 = items.Pile(8,4,"coal Pile2",items.Coal)
		coalPile3 = items.Pile(8,5,"coal Pile3",items.Coal)
		coalPile4 = items.Pile(8,6,"coal Pile4",items.Coal)
		self.furnace = items.Furnace(6,6,"Furnace")
		furnaceDisplay = items.Display(8,8,"Furnace monitoring")

		self.itemsOnFloor.extend([self.lever1,self.lever2,coalPile1,coalPile2,coalPile3,coalPile4,self.furnace,furnaceDisplay])

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
		npcQuests = [quest0]
		npc = Character("Ö",2,1,npcQuests,name="Erwin von Libwig")
		npc.watched = True

		lever2 = self.lever2
		def lever2action(self):
			deactivateLeaverQuest = quests.ActivateQuest(lever2,desiredActive=False)
			npc.assignQuest(deactivateLeaverQuest,active=True)
		self.lever2.activateAction = lever2action

		npc2 = Character("Ü",1,1,name="Ernst Ziegelbach")

		self.addCharacter(npc,2,1)
		self.addCharacter(npc2,1,1)
