import urwid 
import sys

import src.items as items
import src.quests as quests
import src.rooms as rooms
import src.characters as characters
import src.terrains as terrains
import src.cinematics as cinematics
import config.commandChars as commandChars

#import sys, pygame
#pygame.init()
#pygame.mixer.music.load("music/chutulu.mp3")
#pygame.mixer.music.play()

if len(sys.argv) > 1:
	import config.displayChars_fallback as displayChars
else:
	import config.displayChars as displayChars

header = urwid.Text(u"")
main = urwid.Text(displayChars.main_char)
main.set_layout('left', 'clip')
cinematics.main = main
footer = urwid.Text(u"")

cinematics.quests = quests

items.displayChars = displayChars
rooms.displayChars = displayChars
terrains.displayChars = displayChars

items.commandChars = commandChars

def callShow_or_exit(loop,key):
	show_or_exit(key)

itemMarkedLast = None
lastMoveAutomated = False
fullAutoMode = False

stealKey = {}
items.stealKey = stealKey

def show_or_exit(key):
	if not len(key) == 1:
		return

	if key in (commandChars.autoAdvance):
		loop.set_alarm_in(0.2, callShow_or_exit, commandChars.autoAdvance)

	global itemMarkedLast
	global lastMoveAutomated
	stop = False
	doAdvanceGame = True
	if len(cinematics.cinematicQueue):
		if key in (commandChars.quit_normal, commandChars.quit_instant):
			raise urwid.ExitMainLoop()
		elif key in (commandChars.pause,commandChars.advance,commandChars.autoAdvance):
			cinematics.cinematicQueue[0].abort()
			cinematics.cinematicQueue = cinematics.cinematicQueue[1:]
			loop.set_alarm_in(0.0, callShow_or_exit, commandChars.ignore)
			return
		else:
			if not cinematics.cinematicQueue[0].advance():
				return
			key = commandChars.ignore
	if key in (commandChars.ignore):
		doAdvanceGame = False

	if key in stealKey:
		stealKey[key]()
	else:
		if key in (commandChars.quit_normal, commandChars.quit_instant):
			raise urwid.ExitMainLoop()
		if key in (commandChars.move_north):
			if mainChar.room:
				item = mainChar.room.moveCharacterNorth(mainChar)

				if item:
					messages.append("You cannot walk there")
					messages.append("press "+commandChars.activate+" to apply")
					itemMarkedLast = item
					footer.set_text(renderMessagebox())
					return
			else:
				try:
					room = terrain.roomByCoordinates[(mainChar.xPosition)//15,(mainChar.yPosition-1)//15]
				except Exception as e:
					room = None
				hadRoomInteraction = False
				if room:
					if room.yPosition*15+room.offsetY+room.sizeY == mainChar.yPosition:
						if room.xPosition*15+room.offsetX-1 < mainChar.xPosition and room.xPosition*15+room.offsetX+room.sizeX > mainChar.xPosition:
							hadRoomInteraction = True
							localisedEntry = (mainChar.xPosition%15-room.offsetX,mainChar.yPosition%15-room.offsetY-1)
							if localisedEntry[1] == -1:
								localisedEntry = (localisedEntry[0],room.sizeY-1)
							if localisedEntry in room.walkingAccess:
								if localisedEntry in room.itemByCoordinates and not room.itemByCoordinates[localisedEntry].walkable:
									itemMarkedLast = room.itemByCoordinates[localisedEntry]
									messages.append("you need to open the door first")
									messages.append("press "+commandChars.activate+" to apply")
									footer.set_text(renderMessagebox())
									return
								else:
									room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
									terrain.characters.remove(mainChar)
							else:
								messages.append("you cannot move there")
				if not hadRoomInteraction:
					try:
						item = terrain.itemByCoordinates[mainChar.xPosition,mainChar.yPosition-1]
					except Exception as e:
						item = None

					if item and not item.walkable:
						messages.append("You cannot walk there")
						messages.append("press "+commandChars.activate+" to apply")
						itemMarkedLast = item
						footer.set_text(renderMessagebox())
					else:	
						characters[0].yPosition -= 1
						characters[0].changed()

		if key in (commandChars.move_south):
			if mainChar.room:
				item = mainChar.room.moveCharacterSouth(mainChar)

				if item:
					messages.append("You cannot walk there")
					messages.append("press "+commandChars.activate+" to apply")
					itemMarkedLast = item
					footer.set_text(renderMessagebox())
					return
			else:
				try:
					room = terrain.roomByCoordinates[((mainChar.xPosition)//15,(mainChar.yPosition+1)//15)]
				except Exception as e:
					room = None
				hadRoomInteraction = False
				if room:
					if room.yPosition*15+room.offsetY == mainChar.yPosition+1:
						if room.xPosition*15+room.offsetX-1 < mainChar.xPosition and room.xPosition*15+room.offsetX+room.sizeX > mainChar.xPosition:
							hadRoomInteraction = True
							localisedEntry = ((mainChar.xPosition-room.offsetX)%15,(mainChar.yPosition-room.offsetY+1)%15)
							if localisedEntry in room.walkingAccess:
								if localisedEntry in room.itemByCoordinates and not room.itemByCoordinates[localisedEntry].walkable:
									itemMarkedLast = room.itemByCoordinates[localisedEntry]
									messages.append("you need to open the door first")
									messages.append("press "+commandChars.activate+" to apply")
									footer.set_text(renderMessagebox())
									return
								else:
									room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
									terrain.characters.remove(mainChar)
							else:
								messages.append("you cannot move there")
				if not hadRoomInteraction:
					try:
						item = terrain.itemByCoordinates[mainChar.xPosition,mainChar.yPosition+1]
					except Exception as e:
						item = None

					if item and not item.walkable:
						messages.append("You cannot walk there")
						messages.append("press "+commandChars.activate+" to apply")
						itemMarkedLast = item
						footer.set_text(renderMessagebox())
					else:	
						characters[0].yPosition += 1
						characters[0].changed()

		if key in (commandChars.move_east):
			if mainChar.room:
				item = mainChar.room.moveCharacterEast(mainChar)

				if item:
					messages.append("You cannot walk there")
					messages.append("press "+commandChars.activate+" to apply")
					itemMarkedLast = item
					footer.set_text(renderMessagebox())
					return
			else:
				try:
					room = terrain.roomByCoordinates[(mainChar.xPosition)//15,(mainChar.yPosition+1)//15]
				except Exception as e:
					room = None
				hadRoomInteraction = False
				if room:
					if room.xPosition*15+room.offsetX == mainChar.xPosition+1:
						if room.yPosition*15+room.offsetY < mainChar.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > mainChar.yPosition:
							hadRoomInteraction = True
							localisedEntry = ((mainChar.xPosition-room.offsetX+1)%15,(mainChar.yPosition-room.offsetY)%15)
							if localisedEntry in room.walkingAccess:
								if localisedEntry in room.itemByCoordinates and not room.itemByCoordinates[localisedEntry].walkable:
									itemMarkedLast = room.itemByCoordinates[localisedEntry]
									messages.append("you need to open the door first")
									messages.append("press "+commandChars.activate+" to apply")
									footer.set_text(renderMessagebox())
									return
								else:
									room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
									terrain.characters.remove(mainChar)
							else:
								messages.append("you cannot move there")
				if not hadRoomInteraction:
					try:
						item = terrain.itemByCoordinates[mainChar.xPosition+1,mainChar.yPosition]
					except Exception as e:
						item = None

					if item and not item.walkable:
						messages.append("You cannot walk there")
						messages.append("press "+commandChars.activate+" to apply")
						itemMarkedLast = item
						footer.set_text(renderMessagebox())
					else:	
						characters[0].xPosition += 1
						characters[0].changed()

		if key in (commandChars.move_west):
			if mainChar.room:
				item = mainChar.room.moveCharacterWest(mainChar)

				if item:
					messages.append("You cannot walk there")
					messages.append("press "+commandChars.activate+" to apply")
					itemMarkedLast = item
					footer.set_text(renderMessagebox())
					return
			else:
				try:
					room = terrain.roomByCoordinates[(mainChar.xPosition)//15,(mainChar.yPosition+1)//15]
				except Exception as e:
					room = None
				hadRoomInteraction = False
				if room:
					if room.xPosition*15+room.offsetX+room.sizeX == mainChar.xPosition:
						if room.yPosition*15+room.offsetY < mainChar.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > mainChar.yPosition:
							hadRoomInteraction = True
							localisedEntry = ((mainChar.xPosition-room.offsetX-1)%15,(mainChar.yPosition-room.offsetY)%15)
							if localisedEntry in room.walkingAccess:
								if localisedEntry in room.itemByCoordinates and not room.itemByCoordinates[localisedEntry].walkable:
									itemMarkedLast = room.itemByCoordinates[localisedEntry]
									messages.append("you need to open the door first")
									messages.append("press "+commandChars.activate+" to apply")
									footer.set_text(renderMessagebox())
									return
								else:
									room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
									terrain.characters.remove(mainChar)
							else:
								messages.append("you cannot move there")
				if not hadRoomInteraction:
					try:
						item = terrain.itemByCoordinates[mainChar.xPosition-1,mainChar.yPosition]
					except Exception as e:
						item = None

					if item and not item.walkable:
						messages.append("You cannot walk there")
						messages.append("press "+commandChars.activate+" to apply")
						itemMarkedLast = item
						footer.set_text(renderMessagebox())
					else:	
						characters[0].xPosition -= 1
						characters[0].changed()

		if key in (commandChars.activate):
			if itemMarkedLast:
				itemMarkedLast.apply(mainChar)
			else:
				if mainChar.room:
					itemList = mainChar.room.itemsOnFloor
				else:
					itemList = terrain.itemsOnFloor
				for item in itemList:
					if item.xPosition == characters[0].xPosition and item.yPosition == characters[0].yPosition:
						item.apply(mainChar)
		if key in (commandChars.drop):
			if len(characters[0].inventory):
				item = characters[0].inventory.pop()	
				item.xPosition = characters[0].xPosition		
				item.yPosition = characters[0].yPosition		
				if mainChar.room:
					itemList = mainChar.room.itemsOnFloor
				else:
					itemList = terrain.itemsOnFloor
				itemList.append(item)
				item.changed()
		if key in (commandChars.hail):
			messages.append(characters[0].name+": HÜ!")
			messages.append(characters[0].name+": HOTT!")
		if key in (commandChars.pickUp):
			if mainChar.room:
				itemList = mainChar.room.itemsOnFloor
			else:
				itemList = terrain.itemsOnFloor

			for item in itemList:
				if item.xPosition == characters[0].xPosition and item.yPosition == characters[0].yPosition:
					itemList.remove(item)
					if hasattr(item,"xPosition"):
						del item.xPosition
					if hasattr(item,"yPosition"):
						del item.yPosition
					characters[0].inventory.append(item)
					item.changed()

		if key in (commandChars.advance,commandChars.autoAdvance):
			if len(mainChar.quests):
				if not lastMoveAutomated:
					mainChar.setPathToQuest(mainChar.quests[0])
				lastMoveAutomated = True

				mainChar.automated = True
				mainChar.advance()
				mainChar.automated = False
			else:
				pass
		else:
			lastMoveAutomated = False

	itemMarkedLast = None
		
	if not gamestate.gameWon:
		if doAdvanceGame:
			advanceGame()

		header.set_text(renderQuests())
		main.set_text(render());
		footer.set_text(renderMessagebox())
	else:
		main.set_text("")
		footer.set_text("good job")


frame = urwid.Frame(urwid.Filler(main,"top"),header=header,footer=footer)
loop = urwid.MainLoop(frame, unhandled_input=show_or_exit)
cinematics.loop = loop
quests.loop = loop

cinematics.callShow_or_exit = callShow_or_exit
quests.callShow_or_exit = callShow_or_exit

def calculatePath(startX,startY,endX,endY,walkingPath):
	import math
	path = []

	if (startX == endX and startY == endY):
		return []
	if (startX == endX+1 and startY == endY):
		return [(endX,endY)]
	if (startX == endX-1 and startY == endY):
		return [(endX,endY)]
	if (startX == endX and startY == endY+1):
		return [(endX,endY)]
	if (startX == endX and startY == endY-1):
		return [(endX,endY)]

	circlePath = True
	if (startY > 11 and not startX==endX):
		circlePath = True
	elif (startY < 11):
		circlePath = True

	if (startX,startY) in walkingPath and (endX,endY) in walkingPath:
		startIndex = None
		index = 0
		for wayPoint in walkingPath:
			if wayPoint == (startX,startY):
				startIndex = index
			index += 1
		endIndex = None
		index = 0
		for wayPoint in walkingPath:
			if wayPoint == (endX,endY):
				endIndex = index
			index += 1

		distance = startIndex-endIndex
		if distance > 0:
			if circlePath:
				if distance < len(walkingPath)/2:
					result = []
					result.extend(reversed(walkingPath[endIndex:startIndex]))
					return result
				else:
					result = []
					result.extend(walkingPath[startIndex:])
					result.extend(walkingPath[:endIndex+1])
					return result
			else:
				result = []
				result.extend(reversed(walkingPath[endIndex:startIndex]))
				return result
		else:
			if circlePath:
				if (-distance) <= len(walkingPath)/2:
					return walkingPath[startIndex+1:endIndex+1]
				else:
					result = []
					result.extend(reversed(walkingPath[:startIndex]))
					result.extend(reversed(walkingPath[endIndex:]))
					return result
			else:
				return walkingPath[startIndex+1:endIndex+1]

	elif (endX,endY) in walkingPath:
		nearestPoint = None
		lowestDistance = 1234567890
		for waypoint in walkingPath:
			distance = abs(waypoint[0]-startX)+abs(waypoint[1]-startY)
			if lowestDistance > distance:
				lowestDistance = distance
				nearestPoint = waypoint

		if (endX,endY) == nearestPoint:
			pass
		else:
			result = []
			result.extend(calculatePath(startX,startY,nearestPoint[0],nearestPoint[1],walkingPath))
			result.extend(calculatePath(nearestPoint[0],nearestPoint[1],endX,endY,walkingPath))
			return result

	elif (startX,startY) in walkingPath:
		nearestPoint = None
		lowestDistance = 1234567890
		for waypoint in walkingPath:
			distance = abs(waypoint[0]-endX)+abs(waypoint[1]-endY)
			if lowestDistance > distance:
				lowestDistance = distance
				nearestPoint = waypoint

		if (startX,startY) == nearestPoint:
			pass
		else:
			result = []
			result.extend(calculatePath(startX,startY,nearestPoint[0],nearestPoint[1],walkingPath))
			result.extend(calculatePath(nearestPoint[0],nearestPoint[1],endX,endY,walkingPath))
			return result
	else:
		path = []
		startPoint = None
		lowestDistance = 1234567890
		for waypoint in walkingPath:
			distance = abs(waypoint[0]-startX)+abs(waypoint[1]-startY)
			if lowestDistance > distance:
				lowestDistance = distance
				startPoint = waypoint

		endPoint = None
		lowestDistance = 1234567890
		for waypoint in walkingPath:
			distance = abs(waypoint[0]-endX)+abs(waypoint[1]-endY)
			if lowestDistance > distance:
				lowestDistance = distance
				endPoint = waypoint

		path.extend(calculatePath(startX,startY,startPoint[0],startPoint[1],walkingPath))
		path.extend(calculatePath(startPoint[0],startPoint[1],endPoint[0],endPoint[1],walkingPath))
		path.extend(calculatePath(endPoint[0],endPoint[1],endX,endY,walkingPath))
		
		return path			

	diffX = startX-endX
	diffY = startY-endY
		
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
terrains.calculatePath = calculatePath

rooms.Character = characters.Character
		
class GameState():
	def __init__(self,characters):
		self.characters = characters
		self.gameWon = False
		self.tick = 0

messages = []
items.messages = messages
quests.messages = messages
rooms.messages = messages
characters.messages = messages
terrains.messages = messages
cinematics.messages = messages

quests.showCinematic = cinematics.showCinematic

terrain = terrains.TutorialTerrain()

characters.roomsOnMap = terrain.rooms

mapHidden = True

mainChar = characters.Character(displayChars.main_char,1,3,automated=False,name="Sigmund Bärenstein")
mainChar.terrain = terrain
mainChar.room = terrain.tutorialMachineRoom
mainChar.watched = True
terrain.tutorialMachineRoom.addCharacter(mainChar,1,4)

def setupFirstTutorialPhase():
	npc = characters.Character(displayChars.staffCharacters[11],1,2,name="Erwin von Libwig")
	#npc2.watched = True
	terrain.tutorialMachineRoom.addCharacter(npc,1,3)
	npc.terrain = terrain
	npc.room = terrain.tutorialMachineRoom
	#npc2.assignQuest(quest0)
	#npc2.automated = False

	npc2 = characters.Character(displayChars.staffCharacters[25],1,1,name="Ernst Ziegelbach")
	#npc2.watched = True
	terrain.tutorialMachineRoom.addCharacter(npc2,1,1)
	npc2.terrain = terrain
	npc2.room = terrain.tutorialMachineRoom
	#npc2.assignQuest(quest0)
	#npc2.automated = False

	cinematics.showCinematic("welcome to the Trainingenvironment\n\nplease, try to learn fast.\n\nParticipants with low Evaluationscores will be given suitable Assignments in the Vats")
	cinematics.showCinematic("the Trainingenvironment will show the Map now. take a look at everything and press "+commandChars.wait+" afterwards")
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.showCinematic("you are represented by the "+displayChars.main_char+" Character. find yourself on the screen and press "+commandChars.wait)
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.showCinematic("right now you are in the Boilerroom\n\nthe Floor is represented by "+displayChars.floor+" and Walls are shown as "+displayChars.wall+". the Door is represented by "+displayChars.door_closed+" or "+displayChars.door_opened+" when closed.\n\na empty Room would look like this:\n\n"+displayChars.wall*5+"\n"+displayChars.wall+displayChars.floor*3+displayChars.wall+"\n"+displayChars.wall+displayChars.floor*3+displayChars.door_closed+"\n"+displayChars.wall+displayChars.floor*3+displayChars.wall+"\n"+displayChars.wall*5+"\n\nthe Trainingenvironment will display now. please try to orient yourself in the Room.\n\npress "+commandChars.wait+" when successful")
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.showCinematic("in the Middle of the Room you see the Steamgenerator\n\n"+displayChars.void+displayChars.pipe+displayChars.boiler_inactive+displayChars.furnace_inactive+"\n"+displayChars.pipe+displayChars.pipe+displayChars.boiler_inactive+displayChars.furnace_inactive+"\n"+displayChars.void+displayChars.pipe+displayChars.boiler_active+displayChars.furnace_active+"\n\nit consist of Furnaces marked by "+displayChars.furnace_inactive+" or "+displayChars.furnace_active+" that heat the Water in the Boilers "+displayChars.boiler_inactive+" till it boils. a Boiler with boiling Water will be shown as "+displayChars.boiler_active+".\n\nthe Steam is transfered to the Pipes marked with "+displayChars.pipe+" and used to power the Ships Mechanics and Weapons\n\ntry to recognize the Design and press "+commandChars.wait)
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.showCinematic("the Furnaces burn Coal shown as "+displayChars.coal+". if a Furnace is burning Coal, it is shown as "+displayChars.furnace_active+" and shown as "+displayChars.furnace_inactive+" if not.\n\nthe Coal is stored in Piles shown as "+displayChars.pile+". the Coalpiles are on the right Side of the Room and are filled through the Pipes when needed.\n\nSince a Coaldelivery is incoming anyway. please wait and pay Attention.\n\ni will count down the ticks in the messageBox now")
	
	class CoalRefillEvent(object):
		def __init__(subself,tick):
			subself.tick = tick

		def handleEvent(subself):
			messages.append("*rumbling*")
			messages.append("*rumbling*")
			messages.append("*smoke and dust on cole piles and neighbour fields*")
			messages.append("*a chunk of coal drops onto the floor*")
			messages.append("*smoke clears*")

	terrain.tutorialMachineRoom.events.append(CoalRefillEvent(14))

	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("8"))
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("7"))
	cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("by the way: the Piles on the lower End of the Room are Storage for Replacementparts and you can sleep in the Hutches to the left shown as Ѻ "))
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("6"))
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("5"))
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("4"))
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("3"))
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("2"))
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("1"))
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("Coaldelivery now"))
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(2))
	cinematics.showCinematic("your cohabitants in this Room are:\n 'Erwin von Libwig' ("+displayChars.staffCharacters[11]+") is this Rooms 'Raumleiter' and therefore responsible for proper Steamgeneration in this Room\n 'Ernst Ziegelbach' ("+displayChars.staffCharacters[25]+") was dispatched to support 'Erwin von Libwig' and is his Subordinate\n\nyou will likely report to 'Erwin von Libwig' later. please try to find them on the display and press "+commandChars.wait)
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
	"""
	startShowGameCutScene()
	*Erwin von Libwig walks to a Pile and fires a furnace*
	*Erwin von Libwig walks back to a Pile and fires a furnace*
	endShowGameCutScene()
	*Erwin von Libwig goes back to waiting position*
	"""
	
	cinematics.showCinematic("Erwin von Libwig will demonstrate how to fire a furnace now.\n\nwatch and learn.")
	class AddQuestEvent(object):
		def __init__(subself,tick):
			subself.tick = tick

		def handleEvent(subself):
			quest0 = quests.CollectQuest()
			quest1 = quests.ActivateQuest(terrain.tutorialMachineRoom.furnace)
			quest2 = quests.MoveQuest(terrain.tutorialMachineRoom,1,3,startCinematics="inside the Simulationchamber everything has to be taught from Scratch\n\nthe basic Movementcommands are:\n\n w=up\n a=right\n s=down\n d=right\n\nplease move to the designated Target. the Implant will mark your Way\n\nremeber you are the "+displayChars.main_char)
			quest0.followUp = quest1
			quest1.followUp = quest2
			quest2.followUp = None
			npc.assignQuest(quest0,active=True)

	class ShowMessageEvent(object):
		def __init__(subself,tick):
			subself.tick = tick

		def handleEvent(subself):
			messages.append("*Erwin von Libwig, please fire the furnace now*")

	terrain.tutorialMachineRoom.events.append(ShowMessageEvent(17))
	terrain.tutorialMachineRoom.events.append(AddQuestEvent(18))
	cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(25))

	cinematics.showCinematic("there are other Items in the Room that may or may not be important for you. Here is the full List for you to review:\n\n Bin ("+displayChars.binStorage+"): Used for storing Things intended to be transported further\n Pile ("+displayChars.pile+"): a Pile of Things\n Door ("+displayChars.door_opened+" or "+displayChars.door_closed+"): you can move through it when open\n Lever ("+displayChars.lever_notPulled+" or "+displayChars.lever_pulled+"): a simple Man-Machineinterface\n Furnace ("+displayChars.furnace_inactive+"): used to generate heat burning Things\n Display ("+displayChars.display+"): a complicated Machine-Maninterface\n Wall ("+displayChars.wall+"): ensures the structural Integrity of basically any Structure\n Pipe ("+displayChars.wall+"): transports Liquids, Pseudoliquids and Gasses\n Coal ("+displayChars.coal+"): a piece of Coal, quite usefull actually\n Boiler ("+displayChars.boiler_inactive+" or "+displayChars.boiler_active+"): generates Steam using Water and and Heat\n Chains ("+displayChars.chains+"): some Chains dangling about. sometimes used as Man-Machineinterface or for Climbing\n Comlink ("+displayChars.commLink+"): a Pipe based Voicetransportationsystem that allows Communication with other Rooms\n Hutch ("+displayChars.hutch_free+"): a comfy and safe Place to sleep and eat")

setupFirstTutorialPhase()

#cinematics.showCinematic("movement can be tricky sometimes so please make yourself comfortable with the controls.\n\nyou can move in 4 Directions along the x and y Axis. the z Axis is not supported yet. diagonal Movements are not supported since they do not exist.\n\nthe basic Movementcommands are:\n w=up\n a=right\n s=down\n d=right\nplease move to the designated Target. the Implant will mark your Way")
#"""
#*move back to waiting position*
#"""
#cinematics.showCinematic("you have 20 Ticks to familiarise yourself with the Movementcommands. please do.")
#cinematics.showCinematic("next on my Checklist is to explain the Interaction with your Environment\n\ninteraction with your Environment is somewhat complicated\n\nthe basic Interationcommands are:\n j=activate/apply\n e=examine\n k=pick up\n\nsee this Piles of Coal marked with ӫ on the rigth Side of the Room.\n\nwhenever you bump into an item that is to big to be walked on, you will promted for giving an extra interaction command. I'll give you an example:\n\nΩΩ＠ӫӫ\n\n pressing a and j would result in Activation of the Furnace\n pressing d and j would result in Activation of the Pile\n pressing a and e would result make you examine the Furnace\n pressing d and e would result make you examine the Pile\n\nplease grab yourself some Coal from a pile by bumping into it and pressing j afterwards.")

tutorialQuest1 = quests.MoveQuest(terrain.tutorialMachineRoom,5,7,startCinematics="inside the Simulationchamber everything has to be taught from Scratch\n\nthe basic Movementcommands are:\n\n w=up\n a=right\n s=down\n d=right\n\nplease move to the designated Target. the Implant will mark your Way\n\nremeber you are the "+displayChars.main_char)
#tutorialQuest1 = quests.PatrolQuest([(terrain.tutorialMachineRoom,2,2),(terrain.tutorialMachineRoom,2,7),(terrain.tutorialMachineRoom,7,7),(terrain.tutorialMachineRoom,7,2)])
tutorialQuest2 = quests.CollectQuest(startCinematics="interaction with your Environment ist somewhat complicated\n\nthe basic Interationcommands are:\n\n j=activate/apply\n e=examine\n k=pick up\n\nsee this Piles of Coal marked with "+displayChars.coal+" on the rigth Side of the room.\n\nplease grab yourself some Coal from a pile by moving onto it and pressing "+commandChars.activate+".")
tutorialQuest3 = quests.ActivateQuest(terrain.tutorialMachineRoom.furnace,startCinematics="now go and activate the Furnace marked with a "+displayChars.furnace_inactive+". you need to have burnable Material like Coal in your Inventory\n\nso ensure that you have some Coal in your Inventory go to the Furnace and press "+commandChars.activate+".")
tutorialQuest4 = quests.MoveQuest(terrain.tutorialMachineRoom,1,3,startCinematics="Move back to Waitingposition")
tutorialQuest5 = quests.LeaveRoomQuest(terrain.tutorialMachineRoom,startCinematics="please exit the Room")
tutorialQuest5 = quests.EnterRoomQuest(terrain.tutorialVat,startCinematics="please goto the Vat")
tutorialQuest6 = quests.MoveQuest(terrain.tutorialVat,4,4,startCinematics="please move to Waitingposition")

tutorialQuest1.followUp = tutorialQuest2
tutorialQuest2.followUp = tutorialQuest3
tutorialQuest3.followUp = tutorialQuest4
tutorialQuest4.followUp = tutorialQuest5
tutorialQuest5.followUp = tutorialQuest6
tutorialQuest6.followUp = None

rooms.mainChar = mainChar
terrains.mainChar = mainChar

mainChar.assignQuest(tutorialQuest1)

"""
quest0 = quests.MoveQuest(terrain.tutorialMachineRoom,7,7)
quest1 = quests.MoveQuest(room1,4,4)
quest2 = quests.MoveQuest(room3,6,6)
quest3 = quests.MoveQuest(room4,2,8)
quest4 = quests.MoveQuest(room5,2,2)
quest5 = quests.MoveQuest(room6,2,2)
quest6 = quests.MoveQuest(room7,2,2)
quest7 = quests.MoveQuest(room8,2,2)
quest8 = quests.MoveQuest(room9,2,2)
quest9 = quests.MoveQuest(room1,2,2)
quest10 = quests.MoveQuest(room9,2,2)
quest11 = quests.MoveQuest(room8,2,2)
quest12 = quests.MoveQuest(room7,2,2)
quest13 = quests.MoveQuest(room6,2,2)
quest14 = quests.MoveQuest(room5,2,2)
quest15 = quests.MoveQuest(room4,2,2)
quest16 = quests.MoveQuest(room3,2,2)
quest17 = quests.MoveQuest(room2,2,2)
quest18 = quests.MoveQuest(room1,2,2)
quest19 = quests.MoveQuest(room2,2,2)
quest0.followUp = quest1
quest1.followUp = quest2
quest2.followUp = quest3
quest3.followUp = quest4
quest4.followUp = quest5
quest5.followUp = quest6
quest6.followUp = quest7
quest7.followUp = quest8
quest8.followUp = quest9
quest9.followUp = quest10
quest10.followUp = quest11
quest11.followUp = quest12
quest12.followUp = quest13
quest13.followUp = quest14
quest14.followUp = quest15
quest15.followUp = quest16
quest16.followUp = quest17
quest17.followUp = quest18
quest18.followUp = quest19
quest19.followUp = quest0
"""
npc2 = characters.Character(displayChars.staffCharacters[25],1,1,name="Ernst Ziegelbach")
#npc2.watched = True
terrain.tutorialMachineRoom.addCharacter(npc2,1,1)
npc2.terrain = terrain
npc2.room = terrain.tutorialMachineRoom
#npc2.assignQuest(quest0)
#npc2.automated = False

characters = [mainChar]
items.characters = characters
rooms.characters = characters

gamestate = GameState(characters)

movestate = "up"
def advanceGame():
	global movestate
	for character in terrain.characters:
		character.advance()

	for room in terrain.rooms:
		room.advance()

	if terrain.movingRoom.gogogo:
		if movestate == "up":
			terrain.moveRoomNorth(terrain.movingRoom)
			if terrain.movingRoom.yPosition == 3 and terrain.movingRoom.offsetY == 2:
				movestate = "left"
		elif movestate == "left":
			terrain.moveRoomWest(terrain.movingRoom)
			if terrain.movingRoom.xPosition == 2 and terrain.movingRoom.offsetX == 2:
				movestate = "down"
		elif movestate == "down":
			terrain.moveRoomSouth(terrain.movingRoom)
			if terrain.movingRoom.yPosition == 6 and terrain.movingRoom.offsetY == 2:
				movestate = "right"
		elif movestate == "right":
			terrain.moveRoomEast(terrain.movingRoom)
			if terrain.movingRoom.xPosition == 8 and terrain.movingRoom.offsetX == 2:
				movestate = "up"

	gamestate.tick += 1

cinematics.advanceGame = advanceGame

def renderQuests():
	txt = ""
	if len(characters[0].quests):
		for quest in mainChar.quests:
			txt+= "QUEST: "+quest.description+"\n"
		txt += str(mainChar.xPosition)+"/"+str(mainChar.yPosition)
	else:
		txt += "QUEST: keinQuest\n\n"
		gamestate.gameWon = True
		loop.set_alarm_in(0.0, callShow_or_exit, commandChars.ignore)
	return txt
	
def renderMessagebox():
	txt = ""
	for message in messages[-5:]:
		txt += str(message)+"\n"
	return txt

def render():
	chars = terrain.render()

	if mainChar.room:
		centerX = mainChar.room.xPosition*15+mainChar.room.offsetX+mainChar.xPosition
		centerY = mainChar.room.yPosition*15+mainChar.room.offsetY+mainChar.yPosition
	else:
		centerX = mainChar.xPosition
		centerY = mainChar.yPosition

	screensize = loop.screen.get_cols_rows()
	decorationSize = frame.frame_top_bottom(loop.screen.get_cols_rows(),True)
	screensize = (screensize[0]-decorationSize[0][0],screensize[1]-decorationSize[0][1])

	offsetX = int((screensize[0]/4)-centerX)
	offsetY = int((screensize[1]/2)-centerY)

	result = ""

	if offsetY > 0:
		result += "\n"*offsetY

	if offsetY < 0:
		chars = chars[-offsetY:]

	for line in chars:
		lineRender = ""
		rowCounter = 0

		if offsetX > 0:
			lineRender += "  "*offsetX

		if offsetX < 0:
			line = line[-offsetX:]

		for char in line:
			lineRender += char
			rowCounter += 1
		lineRender += "\n"
		result += lineRender
		
	return result

loop.set_alarm_in(0.0, callShow_or_exit, commandChars.ignore)
loop.run()
