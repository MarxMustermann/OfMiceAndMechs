messages = None
characters = None
displayChars = None
stealKey = None
commandChars = None
terrain = None

class Item(object):
	def __init__(self,display=None,xPosition=0,yPosition=0,name="item"):
		if not display:
			self.display = displayChars.notImplentedYet
		else:
			self.display = display
		self.xPosition = xPosition
		self.yPosition = yPosition
		self.listeners = []
		self.walkable = False
		self.room = None
		self.lastMovementToken = None
		self.chainedTo = []
		self.name = name

		self.description = "a "+self.name

	def getDetailedInfo(self):
		return str(self.getDetailedState)

	def getDetailedState(self):
		return self

	def apply(self,character):
		messages.append("i can't do anything useful with this")

	def changed(self):
		messages.append(self.name+": Object changed")
		for listener in self.listeners:
			listener()

	def addListener(self,listenFunction):
		if not listenFunction in self.listeners:
			self.listeners.append(listenFunction)

	def delListener(self,listenFunction):
		if listenFunction in self.listeners:
			self.listeners.remove(listenFunction)

	def getAffectedByMovementNorth(self,force=1,movementBlock=set()):
		movementBlock.add(self)
		
		for thing in self.chainedTo:
			if thing not in movementBlock and not thing == self:
				movementBlock.add(thing)
				thing.getAffectedByMovementNorth(force=force,movementBlock=movementBlock)

		return movementBlock

	def moveNorth(self,force=1,initialMovement=True):
		self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
		if len(self.terrain.itemByCoordinates) == 0:
			del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]
		self.yPosition -= 1
		if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
			self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
		else:
			self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

	def getAffectedByMovementSouth(self,force=1,movementBlock=set()):
		movementBlock.add(self)
		
		for thing in self.chainedTo:
			if thing not in movementBlock and not thing == self:
				movementBlock.add(thing)
				thing.getAffectedByMovementSouth(force=force,movementBlock=movementBlock)

		return movementBlock

	def moveSouth(self,force=1,initialMovement=True):
		self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
		if len(self.terrain.itemByCoordinates) == 0:
			del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]

		self.yPosition += 1
		if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
			self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
		else:
			self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

	def getAffectedByMovementWest(self,force=1,movementBlock=set()):
		movementBlock.add(self)
		
		for thing in self.chainedTo:
			if thing not in movementBlock and not thing == self:
				movementBlock.add(thing)
				thing.getAffectedByMovementWest(force=force,movementBlock=movementBlock)

		return movementBlock

	def moveWest(self,force=1,initialMovement=True):
		self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
		if len(self.terrain.itemByCoordinates) == 0:
			del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]

		self.xPosition -= 1
		if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
			self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
		else:
			self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

	def getAffectedByMovementEast(self,force=1,movementBlock=set()):
		movementBlock.add(self)
		
		for thing in self.chainedTo:
			if thing not in movementBlock and not thing == self:
				movementBlock.add(thing)
				thing.getAffectedByMovementEast(force=force,movementBlock=movementBlock)

		return movementBlock

	def moveEast(self,force=1,initialMovement=True):
		self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
		if len(self.terrain.itemByCoordinates) == 0:
			del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]
		self.xPosition += 1
		if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
			self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
		else:
			self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

	def getResistance(self):
		if (self.walkable):
			return 1
		else:
			return 50

class Corpse(Item):
	def __init__(self,xPosition=0,yPosition=0,name="corpse"):
		super().__init__(displayChars.corpse,xPosition,yPosition)
		self.walkable = True

class Hutch(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Hutch",activated=False):
		self.activated = activated
		if self.activated:
			super().__init__(displayChars.hutch_free,xPosition,yPosition)
		else:
			super().__init__(displayChars.hutch_occupied,xPosition,yPosition)

	def apply(self,character):
		if not self.activated:
			self.activated = True
			self.display = displayChars.hutch_occupied
		else:
			self.activated = False
			self.display = displayChars.hutch_free

class Lever(Item):
	def __init__(self,xPosition=0,yPosition=0,name="lever",activated=False):
		self.activated = activated
		self.display = {True:displayChars.lever_pulled,False:displayChars.lever_notPulled}
		super().__init__(displayChars.lever_notPulled,xPosition,yPosition,name=name)
		self.activateAction = None
		self.deactivateAction = None
		self.walkable = True

	def apply(self,character):
		if not self.activated:
			self.activated = True
			self.display = displayChars.lever_pulled
			messages.append(self.name+": activated!")

			if self.activateAction:
				self.activateAction(self)
		else:
			self.activated = False
			self.display = displayChars.lever_notPulled
			messages.append(self.name+": deactivated!")

			if self.deactivateAction:
				self.activateAction(self)
		self.changed()

class Furnace(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Furnace"):
		self.activated = False
		self.boilers = None
		self.stopBoilingEvent = None
		super().__init__(displayChars.furnace_inactive,xPosition,yPosition,name=name)

	def apply(self,character):
		messages.append("Furnace used")
		foundItem = None
		for item in character.inventory:
			try:
				canBurn = item.canBurn
			except:
				continue
			if not canBurn:
				continue

			foundItem = item

		if not foundItem:
			messages.append("keine KOHLE zum anfeuern")
		else:
			if self.activated:
				messages.append("already burning")
			else:
				self.activated = True
				self.display = displayChars.furnace_active
				character.inventory.remove(foundItem)
				messages.append("*wush*")

				class BoilerBoilingEvent(object):
					def __init__(subself,tick):
						subself.tick = tick
					
					def handleEvent(subself):
						messages.append("*boil*")
						for boiler in self.boilers:
							boiler.display = displayChars.boiler_active

				class BoilerStopBoilingEvent(object):
					def __init__(subself,tick):
						subself.tick = tick
					
					def handleEvent(subself):
						messages.append("*unboil*")
						for boiler in self.boilers:
							boiler.display = displayChars.boiler_inactive
						self.stopBoilingEvent = None

				class FurnaceBurnoutEvent(object):
					def __init__(subself,tick):
						subself.tick = tick

					def handleEvent(subself):
						self.activated = False
						self.display = displayChars.furnace_inactive
						self.stopBoilingEvent = BoilerStopBoilingEvent(self.room.timeIndex+5)
						self.room.addEvent(self.stopBoilingEvent)
						self.changed()

				if self.boilers == None:
					self.boilers = []
					for boiler in self.room.boilers:
						if ((boiler.xPosition in [self.xPosition,self.xPosition-1,self.xPosition+1] and boiler.yPosition == self.yPosition) or boiler.yPosition in [self.yPosition-1,self.yPosition+1] and boiler.xPosition == self.xPosition):
							self.boilers.append(boiler)

				if self.stopBoilingEvent == None:
					self.room.addEvent(BoilerBoilingEvent(self.room.timeIndex+5))
				else:
					self.room.removeEvent(self.stopBoilingEvent)
				self.room.addEvent(FurnaceBurnoutEvent(self.room.timeIndex+20))

				self.changed()

class Commlink(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Commlink"):
		super().__init__(displayChars.commLink,xPosition,yPosition,name=name)

	def apply(self,character):
		messages.append("Sigmund Bärenstein@Logisticcentre: we need more coal")
		messages.append("Logisticcentre@Sigmund Bärenstein: on its way")
	
		class CoalRefillEvent(object):
			def __init__(subself,tick):
				subself.tick = tick

			def handleEvent(subself):
				messages.append("*rumbling*")
				messages.append("*rumbling*")
				messages.append("*smoke and dust on cole piles and neighbour fields*")
				messages.append("*a chunk of coal drops onto the floor*")
				messages.append("*smoke clears*")

		self.room.events.append(CoalRefillEvent(self.room.timeIndex+10))


class Display(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Display"):
		super().__init__(displayChars.display,xPosition,yPosition,name=name)

	def apply(self,character):
		def moveNorth():
			self.room.moveNorth(force=self.room.engineStrength)
		def moveSouth():
			self.room.moveSouth(force=self.room.engineStrength)
		def moveWest():
			self.room.moveWest(force=self.room.engineStrength)
		def moveEast():
			self.room.moveEast(force=self.room.engineStrength)
		def disapply():
			del stealKey[commandChars.move_north]
			del stealKey[commandChars.move_south]
			del stealKey[commandChars.move_west]
			del stealKey[commandChars.move_east]
			del stealKey[commandChars.activate]
		stealKey[commandChars.move_north] = moveNorth
		stealKey[commandChars.move_south] = moveSouth
		stealKey[commandChars.move_west] = moveWest
		stealKey[commandChars.move_east] = moveEast
		stealKey[commandChars.activate] = disapply

class Wall(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Wall"):
		super().__init__(displayChars.wall,xPosition,yPosition,name=name)

class Pipe(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Wall"):
		super().__init__(displayChars.pipe,xPosition,yPosition,name=name)

class Coal(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Coal"):
		self.canBurn = True
		super().__init__(displayChars.coal,xPosition,yPosition,name=name)
		self.walkable = True

class Door(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Door"):
		super().__init__(displayChars.door_closed,xPosition,yPosition,name=name)
		self.walkable = False

	def apply(self,character):
		if self.walkable:
			self.close()
		else:
			self.open()
	
	def open(self):
		self.walkable = True
		self.display = displayChars.door_opened
		self.room.open = True

	def close(self):
		self.walkable = False
		self.display = displayChars.door_closed
		self.room.open = False

class Pile(Item):
	def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal):
		self.canBurn = True
		self.type = itemType
		super().__init__(displayChars.pile,xPosition,yPosition,name=name)

	def apply(self,character):
		messages.append("Pile used")
		character.inventory.append(self.type())
		character.changed()

class Acid(Item):
	def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal):
		self.canBurn = True
		self.type = itemType
		super().__init__(displayChars.acid,xPosition,yPosition,name=name)

	def apply(self,character):
		messages.append("Pile used")
		character.inventory.append(self.type())
		character.changed()

class Chain(Item):
	def __init__(self,xPosition=0,yPosition=0,name="chain"):
		super().__init__(displayChars.chains,xPosition,yPosition,name=name)
		self.walkable = True

		self.chainedTo = []
		self.fixed = False

	def apply(self,character):
		if not self.fixed:
			if self.room:
				messages.append("TODO")
			else:
				self.fixed = True

				items = []
				for coordinate in [(self.xPosition-1,self.yPosition),(self.xPosition+1,self.yPosition),(self.xPosition,self.yPosition-1),(self.xPosition,self.yPosition+1)]:
					if coordinate in self.terrain.itemByCoordinates:
						items.extend(self.terrain.itemByCoordinates[coordinate])

				roomCandidates = []
				bigX = self.xPosition//15
				bigY = self.yPosition//15
				for coordinate in [(bigX,bigY),(bigX-1,bigY),(bigX+1,bigY),(bigX,bigY-1),(bigX,bigY+1)]:
					if coordinate in self.terrain.roomByCoordinates:
						roomCandidates.extend(self.terrain.roomByCoordinates[coordinate])

				rooms = []
				for room in roomCandidates:
					if (room.xPosition*15+room.offsetX == self.xPosition+1) and (self.yPosition > room.yPosition*15+room.offsetY-1 and self.yPosition < room.yPosition*15+room.offsetY+room.sizeY):
						rooms.append(room)
					if (room.xPosition*15+room.offsetX+room.sizeX == self.xPosition) and (self.yPosition > room.yPosition*15+room.offsetY-1 and self.yPosition < room.yPosition*15+room.offsetY+room.sizeY):
						rooms.append(room)
					if (room.yPosition*15+room.offsetY == self.yPosition+1) and (self.xPosition > room.xPosition*15+room.offsetX-1 and self.xPosition < room.xPosition*15+room.offsetX+room.sizeX):
						rooms.append(room)
					if (room.yPosition*15+room.offsetY+room.sizeY == self.yPosition) and (self.xPosition > room.xPosition*15+room.offsetX-1 and self.xPosition < room.xPosition*15+room.offsetX+room.sizeX):
						rooms.append(room)

				self.chainedTo = []
				self.chainedTo.extend(items)
				self.chainedTo.extend(rooms)

				for thing in self.chainedTo:
					thing.chainedTo.append(self)
					messages.append(thing.chainedTo)
		else:
			self.fixed = False
			for thing in self.chainedTo:
				if self in thing.chainedTo:
					thing.chainedTo.remove(self)
			self.chainedTo = []
			
class Winch(Item):
	def __init__(self,xPosition=0,yPosition=0,name="winch"):
		super().__init__(displayChars.winch_inactive,xPosition,yPosition,name=name)

	def apply(self,character):
		messages.append("TODO")

