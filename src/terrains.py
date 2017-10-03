import src.items as items
import src.rooms as rooms

mainChar = None
messages = None
displayChars = None

class Terrain(object):
	def __init__(self,rooms,detailedLayout):
		self.itemsOnFloor = []
		self.characters = []
		self.walkingPath = []

		self.rooms = rooms
		for room in self.rooms:
			room.terrain = self

		self.detailedLayout = detailedLayout
		lineCounter = 0
		for layoutline in self.detailedLayout.split("\n")[1:]:
			rowCounter = 0
			for char in layoutline:
				if char in (" ",".",",","@"):
					pass
				elif char == "X":
					self.itemsOnFloor.append(items.Wall(rowCounter,lineCounter))
				elif char == "#":
					self.itemsOnFloor.append(items.Pipe(rowCounter,lineCounter))
				elif char == "R":
					pass
				elif char == "O":
					self.itemsOnFloor.append(items.Item(displayChars.clamp_active,rowCounter,lineCounter))
				elif char == "0":
					self.itemsOnFloor.append(items.Item(displayChars.clamp_inactive,rowCounter,lineCounter))
				else:
					self.itemsOnFloor.append(items.Item(displayChars.randomStuff2[((2*rowCounter)+lineCounter)%10],rowCounter,lineCounter))
				rowCounter += 1
			lineCounter += 1

		rawWalkingPath = []
		lineCounter = 0
		for line in self.detailedLayout[1:].split("\n"):
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
		for i in range(0,250):
			line = []
			for j in range(0,250):
				if not mapHidden:
					line.append(displayChars.floor)
				else:
					line.append(displayChars.void)
			chars.append(line)

		for room in self.rooms:
			if mainChar.room == room:
				room.hidden = False
			else:
				if not mapHidden and room.open:
					room.hidden = False
					room.applySkippedAdvances()
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

		if not mapHidden:
			for character in self.characters:
				chars[character.yPosition][character.xPosition] = character.display

				if character == mainChar:
					if len(mainChar.quests):
						try:
							path = calculatePath(mainChar.xPosition,mainChar.yPosition,mainChar.quests[0].dstX,mainChar.quests[0].dstY,self.walkingPath)
							for item in path[:-1]:
								chars[item[1]][item[0]] = displayChars.pathMarker
						except:
							pass

		return chars

class TutorialTerrain(Terrain):
	def __init__(self):

		detailedLayout = """
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                  ###  ###        ######                                                                                                     XXXXXXXXX               
               ####O####O####  ####O  O########  O    O   #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # RRRRRRRRRR #  #RRRRRRRRRR#   #RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #ORRRRRRRRRRO# ##RRRRRRRRRR## ##RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # RRRRRRRRRR # #ORRRRRRRRRRO# #ORRRRRRRRRRO#XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # RRRRRRRRRR # # RRRRRRRRRR # ##RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #ORRRRRRRRRRO# # RRRRRRRRRR #  #RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # RRRRRRRRRR # # RRRRRRRRRR # ##RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               # RRRRRRRRRR ### RRRRRRRRRR # #ORRRRRRRRRRO#XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #ORRRRRRRRRRO ##ORRRRRRRRRRO# ##RRRRRRRRRR #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               ##RRRRRRRRRR# ###RRRRRRRRRR##  #RRRRRRRRRR#####           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
                 RRRRRRRRRR  #  RRRRRRRRRR     RRRRRRRRRR XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               XX  O    O    ####O#...##O####    O    O    X                                                                                                         
               XX...............###.X..###................                                                                                                           
                ..X  O   O     .....XX.....##            . X                                                                                                        
               X.XORRRRRRRRRRO     XXX     #     XXXXXXX . XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               ..  RRRRRRRRRR#  O  XO  O   ####X O   O X.. XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               .XXORRRRRRRRRR# RRRRRRRRRRR ## RRRRRRRRRR.###X#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               ....RRRRRRRRRR#ORRRRRRRRRRRO## RRRRRRRRRR..#XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.RRRRRRRRRR# RRRRRRRRRRR ##ORRRRRRRRRRO.#XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               ....RRRRRRRRRR##RRRRRRRRRRR ## RRRRRRRRRR .#XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               .XXORRRRRRRRRRO#RRRRRRRRRRRO## RRRRRRRRRR .#XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               ....RRRRRRRRRR##RRRRRRRRRRR ##ORRRRRRRRRRO..XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.RRRRRRRRRR# RRRRRRRRRRR ## RRRRRRRRRR #.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               ....RRRRRRRRRR#ORRRRRRRRRRRO## RRRRRRRRRR##.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               .XXXX O   O   # RRRRRRRRRRR ##ORRRRRRRRRRO..XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               ....          #   O  O  O   ## RRRRRRRRRR..#XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.          ##################  O   O  .##XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               ....X                          #         .. XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               .XXXX                                     . X                                                                                                         
               ........................................... X                                                                                                         
               X                                           X                                                                                                         
               X#           #X X XXX       #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X#           #X X           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X#           #X X           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X#           #X X           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X#           #X X           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X#           #X X           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X#           #X X           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X#           #X X           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X#           #X X           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X#           #X X           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X            #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               ##############XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXXXXXXXXXXX#XXX#XXXXXXXXXXX#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               X.XXXXXXXXXXXXXXXX XXXXXXX . XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               X...X        XX##X X     X.. XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#XX X     X.###X#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.XXX        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X...XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.XXX        XX#X        X #.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X##.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X#####   XX#X        X...XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.##XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #.XXX#########X##        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.. XXXXXXXX#XXX#XXXXXXXXX.. XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               X.XXXXXXXXXXXXXXXX XXXXXXX . XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               X...X        XX##X X     X.. XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#XX X     X.###X#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.XXX        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X...XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.XXX        XX#X        X #.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X##.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X#####   XX#X        X...XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.##XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #.XXX#########X##        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.. XXXXXXXX#XXX#XXXXXXXXX.. XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               X.XXXXXXXXXXXXXXXX XXXXXXX . XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               X...X        XX##X X     X.. XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#XX X     X.###X#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.XXX        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X...XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X...XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.XXX        XX#X        X #.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X##.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X#####   XX#X        X...XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.##XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #.XXX#########X##        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.. XXXXXXXX#XXX#XXXXXXXXX.. XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               X.XXXXXXXXXXXXXXXX XXXXXXX . XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               X...X        XX##X X     X.. XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#XX X     X.###X#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.XXX        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X...XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.XXX        XX#X        X #.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X##.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X#####   XX#X        X...XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.##XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #.XXX#########X##        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.. XXXXXXXX#XXX#XXXXXXXXX.. XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               X.XXXXXXXXXXXXXXXX XXXXXXX . XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
               X...X        XX##X X     X.. XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#XX X     X.###X#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.XXX        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X        XX#X        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X...XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.XXX        XX#X        X #.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X##.XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               XXX.X#####   XX#X        X...XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X...X        XX#X        X.##XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               #.XXX#########X##        X.# XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #XX#           #X               
               X.. XXXXXXXX#XXX#XXXXXXXXX.. XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX               
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
                                                                                                                                                                    
"""

		hull = []
		for i in range(0,10):
			hull.append(rooms.MechArmor(0,i,0,0))
			hull.append(rooms.MechArmor(9,i,0,0))
		for i in range(1,9):
			hull.append(rooms.MechArmor(i,0,0,0))
			hull.append(rooms.MechArmor(i,9,0,0))

		self.tutorialVat = rooms.Vat2(1,1,2,2)
		self.tutorialMachineRoom = rooms.TutorialMachineRoom(1,2,4,0)
		room3 = rooms.Vat1(2,1,2,2)
		room4 = rooms.InfanteryQuarters(2,2,1,2)

		room5 = rooms.CpuWasterRoom(1,3,2,2)
		room6 = rooms.CpuWasterRoom(2,3,2,2)
		room7 = rooms.Room1(3,1,2,2)
		room8 = rooms.CpuWasterRoom(3,2,1,2)
		room9 = rooms.CpuWasterRoom(3,3,2,2)

		roomsOnMap = [self.tutorialVat,self.tutorialMachineRoom,room3,room4,room5,room6,room7,room8,room9]
		roomsOnMap.extend(hull)

		for i in range(1,9):
			for j in range(1,9):
				if not (i < 4 and j < 4):
					roomsOnMap.append(rooms.CpuWasterRoom(i,j,2,2))

		super().__init__(roomsOnMap,detailedLayout)

