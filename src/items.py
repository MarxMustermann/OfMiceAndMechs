####################################################################################
###
##     items and item related code belongs here 
#
####################################################################################

# load basic libs
import urwid
import json

# load basic internal libs
import gamestate # bad code: wtf is this?
import src.saveing
import src.events

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
class Item(src.saveing.Saveable):
    '''
    state initialization and id generation
    '''
    def __init__(self,display=None,xPosition=0,yPosition=0,creator=None,name="item"):
        super().__init__()

        # set attributes
        if not hasattr(self,"type"):
            self.type = "Item"
        if not display:
            self.display = displayChars.notImplentedYet
        else:
            try:
                self.display = display
            except:
                pass
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.room = None
        self.listeners = {"default":[]}
        self.walkable = False
        self.lastMovementToken = None
        self.chainedTo = []
        self.name = name
        self.description = "a "+self.name
        self.mayContainMice = False
        self.bolted = not self.walkable

        # set up saveing
        self.attributesToStore.extend([
               "mayContainMice","name","type","walkable","xPosition","yPosition"])

        # set id
        self.id = {
                   "other":"item",
                   "xPosition":xPosition,
                   "yPosition":yPosition,
                   "counter":creator.getCreationCounter()
                  }
        self.id["creator"] = creator.id
        self.id = json.dumps(self.id, sort_keys=True).replace("\\","")

        # store state and register self
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    generate a text with a detailed description of the items state
    bad code: casting a dict to string is not really enough
    '''
    def getDetailedInfo(self):
        return str(self.getDetailedState())

    '''
    get a short description
    bad code: name and function say diffrent things
    '''
    def getDetailedState(self):
        return self.description

    '''
    no operation when applying a base item
    '''
    def apply(self,character,silent=False):
        character.changed("activate",self)
        self.changed("activated",character)
        if not silent:
            messages.append("i can't do anything useful with this")

    '''
    get picked up by the supplied character
    '''
    def pickUp(self,character):
        if self.bolted:
            messages.append("you cannot pick up bolted items")
            return

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

        # spawn mice with pseudorandom chance
        if ((self.mayContainMice and (gamestate.tick+self.xPosition+self.yPosition)%10 == 0 and not self.walkable) or
           (not self.mayContainMice and (gamestate.tick+self.xPosition-self.yPosition)%100 == 0 and not self.walkable)):

            # create mouse
            # bad code: variable name lies
            rat = characters.Mouse(creator=self)
        
            # make mouse attack the player
            quest = quests.MetaQuestSequence([],creator=self)
            quest.addQuest(quests.MoveQuestMeta(room=self.room,x=self.xPosition,y=self.yPosition,creator=self))
            quest.addQuest(quests.KnockOutQuest(character,lifetime=30,creator=self))
            quest.addQuest(quests.WaitQuest(lifetime=5,creator=self))
            rat.assignQuest(quest,active=True)

            # make mouse vanish after successful attack
            quest.endTrigger = {"container":rat,"method":"vanish"}

            if self.room:
                room = self.room
                xPosition = self.xPosition
                yPosition = self.yPosition

                # add mouse
                room.addCharacter(rat,xPosition,yPosition)

                '''
                set up an ambush if target left the room
                bad code: nameing
                '''
                def test(character2):
                    # only trigger for target
                    if not character == character2:
                       return

                    # get ambush position next to door
                    ambushXPosition = None
                    ambushYPosition = None
                    for item in room.itemsOnFloor:
                        if not isinstance(item,Door):
                            continue
                        ambushXPosition = item.xPosition
                        ambushYPosition = item.yPosition
                        if ambushXPosition == 0:
                          ambushXPosition += 1
                        if ambushYPosition == 0:
                          ambushYPosition += 1
                        if ambushXPosition == room.sizeX-1:
                          ambushXPosition -= 1
                        if ambushYPosition == room.sizeY-1:
                          ambushYPosition -= 1

                    # remove old attack quests
                    while len(quest.subQuests) > 1:
                        subQuest = quest.subQuests.pop()
                        subQuest.deactivate()

                    # make mouse wait on ambush position
                    if (not yPosition == None) and (not xPosition == None):
                        quest.addQuest(quests.WaitQuest(creator=self))
                        quest.addQuest(quests.MoveQuestMeta(room=room,x=ambushXPosition,y=ambushYPosition,creator=self))

                    # remove self from listeners
                    room.delListener(test,"left room")

                    '''
                    trigger ambush
                    '''
                    def test2(character3):
                        # make mouse atack anybody entering the room
                        quest.addQuest(quests.MoveQuestMeta(room=room,x=xPosition,y=yPosition,creator=self))
                        quest.addQuest(quests.KnockOutQuest(character3,lifetime=10,creator=self))

                        # remove old quests
                        while len(quest.subQuests) > 2:
                            subQuest = quest.subQuests[-1]
                            subQuest.deactivate()
                            quest.subQuests.remove(subQuest)

                        # remove self from wath list
                        room.delListener(test2,"entered room")
                        
                    # start watching for somebody entering the room
                    room.addListener(test2,"entered room")

                # start watching for character leaving the room
                room.addListener(test,"left room")
            else:
                # add mouse
                self.terrain.addCharacter(rat,self.xPosition,self.yPosition)


        # remove position information to place item in the void
        self.xPosition = None
        self.yPosition = None

        # add item to characters inventory
        character.inventory.append(self)
        self.changed()

    '''
    registering for notifications
    bad code: should be extra class
    '''
    def addListener(self,listenFunction,tag="default"):
        # create bucket if it does not exist yet
        if not tag in self.listeners:
            self.listeners[tag] = []

        if not listenFunction in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    '''
    deregistering for notifications
    bad code: should be extra class
    '''
    def delListener(self,listenFunction,tag="default"):
        # remove listener
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        # clean up empty buckets
        # bad performance: probably better to not clear and recreate buckets
        if not self.listeners[tag] and not tag == "default":
            del self.listeners[tag]

    '''
    sending notifications
    bad code: probably misnamed
    bad code: should be extra class
    '''
    def changed(self,tag="default",info=None):
        if not tag in self.listeners:
            return

        for listenFunction in self.listeners[tag]:
            if info == None:
                listenFunction()
            else:
                listenFunction(info)

    '''
    get a list of items that is affected if the item would move into some direction
    '''
    def getAffectedByMovementDirection(self,direction,force=1,movementBlock=set()):
        # add self
        movementBlock.add(self)
        
        # add things chained to the item
        for thing in self.chainedTo:
            if thing not in movementBlock and not thing == self:
                movementBlock.add(thing)
                thing.getAffectedByMovementDirection(direction,force=force,movementBlock=movementBlock)

        return movementBlock

    def moveDirection(self,direction,force=1,initialMovement=True):
        if self.walkable:
            # destroy small items instead of moving it
            self.destroy()
        else:
            oldPosition = (self.xPosition,self.yPosition)
            if direction == "north":
                newPosition = (self.xPosition,self.yPosition-1)
            elif direction == "south":
                newPosition = (self.xPosition,self.yPosition+1)
            elif direction == "west":
                newPosition = (self.xPosition-1,self.yPosition)
            elif direction == "east":
                newPosition = (self.xPosition+1,self.yPosition)

            # remove self from current position
            self.terrain.itemByCoordinates[oldPosition].remove(self)
            if len(self.terrain.itemByCoordinates) == 0:
                del self.terrain.itemByCoordinates[oldPosition]

            # destroy everything on target position
            if newPosition in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[newPosition]:
                    item.destroy()

            # place self on new position
            self.xPosition = newPosition[0]
            self.yPosition = newPosition[1]
            if newPosition in self.terrain.itemByCoordinates:
                self.terrain.itemByCoordinates[newPosition].append(self)
            else:
                self.terrain.itemByCoordinates[newPosition] = [self]

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
    do nothing
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
            newItem = Scrap(self.xPosition,self.yPosition,3,creator=self)
        else:
            newItem = Scrap(self.xPosition,self.yPosition,10,creator=self)
        newItem.room = self.room
        newItem.terrain = self.terrain

        # place scrap
        self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(newItem)
        self.terrain.itemsOnFloor.append(newItem)
            
'''
crushed something, basically raw metal
'''
class Scrap(Item):
    type = "Scrap"
        
    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="scrap",creator=None):
        self.amount = amount

        super().__init__(displayChars.scrap_light,xPosition,yPosition,creator=creator)
        self.bolted = False

        self.setWalkable()

        # set up saveing
        self.attributesToStore.extend([
               "amount"])

        self.initialState = self.getState()

    def moveDirection(self,direction,force=1,initialMovement=True):
        self.dropStuff()
        super().moveDirection(direction,force,initialMovement)

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
            newItem = Scrap(self.xPosition,self.yPosition,fallOffAmount,creator=self)
            newItem.room = self.room
            newItem.terrain = self.terrain

            # place the fallen off parts on map
            # bad code: should be handled by terrain
            self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(newItem)
            self.terrain.itemsOnFloor.append(newItem)
        self.setWalkable()


    def setWalkable(self):
        if self.amount < 5:
            self.walkable = True
        else:
            self.walkable = False
      

    @property
    def display(self):
        if self.amount < 5:
            return displayChars.scrap_light
        elif self.amount < 15:
            return displayChars.scrap_medium
        else:
            return displayChars.scrap_heavy
                
    '''
    get resistance to beeing moved depending on size
    '''
    def getResistance(self):
        return self.amount*2

    '''
    create bigger ball of scrap
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
            for item in foundScraps:
                if item == self:
                    continue
                self.amount += item.amount
                # bad code: direct manipulation of terrain state
                self.terrain.itemsOnFloor.remove(item)
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(item)

'''
dummy class for a corpse
'''
class Corpse(Item):
    type = "Corpse"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="corpse",creator=None):
        super().__init__(displayChars.corpse,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

'''
an character spawning item
'''
class GrowthTank(Item):
    type = "GrowthTank"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="growth tank",filled=False,creator=None):
        self.filled = filled
        if filled:
            super().__init__(displayChars.growthTank_filled,xPosition,yPosition,name=name,creator=creator)
        else:
            super().__init__(displayChars.growthTank_unfilled,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "filled"])

        # bad code: repetetive and easy to forget
        self.initialState = self.getState()

    '''
    manually eject character
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        if self.filled:
            self.eject()


    @property
    def display(self):
        if self.filled:
            return displayChars.growthTank_filled
        else:
            return displayChars.growthTank_unfilled

    '''
    ejecting a character
    '''
    def eject(self,character=None):
        # emtpy growth tank
        self.filled = False

        '''
        generate a name
        bad code: should be somewhere else
        bad code: redundant code
        '''
        def getRandomName(seed1=0,seed2=None):
            if seed2 == None:
                seed2 = seed1+(seed1//5)
            return names.characterFirstNames[seed1%len(names.characterFirstNames)]+" "+names.characterLastNames[seed2%len(names.characterLastNames)]

        # add character
        if not character:
            name = getRandomName(self.xPosition+self.room.timeIndex,self.yPosition+self.room.timeIndex)
            character = characters.Character(displayChars.staffCharactersByLetter[name[0].lower()],self.xPosition+1,self.yPosition,name=name,creator=self)

        # inhabit character
        character.fallUnconcious()
        character.hasFloorPermit = False
        self.room.addCharacter(character,self.xPosition+1,self.yPosition)
        character.reputation -= 1

        return character

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        if self.filled:
            self.display = displayChars.growthTank_filled
        else:
            self.display = displayChars.growthTank_unfilled

'''
basically a bed with a activatable cover
'''
class Hutch(Item):
    type = "Hutch"

    def __init__(self,xPosition=0,yPosition=0,name="Hutch",activated=False,creator=None):
        self.activated = activated
        super().__init__(displayChars.hutch_free,xPosition,yPosition,creator=creator)

        self.attributesToStore.extend([
               "activated"])

        self.initialState = self.getState()

    @property
    def display(self):
        if self.activated:
            return displayChars.hutch_occupied
        else:
            return displayChars.hutch_free

    '''
    open/close cover
    bad code: open close methods would be nice
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        if not self.activated:
            self.activated = True
        else:
            self.activated = False

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

'''
item for letting characters trigger somesthing
'''
class Lever(Item):
    type = "Lever"

    '''
    straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="lever",activated=False,creator=None):
        self.activated = activated
        super().__init__(displayChars.lever_notPulled,xPosition,yPosition,name=name,creator=creator)
        self.activateAction = None
        self.deactivateAction = None
        self.walkable = True
        self.bolted = True

        self.attributesToStore.extend([
               "activated"])

        self.initialState = self.getState()

    '''
    pull the lever!
    bad code: activate/deactive methods would be nice
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        if not self.activated:
            # activate the lever
            self.activated = True

            # run the action
            if self.activateAction:
                self.activateAction(self)
        else:
            # deactivate the lever
            self.activated = False

            # run the action
            if self.deactivateAction:
                self.activateAction(self)

        # notify listeners
        self.changed()

    @property
    def display(self):
        if self.activated:
            return displayChars.lever_pulled
        else:
            return displayChars.lever_notPulled

'''
heat source for generating steam and similar
'''
class Furnace(Item):
    type = "Furnace"

    '''
    straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Furnace",creator=None):
        self.activated = False
        self.boilers = []
        self.stopBoilingEvent = None
        super().__init__(displayChars.furnace_inactive,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "activated"])

        self.initialState = self.getState()

    '''
    fire the furnace
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        # select fuel
        # bad pattern: the player should be able to select fuel
        # bad pattern: coal should be preferred
        # bad code: try except clusterfuck
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
                character.inventory.remove(foundItem)

                if character.watched:
                    messages.append("*wush*")

                # get the boilers affected
                self.boilers = []
                for boiler in self.room.boilers:
                    if ((boiler.xPosition in [self.xPosition,self.xPosition-1,self.xPosition+1] and boiler.yPosition == self.yPosition) or boiler.yPosition in [self.yPosition-1,self.yPosition+1] and boiler.xPosition == self.xPosition):
                        self.boilers.append(boiler)

                # heat up boilers
                for boiler in self.boilers:
                    boiler.startHeatingUp()
                
                # make the furnace stop burning after some time
                event = src.events.FurnaceBurnoutEvent(self.room.timeIndex+30,creator=self)
                event.furnace = self

                # add burnout event 
                self.room.addEvent(event)

                # notify listeners
                self.changed()

    @property
    def display(self):
        if self.activated:
            return displayChars.furnace_active
        else:
            return displayChars.furnace_inactive

'''
a dummy for an interface with the mech communication network
bad code: this class is dummy only and basically is to be implemented
'''
class Commlink(Item):
    type = "CommLink"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Commlink",creator=None):
        super().__init__(displayChars.commLink,xPosition,yPosition,name=name,creator=creator)

    '''
    fake requesting and getting a coal refill
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        # add messages requesting coal
        # bad pattern: requesting coal in random room is not smart
        messages.append("Sigmund Bärenstein@Logisticcentre: we need more coal")
        messages.append("Logisticcentre@Sigmund Bärenstein: on its way")
    
        '''
        the event for stopping to burn after a while
        bad code: should be an abstract event calling a method
        '''
        class CoalRefillEvent(src.events.Event):
            '''
            straightforward state initialization
            '''
            def __init__(subself,tick,creator=None):
                super().__init__(tick,creator=creator)
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
        self.room.events.append(CoalRefillEvent(self.room.timeIndex+10,creator=self))

'''
should be a display, but is abused as vehicle control
bad code: use an actual vehicle control
'''
class Display(Item):
    type = "Display"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Display",creator=None):
        super().__init__(displayChars.display,xPosition,yPosition,name=name,creator=creator)

    '''
    map player controls to room movement 
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        # handle movement keystrokes
        '''
        move room to north
        '''
        def moveNorth():
            self.room.moveDirection("north",force=self.room.engineStrength)
        '''
        move room to south
        '''
        def moveSouth():
            self.room.moveDirection("south",force=self.room.engineStrength)
        '''
        move room to west
        '''
        def moveWest():
            self.room.moveDirection("west",force=self.room.engineStrength)
        '''
        move room to east
        '''
        def moveEast():
            self.room.moveDirection("east",force=self.room.engineStrength)

        '''
        reset key mapping
        '''
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
    type = "Wall"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Wall",creator=None):
        super().__init__(displayChars.wall,xPosition,yPosition,name=name,creator=creator)

'''
basic item with different appearance
'''
class Pipe(Item):
    type = "Pipe"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Pipe",creator=None):
        super().__init__(displayChars.pipe,xPosition,yPosition,name=name,creator=creator)

'''
basic item with different appearance
'''
class Coal(Item):
    type = "Coal"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Coal",creator=None):
        self.canBurn = True
        super().__init__(displayChars.coal,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False
        self.initialState = self.getState()

'''
a door for opening/closing and looking people in/out
'''
class Door(Item):
    type = "Door"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Door",creator=None):
        super().__init__(displayChars.door_closed,xPosition,yPosition,name=name,creator=creator)
        self.walkable = False
        self.initialState = self.getState()

    '''
    set state from dict
    bad code: should have a open attribute
    '''
    def setState(self,state):
        super().setState(state)
        if self.walkable:
            self.open(None)

    '''
    open or close door depending on state
    bad code: should have a open attribute
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        if self.walkable:
            self.close()
        else:
            self.open(character)
        self.changed()
    
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
                        # bad pattern: should only generate sound for nearby characters
                        messages.append("*TSCHUNK*")
                        self.close()

                self.room.addEvent(AutoCloseDoor(self.room.timeIndex+5))
        else:
            # refuse to open the door
            # bad code: should only apply tho watched characters
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
    type = "Pile"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal,creator=None):
        self.contains_canBurn = True # bad code: should be abstracted
        self.itemType = itemType
        self.numContained = 100
        super().__init__(displayChars.pile,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "numContained"])

        self.initialState = self.getState()

    '''
    take from the pile
    '''
    def apply(self,character):
        # check characters inventory
        if len(character.inventory) > 10:
            messages.append("you cannot carry more items")
            return

        # write log on impossible state
        if self.numContained < 1:
            debugMessages.append("something went seriously wrong. I should have morphed by now")
            return

        # spawn item to inventory
        character.inventory.append(self.itemType(creator=self))
        character.changed()
        messages.append("you take a piece of "+str(self.itemType.type))

        # reduce item count
        self.numContained -= 1

        if self.numContained == 1:
            # morph into a single item
            self.room.removeItem(self)
            new = self.itemType(creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.room.addItems([new])

        super().apply(character,silent=True)

    '''
    print info with item counter
    '''
    def getDetailedInfo(self):
        return super().getDetailedInfo()+" of "+str(self.type)+" containing "+str(self.numContained)

'''
basic item with different appearance
'''
class Acid(Item):
    type = "Acid"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal,creator=None):
        self.canBurn = True
        self.type = itemType
        self.type = "Acid"
        super().__init__(displayChars.acid,xPosition,yPosition,name=name,creator=creator)
        self.initialState = self.getState()

'''
used to connect rooms and items to drag them around
'''
class Chain(Item):
    type = "Chain"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="chain",creator=None):
        super().__init__(displayChars.chains,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False
        self.initialState = self.getState()

        self.chainedTo = []
        self.fixed = False

    '''
    attach/detach chain
    bad code: attaching and detaching should be methods
    bad code: only works on terrains
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        # chain to surrounding items/rooms
        # bad pattern: the user needs to be able to select to what to chain to
        if not self.fixed:
            if self.room:
                # bad code: NIY
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
    type = "Winch"

    '''
    call superclass constructor with modified paramters 
    '''
    def __init__(self,xPosition=0,yPosition=0,name="winch",creator=None):
        super().__init__(displayChars.winch_inactive,xPosition,yPosition,name=name,creator=creator)

'''
basic item with different appearance
'''
class MetalBars(Item):
    type = "MetalBars"

    def __init__(self,xPosition=0,yPosition=0,name="metal bar",creator=None):
        super().__init__("==",xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False

'''
produces steam from heat
bad code: sets the rooms steam generation directly without using pipes
'''
class Boiler(Item):
    type = "Boiler"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="boiler",creator=None):
        super().__init__(displayChars.boiler_inactive,xPosition,yPosition,name=name,creator=creator)
        self.isBoiling = False
        self.isHeated = False
        self.startBoilingEvent = None
        self.stopBoilingEvent = None
        self.initialState = self.getState()

    '''
    start producing steam after a delay
    '''
    def startHeatingUp(self):
        if self.isHeated:
            return

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
                    # bad pattern: should only make noise for nearby things
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
        if not self.isHeated:
            return
        # flag self as heated
        self.isHeated = False

        # abort any heating up
        if self.startBoilingEvent:
            self.room.removeEvent(self.startBoilingEvent)
            self.startBoilingEvent = None
        if not self.stopBoilingEvent and self.isBoiling:
            '''
            the event for stopping to boil
            bad code: should be an abstract event calling a method
            '''
            class StopBoilingEvent(object):
                id = "StopBoilingEvent"
                type = "StopBoilingEvent"

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

            # stop boiling after some time
            self.stopBoilingEvent = StopBoilingEvent(self.room.timeIndex+5)
            self.room.addEvent(self.stopBoilingEvent)

        # notify listeners
        self.changed()
            
'''
steam sprayer used as a prop in the vat
'''
class Spray(Item):
    type = "Spray"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="spray",direction=None,creator=None):
        # skin acording to spray direction
        if direction == None:
            direction = "left"

        self.direction = direction

        super().__init__(displayChars.spray_left_inactive,xPosition,yPosition,name=name,creator=creator)

        # set up saveing
        self.attributesToStore.extend([
               "direction"])

        self.initialState = self.getState()

    '''
    set appearance depending on energy supply
    bad code: energy supply is directly taken from the machine room
    '''
    @property
    def display(self):
        if direction == "left":
            if terrain.tutorialMachineRoom.steamGeneration == 0:
                return displayChars.spray_left_inactive
            elif terrain.tutorialMachineRoom.steamGeneration == 1:
                return displayChars.spray_left_stage1
            elif terrain.tutorialMachineRoom.steamGeneration == 2:
                return displayChars.spray_left_stage2
            elif terrain.tutorialMachineRoom.steamGeneration == 3:
                return displayChars.spray_left_stage3
        else:
            if terrain.tutorialMachineRoom.steamGeneration == 0:
                return displayChars.spray_right_inactive
            elif terrain.tutorialMachineRoom.steamGeneration == 1:
                return displayChars.spray_right_stage1
            elif terrain.tutorialMachineRoom.steamGeneration == 2:
                return displayChars.spray_right_stage2
            elif terrain.tutorialMachineRoom.steamGeneration == 3:
                return displayChars.spray_right_stage3
            
'''
marker ment to be placed by characters and to control actions with
'''
class MarkerBean(Item):
    type = "MarkerBean"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="bean",creator=None):
        self.activated = False
        super().__init__(" -",xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False

        self.attributesToStore.extend([
               "activated"])

        self.initialState = self.getState()

    @property
    def display(self):
        if self.activated:
            return "x-"
        else:
            return " -"

    '''
    avtivate marker
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        self.activated = True

'''
machine for filling up goo flasks
'''
class GooDispenser(Item):
    type = "GooDispenser"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo dispenser",creator=None):
        self.activated = False
        super().__init__("g%",xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "activated"])

        self.initialState = self.getState()
    
    '''
    fill goo flask
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        for item in character.inventory:
            if isinstance(item,GooFlask):
                item.uses = 100
        self.activated = True

'''
flask with food to carry around and drink from
'''
class GooFlask(Item):
    type = "GooFlask"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo flask",creator=None):
        self.uses = 100
        super().__init__(" -",xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False
        self.description = "a flask conatining goo"

        self.attributesToStore.extend([
               "uses"])

        self.initialState = self.getState()

    '''
    drink from flask
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        if self.uses > 0:
            self.uses -= 1
            self.changed()
            character.satiation = 1000
            character.changed()

    @property
    def display(self):
        displayByUses = ["ò ","ò.","ò,","ò-","ò~","ò="]
        return (urwid.AttrSpec("#3f3","black"),displayByUses[self.uses//20])

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
    type = "ObjectDispenser"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="object dispenser",creator=None):
        super().__init__("U\\",xPosition,yPosition,name=name,creator=creator)
        self.initialState = self.getState()

    '''
    drop goo flask
    '''
    def dispenseObject(self):
        new = GooFlask(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition+1
        self.room.addItems([new])

'''
token object ment to produce anything from metal bars
bad pattern: serves as dummy for actual production lines
'''
class ProductionArtwork(Item):
    type = "ProductionArtwork"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="production artwork",creator=None):
        super().__init__("U\\",xPosition,yPosition,name=name,creator=creator)

    '''
    trigger production of a player selected item
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)
        options = []
        for key,value in itemMap.items():
            options.append((value,key))
        self.submenue = interaction.SelectionMenu("select the item to produce",options)
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
        metalBar = None
        for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
            if isinstance(item,MetalBars):
                metalBar = item
                break
        
        if not metalBar:
            # refuse production without ressources
            messages.append("no metal bars available")
            return

        # remove ressources
        self.room.removeItem(item)

        # spawn new item
        new = itemType(creator=self)
        new.xPosition = self.xPosition-1
        new.yPosition = self.yPosition
        new.bolted = False
        self.room.addItems([new])

'''
scrap to metal bar converter
'''
class ScrapCompactor(Item):
    type = "ScrapCompactor"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="scrap compactor",creator=None):
        super().__init__("U\\",xPosition,yPosition,name=name,creator=creator)

    '''
    produce a metal bar
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)
        # fetch input scrap
        scrap = None
        for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
            if isinstance(item,Scrap):
                scrap = item

        if not scrap:
            # refuse to produce without ressources
            messages.append("no scraps available")
            return
       
        # remove ressources
        self.room.removeItem(item)

        # spawn the metal bar
        new = MetalBars(creator=self)
        new.xPosition = self.xPosition-1
        new.yPosition = self.yPosition
        self.room.addItems([new])

# maping from strings to all items
# should be extendable
itemMap = {
            "Item":Item,
            "Scrap":Scrap,
            "Corpse":Corpse,
            "GrowthTank":GrowthTank,
            "Hutch":Hutch,
            "Lever":Lever,
            "Furnace":Furnace,
            "CommLink":Commlink,
            "Display":Display,
            "Wall":Wall,
            "Pipe":Pipe,
            "Coal":Coal,
            "Door":Door,
            "Pile":Pile,
            "Acid":Acid,
            "Chain":Chain,
            "Winch":Winch,
            "MetalBars":MetalBars,
            "Boiler":Boiler,
            "Spray":Spray,
            "MarkerBean":MarkerBean,
            "GooDispenser":GooDispenser,
            "GooFlask":GooFlask,
            "ProductionArtwork":ProductionArtwork,
            "ScrapCompactor":ScrapCompactor,
            "ObjectDispenser":OjectDispenser
}

'''
get item instances from dict state
'''
def getItemFromState(state):
    item = itemMap[state["type"]](creator=void)
    item.setState(state)
    loadingRegistry.register(item)
    return item

