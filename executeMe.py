import urwid 
import items 
import quests
import rooms
import characters

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
rooms.calculatePath = calculatePath
quests.calculatePath = calculatePath
characters.calculatePath = calculatePath

rooms.Character = characters.Character
		
class GameState():
	def __init__(self,characters):
		self.characters = characters
		self.gameWon = False

messages = []
items.messages = messages
quests.messages = messages
rooms.messages = messages
characters.messages = messages

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

room1 = rooms.Room1()
room2 = rooms.Room2()
room1.hidden = True

roomsOnMap = [room1,room2]

tutorialQuest1 = quests.MoveQuest(room2,5,5,startCinematics="inside the Simulationchamber everything has to be taught from Scratch\n\nthe basic Movementcommands are:\n\n w=up\n a=right\n s=down\n d=right\n\nplease move to the designated Target. the Implant will mark your Way")
tutorialQuest2 = quests.CollectQuest(startCinematics="interaction with your Environment ist somewhat complicated\n\nthe basic Interationcommands are:\n\n j=activate/apply\n e=examine\n k=pick up\n\nsee this Piles of Coal marked with ӫ on the rigth Side of the room.\n\nplease grab yourself some Coal from a pile by moving onto it and pressing j.")
tutorialQuest3 = quests.ActivateQuest(room2.furnace,startCinematics="now go and activate the Furnace marked with a Ω. you need to have burnable Material like Coal in your Inventory\n\nso ensure that you have some Coal in your Inventory go to the Furnace and press j.")
tutorialQuest4 = quests.MoveQuest(room2,1,3,startCinematics="Move back to waiting position")
def tutorialQuest4Endtrigger():
	room1.openDoors()
	room2.openDoors()
	room1.hidden = False
tutorialQuest4.endTrigger = tutorialQuest4Endtrigger
tutorialQuest5 = quests.LeaveRoomQuest(room2,startCinematics="please exit the Room")
def tutorialQuest5Endtrigger():
	room1.closeDoors()
	room2.closeDoors()
tutorialQuest5.endTrigger = tutorialQuest5Endtrigger
tutorialQuest6 = quests.MoveQuest(room1,1,3,startCinematics="pleas move to waiting position")

tutorialQuest1.followUp = tutorialQuest2
tutorialQuest2.followUp = tutorialQuest3
tutorialQuest3.followUp = tutorialQuest4
tutorialQuest4.followUp = tutorialQuest5
tutorialQuest5.followUp = tutorialQuest6
tutorialQuest6.followUp = None

mainQuests = [tutorialQuest1]
mainChar = characters.Character("@",1,3,mainQuests,False,name="Sigmund Bärenstein")
mainChar.watched = True
rooms.mainChar = mainChar
room2.addCharacter(mainChar,1,3)

characters = [mainChar]
items.characters = characters
rooms.characters = characters

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
			foundItem = None
			for item in mainChar.room.itemsOnFloor:
				if item.xPosition == characters[0].xPosition and item.yPosition == characters[0].yPosition-1:
					foundItem = item
			if foundItem and not foundItem.walkable:
				messages.append("You cannot walk there")
				a = input()
				if a == 'j':
					foundItem.apply()
			else:
				characters[0].yPosition -= 1
				characters[0].changed()
		else:
			room2.removeCharacter(mainChar)
			room1.addCharacter(mainChar,4,9)
			characters[0].changed()
	if key in ('s'):
		if characters[0].yPosition < 9:
			foundItem = None
			for item in mainChar.room.itemsOnFloor:
				if item.xPosition == characters[0].xPosition and item.yPosition == characters[0].yPosition+1:
					foundItem = item
			if foundItem and not foundItem.walkable:
				messages.append("You cannot walk there")
				a = input()
				if a == 'j':
					foundItem.apply()
			else:
				characters[0].yPosition += 1
				characters[0].changed()
		else:
			room1.removeCharacter(mainChar)
			room2.addCharacter(mainChar,4,0)
			characters[0].changed()
	if key in ('d'):
		if characters[0].xPosition < 9:
			foundItem = None
			for item in mainChar.room.itemsOnFloor:
				if item.xPosition == characters[0].xPosition+1 and item.yPosition == characters[0].yPosition:
					foundItem = item
			if foundItem and not foundItem.walkable:
				messages.append("You cannot walk there")
				a = input()
				if a == 'j':
					foundItem.apply()
			else:
				characters[0].xPosition += 1
				characters[0].changed()
	if key in ('a'):
		if characters[0].xPosition:
			foundItem = None
			for item in mainChar.room.itemsOnFloor:
				if item.xPosition == characters[0].xPosition-1 and item.yPosition == characters[0].yPosition:
					foundItem = item
			if foundItem and not foundItem.walkable:
				messages.append("You cannot walk there")
				a = input()
				if a == 'j':
					foundItem.apply()
			else:
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
	for room in roomsOnMap:
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
	for room in roomsOnMap:
		if room.hidden:
			lineCounter += 15
			continue
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
