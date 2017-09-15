import items

mainChar = None
messages = None

class Terrain(object):
	def __init__(self,rooms,layout):
		self.itemsOnFloor = []
		self.characters = []

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
