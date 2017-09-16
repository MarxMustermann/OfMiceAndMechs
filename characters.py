characters = None
calculatePath = None
roomsOnMap = None

class Character():
	def __init__(self,display="＠",xPosition=0,yPosition=0,quests=[],automated=True,name="Person"):
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
			if active:
				self.quests.insert(0,quest)
			else:
				self.quests.append(quest)
			quest.assignToCharacter(self)
			quest.activate()
			if (active or len(self.quests) == 1):
				try:
					self.setPathToQuest(quest)
				except:
					pass

			if self.watched:
				messages.append(self.name+": got a new Quest\n - "+quest.description)

	def setPathToQuest(self,quest):
		if hasattr(quest,"dstX") and hasattr(quest,"dstY"):
			if self.room:
				self.path = calculatePath(self.xPosition,self.yPosition,quest.dstX,quest.dstY,self.room.walkingPath)
			else:
				self.path = calculatePath(self.xPosition,self.yPosition,quest.dstX,quest.dstY,self.terrain.walkingPath)

	def addToInventory(self,item):
		self.inventory.append(item)

	def applysolver(self,solver):
		solver(self)

	def walkPath(self):
		if not len(self.path):
			self.setPathToQuest(self.quests[0])

		if len(self.path):
			currentPosition = (self.xPosition,self.yPosition)
			nextPosition = self.path[0]

			item = None
			if self.room:
				if nextPosition[0] < currentPosition[0]:
					item = self.room.moveCharacterWest(self)
				elif nextPosition[0] > currentPosition[0]:
					item = self.room.moveCharacterEast(self)
				elif nextPosition[1] < currentPosition[1]:
					item = self.room.moveCharacterNorth(self)
				elif nextPosition[1] > currentPosition[1]:
					item = self.room.moveCharacterSouth(self)

			else:
				for room in self.terrain.rooms:
					if room.yPosition*15+room.offsetY+10 == nextPosition[1]+1:
						if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+10 > self.xPosition:
							localisedEntry = (self.xPosition%15-room.offsetX,nextPosition[1]%15-room.offsetY)
							if localisedEntry in room.walkingAccess:
								if localisedEntry in room.itemByCoordinates and not room.itemByCoordinates[localisedEntry].walkable:
									item = room.itemByCoordinates[localisedEntry]
									break
								else:
									room.addCharacter(self,localisedEntry[0],localisedEntry[1]+1)
									self.terrain.characters.remove(self)
									self.terrain = None
									self.changed()
									break
							else:
								messages.append("you cannot move there")
								break
					if room.yPosition*15+room.offsetY == nextPosition[1]:
						if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+10 > self.xPosition:
							localisedEntry = ((self.xPosition-room.offsetX)%15,((nextPosition[1]-room.offsetY)%15))
							if localisedEntry in room.walkingAccess:
								if localisedEntry in room.itemByCoordinates and not room.itemByCoordinates[localisedEntry].walkable:
									item = room.itemByCoordinates[localisedEntry]
									break
								else:
									room.addCharacter(self,localisedEntry[0],localisedEntry[1]-1)
									self.terrain.characters.remove(self)
									self.terrain = None
									self.changed()
									break
				else:
					self.xPosition = nextPosition[0]
					self.yPosition = nextPosition[1]
					self.changed()
			
			if item:
				item.apply()				
			else:
				if (self.xPosition == nextPosition[0] and self.yPosition == nextPosition[1]):
					self.path = self.path[1:]
			return False
		else:
			return True

	def advance(self):
		if self.automated:

			"""
			if self.yPosition == 0:
				self.room.removeCharacter(self)
				roomsOnMap[0].addCharacter(self,4,8)
				self.changed()
				return

			if self.yPosition == 9:
				self.room.removeCharacter(self)
				roomsOnMap[1].addCharacter(self,4,1)
				self.changed()
				return
			"""
	
			self.applysolver(self.quests[0].solver)
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
