mainChar = None
messages = None

class Terrain(object):
	def __init__(self,rooms,layout):
		self.rooms = rooms
		for room in self.rooms:
			room.terrain = self
		self.layout = layout
		self.characters = []

	def render(self):
		global mapHidden
		chars = []
		for i in range(0,30):
			line = []
			for j in range(0,30):
				line.append("  ")
			chars.append(line)

		if mainChar.room == None:
			mapHidden = False
		else:
			if mainChar.room.open:
				mapHidden = False
			else:
				mapHidden = True

		for room in self.rooms:
			if mainChar.room == room:
				room.hidden = False
			else:
				if not mapHidden and room.open:
					room.hidden = False
				else:
					room.hidden = True
				
		if not mapHidden:
			lineCounter = 0
			for layoutline in self.layout.split("\n")[1:]:
				rowCounter = 0
				for char in layoutline:
					if char == "X":
						chars[lineCounter][rowCounter] = "⛝ "
					if char == "0":
						chars[lineCounter][rowCounter] = "✠✠"
					if char in (".",","):
						chars[lineCounter][rowCounter] = "⛚ "
					rowCounter += 1
				lineCounter += 1
		

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
X0,,,,,,,,,,,0000,,,,,,,,,,000
X0............................ 
X0,,,,,,,,,,,,,,,,,,,,,,,,,,00
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
