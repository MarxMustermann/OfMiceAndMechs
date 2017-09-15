import urwid 
import items 
import quests
import rooms
import characters
import terrains
import cinematics

header = urwid.Text(u"")
main = urwid.Text(u"＠")
cinematics.main = main
footer = urwid.Text(u"")

cinematics.quests = quests

def callShow_or_exit(loop,key):
	show_or_exit(key)

itemMarkedLast = None
def show_or_exit(key):
	if not len(key) == 1:
		return
	global itemMarkedLast
	stop = False
	if len(cinematics.cinematicQueue):
		if key in ('q', 'Q'):
			raise urwid.ExitMainLoop()
		elif key in (' '):
			cinematics.cinematicQueue = cinematics.cinematicQueue[1:]
			loop.set_alarm_in(0.0, callShow_or_exit, '~')
		else:
			stop = True
			cinematics.cinematicQueue[0].advance()
	if stop:
		return
	if key in ('~'):
		return

	if key in ('q', 'Q'):
		raise urwid.ExitMainLoop()
	if key in ('w'):
		if mainChar.room:
			item = mainChar.room.moveCharacterNorth(mainChar)

			if item:
				messages.append("You cannot walk there")
				messages.append("press j to apply")
				itemMarkedLast = item
				footer.set_text(renderMessagebox())
				return
		else:
			for room in terrain.rooms:
				if room.yPosition*15+room.offsetY+10 == mainChar.yPosition:
					if room.xPosition*15+room.offsetX < mainChar.xPosition and room.xPosition*15+room.offsetX+10 > mainChar.xPosition:
						localisedEntry = (mainChar.xPosition%15-room.offsetX,mainChar.yPosition%15-room.offsetY-1)
						if localisedEntry in room.walkingAccess:
							if localisedEntry in room.itemByCoordinates and not room.itemByCoordinates[localisedEntry].walkable:
								itemMarkedLast = room.itemByCoordinates[localisedEntry]
								messages.append("you need to open the door first")
								messages.append("press j to apply")
								footer.set_text(renderMessagebox())
								return
							else:
								room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
								terrain.characters.remove(mainChar)
								break

						else:
							messages.append("you cannot move there")
							break
			else:
				characters[0].yPosition -= 1
				characters[0].changed()

	if key in ('s'):
		if mainChar.room:
			item = mainChar.room.moveCharacterSouth(mainChar)

			if item:
				messages.append("You cannot walk there")
				messages.append("press j to apply")
				itemMarkedLast = item
				footer.set_text(renderMessagebox())
				return
			"""
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
				characters[0].changed()
			"""
		else:
			for room in terrain.rooms:
				if room.yPosition*15+room.offsetY == mainChar.yPosition+1:
					if room.xPosition*15+room.offsetX < mainChar.xPosition and room.xPosition*15+room.offsetX+10 > mainChar.xPosition:
						localisedEntry = ((mainChar.xPosition-room.offsetX)%15,(mainChar.yPosition-room.offsetY+1)%15)
						if localisedEntry in room.walkingAccess:
							if localisedEntry in room.itemByCoordinates and not room.itemByCoordinates[localisedEntry].walkable:
								itemMarkedLast = room.itemByCoordinates[localisedEntry]
								messages.append("you need to open the door first")
								messages.append("press j to apply")
								footer.set_text(renderMessagebox())
								return
							else:
								room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
								terrain.characters.remove(mainChar)
								break
			else:
				characters[0].yPosition += 1
				characters[0].changed()

	if key in ('d'):
		item = None
		if mainChar.room:
			item = mainChar.room.moveCharacterEast(mainChar)
		else:
			characters[0].xPosition += 1
			characters[0].changed()

		if item:
			messages.append("You cannot walk there")
			messages.append("press j to apply")
			itemMarkedLast = item
			footer.set_text(renderMessagebox())
			return

	if key in ('a'):
		item = None
		if mainChar.room:
			item = mainChar.room.moveCharacterWest(mainChar)
		else:
			characters[0].xPosition -= 1
			characters[0].changed()

		if item:
			messages.append("You cannot walk there")
			messages.append("press j to apply")
			itemMarkedLast = item
			footer.set_text(renderMessagebox())
			return

		"""
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
		"""

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
		circlePath = False
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

messages = []
items.messages = messages
quests.messages = messages
rooms.messages = messages
characters.messages = messages
terrains.messages = messages
cinematics.messages = messages

quests.showCinematic = cinematics.showCinematic

cinematics.showCinematic("welcome to the Trainingenvironment\n\nplease, try to learn fast.\n\nParticipants with low Evaluationscores will be given suitable Assignments in the Vats")

room1 = rooms.Room1()
room2 = rooms.Room2()
room3 = rooms.Room3()
room4 = rooms.GenericRoom(1,1,2,2)

roomsOnMap = [room1,room2,room3,room4]
characters.roomsOnMap = roomsOnMap

terrain = terrains.Terrain1(roomsOnMap)

mapHidden = True

tutorialQuest1 = quests.MoveQuest(room2,5,7,startCinematics="inside the Simulationchamber everything has to be taught from Scratch\n\nthe basic Movementcommands are:\n\n w=up\n a=right\n s=down\n d=right\n\nplease move to the designated Target. the Implant will mark your Way")
tutorialQuest2 = quests.CollectQuest(startCinematics="interaction with your Environment ist somewhat complicated\n\nthe basic Interationcommands are:\n\n j=activate/apply\n e=examine\n k=pick up\n\nsee this Piles of Coal marked with ӫ on the rigth Side of the room.\n\nplease grab yourself some Coal from a pile by moving onto it and pressing j.")
tutorialQuest3 = quests.ActivateQuest(room2.furnace,startCinematics="now go and activate the Furnace marked with a Ω. you need to have burnable Material like Coal in your Inventory\n\nso ensure that you have some Coal in your Inventory go to the Furnace and press j.")
tutorialQuest4 = quests.MoveQuest(room2,1,3,startCinematics="Move back to waiting position")
tutorialQuest5 = quests.LeaveRoomQuest(room2,startCinematics="please exit the Room")
tutorialQuest5 = quests.EnterRoomQuest(room1,startCinematics="please goto the Vat")
tutorialQuest6 = quests.MoveQuest(room1,4,4,startCinematics="please move to waiting position")

tutorialQuest1.followUp = tutorialQuest2
tutorialQuest2.followUp = tutorialQuest3
tutorialQuest3.followUp = tutorialQuest4
tutorialQuest4.followUp = tutorialQuest5
tutorialQuest5.followUp = tutorialQuest6
tutorialQuest6.followUp = None

mainQuests = [tutorialQuest1]
mainChar = characters.Character("＠",1,3,automated=False,name="Sigmund Bärenstein")
mainChar.terrain = terrain
mainChar.watched = True
rooms.mainChar = mainChar
terrains.mainChar = mainChar
room2.addCharacter(mainChar,2,4)
mainChar.assignQuest(tutorialQuest1)

quest0 = quests.MoveQuest(room2,7,7)
quest1 = quests.MoveQuest(room1,4,4)
quest2 = quests.MoveQuest(room3,6,6)
quest3 = quests.MoveQuest(room4,2,8)
quest0.followUp = quest1
quest1.followUp = quest2
quest2.followUp = quest3
quest3.followUp = quest0
npc2 = characters.Character("Ⓩ ",1,1,name="Ernst Ziegelbach")
#npc2.watched = True
room2.addCharacter(npc2,1,1)
npc2.terrain = terrain
npc2.assignQuest(quest0)

characters = [mainChar]
items.characters = characters
rooms.characters = characters

gamestate = GameState(characters)

def advanceGame():
	for character in terrain.characters:
		character.advance()
	for room in roomsOnMap:
		for character in room.characters:
			character.advance()

def renderQuests():
	txt = ""
	if len(characters[0].quests):
		for quest in mainChar.quests:
			txt+= "QUEST: "+quest.description+"\n"
		txt += str(mainChar.xPosition)+"/"+str(mainChar.yPosition)
	else:
		txt += "QUEST: keinQuest\n\n"
		gamestate.gameWon = True
		loop.set_alarm_in(0.0, callShow_or_exit, '~')
	return txt
	
def renderMessagebox():
	txt = ""
	for message in messages[-5:]:
		txt += str(message)+"\n"
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

loop.set_alarm_in(0.0, callShow_or_exit, '~')
loop.run()
