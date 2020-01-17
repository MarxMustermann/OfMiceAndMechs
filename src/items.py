####################################################################################
###
##     items and item related code belongs here 
#
####################################################################################

# load basic libs
import urwid
import json

# load basic internal libs
import src.saveing
import src.events

# bad code: global state
messages = None
characters = None
displayChars = None
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

        self.customDescription = None

        # set up metadata for saving
        self.attributesToStore.extend([
               "mayContainMice","name","type","walkable","xPosition","yPosition","bolted"])

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
    bad code: name and function say different things
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
            character.messages.append("i can't do anything useful with this")

    '''
    get picked up by the supplied character
    '''
    def pickUp(self,character):
        if self.xPosition == None or self.yPosition == None:
            return

        # apply restrictions
        if self.bolted:
            character.messages.append("you cannot pick up bolted items")
            return

        character.messages.append("you pick up a "+self.type)

        # bad code: should be a simple self.container.removeItem(self)
        if self.room:
            # remove item from room
            container = self.room
            container.removeItem(self)
        else:
            # remove item from terrain
            # bad code: should be handled by the terrain
            container = self.terrain
            container.itemsOnFloor.remove(self)
            container.itemByCoordinates[(self.xPosition,self.yPosition)].remove(self)
            if not container.itemByCoordinates[(self.xPosition,self.yPosition)]:
                del container.itemByCoordinates[(self.xPosition,self.yPosition)]

            if not self.walkable:
                terrain.calculatePathMap()

        """
        # spawn mice with pseudorandom chance
        # bad code: this code should be somewhere else
        if ((self.mayContainMice and (gamestate.tick+self.xPosition+self.yPosition)%10 == 0 and not self.walkable) or
           (not self.mayContainMice and (gamestate.tick+self.xPosition-self.yPosition)%100 == 0 and not self.walkable)):

            # create mouse
            mouse = characters.Mouse(creator=self)
        
            # make mouse attack the player
            quest = quests.MetaQuestSequence([],creator=self)
            quest.addQuest(quests.MoveQuestMeta(room=self.room,x=self.xPosition,y=self.yPosition,creator=self))
            quest.addQuest(quests.KnockOutQuest(character,lifetime=30,creator=self))
            quest.addQuest(quests.WaitQuest(lifetime=5,creator=self))
            mouse.assignQuest(quest,active=True)

            # make mouse vanish after successful attack
            quest.endTrigger = {"container":mouse,"method":"vanish"}

            if self.room:
                room = self.room
                xPosition = self.xPosition
                yPosition = self.yPosition

                # add mouse
                room.addCharacter(mouse,xPosition,yPosition)

                '''
                set up an ambush if target left the room
                '''
                def setUpAmbush(characterLeaving):

                    # only trigger for target
                    if not character == characterLeaving:
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
                    room.delListener(setUpAmbush,"left room")

                    '''
                    trigger ambush
                    '''
                    def triggerAmbush(characterEntering):
                        # make mouse atack anybody entering the room
                        quest.addQuest(quests.MoveQuestMeta(room=room,x=xPosition,y=yPosition,creator=self))
                        quest.addQuest(quests.KnockOutQuest(characterEntering,lifetime=10,creator=self))

                        # remove old quests
                        while len(quest.subQuests) > 2:
                            subQuest = quest.subQuests[-1]
                            subQuest.deactivate()
                            quest.subQuests.remove(subQuest)

                        # remove self from wath list
                        room.delListener(triggerAmbush,"entered room")
                        
                    # start watching for somebody entering the room
                    room.addListener(triggerAmbush,"entered room")

                # start watching for character leaving the room
                room.addListener(setUpAmbush,"left room")
            else:
                # add mouse
                self.terrain.addCharacter(mouse,self.xPosition,self.yPosition)
        """

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

    '''
    move the item
    '''
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
            
    def getDiffState(self):
        state = super().getDiffState()

        state["type"] = self.type
        state["xPosition"] = self.xPosition
        state["yPosition"] = self.yPosition

        return state

    def getLongInfo(self):
        return

'''
crushed something, basically raw metal
'''
class Scrap(Item):
    type = "Scrap"
        
    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="scrap",creator=None):

        self.amount = 1

        super().__init__(displayChars.scrap_light,xPosition,yPosition,creator=creator,name=name)
        
        # set up metadata for saveing
        self.attributesToStore.extend([
               "amount"])
        
        self.initialState = self.getState()

        self.bolted = False

        self.amount = amount

        self.setWalkable()

    '''
    move the item and leave residue
    '''
    def moveDirection(self,direction,force=1,initialMovement=True):
        self.dropStuff()
        super().moveDirection(direction,force,initialMovement)

    '''
    leave a trail of pieces
    bad code: only works on terrain
    '''
    def dropStuff(self):
        self.setWalkable()

        # only drop something if there is something left to drop
        if self.amount <= 1:
            return

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

    '''
    recalculate the walkabe attribute
    '''
    def setWalkable(self):
        if self.amount < 5:
            self.walkable = True
        else:
            self.walkable = False
      
    '''
    recalculate the display char
    '''
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
    destroying scrap means to merge the scrap 
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
        else:
            flask = None
            for item in character.inventory:
                if isinstance(item,GooFlask):
                    if item.uses == 100:
                        flask = item
            if flask:
                flask.uses = 0
                flask.changed()
                self.filled = True
                self.changed()
            else:
                character.messages.append("you need to have a full goo flask to refill the growth tank")

    '''
    render the growth tank
    '''
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

            character.solvers = [
                      "SurviveQuest",
                      "Serve",
                      "NaiveMoveQuest",
                      "MoveQuestMeta",
                      "NaiveActivateQuest",
                      "ActivateQuestMeta",
                      "NaivePickupQuest",
                      "PickupQuestMeta",
                      "DrinkQuest",
                      "ExamineQuest",
                      "FireFurnaceMeta",
                      "CollectQuestMeta",
                      "WaitQuest"
                      "NaiveDropQuest",
                      "NaiveDropQuest",
                      "DropQuestMeta",
                    ]

        # inhabit character
        character.fallUnconcious()
        character.hasFloorPermit = False
        self.room.addCharacter(character,self.xPosition+1,self.yPosition)
        character.revokeReputation(amount=4,reason="beeing helpless")

        return character

'''
basically a bed with a activatable cover
'''
class Hutch(Item):
    type = "Hutch"

    def __init__(self,xPosition=0,yPosition=0,name="Hutch",activated=False,creator=None):
        self.activated = activated
        super().__init__(displayChars.hutch_free,xPosition,yPosition,creator=creator)

        # bad code: set metadata for saving
        self.attributesToStore.extend([
               "activated"])

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    '''
    render the hutch
    '''
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
item for letting characters trigger something
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

        # set metadata for saving
        self.attributesToStore.extend([
               "activated"])

        # bad code: repetetive and easy to forgett
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

    '''
    render the lever
    '''
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

        # set metadata for saving
        self.attributesToStore.extend([
               "activated"])

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    '''
    fire the furnace
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            return
        
        # select fuel
        # bad pattern: the player should be able to select fuel
        # bad pattern: coal should be preferred
        foundItem = None
        for item in character.inventory:
            canBurn = False
            if hasattr(item,"canBurn"):
                canBurn = item.canBurn

            if not canBurn:
                continue
            foundItem = item

        # refuse to fire the furnace without fuel
        if not foundItem:
            # bad code: return would be preferable to if/else
            if character.watched:
                character.messages.append("you need coal to fire the furnace and you have no coal in your inventory")
        else:
            # refuse to fire burning furnace
            if self.activated:
                # bad code: return would be preferable to if/else
                if character.watched:
                    character.messages.append("already burning")
            # fire the furnace
            else:
                self.activated = True

                # destroy fuel
                character.inventory.remove(foundItem)
                character.changed()

                # add fluff
                if character.watched:
                    character.messages.append("you fire the furnace")

                # get the boilers affected
                self.boilers = []
                #for boiler in self.room.boilers:
                for boiler in self.room.itemsOnFloor:
                    if isinstance(boiler, src.items.Boiler):
                        if ((boiler.xPosition in [self.xPosition,self.xPosition-1,self.xPosition+1] and boiler.yPosition == self.yPosition) or boiler.yPosition in [self.yPosition-1,self.yPosition+1] and boiler.xPosition == self.xPosition):
                            self.boilers.append(boiler)

                # heat up boilers
                for boiler in self.boilers:
                    boiler.startHeatingUp()
                
                # make the furnace stop burning after some time
                event = src.events.FurnaceBurnoutEvent(self.room.timeIndex+30,creator=self)
                event.furnace = self
                self.room.addEvent(event)

                # notify listeners
                self.changed()

    '''
    render the furnace
    '''
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
        character.messages.append("Sigmund Bärenstein@Logisticcentre: we need more coal")
        character.messages.append("Logisticcentre@Sigmund Bärenstein: on its way")
    
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
                character.messages.append("*rumbling*")
                character.messages.append("*rumbling*")
                character.messages.append("*smoke and dust on cole piles and neighbour fields*")
                character.messages.append("*a chunk of coal drops onto the floor*")
                character.messages.append("*smoke clears*")

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

        if self.room:
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

            if not "stealKey" in character.macroState:
                character.macroState["stealKey"] = {}

            '''
            reset key mapping
            '''
            def disapply():
                del character.macroState["stealKey"][commandChars.move_north]
                del character.macroState["stealKey"][commandChars.move_south]
                del character.macroState["stealKey"][commandChars.move_west]
                del character.macroState["stealKey"][commandChars.move_east]
                del character.macroState["stealKey"]["up"]
                del character.macroState["stealKey"]["down"]
                del character.macroState["stealKey"]["right"]
                del character.macroState["stealKey"]["left"]
                del character.macroState["stealKey"][commandChars.activate]

            # map the keystrokes
            character.macroState["stealKey"][commandChars.move_north] = moveNorth
            character.macroState["stealKey"][commandChars.move_south] = moveSouth
            character.macroState["stealKey"][commandChars.move_west] = moveWest
            character.macroState["stealKey"][commandChars.move_east] = moveEast
            character.macroState["stealKey"]["up"] = moveNorth
            character.macroState["stealKey"]["down"] = moveSouth
            character.macroState["stealKey"]["left"] = moveWest
            character.macroState["stealKey"]["right"] = moveEast
            character.macroState["stealKey"][commandChars.activate] = disapply
        else:
            wallLeft = False
            for offset in range(1,15):
                pos = (self.xPosition-offset,self.yPosition)
                if pos in self.terrain.itemByCoordinates:
                    for item in self.terrain.itemByCoordinates[pos]:
                        if isinstance(item,Wall) or isinstance(item,Door):
                            wallLeft = item
                            break
                if wallLeft:
                    break
            wallRight = False
            for offset in range(1,15):
                pos = (self.xPosition+offset,self.yPosition)
                if pos in self.terrain.itemByCoordinates:
                    for item in self.terrain.itemByCoordinates[pos]:
                        if isinstance(item,Wall) or isinstance(item,Door):
                            wallRight = item
                            break
                if wallRight:
                    break
            wallTop = False
            for offset in range(1,15):
                pos = (self.xPosition,self.yPosition-offset)
                if pos in self.terrain.itemByCoordinates:
                    for item in self.terrain.itemByCoordinates[pos]:
                        if isinstance(item,Wall) or isinstance(item,Door):
                            wallTop = item
                            break
                if wallTop:
                    break
            wallBottom = False
            for offset in range(1,15):
                pos = (self.xPosition,self.yPosition+offset)
                if pos in self.terrain.itemByCoordinates:
                    for item in self.terrain.itemByCoordinates[pos]:
                        if isinstance(item,Wall) or isinstance(item,Door):
                            wallBottom = item
                            break
                if wallBottom:
                    break

            if not ( wallLeft and wallRight and wallTop and wallBottom) :
                character.messages.append("no boundaries found")
                character.messages.append((wallLeft,wallRight,wallTop,wallBottom))
                return

            roomLeft = self.xPosition-wallLeft.xPosition
            roomRight = wallRight.xPosition-self.xPosition
            roomTop = self.yPosition-wallTop.yPosition
            roomBottom = wallBottom.yPosition-self.yPosition

            wallMissing = False
            items = []
            character.messages.append([roomLeft,roomRight,roomTop,roomBottom,])
            for x in range(-roomLeft,roomRight+1):
                pos = (self.xPosition+x,self.yPosition-roomTop)
                wallFound = None 
                if pos in self.terrain.itemByCoordinates:
                    for item in self.terrain.itemByCoordinates[pos]:
                        if isinstance(item,Wall) or isinstance(item,Door):
                            wallFound = item
                            items.append(item)
                            break
                if not wallFound:
                    wallMissing = True
                    break
            for y in range(-roomTop,roomBottom+1):
                pos = (self.xPosition-roomLeft,self.yPosition+y)
                wallFound = None 
                if pos in self.terrain.itemByCoordinates:
                    for item in self.terrain.itemByCoordinates[pos]:
                        if isinstance(item,Wall) or isinstance(item,Door):
                            wallFound = item
                            items.append(item)
                            break
                if not wallFound:
                    wallMissing = True
                    break
            for y in range(-roomTop,roomBottom+1):
                pos = (self.xPosition+roomRight,self.yPosition+y)
                wallFound = None 
                if pos in self.terrain.itemByCoordinates:
                    for item in self.terrain.itemByCoordinates[pos]:
                        if isinstance(item,Wall) or isinstance(item,Door):
                            wallFound = item
                            items.append(item)
                            break
                if not wallFound:
                    wallMissing = True
                    break
            for x in range(-roomLeft,roomRight+1):
                pos = (self.xPosition+x,self.yPosition+roomBottom)
                wallFound = None 
                if pos in self.terrain.itemByCoordinates:
                    for item in self.terrain.itemByCoordinates[pos]:
                        if isinstance(item,Wall) or isinstance(item,Door):
                            wallFound = item
                            items.append(item)
                            break
                if not wallFound:
                    wallMissing = True
                    break

            if wallMissing:
                character.messages.append("wall missing")
                return

            character.messages.append(len(items))
            items.append(self)
            for item in items:
                try:
                    terrain.removeItem(item,recalculate=False)
                except:
                    character.messages.append(("failed to remove item",item))

            door = None
            for item in items:
                if isinstance(item,Door):
                    if not door:
                        door = item
                    else:
                        character.messages.append("too many doors")
                        return
            if not door:
                character.messages.append("too little doors")
                return

            import src.rooms
            doorPos = (roomLeft+door.xPosition-self.xPosition,roomTop+door.yPosition-self.yPosition)
            room = src.rooms.EmptyRoom(self.xPosition//15,self.yPosition//15,self.xPosition%15-roomLeft,self.yPosition%15-roomTop,creator=self)
            room.reconfigure(roomLeft+roomRight+1,roomTop+roomBottom+1,doorPos)

            xOffset = character.xPosition-self.xPosition
            yOffset = character.yPosition-self.yPosition

            self.terrain.removeCharacter(character)
            self.terrain.addRooms([room])
            character.xPosition = roomLeft+xOffset
            character.yPosition = roomTop+yOffset
            room.addCharacter(character,roomLeft+xOffset,roomTop+yOffset)

            self.xPosition = roomLeft
            self.yPosition = roomTop
            room.addItems([self])

'''
'''
class RoomBuilder(Item):
    type = "RoomBuilder"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="RoomBuilder",creator=None):
        super().__init__("RB",xPosition,yPosition,name=name,creator=creator)

    '''
    map player controls to room movement 
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        wallLeft = False
        for offset in range(1,15):
            pos = (self.xPosition-offset,self.yPosition)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallLeft = item
                        break
            if wallLeft:
                break
        wallRight = False
        for offset in range(1,15):
            pos = (self.xPosition+offset,self.yPosition)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallRight = item
                        break
            if wallRight:
                break
        wallTop = False
        for offset in range(1,15):
            pos = (self.xPosition,self.yPosition-offset)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallTop = item
                        break
            if wallTop:
                break
        wallBottom = False
        for offset in range(1,15):
            pos = (self.xPosition,self.yPosition+offset)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallBottom = item
                        break
            if wallBottom:
                break

        if not ( wallLeft and wallRight and wallTop and wallBottom) :
            character.messages.append("no boundaries found")
            character.messages.append((wallLeft,wallRight,wallTop,wallBottom))
            return

        roomLeft = self.xPosition-wallLeft.xPosition
        roomRight = wallRight.xPosition-self.xPosition
        roomTop = self.yPosition-wallTop.yPosition
        roomBottom = wallBottom.yPosition-self.yPosition

        wallMissing = False
        items = []
        character.messages.append([roomLeft,roomRight,roomTop,roomBottom,])
        for x in range(-roomLeft,roomRight+1):
            pos = (self.xPosition+x,self.yPosition-roomTop)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallFound = item
                        items.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for y in range(-roomTop,roomBottom+1):
            pos = (self.xPosition-roomLeft,self.yPosition+y)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallFound = item
                        items.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for y in range(-roomTop,roomBottom+1):
            pos = (self.xPosition+roomRight,self.yPosition+y)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallFound = item
                        items.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for x in range(-roomLeft,roomRight+1):
            pos = (self.xPosition+x,self.yPosition+roomBottom)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallFound = item
                        items.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break

        if wallMissing:
            character.messages.append("wall missing")
            return

        character.messages.append(len(items))
        items.append(self)
        for item in items:
            try:
                terrain.removeItem(item,recalculate=False)
            except:
                character.messages.append(("failed to remove item",item))

        door = None
        for item in items:
            if isinstance(item,Door):
                if not door:
                    door = item
                else:
                    character.messages.append("too many doors")
                    return
        if not door:
            character.messages.append("too little doors")
            return

        import src.rooms
        doorPos = (roomLeft+door.xPosition-self.xPosition,roomTop+door.yPosition-self.yPosition)
        room = src.rooms.EmptyRoom(self.xPosition//15,self.yPosition//15,self.xPosition%15-roomLeft,self.yPosition%15-roomTop,creator=self)
        room.reconfigure(roomLeft+roomRight+1,roomTop+roomBottom+1,doorPos)

        xOffset = character.xPosition-self.xPosition
        yOffset = character.yPosition-self.yPosition

        self.terrain.removeCharacter(character)
        self.terrain.addRooms([room])
        character.xPosition = roomLeft+xOffset
        character.yPosition = roomTop+yOffset
        room.addCharacter(character,roomLeft+xOffset,roomTop+yOffset)

        self.xPosition = roomLeft
        self.yPosition = roomTop
        room.addItems([self])


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

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

'''
a door for opening/closing and locking people in/out
# bad code: should use a rendering method
'''
class Door(Item):
    type = "Door"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Door",creator=None):
        super().__init__(displayChars.door_closed,xPosition,yPosition,name=name,creator=creator)
        self.walkable = False

        # bad code: repetetive and easy to forgett
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
        if not self.room:
            return
            character.messages.append("you can only use doors within rooms")
            return

        # check if the door can be opened
        if (self.room.isContainment and character.room):
            # bad code: should only apply tho watched characters
            character.messages.append("you cannot open the door from the inside")
            return

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
                    character.messages.append("*TSCHUNK*")
                    self.close()

            self.room.addEvent(AutoCloseDoor(self.room.timeIndex+5))

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

        # set metadata for saving
        self.attributesToStore.extend([
               "numContained"])

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    '''
    take from the pile
    '''
    def apply(self,character):
        # write log on impossible state
        if self.numContained < 1:
            debugMessages.append("something went seriously wrong. I should have morphed by now")
            return

        # check characters inventory
        if len(character.inventory) > 10:
            character.messages.append("you cannot carry more items")
            return

        # spawn item to inventory
        character.inventory.append(self.itemType(creator=self))
        character.changed()
        character.messages.append("you take a piece of "+str(self.itemType.type))

        # reduce item count
        self.numContained -= 1

        # morph into a single item
        if self.numContained == 1:
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
        return super().getDetailedInfo()+" of "+str(self.itemType.type)+" containing "+str(self.numContained)

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

        # bad code: repetetive and easy to forgett
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

        # bad code: repetetive and easy to forgett
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
                character.messages.append("TODO")
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

                # set chaining for self
                self.chainedTo = []
                self.chainedTo.extend(items)
                self.chainedTo.extend(rooms)

                # set chaining for chained objects
                for thing in self.chainedTo:
                    thing.chainedTo.append(self)
                    character.messages.append(thing.chainedTo)

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

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    '''
    start producing steam after a delay
    '''
    def startHeatingUp(self):

        # do not heat up heated items
        if self.isHeated:
            return

        # flag self as heated
        self.isHeated = True

        # abort cooling down
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
                id = "StartBoilingEvent"
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
        # don't do cooldown on cold boilers
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
    call superclass constructor with modified parameters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="spray",direction=None,creator=None):
        # skin acording to spray direction
        if direction == None:
            direction = "left"

        self.direction = direction

        super().__init__(displayChars.spray_left_inactive,xPosition,yPosition,name=name,creator=creator)

        # set up meta information for saveing
        self.attributesToStore.extend([
               "direction"])

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    '''
    set appearance depending on energy supply
    bad code: energy supply is directly taken from the machine room
    '''
    @property
    def display(self):
        if self.direction == "left":
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

        # set up meta information for saveing
        self.attributesToStore.extend([
               "activated"])

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    '''
    render the marker
    '''
    @property
    def display(self):
        if self.activated:
            return "x-"
        else:
            return " -"

    '''
    activate marker
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        character.messages.append(character.name+" activates a marker bean")
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
        self.baseName = name
        super().__init__("g%",xPosition,yPosition,name=name,creator=creator)

        # set up meta information for saveing
        self.attributesToStore.extend([
               "activated","charges"])

        self.charges = 0

        self.description = self.baseName + " (%s charges)"%(self.charges)

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    def setDescription(self):
        self.description = self.baseName + " (%s charges)"%(self.charges)
    
    '''
    fill goo flask
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.charges:
            character.messages.append("the dispenser has no charges")
            return

        filled = False
        for item in character.inventory:
            if isinstance(item,GooFlask) and not item.uses == 100:
                item.uses = 100
                filled = True
                self.charges -= 1 
                self.description = self.baseName + " (%s charges)"%(self.charges)
                break
        if filled:
            character.messages.append("you fill the goo flask")
        self.activated = True

    def addCharge(self):
        self.charges += 1 
        self.description = self.baseName + " (%s charges)"%(self.charges)

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

'''
'''
class MaggotFermenter(Item):
    type = "MaggotFermenter"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="maggot fermenter",creator=None):
        self.activated = False
        super().__init__("%0",xPosition,yPosition,name=name,creator=creator)

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()
    
    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # fetch input scrap
        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,VatMaggot):
                    items.append(item)

        # refuse to produce without ressources
        if len(items) < 10:
            character.messages.append("not enough maggots")
            return
       
        # remove ressources
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.room.removeItem(item)

        # spawn the new item
        new = BioMass(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

'''
'''
class GooProducer(Item):
    type = "GooProducer"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo producer",creator=None):
        self.activated = False
        super().__init__("%>",xPosition,yPosition,name=name,creator=creator)

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()
    
    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # fetch input scrap
        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,PressCake):
                    items.append(item)

        # refuse to produce without ressources
        if len(items) < 10:
            character.messages.append("not enough press cakes")
            return
       
        # refill goo dispenser
        dispenser = None
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if isinstance(item,GooDispenser):
                    dispenser = item
        if not dispenser:
            character.messages.append("no goo dispenser attached")
            return 

        # remove ressources
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.room.removeItem(item)

        dispenser.addCharge()

'''
'''
class BioPress(Item):
    type = "BioPress"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="bio press",creator=None):
        self.activated = False
        super().__init__("%=",xPosition,yPosition,name=name,creator=creator)

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()
    
    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # fetch input scrap
        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,BioMass):
                    items.append(item)

        # refuse to produce without ressources
        if len(items) < 10:
            character.messages.append("not enough bio mass")
            return
       
        # remove ressources
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.room.removeItem(item)

        # spawn the new item
        new = PressCake(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

'''
flask with food to carry around and drink from
'''
class GooFlask(Item):
    type = "GooFlask"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo flask",creator=None):
        self.uses = 0
        super().__init__(" -",xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False
        self.description = "a flask containing goo"

        # set up meta information for saveing
        self.attributesToStore.extend([
               "uses"])

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    '''
    drink from flask
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # handle edge case
        if self.uses <= 0:
            if character.watched:
                character.messages.append("you drink from your flask, but it is empty")
            return

        # print feedback
        if character.watched:
            if not self.uses == 1:
                character.messages.append("you drink from your flask")
            else:
                character.messages.append("you drink from your flask and empty it")

        # change state
        self.uses -= 1
        self.changed()
        character.satiation = 1000
        character.changed()

    '''
    render based on fill amount
    '''
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
    '''
    def __init__(self,xPosition=None,yPosition=None, name="object dispenser",creator=None):
        super().__init__("U\\",xPosition,yPosition,name=name,creator=creator)

        self.storage = []
        counter = 0
        while counter < 5:
            self.storage.append(GooFlask(creator=self))
            counter += 1

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    '''
    drop goo flask
    '''
    def dispenseObject(self):
        if len(self.storage):
            new = self.storage.pop()
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition+1
            self.room.addItems([new])
        else:
            messages.append("the object dispenser is empty")

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
        self.coolDown = 10000
        self.coolDownTimer = -self.coolDown

        super().__init__("ßß",xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])

    '''
    trigger production of a player selected item
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        # gather a metal bar
        metalBar = None
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if isinstance(item,MetalBars):
                   metalBar = item
                   break
        if not metalBar:
            return
        
        if gamestate.tick < self.coolDownTimer+self.coolDown:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return

        excludeList = ("ProductionArtwork","Machine","Tree","Scrap","Corpse","Acid","Item","Pile","InfoScreen","CoalMine","RoomBuilder","BluePrint",)

        options = []
        for key,value in itemMap.items():
            if key in excludeList:
                continue
            options.append((value,key))
        self.submenue = interaction.SelectionMenu("select the item to produce",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.produceSelection

    '''
    trigger production of the selected item
    '''
    def produceSelection(self):
        self.produce(self.submenue.selection)

    '''
    produce an item
    '''
    def produce(self,itemType,resultType=None):
        self.coolDownTimer = gamestate.tick

        # gather a metal bar
        metalBar = None
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if isinstance(item,MetalBars):
                   metalBar = item
                   break
        
        # refuse production without ressources
        if not metalBar:
            messages.append("no metal bars available - place a metal bar to left/west")
            return

        # remove ressources
        self.room.removeItem(item)

        # spawn new item
        new = itemType(creator=self)
        new.xPosition = self.xPosition-1
        new.yPosition = self.yPosition
        new.bolted = False
        self.room.addItems([new])

    def getLongInfo(self):
        text = """
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This machine can build almost anything, but is very slow.

Prepare for production by placing metal bars to the west/left of this machine.
Activate the machine to start producing. You will be shown a list of things to produce.
Select the thing to produce and confirm.

After using this machine you need to wait %s ticks till you can use this machine again.
"""%(self.coolDown,)

        coolDownLeft = self.coolDown-(gamestate.tick-self.coolDownTimer)
        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

"""%(coolDownLeft,)
        else:
            text += """
Currently you do not have to wait to use this machine.

"""
        return text

'''
scrap to metal bar converter
'''
class ScrapCompactor(Item):
    type = "ScrapCompactor"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="scrap compactor",creator=None):
        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        
        super().__init__("RC",xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])

    '''
    produce a metal bar
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        # fetch input scrap
        scrap = None
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if isinstance(item,Scrap):
                    scrap = item
                    break

        if gamestate.tick < self.coolDownTimer+self.coolDown:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = gamestate.tick

        # refuse to produce without ressources
        if not scrap:
            character.messages.append("no scraps available")
            return

        # remove ressources
        self.room.removeItem(item)

        # spawn the metal bar
        new = MetalBars(creator=self)
        new.xPosition = self.xPosition-1
        new.yPosition = self.yPosition
        self.room.addItems([new])

'''
'''
class Scraper(Item):
    type = "Scraper"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="scraper",creator=None):
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        
        super().__init__("RS",xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])

    '''
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        # fetch input scrap
        itemFound = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                itemFound = item
                break

        if gamestate.tick < self.coolDownTimer+self.coolDown:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = gamestate.tick

        # refuse to produce without ressources
        if not itemFound:
            character.messages.append("no items available")
            return

        # remove ressources
        self.room.removeItem(item)

        # spawn scrap
        new = Scrap(self.xPosition,self.yPosition,10,creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

'''
'''
class Sorter(Item):
    type = "Sorter"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="sorter",creator=None):
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        
        super().__init__("U\\",xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])

    '''
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        # fetch input scrap
        itemFound = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                itemFound = item
                break

        compareItemFound = None
        if (self.xPosition,self.yPosition-1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                compareItemFound = item
                break

        if gamestate.tick < self.coolDownTimer+self.coolDown:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = gamestate.tick

        # refuse to produce without ressources
        if not itemFound:
            character.messages.append("no items available")
            return
        if not compareItemFound:
            character.messages.append("no compare items available")
            return

        # remove ressources
        self.room.removeItem(itemFound)

        if itemFound.type == compareItemFound.type:
            itemFound.xPosition = self.xPosition
            itemFound.yPosition = self.yPosition+1
        else:
            itemFound.xPosition = self.xPosition+1
            itemFound.yPosition = self.yPosition
        self.room.addItems([itemFound])

'''
'''
class Token(Item):
    type = "Token"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="token",creator=None):
        super().__init__(". ",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

'''
'''
class VatMaggot(Item):
    type = "VatMaggot"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="vat maggot",creator=None):
        super().__init__("~-",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    '''
    '''
    def apply(self,character,resultType=None):

        # remove ressources
        character.messages.append("you consume the vat maggot")
        character.satiation += 50
        if self.xPosition and self.yPosition:
            if self.room:
                self.room.removeItem(self)
            elif self.terrain:
                self.terrain.removeItem(self)
        else:
            character.inventory.remove(self)
        character.awardReputation(amount=5,reason="eating a vat magot")
        if (gamestate.tick%2 == 0):
            if (gamestate.tick%8 == 0):
                character.satiation -= 25
                character.fallUnconcious()
                character.revokeReputation(amount=15,reason="passing out from eating a vat magot")
            else:
                character.messages.append("you wretch")
                character.revokeReputation(amount=5,reason="wretching from eating a vat magot")

        super().apply(character,silent=True)

'''
'''
class Sheet(Item):
    type = "Sheet"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="sheet",creator=None):
        super().__init__("+#",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

'''
'''
class Rod(Item):
    type = "Rod"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="rod",creator=None):
        super().__init__("+|",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True


'''
'''
class Nook(Item):
    type = "Nook"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="nook",creator=None):
        super().__init__("+L",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True


'''
'''
class Stripe(Item):
    type = "Stripe"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="stripe",creator=None):
        super().__init__("+-",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True


'''
'''
class Bolt(Item):
    type = "Bolt"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="bolt",creator=None):
        super().__init__("+i",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

'''
'''
class Coil(Item):
    type = "Coil"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="coil",creator=None):
        super().__init__("+g",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

'''
'''
class Tank(Item):
    type = "Tank"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="tank",creator=None):
        super().__init__("#o",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

'''
'''
class Heater(Item):
    type = "Heater"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="heater",creator=None):
        super().__init__("#%",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True


'''
'''
class Connector(Item):
    type = "Connector"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="connector",creator=None):
        super().__init__("#H",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True


'''
'''
class Puller(Item):
    type = "puller"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="puller",creator=None):
        super().__init__("#>",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True


'''
'''
class Pusher(Item):
    type = "pusher"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="pusher",creator=None):
        super().__init__("#<",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

'''
'''
class Tree(Item):
    type = "Tree"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="tree",creator=None):
        super().__init__("&/",xPosition,yPosition,name=name,creator=creator)

        self.bolted = True
        self.walkable = False

    def apply(self,character):

        character.messages.append("you harvest a vat maggot")

        # spawn new item
        new = VatMaggot(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.terrain.addItems([new])

'''
'''
class BioMass(Item):
    type = "BioMass"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="bio mass",creator=None):
        super().__init__("~=",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

'''
'''
class PressCake(Item):
    type = "PressCake"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="press cake",creator=None):
        super().__init__("~#",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

'''
'''
class GameTestingProducer(Item):
    type = "GameTestingProducer"

    def __init__(self,xPosition=None,yPosition=None, name="testing producer",creator=None, seed=0, possibleSources=[], possibleResults=[]):
        self.coolDown = 20
        self.coolDownTimer = -self.coolDown

        super().__init__("/\\",xPosition,yPosition,name=name,creator=creator)

        self.seed = seed
        self.baseName = name
        self.possibleResults = possibleResults
        self.possibleSources = possibleSources
        self.change_apply_2(force=True)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])

    def apply(self,character,resultType=None):

        token = None
        for item in character.inventory:
            if isinstance(item,src.items.Token):
                token = item

        if gamestate.tick < self.coolDownTimer+self.coolDown:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = gamestate.tick

        if token:
            self.change_apply_1(character,token)
        else:
            self.produce_apply(character)

    def change_apply_1(self,character,token):
        options = [(("yes",character,token),"yes"),(("no",character,token),"no")]
        self.submenue = interaction.SelectionMenu("Do you want to reconfigure the machine?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.change_apply_2

    def change_apply_2(self,force=False):
        if not force:
            if self.submenue.selection[0] == "no":
                return
            character = self.submenue.selection[1]
            token = self.submenue.selection[2]
            character.inventory.remove(token)

        seed = self.seed

        self.ressource = None
        while not self.ressource:
            self.product = self.possibleResults[seed%23%len(self.possibleResults)]
            self.ressource = self.possibleSources[seed%len(self.possibleSources)]
            seed += 3+(seed%7)
            if self.product == self.ressource:
                self.ressource = None

        self.seed += self.seed%107
                    
        self.description = self.baseName + " | " + str(self.ressource.type) + " -> " + str(self.product.type) 

    def produce_apply(self,character):

        # gather the ressource
        itemFound = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,self.ressource):
                   itemFound = item
                   break
        
        # refuse production without ressources
        if not itemFound:
            character.messages.append("no "+self.ressource.type+" available")
            return

        # remove ressources
        self.room.removeItem(item)

        # spawn new item
        new = self.product(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.room.addItems([new])

        super().apply(character,silent=True)

'''
'''
class MachineMachine(Item):
    type = "MachineMachine"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="machine machine",creator=None):
        self.coolDown = 1000
        self.coolDownTimer = -self.coolDown

        self.endProducts = [
            "GrowthTank",
            "Hutch",
            "Lever",
            "Furnace",
            "CommLink",
            "Display",
            "Wall",
            "Pipe",
            "Coal",
            "Door",
            "Chain",
            "Winch",
            "Boiler",
            "Spray",
            "MarkerBean",
            "GooDispenser",
            "GooFlask",
            "ScrapCompactor",
            "ObjectDispenser",
            "Token",
            "Connector",
            "Bolt",
            "Stripe",
            "puller",
            "pusher",
            "Stripe",
            "Sheet",
            "Rod",
            "Heater",
            "Nook",
            "Tank",
            "Coil",
            "MaggotFermenter",
            "BioPress",
            "GooProducer",
            "Scraper",
            "Sorter",
            "Drill",
            "MemoryBank",
            "MemoryDump",
            "InfoScreen",
            "RoomBuilder",
        ]

        self.endProducts = {
        }

        super().__init__("M\\",xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","endProducts"])


    '''
    trigger production of a player selected item
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        options = []
        options.append(("blueprint","insert blueprint"))
        options.append(("produce","produce machine"))
        self.submenue = interaction.SelectionMenu("select the item to produce",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.basicSwitch
        self.character = character

    def basicSwitch(self):
        selection = self.character.macroState["submenue"].getSelection() 
        if selection == "blueprint":
            self.addBlueprint()
        elif selection == "produce":
            self.productionSwitch()

    def addBlueprint(self):
        blueprintFound = None
        for item in self.character.inventory:
            if isinstance(item,BluePrint):
                blueprintFound = item

        if not blueprintFound:
            self.character.messages.append("no blueprint found in inventory")
            return

        self.endProducts[blueprintFound.endProduct] = blueprintFound.endProduct
        self.character.messages.append("blueprint for "+blueprintFound.endProduct+" inserted")
        self.character.inventory.remove(blueprintFound)

    def productionSwitch(self):

        if self.endProducts == {}:
            self.character.messages.append("no blueprints available.")
            return

        if gamestate.tick < self.coolDownTimer+self.coolDown:
            self.character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return

        self.coolDownTimer = gamestate.tick

        options = []
        for itemType in self.endProducts:
            options.append((itemType,itemType+" machine"))
        self.submenue = interaction.SelectionMenu("select the item to produce",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.produceSelection

    '''
    trigger production of the selected item
    '''
    def produceSelection(self):
        self.produce(self.submenue.selection)

    '''
    produce an item
    '''
    def produce(self,itemType,resultType=None):
        # gather a metal bar
        metalBar = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,MetalBars):
                   metalBar = item
                   break
        
        # refuse production without ressources
        if not metalBar:
            messages.append("no metal bars available")
            return

        # remove ressources
        self.room.removeItem(item)

        # spawn new item
        new = Machine(creator=self)
        new.setToProduce(itemType)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.room.addItems([new])

    def getLongInfo(self):
        text = """
This machine produces machines that build machines. It needs blueprints to do that.

You can add blueprints by activating the machine while having a blueprint in your inventory.
After activation select "insert blueprint" and the blueprint will be added.

You can produce machines for blueprints that were added.
Prepare for production by placing metal bars to the west/left of this machine.
Activate the machine to start producing. You will be shown a list of things to produce.
Select the thing to produce and confirm.

After using this machine you need to wait %s ticks till you can use this machine again.
"""%(self.coolDown,)

        coolDownLeft = self.coolDown-(gamestate.tick-self.coolDownTimer)
        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

"""%(coolDownLeft,)
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if len(self.endProducts):
            text += """
This machine has blueprints for:

"""
            for itemType in self.endProducts:
                text += "* %s\n"%(itemType)
            text += "\n"
        else:
            text += """
This machine cannot produce anything since there were no blueprints added to the machine

"""
        return text

'''
'''
class Machine(Item):
    type = "Machine"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Machine",creator=None):
        self.toProduce = "Wall"

        self.coolDown = 100
        self.coolDownTimer = -self.coolDown

        super().__init__("X\\",xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "toProduce"])

        self.baseName = name

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])

        self.setDescription()

        self.initialState = self.getState()

    def setDescription(self):
        self.description = self.baseName+" MetalBar -> %s"%(self.toProduce,)

    def setToProduce(self,toProduce):
        self.toProduce = toProduce
        self.setDescription()

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if gamestate.tick < self.coolDownTimer+self.coolDown:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = gamestate.tick

        # gather a metal bar
        metalBar = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,MetalBars):
                   metalBar = item
                   break
        
        # refuse production without ressources
        if not metalBar:
            character.messages.append("no metal bars available")
            return

        # remove ressources
        self.room.removeItem(item)

        # spawn new item
        new = itemMap[self.toProduce](creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.room.addItems([new])

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()



'''
'''
class Drill(Item):
    type = "Drill"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Drill",creator=None):

        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.isBroken = False
        self.isCleaned = True

        self.baseName = name

        super().__init__("&|",xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
                "coolDown","coolDownTimer",
                "isBroken","isCleaned"])

        self.setDescription()

        self.initialState = self.getState()

    def setDescription(self):
        addition = ""
        if self.isBroken:
            addition = " (broken)"
        self.description = self.baseName+addition

    def setToProduce(self,toProduce):
        self.setDescription()

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if self.room:
            character.messages.append("this machine can not be used in rooms")
            return

        if self.isBroken:
            if not self.isCleaned:

                character.messages.append("you remove the broken rod")

                # spawn new item
                new = Scrap(self.xPosition,self.yPosition,3,creator=self)
                new.xPosition = self.xPosition
                new.yPosition = self.yPosition+1
                new.bolted = False
                self.terrain.addItems([new])

                self.isCleaned = True

            else:

                character.messages.append("you repair te machine")

                rod = None
                if (self.xPosition-1,self.yPosition) in self.terrain.itemByCoordinates:
                    for item in self.terrain.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                        if isinstance(item,Rod):
                           rod = item
                           break
                
                # refuse production without ressources
                if not rod:
                    character.messages.append("needs repairs Rod -> repaired")
                    character.messages.append("no rod available")
                    return

                # remove ressources
                self.terrain.removeItem(item)

                self.isBroken = False

            self.setDescription()
            return

        if gamestate.tick < self.coolDownTimer+self.coolDown:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = gamestate.tick


        # spawn new item
        new = Scrap(self.xPosition,self.yPosition,3,creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.terrain.addItems([new])

        self.isBroken = True
        self.isCleaned = False

        self.setDescription()

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

class MemoryDump(Item):
    type = "MemoryDump"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MemoryDump",creator=None):

        self.macros = None

        self.baseName = name

        super().__init__("mD",xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
                "macros"])

        self.setDescription()

        self.initialState = self.getState()

    def setDescription(self):
        addition = ""
        if self.macros:
            addition = " (imprinted)"
        self.description = self.baseName+addition

    def setToProduce(self,toProduce):
        self.setDescription()

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can not be used within rooms")
            return

        import copy
        if not self.macros == None:
            character.messages.append("you overwrite your macros with the ones in your memory dump")
            character.macroState["macros"] = copy.deepcopy(self.macros)
            self.macros = None
        else:
            character.messages.append("you dump your macros in the memory dump")
            self.macros = copy.deepcopy(character.macroState["macros"])

        self.setDescription()

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

'''
'''
class MemoryBank(Item):
    type = "MemoryBank"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MemoryBank",creator=None):

        self.macros = {}

        self.baseName = name

        super().__init__("mM",xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
                "macros"])

        self.setDescription()

        self.initialState = self.getState()

    def setDescription(self):
        addition = ""
        if self.macros:
            addition = " (imprinted)"
        self.description = self.baseName+addition

    def setToProduce(self,toProduce):
        self.setDescription()

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can not be used within rooms")
            return

        import copy
        if self.macros:
            character.messages.append("you overwrite your macros with the ones in your memory bank")
            character.macroState["macros"] = copy.deepcopy(self.macros)
        else:
            character.messages.append("you store your macros in the memory bank")
            self.macros = copy.deepcopy(character.macroState["macros"])

        self.setDescription()

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

'''
'''
class Engraver(Item):
    type = "Engraver"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Engraver",creator=None):
        super().__init__("eE",xPosition,yPosition,name=name,creator=creator)
        self.submenue = None
        self.text = None

    def apply(self,character):
        super().apply(character,silent=True)

        self.character = character

        if not self.text:
            character.messages.append("starting interaction")
            self.submenue = interaction.InputMenu("Set the text to engrave")
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.setText
        else:
            if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
                 self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)][0].customDescription = self.text

    '''
    trigger production of the selected item
    '''
    def setText(self):
        self.character.messages.append("stopping interaction")
        self.text = self.submenue.text
        self.submenue = None

'''
'''
class InfoScreen(Item):
    type = "InfoScreen"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="InfoScreen",creator=None):
        super().__init__("iD",xPosition,yPosition,name=name,creator=creator)
        self.submenue = None
        self.text = None

    def apply(self,character):
        if not self.room:
            character.messages.append("can only be used within rooms")
            return
        super().apply(character,silent=True)

        options = []

        options.append(("level1","basic information "+str(self.room.steamGeneration)))
        if self.room.steamGeneration > 0:
            options.append(("level2","l2 information"))
        else:
            options.append(("level2","disabled - NOT ENOUGH ENERGY"))
        if self.room.steamGeneration > 1:
            options.append(("level3","l3 information"))
        else:
            options.append(("level3","disabled - NOT ENOUGH ENERGY"))
        if self.room.steamGeneration > 2:
            options.append(("level3","l4 information"))
        else:
            options.append(("level4","disabled - NOT ENOUGH ENERGY"))

        self.submenue = interaction.SelectionMenu("select the information you need",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.step2

        self.character = character

    def step2(self):

        selection = self.submenue.getSelection()
        self.submenue = None

        if selection == "level1":
            self.basicInfo()
        elif selection == "level2" and self.room.steamGeneration > 0:
            self.l2Info()
        elif selection == "level3" and self.room.steamGeneration > 1:
            self.l3Info()
        elif selection == "level4" and self.room.steamGeneration > 2:
            self.l4Info()
        else:
            self.character.messages.append("NOT ENOUGH ENERGY")

    def basicInfo(self):

        options = []

        options.append(("level1_movement","movement"))
        options.append(("level1_interaction","interaction"))
        options.append(("level1_machines","machines"))

        self.submenue = interaction.SelectionMenu("select the information you need",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level1_selection

    def level1_selection(self):

        selection = self.submenue.getSelection()

        if selection == "level1_movement":
            self.submenue = interaction.TextMenu("\n\n * press ? for help\n\n * press a to move left/west\n * press w to move up/north\n * press s to move down/south\n * press d to move right/east\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_interaction":
            self.submenue = interaction.TextMenu("\n\n * press k to pick up\n * press l to pick up\n * press i to view inventory\n * press @ to view your stats\n * press j to activate \n * press e to examine\n * press ? for help\n\nMove onto an item and press the key to interact with it. Move against big items and press the key to interact with it\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines":
            options = []

            options.append(("level1_machines_bars","metal bar production"))
            options.append(("level1_machines_machines","machine production"))
            options.append(("level1_machines_food","food production"))
            options.append(("level1_machines_energy","energy production"))

            self.submenue = interaction.SelectionMenu("select the information you need",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stepLevel1Machines

    def stepLevel1Machines(self):

        selection = self.submenue.getSelection()

        if selection == "level1_machines_bars":
            self.submenue = interaction.TextMenu("\n\nMetal bars are used to produce most thing. You can produce metal bars by using a scrap compactor.\nA scrap compactor is represented by RC. Place the scrap to the right/east of the scrap compactor.\nActivate it to produce a metal bar. The metal bar will be outputted to the left/west of the scrap compactor.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_machines":
            self.submenue = interaction.TextMenu("\n\nAll items are produces in machines. There is a special machine to produce each item.\nThese machines are shown as X\\. Place metal bars to the west/left of the machine and activate it to produce the item.\n\nThe machines to produce items with are produced by a machine-machine. The machine machine is shown as M\\\nPlace a metal bar to the west/left of the machine-machine and activate it. Select what the machine should produce.\n\nMachine-machines are produced by the production artwork. The production artwork is represented by ßß.\nPlace metal bars to the right of the production artwork and activate it to produce a machine-machine.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_food":
            self.submenue = interaction.TextMenu("\n\nFood production is based on vat maggots. Vat maggots can be harvested from trees.\nActivate the tree and a vat maggot will be dropped to the east of the tree.\n\nvat maggots are processed into bio mass using a maggot fermenter.\nPlace 10 vat maggots left/west to the maggot fermenter and activate it to produce 1 bio mass.\n\nThe bio mass is processed into press cake using a bio press.\nPlace 10 biomass left/west to the bio press and activate it to produce one press cake.\n\nThe press cake is processed into goo by a goo producer. Place 10 press cakes west/left to the goo producer and a goo dispenser to the right/east of the goo producer.\nActivate the goo producer to add a charge to the goo dispenser.\n\nIf the goo dispenser is charged, you can fill your flask by having it in your inventory and activating the goo dispenser.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_energy":
            self.submenue = interaction.TextMenu("\n\nEnergy production is steam based. Steam is generated heating a boiler.\nA boiler is represented by OO or 00.\n\nA boiler is heated by placing a furnace next to it and fireing it. A furnace is fired by activating it while having coal in you inventory.\nA furnace is represented by oo or öö.\n\nCoal can be harvested from coal mines. Coal mines are represented by &c.\nActivate it and a piece of coal will be outputted to the right/east.\ncoal is represented by sc.\n\n")
            self.character.macroState["submenue"] = self.submenue

    def l2Info(self):

        options = []

        options.append(("level2_multiplier","action multipliers"))
        options.append(("level2_rooms","room creation"))

        self.submenue = interaction.SelectionMenu("select the information you need",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level2_selection

    def level2_selection(self):

        selection = self.submenue.getSelection()

        if selection == "level2_multiplier":
            self.submenue = interaction.TextMenu("\n\nyou can use multiplicators with commands. Typing a number followed by a command will result in the command to to be run multiple times\n\nTyping 10l is the same as typing llllllllll.\nThis will result in you dropping 10 items from your inventory\n\nThe multiplicator only applies to the following command.\nTyping 3aj will be expanded to aaaj.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level2_rooms":
            self.submenue = interaction.TextMenu("\n\nmany machines only work within rooms. You can build new rooms.\nRooms are rectangular and have one door.\n\nYou can build new rooms. Prepare by placing walls and a door in the form of a rectangle on the ground.\n\nPlace a room builder within the walls and activate it to create a room from the basic items.\n\n")
            self.character.macroState["submenue"] = self.submenue
        else:
            self.character.messages.append("unknown selection: "+selection)

    def l3Info(self):

        options = []

        options.append(("level3_macrosBasic","macro basics"))
        options.append(("level3_macrosExtra","macro extra"))
        options.append(("level3_macrosShortcuts","macro shortCuts"))

        self.submenue = interaction.SelectionMenu("select the information you need",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level3_selection

    def level3_selection(self):

        selection = self.submenue.getSelection()

        if selection == "level3_macrosBasic":
            self.submenue = interaction.TextMenu("\n\nyou can use macros to automate task. This means you can record and replay keystrokes.\n\nTo record a macro press - to start recording and press the key to record to.\nAfterwards do your movement and press - to stop recording.\nTo replay the recorded macro press _ and the key the macro was recorded to.\n\nFor example typing -kasdw- will record asdw to the buffer k\nPressing _k afterwards will be the same as pressing asdw\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level3_macrosExtra":
            self.submenue = interaction.TextMenu("\n\nMacros can be combined with each other. You can do this by replaying a macro while recording a macro\nFor example -qaaa- will record aaa to the buffer q.\nPressing -wddd_q- will record ddd_q to the buffer w. Pressing _w will be the same as dddaaa\nThe macro are referenced not copied. This means overwriting a macro will change alle macros referencing it. \n\nYou also can use multipliers within and with macros.\nPressing 5_q for example is the same as _q_q_q_q_q\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level3_macrosShortcuts":
            self.submenue = interaction.TextMenu("\n\nThere are some shortcuts that are usefull in combination with macros.\n\nctrl-d - aborts running the current macro\nctrl-p - pauses/unpauses running the current macro\nctrl-k writes macros fo disk\nctrl-o loads macros from disk\nctrl-x - saves and exits the game without interrupting running macros\n\n")
            self.character.macroState["submenue"] = self.submenue
        else:
            self.character.messages.append("unknown selection: "+selection)


    def l4Info(self):

        options = []

        options.append(("level4_npcCreation","npc creation"))
        options.append(("level4_npcControl","npc control"))
        options.append(("level4_npcCreation","npc creation"))

        self.submenue = interaction.SelectionMenu("select the information you need",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level4_selection

    def level4_selection(self):

        if selection == "level4_npcCreation":
            self.submenue = interaction.TextMenu("\n\nYou can spawn new npcs. Npcs work just like your main character\nNpcs are generated from growth tanks. You need to activate the growth tank with a full flask in your inventory\nActivate the filled growth tank to spwan the npc. \n\n")
            self.character.macroState["submenue"] = self.submenue
        else:
            self.character.messages.append("unknown selection: "+selection)

'''
'''
class BluePrinter(Item):
    type = "BluePrinter"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="BluePrinter",creator=None):
        super().__init__("sX",xPosition,yPosition,name=name,creator=creator)
        self.submenue = None
        self.text = None

        self.reciepes = [
                [["Stripe","Connector","Rod"],"MemoryBank"],
                [["Stripe","Connector","Coil"],"MemoryDump"],

                [["Sheet","pusher"],"Sorter"],
                [["Stripe","Connector"],"Display"],
                [["GooFlask","Tank"],"GrowthTank"],

                [["Scrap","MetalBars"],"Scraper"],
                [["Sheet","MetalBars"],"Tank"],
                [["Coil","MetalBars"],"Heater"],
                [["Nook","MetalBars"],"Connector"],
                [["Stripe","MetalBars"],"Pusher"],
                [["Bolt","MetalBars"],"Puller"],
                [["Rod","MetalBars"],"GooFlask"],

                [["Tank"],"GooFlask"],
                [["Heater"],"Boiler"],
                [["Connector"],"Door"],
                [["pusher"],"Drill"],
                [["puller"],"RoomBuilder"],

                [["Sheet"],"Sheet"],
                [["Coil"],"Coil"],
                [["Nook"],"Nook"],
                [["Stripe"],"Stripe"],
                [["Bolt"],"Bolt"],
                [["Rod"],"Rod"],

                [["Scrap"],"ScrapCompactor"],
                [["Coal"],"Furnace"],
                [["BluePrint"],"BluePrinter"],
                [["MetalBars"],"Wall"],

                [["GooFlask"],"GooDispenser"],
                [["VatMaggot"],"MaggotFermenter"],
                [["BioMass"],"BioPress"],
                [["PressCake"],"GooProducer"],
            ]

    def apply(self,character):
        super().apply(character,silent=True)

        inputThings = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            inputThings = self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]

        if not inputThings:
            character.messages.append("no items - place items to the left/west")
            return

        abstractedInputThings = {}
        for item in inputThings:
            abstractedInputThings[item.type] = {"item":item}

        reciepeFound = None
        for reciepe in self.reciepes:
            hasMaterials = True
            for requirement in reciepe[0]:
                if not requirement in abstractedInputThings:
                    hasMaterials = False

            if hasMaterials:
                reciepeFound = reciepe
                break

        if reciepeFound:
            # spawn new item
            new = BluePrint(creator=self)
            new.setToProduce(reciepeFound[1])
            new.xPosition = self.xPosition+1
            new.yPosition = self.yPosition
            new.bolted = False
            self.room.addItems([new])

            for itemType in reciepeFound[0]:
                self.room.removeItem(abstractedInputThings[itemType]["item"])
            character.messages.append("you create a blueprint for "+reciepe[1])
        else:
            character.messages.append("unable to produce blueprint from given items")
            return


'''
'''
class BluePrint(Item):
    type = "BluePrint"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="BluePrint",creator=None):
        super().__init__("bb",xPosition,yPosition,name=name,creator=creator)

        self.endProduct = None
        self.walkable = True
        self.baseName = name

        self.attributesToStore.extend([
                "endProduct"])

        self.setDescription()

        self.initialState = self.getState()

    def setDescription(self):
        if not self.endProduct:
            self.description = self.baseName
        else:
            self.description = self.baseName+" for %s"%(self.endProduct,)

    def setToProduce(self, toProduce):
        self.endProduct = toProduce

        self.setDescription()

    def apply(self,character):
        super().apply(character,silent=True)

        character.messages.append("a blueprint for "+self.endProduct)

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

'''
'''
class CoalMine(Item):
    type = "CoalMine"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="coal mine",creator=None):
        super().__init__("&c",xPosition,yPosition,name=name,creator=creator)

        self.bolted = True
        self.walkable = False

    def apply(self,character):

        character.messages.append("you mine a piece of coal")

        # spawn new item
        new = Coal(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.terrain.addItems([new])


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
            "ObjectDispenser":OjectDispenser,
            "Token":Token,
            "Connector":Connector,
            "Bolt":Bolt,
            "Stripe":Stripe,
            "puller":Puller,
            "pusher":Pusher,
            "Stripe":Stripe,
            "Sheet":Sheet,
            "Rod":Rod,
            "Heater":Heater,
            "Nook":Nook,
            "Tank":Tank,
            "Coil":Coil,
            "Tree":Tree,
            "MaggotFermenter":MaggotFermenter,
            "BioPress":BioPress,
            "PressCake":PressCake,
            "BioMass":BioMass,
            "VatMaggot":VatMaggot,
            "GooProducer":GooProducer,
            "Machine":Machine,
            "MachineMachine":MachineMachine,
            "Scraper":Scraper,
            "Sorter":Sorter,
            "Drill":Drill,
            "MemoryBank":MemoryBank,
            "MemoryDump":MemoryDump,
            "Engraver":Engraver,
            "InfoScreen":InfoScreen,
            "CoalMine":CoalMine,
            "RoomBuilder":RoomBuilder,
            "BluePrinter":BluePrinter,
            "BluePrint":BluePrint,
}

producables = {
            "Wall":Wall,
            "Door":Door,
            "GrowthTank":GrowthTank,
            "ScrapCompactor":ScrapCompactor,
            "Scraper":Scraper,
            "Drill":Drill,
            "Hutch":Hutch,
            "Lever":Lever,
            "Furnace":Furnace,
            "CommLink":Commlink,
            "Display":Display,
            "Pipe":Pipe,
            "Chain":Chain,
            "Winch":Winch,
            "Boiler":Boiler,
            "Spray":Spray,
            "MarkerBean":MarkerBean,
            "ObjectDispenser":OjectDispenser,
            "Token":Token,
            "Connector":Connector,
            "Bolt":Bolt,
            "Stripe":Stripe,
            "puller":Puller,
            "pusher":Pusher,
            "Stripe":Stripe,
            "Sheet":Sheet,
            "Rod":Rod,
            "Heater":Heater,
            "Nook":Nook,
            "Tank":Tank,
            "Coil":Coil,
            "MaggotFermenter":MaggotFermenter,
            "BioPress":BioPress,
            "GooProducer":GooProducer,
            "GooDispenser":GooDispenser,
            "GooFlask":GooFlask,
            "Sorter":Sorter,
            "MemoryBank":MemoryBank,
            "MemoryDump":MemoryDump,
            
        }

'''
get item instances from dict state
'''
def getItemFromState(state):
    item = itemMap[state["type"]](creator=void)
    item.setState(state)
    loadingRegistry.register(item)
    return item

