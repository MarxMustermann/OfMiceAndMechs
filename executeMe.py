import urwid 
import sys
import json

import src.items as items
import src.quests as quests
import src.rooms as rooms
import src.characters as characters
import src.terrains as terrains
import src.cinematics as cinematics
import config.commandChars as commandChars
import config.names as names

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
			gamestate.save()
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
			gamestate.save()
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
				rooms = []
				bigX = (mainChar.xPosition)//15
				bigY = (mainChar.yPosition-1)//15
				for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
					if coordinate in terrain.roomByCoordinates:
						rooms.extend(terrain.roomByCoordinates[coordinate])

				hadRoomInteraction = False
				for room in rooms:
					if room.yPosition*15+room.offsetY+room.sizeY == mainChar.yPosition:
						if room.xPosition*15+room.offsetX-1 < mainChar.xPosition and room.xPosition*15+room.offsetX+room.sizeX > mainChar.xPosition:
							hadRoomInteraction = True
							localisedEntry = (mainChar.xPosition%15-room.offsetX,mainChar.yPosition%15-room.offsetY-1)
							if localisedEntry[1] == -1:
								localisedEntry = (localisedEntry[0],room.sizeY-1)
							if localisedEntry in room.walkingAccess:
								for item in room.itemByCoordinates[localisedEntry]:
									if not item.walkable:
										itemMarkedLast = item
										messages.append("you need to open the door first")
										messages.append("press "+commandChars.activate+" to apply")
										footer.set_text(renderMessagebox())
										return
								
								room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
								terrain.characters.remove(mainChar)
							else:
								messages.append("you cannot move there")
				if not hadRoomInteraction:
					try:
						items = terrain.itemByCoordinates[mainChar.xPosition,mainChar.yPosition-1]
					except Exception as e:
						items = []

					foundItem = False
					for item in items:
						if item and not item.walkable:
							messages.append("You cannot walk there")
							messages.append("press "+commandChars.activate+" to apply")
							itemMarkedLast = item
							footer.set_text(renderMessagebox())
							foundItem = True
					if not foundItem:
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
				rooms = []
				bigX = (mainChar.xPosition)//15
				bigY = (mainChar.yPosition+1)//15
				for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
					if coordinate in terrain.roomByCoordinates:
						rooms.extend(terrain.roomByCoordinates[coordinate])

				hadRoomInteraction = False
				for room in rooms:
					if room.yPosition*15+room.offsetY == mainChar.yPosition+1:
						if room.xPosition*15+room.offsetX-1 < mainChar.xPosition and room.xPosition*15+room.offsetX+room.sizeX > mainChar.xPosition:
							hadRoomInteraction = True
							localisedEntry = ((mainChar.xPosition-room.offsetX)%15,(mainChar.yPosition-room.offsetY+1)%15)
							if localisedEntry in room.walkingAccess:
								for item in room.itemByCoordinates[localisedEntry]:
									if not item.walkable:
										itemMarkedLast = item
										messages.append("you need to open the door first")
										messages.append("press "+commandChars.activate+" to apply")
										footer.set_text(renderMessagebox())
										return
								
								room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
								terrain.characters.remove(mainChar)
							else:
								messages.append("you cannot move there")
				if not hadRoomInteraction:
					try:
						items = terrain.itemByCoordinates[mainChar.xPosition,mainChar.yPosition+1]
					except Exception as e:
						items = []

					foundItem = False
					for item in items:
						if item and not item.walkable:
							messages.append("You cannot walk there")
							messages.append("press "+commandChars.activate+" to apply")
							itemMarkedLast = item
							footer.set_text(renderMessagebox())
							foundItem = True
					if not foundItem:
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
				rooms = []
				bigX = (mainChar.xPosition+1)//15
				bigY = (mainChar.yPosition)//15
				for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
					if coordinate in terrain.roomByCoordinates:
						rooms.extend(terrain.roomByCoordinates[coordinate])

				hadRoomInteraction = False
				for room in rooms:
					if room.xPosition*15+room.offsetX == mainChar.xPosition+1:
						if room.yPosition*15+room.offsetY < mainChar.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > mainChar.yPosition:
							hadRoomInteraction = True
							localisedEntry = ((mainChar.xPosition-room.offsetX+1)%15,(mainChar.yPosition-room.offsetY)%15)
							if localisedEntry in room.walkingAccess:
								for item in room.itemByCoordinates[localisedEntry]:
									if not item.walkable:
										itemMarkedLast = item
										messages.append("you need to open the door first")
										messages.append("press "+commandChars.activate+" to apply")
										footer.set_text(renderMessagebox())
										return
								
								room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
								terrain.characters.remove(mainChar)
							else:
								messages.append("you cannot move there")
				if not hadRoomInteraction:
					try:
						items = terrain.itemByCoordinates[mainChar.xPosition+1,mainChar.yPosition]
					except Exception as e:
						items = []

					foundItem = False
					for item in items:
						if item and not item.walkable:
							messages.append("You cannot walk there")
							messages.append("press "+commandChars.activate+" to apply")
							itemMarkedLast = item
							footer.set_text(renderMessagebox())
							foundItem = True
					if not foundItem:
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
				rooms = []
				bigX = (mainChar.xPosition)//15
				bigY = (mainChar.yPosition-1)//15
				for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
					if coordinate in terrain.roomByCoordinates:
						rooms.extend(terrain.roomByCoordinates[coordinate])

				hadRoomInteraction = False
				for room in rooms:
					if room.xPosition*15+room.offsetX+room.sizeX == mainChar.xPosition:
						if room.yPosition*15+room.offsetY < mainChar.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > mainChar.yPosition:
							hadRoomInteraction = True
							localisedEntry = ((mainChar.xPosition-room.offsetX-1)%15,(mainChar.yPosition-room.offsetY)%15)
							if localisedEntry in room.walkingAccess:
								for item in room.itemByCoordinates[localisedEntry]:
									if not item.walkable:
										itemMarkedLast = item
										messages.append("you need to open the door first")
										messages.append("press "+commandChars.activate+" to apply")
										footer.set_text(renderMessagebox())
										return
								
								room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
								terrain.characters.remove(mainChar)
							else:
								messages.append("you cannot move there")
				if not hadRoomInteraction:
					try:
						items = terrain.itemByCoordinates[mainChar.xPosition-1,mainChar.yPosition]
					except Exception as e:
						items = []

					foundItem = False
					for item in items:
						if item and not item.walkable:
							messages.append("You cannot walk there")
							messages.append("press "+commandChars.activate+" to apply")
							itemMarkedLast = item
							footer.set_text(renderMessagebox())
							foundItem = True
					if not foundItem:
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

		if key in (commandChars.examine):
			if itemMarkedLast:
				messages.append(itemMarkedLast.description)
				messages.append(itemMarkedLast.getDetailedInfo())
			else:
				if mainChar.room:
					itemList = mainChar.room.itemsOnFloor
				else:
					itemList = terrain.itemsOnFloor
				for item in itemList:
					if item.xPosition == characters[0].xPosition and item.yPosition == characters[0].yPosition:
						messages.append(item.description)
						messages.append(item.getDetailedInfo())

		if key in (commandChars.drop):
			if len(characters[0].inventory):
				item = characters[0].inventory.pop()	
				item.xPosition = characters[0].xPosition		
				item.yPosition = characters[0].yPosition		
				if mainChar.room:
					characters[0].room.addItems([item])
				else:
					characters[0].terrain.addItems([item])
				item.changed()

		if key in (commandChars.pickUp):
			if len(mainChar.inventory) > 10:
				messages.append("you cannot carry more items")
			if mainChar.room:
				itemByCoordinates = mainChar.room.itemByCoordinates
				itemList = mainChar.room.itemsOnFloor
			else:
				itemByCoordinates = terrain.itemByCoordinates
				itemList = terrain.itemsOnFloor

			if (characters[0].xPosition,characters[0].yPosition) in itemByCoordinates:
				for item in itemByCoordinates[(characters[0].xPosition,characters[0].yPosition)]:
					itemList.remove(item)
					if hasattr(item,"xPosition"):
						del item.xPosition
					if hasattr(item,"yPosition"):
						del item.yPosition
					characters[0].inventory.append(item)
					item.changed()
				del itemByCoordinates[(characters[0].xPosition,characters[0].yPosition)]

		if key in (commandChars.hail):
			messages.append(characters[0].name+": HÜ!")
			messages.append(characters[0].name+": HOTT!")

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
	path = calculatePathReal(startX,startY,endX,endY,walkingPath)

	index = 0
	lastFoundIndex = index
	for wayPoint in path:
		if wayPoint == (startX,startY):
			lastFoundIndex = index
		index += 1

	return path[lastFoundIndex:]

def calculatePathReal(startX,startY,endX,endY,walkingPath):
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
			result.extend(calculatePathReal(startX,startY,nearestPoint[0],nearestPoint[1],walkingPath))
			result.extend(calculatePathReal(nearestPoint[0],nearestPoint[1],endX,endY,walkingPath))
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
			result.extend(calculatePathReal(startX,startY,nearestPoint[0],nearestPoint[1],walkingPath))
			result.extend(calculatePathReal(nearestPoint[0],nearestPoint[1],endX,endY,walkingPath))
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

		path.extend(calculatePathReal(startX,startY,startPoint[0],startPoint[1],walkingPath))
		path.extend(calculatePathReal(startPoint[0],startPoint[1],endPoint[0],endPoint[1],walkingPath))
		path.extend(calculatePathReal(endPoint[0],endPoint[1],endX,endY,walkingPath))
		
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
		
phasesByName = {}

class GameState():
	def __init__(self):
		self.gameWon = False
		self.currentPhase = phasesByName["FirstTutorialPhase"]
		self.tick = 0

		self.mainChar = characters.Character(displayChars.main_char,3,3,automated=False,name=names.characterFirstNames[self.tick%len(names.characterFirstNames)]+" "+names.characterLastNames[self.tick%len(names.characterLastNames)])
		self.mainChar.terrain = terrain
		self.mainChar.room = terrain.tutorialMachineRoom
		self.mainChar.watched = True
		terrain.tutorialMachineRoom.addCharacter(self.mainChar,3,3)

	def save(self):
		saveFile = open("gamestate/gamestate.json","w")
		state = self.getState()
		saveFile.write(json.dumps(state))
		saveFile.close()

	def load(self):
		saveFile = open("gamestate/gamestate.json")
		state = json.loads(saveFile.read())
		self.setState(state)
		saveFile.close()

	def setState(self,state):
		self.gameWon = state["gameWon"]
		self.currentPhase = phasesByName[state["currentPhase"]]
		self.tick = state["tick"]

	def getState(self):
		return {"gameWon":self.gameWon,"currentPhase":self.currentPhase.name,"tick":self.tick}
gamestate = None

messages = []
items.messages = messages
quests.messages = messages
rooms.messages = messages
characters.messages = messages
terrains.messages = messages
cinematics.messages = messages

quests.showCinematic = cinematics.showCinematic

terrain = terrains.TutorialTerrain()

items.terrain = terrain

characters.roomsOnMap = terrain.rooms

mapHidden = True

mainChar = None

class FirstTutorialPhase(object):
	def __init__(self):
		self.name = "FirstTutorialPhase"

	def start(self):
		gamestate.currentPhase = self

		# fix the setup
		if not terrain.tutorialMachineRoom.secondOfficer:
			npc = characters.Character(displayChars.staffCharacters[11],4,3,name=names.characterFirstNames[gamestate.tick%(len(names.characterFirstNames)+2)]+" "+names.characterLastNames[gamestate.tick%(len(names.characterLastNames)+2)])
			npc.terrain = terrain
			npc.room = terrain.tutorialMachineRoom
			terrain.tutorialMachineRoom.addCharacter(npc,4,3)
			terrain.tutorialMachineRoom.secondOfficer = npc
		npc = terrain.tutorialMachineRoom.secondOfficer

		if not terrain.tutorialMachineRoom.secondOfficer:
			npc2 = characters.Character(displayChars.staffCharacters[25],5,3,name=names.characterFirstNames[self.tick%(len(names.characterFirstNames)+9)]+" "+names.characterLastNames[self.tick%(len(names.characterLastNames)+4)])
			npc2.terrain = terrain
			npc2.room = terrain.tutorialMachineRoom
			terrain.tutorialMachineRoom.addCharacter(npc2,5,3)
			terrain.tutorialMachineRoom.firstOfficer = npc2
		npc2 = terrain.tutorialMachineRoom.firstOfficer

		cinematics.showCinematic("welcome to the Trainingenvironment\n\nplease, try to learn fast.\n\nParticipants with low Evaluationscores will be given suitable Assignments in the Vats")
		cinematics.showCinematic("the Trainingenvironment will show now. take a look at Everything and press "+commandChars.wait+" afterwards. You will be able to move later")
		cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
		cinematics.showCinematic("you are represented by the "+displayChars.main_char+" Character. find yourself on the Screen and press "+commandChars.wait)
		cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
		cinematics.showCinematic("right now you are in the Boilerroom\n\nthe Floor is represented by "+displayChars.floor+" and Walls are shown as "+displayChars.wall+". the Door is represented by "+displayChars.door_closed+" or "+displayChars.door_opened+" when closed.\n\na empty Room would look like this:\n\n"+displayChars.wall*5+"\n"+displayChars.wall+displayChars.floor*3+displayChars.wall+"\n"+displayChars.wall+displayChars.floor*3+displayChars.door_closed+"\n"+displayChars.wall+displayChars.floor*3+displayChars.wall+"\n"+displayChars.wall*5+"\n\nthe Trainingenvironment will display now. please try to orient yourself in the Room.\n\npress "+commandChars.wait+" when successful")
		cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
		cinematics.showCinematic("on the southern Side of the Room you see the Steamgenerators. A Steamgenerator might look like this:\n\n"+displayChars.void+displayChars.pipe+displayChars.boiler_inactive+displayChars.furnace_inactive+"\n"+displayChars.pipe+displayChars.pipe+displayChars.boiler_inactive+displayChars.furnace_inactive+"\n"+displayChars.void+displayChars.pipe+displayChars.boiler_active+displayChars.furnace_active+"\n\nit consist of Furnaces marked by "+displayChars.furnace_inactive+" or "+displayChars.furnace_active+" that heat the Water in the Boilers "+displayChars.boiler_inactive+" till it boils. a Boiler with boiling Water will be shown as "+displayChars.boiler_active+".\n\nthe Steam is transfered to the Pipes marked with "+displayChars.pipe+" and used to power the Ships Mechanics and Weapons\n\nDesign of generators are often quite unique. try to recognize the Genrators in this room and press "+commandChars.wait+"")
		cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
		cinematics.showCinematic("the Furnaces burn Coal shown as "+displayChars.coal+" . if a Furnace is burning Coal, it is shown as "+displayChars.furnace_active+" and shown as "+displayChars.furnace_inactive+" if not.\n\nthe Coal is stored in Piles shown as "+displayChars.pile+". the Coalpiles are on the right Side of the Room and are filled through the Pipes when needed.\n\nSince a Coaldelivery is incoming anyway. please wait and pay Attention.\n\ni will count down the Ticks in the Messagebox now")
		
		class CoalRefillEvent(object):
			def __init__(subself,tick):
				subself.tick = tick

			def handleEvent(subself):
				messages.append("*rumbling*")
				messages.append("*rumbling*")
				messages.append("*smoke and dust on Coalpiles and neighbourng Fields*")
				messages.append("*a chunk of Coal drops onto the floor*")
				terrain.tutorialMachineRoom.addItems([items.Coal(7,5)])
				messages.append("*smoke clears*")

		terrain.tutorialMachineRoom.addEvent(CoalRefillEvent(gamestate.tick+14))

		cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
		cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("8"))
		cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
		cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("7"))
		cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("by the Way: the Piles on the lower End of the Room are Storage for Replacementparts and you can sleep in the Hutches to the left shown as "+displayChars.hutch_free+" or "+displayChars.hutch_occupied))
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
		
		cinematics.showCinematic("Erwin von Libwig will demonstrate how to fire a furnace now.\n\nwatch and learn.")
		class AddQuestEvent(object):
			def __init__(subself,tick):
				subself.tick = tick

			def handleEvent(subself):
				quest0 = quests.CollectQuest()
				quest1 = quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[2])
				quest2 = quests.MoveQuest(terrain.tutorialMachineRoom,4,3)
				quest0.followUp = quest1
				quest1.followUp = quest2
				quest2.followUp = None
				npc.assignQuest(quest0,active=True)

		class ShowMessageEvent(object):
			def __init__(subself,tick):
				subself.tick = tick

			def handleEvent(subself):
				messages.append("*Erwin von Libwig, please fire the Furnace now*")

		terrain.tutorialMachineRoom.addEvent(ShowMessageEvent(gamestate.tick+17))
		terrain.tutorialMachineRoom.addEvent(AddQuestEvent(gamestate.tick+18))
		cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(gamestate.tick+24))

		cinematics.showCinematic("there are other Items in the Room that may or may not be important for you. Here is the full List for you to review:\n\n Bin ("+displayChars.binStorage+"): Used for storing Things intended to be transported further\n Pile ("+displayChars.pile+"): a Pile of Things\n Door ("+displayChars.door_opened+" or "+displayChars.door_closed+"): you can move through it when open\n Lever ("+displayChars.lever_notPulled+" or "+displayChars.lever_pulled+"): a simple Man-Machineinterface\n Furnace ("+displayChars.furnace_inactive+"): used to generate heat burning Things\n Display ("+displayChars.display+"): a complicated Machine-Maninterface\n Wall ("+displayChars.wall+"): ensures the structural Integrity of basically any Structure\n Pipe ("+displayChars.pipe+"): transports Liquids, Pseudoliquids and Gasses\n Coal ("+displayChars.coal+"): a piece of Coal, quite usefull actually\n Boiler ("+displayChars.boiler_inactive+" or "+displayChars.boiler_active+"): generates Steam using Water and and Heat\n Chains ("+displayChars.chains+"): some Chains dangling about. sometimes used as Man-Machineinterface or for Climbing\n Comlink ("+displayChars.commLink+"): a Pipe based Voicetransportationsystem that allows Communication with other Rooms\n Hutch ("+displayChars.hutch_free+"): a comfy and safe Place to sleep and eat")

		class StartNextPhaseEvent(object):
			def __init__(subself,tick):
				subself.tick = tick

			def handleEvent(subself):
				self.end()

		terrain.tutorialMachineRoom.addEvent(StartNextPhaseEvent(40))

	def end(self):
		cinematics.showCinematic("please try to remember the Information. The lesson will now continue with movement.")
		phase2 = SecondTutorialPhase()
		phase2.start()
phasesByName["FirstTutorialPhase"] = FirstTutorialPhase

class SecondTutorialPhase(object):
	def __init__(self):
		self.name = "SecondTutorialPhase"

	def start(self):
		gamestate.currentPhase = self

		if not terrain.tutorialMachineRoom.secondOfficer:
			npc = characters.Character(displayChars.staffCharacters[11],4,3,name="Erwin von Libwig")
			npc.terrain = terrain
			npc.room = terrain.tutorialMachineRoom
			terrain.tutorialMachineRoom.addCharacter(npc,4,3)
			terrain.tutorialMachineRoom.secondOfficer = npc
		npc = terrain.tutorialMachineRoom.secondOfficer

		if not terrain.tutorialMachineRoom.secondOfficer:
			npc2 = characters.Character(displayChars.staffCharacters[25],5,3,name="Ernst Ziegelbach")
			npc2.terrain = terrain
			npc2.room = terrain.tutorialMachineRoom
			terrain.tutorialMachineRoom.addCharacter(npc2,5,3)
			terrain.tutorialMachineRoom.firstOfficer = npc2
		npc2 = terrain.tutorialMachineRoom.firstOfficer

		questList = []
		questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,5,5,startCinematics="movement can be tricky sometimes so please make yourself comfortable with the controls.\n\nyou can move in 4 Directions along the x and y Axis. the z Axis is not supported yet. diagonal Movements are not supported since they do not exist.\n\nthe basic Movementcommands are:\n "+commandChars.move_north+"=up\n "+commandChars.move_east+"=right\n "+commandChars.move_south+"=down\n "+commandChars.move_west+"=right\nplease move to the designated Target. the Implant will mark your Way"))
		questList.append(quests.PatrolQuest([(terrain.tutorialMachineRoom,2,2),(terrain.tutorialMachineRoom,2,5),(terrain.tutorialMachineRoom,7,5),(terrain.tutorialMachineRoom,7,2)],startCinematics="now please patrol around the rooms a few times.",lifetime=80))
		questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="thats enough. move back to waiting position"))
		questList.append(quests.ExamineQuest(lifetime=100,startCinematics="use e to examine items. you can get Descriptions and more detailed Information about your Environment than just by looking at things.\n\nto look at something you have to walk into or over the item and press "+commandChars.examine+". For example if you stand next to a Furnace like this:\n\n"+displayChars.furnace_inactive+displayChars.main_char+"\n\npressing "+commandChars.move_west+" and then "+commandChars.examine+" would result in the Description:\n\n\"this is a Furnace\"\n\nyou have 100 Ticks to familiarise yourself with the Movementcommands and to examine the Room. please do."))
		questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="Move back to Waitingposition"))
		questList.append(quests.CollectQuest(startCinematics="next on my Checklist is to explain the Interaction with your Environment.\n\nthe basic Interationcommands are:\n\n "+commandChars.activate+"=activate/apply\n "+commandChars.examine+"=examine\n "+commandChars.pickUp+"=pick up\n "+commandChars.drop+"=drop\n\nsee this Piles of Coal marked with ӫ on the rigth Side and left Side of the Room.\n\nwhenever you bump into an Item that is to big to be walked on, you will promted for giving an extra Interactioncommand. i'll give you an Example:\n\n ΩΩ＠ӫӫ\n\n pressing "+commandChars.move_west+" and "+commandChars.activate+" would result in Activation of the Furnace\n pressing "+commandChars.move_east+" and "+commandChars.activate+" would result in Activation of the Pile\n pressing "+commandChars.move_west+" and "+commandChars.examine+" would result make you examine the Furnace\n pressing "+commandChars.move_east+" and "+commandChars.examine+" would result make you examine the Pile\n\nplease grab yourself some Coal from a pile by bumping into it and pressing j afterwards."))
		questList.append(quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[0],startCinematics="now go and fire the top most Furnace."))
		questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="please pick up the Coal on the Floor. \n\nyou won't see a whole Year of Service leaving burnable Material next to a Furnace"))
		questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="please move back to the waiting position"))

		lastQuest = questList[0]
		for item in questList[1:]:
			lastQuest.followUp = item
			lastQuest = item
		questList[-1].followup = None

		questList[-1].endTrigger = self.end

		mainChar.assignQuest(questList[0])

	def end(self):
		cinematics.showCinematic("you recieved your Preparatorytraining. Time for the Test.")
		phase = ThirdTutorialPhase()
		phase.start()
phasesByName["SecondTutorialPhase"] = SecondTutorialPhase

class ThirdTutorialPhase(object):
	def __init__(self):
		self.name = "ThirdTutorialPhase"

	def start(self):
		gamestate.currentPhase = self

		if not terrain.tutorialMachineRoom.secondOfficer:
			npc = characters.Character(displayChars.staffCharacters[11],4,3,name="Erwin von Libwig")
			terrain.tutorialMachineRoom.addCharacter(npc,4,3)
			terrain.tutorialMachineRoom.secondOfficer = npc
		self.npc = terrain.tutorialMachineRoom.secondOfficer

		cinematics.showCinematic("during the test Messages and new Task will be shown on the Buttom of the Screen. start now.")

		questList = []
		questList.append(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[0],startCinematics="fire the first Furnace from the west"))
		questList.append(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[1],startCinematics="fire the second Furnace from the west"))
		questList.append(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[2],startCinematics="fire the third Furnace from the west"))
		questList.append(quests.FillPocketsQuest(startCinematics="fill you Pockets with Coal now"))

		lastQuest = questList[0]
		for item in questList[1:]:
			lastQuest.followUp = item
			lastQuest = item
		questList[-1].followup = None

		self.mainCharFurnaceIndex = 0
		self.npcFurnaceIndex = 0

		def endMainChar():
			cinematics.showCinematic("stop.")
			for quest in mainChar.quests:
				quest.deactivate()
			mainChar.quests = []
			terrain.tutorialMachineRoom.removeEventsByType(AnotherOne)
			mainChar.assignQuest(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="please move back to the waiting position"))

			messages.append("your turn Ludwig")

			questList = []
			#questList.append(quests.FillPocketsQuest())
			#questList.append(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[1]))
			#questList.append(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[2]))
			questList.append(quests.FillPocketsQuest())

			lastQuest = questList[0]
			for item in questList[1:]:
				lastQuest.followUp = item
				lastQuest = item
			questList[-1].followup = None

			class AnotherOne2(object):
				def __init__(subself,tick,index):
					subself.tick = tick
					subself.furnaceIndex = index

				def handleEvent(subself):
					self.npc.assignQuest(quests.KeepFurnaceFired(terrain.tutorialMachineRoom.furnaces[subself.furnaceIndex],failTrigger=self.end))
					newIndex = subself.furnaceIndex+1
					self.npcFurnaceIndex = subself.furnaceIndex
					if newIndex < 8:
						self.npc.assignQuest(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[newIndex]))
						terrain.tutorialMachineRoom.addEvent(AnotherOne2(gamestate.tick+20,newIndex))

			self.anotherOne2 = AnotherOne2

			class WaitForClearStart(object):
				def __init__(subself,tick,index):
					subself.tick = tick

				def handleEvent(subself):
					boilerStillBoiling = False
					for boiler in terrain.tutorialMachineRoom.boilers:
						if boiler.isBoiling:
							boilerStillBoiling = True	
					if boilerStillBoiling:
						terrain.tutorialMachineRoom.addEvent(WaitForClearStart(gamestate.tick+2,0))
					else:
						cinematics.showCinematic("Libwig start now.")
						self.npc.assignQuest(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[0]))
						terrain.tutorialMachineRoom.addEvent(AnotherOne2(gamestate.tick+10,0))

			def tmp2():
				terrain.tutorialMachineRoom.addEvent(WaitForClearStart(gamestate.tick+2,0))

			questList[-1].endTrigger = tmp2
			self.npc.assignQuest(questList[0])

		class AnotherOne(object):
			def __init__(subself,tick,index):
				subself.tick = tick
				subself.furnaceIndex = index

			def handleEvent(subself):
				messages.append("another one")
				mainChar.assignQuest(quests.KeepFurnaceFired(terrain.tutorialMachineRoom.furnaces[subself.furnaceIndex],failTrigger=endMainChar))
				newIndex = subself.furnaceIndex+1
				self.mainCharFurnaceIndex = subself.furnaceIndex
				if newIndex < 8:
					terrain.tutorialMachineRoom.addEvent(AnotherOne(gamestate.tick+20,newIndex))

		def tmp():
			terrain.tutorialMachineRoom.addEvent(AnotherOne(gamestate.tick+1,0))

		questList[-1].endTrigger = tmp
		mainChar.assignQuest(questList[0])

	def end(self):
		messages.append("your Score: "+str(self.mainCharFurnaceIndex))
		messages.append("Libwigs Score: "+str(self.npcFurnaceIndex))

		for quest in self.npc.quests:
			quest.deactivate()
		self.npc.quests = []
		terrain.tutorialMachineRoom.removeEventsByType(self.anotherOne2)
		mainChar.assignQuest(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="please move back to the waiting position"))


		if self.npcFurnaceIndex > self.mainCharFurnaceIndex:
			cinematics.showCinematic("considering your Score until now moving you directly to your proper assignment is the most efficent Way for you to proceed.")
			phase3 = VatPhase()
			phase3.start()
		elif self.mainCharFurnaceIndex == 8:
			cinematics.showCinematic("you passed the test. in fact you passed the Test with a perfect Score. you will be valuable")
			phase3 = MachineRoomPhase()
			phase3.start()
		else:
			cinematics.showCinematic("you passed the test")
			phase3 = MachineRoomPhase()
			phase3.start()
phasesByName["ThirdTutorialPhase"] = ThirdTutorialPhase

class VatPhase(object):
	def __init__(self):
		self.name = "VatPhase"

	def start(self):
		gamestate.currentPhase = self
	
		questList = []
		if not (mainChar.room and mainChar.room == terrain.tutorialVat):
			questList.append(quests.EnterRoomQuest(terrain.tutorialVat,startCinematics="please goto the Vat"))

		questList.append(quests.MoveQuest(terrain.tutorialVat,3,3,startCinematics="please move back to the waiting position"))

		lastQuest = questList[0]
		for item in questList[1:]:
			lastQuest.followUp = item
			lastQuest = item
		questList[-1].followup = None

		questList[-1].endTrigger = self.end

		mainChar.assignQuest(questList[0])


	def end(self):
		cinematics.showCinematic("you seem to be able to follow orders after all. you may go back to your training.")
		MachineRoomPhase().start()
phasesByName["VatPhase"] = VatPhase

class MachineRoomPhase(object):
	def __init__(self):
		self.name = "MachineRoomPhase"

	def start(self):
		gamestate.currentPhase = self
	
		questList = []
		if not (mainChar.room and mainChar.room == terrain.tutorialMachineRoom):
			questList.append(quests.EnterRoomQuest(terrain.tutorialMachineRoom,startCinematics="please goto the Machineroom"))
		questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="time to do some actual work. report to {machine room supervisor}"))

		lastQuest = questList[0]
		for item in questList[1:]:
			lastQuest.followUp = item
			lastQuest = item
		questList[-1].followup = None

		questList[-1].endTrigger = self.end

		mainChar.assignQuest(questList[0])

	def end(self):
		gamestate.gameWon = True
phasesByName["MachineRoomPhase"] = MachineRoomPhase

gamestate = GameState()

try:
	gamestate.load()
except:
	pass
if gamestate.gameWon:
	gamestate = GameState()

mainChar = gamestate.mainChar
gamestate.currentPhase().start()

#cinematics.showCinematic("movement can be tricky sometimes so please make yourself comfortable with the controls.\n\nyou can move in 4 Directions along the x and y Axis. the z Axis is not supported yet. diagonal Movements are not supported since they do not exist.\n\nthe basic Movementcommands are:\n w=up\n a=right\n s=down\n d=right\nplease move to the designated Target. the Implant will mark your Way")
#"""
#*move back to waiting position*
#"""
#cinematics.showCinematic("you have 20 Ticks to familiarise yourself with the Movementcommands. please do.")
#cinematics.showCinematic("next on my Checklist is to explain the Interaction with your Environment\n\ninteraction with your Environment is somewhat complicated\n\nthe basic Interationcommands are:\n j=activate/apply\n e=examine\n k=pick up\n\nsee this Piles of Coal marked with ӫ on the rigth Side of the Room.\n\nwhenever you bump into an item that is to big to be walked on, you will promted for giving an extra interaction command. I'll give you an example:\n\nΩΩ＠ӫӫ\n\n pressing a and j would result in Activation of the Furnace\n pressing d and j would result in Activation of the Pile\n pressing a and e would result make you examine the Furnace\n pressing d and e would result make you examine the Pile\n\nplease grab yourself some Coal from a pile by bumping into it and pressing j afterwards.")
rooms.mainChar = mainChar
terrains.mainChar = mainChar

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
#npc2 = characters.Character(displayChars.staffCharacters[25],1,1,name="Ernst Ziegelbach")
#npc2.watched = True
#terrain.tutorialMachineRoom.addCharacter(npc2,1,1)
#npc2.terrain = terrain
#npc2.room = terrain.tutorialMachineRoom
#npc2.assignQuest(quest0)
#npc2.automated = False

characters = [mainChar]
items.characters = characters
rooms.characters = characters

movestate = "up"
def advanceGame():
	global movestate
	for character in terrain.characters:
		character.advance()

	for room in terrain.rooms:
		room.advance()

	if terrain.movingRoom.gogogo:
		if movestate == "up":
			terrain.movingRoom.moveNorth()
			if terrain.movingRoom.yPosition == 3 and terrain.movingRoom.offsetY == 2:
				movestate = "left"
		elif movestate == "left":
			terrain.movingRoom.moveWest()
			if terrain.movingRoom.xPosition == 2 and terrain.movingRoom.offsetX == 2:
				movestate = "down"
		elif movestate == "down":
			terrain.movingRoom.moveSouth()
			if terrain.movingRoom.yPosition == 6 and terrain.movingRoom.offsetY == 2:
				movestate = "right"
		elif movestate == "right":
			terrain.movingRoom.moveEast()
			if terrain.movingRoom.xPosition == 8 and terrain.movingRoom.offsetX == 2:
				movestate = "up"

	gamestate.tick += 1

cinematics.advanceGame = advanceGame

def renderQuests():
	char = mainChar
	txt = ""
	if len(char.quests):
		counter = 0
		for quest in char.quests:
			txt+= "QUEST: "+quest.description+"\n"
			counter += 1
			if counter == 2:
				break
		txt += str(char.xPosition)+"/"+str(char.yPosition)+" "+str(gamestate.tick)+" "+str(mainChar.inventory)
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
