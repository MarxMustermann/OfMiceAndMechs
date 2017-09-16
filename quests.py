showCinematic = None
loop = None
callShow_or_exit = None

class Quest(object):
	def __init__(self,followUp=None,startCinematics=None):
		self.followUp = followUp
		self.character = None
		self.listener = []
		self.active = False
		self.startCinematics = startCinematics
		self.endCinematics = None
		self.startTrigger = None
		self.endTrigger = None

	def triggerCompletionCheck(self):
		if not self.active:
			return 
		pass

	def solver(self,character):
		return character.walkPath()
	
	def postHandler(self):
		self.character.quests.remove(self)
		if self.endTrigger:
			self.endTrigger()
		if self.endCinematics:
			showCinematic(self.endCinematics)			
			loop.set_alarm_in(0.0, callShow_or_exit, '.')

		if self.character.watched:
			messages.append("Thank you kindly. @"+self.character.name)
		
		self.deactivate()

		if self.followUp:
			self.character.assignQuest(self.followUp,active=True)
		else:
			self.character.startNextQuest()

	def assignToCharacter(self,character):
		self.character = character
		self.recalculate()
		if self.active:
			self.character.setPathToQuest(self)

	def recalculate(self):
		if not self.active:
			return 

		self.triggerCompletionCheck()

	def changed(self):
		messages.append("QUEST: "+self.description+" changed")

	def addListener(self,listenFunction):
		if not listenFunction in self.listener:
			self.listener.append(listenFunction)

	def delListener(self,listenFunction):
		if listenFunction in self.listener:
			self.listener.remove(listenFunction)

	def activate(self):
		self.active = True
		if self.startTrigger:
			self.startTrigger()
		if self.startCinematics:
			showCinematic(self.startCinematics)			
			loop.set_alarm_in(0.0, callShow_or_exit, '.')

	def deactivate(self):
		self.active = False

class CollectQuest(Quest):
	def __init__(self,toFind="canBurn",startCinematics=None):
		self.toFind = toFind
		self.description = "please fetch things with property: "+toFind
		
		foundItem = None

		super().__init__(startCinematics=startCinematics)

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		foundItem = None
		for item in self.character.inventory:
			hasProperty = False
			try:
				hasProperty = getattr(item,self.toFind)
			except:
				continue
			
			if hasProperty:
				foundItem = item
				break

		if foundItem:
			self.postHandler()
			pass

	def assignToCharacter(self,character):
		super().assignToCharacter(character)
		character.addListener(self.recalculate)

	def recalculate(self):
		if hasattr(self,"dstX"):
			del self.dstX
		if hasattr(self,"dstY"):
			del self.dstY

		if not self.active:
			return 

		try:
			for item in self.character.room.itemsOnFloor:
				hasProperty = False
				try:
					hasProperty = getattr(item,self.toFind)
				except:
					continue
				
				if hasProperty:
					foundItem = item
					break

			if foundItem:
				self.dstX = foundItem.xPosition
				self.dstY = foundItem.yPosition
		except:
			pass
		super().recalculate()

class ActivateQuest(Quest):
	def __init__(self,toActivate,followUp=None,desiredActive=True,startCinematics=None):
		self.toActivate = toActivate
		self.toActivate.addListener(self.recalculate)
		self.description = "please activate the "+self.toActivate.name+" ("+str(self.toActivate.xPosition)+"/"+str(self.toActivate.yPosition)+")"
		self.dstX = self.toActivate.xPosition
		self.dstY = self.toActivate.yPosition
		self.desiredActive = desiredActive
		super().__init__(followUp,startCinematics=startCinematics)

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		if self.toActivate.activated == self.desiredActive:
			self.postHandler()

	def recalculate(self):
		if not self.active:
			return 

		if hasattr(self,"dstX"):
			del self.dstX
		if hasattr(self,"dstY"):
			del self.dstY
		if hasattr(self,"toActivate"):
			if hasattr(self.toActivate,"xPosition"):
				self.dstX = self.toActivate.xPosition
			if hasattr(self.toActivate,"xPosition"):
				self.dstY = self.toActivate.yPosition
		super().recalculate()

class MoveQuest(Quest):
	def __init__(self,room,x,y,followUp=None,startCinematics=None):
		self.dstX = x
		self.dstY = y
		self.targetX = x
		self.targetY = y
		self.room = room
		self.description = "please go to coordinate "+str(self.dstX)+"/"+str(self.dstY)	
		super().__init__(followUp,startCinematics=startCinematics)

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		if hasattr(self,"dstX") and hasattr(self,"dstY"):
			if self.character.xPosition == self.dstX and self.character.yPosition == self.dstY:
				self.postHandler()

	def assignToCharacter(self,character):
		super().assignToCharacter(character)
		character.addListener(self.recalculate)

	def recalculate(self):
		if not self.active:
			return 

		if hasattr(self,"dstX"):
			del self.dstX
		if hasattr(self,"dstY"):
			del self.dstY

		if self.room == self.character.room:
			self.dstX = self.targetX
			self.dstY = self.targetY
		elif self.character.room and self.character.quests[0] == self:
			self.character.assignQuest(LeaveRoomQuest(self.character.room),active=True)
		elif not self.character.room and self.character.quests[0] == self:
			self.character.assignQuest(EnterRoomQuest(self.room),active=True)
			pass
		super().recalculate()

class LeaveRoomQuest(Quest):
	def __init__(self,room,followUp=None,startCinematics=None):
		self.room = room
		self.description = "please leave the room."
		self.dstX = self.room.walkingAccess[0][0]
		self.dstY = self.room.walkingAccess[0][1]
		super().__init__(followUp,startCinematics=startCinematics)

	def solver(self,character):
		if super().solver(character):
			if character.room:
				character.room.itemByCoordinates[(character.xPosition,character.yPosition)].close()
				if character.yPosition == 0:
					character.path.append((character.xPosition,character.yPosition-1))
				else:
					character.path.append((character.xPosition,character.yPosition+1))
				character.walkPath()
				return False
			return True

	def assignToCharacter(self,character):

		super().assignToCharacter(character)
		character.addListener(self.recalculate)

		super().recalculate()

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		if not self.character:
			return

		if not self.character.room == self.room:
			self.postHandler()

class EnterRoomQuest(Quest):
	def __init__(self,room,followUp=None,startCinematics=None):
		self.description = "please enter the room: "+room.name
		self.room = room
		self.dstX = self.room.walkingAccess[0][0]+room.xPosition*15+room.offsetX
		self.dstY = self.room.walkingAccess[0][1]+room.yPosition*15+room.offsetY
		super().__init__(followUp,startCinematics=startCinematics)

	def assignToCharacter(self,character):
		super().assignToCharacter(character)
		character.addListener(self.recalculate)

	def solver(self,character):
		return character.walkPath()

	def recalculate(self):
		if not self.active:
			return 

		if self.character.room and not self.character.room == self.room and self.character.quests[0] == self:
			self.character.assignQuest(LeaveRoomQuest(self.character.room),active=True)

		super().recalculate()

	def triggerCompletionCheck(self):
		if not self.active:
			return 

		if self.character.room == self.room:
			self.postHandler()
