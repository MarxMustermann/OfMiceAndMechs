import urwid 
import items 
import quests

header = urwid.Text(u"")
main = urwid.Text(u"@")
footer = urwid.Text(u"")
cinematicQueue = []

def calculatePath(startX,startY,endX,endY):
	diffX = startX-endX
	diffY = startY-endY

	import math
	path = []
	while (not diffX == 0) or (not diffY == 0):
			if (diffX<0):
				startX += 1
				diffX  += 1
			if (diffX>0):
				startX -= 1
				diffX  -= 1
			if (diffY<0):
				startY += 1
				diffY  += 1
			if (diffY>0):
				startY -= 1
				diffY  -= 1
			path.append((startX,startY))

			"""
			if math.abs(diffX) > math.abs(diffY):
				if (diffX<1):
					endX-1
					diffX+1
				else:
					endX+1
					diffX-1
				if (diffY<1):
					endY-1
					diffY+1
				else:
					endY+1
					diffY-1
				path.append((startX,startY))
			"""
	return path

class Room(object):
	def __init__(self,layout):
		self.layout = layout
		self.itemsOnFloor = []
		self.characters = []

		self.walkingAccess = []

		lineCounter = 0
		for line in self.layout[1:].split("\n"):
			rowCounter = 0
			for char in line:
				if char == "X":
					self.itemsOnFloor.append(items.Wall(rowCounter,lineCounter))
				if char == "$":
					self.itemsOnFloor.append(items.Door(rowCounter,lineCounter))
					self.walkingAccess.append((rowCounter,lineCounter))
				rowCounter += 1
			lineCounter += 1


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
			messages.append("Bitte unterlassen Sie das anschalten des Alarms!")
			deactivateLeaverQuest = ActivateQuest(lever2,desiredActive=False)
			npc.assignQuest(deactivateLeaverQuest,active=True)
		self.lever2.activateAction = lever2action

		npc2 = Character("Ü",1,1,name="Ernst Ziegelbach")

		self.addCharacter(npc,2,1)
		self.addCharacter(npc2,1,1)

class Character():
	def __init__(self,display="@",xPosition=0,yPosition=0,quests=[],automated=True,name="Person"):
		self.display = display
		self.xPosition = xPosition
		self.yPosition = yPosition
		self.automated = automated
		self.quests = []
		self.name = name
		self.inventory = []
		self.watched = False
		self.listeners = []
		self.room = None
		
		for quest in quests:
			self.assignQuest(quest)

	def startNextQuest(self):
		if len(self.quests):
			self.setPathToQuest(self.quests[0])

	def assignQuest(self,quest,active=False):
			quest.activate()
			if active:
				self.quests.insert(0,quest)
			else:
				self.quests.append(quest)
			quest.assignToCharacter(self)
			if self.automated and (active or len(self.quests) == 1):
				try:
					self.setPathToQuest(quest)
				except:
					pass

			if self.watched:
				messages.append(self.name+": got a new Quest\n - "+quest.description)

	def setPathToQuest(self,quest):
		self.path = calculatePath(self.xPosition,self.yPosition,quest.dstX,quest.dstY)

	def addToInventory(self,item):
		self.inventory.append(item)

	def advance(self):
		if self.automated:
			if hasattr(self,"path") and len(self.path):
				self.xPosition = self.path[0][0]
				self.yPosition = self.path[0][1]
				self.path = self.path[1:]
			try:
				if not len(self.path):
					self.quests[0].toActivate.apply()
			except:
				pass
			self.changed()

	def addListener(self,listenFunction):
		if not listenFunction in self.listeners:
			self.listeners.append(listenFunction)

	def delListener(self,listenFunction):
		if listenFunction in self.listeners:
			self.listeners.remove(listenFunction)

	def changed(self):
		for listenFunction in self.listeners:
			listenFunction()
		
class GameState():
	def __init__(self,characters):
		self.characters = characters
		self.gameWon = False

messages = []
items.messages = messages
quests.messages = messages

class Cinematic(object):
	def __init__(self,text):
		self.text = text+"\n\n-- press space to proceed -- "
		self.position = 0
		self.endPosition = len(self.text)

	def advance(self):
		if self.position >= self.endPosition:
			return

		main.set_text(self.text[0:self.position])
		if self.text[self.position] in ("\n"):
			loop.set_alarm_in(0.5, callShow_or_exit, '.')
		else:
			loop.set_alarm_in(0.05, callShow_or_exit, '.')
		self.position += 1

def showCinematic(text):
	cinematicQueue.append(Cinematic(text))
quests.showCinematic = showCinematic

showCinematic("welcome to the Trainingenvironment\n\nplease, try to learn fast.\n\nParticipants with low Evaluationscores will be given suitable Assignments in the Vats")

itemsOnFloor = []

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
"""
roomLayout = """
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
"""
roomLayout = """
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
"""
roomLayout = """
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
roomLayout2 = """
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
"""
lineCounter = 0
for line in roomLayout[1:].split("\n"):
	rowCounter = 0
	for char in line:
		if char == "X":
			itemsOnFloor.append(items.Wall(rowCounter,lineCounter,"Wall"))
		rowCounter += 1
	lineCounter += 1

room1 = Room1()
room2 = Room2()

rooms = [room1,room2]

tutorialQuest1 = quests.MoveQuest(room2,5,5,startCinematics="inside the Simulationchamber everything has to be taught from Scratch\n\nthe basic Movementcommands are:\n\n w=up\n a=right\n s=down\n d=right\n\nplease move to the designated Target. the Implant will mark your Way")
tutorialQuest2 = quests.CollectQuest(startCinematics="interaction with your Environment ist somewhat complicated\n\nthe basic Interationcommands are:\n\n j=activate/apply\n e=examine\n k=pick up\n\nsee this Piles of Coal marked with ӫ on the rigth Side of the room.\n\nplease grab yourself some Coal from a pile by moving onto it and pressing j.")
tutorialQuest3 = quests.ActivateQuest(room2.furnace,startCinematics="now go and activate the Furnace marked with a Ω. you need to have burnable Material like Coal in your Inventory\n\nso ensure that you have some Coal in your Inventory go to the Furnace and press j.")
tutorialQuest4 = quests.MoveQuest(room2,1,3,startCinematics="Move back to waiting position")
tutorialQuest5 = quests.LeaveRoomQuest(room2,startCinematics="please exit the Room")

tutorialQuest1.followUp = tutorialQuest2
tutorialQuest2.followUp = tutorialQuest3
tutorialQuest3.followUp = tutorialQuest4
tutorialQuest4.followUp = tutorialQuest5
tutorialQuest5.followUp = None

mainQuests = [tutorialQuest1]
mainChar = Character("@",1,3,mainQuests,False,name="Sigmund Bärenstein")
mainChar.watched = True
room2.addCharacter(mainChar,1,3)

characters = [mainChar]
items.characters = characters

gamestate = GameState(characters)

def callShow_or_exit(loop,key):
	show_or_exit(key)

def show_or_exit(key):
	if not len(key) == 1:
		return
	global cinematicQueue
	stop = False
	if len(cinematicQueue):
		if key in ('q', 'Q'):
			raise urwid.ExitMainLoop()
		elif key in (' '):
			cinematicQueue = cinematicQueue[1:]
			loop.set_alarm_in(0.0, callShow_or_exit, '.')
		else:
			stop = True
			cinematicQueue[0].advance()
	if stop:
		return

	if key in ('q', 'Q'):
		raise urwid.ExitMainLoop()
	if key in ('w'):
		if characters[0].yPosition:
			characters[0].yPosition -= 1
		else:
			room2.removeCharacter(mainChar)
			room1.addCharacter(mainChar,4,9)
		characters[0].changed()
	if key in ('s'):
		if characters[0].yPosition < 9:
			characters[0].yPosition += 1
		else:
			room1.removeCharacter(mainChar)
			room2.addCharacter(mainChar,4,0)
		characters[0].changed()
	if key in ('d'):
		characters[0].xPosition += 1
		characters[0].changed()
	if key in ('a'):
		if characters[0].xPosition:
			characters[0].xPosition -= 1
		characters[0].changed()
	if key in ('j'):
		for item in mainChar.room.itemsOnFloor:
			if item.xPosition == characters[0].xPosition and item.yPosition == characters[0].yPosition:
				item.apply()
	if key in ('l'):
		if len(characters[0].inventory):
			item = characters[0].inventory.pop()	
			item.xPosition = characters[0].xPosition		
			item.yPosition = characters[0].yPosition		
			itemsOnFloor.append(item)
			item.changed()
	if key in ('h'):
		messages.append(characters[0].name+": HÜ!")
		messages.append(characters[0].name+": HOTT!")
	if key in ('k'):
		for item in itemsOnFloor:
			if item.xPosition == characters[0].xPosition and item.yPosition == characters[0].yPosition:
				itemsOnFloor.remove(item)
				if hasattr(item,"xPosition"):
					del item.xPosition
				if hasattr(item,"yPosition"):
					del item.yPosition
				characters[0].inventory.append(item)
				item.changed()
		
	if not gamestate.gameWon:
		if len(characters[0].quests):
			header.set_text("QUEST: "+characters[0].quests[0].description)
		else:
			header.set_text("QUEST: keinQuest")
			gamestate.gameWon = True

		advanceGame()

		main.set_text(render());
		footer.set_text(renderMessagebox())
	else:
		main.set_text("")
		footer.set_text("good job")


def advanceGame():
	for character in characters:
		character.advance()
	for room in rooms:
		for character in room.characters:
			character.advance()

def renderMessagebox():
	txt = ""
	for message in messages[-5:]:
		txt += message+"\n"
	return txt

def render():
	layout = """
XXXXXXXXXXXXXXX
X             X
X             X
X             X
X             X
X             X
X             X
X             X
X             X
X             X
X             X
XXXXXXXXXXXXXXX
X             X
X             X
X             X
XXXXXXXXXXXXXXX
X             X
X             X
X             X
X             X
X             X
X             X
X             X
X             X
X             X
X             X
X             X
X             X
XXXXXXXXXXXXXXX
"""
	result = ""

	layoutByLine = layout.split("\n")[1:]

	lineCounter = 0
	for room in rooms:
		for i in range(0,room.offsetY):
			result += layoutByLine[lineCounter]+"\n"
			lineCounter += 1
		for line in room.render().split("\n"):
			result += layoutByLine[lineCounter][:room.offsetX]+line+layoutByLine[lineCounter][(10+room.offsetX):]+"\n"
			lineCounter += 1
		for i in range(room.offsetY,5):
			result += layoutByLine[lineCounter]+"\n"
			lineCounter += 1

	return result

frame = urwid.Frame(urwid.Filler(main,"top"),header=header,footer=footer)
loop = urwid.MainLoop(frame, unhandled_input=show_or_exit)
loop.set_alarm_in(0.0, callShow_or_exit, '.')
loop.run()
