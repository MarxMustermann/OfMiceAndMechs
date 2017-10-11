messages = None
characters = None
displayChars = None
stealKey = None
commandChars = None
terrain = None

class Item(object):
	def __init__(self,display=None,xPosition=0,yPosition=0):
		if not display:
			self.display = displayChars.notImplentedYet
		else:
			self.display = display
		self.xPosition = xPosition
		self.yPosition = yPosition
		self.listeners = []
		self.walkable = False
		self.room = None
		self.name = "item"

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
		self.name = name
		super().__init__(displayChars.lever_notPulled,xPosition,yPosition)
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
		self.name = name
		self.activated = False
		super().__init__(displayChars.furnace_inactive,xPosition,yPosition)

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
			self.activated = True
			self.display = displayChars.furnace_active
			character.inventory.remove(foundItem)
			messages.append("burn it ALL")
		self.changed()

class Display(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Display"):
		self.name = name
		super().__init__(displayChars.display,xPosition,yPosition)

	def apply(self,character):
		def moveNorth():
			self.room.moveNorth()
		def moveSouth():
			self.room.moveSouth()
		def moveWest():
			self.room.moveWest()
		def moveEast():
			self.room.moveEast()
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
		self.name = name
		super().__init__(displayChars.wall,xPosition,yPosition)

class Pipe(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Wall"):
		self.name = name
		super().__init__(displayChars.pipe,xPosition,yPosition)

class Coal(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Coal"):
		self.name = name
		self.canBurn = True
		super().__init__(displayChars.coal,xPosition,yPosition)
		self.walkable = True

class Door(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Door"):
		super().__init__(displayChars.door_closed,xPosition,yPosition)
		self.name = name
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
		self.name = name
		self.canBurn = True
		self.type = itemType
		super().__init__(displayChars.pile,xPosition,yPosition)

	def apply(self,character):
		messages.append("Pile used")
		character.inventory.append(self.type())
		character.changed()

class Acid(Item):
	def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal):
		self.name = name
		self.canBurn = True
		self.type = itemType
		super().__init__(displayChars.acid,xPosition,yPosition)

	def apply(self,character):
		messages.append("Pile used")
		character.inventory.append(self.type())
		character.changed()

class Chain(Item):
	def __init__(self,xPosition=0,yPosition=0,name="chain"):
		self.name = name
		super().__init__(displayChars.chains,xPosition,yPosition)
		self.walkable = True

	def apply(self,character):
		messages.append("TODO")

class Winch(Item):
	def __init__(self,xPosition=0,yPosition=0,name="winch"):
		self.name = name
		super().__init__(displayChars.winch_inactive,xPosition,yPosition)

	def apply(self,character):
		messages.append("TODO")

