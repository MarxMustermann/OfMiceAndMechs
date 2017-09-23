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
		self.shownQuestmarkerLastRender = False
		self.sizeX = None
		self.sizeY = None
		self.timeIndex = 0
		self.delayedTicks = 0
		self.events = []
		self.floorDisplay = ["::"]

		self.itemByCoordinates = {}

		self.walkingAccess = []
		lineCounter = 0
		itemsOnFloor = []
		for line in self.layout[1:].split("\n"):
			rowCounter = 0
			for char in line:
				if char in (" ",".","@"):
					pass
				elif char in ("X","&"):
					itemsOnFloor.append(items.Wall(rowCounter,lineCounter))
				elif char == "$":
					door = items.Door(rowCounter,lineCounter)
					itemsOnFloor.append(door)
					self.walkingAccess.append((rowCounter,lineCounter))
					self.doors.append(door)
				elif char == "P":
					itemsOnFloor.append(items.Pile(rowCounter,lineCounter))
				elif char == "F":
					itemsOnFloor.append(items.Furnace(rowCounter,lineCounter))
				elif char == "#":
					itemsOnFloor.append(items.Pipe(rowCounter,lineCounter))
				elif char == "D":
					itemsOnFloor.append(items.Display(rowCounter,lineCounter))
				elif char == "v":
					#to be bin
					itemsOnFloor.append(items.Item("⛛ ",rowCounter,lineCounter))
				elif char == "O":
					#to be pressure Tank
					itemsOnFloor.append(items.Item("伫",rowCounter,lineCounter))
					#itemsOnFloor.append(items.Item("伾",rowCounter,lineCounter))
				elif char == "8":
					#to be chains
					itemsOnFloor.append(items.Item("⛓ ",rowCounter,lineCounter))
				elif char == "I":
					#to be commlink
					itemsOnFloor.append(items.Item("ߐߐ",rowCounter,lineCounter))
				elif char == "H":
					itemsOnFloor.append(items.Hutch(rowCounter,lineCounter))
				elif char == "'":
					itemsOnFloor.append(items.Hutch(rowCounter,lineCounter,activated=True))
				elif char == "o":
					#to be grid
					itemsOnFloor.append(items.Item("░░",rowCounter,lineCounter))
				elif char == "a":
					#to be acid
					displayChars = ["♒♒","≈≈","≈♒","♒≈","≈≈"]
					item = items.Item(displayChars[((2*rowCounter)+lineCounter)%5],rowCounter,lineCounter)
					item.walkable = True
					itemsOnFloor.append(item)
				elif char == "b":
					#to be foodstuffs
					displayChars = ["՞՞","🍖 "," ☠","💀 ","👂 ","✋ "]
					itemsOnFloor.append(items.Item(displayChars[((2*rowCounter)+lineCounter)%6],rowCounter,lineCounter))
				elif char == "m":
					displayChars = ["⌺ ","⚙ ","⌼ ","⍯ ","⌸ "]
					itemsOnFloor.append(items.Item(displayChars[((2*rowCounter)+lineCounter)%5],rowCounter,lineCounter))
				elif char == "h":
					itemsOnFloor.append(items.Item("🜹 ",rowCounter,lineCounter))
				elif char == "i":
					itemsOnFloor.append(items.Item("⍌ ",rowCounter,lineCounter))
				elif char == "p":
					itemsOnFloor.append(items.Item("┅┅",rowCounter,lineCounter))
				elif char == "q":
					item = items.Item("━━",rowCounter,lineCounter)
					item.walkable = True
					itemsOnFloor.append(item)
				elif char == "r":
					item = items.Item("┳━",rowCounter,lineCounter)
					item.walkable = True
					itemsOnFloor.append(item)
				elif char == "s":
					item = items.Item("┓ ",rowCounter,lineCounter)
					item.walkable = True
					itemsOnFloor.append(item)
				elif char == "t":
					item = items.Item("┛ ",rowCounter,lineCounter)
					item.walkable = True
					itemsOnFloor.append(item)
				elif char == "u":
					item = items.Item("┗━",rowCounter,lineCounter)
					item.walkable = True
					itemsOnFloor.append(item)
				elif char == "w":
					itemsOnFloor.append(items.Item("⚟ ",rowCounter,lineCounter))
				elif char == "x":
					itemsOnFloor.append(items.Item("⚞ ",rowCounter,lineCounter))
				elif char == "y":
					itemsOnFloor.append(items.Item("◎ ",rowCounter,lineCounter))
				elif char == "j":
					itemsOnFloor.append(items.Item("🝇 ",rowCounter,lineCounter))
				elif char == "c":
					# to be corpse type I
					itemsOnFloor.append(items.Corpse(rowCounter,lineCounter))
				elif char == "z":
					item = items.Item("┃ ",rowCounter,lineCounter)
					item.walkable = True
					itemsOnFloor.append(item)
				elif char == "B":
					item = items.Item("❖❖",rowCounter,lineCounter)
					item.walkable = True
					itemsOnFloor.append(item)
				else:
					displayChars = ["🜆 ","🜾 ","ꘒ ","ꖻ ","ᵺ "]
					displayChars = ["🝍🝍","🝍🝍","🝍🝍","🖵 ","🞇 ","🖵 ","⿴","⿴","🞇 ","🜕 "]
					itemsOnFloor.append(items.Item(displayChars[((2*rowCounter)+lineCounter)%10],rowCounter,lineCounter))
				rowCounter += 1
				self.sizeX = rowCounter
			lineCounter += 1
		self.sizeY = lineCounter-1

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
			fixedChar = None
			if len(self.floorDisplay) == 1:
				fixedChar = self.floorDisplay[0]
			for i in range(0,self.sizeY):
				subChars = []
				for j in range(0,self.sizeX):
					if fixedChar:
						subChars.append(fixedChar)
					else:
						subChars.append(self.floorDisplay[(j+i+self.timeIndex*2)%len(self.floorDisplay)])
				chars.append(subChars)
			
			for item in self.itemsOnFloor:
				chars[item.yPosition][item.xPosition] = item.display

			for character in self.characters:
				chars[character.yPosition][character.xPosition] = character.display

			if mainChar.room == self:
				if len(characters[0].quests):
					try:
						if not self.shownQuestmarkerLastRender:
							chars[characters[0].quests[0].dstY][characters[0].quests[0].dstX] = "xX"
							path = calculatePath(characters[0].xPosition,characters[0].yPosition,characters[0].quests[0].dstX,characters[0].quests[0].dstY,self.walkingPath)
							for item in path:
								chars[item[1]][item[0]] = "xx"
							
							self.shownQuestmarkerLastRender = True
						else:
							self.shownQuestmarkerLastRender = False
					except:
						pass

			if mainChar.room == self:
				chars[mainChar.yPosition][mainChar.xPosition] = mainChar.display
		else:
			chars = []
			for i in range(0,self.sizeY):
				subChars = []
				for j in range(0,self.sizeX):
					subChars.append("⼞")
				chars.append(subChars)

			for item in self.itemsOnFloor:
				if item.xPosition == 0 or item.xPosition == self.sizeX-1 or item.yPosition == 0 or item.yPosition == self.sizeY-1:
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
		if character.yPosition == self.sizeY-1:
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

	def applySkippedAdvances(self):
		while self.delayedTicks > 0:
			for character in self.characters:
				character.advance()
			self.delayedTicks -= 1

	def advance(self):
		self.timeIndex += 1
		if len(self.events):
			if self.timeIndex == self.events[0].tick:
				self.events[0].handleEvent()
				self.events.remove(self.events[0])
		if not self.hidden:
			if self.delayedTicks > 0:
				self.applySkippedAdvances()
			
			for character in self.characters:
				character.advance()
		else:
			self.delayedTicks += 1
	
class Room1(Room):
	def __init__(self,xPosition=0,yPosition=0,offsetX=2,offsetY=2):
		self.roomLayout = """
XXXXXXXXXX
X#-------X
X#......-X
X#.- --.-X
X#.   -.-X
X#.----.-X
XB.BBBB.BX
X ...... X
XMMv vMMMX
XXXX$XXXXX
"""
		super().__init__(self.roomLayout)
		self.name = "Vat"
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.xPosition = xPosition
		self.yPosition = yPosition

class Room2(Room):
	def __init__(self,xPosition=0,yPosition=1,offsetX=4,offsetY=0):
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
X@.8#O . X
X@.##O . X
XH.8#O . X
XH.|DI . X
XH......#X
XXPPP ID#X
XXXXXXXXXX
"""
		super().__init__(roomLayout)
		self.name = "Boilerroom"
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.xPosition = xPosition
		self.yPosition = yPosition

		self.lever1 = items.Lever(3,6,"engine control")
		self.lever2 = items.Lever(1,2,"boarding alarm")

		coalPile1 = items.Pile(8,3,"coal Pile1",items.Coal)
		coalPile2 = items.Pile(8,4,"coal Pile2",items.Coal)
		coalPile3 = items.Pile(8,5,"coal Pile3",items.Coal)
		coalPile4 = items.Pile(8,6,"coal Pile4",items.Coal)
		self.furnace1 = items.Furnace(6,3,"Furnace")
		self.furnace2 = items.Furnace(6,4,"Furnace")
		self.furnace3 = items.Furnace(6,5,"Furnace")

		self.addItems([self.lever1,self.lever2,coalPile1,coalPile2,coalPile3,coalPile4,self.furnace])

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
		npc = Character("Ⓛ ",1,2,name="Erwin von Libwig")
		self.addCharacter(npc,1,3)
		npc.room = self
		npc.assignQuest(quest0)
		#npc.automated = False

		lever2 = self.lever2
		def lever2action(self):
			deactivateLeaverQuest = quests.ActivateQuest(lever2,desiredActive=False)
			npc.assignQuest(deactivateLeaverQuest,active=True)
		self.lever2.activateAction = lever2action

class TutorialMachineRoom(Room):
	def __init__(self,xPosition=0,yPosition=1,offsetX=4,offsetY=0):
		roomLayout = """
XXXX$XXXXX
X@ v vID#X
X@......#X
X@.8#OF. X
X@.##OF. X
XH.8#O . X
XH.|DI . X
XH......#X
XXRRR ID#X
XXXXXXXXXX
"""
		super().__init__(roomLayout)
		self.name = "Boilerroom"
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.xPosition = xPosition
		self.yPosition = yPosition

		self.lever1 = items.Lever(3,6,"engine control")
		self.lever2 = items.Lever(1,2,"boarding alarm")

		coalPile1 = items.Pile(8,3,"coal Pile1",items.Coal)
		coalPile2 = items.Pile(8,4,"coal Pile2",items.Coal)
		coalPile3 = items.Pile(8,5,"coal Pile3",items.Coal)
		coalPile4 = items.Pile(8,6,"coal Pile4",items.Coal)
		self.furnace = items.Furnace(6,5,"Furnace")

		self.addItems([self.lever1,self.lever2,coalPile1,coalPile2,coalPile3,coalPile4,self.furnace])

class Room3(Room):
	def __init__(self,xPosition=1,yPosition=0,offsetX=2,offsetY=2):
		self.roomLayout = """
XXXXXXXXXX
X????????X
X?......?X
X?.X#X?.?X
XP.?#??.?X
XP.X#X?.?X
X?.X#  .?X
X?......?X
X??v v???X
XXXX$XXXXX
"""
		super().__init__(self.roomLayout)
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.xPosition = xPosition
		self.yPosition = yPosition

class Room4(Room):
	def __init__(self):
		self.roomLayout = """
XX$XXXXXXX
Xv v?????X
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

class GenericRoom(Room):
	def __init__(self,xPosition,yPosition,offsetX,offsetY):
		self.roomLayout = """
XX$XXXXXXX
Xv v?????X
X?......PX
X?.????.PX
X?.????.#X
X?.???P.#X
X?.?X??.#X
X?......#X
X? XXXXX#X
XXXXXXXXXX
"""
		super().__init__(self.roomLayout)
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.xPosition = xPosition
		self.yPosition = yPosition

class CpuWasterRoom(Room):
	def __init__(self,xPosition,yPosition,offsetX,offsetY):
		self.roomLayout = """
XX$XXXXXXX
Xv v?????X
X?......PX
X?.PPPP.PX
X?.????.#X
X?.???P.#X
X?.?X??.#X
X?......#X
X? XXXXX#X
XXXXXXXXXX
"""
		super().__init__(self.roomLayout)
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.xPosition = xPosition
		self.yPosition = yPosition

		def addNPC(x,y):
			quest1 = quests.MoveQuest(self,2,2)
			quest2 = quests.MoveQuest(self,2,7)
			quest3 = quests.MoveQuest(self,7,7)
			quest4 = quests.MoveQuest(self,7,2)
			quest1.followUp = quest2
			quest2.followUp = quest3
			quest3.followUp = quest4
			quest4.followUp = quest1
			npc = Character("Ⓛ ",x,y,name="Erwin von Libwig")
			self.addCharacter(npc,x,y)
			npc.room = self
			npc.assignQuest(quest1)
			return npc

		addNPC(2,2)
		addNPC(3,2)
		addNPC(4,2)
		addNPC(5,2)
		addNPC(6,2)
		addNPC(7,2)
		addNPC(7,3)
		addNPC(7,4)
		addNPC(7,5)
		addNPC(7,6)
		
		class Event(object):
			def __init__(subself,tick):
				subself.tick = tick

			def handleEvent(subself):
				self.applySkippedAdvances()

class StorageRoom(Room):
	def __init__(self,xPosition,yPosition,offsetX,offsetY):
		self.roomLayout = """
XX&XX&XX&XX
X?....?? ?X
X?.??.?? ?X
X?.??.?? ?X
X?.??.?? ?X
X?....   ?X
X? ?? ?? ?X
X? ?? ?? ?X
X? ?v v? ?X
XX&XX$XX&XX
"""
		super().__init__(self.roomLayout)
		self.maxStorage = 2
		self.store = {}
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.xPosition = xPosition
		self.yPosition = yPosition

class InfanteryQuarters(Room):
	def __init__(self,xPosition,yPosition,offsetX,offsetY):
		self.roomLayout = """
XX$X&&XXXXX
XX PPPPPPXX
X .......DX
X'.'' ''.IX
X'.'' ''.|X
X'.'' ''.|X
X'.'' ''.IX
X .......DX
XXXXXXXXXXX
"""
		super().__init__(self.roomLayout)
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.xPosition = xPosition
		self.yPosition = yPosition
	
class FreePlacemenRoom(Room):
	def __init__(self):
		super().__init__(self.roomLayout)

class Vat1(Room):
	def __init__(self,xPosition,yPosition,offsetX,offsetY):
		self.roomLayout = """
XXXXXXXXXX
XababaabbX
XrqqrqqsaX
XzayzayzaX
XuwbuwxtbX
XabybayaaX
XpsaabbaiX
XmhmooooDX
Xmmmv.voIX
XXXXX$XXXX
"""
		self.roomLayout = """
XXXXXXXXXX
XaaaaaaaaX
XrqqrqqsaX
XzayzayzaX
XuwauwxtaX
XaayaayaaX
XpsBBBBBBX
Xmhm ...DX
Xmmmv.v.IX
XXXXX$XXXX
"""
		super().__init__(self.roomLayout)
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.xPosition = xPosition
		self.yPosition = yPosition

class Vat2(Room):
	def __init__(self,xPosition,yPosition,offsetX,offsetY):
		self.roomLayout = """
XXXXXXXXXX
X   b jjjX
X      b X
X b b b  X
X    c b X
X  b  j  X
X    b b X
X b    b X
##   .v ##
XXXXX$XXXX
"""
		super().__init__(self.roomLayout)
		self.floorDisplay = ["♒♒","≈≈","≈♒","♒≈","≈≈"]
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.xPosition = xPosition
		self.yPosition = yPosition

class MechArmor(Room):
	def __init__(self,xPosition,yPosition,offsetX,offsetY):
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
		super().__init__(self.roomLayout)
		self.floorDisplay = ["--"]
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.xPosition = xPosition
		self.yPosition = yPosition
