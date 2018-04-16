import urwid

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
        return str(self.getDetailedState())

    def getDetailedState(self):
        return self.description

    def apply(self,character):
        messages.append("i can't do anything useful with this")

    def changed(self):
        for listener in self.listeners:
            listener()

    def pickUp(self,character):
        if self.room:
            container = self.room
        else:
            container = terrain

        container.itemsOnFloor.remove(self)

        character.inventory.append(self)
        self.changed()

        container.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
        if not container.itemByCoordinates[(self.xPosition,self.yPosition)]:
            del container.itemByCoordinates[(self.xPosition,self.yPosition)]

        del self.xPosition
        del self.yPosition

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
        if self.walkable:
            self.destroy()
        else:
            self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
            if len(self.terrain.itemByCoordinates) == 0:
                del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]

            if (self.xPosition,self.yPosition-1) in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                    item.destroy()

            self.yPosition -= 1
            if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
            else:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

            if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]) > 1:
                self.destroy()

    def getAffectedByMovementSouth(self,force=1,movementBlock=set()):
        movementBlock.add(self)
        
        for thing in self.chainedTo:
            if thing not in movementBlock and not thing == self:
                movementBlock.add(thing)
                thing.getAffectedByMovementSouth(force=force,movementBlock=movementBlock)

        return movementBlock

    def moveSouth(self,force=1,initialMovement=True):
        if self.walkable:
            self.destroy()
        else:
            self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
            if len(self.terrain.itemByCoordinates) == 0:
                del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]

            if (self.xPosition,self.yPosition+1) in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[(self.xPosition,self.yPosition+1)]:
                    item.destroy()

            self.yPosition += 1
            if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
            else:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

            if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]) > 1:
                self.destroy()

    def getAffectedByMovementWest(self,force=1,movementBlock=set()):
        movementBlock.add(self)
        
        for thing in self.chainedTo:
            if thing not in movementBlock and not thing == self:
                movementBlock.add(thing)
                thing.getAffectedByMovementWest(force=force,movementBlock=movementBlock)

        return movementBlock

    def moveWest(self,force=1,initialMovement=True):
        if self.walkable:
            self.destroy()
        else:
            self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
            if len(self.terrain.itemByCoordinates) == 0:
                del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]

            if (self.xPosition-1,self.yPosition) in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                    item.destroy()

            self.xPosition -= 1
            if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
            else:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

            if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]) > 1:
                self.destroy()

    def getAffectedByMovementEast(self,force=1,movementBlock=set()):
        movementBlock.add(self)
        
        for thing in self.chainedTo:
            if thing not in movementBlock and not thing == self:
                movementBlock.add(thing)
                thing.getAffectedByMovementEast(force=force,movementBlock=movementBlock)

        return movementBlock

    def moveEast(self,force=1,initialMovement=True):

        if self.walkable:
            self.destroy()
        else:
            self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
            if len(self.terrain.itemByCoordinates) == 0:
                del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]

            if (self.xPosition+1,self.yPosition) in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    item.destroy()

            self.xPosition += 1
            if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
            else:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

            if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]) > 1:
                self.destroy()

    def getResistance(self):
        if (self.walkable):
            return 1
        else:
            return 50

    def recalculate(self):
        pass

    def destroy(self):
        self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
        self.terrain.itemsOnFloor.remove(self)

        if self.walkable:
            newItem = Scrap(self.xPosition,self.yPosition,3)
        else:
            newItem = Scrap(self.xPosition,self.yPosition,10)

        newItem.room = self.room
        newItem.terrain = self.terrain

        self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(newItem)
        self.terrain.itemsOnFloor.append(newItem)
            

class Scrap(Item):
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="scrap"):
        super().__init__(displayChars.scrap_light,xPosition,yPosition)

        self.amount = amount
        if self.amount < 5:
            self.walkable = True
            self.display = displayChars.scrap_light
        elif self.amount < 15:
            self.walkable = False
            self.display = displayChars.scrap_medium
        else:
            self.walkable = False
            self.display = displayChars.scrap_heavy

    def moveNorth(self,force=1,initialMovement=True):
        self.dropStuff()
        super().moveNorth(force=force,initialMovement=initialMovement)

    def moveSouth(self,force=1,initialMovement=True):
        self.dropStuff()
        super().moveSouth(force=force,initialMovement=initialMovement)

    def moveWest(self,force=1,initialMovement=True):
        self.dropStuff()
        super().moveWest(force=force,initialMovement=initialMovement)

    def moveEast(self,force=1,initialMovement=True):
        self.dropStuff()
        super().moveEast(force=force,initialMovement=initialMovement)

    def dropStuff(self):
        if self.amount > 1:
            fallOffAmount = 1
            if self.amount > 2:
                fallOffAmount = 2
            self.amount -= fallOffAmount
            newItem = Scrap(self.xPosition,self.yPosition,fallOffAmount)
            newItem.room = self.room
            newItem.terrain = self.terrain
            self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(newItem)
            self.terrain.itemsOnFloor.append(newItem)

        if self.amount < 5:
            self.walkable = True
            self.display = displayChars.scrap_light
        elif self.amount < 15:
            self.walkable = False
            self.display = displayChars.scrap_medium
        else:
            self.walkable = False
            self.display = displayChars.scrap_heavy
                

    def getResistance(self):
        return self.amount*2

    def destroy(self):
        foundScraps = []
        for item in self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]:
            if type(item) == Scrap:
                foundScraps.append(item)
        
        if len(foundScraps) > 1:
            messages.append("compressing foundScraps")
            for item in foundScraps:
                if item == self:
                    continue
                self.amount += item.amount
                self.terrain.itemsOnFloor.remove(item)
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(item)

        if self.amount < 5:
            self.walkable = True
            self.display = displayChars.scrap_light
        elif self.amount < 15:
            self.walkable = False
            self.display = displayChars.scrap_medium
        else:
            self.walkable = False
            self.display = displayChars.scrap_heavy

class Corpse(Item):
    def __init__(self,xPosition=0,yPosition=0,name="corpse"):
        super().__init__(displayChars.corpse,xPosition,yPosition,name=name)

class UnconciousBody(Item):
    def __init__(self,xPosition=0,yPosition=0,name="unconcious body"):
        super().__init__(displayChars.unconciousBody,xPosition,yPosition,name=name)
        self.activated = False

    def apply(self,character):
        if not self.activated:
            self.activated = True
            self.display = displayChars.hutch_occupied
        else:
            self.activated = False
            self.display = displayChars.hutch_free

class GrowthTank(Item):
    def __init__(self,xPosition=0,yPosition=0,name="growth tank",filled=False):
        if filled:
            super().__init__(displayChars.growthTank_filled,xPosition,yPosition,name=name)
        else:
            super().__init__(displayChars.growthTank_unfilled,xPosition,yPosition,name=name)

    def eject(self):
        self.display = displayChars.growthTank_unfilled

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

            if self.activateAction:
                self.activateAction(self)
        else:
            self.activated = False
            self.display = displayChars.lever_notPulled

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
        if character.watched:
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
            if character.watched:
                messages.append("keine KOHLE zum anfeuern")
        else:
            if self.activated:
                if character.watched:
                    messages.append("already burning")
            else:
                self.activated = True
                self.display = displayChars.furnace_active
                character.inventory.remove(foundItem)
                if character.watched:
                    messages.append("*wush*")

                class FurnaceBurnoutEvent(object):
                    def __init__(subself,tick):
                        subself.tick = tick

                    def handleEvent(subself):
                        self.activated = False
                        self.display = displayChars.furnace_inactive

                        for boiler in self.boilers:
                            boiler.stopHeatingUp()

                        self.changed()

                if self.boilers == None:
                    self.boilers = []
                    for boiler in self.room.boilers:
                        if ((boiler.xPosition in [self.xPosition,self.xPosition-1,self.xPosition+1] and boiler.yPosition == self.yPosition) or boiler.yPosition in [self.yPosition-1,self.yPosition+1] and boiler.xPosition == self.xPosition):
                            self.boilers.append(boiler)

                for boiler in self.boilers:
                    boiler.startHeatingUp()

                self.room.addEvent(FurnaceBurnoutEvent(self.room.timeIndex+30))

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
    def __init__(self,xPosition=0,yPosition=0,name="Pipe"):
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
        self.room.forceRedraw()

    def close(self):
        self.walkable = False
        self.display = displayChars.door_closed
        self.room.open = False
        self.room.forceRedraw()

class Pile(Item):
    def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal):
        self.contains_canBurn = True
        self.type = itemType
        self.numContained = 100
        super().__init__(displayChars.pile,xPosition,yPosition,name=name)

    def apply(self,character):
        if len(character.inventory) > 10:
            messages.append("you cannot carry more items")
            return

        if self.numContained < 1:
            messages.append("something went seriously wrong. I should have morphed by now")
            return

        character.inventory.append(self.type())
        character.changed()
        messages.append("you take a piece of "+str(self.type))

        self.numContained -= 1

        if self.numContained == 1:
                messages.append("i should morph to item now")
                self.room.removeItem(self)
                new = self.type()
                new.xPosition = self.xPosition
                new.yPosition = self.yPosition
                self.room.addItems([new])

    def getDetailedInfo(self):
        return super().getDetailedInfo()+" of "+str(self.type)+" containing "+str(self.numContained)

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

class Boiler(Item):
    def __init__(self,xPosition=0,yPosition=0,name="boiler"):
        super().__init__(displayChars.boiler_inactive,xPosition,yPosition,name=name)
        self.isBoiling = False
        self.isHeated = False
        self.startBoilingEvent = None
        self.stopBoilingEvent = None

    def startHeatingUp(self):
        if not self.isHeated:
            self.isHeated = True

            if self.stopBoilingEvent:
                self.room.removeEvent(self.stopBoilingEvent)
                self.stopBoilingEvent = None
            if not self.startBoilingEvent and not self.isBoiling:
                class StartBoilingEvent(object):
                    def __init__(subself,tick):
                        subself.tick = tick
            
                    def handleEvent(subself):
                        messages.append("*boil*")
                        self.display = displayChars.boiler_active
                        self.isBoiling = True
                        self.startBoilingEvent = None
                        self.changed()
                        self.room.steamGeneration += 1
                        self.room.changed()

                self.startBoilingEvent = StartBoilingEvent(self.room.timeIndex+5)
                self.room.addEvent(self.startBoilingEvent)

            self.changed()
        
    def stopHeatingUp(self):
        if self.isHeated:
            self.isHeated = False

            if self.startBoilingEvent:
                self.room.removeEvent(self.startBoilingEvent)
                self.startBoilingEvent = None
            if not self.stopBoilingEvent and self.isBoiling:
                class StopBoilingEvent(object):
                    def __init__(subself,tick):
                        subself.tick = tick
            
                    def handleEvent(subself):
                        messages.append("*unboil*")
                        self.display = displayChars.boiler_inactive
                        self.isBoiling = False
                        self.stopBoilingEvent = None
                        self.changed()
                        self.room.steamGeneration -= 1
                        self.room.changed()

                self.stopBoilingEvent = StopBoilingEvent(self.room.timeIndex+5)
                self.room.addEvent(self.stopBoilingEvent)

            self.changed()
            
class Spray(Item):
    def __init__(self,xPosition=0,yPosition=0,name="spray",direction=None):
        if direction == None:
            direction = "left"

        if direction == "left":
            self.display_inactive = displayChars.spray_left_inactive
            self.display_stage1 = displayChars.spray_left_stage1
            self.display_stage2 = displayChars.spray_left_stage2
            self.display_stage3 = displayChars.spray_left_stage3
        else:
            self.display_inactive = displayChars.spray_right_inactive
            self.display_stage1 = displayChars.spray_right_stage1
            self.display_stage2 = displayChars.spray_right_stage2
            self.display_stage3 = displayChars.spray_right_stage3

        super().__init__(self.display_inactive,xPosition,yPosition,name=name)

    def recalculate(self):
        if terrain.tutorialMachineRoom.steamGeneration == 0:
            self.display = self.display_inactive
        if terrain.tutorialMachineRoom.steamGeneration == 1:
            self.display = self.display_stage1
        if terrain.tutorialMachineRoom.steamGeneration == 2:
            self.display = self.display_stage2
        if terrain.tutorialMachineRoom.steamGeneration == 3:
            self.display = self.display_stage3
            
class MarkerBean(Item):
    def __init__(self,xPosition=0,yPosition=0,name="bean"):
        super().__init__(" -",xPosition,yPosition,name=name)
        self.activated = False
        self.walkable = True

    def apply(self,character):
        self.display = "x-"
        self.activated = True

class GooDispenser(Item):
    def __init__(self,xPosition=None,yPosition=None,name="goo dispenser"):
        super().__init__("g%",xPosition,yPosition,name=name)
        self.activated = False
    
    def apply(self,character):
        for item in character.inventory:
            if isinstance(item,GooFlask):
                item.uses = 100
        self.activated = True

class GooFlask(Item):
    def __init__(self,xPosition=None,yPosition=None,name="goo flask"):
        super().__init__(" -",xPosition,yPosition,name=name)
        self.walkable = True
        self.uses = 100
        self.displayByUses = ["ò ","ò.","ò,","ò-","ò~","ò="]
        self.display = (urwid.AttrSpec("#3f3","black"),self.displayByUses[self.uses//20])
        self.description = "a flask conatining goo"

    def apply(self,character):
        if self.uses > 0:
            self.uses -= 1
            self.display = (urwid.AttrSpec("#3f3","black"),self.displayByUses[self.uses//20])
            self.changed()
            character.satiation = 1000
            character.changed()

    def getDetailedInfo(self):
        return super().getDetailedInfo()+" ("+str(self.uses)+" charges)"

class OjectDispenser(Item):
    def __init__(self,xPosition=None,yPosition=None, name="oject dispenser"):
        super().__init__("U\\",xPosition,yPosition,name=name)

    def dispenseObject(self):
        new = GooFlask()
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition+1
        self.room.addItems([new])
