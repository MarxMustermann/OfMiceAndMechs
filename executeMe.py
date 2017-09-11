import urwid 
import items 
import quests
import rooms
import characters

header = urwid.Text(u"")
main = urwid.Text(u"＠")
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
			elif (diffX>0):
				startX -= 1
				diffX  -= 1
			elif (diffY<0):
				startY += 1
				diffY  += 1
			elif (diffY>0):
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
			loop.set_alarm_in(0.5, callShow_or_exit, '~')
		else:
			loop.set_alarm_in(0.05, callShow_or_exit, '~')
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

class Terrain(object):
	def __init__(self,rooms,layout):
		self.rooms = rooms
		self.layout = layout
		self.characters = []

	def render(self):
		chars = []
		for i in range(0,30):
			line = []
			for j in range(0,30):
				line.append("  ")
			chars.append(line)
				
		if not mapHidden:
			lineCounter = 0
			for layoutline in terrain.layout.split("\n")[1:]:
				rowCounter = 0
				for char in layoutline:
					if char == "X":
						chars[lineCounter][rowCounter] = "⛝ "
					if char == "0":
						chars[lineCounter][rowCounter] = "✠✠"
					if char == ".":
						chars[lineCounter][rowCounter] = "⛚ "
					rowCounter += 1
				lineCounter += 1
		

		for room in terrain.rooms:
			if mapHidden and room.hidden:
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

		for character in self.characters:
			chars[character.yPosition][character.xPosition] = character.display

			if character == mainChar:
				if len(characters[0].quests):
                                        try:
                                                chars[characters[0].quests[0].dstY][characters[0].quests[0].dstX] = "xX"

                                                path = calculatePath(characters[0].xPosition,characters[0].yPosition,characters[0].quests[0].dstX,characters[0].quests[0].dstY)
                                                for item in path:
                                                        chars[item[1]][item[0]] = "xx"
                                        except:
                                                pass


		return chars

class Terrain1(Terrain):
	def __init__(self,rooms):
		layout = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X0000000000000XX000000000000 X
X0           0XX0          0 X
X0           0XX0          0 X
X0           0XX0          0 X
X0           0XX0          0 X
X0           0XX0          0 X
X0           0XX0          0 X
X0           0XX0          0 X
X0           0XX0          0 X
X0           0XX0          0 X
X0XXXXXXXXXXX0XX0XXXXXXXXXX0XX
X0...........0000..........000
X0............................ 
X0..........................00
X0XXXXXXXXXXXXX XXX.XXXXXXXX0X
X0           0X X X.X       0X
X0           0X X XXX       0X
X0           0X X           0X
X0           0X X           0X
X0           0X X           0X
X0           0X X           0X
X0           0X X           0X
X0           0X X           0X
X0           0X X           0X
X000000000   0X X           0X
X            0X X           0X
00000000000000000000000000000X
XXXXXXXXXXXX0XX XXXXXXXXXXXXXX
"""
		super().__init__(rooms,layout)

room1 = rooms.Room1()
#room1.hidden = True
room2 = rooms.Room2()
room3 = rooms.Room3()
#room3.hidden = True
room4 = rooms.Room4()
#room4.hidden = True
#room1.hidden = True

roomsOnMap = [room1,room2,room3,room4]
characters.roomsOnMap = roomsOnMap

terrain = Terrain1(roomsOnMap)

mapHidden = True

tutorialQuest1 = quests.MoveQuest(room2,5,5,startCinematics="inside the Simulationchamber everything has to be taught from Scratch\n\nthe basic Movementcommands are:\n\n w=up\n a=right\n s=down\n d=right\n\nplease move to the designated Target. the Implant will mark your Way")
tutorialQuest2 = quests.CollectQuest(startCinematics="interaction with your Environment ist somewhat complicated\n\nthe basic Interationcommands are:\n\n j=activate/apply\n e=examine\n k=pick up\n\nsee this Piles of Coal marked with ӫ on the rigth Side of the room.\n\nplease grab yourself some Coal from a pile by moving onto it and pressing j.")
tutorialQuest3 = quests.ActivateQuest(room2.furnace,startCinematics="now go and activate the Furnace marked with a Ω. you need to have burnable Material like Coal in your Inventory\n\nso ensure that you have some Coal in your Inventory go to the Furnace and press j.")
tutorialQuest4 = quests.MoveQuest(room2,1,3,startCinematics="Move back to waiting position")
def tutorialQuest4Endtrigger():
	room1.openDoors()
	room2.openDoors()
	#room1.hidden = False
	global mapHidden
	mapHidden = False
tutorialQuest4.endTrigger = tutorialQuest4Endtrigger
tutorialQuest5 = quests.LeaveRoomQuest(room2,startCinematics="please exit the Room")
def tutorialQuest5Endtrigger():
	room1.closeDoors()
	room2.closeDoors()
	#room2.hidden = True
	global mapHidden
	mapHidden = True
tutorialQuest5.endTrigger = tutorialQuest5Endtrigger
tutorialQuest6 = quests.MoveQuest(room1,1,3,startCinematics="please move to waiting position")

tutorialQuest1.followUp = tutorialQuest2
tutorialQuest2.followUp = tutorialQuest3
tutorialQuest3.followUp = tutorialQuest4
tutorialQuest4.followUp = tutorialQuest5
tutorialQuest5.followUp = tutorialQuest6
tutorialQuest6.followUp = None

mainQuests = [tutorialQuest1]
mainChar = characters.Character("＠",1,3,automated=False,name="Sigmund Bärenstein")
mainChar.watched = True
rooms.mainChar = mainChar
room2.addCharacter(mainChar,1,3)
mainChar.assignQuest(tutorialQuest1)

quest0 = quests.MoveQuest(room2,5,5)
def quest0Endtrigger():
	room1.openDoors()
	room2.openDoors()
	global mapHidden
	mapHidden = False
quest0.endTrigger = quest0Endtrigger
quest1 = quests.LeaveRoomQuest(room2)
def quest1Endtrigger():
	room1.closeDoors()
	room2.closeDoors()
	global mapHidden
	mapHidden = True
quest1.endTrigger = quest1Endtrigger
quest2 = quests.MoveQuest(room1,5,5)
def quest2Endtrigger():
	room1.openDoors()
	room2.openDoors()
	global mapHidden
	mapHidden = False
quest2.endTrigger = quest2Endtrigger
quest3 = quests.LeaveRoomQuest(room1)
def quest3Endtrigger():
	room1.closeDoors()
	room2.closeDoors()
	global mapHidden
	mapHidden = True
quest3.endTrigger = quest3Endtrigger
quest0.followUp = quest1
quest1.followUp = quest2
quest2.followUp = quest3
quest3.followUp = quest0
npc2 = characters.Character("⒬ ",1,1,name="Ernst Ziegelbach")
room2.addCharacter(npc2,1,1)
npc2.assignQuest(quest0)

characters = [mainChar]
items.characters = characters
rooms.characters = characters

gamestate = GameState(characters)

def callShow_or_exit(loop,key):
	show_or_exit(key)

itemMarkedLast = None
def show_or_exit(key):
	if not len(key) == 1:
		return
	global cinematicQueue
	global itemMarkedLast
	stop = False
	if len(cinematicQueue):
		if key in ('q', 'Q'):
			raise urwid.ExitMainLoop()
		elif key in (' '):
			cinematicQueue = cinematicQueue[1:]
			loop.set_alarm_in(0.0, callShow_or_exit, '~')
		else:
			stop = True
			cinematicQueue[0].advance()
	if stop:
		return
	if key in ('~'):
		return

	if key in ('q', 'Q'):
		raise urwid.ExitMainLoop()
	if key in ('w'):
		if mainChar.room:
			if characters[0].yPosition:
				foundItem = None
				for item in mainChar.room.itemsOnFloor:
					if item.xPosition == characters[0].xPosition and item.yPosition == characters[0].yPosition-1:
						foundItem = item
				if foundItem and not foundItem.walkable:
					messages.append("You cannot walk there")
					messages.append("press j to apply")
					itemMarkedLast = foundItem
					footer.set_text(renderMessagebox())
					return
				else:
					characters[0].yPosition -= 1
					characters[0].changed()
			else:
				newYPos = characters[0].yPosition+mainChar.room.yPosition*15+mainChar.room.offsetY-1
				newXPos = characters[0].xPosition+mainChar.room.xPosition*15+mainChar.room.offsetX
				mainChar.xPosition = newXPos
				mainChar.yPosition = newYPos
				mainChar.room.removeCharacter(mainChar)
				terrain.characters.append(mainChar)
				#room1.hidden = False
				#room2.hidden = True
				characters[0].changed()
		else:
			for room in terrain.rooms:
				if room.yPosition*15+room.offsetY+10 == mainChar.yPosition:
					if room.xPosition*15+room.offsetX < mainChar.xPosition and room.xPosition*15+room.offsetX+10 > mainChar.xPosition:
						localisedEntry = (mainChar.xPosition%15-room.offsetX,mainChar.yPosition%15-room.offsetY-1)
						if localisedEntry in room.walkingAccess:
							messages.append(str(room))
							room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1]+1)
							terrain.characters.remove(mainChar)
			characters[0].yPosition -= 1
			characters[0].changed()

	if key in ('s'):
		if mainChar.room:
			if characters[0].yPosition < 9:
				foundItem = None
				for item in mainChar.room.itemsOnFloor:
					if item.xPosition == characters[0].xPosition and item.yPosition == characters[0].yPosition+1:
						foundItem = item
				if foundItem and not foundItem.walkable:
					messages.append("You cannot walk there")
					messages.append("press j to apply")
					itemMarkedLast = foundItem
					footer.set_text(renderMessagebox())
					return
				else:
					characters[0].yPosition += 1
					characters[0].changed()
			else:
				newYPos = characters[0].yPosition+mainChar.room.yPosition*15+mainChar.room.offsetY+1
				newXPos = characters[0].xPosition+mainChar.room.xPosition*15+mainChar.room.offsetX
				mainChar.xPosition = newXPos
				mainChar.yPosition = newYPos
				mainChar.room.removeCharacter(mainChar)
				terrain.characters.append(mainChar)
				#room2.hidden = False
				#room1.hidden = True
				characters[0].changed()
		else:
			for room in terrain.rooms:
				if room.yPosition*15+room.offsetY == mainChar.yPosition+1:
					if room.xPosition*15+room.offsetX < mainChar.xPosition and room.xPosition*15+room.offsetX+10 > mainChar.xPosition:
						localisedEntry = ((mainChar.xPosition-room.offsetX)%15,(mainChar.yPosition-room.offsetY+1)%15)
						if localisedEntry in room.walkingAccess:
							room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1]-1)
							terrain.characters.remove(mainChar)
			characters[0].yPosition += 1
			characters[0].changed()

	if key in ('d'):
		if mainChar.room:
			if characters[0].xPosition < 9:
				foundItem = None
				if mainChar.room:
					for item in mainChar.room.itemsOnFloor:
						if item.xPosition == characters[0].xPosition+1 and item.yPosition == characters[0].yPosition:
							foundItem = item
				if foundItem and not foundItem.walkable:
					messages.append("You cannot walk there")
					messages.append("press j to apply")
					itemMarkedLast = foundItem
					footer.set_text(renderMessagebox())
					return
				else:
					characters[0].xPosition += 1
					characters[0].changed()
		else:
			characters[0].xPosition += 1
			characters[0].changed()
	if key in ('a'):
		if mainChar.room:
			if characters[0].xPosition:
				foundItem = None
				if mainChar.room:
					for item in mainChar.room.itemsOnFloor:
						if item.xPosition == characters[0].xPosition-1 and item.yPosition == characters[0].yPosition:
							foundItem = item
				if foundItem and not foundItem.walkable:
					messages.append("You cannot walk there")
					messages.append("press j to apply")
					itemMarkedLast = foundItem
					footer.set_text(renderMessagebox())
					return
				else:
					characters[0].xPosition -= 1
					characters[0].changed()
		else:
			characters[0].xPosition -= 1
			characters[0].changed()
	if key in ('j'):
		if itemMarkedLast:
			itemMarkedLast.apply()
		else:
			if mainChar.room:
				for item in mainChar.room.itemsOnFloor:
					if item.xPosition == characters[0].xPosition and item.yPosition == characters[0].yPosition:
						item.apply()
	if key in ('l'):
		if len(characters[0].inventory):
			item = characters[0].inventory.pop()	
			item.xPosition = characters[0].xPosition		
			item.yPosition = characters[0].yPosition		
			characters[0].room.itemsOnFloor.append(item)
			item.changed()
	if key in ('h'):
		messages.append(characters[0].name+": HÜ!")
		messages.append(characters[0].name+": HOTT!")
	if key in ('k'):
		for item in characters[0].room.itemsOnFloor:
			if item.xPosition == characters[0].xPosition and item.yPosition == characters[0].yPosition:
				characters[0].room.itemsOnFloor.remove(item)
				if hasattr(item,"xPosition"):
					del item.xPosition
				if hasattr(item,"yPosition"):
					del item.yPosition
				characters[0].inventory.append(item)
				item.changed()

	itemMarkedLast = None
		
	if not gamestate.gameWon:
		advanceGame()

		header.set_text(renderQuests())
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

def renderQuests():
	txt = ""
	if len(characters[0].quests):
		"""
		txt += "QUEST: "+characters[0].quests[0].description+"\n"
		try:
			txt += "QUEST: "+characters[0].quests[1].description+"\n"
		except:
			txt += "\n"
		"""
		for quest in mainChar.quests:
			txt+= "QUEST: "+quest.description+"\n"
	else:
		txt += "QUEST: keinQuest\n\n"
		gamestate.gameWon = True
		loop.set_alarm_in(0.0, callShow_or_exit, '~')
	return txt
	
def renderMessagebox():
	txt = ""
	for message in messages[-5:]:
		txt += message+"\n"
	return txt

def render():
	chars = terrain.render()

	result = ""
	for line in chars:
		lineRender = ""
		for char in line:
			lineRender += char
		lineRender += "\n"
		result += lineRender
		
	return result

frame = urwid.Frame(urwid.Filler(main,"top"),header=header,footer=footer)
loop = urwid.MainLoop(frame, unhandled_input=show_or_exit)
loop.set_alarm_in(0.0, callShow_or_exit, '~')
loop.run()
