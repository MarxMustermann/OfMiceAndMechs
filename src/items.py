import urwid

# bad code: global state
messages = None
characters = None
displayChars = None
stealKey = None
commandChars = None
terrain = None

'''
the base class for all items.
'''
class Item(object):
    '''
    straightforward state initialization
    '''
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

    '''
    generate a text with a detailed description of the items state
    bad code: casting a dict to string is not really enough
    '''
    def getDetailedInfo(self):
        return str(self.getDetailedState())

    '''
    get a short 
    '''
    def getDetailedState(self):
        return self.description

    '''
    no operation when applying a base item
    '''
    def apply(self,character):
        messages.append("i can't do anything useful with this")

    '''
    call callbacks for all listeners
    bad code: this should be specific for certain changes
    '''
    def changed(self):
        for listener in self.listeners:
            listener()

    '''
    get picked up by the suplied character
    '''
    def pickUp(self,character):
        # bad code: should be a simple self.container.removeItem(self)
        if self.room:
            # remove item from room
            container = self.room
            container.removeItem(self)
        else:
            # remove item from terrain
            # bad code: should be handled by the terrain
            container = terrain
            container.itemsOnFloor.remove(self)
            container.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
            if not container.itemByCoordinates[(self.xPosition,self.yPosition)]:
                del container.itemByCoordinates[(self.xPosition,self.yPosition)]

        # remove position information to place item in the void
        del self.xPosition
        del self.yPosition

        # add item to characters inventory
        character.inventory.append(self)
        self.changed()

    '''
    register a callback to be called when the item changes
    '''
    def addListener(self,listenFunction):
        if not listenFunction in self.listeners:
            self.listeners.append(listenFunction)

    '''
    delete a callback to be called when the item changes
    '''
    def delListener(self,listenFunction):
        if listenFunction in self.listeners:
            self.listeners.remove(listenFunction)

    '''
    get a list of items that is affected if the item would move north
    bad code: a method for each direction
    '''
    def getAffectedByMovementNorth(self,force=1,movementBlock=set()):
        movementBlock.add(self)
        
        # add things chained to the item
        for thing in self.chainedTo:
            if thing not in movementBlock and not thing == self:
                movementBlock.add(thing)
                thing.getAffectedByMovementNorth(force=force,movementBlock=movementBlock)

        return movementBlock

    '''
    move the item to the north
    bad code: a method for each direction
    '''
    def moveNorth(self,force=1,initialMovement=True):
        if self.walkable:
            # destroy small items instead of moving it
            self.destroy()
        else:
            # remove self from current position
            self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
            if len(self.terrain.itemByCoordinates) == 0:
                del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]

            # destroy everything on target position
            if (self.xPosition,self.yPosition-1) in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                    item.destroy()

            # place self on new position
            self.yPosition -= 1
            if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
            else:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

            # destroy yourself if anything is left on target position
            # bad code: this cannot happen since everything on the target position was destroyed already
            if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]) > 1:
                self.destroy()

    '''
    get a list of items that is affected if the item would move south
    bad code: a method for each direction
    '''
    def getAffectedByMovementSouth(self,force=1,movementBlock=set()):
        movementBlock.add(self)
        
        # add things chained to the item
        for thing in self.chainedTo:
            if thing not in movementBlock and not thing == self:
                movementBlock.add(thing)
                thing.getAffectedByMovementSouth(force=force,movementBlock=movementBlock)

        return movementBlock

    '''
    move the item to the south
    bad code: a method for each direction
    '''
    def moveSouth(self,force=1,initialMovement=True):
        if self.walkable:
            # destroy small items instead of moving it
            self.destroy()
        else:
            # remove self from current position
            self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
            if len(self.terrain.itemByCoordinates) == 0:
                del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]

            # destroy everything on target position
            if (self.xPosition,self.yPosition+1) in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[(self.xPosition,self.yPosition+1)]:
                    item.destroy()

            # place self on new position
            self.yPosition += 1
            if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
            else:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

            # destroy yourself if anything is left on target position
            # bad code: this cannot happen since everything on the target position was destroyed already
            if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]) > 1:
                self.destroy()

    '''
    get a list of items that is affected if the item would move west
    bad code: a method for each direction
    '''
    def getAffectedByMovementWest(self,force=1,movementBlock=set()):
        movementBlock.add(self)
        
        # add things chained to the item
        for thing in self.chainedTo:
            if thing not in movementBlock and not thing == self:
                movementBlock.add(thing)
                thing.getAffectedByMovementWest(force=force,movementBlock=movementBlock)

        return movementBlock

    '''
    move the item to the west
    bad code: a method for each direction
    '''
    def moveWest(self,force=1,initialMovement=True):
        if self.walkable:
            # destroy small items instead of moving it
            self.destroy()
        else:
            # remove self from current position
            self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
            if len(self.terrain.itemByCoordinates) == 0:
                del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]

            # destroy everything on target position
            if (self.xPosition-1,self.yPosition) in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                    item.destroy()

            # place self on new position
            self.xPosition -= 1
            if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
            else:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

            # destroy yourself if anything is left on target position
            # bad code: this cannot happen since everything on the target position was destroyed already
            if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]) > 1:
                self.destroy()

    '''
    get a list of items that is affected if the item would move east
    bad code: a method for each direction
    '''
    def getAffectedByMovementEast(self,force=1,movementBlock=set()):
        movementBlock.add(self)
        
        # add things chained to the item
        for thing in self.chainedTo:
            if thing not in movementBlock and not thing == self:
                movementBlock.add(thing)
                thing.getAffectedByMovementEast(force=force,movementBlock=movementBlock)

        return movementBlock

    '''
    move the item to the east
    bad code: a method for each direction
    '''
    def moveEast(self,force=1,initialMovement=True):

        if self.walkable:
            # destroy small items instead of moving it
            self.destroy()
        else:
            # remove self from current position
            self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
            if len(self.terrain.itemByCoordinates) == 0:
                del self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]

            # destroy everything on target position
            if (self.xPosition+1,self.yPosition) in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    item.destroy()

            # place self on new position
            self.xPosition += 1
            if (self.xPosition,self.yPosition) in self.terrain.itemByCoordinates:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(self)
            else:
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)] = [self]

            # destroy yourself if anything is left on target position
            # bad code: this cannot happen since everything on the target position was destroyed already
            if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]) > 1:
                self.destroy()
    
    '''
    get the physical resistance to beeing moved
    '''
    def getResistance(self):
        if (self.walkable):
            return 1
        else:
            return 50

    '''
    dummy for state correction
    '''
    def recalculate(self):
        pass

    '''
    destroy the item and leave scrap
    bad code: only works on terrain
    '''
    def destroy(self):
        # remove item from terrain
        self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
        self.terrain.itemsOnFloor.remove(self)

        # generatate scrao
        if self.walkable:
            newItem = Scrap(self.xPosition,self.yPosition,3)
        else:
            newItem = Scrap(self.xPosition,self.yPosition,10)
        newItem.room = self.room
        newItem.terrain = self.terrain

        # place scrap
        self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(newItem)
        self.terrain.itemsOnFloor.append(newItem)
            
'''
crushed something basically raw metal
'''
class Scrap(Item):
    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="scrap"):
        super().__init__(displayChars.scrap_light,xPosition,yPosition)
        self.amount = amount

        # set display char
        # bad code: redundant
        if self.amount < 5:
            self.walkable = True
            self.display = displayChars.scrap_light
        elif self.amount < 15:
            self.walkable = False
            self.display = displayChars.scrap_medium
        else:
            self.walkable = False
            self.display = displayChars.scrap_heavy

    '''
    move and leave a trail of pieces
    bad code: same code for every direction
    '''
    def moveNorth(self,force=1,initialMovement=True):
        self.dropStuff()
        super().moveNorth(force=force,initialMovement=initialMovement)

    '''
    move and leave a trail of pieces
    bad code: same code for every direction
    '''
    def moveSouth(self,force=1,initialMovement=True):
        self.dropStuff()
        super().moveSouth(force=force,initialMovement=initialMovement)

    '''
    move and leave a trail of pieces
    bad code: same code for every direction
    '''
    def moveWest(self,force=1,initialMovement=True):
        self.dropStuff()
        super().moveWest(force=force,initialMovement=initialMovement)

    '''
    move and leave a trail of pieces
    bad code: same code for every direction
    '''
    def moveEast(self,force=1,initialMovement=True):
        self.dropStuff()
        super().moveEast(force=force,initialMovement=initialMovement)

    '''
    leave a trail of pieces
    bad code: only works on terrain
    '''
    def dropStuff(self):
        if self.amount > 1:
            # determine how much should fall off
            fallOffAmount = 1
            if self.amount > 2:
                fallOffAmount = 2

            # remove scrap from self
            self.amount -= fallOffAmount

            # generate the fallen off scrap
            newItem = Scrap(self.xPosition,self.yPosition,fallOffAmount)
            newItem.room = self.room
            newItem.terrain = self.terrain

            # place the fallen off map
            # bad code: should be handled by terrain
            self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(newItem)
            self.terrain.itemsOnFloor.append(newItem)

        # recalculate the display char
        # bad code: redundant
        if self.amount < 5:
            self.walkable = True
            self.display = displayChars.scrap_light
        elif self.amount < 15:
            self.walkable = False
            self.display = displayChars.scrap_medium
        else:
            self.walkable = False
            self.display = displayChars.scrap_heavy
                
    '''
    get resistance to beeing moved depending on size
    '''
    def getResistance(self):
        return self.amount*2

    '''
    '''
    def destroy(self):
        # get list of scrap on same location
        # bad code: should be handled in the container
        foundScraps = []
        for item in self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]:
            if type(item) == Scrap:
                foundScraps.append(item)
        
        # merge existing and new scrap
        if len(foundScraps) > 1:
            messages.append("compressing foundScraps") # bad code: debug output in ui
            for item in foundScraps:
                if item == self:
                    continue
                self.amount += item.amount
                # bad code: direct manipulation of terrain state
                self.terrain.itemsOnFloor.remove(item)
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(item)

        # recalculate the display char
        # bad code: redundant
        if self.amount < 5:
            self.walkable = True
            self.display = displayChars.scrap_light
        elif self.amount < 15:
            self.walkable = False
            self.display = displayChars.scrap_medium
        else:
            self.walkable = False
            self.display = displayChars.scrap_heavy

'''
dummy class for a corpse
'''
class Corpse(Item):
    def __init__(self,xPosition=0,yPosition=0,name="corpse"):
        super().__init__(displayChars.corpse,xPosition,yPosition,name=name)

'''
dummy class for an unconcious body
bad code: transforming a character to item and back begs for trouble
'''
class UnconciousBody(Item):
    def __init__(self,xPosition=0,yPosition=0,name="unconcious body"):
        super().__init__(displayChars.unconciousBody,xPosition,yPosition,name=name)
        self.activated = False

    '''
    random code from elsewhere
    bad code: this seem to be a copy paste error or something, delete this
    '''
    def apply(self,character):
        if not self.activated:
            self.activated = True
            self.display = displayChars.hutch_occupied
        else:
            self.activated = False
            self.display = displayChars.hutch_free

'''
an character spawning item
'''
class GrowthTank(Item):
    def __init__(self,xPosition=0,yPosition=0,name="growth tank",filled=False):
        self.filled = filled
        if filled:
            super().__init__(displayChars.growthTank_filled,xPosition,yPosition,name=name)
        else:
            super().__init__(displayChars.growthTank_unfilled,xPosition,yPosition,name=name)

    def apply(self,character):
        if self.filled:
            self.eject()

    '''
    ejecting a character
    '''
    def eject(self,character=None):
        # emtpy growth tank
        self.filled = False
        self.display = displayChars.growthTank_unfilled

        def getRandomName(seed1=0,seed2=None):
            if seed2 == None:
                seed2 = seed1+(seed1//5)
            return names.characterFirstNames[seed1%len(names.characterFirstNames)]+" "+names.characterLastNames[seed2%len(names.characterLastNames)]

        # add character
        if not character:
            name = getRandomName(self.xPosition+self.room.timeIndex,self.yPosition+self.room.timeIndex)
            character = characters.Character(displayChars.staffCharactersByLetter[name[0].lower()],self.xPosition+1,self.yPosition,name=name)
        character.fallUnconcious()
        self.room.addCharacter(character,self.xPosition+1,self.yPosition)

'''
basically a bed with a activatable cover
'''
class Hutch(Item):
    def __init__(self,xPosition=0,yPosition=0,name="Hutch",activated=False):
        self.activated = activated
        if self.activated:
            super().__init__(displayChars.hutch_free,xPosition,yPosition)
        else:
            super().__init__(displayChars.hutch_occupied,xPosition,yPosition)

    '''
    open/close cover
    bad code: open close methods would be nice
    '''
    def apply(self,character):
        if not self.activated:
            self.activated = True
            self.display = displayChars.hutch_occupied
        else:
            self.activated = False
            self.display = displayChars.hutch_free

'''
item for letting characters 
'''
class Lever(Item):
    '''
    straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="lever",activated=False):
        self.activated = activated
        self.display = {True:displayChars.lever_pulled,False:displayChars.lever_notPulled}
        super().__init__(displayChars.lever_notPulled,xPosition,yPosition,name=name)
        self.activateAction = None
        self.deactivateAction = None
        self.walkable = True

    '''
    pull the lever!
    bad code: activate/deactive methods would be nice
    '''
    def apply(self,character):
        if not self.activated:
            # activate the lever
            self.activated = True
            self.display = displayChars.lever_pulled

            if self.activateAction:
                self.activateAction(self)
        else:
            # deactivate the lever
            self.activated = False
            self.display = displayChars.lever_notPulled

            if self.deactivateAction:
                self.activateAction(self)

        # notify listeners
        self.changed()

'''
heat source for generating steam and similar
'''
class Furnace(Item):
    '''
    straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Furnace"):
        self.activated = False
        self.boilers = None
        self.stopBoilingEvent = None
        super().__init__(displayChars.furnace_inactive,xPosition,yPosition,name=name)

    '''
    fire the furnace
    '''
    def apply(self,character):
        # bad code: debug out in ui
        if character.watched:
            messages.append("Furnace used")

        # select fuel
        # bad pattern: the player should be able to select fuel
        # bad pattern: coal should be preferred
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
            # refuse to fire the furnace without fuel
            # bad code: return would be preferable to if/else
            if character.watched:
                messages.append("you need coal to fire the furnace and you have none")
        else:
            if self.activated:
                # refuse to fire burning furnace
                # bad code: return would be preferable to if/else
                if character.watched:
                    messages.append("already burning")
            else:
                self.activated = True
                self.display = displayChars.furnace_active
                character.inventory.remove(foundItem)
                if character.watched:
                    messages.append("*wush*")

                # get the boilers affected
                if self.boilers == None:
                    self.boilers = []
                    for boiler in self.room.boilers:
                        if ((boiler.xPosition in [self.xPosition,self.xPosition-1,self.xPosition+1] and boiler.yPosition == self.yPosition) or boiler.yPosition in [self.yPosition-1,self.yPosition+1] and boiler.xPosition == self.xPosition):
                            self.boilers.append(boiler)

                for boiler in self.boilers:
                    boiler.startHeatingUp()

                '''
                the event for stopping to burn after a while
                bad code: should be an abstact event calling a method
                '''
                class FurnaceBurnoutEvent(object):
                    '''
                    straightforward state initialization
                    '''
                    def __init__(subself,tick):
                        subself.tick = tick

                    '''
                    stop burning
                    '''
                    def handleEvent(subself):
                        # stop burning
                        self.activated = False
                        self.display = displayChars.furnace_inactive

                        # stop heating the boilers
                        for boiler in self.boilers:
                            boiler.stopHeatingUp()

                        # notify listeners
                        self.changed()

                # add burnout event 
                self.room.addEvent(FurnaceBurnoutEvent(self.room.timeIndex+30))

                # notify listeners
                self.changed()

'''
a dummy for an interface with the mech communication network
bad code: this class is dummy only and basically is to be implemented
'''
class Commlink(Item):
    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Commlink"):
        super().__init__(displayChars.commLink,xPosition,yPosition,name=name)

    '''
    fake requesting and getting a coal refill
    '''
    def apply(self,character):
        # add messages requesting coal
        messages.append("Sigmund Bärenstein@Logisticcentre: we need more coal")
        messages.append("Logisticcentre@Sigmund Bärenstein: on its way")
    
        '''
        the event for stopping to burn after a while
        bad code: should be an abstact event calling a method
        '''
        class CoalRefillEvent(object):
            '''
            straightforward state initialization
            '''
            def __init__(subself,tick):
                subself.tick = tick

            '''
            make coal delivery noises
            '''
            def handleEvent(subself):
                messages.append("*rumbling*")
                messages.append("*rumbling*")
                messages.append("*smoke and dust on cole piles and neighbour fields*")
                messages.append("*a chunk of coal drops onto the floor*")
                messages.append("*smoke clears*")

        # add event for the faked coal delivery
        self.room.events.append(CoalRefillEvent(self.room.timeIndex+10))

'''
should be a display, but is abused as vehicle control
bad code: use an actual vehicle control
'''
class Display(Item):
    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Display"):
        super().__init__(displayChars.display,xPosition,yPosition,name=name)

    '''
    map player controls to room movement 
    '''
    def apply(self,character):
        # handle movement keystrokes
        def moveNorth():
            self.room.moveNorth(force=self.room.engineStrength)
        def moveSouth():
            self.room.moveSouth(force=self.room.engineStrength)
        def moveWest():
            self.room.moveWest(force=self.room.engineStrength)
        def moveEast():
            self.room.moveEast(force=self.room.engineStrength)

        # reset key mapping
        def disapply():
            del stealKey[commandChars.move_north]
            del stealKey[commandChars.move_south]
            del stealKey[commandChars.move_west]
            del stealKey[commandChars.move_east]
            del stealKey[commandChars.activate]

        # map the keystrokes
        stealKey[commandChars.move_north] = moveNorth
        stealKey[commandChars.move_south] = moveSouth
        stealKey[commandChars.move_west] = moveWest
        stealKey[commandChars.move_east] = moveEast
        stealKey[commandChars.activate] = disapply

'''
basic item with different appearance
'''
class Wall(Item):
    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Wall"):
        super().__init__(displayChars.wall,xPosition,yPosition,name=name)

'''
basic item with different appearance
'''
class Pipe(Item):
    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Pipe"):
        super().__init__(displayChars.pipe,xPosition,yPosition,name=name)

'''
basic item with different appearance
'''
class Coal(Item):
    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Coal"):
        self.canBurn = True
        super().__init__(displayChars.coal,xPosition,yPosition,name=name)
        self.walkable = True

'''
a door for opening/closing and looking people in/out
'''
class Door(Item):
    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Door"):
        super().__init__(displayChars.door_closed,xPosition,yPosition,name=name)
        self.walkable = False

    '''
    open or close door depending on state
    '''
    def apply(self,character):
        if self.walkable:
            self.close()
        else:
            self.open(character)
    
    '''
    open door
    '''
    def open(self,character):
        if not (self.room.isContainment and character.room):
            # open the door
            self.walkable = True
            self.display = displayChars.door_opened
            self.room.open = True

            # redraw room
            self.room.forceRedraw()

            # auto close door in containment
            if self.room.isContainment:
                '''
                the event for closing the door
                bad code: should be an abstact event calling a method
                '''
                class AutoCloseDoor(object):
                    '''
                    straightforward state initialization
                    '''
                    def __init__(subself,tick):
                        subself.tick = tick
            
                    '''
                    close the door
                    '''
                    def handleEvent(subself):
                        messages.append("*TSCHUNK*")
                        self.close()

                self.room.addEvent(AutoCloseDoor(self.room.timeIndex+5))
        else:
            # refuse to open the door
            messages.append("you cannot open the door from the inside")

    '''
    close the door
    '''
    def close(self):
        self.walkable = False
        self.display = displayChars.door_closed
        self.room.open = False
        self.room.forceRedraw()

'''
a pile of stuff to take things from
this doesn't hold objects but spawns them
'''
class Pile(Item):
    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal):
        self.contains_canBurn = True
        self.type = itemType
        self.numContained = 100
        super().__init__(displayChars.pile,xPosition,yPosition,name=name)

    '''
    take from the pile
    '''
    def apply(self,character):
        # check chracters inventory
        if len(character.inventory) > 10:
            messages.append("you cannot carry more items")
            return

        # print debug code on impossible state
        # bad code: debug output in ui
        if self.numContained < 1:
            messages.append("something went seriously wrong. I should have morphed by now")
            return

        # spawn item to inventory
        character.inventory.append(self.type())
        character.changed()
        messages.append("you take a piece of "+str(self.type))

        # reduce item count
        self.numContained -= 1

        if self.numContained == 1:
            # morph into a single item
            # bad code: debug output in ui
            messages.append("i should morph to item now")
            self.room.removeItem(self)
            new = self.type()
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.room.addItems([new])

    '''
    print info with item counter
    '''
    def getDetailedInfo(self):
        return super().getDetailedInfo()+" of "+str(self.type)+" containing "+str(self.numContained)

'''
basic item with different appearance
'''
class Acid(Item):
    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal):
        self.canBurn = True
        self.type = itemType
        super().__init__(displayChars.acid,xPosition,yPosition,name=name)

    '''
    do someting stupid
    bad code: copy paste eror probably. delete
    '''
    def apply(self,character):
        messages.append("Pile used")
        character.inventory.append(self.type())
        character.changed()

'''
used to connect rooms and items to drag them around
'''
class Chain(Item):
    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="chain"):
        super().__init__(displayChars.chains,xPosition,yPosition,name=name)
        self.walkable = True

        self.chainedTo = []
        self.fixed = False

    '''
    attach/detach chain
    bad code: attaching and detaching should be methods
    bad code: only works on terrains
    '''
    def apply(self,character):
        # chain to surrounding items/rooms
        # bad pattern: the user needs to be able to select to what to chain to
        if not self.fixed:
            if self.room:
                messages.append("TODO")
            else:
                # flag self as chained onto something
                self.fixed = True

                # gather items to chain to
                items = []
                for coordinate in [(self.xPosition-1,self.yPosition),(self.xPosition+1,self.yPosition),(self.xPosition,self.yPosition-1),(self.xPosition,self.yPosition+1)]:
                    if coordinate in self.terrain.itemByCoordinates:
                        items.extend(self.terrain.itemByCoordinates[coordinate])

                # gather nearby rooms
                roomCandidates = []
                bigX = self.xPosition//15
                bigY = self.yPosition//15
                for coordinate in [(bigX,bigY),(bigX-1,bigY),(bigX+1,bigY),(bigX,bigY-1),(bigX,bigY+1)]:
                    if coordinate in self.terrain.roomByCoordinates:
                        roomCandidates.extend(self.terrain.roomByCoordinates[coordinate])

                # gather rooms to chain to
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

                # set chaing for self
                self.chainedTo = []
                self.chainedTo.extend(items)
                self.chainedTo.extend(rooms)

                # set chaing for chained objects
                for thing in self.chainedTo:
                    thing.chainedTo.append(self)
                    messages.append(thing.chainedTo)

        # unchain from chained items
        else:
            # clear chaining information
            self.fixed = False
            for thing in self.chainedTo:
                if self in thing.chainedTo:
                    thing.chainedTo.remove(self)
            self.chainedTo = []
            
'''
basic item with different appearance
'''
class Winch(Item):
    '''
    call superclass constructor with modified paramters 
    '''
    def __init__(self,xPosition=0,yPosition=0,name="winch"):
        super().__init__(displayChars.winch_inactive,xPosition,yPosition,name=name)

    '''
    print "TODO"
    bad code: this useless. delete
    '''
    def apply(self,character):
        messages.append("TODO")

'''
basic item with different appearance
'''
class MetalBars(Item):
    def __init__(self,xPosition=0,yPosition=0,name="metal bar"):
        super().__init__("==",xPosition,yPosition,name=name)

'''
produces steam from heat
bad code: sets the rooms steam generation directly without using pipes
'''
class Boiler(Item):
    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="boiler"):
        super().__init__(displayChars.boiler_inactive,xPosition,yPosition,name=name)
        self.isBoiling = False
        self.isHeated = False
        self.startBoilingEvent = None
        self.stopBoilingEvent = None

    '''
    start producing steam after a delay
    '''
    def startHeatingUp(self):
        # bad code: guard with return would be preferrable to shifting the whole methods
        if not self.isHeated:
            # flag self as heated
            self.isHeated = True

            # abort any cooling down
            if self.stopBoilingEvent:
                self.room.removeEvent(self.stopBoilingEvent)
                self.stopBoilingEvent = None

            # shedule the steam generation
            if not self.startBoilingEvent and not self.isBoiling:
                '''
                the event for starting to boil
                bad code: should be an abstact event calling a method
                '''
                class StartBoilingEvent(object):
                    '''
                    straightforward state initialization
                    '''
                    def __init__(subself,tick):
                        subself.tick = tick
            
                    '''
                    start producing steam
                    '''
                    def handleEvent(subself):
                        # add noises
                        messages.append("*boil*")

                        # set own state
                        self.display = displayChars.boiler_active
                        self.isBoiling = True
                        self.startBoilingEvent = None
                        self.changed()

                        # change rooms steam production
                        self.room.steamGeneration += 1
                        self.room.changed()

                # shedule the event
                self.startBoilingEvent = StartBoilingEvent(self.room.timeIndex+5)
                self.room.addEvent(self.startBoilingEvent)

            # notify listeners
            self.changed()
        
    '''
    stop producing steam after a delay
    '''
    def stopHeatingUp(self):
        # bad code: guard with return would be preferrable to shifting the whole methods
        if self.isHeated:
            # flag self as heated
            self.isHeated = False

            # abort any heating up
            if self.startBoilingEvent:
                self.room.removeEvent(self.startBoilingEvent)
                self.startBoilingEvent = None
            if not self.stopBoilingEvent and self.isBoiling:
                '''
                the event for starting to boil
                bad code: should be an abstact event calling a method
                '''
                class StopBoilingEvent(object):
                    '''
                    straightforward state initialization
                    '''
                    def __init__(subself,tick):
                        subself.tick = tick
            
                    '''
                    start producing steam
                    '''
                    def handleEvent(subself):
                        # add noises
                        messages.append("*unboil*")

                        # set own state
                        self.display = displayChars.boiler_inactive
                        self.isBoiling = False
                        self.stopBoilingEvent = None
                        self.changed()

                        # change rooms steam production
                        self.room.steamGeneration -= 1
                        self.room.changed()

                self.stopBoilingEvent = StopBoilingEvent(self.room.timeIndex+5)
                self.room.addEvent(self.stopBoilingEvent)

            # notify listeners
            self.changed()
            
'''
steam sprayer used as a prop in the vat
'''
class Spray(Item):
    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="spray",direction=None):
        # skin acording to spray direction
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

    '''
    set appearance depending on energy supply
    bad code: energy supply is directly taken from the machine room
    '''
    def recalculate(self):
        if terrain.tutorialMachineRoom.steamGeneration == 0:
            self.display = self.display_inactive
        if terrain.tutorialMachineRoom.steamGeneration == 1:
            self.display = self.display_stage1
        if terrain.tutorialMachineRoom.steamGeneration == 2:
            self.display = self.display_stage2
        if terrain.tutorialMachineRoom.steamGeneration == 3:
            self.display = self.display_stage3
            
'''
marker ment to be placed by characters and to control actions with
'''
class MarkerBean(Item):
    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="bean"):
        super().__init__(" -",xPosition,yPosition,name=name)
        self.activated = False
        self.walkable = True

    '''
    avtivate marker
    '''
    def apply(self,character):
        self.display = "x-"
        self.activated = True

'''
machine for filling up goo flasks
'''
class GooDispenser(Item):
    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo dispenser"):
        super().__init__("g%",xPosition,yPosition,name=name)
        self.activated = False
    
    '''
    fill goo flask
    '''
    def apply(self,character):
        for item in character.inventory:
            if isinstance(item,GooFlask):
                item.uses = 100
        self.activated = True

'''
flask with food to carry around and drink from
'''
class GooFlask(Item):
    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo flask"):
        super().__init__(" -",xPosition,yPosition,name=name)
        self.walkable = True
        self.uses = 100
        self.displayByUses = ["ò ","ò.","ò,","ò-","ò~","ò="]
        self.display = (urwid.AttrSpec("#3f3","black"),self.displayByUses[self.uses//20])
        self.description = "a flask conatining goo"

    '''
    drink from flask
    '''
    def apply(self,character):
        if self.uses > 0:
            self.uses -= 1
            self.display = (urwid.AttrSpec("#3f3","black"),self.displayByUses[self.uses//20])
            self.changed()
            character.satiation = 1000
            character.changed()

    '''
    get info including the charges on the flask
    '''
    def getDetailedInfo(self):
        return super().getDetailedInfo()+" ("+str(self.uses)+" charges)"

'''
a vending machine basically
bad code: currently only dispenses goo flasks
'''
class OjectDispenser(Item):
    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="object dispenser"):
        super().__init__("U\\",xPosition,yPosition,name=name)

    '''
    drop goo flask
    '''
    def dispenseObject(self):
        new = GooFlask()
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition+1
        self.room.addItems([new])

'''
token object ment to produce anything from metal bars
bad code: doesn't actually allow to produce a few items
bad pattern: serves as dummy for actual production lines
'''
class ProductionArtwork(Item):
    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="production artwork"):
        super().__init__("U\\",xPosition,yPosition,name=name)

    '''
    trigger production of a player selected item
    '''
    def apply(self,character,resultType=None):
        self.submenue = interaction.SelectionMenu("test",{1:Pipe,2:Wall},{1:"pipe",2:"wall"})
        interaction.submenue = self.submenue
        interaction.submenue.followUp = self.produceSelection

    '''
    trigger production of the selected item
    '''
    def produceSelection(self):
        self.produce(interaction.submenue.selection)

    '''
    produce an item
    '''
    def produce(self,itemType,resultType=None):
       if not (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            # refuse production without ressources
            # bad code: guard with return would be preferrable to if/else
            messages.append("no metal bars available")
       else:
           # remove ressources
           desintegratedScrap = False # bad code: copy paste error
           for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
               if isinstance(item,MetalBars):
                   self.room.removeItem(item)
                   # bad code: should break here to only take one metal bar

           # spawn new item
           new = itemType()
           new.xPosition = self.xPosition-1
           new.yPosition = self.yPosition
           self.room.addItems([new])

'''
scrap to metal bar converter
'''
class ScrapCompactor(Item):
    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="scrap compactor"):
        super().__init__("U\\",xPosition,yPosition,name=name)

    '''
    produce a metal bar
    '''
    def apply(self,character,resultType=None):
       if not (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            # refuse to produce without ressources
            # bad code: guard with return would be preferrable to if/else
            messages.append("no scraps available")
       else:
           # remove ressources
           desintegratedScrap = False # bad code: unused variable
           for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
               if isinstance(item,Scrap):
                   self.room.removeItem(item)
                   # bad code: should break here to only take only x scrap

           # spawn the metal bar
           new = MetalBars()
           new.xPosition = self.xPosition-1
           new.yPosition = self.yPosition
           self.room.addItems([new])
