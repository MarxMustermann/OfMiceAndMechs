messages = None
characters = None

class Item(object):
	def __init__(self,display="??",xPosition=0,yPosition=0):
		self.display = display
		self.xPosition = xPosition
		self.yPosition = yPosition
		self.listeners = []
		self.walkable = False
		self.room = None

	def apply(self):
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

class Lever(Item):
	def __init__(self,xPosition=0,yPosition=0,name="lever",activated=False):
		self.activated = activated
		self.display = {True:" /",False:" |"}
		self.name = name
		super().__init__(" |",xPosition,yPosition)
		self.activateAction = None
		self.deactivateAction = None
		self.walkable = True

	def apply(self):
		if not self.activated:
			self.activated = True
			self.display = " /"
			messages.append(self.name+": activated!")

			if self.activateAction:
				self.activateAction(self)
		else:
			self.activated = False
			self.display = " |"
			messages.append(self.name+": deactivated!")

			if self.deactivateAction:
				self.activateAction(self)
		self.changed()

class Furnace(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Furnace"):
		self.name = name
		self.activated = False
		super().__init__("ΩΩ",xPosition,yPosition)

	def apply(self):
		messages.append("Furnace used")
		foundItem = None
		for item in characters[0].inventory:
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
			self.display = "ϴϴ"
			characters[0].inventory.remove(foundItem)
			messages.append("burn it ALL")
		self.changed()

class Display(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Display"):
		self.name = name
		super().__init__("ߐߐ",xPosition,yPosition)

class Wall(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Wall"):
		self.name = name
		super().__init__("⛝ ",xPosition,yPosition)

class Pipe(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Wall"):
		self.name = name
		super().__init__("✠✠",xPosition,yPosition)

class Coal(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Coal"):
		self.name = name
		self.canBurn = True
		super().__init__(" *",xPosition,yPosition)
		self.walkable = True

class Door(Item):
	def __init__(self,xPosition=0,yPosition=0,name="Door"):
		super().__init__("⛒ ",xPosition,yPosition)
		self.name = name
		self.walkable = False
		self.display = '⛒ '

	def apply(self):
		if self.walkable:
			self.close()
		else:
			self.open()
	
	def open(self):
		self.walkable = True
		self.display = '⭘ '
		self.room.open = True

	def close(self):
		self.walkable = False
		self.display = '⛒ '
		self.room.open = False

class Pile(Item):
	def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal):
		self.name = name
		self.canBurn = True
		self.type = itemType
		super().__init__(" ӫ",xPosition,yPosition)

	def apply(self):
		messages.append("Pile used")
		characters[0].inventory.append(self.type())
		characters[0].changed()
