import urwid 
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
					self.itemsOnFloor.append(Wall(rowCounter,lineCounter))
				if char == "$":
					self.itemsOnFloor.append(Door(rowCounter,lineCounter))
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
		self.offsetX = 2
		self.offsetY = 2
		super().__init__(self.roomLayout)

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
		self.offsetX = 4
		self.offsetY = 0

		super().__init__(self.roomLayout)

		self.lever1 = Lever(3,6,"engine control")
		self.lever2 = Lever(1,2,"boarding alarm")

		def lever2action(self):
			messages.append("Bitte unterlassen Sie das anschalten des Alarms!")
			deactivateLeaverQuest = ActivateQuest(self.lever2,desiredActive=False)
			characters[1].assignQuest(deactivateLeaverQuest,active=True)

		self.lever2.activateAction = lever2action

		coalPile1 = Pile(8,3,"coal Pile1",Coal)
		coalPile2 = Pile(8,4,"coal Pile2",Coal)
		coalPile3 = Pile(8,5,"coal Pile3",Coal)
		coalPile4 = Pile(8,6,"coal Pile4",Coal)
		self.furnace = Furnace(6,6,"Furnace")
		furnaceDisplay = Display(8,8,"Furnace monitoring")

		self.itemsOnFloor.extend([self.lever1,self.lever2,coalPile1,coalPile2,coalPile3,coalPile4,self.furnace,furnaceDisplay])

		quest0 = ActivateQuest(self.lever1)
		quest1 = MoveQuest(2,2)
		quest2 = MoveQuest(2,7)
		quest3 = MoveQuest(7,7)
		quest4 = MoveQuest(7,2)
		quest0.followUp = quest1
		quest1.followUp = quest2
		quest2.followUp = quest3
		quest3.followUp = quest4
		quest4.followUp = quest1
		npcQuests = [quest0]
		npc = Character("Ö",2,1,npcQuests,name="Erwin von Libwig")
		npc.watched = True

		npc2 = Character("Ü",1,1,name="Ernst Ziegelbach")

		self.addCharacter(npc,2,1)
		self.addCharacter(npc2,1,1)

class Item(object):
	def __init__(self,display="§",xPosition=0,yPosition=0):
		self.display = display
		self.xPosition = xPosition
		self.yPosition = yPosition
		self.listeners = []

	def apply(self):
		messages.append("i can't do anything useful with this")

	def changed(self):
		messages.append(self.name+": Object changed")
		for listener in self.listeners:
			listener()

	def addListener(self,listenFunction):
		if not listenFunction in self.listeners:
			self.listeners.append(listenFunction)

	def delListener(self,listenFunction):
		if listenFunction in self.listeners:
			self.listeners.remove(listenFunction)

class Lever(Item):
	def __init__(self,xPosition=0,yPosition=0,name="lever",activated=False):
		self.activated = activated
		self.display = {True:"/",False:"|"}
		self.name = name
		super().__init__("|",xPosition,yPosition)
		self.activateAction = None
		self.deactivateAction = None

	def apply(self):
		if not self.activated:
			self.activated = True
			self.display = "/"
			messages.append(self.name+": activated!")

			if self.activateAction:
				self.activateAction(self)
		else:
			self.activated = False
			self.display = "|"
			messages.append(self.name+": deactivated!")

			if self.deactivateAction:
				self.activateAction(self)
		self.changed()

class Furnace(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Furnace"):
		self.name = name
		self.activated = False
		super().__init__("Ω",xPosition,yPosition)

	def apply(self):
		messages.append("Furnace used")
		foundItem = None
		for item in characters[0].inventory:
			try:
				canBurn = item.canBurn
			except:
				continue
			if not canBurn:
				continue

			foundItem = item

		if not foundItem:
			messages.append("keine KOHLE zum anfeuern")
		else:
			self.activated = True
			self.display = "ϴ"
			characters[0].inventory.remove(foundItem)
			messages.append("burn it ALL")
		self.changed()

class Display(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Display"):
		self.name = name
		super().__init__("ߐ",xPosition,yPosition)

class Wall(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Wall"):
		self.name = name
		super().__init__("X",xPosition,yPosition)

class Coal(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Coal"):
		self.name = name
		self.canBurn = True
		super().__init__("*",xPosition,yPosition)

class Door(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Door"):
		self.name = name
		super().__init__("$",xPosition,yPosition)

class Pile(Item):
	def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal):
		self.name = name
		self.canBurn = True
		self.type = itemType
		super().__init__("ӫ",xPosition,yPosition)

	def apply(self):
		messages.append("Pile used")
		characters[0].inventory.append(self.type())
		characters[0].changed()

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
		

class Quest(object):
	def __init__(self,followUp=None,startCinematics=None):
		self.followUp = followUp
		self.character = None
		self.listener = []
		self.active = False
		self.startCinematics=startCinematics

	def triggerCompletionCheck(self):
		if not self.active:
			return 
		pass
	
	def postHandler(self):
		self.character.quests.remove(self)
		if self.followUp:
			self.character.assignQuest(self.followUp,active=True)
		else:
			self.character.startNextQuest()

		if self.character.watched:
			messages.append("Thank you kindly. @"+self.character.name)
		
		self.deactivate()

	def assignToCharacter(self,character):
		self.character = character
		self.recalculate()

	def recalculate(self):
		self.triggerCompletionCheck()

	def changed(self):
		messages.append("QUEST: "+self.description+" changed")

	def addListener(self,listenFunction):
		if not listenFunction in self.listener:
			self.listener.append(listenFunction)

	def delListener(self,listenFunction):
		if listenFunction in self.listener:
			self.listener.remove(listenFunction)

	def activate(self):
		self.active = True
		if self.startCinematics:
			showCinematic(self.startCinematics)			
			try:
				loop.set_alarm_in(0.0, callShow_or_exit, '.')
			except:
				pass

	def deactivate(self):
		self.active = False

class CollectQuest(Quest):
	def __init__(self,toFind="canBurn",startCinematics=None):
		self.toFind = toFind
		self.description = "please fetch things with property: "+toFind
		
		foundItem = None

		super().__init__(startCinematics=startCinematics)

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		foundItem = None
		for item in self.character.inventory:
			hasProperty = False
			try:
				hasProperty = getattr(item,self.toFind)
			except:
				continue
			
			if hasProperty:
				foundItem = item
				break

		if foundItem:
			self.postHandler()
			pass

	def assignToCharacter(self,character):
		super().assignToCharacter(character)
		character.addListener(self.recalculate)

	def recalculate(self):
		for item in self.character.room.itemsOnFloor:
			hasProperty = False
			try:
				hasProperty = getattr(item,self.toFind)
			except:
				continue
			
			if hasProperty:
				foundItem = item
				break

		if foundItem:
			self.dstX = foundItem.xPosition
			self.dstY = foundItem.yPosition
		super().recalculate()

class ActivateQuest(Quest):
	def __init__(self,toActivate,followUp=None,desiredActive=True,startCinematics=None):
		self.toActivate = toActivate
		self.toActivate.addListener(self.recalculate)
		self.description = "please activate the "+self.toActivate.name+" ("+str(self.toActivate.xPosition)+"/"+str(self.toActivate.yPosition)+")"
		self.dstX = self.toActivate.xPosition
		self.dstY = self.toActivate.yPosition
		self.desiredActive = desiredActive
		super().__init__(followUp,startCinematics=startCinematics)

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		if self.toActivate.activated == self.desiredActive:
			self.postHandler()

	def recalculate(self):
		if hasattr(self,"dstX"):
			del self.dstX
		if hasattr(self,"dstY"):
			del self.dstY
		if hasattr(self,"toActivate"):
			if hasattr(self.toActivate,"xPosition"):
				self.dstX = self.toActivate.xPosition
			if hasattr(self.toActivate,"xPosition"):
				self.dstY = self.toActivate.yPosition
		super().recalculate()

class MoveQuest(Quest):
	def __init__(self,x,y,followUp=None,startCinematics=None):
		self.dstX = x
		self.dstY = y
		self.description = "please go to coordinate "+str(self.dstX)+"/"+str(self.dstY)	
		super().__init__(followUp,startCinematics=startCinematics)

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		if self.character.xPosition == self.dstX and self.character.yPosition == self.dstY:
			self.postHandler()

	def assignToCharacter(self,character):
		super().assignToCharacter(character)
		character.addListener(self.recalculate)

class MoveToExit(MoveQuest):
	def __init__(self,room,startCinematics=None):
		super().__init__(room.walkingAccess[0][0],room.walkingAccess[0][1],startCinematics=startCinematics)

class GameState():
	def __init__(self,characters):
		self.characters = characters
		self.gameWon = False

messages = []



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
			itemsOnFloor.append(Wall(rowCounter,lineCounter,"Wall"))
		rowCounter += 1
	lineCounter += 1

room1 = Room1()
room2 = Room2()

rooms = [room1,room2]

tutorialQuest1 = MoveQuest(5,5,startCinematics="inside the Simulationchamber everything has to be taught from Scratch\n\nthe basic Movementcommands are:\n\n w=up\n a=right\n s=down\n d=right\n\nplease move to the designated Target. the Implant will mark your Way")
tutorialQuest2 = CollectQuest(startCinematics="interaction with your Environment ist somewhat complicated\n\nthe basic Interationcommands are:\n\n j=activate/apply\n e=examine\n k=pick up\n\nsee this Piles of Coal marked with ӫ on the rigth Side of the room.\n\nplease grab yourself some Coal from a pile by moving onto it and pressing j.")
tutorialQuest3 = ActivateQuest(room2.furnace,startCinematics="now go and activate the Furnace marked with a Ω. you need to have burnable Material like Coal in your Inventory\n\nso ensure that you have some Coal in your Inventory go to the Furnace and press j.")
tutorialQuest4 = MoveQuest(1,3,startCinematics="Move back to waiting position")
tutorialQuest5 = MoveToExit(room2,startCinematics="please exit the Room")

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
			room1.addCharacter(mainChar,4,9)
			room2.removeCharacter(mainChar)
		characters[0].changed()
	if key in ('s'):
		if characters[0].yPosition < 9:
			characters[0].yPosition += 1
		else:
			room2.addCharacter(mainChar,4,0)
			room1.removeCharacter(mainChar)
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
		for line in room.render().split("\n"):
			result += line+layoutByLine[lineCounter][10:]+"\n"
			lineCounter += 1
		for i in range(0,5):
			result += layoutByLine[lineCounter]+"\n"
			lineCounter += 1

	return result

frame = urwid.Frame(urwid.Filler(main,"top"),header=header,footer=footer)
loop = urwid.MainLoop(frame, unhandled_input=show_or_exit)
loop.set_alarm_in(0.0, callShow_or_exit, '.')
loop.run()
