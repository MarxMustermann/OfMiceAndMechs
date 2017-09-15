import items

mainChar = None
messages = None

class Terrain(object):
	def __init__(self,rooms,layout):
		self.itemsOnFloor = []
		self.characters = []
		self.walkingPath = []

		self.rooms = rooms
		for room in self.rooms:
			room.terrain = self

		self.layout = layout
		lineCounter = 0
		for layoutline in self.layout.split("\n")[1:]:
			rowCounter = 0
			for char in layoutline:
				if char in (" ",".",",","@"):
					pass
				elif char == "X":
					self.itemsOnFloor.append(items.Wall(rowCounter,lineCounter))
				elif char == "#":
					self.itemsOnFloor.append(items.Pipe(rowCounter,lineCounter))
				else:
					displayChars = ["🝍🝍","🝍🝍","🝍🝍","🖵 ","🞇 ","🖵 ","⿴","⿴","🞇 ","🜕 "]
					self.itemsOnFloor.append(items.Item(displayChars[((2*rowCounter)+lineCounter)%10],rowCounter,lineCounter))
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

	def render(self):
		global mapHidden
		if mainChar.room == None:
			mapHidden = False
		else:
			if mainChar.room.open:
				mapHidden = False
			else:
				mapHidden = True

		chars = []
		for i in range(0,30):
			line = []
			for j in range(0,30):
				if not mapHidden:
					line.append("::")
				else:
					line.append("  ")
			chars.append(line)

		for room in self.rooms:
			if mainChar.room == room:
				room.hidden = False
			else:
				if not mapHidden and room.open:
					room.hidden = False
				else:
					room.hidden = True
				
		if not mapHidden:
			for item in self.itemsOnFloor:
				chars[item.yPosition][item.xPosition] = item.display

		for room in self.rooms:
			if mapHidden and room.hidden :
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
				if len(mainChar.quests):
					try:
						path = calculatePath(mainChar.xPosition,mainChar.yPosition,mainChar.quests[0].dstX,mainChar.quests[0].dstY)
						for item in path[:-1]:
							chars[item[1]][item[0]] = "xx"
					except:
						pass


		return chars

class Terrain1(Terrain):
	def __init__(self,rooms):
		layout = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X#############XX############ X
X#           #XX#          # X
X#           #XX#          # X
X#           #XX#          # X
X#           #XX#          # X
X#           #XX#          # X
X#           #XX#          # X
X#           #XX#          # X
X#           #XX#          # X
X#           #XX#          # X
X#XXXXXXXXXXX#XX#XXXXXXXXXX#XX
X#,,,,,,,,,,,####,,,,,,,,,,###
X#............................
X#,,,,,,,,,,,,,,,,,,,,,,,,,,##
X#XXXXXXXXXXXXX XXX,XXXXXXXX#X
X#           #X X X,X       #X
X#           #X X XXX       #X
X#           #X X           #X
X#           #X X           #X
X#           #X X           #X
X#           #X X           #X
X#           #X X           #X
X#           #X X           #X
X#           #X X           #X
X#########   #X X           #X
X            #X X           #X
#############################X
XXXXXXXXXXXX#XX XXXXXXXXXXXXXX
"""
		super().__init__(rooms,layout)
