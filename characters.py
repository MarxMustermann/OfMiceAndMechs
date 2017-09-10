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
			quest.activate()
			if active:
				self.quests.insert(0,quest)
			else:
				self.quests.append(quest)
			quest.assignToCharacter(self)
			if self.automated and (active or len(self.quests) == 1):
				try:
					self.setPathToQuest(quest)
				except:
					pass

			if self.watched:
				messages.append(self.name+": got a new Quest\n - "+quest.description)

	def setPathToQuest(self,quest):
		if hasattr(quest,"dstX") and hasattr(quest,"dstY"):
			self.path = calculatePath(self.xPosition,self.yPosition,quest.dstX,quest.dstY)

	def addToInventory(self,item):
		self.inventory.append(item)

	def advance(self):
		if self.automated:
			if self.yPosition == 0:
				roomsOnMap[1].removeCharacter(self)
				roomsOnMap[0].addCharacter(self,4,8)
				self.changed()
				return

			if self.yPosition == 9:
				roomsOnMap[0].removeCharacter(self)
				roomsOnMap[1].addCharacter(self,4,1)
				self.changed()
				return
				
			if hasattr(self,"path") and len(self.path):
				self.xPosition = self.path[0][0]
				self.yPosition = self.path[0][1]
				self.path = self.path[1:]
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
