####################################################################################
###
##     items and item related code belongs here 
#
####################################################################################

# load basic libs
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
urwid = None

'''
the base class for all items.
'''
class Item(src.saveing.Saveable):
    '''
    state initialization and id generation
    '''
    def __init__(self,display=None,xPosition=0,yPosition=0,creator=None,name="item",seed=0,noId=False):
        super().__init__()

        self.seed = seed

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
        self.container = None

        self.customDescription = None

        # set up metadata for saving
        self.attributesToStore.extend([
               "mayContainMice","name","type","walkable","xPosition","yPosition","bolted"])

        # set id
        if not noId:
            self.id = {
                       "other":"item",
                       "xPosition":xPosition,
                       "yPosition":yPosition,
                       "counter":creator.getCreationCounter()
                      }
            self.id["creator"] = creator.id
        else:
            self.id = None
        self.id = json.dumps(self.id, sort_keys=True).replace("\\","")

        # store state and register self
        self.initialState = self.getState()
        loadingRegistry.register(self)

    def upgrade(self):
        self.level += 1

    def downgrade(self):
        self.level += 1

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
            character.messages.append("i can not do anything useful with this")

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

        character.messages.append("you pick up a %s"%(self.type))
        """
        foundBig = False
        for item in character.inventory:
            if item.walkable == False:
                foundBig = True
                break

        if foundBig and self.walkable == False:
            character.messages.append("you cannot carry more big items")
            return

        character.messages.append("you pick up a "+self.type)
        """

        # bad code: should be a simple self.container.removeItem(self)
        if self.room:
            # remove item from room
            self.container = self.room
            self.container.removeItem(self)
        else:
            # remove item from terrain
            # bad code: should be handled by the terrain
            self.container = self.terrain
            self.container.removeItem(self)

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
            if self in self.terrain.itemByCoordinates[oldPosition]:
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
    def destroy(self,generateSrcap=True):

        if not hasattr(self,"terrain"):
            self.terrain = None
        if self.room:
            container = self.room
        elif self.terrain:
            container = self.terrain
        else:
            return

        pos = (self.xPosition,self.yPosition) 

        if pos == (None,None):
            return

        # remove item from terrain
        container.removeItem(self)

        # generatate scrap
        if generateSrcap:
            newItem = Scrap(pos[0],pos[1],1,creator=self)
            newItem.room = self.room
            newItem.terrain = self.terrain

            if pos in container.itemByCoordinates:
                for item in container.itemByCoordinates[pos]:
                    container.removeItem(item)
                    if not item.type == "Scrap":
                        newItem.amount += 1
                    else:
                        newItem.amount += item.amount
            newItem.setWalkable()

            # place scrap
            container.addItems([newItem])

        self.xPosition = None
        self.yPosition = None
            
    def getState(self):
        state = super().getState()
        state["id"] = self.id
        state["type"] = self.type
        state["xPosition"] = self.xPosition
        state["yPosition"] = self.yPosition
        return state

    def getDiffState(self):
        state = super().getDiffState()
        state["id"] = self.id
        state["type"] = self.type
        state["xPosition"] = self.xPosition
        state["yPosition"] = self.yPosition
        return state

    def getLongInfo(self):
        return None

'''
crushed something, basically raw metal
'''
class Scrap(Item):
    type = "Scrap"
        
    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="scrap",creator=None,noId=False):

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
    recalculate the walkable attribute
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
    def destroy(self, generateSrcap=True):
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
                self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].remove(item)

    def getLongInfo(self):
        text = """
item: Scrap

description:
Scrap is a raw material. Its main use is to be converted to metal bars in a scrap compactor.

There is %s in this pile
"""%(self.amount,)

        return text

    '''
    get picked up by the supplied character
    '''
    def pickUp(self,character):
        if self.amount <= 1:
            super().pickUp(character)
            return

        if self.xPosition == None or self.yPosition == None:
            return

        foundBig = False
        for item in character.inventory:
            if item.walkable == False:
                foundBig = True
                break
        self.amount -= 1

        character.messages.append("you pick up a piece of scrap, there is %s left"%(self.amount,))

        self.setWalkable()

        # add item to characters inventory
        character.inventory.append(Scrap(amount=1,creator=self))
        self.changed()

    '''
    get picked up by the supplied character
    '''
    def apply(self,character):
        scrapFound = []
        for item in character.inventory:
            if item.type == "Scrap":
                scrapFound.append(item)
                break

        for item in scrapFound:
            if self.amount < 20:
                self.amount += item.amount
                character.messages.append("you add a piece of scrap there pile contains %s scrap now."%(self.amount,))
                character.inventory.remove(item)

        self.setWalkable()

        self.changed()

    def setState(self,state):
        super().setState(state)

        self.setWalkable()

'''
dummy class for a corpse
'''
class Corpse(Item):
    type = "Corpse"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="corpse",creator=None,noId=False):
        super().__init__(displayChars.corpse,xPosition,yPosition,name=name,creator=creator)
        self.charges = 1000
        self.attributesToStore.extend([
               "activated","charges"])
        self.walkable = True
        self.bolted = False

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    def getLongInfo(self):
        text = """
item: Corpse

description:
A corpse. Activate it to eat from it. Eating from a Corpse will gain you 15 Satiation.

The corpse has %s charges left.

"""%(self.charges)
        return text

    def apply(self,character):
        if isinstance(character,src.characters.Monster):
            if character.phase == 1:
                if character.satiation < 1000:
                    character.macroState["commandKeyQueue"] = [("j",[])] + character.macroState["commandKeyQueue"]
            if character.phase == 3:
                character.enterPhase4()
        if self.charges:
            character.satiation += 15
            if character.satiation > 1000:
                character.satiation = 1000
            self.charges -= 1
            character.messages.append("you eat from the corpse and gain 15 satiation")
        else:
            self.destroy(generateSrcap=False)

class ItemUpgrader(Item):
    type = "ItemUpgrader"

    def __init__(self,xPosition=0,yPosition=0,name="item upgrader",creator=None,noId=False):
        super().__init__(displayChars.itemUpgrader,xPosition,yPosition,name=name,creator=creator)
        self.charges = 3
        self.level = 1

        self.attributesToStore.extend([
               "charges","level"])

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    def apply(self,character):
        if not self.room:
            character.messages.append("this machine can only be used within rooms")

        inputItem = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            inputItem = self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)][0]

        if not inputItem:
            character.messages.append("place item to upgrade on the left")
            return

        if not hasattr(inputItem,"level"):
            character.messages.append("cannot upgrade %s"%(inputItem.type))
            return

        if inputItem.level > self.level:
            character.messages.append("item upgrader needs to be upgraded to upgrade this item further")
            return

        if inputItem.level == 1:
            chance = -1
        elif inputItem.level == 2:
            chance = 0
        elif inputItem.level == 3:
            chance = 1
        elif inputItem.level == 4:
            chance = 2
        else:
            chance = 100

        success = False
        if gamestate.tick % (self.charges+1) > chance:
            success = True

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if inputItem.walkable:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 1:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        self.room.removeItem(inputItem)

        if success:
            inputItem.upgrade()
            character.messages.append("%s upgraded"%(inputItem.type,))
            self.charges = 0
            inputItem.xPosition = self.xPosition+1
            inputItem.yPosition = self.yPosition
            self.room.addItems([inputItem])
        else:
            self.charges += 1
            character.messages.append("failed to upgrade %s - has %s charges now"%(inputItem.type,self.charges))
            inputItem.xPosition = self.xPosition
            inputItem.yPosition = self.yPosition+1
            self.room.addItems([inputItem])
            inputItem.destroy()

    def getLongInfo(self):
        text = """
item: ItemUpgrader

description:
An upgrader works from time to time. A failed upgrade will destroy the item but increase the chances of success
Place item to upgrade to the west and the upgraded item will be placed to the east.
If the upgrade fails the remains of the item will be placed to the south.

it has %s charges.

"""%(self.charges)
        return text

class ItemDowngrader(Item):
    type = "ItemDowngrader"

    def __init__(self,xPosition=0,yPosition=0,name="item downgrader",creator=None,noId=False):
        super().__init__(xPosition,yPosition,name=name,creator=creator)

    def apply(self,character):
        if not self.room:
            character.messages.append("this machine can only be used within rooms")

        inputItem = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            inputItem = self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)][0]

        if not inputItem:
            character.messages.append("place item to downgrade on the left")
            return

        if not hasattr(inputItem,"level"):
            character.messages.append("cannot downgrade %s"%(inputItem.type))
            return

        if inputItem.level == 1:
            character.messages.append("cannot downgrade item further")
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if inputItem.walkable:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 1:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        self.room.removeItem(inputItem)

        inputItem.level -= 1
        character.messages.append("%s downgraded"%(inputItem.type,))
        inputItem.xPosition = self.xPosition+1
        inputItem.yPosition = self.yPosition
        self.room.addItems([inputItem])

    def getLongInfo(self):
        text = """
item: ItemDowngrader

description:

the item downgrader downgrades items

Place item to upgrade to the west and the downgraded item will be placed to the east.

"""
        return text

'''
an character spawning item
'''
class GrowthTank(Item):
    type = "GrowthTank"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="growth tank",filled=False,creator=None,noId=False):
        self.filled = filled
        if filled:
            super().__init__(displayChars.growthTank_filled,xPosition,yPosition,name=name,creator=creator)
        else:
            super().__init__(displayChars.growthTank_unfilled,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "filled",])

        # bad code: repetetive and easy to forget
        self.initialState = self.getState()

    '''
    manually eject character
    '''
    def apply(self,character):

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

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
        #character.fallUnconcious()
        #character.hasFloorPermit = False
        self.room.addCharacter(character,self.xPosition+1,self.yPosition)
        #character.revokeReputation(amount=4,reason="beeing helpless")
        #character.macroState["commandKeyQueue"] = [("j",[])]
        character.macroState["macros"]["j"] = "J"

        return character

    def getLongInfo(self):
        text = """
item: GrowthTank

description:
A growth tank produces NPCs. 

Fill a growth tank to prepare it for generating an npc.
You can fill it by activating it with a full goo flask in your inventory.

Activate a filled growth tank to spawn a new npc.
Wake the NPC by taking to the NPC.

You talk to NPCs by pressing h and selecting the NPC to talk to.

"""
        return text

'''
basically a bed with a activatable cover
'''
class Hutch(Item):
    type = "Hutch"

    def __init__(self,xPosition=0,yPosition=0,name="Hutch",activated=False,creator=None,noId=False):
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

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

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

    def getLongInfo(self):
        text = """
item: Hutch

description:
A hutch. It is not useful.

"""
        return text

'''
item for letting characters trigger something
'''
class Lever(Item):
    type = "Lever"

    '''
    straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="lever",activated=False,creator=None,noId=False):
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

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

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

    def getLongInfo(self):
        text = """
item: Lever

description:
A lever. It is not useful.

"""
        return text

'''
heat source for generating steam and similar
'''
class Furnace(Item):
    type = "Furnace"

    '''
    straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Furnace",creator=None,noId=False):
        self.activated = False
        self.boilers = []
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
            character.messages.append("this machine can only be used within rooms")
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

    def getLongInfo(self):
        text = """
item: Furnace

description:
A furnace is used to generate heat. Heat is used to produce steam in boilers.

You can fire the furnace by activating it with coal in your inventory.

Place the furnace next to a boiler to be able to heat up the boiler with this furnace.

"""
        return text

    def getLongInfo(self):
        return str(self.id)

'''
a dummy for an interface with the mech communication network
bad code: this class is dummy only and basically is to be implemented
'''
class Commlink(Item):
    type = "CommLink"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Commlink",creator=None,noId=False):
        super().__init__(displayChars.commLink,xPosition,yPosition,name=name,creator=creator)

    '''
    fake requesting and getting a coal refill
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return
        
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

    def getLongInfo(self):
        text = """
item: CommLink

description:
A comlink. It is useless.

"""

'''
should be a display, but is abused as vehicle control
bad code: use an actual vehicle control
'''
class RoomControls(Item):
    type = "RoomControls"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="RoomControls",creator=None,noId=False):
        super().__init__(displayChars.display,xPosition,yPosition,name=name,creator=creator)

    '''
    map player controls to room movement 
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages("this machine can only be used within rooms")
            return

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

    def getLongInfo(self):
        text = """
item: RoomControls

description:
Room controls. Can be used to control vehicles.

Use it to take control over the vehice.

While controlling the vehicle your movement keys will be overriden. 
The movement key will move the room instead of yourself.
For example pressing w will not move you to the north, but will move the room to the north.
You need enough steam generation to move

To stop using the room controls press j again.

"""
        return text

'''
'''
class RoomBuilder(Item):
    type = "RoomBuilder"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="RoomBuilder",creator=None,noId=False):
        super().__init__(displayChars.roomBuilder,xPosition,yPosition,name=name,creator=creator)

    '''
    map player controls to room movement 
    '''
    def apply(self,character):
        if self.room:
            character.messages.append("this machine can not be used within rooms")
            return
        
        super().apply(character,silent=True)

        self.character = character

    def apply(self,character):
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
            return

        roomLeft = self.xPosition-wallLeft.xPosition
        roomRight = wallRight.xPosition-self.xPosition
        roomTop = self.yPosition-wallTop.yPosition
        roomBottom = wallBottom.yPosition-self.yPosition

        if roomLeft+roomRight+1 > 15:
            character.messages.append("room to big")
            return
        if roomTop+roomBottom+1 > 15:
            character.messages.append("room to big")
            return

        wallMissing = False
        items = []
        specialItems = []
        for x in range(-roomLeft,roomRight+1):
            pos = (self.xPosition+x,self.yPosition-roomTop)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
                                specialItems.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for y in range(-roomTop,roomBottom+1):
            pos = (self.xPosition-roomLeft,self.yPosition+y)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
                                specialItems.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for y in range(-roomTop,roomBottom+1):
            pos = (self.xPosition+roomRight,self.yPosition+y)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
                                specialItems.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for x in range(-roomLeft,roomRight+1):
            pos = (self.xPosition+x,self.yPosition+roomBottom)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
                                specialItems.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break

        if wallMissing:
            character.messages.append("wall missing")
            return

        for item in specialItems:
            for compareItem in specialItems:
                if item == compareItem:
                    continue
                if abs(item.xPosition-compareItem.xPosition) > 1 or (abs(item.xPosition-compareItem.xPosition) == 1 and abs(item.yPosition-compareItem.yPosition) > 0):
                    continue
                if abs(item.yPosition-compareItem.yPosition) > 1 or (abs(item.yPosition-compareItem.yPosition) == 1 and abs(item.xPosition-compareItem.xPosition) > 0):
                    continue
                character.messages.append("special items to near to each other")
                return

        import src.rooms
        oldTerrain = self.terrain
        for item in items:
            if item == self:
                continue

            oldX = item.xPosition
            oldY = item.yPosition
            item.xPosition = roomLeft+item.xPosition-self.xPosition
            item.yPosition = roomTop+item.yPosition-self.yPosition
            if (item.xPosition < 0 ):
                character.messages.append((oldX,oldY))
                character.messages.append((roomLeft,roomTop))
                character.messages.append((self.xPosition,self.yPosition))
                character.messages.append((item.yPosition,item.xPosition))
        room = src.rooms.EmptyRoom(self.xPosition//15,self.yPosition//15,self.xPosition%15-roomLeft,self.yPosition%15-roomTop,creator=self)
        room.reconfigure(roomLeft+roomRight+1,roomTop+roomBottom+1,items)

        
        xOffset = character.xPosition-self.xPosition
        yOffset = character.yPosition-self.yPosition

        oldTerrain.removeCharacter(character)
        oldTerrain.addRooms([room])
        character.xPosition = roomLeft+xOffset
        character.yPosition = roomTop+yOffset
        room.addCharacter(character,roomLeft+xOffset,roomTop+yOffset)

        self.terrain.removeItem(self)

        self.xPosition = roomLeft
        self.yPosition = roomTop
        self.room = None
        self.terrain = None
        room.addItems([self])

    def getLongInfo(self):
        text = """
item: RoomBuilder

description:
The roombuilder creates rooms from basic items.

Place Walls and and Doors around the room builder and activate the room builder to create a room.

The room has to be a rectangle.

"""
        return text

'''
basic item with different appearance
'''
class Wall(Item):
    type = "Wall"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Wall",creator=None,noId=False):
        super().__init__(displayChars.wall,xPosition,yPosition,name=name,creator=creator)

    def getLongInfo(self):
        text = """
item: Wall

description:
A Wall. Used to build rooms.

"""
        return text

'''
basic item with different appearance
'''
class Pipe(Item):
    type = "Pipe"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Pipe",creator=None,noId=False):
        super().__init__(displayChars.pipe,xPosition,yPosition,name=name,creator=creator)

    def getLongInfo(self):
        text = """
item: Pipe

description:
A Pipe. It is useless

"""
        return text

'''
basic item with different appearance
'''
class Coal(Item):
    type = "Coal"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Coal",creator=None,noId=False):
        self.canBurn = True
        super().__init__(displayChars.coal,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    def getLongInfo(self):
        text = """
item: Coal

description:
Coal is used as an energy source. It can be used to fire furnaces.

"""
        return text

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

    def apply(self,character):
        if isinstance(character,src.characters.Monster) and character.phase == 1 and ((gamestate.tick+self.xPosition)%10 == 5):
            newChar = characters.Exploder(creator=self)
            import copy
            newChar.macroState = copy.deepcopy(character.macroState)
            newChar.satiation = character.satiation
            newChar.explode = False
            
            character.solvers = [
                      "NaiveActivateQuest",
                      "ActivateQuestMeta",
                      "NaivePickupQuest",
                      "NaiveMurderQuest",
                    ]

            self.container.addCharacter(newChar,self.xPosition,self.yPosition)
            character.die()
            self.destroy(generateSrcap=False)
        else:
            super().apply(character)


'''
a door for opening/closing and locking people in/out
# bad code: should use a rendering method
'''
class Door(Item):
    type = "Door"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Door",creator=None,noId=False):
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

    def getLongInfo(self):
        text = """
item: Door

description:
A Door. Used to enter and leave rooms.

"""
        return text

'''
a pile of stuff to take things from
this doesn't hold objects but spawns them
'''
class Pile(Item):
    type = "Pile"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal,creator=None,noId=False):
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

    def getLongInfo(self):
        text = """
item: Pile

description:
A Pile. Use it to take coal from it

"""
        return text

'''
basic item with different appearance
'''
class Acid(Item):
    type = "Acid"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="pile",itemType=Coal,creator=None,noId=False):
        self.canBurn = True
        self.type = itemType
        self.type = "Acid"
        super().__init__(displayChars.acid,xPosition,yPosition,name=name,creator=creator)

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()

    def getLongInfo(self):
        text = """
item: Acid

description:
It is completely useless

"""
        return text

'''
used to connect rooms and items to drag them around
'''
class Chain(Item):
    type = "Chain"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="chain",creator=None,noId=False):
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
            
    def getLongInfo(self):
        text = """
item: Chain

description:
can be used to chain rooms together. Place it next to one or more rooms and activate it to chain rooms together.

"""
        return text

'''
basic item with different appearance
'''
class Winch(Item):
    type = "Winch"

    '''
    call superclass constructor with modified paramters 
    '''
    def __init__(self,xPosition=0,yPosition=0,name="winch",creator=None,noId=False):
        super().__init__(displayChars.winch_inactive,xPosition,yPosition,name=name,creator=creator)

    def getLongInfo(self):
        text = """
item: Winch

description:
A Winch. It is useless.

"""
        return text

'''
basic item with different appearance
'''
class MetalBars(Item):
    type = "MetalBars"

    def __init__(self,xPosition=0,yPosition=0,name="metal bar",creator=None,noId=False):
        super().__init__(displayChars.metalBars,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False

    def getLongInfo(self):
        text = """
item: MetalBars

description:
A metal bar is a raw ressource. It is used by most machines and produced by a scrap compactor.

"""
        return text

'''
produces steam from heat
bad code: sets the rooms steam generation directly without using pipes
'''
class Boiler(Item):
    type = "Boiler"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="boiler",creator=None,noId=False):
        super().__init__(displayChars.boiler_inactive,xPosition,yPosition,name=name,creator=creator)
        self.isBoiling = False
        self.isHeated = False
        self.startBoilingEvent = None
        self.stopBoilingEvent = None

        # set metadata for saving
        self.attributesToStore.extend([
               "isBoiling","isHeated"])

        self.objectsToStore.append("startBoilingEvent")
        self.objectsToStore.append("stopBoilingEvent")

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
            # shedule the event
            event = src.events.StartBoilingEvent(self.room.timeIndex+5,creator=self)
            event.boiler = self
            self.room.addEvent(event)

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

            event = src.events.StopBoilingEvent(self.room.timeIndex+5,creator=self)
            event.boiler = self
            self.room.addEvent(event)

        # notify listeners
        self.changed()

    def getLongInfo(self):
        text = """
a boiler can be heated by a furnace to produce steam. Steam is the basis for energy generation.

"""+self.id
        return text
            
    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        if self.isBoiling:
            self.display = displayChars.boiler_active

'''
steam sprayer used as a prop in the vat
'''
class Spray(Item):
    type = "Spray"

    '''
    call superclass constructor with modified parameters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="spray",direction=None,creator=None,noId=False):
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

    def getLongInfo(self):
        text = """
item: Boiler

description:
a boiler can be heated by a furnace to produce steam. Steam is the basis for energy generation.

"""
        return text
            
'''
marker ment to be placed by characters and to control actions with
'''
class MarkerBean(Item):
    type = "MarkerBean"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="bean",creator=None,noId=False):
        self.activated = False
        super().__init__(displayChars.markerBean_inactive,xPosition,yPosition,name=name,creator=creator)
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
            return displayChars.markerBean_active
        else:
            return displayChars.markerBean_inactive

    '''
    activate marker
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        character.messages.append(character.name+" activates a marker bean")
        self.activated = True

    def getLongInfo(self):
        text = """
item: MarkerBean

description:
A marker been. It can be used to mark things.

"""
        return text

'''
machine for filling up goo flasks
'''
class GooDispenser(Item):
    type = "GooDispenser"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo dispenser",creator=None,noId=False):
        self.activated = False
        self.baseName = name
        self.level = 1
        super().__init__(displayChars.gooDispenser,xPosition,yPosition,name=name,creator=creator)

        # set up meta information for saveing
        self.attributesToStore.extend([
               "activated","charges"])

        self.charges = 0
        self.maxCharges = 100

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

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        if not self.charges:
            character.messages.append("the dispenser has no charges")
            return

        filled = False
        fillAmount = 100+((self.level-1)*10)
        for item in character.inventory:
            if isinstance(item,GooFlask) and not item.uses >= fillAmount:
                item.uses = fillAmount
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

    def getLongInfo(self):
        text = """
item: GooDispenser

description:
A goo dispenser can fill goo flasks.

Activate it with a goo flask in you inventory.
The goo flask will be filled by the goo dispenser.

Filling a flask will use up a charge from your goo dispenser.

This goo dispenser currently has %s charges

"""%(self.charges)
        return text

'''
'''
class BloomShredder(Item):
    type = "BloomShredder"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="bloom shredder",creator=None,noId=False):
        self.activated = False
        super().__init__(displayChars.bloomShredder,xPosition,yPosition,name=name,creator=creator)

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()
    
    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,Bloom):
                    items.append(item)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        # refuse to produce without ressources
        if len(items) < 1:
            character.messages.append("not enough blooms")
            return
       
        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        # remove ressources
        self.room.removeItem(items[0])

        # spawn the new item
        new = BioMass(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: BloomShredder

description:
A bloom shredder produces bio mass from blooms.

Place bloom to the left/west of the bloom shredder.
Activate the bloom shredder to produce biomass.

"""
        return text

'''
'''
class CorpseShredder(Item):
    type = "CorpseShredder"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="corpse shredder",creator=None,noId=False):
        self.activated = False
        super().__init__(displayChars.corpseShredder,xPosition,yPosition,name=name,creator=creator)

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()
    
    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        corpse = None
        moldSpores = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,Corpse):
                    corpse = item
                if isinstance(item,MoldSpore):
                    moldSpores.append(item)

        # refuse to produce without ressources
        if not corpse:
            character.messages.append("no corpse")
            return
       
        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        # remove ressources
        self.room.removeItem(corpse)

        for i in range(0,10):
            if moldSpores:
                self.room.removeItem(moldSpores.pop())
                new = SeededMoldFeed(creator=self)
            else:
                # spawn the new item
                new = MoldFeed(creator=self)
            new.xPosition = self.xPosition+1
            new.yPosition = self.yPosition
            self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: CorpseShredder

description:
A corpse shredder produces mold feed from corpses.
If corpses and MoldSpores are supplied it produces seeded mold feed

Place corpse/mold seed to the west of the bloom shredder.
Activate the corpse shredder to produce mold feed/seeded mold feed.

"""
        return text

'''
'''
class SporeExtractor(Item):
    type = "SporeExtractor"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="spore extractor",creator=None,noId=False):
        self.activated = False
        super().__init__(displayChars.sporeExtractor,xPosition,yPosition,name=name,creator=creator)

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()
    
    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        items = []
        if (self.xPosition-1,self.yPosition) in self.container.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,Bloom):
                    items.append(item)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        # refuse to produce without ressources
        if len(items) < 1:
            character.messages.append("not enough blooms")
            return
       
        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        # remove ressources
        self.room.removeItem(items[0])

        # spawn the new item
        for i in range(1,5):
            new = MoldSpore(creator=self)
            new.xPosition = self.xPosition+1
            new.yPosition = self.yPosition
            self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: SporeExtractor

description:
A Spore Extractor removes spores from mold blooms.

Place mold bloom to the west/left and activate the Spore Extractor.
The MoldSpores will be outputted to the east/right.

"""
        return text


'''
'''
class MaggotFermenter(Item):
    type = "MaggotFermenter"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="maggot fermenter",creator=None,noId=False):
        self.activated = False
        super().__init__(displayChars.maggotFermenter,xPosition,yPosition,name=name,creator=creator)

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

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        # refuse to produce without ressources
        if len(items) < 10:
            character.messages.append("not enough maggots")
            return
       
        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
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

    def getLongInfo(self):
        text = """
item: MaggotFermenter

description:
A maggot fermenter produces bio mass from vat maggots.

Place 10 vat maggots to the left/west of the maggot fermenter.
Activate the maggot fermenter to produce biomass.

"""
        return text

'''
'''
class GooProducer(Item):
    type = "GooProducer"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo producer",creator=None,noId=False):
        self.activated = False
        self.level = 1
        super().__init__(displayChars.gooProducer,xPosition,yPosition,name=name,creator=creator)

        # bad code: repetetive and easy to forgett
        self.attributesToStore.extend([
               "level"])
        self.initialState = self.getState()
    
    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        # fetch input items
        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,PressCake):
                    items.append(item)

        # refuse to produce without ressources
        if len(items) < 10+(self.level-1):
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

        if dispenser.level > self.level:
            character.messages.append("the goo producer has to have higher or equal the level as the goo dispenser")
            return 

        if dispenser.charges >= dispenser.maxCharges:
            character.messages.append("the goo dispenser is full")
            return 

        # remove ressources
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.room.removeItem(item)

        dispenser.addCharge()

    def getLongInfo(self):
        text = """
item: GooProducer

description:
A goo producer produces goo from press cakes.

Place 10 press cakes to the left/west of the goo producer and a goo dispenser to the rigth/east.
Activate the maggot fermenter to add a charge to the goo dispenser.

"""
        return text

'''
'''
class BioPress(Item):
    type = "BioPress"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="bio press",creator=None,noId=False):
        self.activated = False
        super().__init__(displayChars.bioPress,xPosition,yPosition,name=name,creator=creator)

        # bad code: repetetive and easy to forgett
        self.initialState = self.getState()
    
    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

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

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
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

    def getLongInfo(self):
        text = """
item: BioPress

description:
A bio press produces press cake from bio mass.

Place 10 bio mass to the left/west of the bio press.
Activate the bio press to produce biomass.

"""
        return text


'''
flask with food to carry around and drink from
'''
class GooFlask(Item):
    type = "GooFlask"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo flask",creator=None,noId=False):
        self.uses = 0
        super().__init__(displayChars.gooflask_empty,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False
        self.description = "a flask containing goo"
        self.level = 1
        self.maxUses = 100

        # set up meta information for saveing
        self.attributesToStore.extend([
               "uses","level","maxUses"])

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
        displayByUses = [displayChars.gooflask_empty, displayChars.gooflask_part1, displayChars.gooflask_part2, displayChars.gooflask_part3, displayChars.gooflask_part4, displayChars.gooflask_full]
        return displayByUses[self.uses//20]

    '''
    get info including the charges on the flask
    '''
    def getDetailedInfo(self):
        return super().getDetailedInfo()+" ("+str(self.uses)+" charges)"

    def getLongInfo(self):
        text = """
item: GooFlask

description:
A goo flask holds goo. Goo is nourishment for you.

If you do not drink from the flask every 1000 ticks you will starve.

A goo flask can be refilled at a goo dispenser and can hold a maximum of %s charges.

this is a level %s item.

"""%(self.maxUses,self.level)
        return text

    def upgrade(self):
        super().upgrade()

        self.maxUses += 10

    def downgrade(self):
        super().downgrade()

        self.maxUses -= 10

'''
a vending machine basically
bad code: currently only dispenses goo flasks
'''
class OjectDispenser(Item):
    type = "ObjectDispenser"

    '''
    '''
    def __init__(self,xPosition=None,yPosition=None, name="object dispenser",creator=None,noId=False):
        super().__init__(displayChars.objectDispenser,xPosition,yPosition,name=name,creator=creator)

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

    def getLongInfo(self):
        text = """
item: ObjectDispenser

description:
A object dispenser holds and returns objects.

You can use it to retrieve an object from the object dispenser.

"""
        return text


'''
token object ment to produce anything from metal bars
bad pattern: serves as dummy for actual production lines
'''
class ProductionArtwork(Item):
    type = "ProductionArtwork"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="production artwork",creator=None,noId=False):
        self.coolDown = 10000
        self.coolDownTimer = -self.coolDown
        self.charges = 10

        super().__init__(displayChars.productionArtwork,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","charges"])

    '''
    trigger production of a player selected item
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        # gather a metal bar
        metalBar = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,MetalBars):
                   metalBar = item
                   break
        if not metalBar:
            character.messages.append("no metal bars on the left/west")
            return
        
        if gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return

        self.character = character

        excludeList = ("ProductionArtwork","Machine","Tree","Scrap","xCorpse","Acid","Item","Pile","InfoScreen","CoalMine","BluePrint","GlobalMacroStorage","Note","Command",
                       "Hutch","Lever","CommLink","Display","Pipe","Chain","AutoTutor",
                       "Winch","Spray","ObjectDispenser","Token","PressCake","BioMass","VatMaggot","Moss","Mold","MossSeed","MoldSpore","Bloom","Sprout","Sprout2","SickBloom",
                       "PoisonBloom","Bush","PoisonBush","EncrustedBush","Test","EncrustedPoisonBush","Chemical","Spawner","Explosion")

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

        # gather a metal bar
        metalBar = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,MetalBars):
                   metalBar = item
                   break
        
        # refuse production without ressources
        if not metalBar:
            messages.append("no metal bars available - place a metal bar to left/west")
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 0:
                targetFull = True

        if targetFull:
            self.character.messages.append("the target area is full, the machine does not produce anything")
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = gamestate.tick

        self.character.messages.append("you produce a %s"%(itemType.type,))

        # remove ressources
        self.room.removeItem(item)

        # spawn new item
        new = itemType(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.room.addItems([new])

    def getRemainingCooldown(self):
        return self.coolDown-(gamestate.tick-self.coolDownTimer)

    def getLongInfo(self):
        text = """
item: ProductionArtwork

description:
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This machine can build almost anything, but is very slow.

Prepare for production by placing metal bars to the west/left of this machine.
Activate the machine to start producing. You will be shown a list of things to produce.
Select the thing to produce and confirm.

After using this machine you need to wait %s ticks till you can use this machine again.
"""%(self.coolDown,)

        coolDownLeft = self.getRemainingCooldown()
        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

"""%(coolDownLeft,)
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges 

"""%(self.charges)
        else:
            text += """
Currently the machine has no charges 

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
    def __init__(self,xPosition=None,yPosition=None, name="scrap compactor",creator=None,noId=False):
        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1
        
        super().__init__(displayChars.scrapCompactor,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","charges","level"])

    '''
    produce a metal bar
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        # fetch input scrap
        scrap = None
        if not hasattr(self,"container"):
            if self.room:
                self.container = self.room
            else:
                self.container = self.terrain

        for item in self.container.getItemByPosition((self.xPosition-1,self.yPosition)):
            if isinstance(item,Scrap):
                scrap = item
                break
        if self.level > 1:
            if not scrap:
                for item in self.container.getItemByPosition((self.xPosition,self.yPosition+1)):
                    if isinstance(item,Scrap):
                        scrap = item
                        break
        if self.level > 2:
            if not scrap:
                for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1)):
                    if isinstance(item,Scrap):
                        scrap = item
                        break

        if gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return

        # refuse to produce without ressources
        if not scrap:
            character.messages.append("no scraps available")
            return

        targetPos = (self.xPosition+1,self.yPosition)
        targetFull = False
        itemList = self.container.getItemByPosition(targetPos)

        if len(itemList) > 15:
            targetFull = True
        for item in itemList:
            if item.walkable == False:
                targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = gamestate.tick

        character.messages.append("you produce a metal bar")

        # remove ressources
        if scrap.amount <= 1:
            self.container.removeItem(scrap)
        else:
            scrap.amount -= 1
            scrap.changed()
            scrap.setWalkable()

        # spawn the metal bar
        new = MetalBars(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.container.addItems([new])

    def getLongInfo(self):
        directions = "west"
        if self.level > 1:
            directions += "/south"
        if self.level > 2:
            directions += "/north"
        text = """
item: ScrapCompactor

description:
This machine converts scrap into metal bars. Metal bars are a form of metal that can be used to produce other things.

Place scrap to the %s of the machine and activate it 

After using this machine you need to wait %s ticks till you can use this machine again.
"""%(directions,self.coolDown,)

        coolDownLeft = self.coolDown-(gamestate.tick-self.coolDownTimer)
        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

"""%(coolDownLeft,)
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges

"""%(self.charges)
        else:
            text += """
Currently the machine has no charges

"""

        text += """
thie is a level %s item

"""%(self.level)
        return text


'''
'''
class Scraper(Item):
    type = "Scraper"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="scraper",creator=None,noId=False):
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        
        super().__init__(displayChars.scraper,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","charges"])

    '''
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        # fetch input scrap
        itemFound = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                itemFound = item
                break

        if gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = gamestate.tick

        # refuse to produce without ressources
        if not itemFound:
            character.messages.append("no items available")
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        # remove ressources
        self.room.removeItem(item)

        # spawn scrap
        new = Scrap(self.xPosition,self.yPosition,1,creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: Scrapper

description:
A scrapper shreds items to scrap.

Place an item to the west and activate the scrapper to shred an item.

"""
        return text

class Mover(Item):
    type = "Mover"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="mover",creator=None,noId=False):
        super().__init__(displayChars.sorter,xPosition,yPosition,name=name,creator=creator)

    '''
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        # fetch input scrap
        itemFound = None
        for item in self.container.getItemByPosition((self.xPosition-1,self.yPosition)):
            itemFound = item
            break

        # remove ressources
        self.container.removeItem(itemFound)

        targetPos = (self.xPosition+1,self.yPosition)

        itemFound.xPosition = targetPos[0]
        itemFound.yPosition = targetPos[1]


        targetFull = False
        new = itemFound
        items = self.container.getItemByPosition((self.xPosition+1,self.yPosition))
        if new.walkable:
            if len(items) > 15:
                targetFull = True
            for item in items:
                if item.walkable == False:
                    targetFull = True
        else:
            if len(items) > 1:
                targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        self.container.addItems([itemFound])

    def getLongInfo(self):
        text = """
item: Mover

description:
A mover moves items

Place the item or items to the west of the mover.
activate the mover to move one item to the east of the mover.

"""
        return text


'''
'''
class Sorter(Item):
    type = "Sorter"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="sorter",creator=None,noId=False):
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        
        super().__init__(displayChars.sorter,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])

    '''
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

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
            targetPos = (self.xPosition,self.yPosition+1)
        else:
            targetPos = (self.xPosition+1,self.yPosition)

        itemFound.xPosition = targetPos[0]
        itemFound.yPosition = targetPos[1]


        targetFull = False
        new = itemFound
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if new.walkable:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 1:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        self.room.addItems([itemFound])

    def getLongInfo(self):
        text = """
item: Sorter

description:
A sorter can sort items.

To sort item with a sorter place the item you want to compare against on the north.
Place the item or items to be sorted on the west of the sorter.
Activate the sorter to sort an item.
Matching items will be moved to the south and non matching items will be moved to the east.

"""
        return text

'''
'''
class AutoScribe(Item):
    type = "AutoScribe"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="copy machine",creator=None,noId=False):
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        self.level = 1
        
        super().__init__(displayChars.sorter,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","level"])

    '''
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        # fetch input command or Note
        itemFound = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if item.type in ["Command","Note"]:
                    itemFound = item
                    break

        sheetFound = None
        if (self.xPosition,self.yPosition-1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                if item.type in ["Sheet"]:
                    sheetFound = item
                    break

        if gamestate.tick < self.coolDownTimer+self.coolDown:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = gamestate.tick

        # refuse to produce without ressources
        if not itemFound:
            character.messages.append("no items available")
            return
        if not sheetFound:
            character.messages.append("no sheet available")
            return

        # remove ressources
        self.room.removeItem(sheetFound)
        self.room.removeItem(itemFound)

        # spawn new item
        if itemFound.type == "Command":
            new = Command(creator=self)
            new.command = itemFound.command
        elif itemFound.type == "Note":
            new = Note(creator=self)
            new.text = itemFound.text
        elif itemFound.type == "BluePrint":
            new = BluePrint(creator=self)
            new.setToProduce(itemFound.endProduct)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False

        if itemFound.type == "Command":
            new.name = itemFound.name
            new.description = itemFound.description

        if hasattr(itemFound,"level"):
            newLevel = min(itemFound.level,sheetFound.level,self.level)
            new.level = newLevel

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if new.walkable:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 1:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        self.room.addItems([new])
        itemFound.xPosition = self.xPosition
        itemFound.yPosition = self.yPosition + 1
        self.room.addItems([itemFound])

    def getLongInfo(self):
        text = """
item: AutoScribe

description:
A AutoScribe copies commands.

The command to copy has to be placed to the west of the machine.
A sheet has to be placed to the north of the machine.
The copy of the command will be outputted to the east.
The original command will be outputted to the south.

The level of the copied command is the minimum level of the input command, sheet and the auto scribe itself.

This is a level %s item

"""%(self.level)
        return text


'''
'''
class Token(Item):
    type = "Token"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="token",creator=None,noId=False):
        super().__init__(displayChars.token,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
A token. Only has value in the eyes of the beholder.

"""
        return text

'''
'''
class VatMaggot(Item):
    type = "VatMaggot"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="vat maggot",creator=None,noId=False):
        super().__init__(displayChars.vatMaggot,xPosition,yPosition,name=name,creator=creator)

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

    def getLongInfo(self):
        text = """
A vat maggot is the basis for food.

You can eat it, but it may kill you. Activate it to eat it.

Can be processed into bio mass by a maggot fermenter.

"""
        return text


'''
'''
class Sheet(Item):
    type = "Sheet"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="sheet",creator=None,noId=False):
        super().__init__(displayChars.sheet,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.recording = False
        self.character = None

        self.level = 1

        self.attributesToStore.extend([
                "recording","level"])
        self.initialState = self.getState()

    def getLongInfo(self):
        text = """
A sheet. Simple building material and use to store information.

Can be used to create a Note or a written command directly from the sheet.
Activate the sheet to get a selection, whether to create a command or a note.

To create a note select the "create note" option and type the text of the note.
Press enter to finish entering the text.

To create a command from a sheet. select the the "create command" option.
There are two ways to enter the command.

The first option is to record a new command.
After activating this option you will start to record your actions.
Activate the sheet again to create to command and to stop recording.

The second option ist to store a command from an existing macro buffer.
Activate this option and select the macro buffer to create the command.

Sheets are also needed as ressource to create a blueprint in the blueprinter machine.

Sheets can be produced from metal bars.

This is a level %s item

"""%(self.level)
        return text

    def apply(self,character):
        super().apply(character,silent=True)

        if self.recording:
            self.createCommand()
            return

        if isinstance(character,src.characters.Monster):
            return

        self.character = character

        options = []
        options.append(("createCommand","create a written command"))
        options.append(("createNote","create a note"))
        options.append(("createMap","create a map"))
        self.submenue = interaction.SelectionMenu("What do you want do do?",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.actionSwitch

    def actionSwitch(self):
        if self.submenue.selection == "createNote":
            self.createNote()
        elif self.submenue.selection == "createCommand":
            self.createCommand()
        elif self.submenue.selection == "createMap":
            self.createMapItem()

    def createNote(self):
        self.submenue = interaction.InputMenu("type the text you want to write on the note")
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.createNoteItem

    def createNoteItem(self):

        note = Note(self.xPosition,self.yPosition, creator=self)
        note.setText(self.submenue.text)

        if self.xPosition:
            if self.room:
                self.room.removeItem(self)
                self.room.addItems([note])
            else:
                self.container.removeItem(self)
                self.container.addItems([note])
        else:
            self.character.inventory.remove(self)
            self.character.inventory.append(note)

    def createMapItem(self):

        mapItem = Map(self.xPosition,self.yPosition, creator=self)

        if self.xPosition:
            if self.room:
                self.room.removeItem(self)
                self.room.addItems([mapItem])
            else:
                self.container.removeItem(self)
                self.container.addItems([mapItem])
        else:
            self.character.inventory.remove(self)
            self.character.inventory.append(mapItem)

    def createCommand(self):

        if not self.character:
            return

        if not len(self.character.macroState["macros"]):
            self.character.messages.append("no macro found - record a macro to be able to write a command")
        
        if self.recording:
            convertedCommand = []
            convertedCommand.append(("-",["norecord"]))
            self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]

            if not "a" in self.character.macroState["macros"]:
                self.character.messages.append("no macro found in buffer \"a\"")
                return

            if self.xPosition:
                self.character.macroState["macros"]["a"] = self.character.macroState["macros"]["a"][:-1]
            else:
                counter = 1
                while not self.character.macroState["macros"]["a"][-counter] == "i":
                    counter += 1
                self.character.macroState["macros"]["a"] = self.character.macroState["macros"]["a"][:-counter]
            self.storeMacro("a")
            self.recording = False
            del self.character.macroState["macros"]["a"]
            return

        options = []
        options.append(("record","start recording (records to buffer + reapply to create command)"))
        options.append(("store","store macro from memory"))
        self.submenue = interaction.SelectionMenu("select how to get the commands content",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.storeSelect

    def storeSelect(self):
        if self.submenue.selection == "record":
            self.recordAndstore()
        elif self.submenue.selection == "store":
            self.storeFromMacro()

    def recordAndstore(self):
        self.recording = True
        convertedCommand = []
        convertedCommand.append(("-",["norecord"]))
        convertedCommand.append(("a",["norecord"]))
        self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]

    def storeFromMacro(self):
        self.recording = True

        options = []
        for key,value in self.character.macroState["macros"].items():
            compressedMacro = ""
            for keystroke in value:
                if len(keystroke) == 1:
                    compressedMacro += keystroke
                else:
                    compressedMacro += "/"+keystroke+"/"
            options.append((key,key+" - "+compressedMacro))

        self.submenue = interaction.SelectionMenu("select the macro you want to store",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.storeMacro


    def storeMacro(self,key=None):
        if not key:
            key = self.submenue.selection

        if not key in self.character.macroState["macros"]:
            self.character.messages.append("command not found in macro")
            return

        command = Command(self.xPosition,self.yPosition, creator=self)
        command.setPayload(self.character.macroState["macros"][key])

        self.character.messages.append("you created a written command")

        if self.xPosition:
            if self.room:
                self.room.removeItem(self)
                self.room.addItems([command])
            else:
                self.container.removeItem(self)
                self.container.addItems([command])
        else:
            self.character.inventory.remove(self)
            self.character.inventory.append(command)

'''
'''
class Note(Item):
    type = "Note"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Note",creator=None,noId=False):
        super().__init__(displayChars.sheet,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.text = ""

        self.attributesToStore.extend([
                "text"])
        self.initialState = self.getState()

    def getLongInfo(self):

        text = """
A Note. It has a text on it. You can activate it to read it.

it holds the text:

"""+self.text+"""

"""
        return text

    def apply(self,character):
        super().apply(character,silent=True)

        submenue = interaction.OneKeystokeMenu("the note has the text: \n\n\n%s"%(self.text,))
        character.macroState["submenue"] = submenue

    def setText(self,text):
        self.text = text

'''
'''
class Map(Item):
    type = "Map"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Map",creator=None,noId=False):
        super().__init__(displayChars.map,xPosition,yPosition,name=name,creator=creator)

        self.routes = {
                      }
        self.walkable = True
        self.bolted = False
        self.recording = False
        self.recordingStart = None
        self.macroBackup = None

        self.markers = {}

        self.attributesToStore.extend([
                "text","recording"])
        self.initialState = self.getState()

    def apply(self,character):
        super().apply(character,silent=True)

        options = []
        options.append(("walkRoute","walk route"))
        options.append(("showRoutes","show routes"))
        options.append(("addMarker","add marker"))
        options.append(("addRoute","add route"))
        options.append(("abort","abort"))
        self.character = character
        self.submenue = interaction.SelectionMenu("where do you want to do?",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.selectActivity
        self.macroBackup = self.character.macroState["macros"].get("auto")

    def selectActivity(self):
        if self.submenue.selection == "walkRoute":
            self.walkRouteSelect()
        elif self.submenue.selection == "addMarker":
            self.addMarker()
        elif self.submenue.selection == "addRoute":
            self.addRoute()
        else:
            self.submenue = None
            self.character = None

    def addRoute(self):
        pos = (self.character.xPosition,self.character.yPosition)
        if not self.recording:
            self.character.messages.append("walk the path to the target and activate this menu item again")
            self.character.macroState["commandKeyQueue"] = [("-",["norecord"]),("auto",["norecord"])]+self.character.macroState["commandKeyQueue"] 
            self.recordingStart = pos
            self.recording = True
        else:
            self.character.macroState["commandKeyQueue"] = [("-",["norecord"])]+self.character.macroState["commandKeyQueue"] 
            self.recording = None
            if not self.macroBackup:
                return
            if not self.recordingStart in self.routes:
                self.routes[self.recordingStart] = {}
            if self.xPosition:
                counter = 2
            else:
                counter = 1
                while not self.macroBackup[-counter] == "i":
                    counter += 1
            self.routes[self.recordingStart][pos] = self.macroBackup[:-counter]
            del self.character.macroState["macros"]["auto"]
            self.character.messages.append("added path from %s to %s"%(self.recordingStart,pos))
            self.recordingStart = None

    def addMarker(self):
        items = self.character.container.getItemByPosition((self.character.xPosition,self.character.yPosition))
        for item in items:
            if isinstance(item,src.items.FloorPlate):
                self.markers[(self.character.xPosition,self.character.yPosition)] = item.name
                break

    def walkRouteSelect(self):
        charPos = (self.character.xPosition,self.character.yPosition)

        if not charPos in self.routes:
            self.character.messages.append("no routes found for this position")
            return

        options = []
        for target in self.routes[charPos].keys():
            if target in self.markers:
                target = self.markers[target]
            options.append((target,str(target)))
        options.append(("abort","abort"))
        self.submenue = interaction.SelectionMenu("where do you want to go?",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.walkRoute

    def walkRoute(self):
        if self.submenue.selection == "abort":
            return
        charPos = (self.character.xPosition,self.character.yPosition)
        path = self.routes[charPos][self.submenue.selection]
        convertedPath = []
        for step in path:
            convertedPath.append((step,["norecord"]))
        self.character.macroState["commandKeyQueue"] = convertedPath + self.character.macroState["commandKeyQueue"]
        self.character.messages.append("you walk the path")

    def getLongInfo(self):

        text = """
item: Map

description:
A map is a collection of routes.

You can select the routes and run the stored route.

"""
        return text


'''
'''
class Command(Item):
    type = "Command"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Command",creator=None,noId=False):
        super().__init__(displayChars.command,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.command = ""
        self.extraName = ""
        self.description = None
        self.level = 1

        self.attributesToStore.extend([
                "command","extraName","level","description"])
        self.initialState = self.getState()

    def getLongInfo(self):
        compressedMacro = ""
        for keystroke in self.command:
            if len(keystroke) == 1:
                compressedMacro += keystroke
            else:
                compressedMacro += "/"+keystroke+"/"

        text = """
item: Command

description:
A command. A command is written on it. Activate it to run command.

"""
        text += """

This is a level %s item.
"""%(self.level)

        if self.name:
            text += """
name: %s"""%(self.name)
        if self.description and len(self.description) > 0:
            text += """

description:\n%s"""%(self.description)
        text += """

it holds the command:

%s

"""%(compressedMacro)
        return text

    def apply(self,character):
        super().apply(character,silent=True)

        if isinstance(character,src.characters.Monster):
            return

        if self.level == 1:
            self.runPayload(character)
        else:
            options = [("runCommand","run command"),
                       ("setName","set name"),]
            if self.level > 2:
                options.append(("setDescription","set description"))
            if self.level > 3:
                options.append(("rememberCommand","store command in memory"))

            self.submenue = interaction.SelectionMenu("Do you want to reconfigure the machine?",options)
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.advancedActions
            self.character = character
            pass

    def advancedActions(self):
        if self.submenue.selection == "runCommand":
            self.runPayload(self.character)
        elif self.submenue.selection == "setName":
            self.submenue = interaction.InputMenu("Enter the name")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setName
        elif self.submenue.selection == "setDescription":
            self.submenue = interaction.InputMenu("Enter the description")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setDescription
        elif self.submenue.selection == "rememberCommand":

            if not self.name or self.name == "":
                self.character.messages("command not loaded: command has no name")
                return

            properName = True
            for char in self.name[:-1]:
                if not (char.isupper() or char == " "):
                    properName = False
                    break
            if self.name[-1].isupper():
                properName = False
                pass

            if properName:
                self.character.macroState["macros"][self.name] = self.command
                self.character.messages.append("loaded command to macro storage")
            else:
                self.character.messages.append("command not loaded: name not in propper format. Should be capital letters except the last letter. example \"EXAMPLE NAMe\"")
        else:
            self.character.messages("action not found")

    def setName(self):
        self.name = self.submenue.text
        self.character.messages.append("set command name to %s"%(self.name))

    def setDescription(self):
        self.description = self.submenue.text
        self.character.messages.append("set command description")

    def runPayload(self,character):
        convertedCommand = []
        for item in self.command:
            convertedCommand.append((item,["norecord"]))
        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

    def setPayload(self,command):
        import copy
        self.command = copy.deepcopy(command)

    def getDetailedInfo(self):
        if self.extraName == "":
            return super().getDetailedInfo()+" "
        else:
            return super().getDetailedInfo()+" - "+self.extraName

class CommandBook(Item):
    type = "CommandBook"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="command book",creator=None,noId=False):
        super().__init__(displayChars.Command,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        totalCommands = 0

        self.contents = []

        self.attributesToStore.extend([
                "contents"])
        self.initialState = self.getState()

    def getState(self):
        state = super().getState()
        state["contents"] = self.availableChallenges
        state["knownBlueprints"] = self.knownBlueprints
        return state

'''
'''
class FloorPlate_real(Item):
    type = "FloorPlate"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="floor plate",creator=None,noId=False):
        super().__init__(displayChars.floor,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: FloorPlate

description:
Used as building material and can be used to mark paths

"""
        return text


'''
'''
class FloorPlate(Item):
    type = "FloorPlate"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="floor plate",creator=None,noId=False):
        super().__init__("--",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.name = "test"

    def getLongInfo(self):
        text = """
item: FloorPlate

description:
Used as building material and can be used to mark paths

"""
        return text

    def apply(self, character):
        self.character = character
        self.addText()

    def addText(self):
        self.submenue = interaction.InputMenu("Enter the name")
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.setName

    def setName(self):
        self.name = self.character.macroState["submenue"].text

    def getLongInfo(self):
        text = """
item: FloorPlate

description:
%s

"""%(self.name)
        return text

'''
'''
class Rod(Item):
    type = "Rod"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="rod",creator=None,noId=False):
        super().__init__(displayChars.rod,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Rod

description:
A rod. Simple building material.

"""
        return text

'''
'''
class Mount(Item):
    type = "Mount"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="mount",creator=None,noId=False):
        super().__init__(displayChars.nook,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
A mount. Simple building material.

"""
        return text

'''
'''
class Stripe(Item):
    type = "Stripe"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="stripe",creator=None,noId=False):
        super().__init__(displayChars.stripe,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Stripe

description:
A Stripe. Simple building material.

"""
        return text

'''
'''
class Bolt(Item):
    type = "Bolt"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="bolt",creator=None,noId=False):
        super().__init__(displayChars.bolt,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Bolt

description:
A Bolt. Simple building material.

"""
        return text

'''
'''
class Radiator(Item):
    type = "Radiator"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="radiator",creator=None,noId=False):
        super().__init__(displayChars.coil,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Radiator

description:
A radiator. Simple building material.

"""
        return text

'''
'''
class Tank(Item):
    type = "Tank"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="tank",creator=None,noId=False):
        super().__init__(displayChars.tank,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Tank

description:
A tank. Building material.

"""
        return text

'''
'''
class Heater(Item):
    type = "Heater"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="heater",creator=None,noId=False):
        super().__init__(displayChars.heater,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Heater

description:
A heater. Building material.

"""
        return text

'''
'''
class Connector(Item):
    type = "Connector"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="connector",creator=None,noId=False):
        super().__init__(displayChars.connector,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Connector

description:
A connector. Building material.

"""
        return text


'''
'''
class Puller(Item):
    type = "puller"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="puller",creator=None,noId=False):
        super().__init__(displayChars.puller,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
A puller. Building material.

"""
        return text

'''
'''
class Pusher(Item):
    type = "pusher"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="pusher",creator=None,noId=False):
        super().__init__(displayChars.pusher,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Pusher

description:
A pusher. Building material.

"""
        return text

'''
'''
class Frame(Item):
    type = "Frame"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Frame",creator=None,noId=False):
        super().__init__(displayChars.frame,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Frame

description:
A frame. Building material.

"""
        return text

'''
'''
class Tree(Item):
    type = "Tree"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="tree",creator=None,noId=False):
        super().__init__(displayChars.tree,xPosition,yPosition,name=name,creator=creator)

        self.bolted = True
        self.walkable = False

    def apply(self,character):

        character.messages.append("you harvest a vat maggot")

        targetFull = False
        targetPos = (self.xPosition+1,self.yPosition)
        if targetPos in self.terrain.itemByCoordinates:
            if len(self.terrain.itemByCoordinates[targetPos]) > 15:
                targetFull = True
            for item in self.terrain.itemByCoordinates[targetPos]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not work")
            return

        # spawn new item
        new = VatMaggot(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.terrain.addItems([new])

    def getLongInfo(self):
        text = """
item: Tree

description:
A tree can be used as a source for vat maggots.

Activate the tree to harvest a vat maggot.

"""
        return text

'''
'''
class BioMass(Item):
    type = "BioMass"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="bio mass",creator=None,noId=False):
        super().__init__(displayChars.bioMass,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # change state
        character.satiation += 200
        if character.satiation > 1000:
            character.satiation = 1000
        character.changed()
        self.destroy(generateSrcap=False)
        character.messages.append("you eat the bio mass")

    def getLongInfo(self):
        text = """
item: BioMass

description:
A bio mass is basis for food production.

Can be processed into press cake by a bio press.
"""
        return text

'''
'''
class PressCake(Item):
    type = "PressCake"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="press cake",creator=None,noId=False):
        super().__init__(displayChars.pressCake,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: PressCake

description:
A press cake is basis for food production.

Can be processed into goo by a goo producer.
"""
        return text

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # change state
        character.satiation = 1000
        character.changed()
        self.destroy(generateSrcap=False)
        character.messages.append("you eat the press cake and gain 1000 satiation")

'''
'''
class GameTestingProducer(Item):
    type = "GameTestingProducer"

    def __init__(self,xPosition=None,yPosition=None, name="testing producer",creator=None, seed=0, possibleSources=[MetalBars], possibleResults=[Wall],noId=False):
        self.coolDown = 20
        self.coolDownTimer = -self.coolDown

        super().__init__(displayChars.gameTestingProducer,xPosition,yPosition,name=name,creator=creator)

        self.seed = seed
        self.baseName = name
        self.possibleResults = possibleResults
        self.possibleSources = possibleSources
        self.change_apply_2(force=True)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])
        self.initialState = self.getState()

    def apply(self,character,resultType=None):

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

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

    def getLongInfo(self):
        text = """
item: GameTestingProducer

description:
A game testing producer. It produces things.

Place metalbars to left/west and activate the machine to produce.

"""
        return text

'''
'''
class MachineMachine(Item):
    type = "MachineMachine"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="machine machine",creator=None,noId=False):
        self.coolDown = 1000
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1

        self.endProducts = {
        }
        self.blueprintLevels = {
        }

        super().__init__(displayChars.machineMachine,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","endProducts","charges","level"])

        self.initialState = self.getState()

    '''
    trigger production of a player selected item
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        options = []
        options.append(("blueprint","load blueprint"))
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
        if (self.xPosition,self.yPosition-1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                if item.type in ["BluePrint"]:
                    blueprintFound = item
                    break

        if not blueprintFound:
            self.character.messages.append("no blueprint found above/north")
            return

        self.endProducts[blueprintFound.endProduct] = blueprintFound.endProduct
        if not blueprintFound.endProduct in self.blueprintLevels:
            self.blueprintLevels[blueprintFound.endProduct] = 0
        if self.blueprintLevels[blueprintFound.endProduct] < blueprintFound.level:
            self.blueprintLevels[blueprintFound.endProduct] = blueprintFound.level

        self.character.messages.append("blueprint for "+blueprintFound.endProduct+" inserted")
        self.room.removeItem(blueprintFound)

    def productionSwitch(self):

        if self.endProducts == {}:
            self.character.messages.append("no blueprints available.")
            return

        if gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
            self.character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return

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

        if not self.container:
            if self.room:
                self.container = self.room
            elif self.terrain:
                self.container = self.terrain

        # gather a metal bar
        ressourcesNeeded = ["MetalBars"]

        ressourcesFound = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if item.type in ressourcesNeeded:
                   ressourcesFound.append(item)
                   ressourcesNeeded.remove(item.type)
        
        # refuse production without ressources
        if ressourcesNeeded:
            self.character.messages.append("missing ressources: %s"%(",".join(ressourcesNeeded)))
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 0:
                targetFull = True

        if targetFull:
            self.character.messages.append("the target area is full, the machine does not produce anything")
            return
        else:
            self.character.messages.append("not full")

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = gamestate.tick

        self.character.messages.append("you produce a machine that produces %s"%(itemType,))

        # remove ressources
        for item in ressourcesFound:
            self.room.removeItem(item)

        # spawn new item
        new = Machine(creator=self)
        new.productionLevel = self.blueprintLevels[itemType]
        new.setToProduce(itemType)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False

        if hasattr(new,"coolDown"):
            import random
            new.coolDown = random.randint(new.coolDown,int(new.coolDown*1.25))

        self.room.addItems([new])

    def getState(self):
        state = super().getState()
        state["endProducts"] = self.endProducts
        return state

    def getDiffState(self):
        state = super().getDiffState()
        state["endProducts"] = self.endProducts
        return state

    def setState(self,state):
        super().setState(state)
        self.endProducts = state["endProducts"]

    def getLongInfo(self):
        text = """
item: MachineMachine

description:
This machine produces machines that build machines. It needs blueprints to do that.

You can load blueprints into this machine.
Prepare by placing a blueprint to the above/north of this machine.
After activation select "load blueprint" and the blueprint will be added.

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

        if self.charges:
            text += """
Currently the machine has %s charges 

"""%(self.charges)
        else:
            text += """
Currently the machine has no charges 

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
    def __init__(self,xPosition=None,yPosition=None, name="Machine",creator=None,seed=0,noId=False):
        self.toProduce = "Wall"

        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1
        self.productionLevel = 1

        super().__init__(displayChars.machine,xPosition,yPosition,name=name,creator=creator,seed=seed)

        self.attributesToStore.extend([
               "toProduce","level","productionLevel"])

        self.baseName = name

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","charges"])

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

        if not self.container:
            if self.room:
                self.container = self.room
            elif self.terrain:
                self.container = self.terrain

        #if not self.room:
        #    character.messages.append("this machine can only be used within rooms")
        #    return

        if gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
            character.messages.append("cooldown not reached. Wait %s ticks"%(self.coolDown-(gamestate.tick-self.coolDownTimer),))
            return

        if self.toProduce == "Sheet":
            ressourcesNeeded = ["MetalBars"]
        elif self.toProduce == "Radiator":
            ressourcesNeeded = ["MetalBars"]
        elif self.toProduce == "Mount":
            ressourcesNeeded = ["MetalBars"]
        elif self.toProduce == "Stripe":
            ressourcesNeeded = ["MetalBars"]
        elif self.toProduce == "Bolt":
            ressourcesNeeded = ["MetalBars"]
        elif self.toProduce == "Rod":
            ressourcesNeeded = ["MetalBars"]

        elif self.toProduce == "Tank":
            ressourcesNeeded = ["Sheet"]
        elif self.toProduce == "Heater":
            ressourcesNeeded = ["Radiator"]
        elif self.toProduce == "Connector":
            ressourcesNeeded = ["Mount"]
        elif self.toProduce == "pusher":
            ressourcesNeeded = ["Stripe"]
        elif self.toProduce == "puller":
            ressourcesNeeded = ["Bolt"]
        elif self.toProduce == "Frame":
            ressourcesNeeded = ["Rod"]

        elif self.toProduce == "Case":
            ressourcesNeeded = ["Frame"]
        elif self.toProduce == "PocketFrame":
            ressourcesNeeded = ["Frame"]
        elif self.toProduce == "MemoryCell":
            ressourcesNeeded = ["Connector"]
        elif self.toProduce == "AutoScribe":
            ressourcesNeeded = ["Case","MetalBars","MemoryCell","pusher","puller"]
        elif self.toProduce == "FloorPlate":
            ressourcesNeeded = ["Sheet","MetalBars"]

        elif self.toProduce == "Scraper":
            ressourcesNeeded = ["Case","MetalBars"]
        elif self.toProduce == "GrowthTank":
            ressourcesNeeded = ["Case","MetalBars"]
        elif self.toProduce == "Door":
            ressourcesNeeded = ["Case","MetalBars"]
        elif self.toProduce == "Wall":
            ressourcesNeeded = ["Case","MetalBars"]
        elif self.toProduce == "Boiler":
            ressourcesNeeded = ["Case","MetalBars"]
        elif self.toProduce == "Drill":
            ressourcesNeeded = ["Case","MetalBars"]
        elif self.toProduce == "ScrapCompactor":
            ressourcesNeeded = ["MetalBars"]
        elif self.toProduce == "Furnace":
            ressourcesNeeded = ["Case","MetalBars"]

        elif self.toProduce == "GooFlask":
            ressourcesNeeded = ["Tank"]

        elif self.toProduce == "GooDispenser":
            ressourcesNeeded = ["Case","MetalBars","Heater"]
        elif self.toProduce == "MaggotFermenter":
            ressourcesNeeded = ["Case","MetalBars","Heater"]
        elif self.toProduce == "BloomShredder":
            ressourcesNeeded = ["Case","MetalBars","Heater"]
        elif self.toProduce == "SporeExtractor":
            ressourcesNeeded = ["Case","MetalBars","puller"]
        elif self.toProduce == "BioPress":
            ressourcesNeeded = ["Case","MetalBars","Heater"]
        elif self.toProduce == "GooProducer":
            ressourcesNeeded = ["Case","MetalBars","Heater"]
        elif self.toProduce == "CorpseShredder":
            ressourcesNeeded = ["Case","MetalBars","Heater"]

        elif self.toProduce == "MemoryDump":
            ressourcesNeeded = ["Case","MemoryCell"]
        elif self.toProduce == "MemoryStack":
            ressourcesNeeded = ["Case","MemoryCell"]
        elif self.toProduce == "MemoryReset":
            ressourcesNeeded = ["Case","MemoryCell"]
        elif self.toProduce == "MemoryBank":
            ressourcesNeeded = ["Case","MemoryCell"]
        elif self.toProduce == "SimpleRunner":
            ressourcesNeeded = ["Case","MemoryCell"]

        elif self.toProduce == "MarkerBean":
            ressourcesNeeded = ["PocketFrame"]
        elif self.toProduce == "PositioningDevice":
            ressourcesNeeded = ["PocketFrame"]
        elif self.toProduce == "Watch":
            ressourcesNeeded = ["PocketFrame"]
        elif self.toProduce == "BackTracker":
            ressourcesNeeded = ["PocketFrame"]
        elif self.toProduce == "Tumbler":
            ressourcesNeeded = ["PocketFrame"]

        elif self.toProduce == "RoomControls":
            ressourcesNeeded = ["Case","pusher","puller"]
        elif self.toProduce == "StasisTank":
            ressourcesNeeded = ["Case","pusher","puller"]
        elif self.toProduce == "ItemUpgrader":
            ressourcesNeeded = ["Case","pusher","puller"]
        elif self.toProduce == "ItemDowngrader":
            ressourcesNeeded = ["Case","pusher","puller"]
        elif self.toProduce == "RoomBuilder":
            ressourcesNeeded = ["Case","pusher","puller"]
        elif self.toProduce == "BluePrinter":
            ressourcesNeeded = ["Case","pusher","puller"]

        elif self.toProduce == "Container":
            ressourcesNeeded = ["Case","Sheet"]
        elif self.toProduce == "BloomContainer":
            ressourcesNeeded = ["Case","Sheet"]

        elif self.toProduce == "Mover":
            ressourcesNeeded = ["Case","pusher","puller"]
        elif self.toProduce == "Sorter":
            ressourcesNeeded = ["Case","pusher","puller"]
        
        elif self.toProduce == "FireCrystals":
            ressourcesNeeded = ["Coal","SickBloom"]
        elif self.toProduce == "Bomb":
            ressourcesNeeded = ["Frame","Explosive"]

        else:
            ressourcesNeeded = ["MetalBars"]

        """
        if self.toProduce == "Sheet":
            ressourcesNeeded = ["MetalBars"]
        elif self.toProduce == "Radiator":
            ressourcesNeeded = ["MetalBars"]
        elif self.toProduce == "Mount":
            ressourcesNeeded = ["MetalBars"]
        elif self.toProduce == "Stripe":
            ressourcesNeeded = ["MetalBars"]
        elif self.toProduce == "Bolt":
            ressourcesNeeded = ["MetalBars"]
        elif self.toProduce == "Rod":
            ressourcesNeeded = ["MetalBars"]

        elif self.toProduce == "Tank":
            ressourcesNeeded = ["MetalBars","Sheet","Sheet","Rod"]
        elif self.toProduce == "Heater":
            ressourcesNeeded = ["MetalBars","Radiator","Radiator"]
        elif self.toProduce == "Connector":
            ressourcesNeeded = ["MetalBars","Mount","Stripe","Rod"]
        elif self.toProduce == "pusher":
            ressourcesNeeded = ["MetalBars","Stripe","Rod"]
        elif self.toProduce == "puller":
            ressourcesNeeded = ["MetalBars","Stripe","Rod"]
        elif self.toProduce == "Frame":
            ressourcesNeeded = ["MetalBars","Sheet","Rod"]

        elif self.toProduce == "Case":
            ressourcesNeeded = ["Frame","Frame","MetalBars","MetalBars","MetalBars","MetalBars"]
        elif self.toProduce == "MemoryCell":
            ressourcesNeeded = ["MetalBars","Coal","Tank","Rod","Stripe","Stripe"]

        elif self.toProduce == "ScrapCompactor":
            ressourcesNeeded = ["Case","pusher"]
        elif self.toProduce == "Wall":
            ressourcesNeeded = ["Case" ,"MetalBars","MetalBars","MetalBars","MetalBars","MetalBars"]
        elif self.toProduce == "Door":
            ressourcesNeeded = ["Case","Sheet","Connector"]
        elif self.toProduce == "Drill":
            ressourcesNeeded = ["Case","Rod","pusher"]
        elif self.toProduce == "Furnace":
            ressourcesNeeded = ["Case","Mount","Radiator"]
        elif self.toProduce == "Scraper":
            ressourcesNeeded = ["Case","puller","pusher"]
        elif self.toProduce == "GooDispenser":
            ressourcesNeeded = ["Case","Tank","GooFlask"]
        elif self.toProduce == "MaggotFermenter":
            ressourcesNeeded = ["Case","Tank","Heater"]
        elif self.toProduce == "BioPress":
            ressourcesNeeded = ["Case","Sheet","pusher"]
        elif self.toProduce == "GooProducer":
            ressourcesNeeded = ["Case","Stripe","Heater"]
        elif self.toProduce == "Sorter":
            ressourcesNeeded = ["Case","Rod","Connector"]
        elif self.toProduce == "GrowthTank":
            ressourcesNeeded = ["Case","Sheet","Tank"]

        elif self.toProduce == "MemoryDump":
            ressourcesNeeded = ["Case","MemoryCell","Connector"]
        elif self.toProduce == "MemoryStack":
            ressourcesNeeded = ["Case","MemoryCell","MemoryCell","Connector"]
        elif self.toProduce == "MemoryReset":
            ressourcesNeeded = ["Case","Connector"]
        elif self.toProduce == "MemoryBank":
            ressourcesNeeded = ["Case","MemoryCell","Connector","puller"]
        elif self.toProduce == "SimpleRunner":
            ressourcesNeeded = ["Case","MemoryCell","Connector","pusher"]

        elif self.toProduce == "Watch":
            ressourcesNeeded = ["Frame","MemoryCell","Connector","pusher"]
        elif self.toProduce == "BackTracker":
            ressourcesNeeded = ["Frame","MemoryCell","MemoryCell","MemoryCell","puller","pusher"]
        elif self.toProduce == "PositioningDevice":
            ressourcesNeeded = ["Frame","MemoryCell","Connector","Connector","Connector","Connector","pusher"]
        elif self.toProduce == "Tumbler":
            ressourcesNeeded = ["Frame","Watch","MemoryCell","puller","pusher"]

        elif self.toProduce == "MarkerBean":
            ressourcesNeeded = ["Frame","Tank","Coal","Coal","Heater"]

        elif self.toProduce == "RoomBuilder":
            ressourcesNeeded = ["Case","Tank","pusher","puller","Rod","Connector"]

        elif self.toProduce == "GooFlask":
            ressourcesNeeded = ["MetalBars","Tank"]

        elif self.toProduce == "Sorter":
            ressourcesNeeded = ["Case","pusher","puller","Connector","pusher","puller",]
        elif self.toProduce == "StasisTank":
            ressourcesNeeded = ["GrowthTank","Connector","Tank","Sheet","Rod","Rod"]
        elif self.toProduce == "RoomControls":
            ressourcesNeeded = ["Case","pusher","puller","Sheet","Stripe","Rod"]
        elif self.toProduce == "ItemUpgrader":
            ressourcesNeeded = ["Case","Connector","Connector","pusher","puller","Rod"]
        elif self.toProduce == "BluePrinter":
            ressourcesNeeded = ["Case","Connector","Connector","Stripe","Stripe","Rod"]

        else:
            ressourcesNeeded = ["MetalBars"]
        """

        # gather a metal bar
        ressourcesFound = []
        if (self.xPosition-1,self.yPosition) in self.container.itemByCoordinates:
            for item in self.container.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if item.type in ressourcesNeeded:
                    ressourcesFound.append(item)
                    ressourcesNeeded.remove(item.type)
        
        if (self.xPosition,self.yPosition-1) in self.container.itemByCoordinates:
            for item in self.container.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                if item.type in ressourcesNeeded:
                    ressourcesFound.append(item)
                    ressourcesNeeded.remove(item.type)
        
        # refuse production without ressources
        if ressourcesNeeded:
            character.messages.append("missing ressources (place left/west or up/north): %s"%(", ".join(ressourcesNeeded)))
            return

        targetFull = False
        new = itemMap[self.toProduce](creator=self)

        if (self.xPosition+1,self.yPosition) in self.container.itemByCoordinates:
            if new.walkable:
                if len(self.container.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.container.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if len(self.container.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 0:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = gamestate.tick

        character.messages.append("you produce a %s"%(self.toProduce,))

        # remove ressources
        for item in ressourcesFound:
            self.container.removeItem(item)

        # spawn new item
        new = itemMap[self.toProduce](creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False

        if hasattr(new,"coolDown"):
            new.coolDown = round(new.coolDown*(1-(0.05*(self.productionLevel-1))))

            import random
            new.coolDown = random.randint(new.coolDown,int(new.coolDown*1.25))

        self.container.addItems([new])

        if hasattr(new,"level"):
            new.level = self.level

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

    def getLongInfo(self):
        coolDownLeft = self.coolDown-(gamestate.tick-self.coolDownTimer)

        text = """
item: Machine

description:
This Machine produces %s.

Prepare for production by placing the input materials to the west/left/noth/top of this machine.
Activate the machine to produce.

After using this machine you need to wait %s ticks till you can use this machine again.

this is a level %s item and will produce level %s items.

"""%(self.toProduce,self.coolDown,self.level,self.level)

        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

"""%(coolDownLeft,)
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges 

"""%(self.charges)
        else:
            text += """
Currently the machine has no charges 

"""

        return text

'''
'''
class Drill(Item):
    type = "Drill"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Drill",creator=None,noId=False):

        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.isBroken = False
        self.isCleaned = True

        self.baseName = name

        super().__init__(displayChars.drill,xPosition,yPosition,name=name,creator=creator)

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

                targetFull = False
                scrapFound = None
                if (self.xPosition,self.yPosition+1) in self.terrain.itemByCoordinates:
                    if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition+1)]) > 15:
                        targetFull = True
                    for item in self.terrain.itemByCoordinates[(self.xPosition,self.yPosition+1)]:
                        if item.walkable == False:
                            targetFull = True
                        if item.type == "Scrap":
                            scrapFound = item

                if targetFull:
                    character.messages.append("the target area is full, the machine does not produce anything")
                    return

                character.messages.append("you remove the broken rod")

                if scrapFound:
                    item.amount += 1
                else:
                    # spawn new item
                    new = Scrap(self.xPosition,self.yPosition,1,creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition+1
                    new.bolted = False

                    self.terrain.addItems([new])

                self.isCleaned = True

            else:

                character.messages.append("you repair the machine")

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
        possibleProducts = [Scrap,Coal,Scrap,Radiator,Scrap,Mount,Scrap,Sheet,Scrap,Rod,Scrap,Bolt,Scrap,Stripe,Scrap,]
        productIndex = gamestate.tick%len(possibleProducts)
        new = possibleProducts[productIndex](self.xPosition,self.yPosition,creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False

        foundScrap = None
        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.terrain.itemByCoordinates:
            if len(self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True
                if item.type == "Scrap":
                    foundScrap = item

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        if new.type == "Scrap" and foundScrap:
            foundScrap.amount += new.amount
        else:
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

    def getLongInfo(self):
        text = """
This drills items from the ground. You get different things from time to time.

Activate the drill to drill something up. Most likely you will dig up scrap.

After the every use the rod in the drill will break.
You need to replace the rod in the drill to repair it.
Use the drill to eject the broken rod from the drill.
place a rod to the left/west of the drill and activate the drill, to repair it

"""
        return text

class MemoryDump(Item):
    type = "MemoryDump"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MemoryDump",creator=None,noId=False):

        self.macros = None

        self.baseName = name

        super().__init__(displayChars.memoryDump,xPosition,yPosition,name=name,creator=creator)

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
            character.messages.append("this machine can only be used within rooms")
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
    def __init__(self,xPosition=None,yPosition=None, name="MemoryBank",creator=None,noId=False):

        self.macros = {}

        self.baseName = name

        super().__init__(displayChars.memoryBank,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
                "macros"])

        self.setDescription()

        self.initialState = self.getState()

    def setDescription(self):
        addition = ""
        if self.macros:
            addition = " (imprinted)"
        self.description = self.baseName+addition

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
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
class MemoryStack(Item):
    type = "MemoryStack"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MemoryStack",creator=None,noId=False):

        self.macros = []

        super().__init__(displayChars.memoryStack,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
                "macros"])

        self.initialState = self.getState()

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        options = []

        options.append(("p","push macro on stack"))
        options.append(("l","load/pop macro from stack"))

        self.submenue = interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doAction

        self.character = character

    '''
    '''
    def doAction(self):

        import copy
        if self.submenue.getSelection() == "p":
            self.character.messages.append("push your macro onto the memory stack")
            self.macros.append(copy.deepcopy(self.character.macroState["macros"]))
            self.character.messages.append(self.macros)
        elif self.submenue.getSelection() == "l":
            self.character.messages.append("you load a macro from the memory stack")
            self.character.macroState["macros"] = copy.deepcopy(self.macros.pop())
            self.character.messages.append(self.character.macroState["macros"])
        else:
            self.character.messages.append("invalid option")

'''
'''
class MemoryReset(Item):
    type = "MemoryReset"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MemoryStack",creator=None,noId=False):

        super().__init__(displayChars.memoryReset,xPosition,yPosition,name=name,creator=creator)


    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        character.messages.append("you clear your macros")

        character.macroState["macros"] = {}
        character.registers = {}

'''
'''
class Engraver(Item):
    type = "Engraver"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Engraver",creator=None,noId=False):
        super().__init__(displayChars.engraver,xPosition,yPosition,name=name,creator=creator)
        self.submenue = None
        self.text = None

    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

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
class AutoTutor(Item):
    type = "AutoTutor"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="AutoTutor",creator=None,noId=False):
        self.knownBlueprints = []
        self.knownInfos = []
        self.availableChallenges = {
                                   }


        super().__init__(displayChars.infoscreen,xPosition,yPosition,name=name,creator=creator)
        self.submenue = None
        self.text = None
        self.blueprintFound = False
        self.gooChallengeDone = False
        self.metalbarChallengeDone = False
        self.sheetChallengeDone = False
        self.machineChallengeDone = False
        self.blueprintChallengeDone = False
        self.commandChallengeDone = False
        self.energyChallengeDone = False
        self.activateChallengeDone = False
        self.activateChallenge = 100
        self.metalbarChallenge = 100
        self.wallChallenge = 25
        self.autoScribeChallenge = 25
        self.challengeRun2Done = False
        self.challengeRun3Done = False
        self.challengeRun4Done = False
        self.challengeRun5Done = False
        self.initialChallengeDone = False
        self.challengeInfo = {}

        self.attributesToStore.extend([
               "gooChallengeDone","metalbarChallengeDone","sheetChallengeDone","machineChallengeDone","blueprintChallengeDone","energyChallengeDone","activateChallengeDone",
               "commandChallengeDone","challengeRun2Done","challengeRun3Done","challengeRun4Done","challengeRun5Done","initialChallengeDone",
               "activateChallenge","wallChallenge","autoScribeChallenge",
               "knownBlueprints","availableChallenges","knownInfos","challengeInfo"])
        self.initialState = self.getState()

    def addScraps(self,amount=1):
        
        targetFull = False
        scrapFound = None
        itemList = self.container.getItemByPosition((self.xPosition,self.yPosition+1))
        if len(itemList) > 15:
            targetFull = True
        for item in itemList:
            if item.walkable == False:
                targetFull = True
            if item.type == "Scrap":
                scrapFound = item

        if targetFull:
            return False
        
        if scrapFound:
            scrapFound.amount += amount
            scrapFound.setWalkable()
        else:
            # spawn scrap
            new = Scrap(self.xPosition,self.yPosition,1,creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition+1
            new.amount = amount
            self.room.addItems([new])
            new.setWalkable()

        return True


    def apply(self,character):
        if not self.room:
            character.messages.append("can only be used within rooms")
            return
        super().apply(character,silent=True)

        self.character = character

        options = []

        options.append(("level1","check information"))
        options.append(("challenge","do challenge"))

        self.submenue = interaction.SelectionMenu("This is the automated tutor. Complete challenges and get information.\n\nwhat do you want do to?",options)

        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.step2

        self.character = character

    def step2(self):

        selection = self.submenue.getSelection()
        self.submenue = None

        if selection == "level1":
            self.basicInfo()
        elif selection == "challenge":
            self.challenge()
        elif selection == "level2":
            self.l2Info()
        elif selection == "level3":
            self.l3Info()
        elif selection == "level4":
            self.l4Info()
        else:
            self.character.messages.append("NOT ENOUGH ENERGY")

    def challenge(self):

        if not self.activateChallengeDone:
            if not self.initialChallengeDone:
                self.submenue = interaction.TextMenu("\n\nchallenge: find the challenges\nstatus:challenge completed.\n\nReturn to this menu item and you will find more challenges.\nNew challenge \"pick up goo flask\"\n\n")
                self.initialChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.gooChallengeDone:
                if not self.checkInInventory(src.items.GooFlask):
                    self.submenue = interaction.TextMenu("\n\nchallenge: pick up goo flask\nstatus: challenge in progress - Try again with a goo flask in your inventory.\n\ncomment:\nA goo flask is represnted by ò=. There should be some flasks in the room.\n\n")
                else:
                    self.submenue = interaction.TextMenu("\n\nchallenge: pick up goo flask\nstatus: challenge completed.\n\ncomment:\nTry to always keep a goo flask with some charges in your inventory.\nIf you are hungry you will drink from it automatically.\nIf you do not drink regulary you will die.\n\nreward:\nNew information option on \"information->machines\"\nNew Information option on \"information->food\"\nNew challenge \"gather metal bars\"\n\n")
                    self.gooChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.metalbarChallengeDone:
                if not self.checkInInventory(src.items.MetalBars):
                    self.submenue = interaction.TextMenu("\n\nchallenge: gather metal bars\nstatus: challenge in progress - Try again with a metal bar in your inventory.\n\ncomment: \nMetal bars are represented by ==\ncheck \"information->machines->metal bar production\" on how to produce metal bars.\n\n")
                else:
                    self.submenue = interaction.TextMenu("\n\nchallenge: gather metal bars\nstatus: challenge completed.\n\nreward:\nNew information option on \"information->machines->simple item production\"\nNew challenge \"produce sheet\"\n\n")
                    self.metalbarChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.sheetChallengeDone:
                if not self.checkInInventoryOrInRoom(src.items.Sheet):
                    self.submenue = interaction.TextMenu("\n\nchallenge: produce sheet\nstatus: challenge in progress - Try again with a sheet in your inventory.\n\ncomment: \ncheck \"information->machines->simple item production\" on how to produce simple items.\nA sheet machine should be within this room.\n\n")
                else:
                    self.submenue = interaction.TextMenu("\n\nchallenge: produce sheet\nstatus: challenge completed.\n\nreward:\nNew information option on \"information->machines->machine production\"\nNew challenge \"produce rod machine\"\n\n")
                    self.sheetChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.machineChallengeDone:
                foundMachine = False
                for item in self.character.inventory + self.room.itemsOnFloor:
                    if isinstance(item,src.items.Machine) and item.toProduce == "Rod":
                        foundMachine = True
                if not foundMachine:
                    self.submenue = interaction.TextMenu("\n\nchallenge: produce rod machine\nstatus: challenge in progress - Try again with a machine that produces rods in your inventory.\n\ncomment:\n\ncheck \"information->machines->machine production\" on how to produce machines.\nBlueprints for the basic materials including rods should be in this room.\nblueprints are represented by bb\n\n")
                else:
                    self.knownBlueprints.append("Frame")
                    self.knownBlueprints.append("Rod")
                    self.submenue = interaction.TextMenu("\n\nchallenge: produce rod machine\nstatus: challenge completed.\n\nreward:\nNew information option on \"information->machines->blueprint production\"\nNew information option on \"information->blueprint reciepes\"\nNew challenge \"produce blueprint for frame\"\n\n")
                    self.machineChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.blueprintChallengeDone:
                foundBluePrint = False
                for item in self.character.inventory + self.room.itemsOnFloor:
                    if isinstance(item,src.items.BluePrint) and item.endProduct == "Frame":
                        foundBluePrint = True
                if not foundBluePrint:
                    self.submenue = interaction.TextMenu("\n\nchallenge: produce blueprint for frame\nstatus: challenge in progress - Try again with a blueprint for frame in your inventory.\n\ncomment: \ncheck \"information->machines->blueprint production\" on how to produce blueprints.\nThe reciepe for Frame is rod+metalbar\n\n")
                else:
                    self.knownBlueprints.append("Bolt")
                    self.knownBlueprints.append("Sheet")
                    self.submenue = interaction.TextMenu("\n\nchallenge: produce blueprint for frame\nstatus: challenge completed.\n\nreward:\nNew information option on \"information->automation\"\nNew blueprint reciepe for bolt\nNew blueprint reciepe for sheet\nNew challenge \"create command\"\n\n")
                    self.blueprintChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.commandChallengeDone:
                if not self.checkInInventory(src.items.Command + self.room.itemsOnFloor):
                    self.submenue = interaction.TextMenu("\n\nchallenge: create command\nstatus: challenge in progress - Try again with a command in your inventory.\n\ncomment: \ncheck \"information->automation->command creation\" on how to record commands.\n\n")
                else:
                    self.knownBlueprints.append("Stripe")
                    self.knownBlueprints.append("Mount")
                    self.knownBlueprints.append("Radiator")
                    self.submenue = interaction.TextMenu("\n\nchallenge completed.\n\nreward:\nNew information option on \"information->automation->multiplier\"\n\nreward:\nNew blueprint reciepe for stripe.\nNew blueprint reciepe for mount.\nNew blueprint reciepe for radiator.\nNew challenge \"repeat challenge\"\n\n")
                    self.commandChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.activateChallengeDone:
                if self.activateChallenge:
                    self.activateChallenge -= 1
                    if self.activateChallenge == 100:
                        self.submenue = interaction.TextMenu("\n\nchallenge: repeat challenge\nstatus: challenge in progress - Use this menu item a 100 times. The first step is done. Activations remaining %s"%(self.activateChallenge,))
                    else:
                        self.submenue = interaction.TextMenu("\n\nchallenge: repeat challenge\nstatus: challenge in progress - Use this menu item a 100 times. Activations remaining %s"%(self.activateChallenge,))
                else:
                    if len(self.character.inventory):
                        self.submenue = interaction.TextMenu("\n\nchallenge: repeat challenge\nstatus: in progress. Try again with empty inventory to complete.\n\n")
                    else:
                        self.submenue = interaction.TextMenu("\n\nchallenge: repeat challenge\nstatus: challenge completed.\n\ncomment:\nyou completed the first set of challenges\ncome back for more\n\nreward:\nNew blueprint reciepe for scrap compactor\nNew challenge \"produce scrap compactor\"\nNew challenge \"gather bloom\"\n\n")
                        self.activateChallengeDone = True
                        self.knownBlueprints.append("ScrapCompactor")
                        self.availableChallenges = {
                                    "produceScrapCompactors":{"text":"produce scrap compactor"},
                                    "gatherBloom":{"text":"gather bloom"},
                                    "note":{"text":"create note"},
                                   }
                self.character.macroState["submenue"] = self.submenue
        elif not self.challengeRun2Done:
                if len(self.availableChallenges):
                    options = []
                    for (key,value) in self.availableChallenges.items():
                        options.append([key,value["text"]])

                    self.submenue = interaction.SelectionMenu("select the challenge to do:",options)
                    self.character.macroState["submenue"] = self.submenue
                    self.character.macroState["submenue"].followUp = self.challengeRun2
                else:
                    if self.metalbarChallenge:

                        metalBarFound = None
                        for item in self.character.inventory:
                            if isinstance(item,src.items.MetalBars):
                                metalBarFound = item
                                break

                        if not metalBarFound:
                            self.submenue = interaction.TextMenu("\n\nchallenge: produce 100 metal bars\nstatus: no progress - Try again with metal bars in your inventory\nMetal bars remaining %s\n\n"%(self.metalbarChallenge,))
                            self.character.macroState["submenue"] = self.submenue
                            return

                        didAdd = self.addScraps(amount=1)
                        if not didAdd:
                            self.submenue = interaction.TextMenu("\n\nchallenge: produce 100 metal bars\nstatus: no progress - no space to drop scrap\nMetal bars remaining %s\n\n"%(self.metalbarChallenge,))
                            self.character.macroState["submenue"] = self.submenue
                            return

                        self.submenue = interaction.TextMenu("\n\nchallenge: produce 100 metal bars\nstatus: challenge in progress.\nMetal bars remaining %s\n\ncomment: \nscrap ejected to the south/below\nuse commands and multipliers to do this.\n\n"%(self.metalbarChallenge,))
                        self.character.inventory.remove(metalBarFound)
                        self.metalbarChallenge -= 1

                    else:
                        if len(self.character.inventory):
                            self.submenue = interaction.TextMenu("\n\nchallenge: produce 100 metal bars\nstatus: challenge in progress. Try again with empty inventory to complete.\n\n")
                        else:
                            self.submenue = interaction.TextMenu("\n\nchallenge: produce 100 metal bars\nstatus: challenge completed.\n\nreward:\nNew challenges added\nnew reciepes for Connector Pusher\n\n")
                            self.availableChallenges["differentBlueprints"] = {"text":"9 different blueprints"}
                            self.availableChallenges["9blooms"] = {"text":"9 blooms"}
                            self.availableChallenges["produceAdvanced"] = {"text":"produce items"}
                            self.availableChallenges["produceScraper"] = {"text":"scraper"}
                            self.challengeRun2Done = True
                            self.knownBlueprints.append("Connector")
                            self.knownBlueprints.append("Pusher")
                    self.character.macroState["submenue"] = self.submenue
        elif not self.challengeRun3Done:
            if len(self.availableChallenges):
                options = []
                for (key,value) in self.availableChallenges.items():
                    options.append([key,value["text"]])

                self.submenue = interaction.SelectionMenu("select the challenge",options)
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.challengeRun2
            else:
                if self.wallChallenge:
                    wallFound = None
                    for item in self.character.inventory:
                        if isinstance(item,src.items.Wall):
                            wallFound = item
                            break

                    if not wallFound:
                        self.submenue = interaction.TextMenu("\n\nchallenge: produce 25 walls\nstatus: challenge in progress.\nno progress - try again with walls in inventory\nWalls remaining: %s\n\ncomment:\nuse commands and multipliers to do this.\n\n"%(self.wallChallenge,))
                        self.character.macroState["submenue"] = self.submenue
                        return

                    didAdd = self.addScraps(amount=2)
                    if not didAdd:
                        self.submenue = interaction.TextMenu("\n\nchallenge: produce 25 walls\nstatus: challenge in progress.\nno progress - no space to drop scrap\nWalls remaining: %s\n\ncomment:\nuse commands and multipliers to do this.\n\n"%(self.wallChallenge,))
                        self.character.macroState["submenue"] = self.submenue
                        return

                    self.submenue = interaction.TextMenu("\n\nchallenge: produce 25 walls\nstatus: challenge in progress.\nWalls remaining: %s\n\ncomment:\nuse commands and multipliers to do this.\n\n"%(self.wallChallenge,))
                    self.character.inventory.remove(wallFound)
                    self.wallChallenge -= 1
                    self.character.macroState["submenue"] = self.submenue

                else:
                    if len(self.character.inventory):
                        self.submenue = interaction.TextMenu("\n\nchallenge: produce 25 walls\nstatus: challenge in progress. Try again with empty inventory to complete.\n\n")
                    else:
                        self.submenue = interaction.TextMenu("\n\nchallenge: produce 25 walls\nstatus: challenge completed\n\n")
                        self.availableChallenges["produceBioMasses"] = {"text":"produce 9 bio mass"}
                        self.availableChallenges["createMap"] = {"text":"create map"}
                        self.challengeRun3Done = True
                        self.knownBlueprints.append("RoomBuilder")
                        self.knownBlueprints.append("FloorPlate")
                    self.character.macroState["submenue"] = self.submenue
        elif not self.challengeRun4Done:
            if len(self.availableChallenges):
                options = []
                for (key,value) in self.availableChallenges.items():
                    options.append([key,value["text"]])

                self.submenue = interaction.SelectionMenu("select the challenge",options)
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.challengeRun2
            else:
                if not self.challengeInfo:
                    self.challengeInfo = {"current":"testWallCommand","testWallCommand":False,"testDoorCommand":False,"testFloorPlateCommand":False,"mainChallengeRunning":False,"mainQueue":[]}

                if self.challengeInfo["mainChallengeRunning"] and not self.challengeInfo["mainQueue"]:
                    if self.character.inventory:
                        self.submenue = interaction.TextMenu("\n\nactivate with empty inventory to complete challenge.\n\n")
                        self.character.macroState["submenue"] = self.submenue
                    else:
                        self.submenue = interaction.TextMenu("\n\nchallenge completed.\n\n")
                        self.character.macroState["submenue"] = self.submenue
                        self.challengeRun4Done = True

                        self.challengeInfo = {"challengerGiven":[]}

                        self.availableChallenges["produceAutoScribe"] = {"text":"produce auto scribe"}
                        self.availableChallenges["produceFilledGooDispenser"] = {"text":"produce goo"}
                        self.availableChallenges["gatherSickBloom"] = {"text":"gather sick bloom"}
                    return

                options = []
                options.append(["deliverProduct","deliver the product"])
                options.append(["doChallenge","do the challenge"])
                options.append(["setWallCommand","set command for wall"])
                options.append(["testWallCommand","test command for wall"])
                options.append(["setDoorCommand","set command for door"])
                options.append(["testDoorCommand","test command for door"])
                options.append(["setFloorPlateCommand","set command for floor plate"])
                options.append(["testFloorPlateCommand","test command for floor plate"])

                self.submenue = interaction.SelectionMenu("This challenge has two phases:\n * creating commands for producing and delivering Walls, Door and Floorplates each\n * the Autotutor will make your run the commands to produce these items in a random order\n\nIf you set up your commands correctly, you will produce those items and complete the challenge.\n\nlast wall test: %s\nlast door test: %s\nlast floor plate: %s\n\nselect what you want to do:"%(self.challengeInfo["testWallCommand"],self.challengeInfo["testDoorCommand"],self.challengeInfo["testFloorPlateCommand"]),options)
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.challengeRun4FinalSelection
        elif not self.challengeRun5Done:
            if len(self.availableChallenges):
                options = []
                for (key,value) in self.availableChallenges.items():
                    options.append([key,value["text"]])

                self.submenue = interaction.SelectionMenu("select the challenge to do:",options)
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.challengeRun2
            else:
                numFlasksFound = 0
                for item in self.character.inventory:
                    if item.type == "GooFlask" and item.uses == 100:
                        numFlasksFound += 1

                if not numFlasksFound > 3:
                    self.submenue = interaction.TextMenu("\n\nchallenge: Produce 4 filled goo flasks. \nchallenge in progress. Try again with 4 goo flasks with 100 uses left in each in your inventory.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                else:
                    self.submenue = interaction.TextMenu("\n\nchallenge: Produce 4 filled goo flasks. \nchallenge completed.\n\nreward: Character spawned. Talk to it by pressing h and command it.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                    gooFlask1 = None
                    gooFlask2 = None
                    for item in reversed(self.character.inventory):
                        if item.type == "GooFlask" and item.uses == 100:
                            if gooFlask1 == None:
                                gooFlask1 = item
                            else:
                                gooFlask2 = item
                                break

                    self.character.inventory.remove(gooFlask2)
                    gooFlask1.uses = 0

                    # add character
                    name = "Erwin Lauterbach"
                    newCharacter = characters.Character(displayChars.staffCharactersByLetter[name[0].lower()],self.xPosition+1,self.yPosition,name=name,creator=self)

                    newCharacter.solvers = [
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

                    self.challengeRun5Done = True

                    self.room.addCharacter(newCharacter,self.xPosition,self.yPosition+1)
                    newCharacter.macroState["macros"]["j"] = "J"
                    newCharacter.inventory.append(gooFlask2)

        else:
            self.submenue = interaction.TextMenu("\n\nTBD\n\n")
            self.character.macroState["submenue"] = self.submenue

    def checkForOtherItem(self,itemType):
        if len(self.character.inventory) > 2:
            return True
        foundOtherItem = None
        for item in self.character.inventory:
            if not item.type in ["GooFlask",itemType]:
                foundOtherItem = item
                break
        if foundOtherItem:
            return True
        return False

    def getFromInventory(self,itemType):
        foundItem = None
        for item in self.character.inventory:
            if item.type in [itemType]:
                foundItem = item
                break
        return foundItem

    def challengeRun4FinalSelection(self):
        selection = self.submenue.getSelection()
        self.submenue = None

        if selection == "deliverProduct":
            currentChallenge = self.challengeInfo["current"]
            if currentChallenge == "doChallenge":
                item = self.challengeInfo["mainQueue"][0]
                if self.checkForOtherItem(item):
                    self.submenue = interaction.TextMenu("\n\nclear your inventory except the item and a goo flask.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                    self.challengeInfo["testWallCommand"] = "fail - inventory not clear/wrong item"
                    self.challengeInfo["mainChallengeRunning"] = False
                    return

                foundWall = self.getFromInventory(item)
                if not foundWall:
                    self.submenue = interaction.TextMenu("\n\ntry again with the item in your inventory.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                    self.challengeInfo["testWallCommand"] = "fail - item not in inventory/wrong item"
                    self.challengeInfo["mainChallengeRunning"] = False
                    return
                
                self.submenue = interaction.TextMenu("\n\nyou completed the test.\n\n")
                self.character.macroState["submenue"] = self.submenue
                self.character.inventory.remove(foundWall)
                self.challengeInfo["testWallCommand"] = "success - item delivered"

                self.challengeInfo["mainQueue"].remove(item)

                self.addScraps(amount=2)
            if currentChallenge == "testWallCommand":
                if self.checkForOtherItem("Wall"):
                    self.submenue = interaction.TextMenu("\n\nclear your inventory except for the wall and a goo flask.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                    self.challengeInfo["testWallCommand"] = "fail - inventory not clear"
                    return

                foundWall = self.getFromInventory("Wall")
                if not foundWall:
                    self.submenue = interaction.TextMenu("\n\ntry again with a wall in your inventory.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                    self.challengeInfo["testWallCommand"] = "fail - item not in inventory"
                    return
                
                self.submenue = interaction.TextMenu("\n\nyou completed the test.\n\n")
                self.character.macroState["submenue"] = self.submenue
                self.character.inventory.remove(foundWall)
                self.challengeInfo["testWallCommand"] = "success - item delivered"

                self.addScraps(amount=2)
            elif currentChallenge == "testDoorCommand":
                if self.checkForOtherItem("Door"):
                    self.submenue = interaction.TextMenu("\n\nclear your inventory except for the door and a goo flask.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                    self.challengeInfo["testDoorCommand"] = "fail - inventory not clear"
                    return

                foundDoor = self.getFromInventory("Door")
                if not foundDoor:
                    self.submenue = interaction.TextMenu("\n\ntry again with a door in your inventory.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                    self.challengeInfo["testDoorCommand"] = "fail - item not in inventory"
                    return
                
                self.submenue = interaction.TextMenu("\n\nyou completed the test.\n\n")
                self.character.macroState["submenue"] = self.submenue
                self.character.inventory.remove(foundDoor)
                self.challengeInfo["testDoorCommand"] = "success - item delivered"

                self.addScraps(amount=2)
            elif currentChallenge == "testFloorPlateCommand":
                if self.checkForOtherItem("FloorPlate"):
                    self.submenue = interaction.TextMenu("\n\nclear your inventory except for the floor plate and a goo flask.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                    self.challengeInfo["testFloorPlateCommand"] = "fail - inventory not clear"

                foundFloorplate = self.getFromInventory("FloorPlate")
                if not foundFloorplate:
                    self.submenue = interaction.TextMenu("\n\ntry again with a floor plate in your inventory.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                    self.challengeInfo["testFloorPlateCommand"] = "fail - item not in inventory"
                    return
                
                self.submenue = interaction.TextMenu("\n\nyou completed the test.\n\n")
                self.character.macroState["submenue"] = self.submenue
                self.character.inventory.remove(foundFloorplate)
                self.challengeInfo["testFloorPlateCommand"] = "success - item delivered"

                self.addScraps(amount=2)
            else:
                self.submenue = interaction.TextMenu("\n\nno item requested at the moment.\n\n")
                
            self.character.macroState["submenue"] = self.submenue
            return

        elif selection == "doChallenge":
            self.challengeInfo["mainQueue"] = []
            for i in range(0,25):

                import random
                selected = random.choice("Wall","Door","FloorPlate")

                if selected == "Wall":
                    self.challengeInfo["mainQueue"].insert(0,"Wall")
                    convertedCommand = []
                    for char in self.challengeInfo["wallCommand"]:
                        convertedCommand.append((char,[]))
                    self.challengeInfo["current"] = "doChallenge"
                    self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]

                elif selected == "Door":
                    self.challengeInfo["mainQueue"].insert(0,"Door")
                    convertedCommand = []
                    for char in self.challengeInfo["doorCommand"]:
                        convertedCommand.append((char,[]))
                    self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]

                elif selected == "FloorPlate":
                    self.challengeInfo["mainQueue"].insert(0,"FloorPlate")
                    convertedCommand = []
                    for char in self.challengeInfo["floorPlateCommand"]:
                        convertedCommand.append((char,[]))
                    self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]
                
            self.challengeInfo["mainChallengeRunning"] = True
            return

        elif selection == "setWallCommand":
            foundCommands = []
            for item in self.character.inventory:
                if item.type == "Command":
                    foundCommands.append(item)

            if not foundCommands:
                self.submenue = interaction.TextMenu("\n\nno command found\n\n")
                self.character.macroState["submenue"] = self.submenue
                return

            if len(foundCommands) > 1:
                self.submenue = interaction.TextMenu("\n\nmore than one command found\n\n")
                self.character.macroState["submenue"] = self.submenue
                return

            self.challengeInfo["wallCommand"] = foundCommands[0].command
            self.submenue = interaction.TextMenu("\n\nloaded command for producing wall.\n\nremember to include delivering the product.\n\ncommand: %s\n\n"%(str(self.challengeInfo["wallCommand"])))
            self.character.macroState["submenue"] = self.submenue
            return
                
        elif selection == "testWallCommand":
            convertedCommand = []
            for char in self.challengeInfo["wallCommand"]:
                convertedCommand.append((char,[]))
            self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]
            self.challengeInfo["current"] = "testWallCommand"
            self.challengeInfo["testWallCommand"] = "started - not returned"
            return
        elif selection == "setDoorCommand":
            foundCommands = []
            for item in self.character.inventory:
                if item.type == "Command":
                    foundCommands.append(item)

            if not foundCommands:
                self.submenue = interaction.TextMenu("\n\nno command found\n\n")
                self.character.macroState["submenue"] = self.submenue
                return

            if len(foundCommands) > 1:
                self.submenue = interaction.TextMenu("\n\nmore than one command found\n\n")
                self.character.macroState["submenue"] = self.submenue
                return

            self.challengeInfo["doorCommand"] = foundCommands[0].command
            self.submenue = interaction.TextMenu("\n\nloaded command for producing door.\n\nremember to include delivering the product.\n\ncommand: %s\n\n"%(str(self.challengeInfo["doorCommand"])))
            self.character.macroState["submenue"] = self.submenue
            return
        elif selection == "testDoorCommand":
            convertedCommand = []
            for char in self.challengeInfo["doorCommand"]:
                convertedCommand.append((char,[]))
            self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]
            self.challengeInfo["current"] = "testDoorCommand"
            self.challengeInfo["testWallCommand"] = "started - not returned"
            return
        elif selection == "setFloorPlateCommand":
            foundCommands = []
            for item in self.character.inventory:
                if item.type == "Command":
                    foundCommands.append(item)

            if not foundCommands:
                self.submenue = interaction.TextMenu("\n\nno command found\n\n")
                self.character.macroState["submenue"] = self.submenue
                return

            if len(foundCommands) > 1:
                self.submenue = interaction.TextMenu("\n\nmore than one command found\n\n")
                self.character.macroState["submenue"] = self.submenue
                return

            self.challengeInfo["floorPlateCommand"] = foundCommands[0].command
            self.submenue = interaction.TextMenu("\n\nloaded command for producing door.\n\nremember to include delivering the product.\n\ncommand: %s\n\n"%(str(self.challengeInfo["floorPlateCommand"])))
            self.character.macroState["submenue"] = self.submenue
            return
        elif selection == "testFloorPlateCommand":
            convertedCommand = []
            for char in self.challengeInfo["floorPlateCommand"]:
                convertedCommand.append((char,[]))
            self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]
            self.challengeInfo["current"] = "testFloorPlateCommand"
            self.challengeInfo["testFloorPlateCommand"] = "started - not returned"
            return

        self.submenue = interaction.TextMenu("\n\ninvalid option: %s\n\n"%(selection))
        self.character.macroState["submenue"] = self.submenue


    def challengeRun2(self):

        selection = self.submenue.getSelection()
        self.submenue = None

        #<=
            # 
        # Note
        # gatherBloom
            #R SporeExtractor
            #R Puller
            #I food/moldfarming
            # produceSporeExtractor
        # produceScrapCompactors
            #R Tank
            #R Scraper
            # produceBasics
                #R Case
                #R Wall
                # prodCase
                    #R Heater
        # => produce 100 metal bars

        if selection == "note": # from root
            if not self.checkInInventoryOrInRoom(src.items.Note):
                self.submenue = interaction.TextMenu("\n\nchallenge: write note\nstatus: challenge in progress - Try again with a note in your inventory.\n\ncomment:\n check \"information->items->notes\" on how to create notes.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: write note\nstatus: challenge completed.\n\nreward:\nnew Information option on \"Information->automation->maps\"\n\n")
                del self.availableChallenges["note"]

        elif selection == "gatherBloom": # from root
            if not self.checkInInventoryOrInRoom(src.items.Bloom):
                self.submenue = interaction.TextMenu("\n\nchallenge: gather bloom\nstatus: challenge in progress - Try again with a bloom in your inventory.\n\ncomment: \nBlooms are represented by ** and are white.\n\n")
            else:
                del self.availableChallenges["gatherBloom"]
                self.availableChallenges["produceSporeExtractor"] = {"text":"produce a Spore Extractor"}
                self.knownBlueprints.append("SporeExtractor")
                self.knownBlueprints.append("Puller")
                self.knownInfos.append("food/moldfarming")
                blooms = []
                for i in range(0,4):
                    new = itemMap["MoldSpore"](creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition+1
                    blooms.append(new)
                self.container.addItems(blooms)
                self.submenue = interaction.TextMenu("\n\nchallenge: gather bloom\nstatus: challenge completed.\n\nreward:\nchallenge \"produce a Spore Extractor\" added\nmold spores added to south/below\nnew Information option on \"information->food->mold farming\"\nNew blueprint reciepes for Tank + Puller\n\n")

        elif selection == "produceSporeExtractor": # from gatherBloom
            if not self.checkInInventoryOrInRoom(src.items.SporeExtractor):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce spore extractor\nstatus: challenge in progress - try again with spore extractor in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce spore extractor\nstatus: challenge completed.\n\n")
                del self.availableChallenges["produceSporeExtractor"]

        elif selection == "produceScrapCompactors": # from root
            if not self.checkInInventory(src.items.ScrapCompactor):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce scrap compactor\nstatus: challenge in progress - try again with scrap compactor in your inventory.\n\n")
            else:
                self.knownBlueprints.append("Tank")
                self.knownBlueprints.append("Scraper")
                self.availableChallenges["produceBasics"] = {"text":"produce basics"}
                self.submenue = interaction.TextMenu("\n\nchallenge: produce scrap compactor\nstatus: challenge completed.\n\nreward:\nchallenge \"%s\" added\nNew blueprint reciepes for Tank, Scraper\n\n"%(self.availableChallenges["produceBasics"]["text"]))
                del self.availableChallenges["produceScrapCompactors"]

        elif selection == "produceBasics": # from produceScrapCompactors
            if self.checkListAgainstInventoryOrIsRoom(["Rod","Bolt","Stripe","Mount","Radiator","Sheet"]):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce basics\nstatus: challenge in progress. Try again with rod + bolt + stripe + mount + radiator + sheet in your inventory.\n\ncomment:\nThe blueprints required should be in this room.\n\n")
            else:
                del self.availableChallenges["produceBasics"]
                self.knownBlueprints.append("Case")
                self.knownBlueprints.append("Wall")
                self.availableChallenges["prodCase"] = {"text":"produce case"}
                self.submenue = interaction.TextMenu("\n\nchallenge: produce basics\nstatus: challenge completed.\n\nreward:\nchallenge \"%s\" added\nNew blueprint reciepes for Case, Wall\n"%(self.availableChallenges["prodCase"]["text"]))

        elif selection == "prodCase": # from produceBasics
            if not self.checkInInventoryOrInRoom(src.items.Case):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce case\nstatus: challenge in progress - Try again with a case in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce case\nstatus: challenge completed.\n\n")
                self.knownBlueprints.append("Heater")
                del self.availableChallenges["prodCase"]


        #<=
            #R Connector
            #R Pusher
        # differentBlueprints
        # 9blooms
            #R BloomShredder
            # processedBloom
        # produceAdvanced
            # produceWall
                #R Door
                # produceDoor
                    #R FloorPlate
                    # produceFloorPlate
        # produceScraper

        #=> 25 walls

        elif selection == "differentBlueprints": # from root2
            blueprints = []
            for item in self.character.inventory + self.room.itemsOnFloor:
                if isinstance(item,src.items.BluePrint) and not item.endProduct in blueprints:
                    blueprints.append(item.endProduct)
            if not len(blueprints) > 8:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce 9 different blueprint\nstatus: challenge in progress - try again with 9 different blueprints in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce 9 different blueprint\nstatus: challenge completed.\n\n")
                del self.availableChallenges["differentBlueprints"]

        elif selection == "9blooms": # from root2
            if self.countInInventoryOrRoom(src.items.Bloom) < 9:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather 9 blooms\nstatus: failed. Try with 9 bloom in your inventory.\n\n")
            else:
                self.availableChallenges["processedBloom"] = {"text":"process bloom"}
                self.knownBlueprints.append("BloomShredder")
                self.submenue = interaction.TextMenu("\n\nchallenge completed.\n\nchallenge %s added\n\n"%(self.availableChallenges["processedBloom"]["text"]))
                del self.availableChallenges["9blooms"]

        elif selection == "processedBloom": # from 9blooms
            if not self.checkInInventoryOrInRoom(src.items.BioMass):
                self.submenue = interaction.TextMenu("\n\nchallenge: process bloom\nstatus: challenge in progress - try with bio mass in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: process bloom\nstatus: challenge completed.\n\n")
                del self.availableChallenges["processedBloom"]

        elif selection == "produceAdvanced": # from root2
            if self.checkListAgainstInventoryOrIsRoom(["Tank","Heater","Connector","pusher","puller","Frame"]):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge in progress - try again with tank + heater + connector + pusher + puller + frame in your inventory.\n\n")
            else:
                del self.availableChallenges["produceAdvanced"]
                self.submenue = interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge completed.\n\n")

        elif selection == "produceWall": # from produceAdvanced
            if not self.checkInInventoryOrInRoom(src.items.Wall):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge in progress - try again with wall in your inventory.\n\nreward: new blueprint reciepe for door\n\n")
            else:
                del self.availableChallenges["produceWall"]
                self.knownBlueprints.append("Door")
                self.submenue = interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge completed.\n\n")

        elif selection == "produceDoor": # from produceWall
            if not self.checkInInventoryOrInRoom(src.items.Door):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge in progress - try again with door in your inventory.\n\nreward:\n* new blueprint reciepe for floor plate\n\n")
            else:
                del self.availableChallenges["produceDoor"]
                self.knownBlueprints.append("FloorPlate")
                self.submenue = interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge completed.\n\n")

        elif selection == "produceFloorPlate": # from produceDoor
            if not self.checkInInventoryOrInRoom(src.items.FloorPlate):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge in progress - try again with floor plate in your inventory.\n\n")
            else:
                del self.availableChallenges["produceFloorPlate"]
                self.submenue = interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge completed.\n\n")

        elif selection == "produceScraper": # from root2
            if not self.checkInInventoryOrInRoom(src.items.Scraper):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce scraper\nstatus: challenge in progress. Try with scraper in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce scraper\nstatus: challenge completed.\n\n")
                del self.availableChallenges["produceScraper"]


        #<=
            #R RoomBuilder
            #R FloorPlate
        # produceBioMasses
            #R BioPress
            # processBioMass
                # producePressCakes
                    #R GooDispenser
                    #R GooFlask
                # buildGooProducer
                #R GooProducer
        # createMap
            # createMapWithPaths

        #=> produce random door/wall/floorplate things

        elif selection == "produceBioMasses": # from root3
            if self.countInInventoryOrRoom(src.items.BioMass) < 9:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce 9 Biomass\nstatus: challenge in progress. Try with 9 BioMass in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce 9 Biomass\nstatus: challenge completed.\n\n")
                self.availableChallenges["processBioMass"] = {"text":"process bio mass"}
                self.knownBlueprints.append("BioPress")
                del self.availableChallenges["produceBioMasses"]

        elif selection == "processBioMass": # from produceBioMasses
            if not self.checkInInventoryOrInRoom(src.items.PressCake):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce press cake\nstatus: challenge in progress. Try with Press cake in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce press cake\nstatus: challenge completed.\n\n")
                self.availableChallenges["producePressCakes"] = {"text":"produce press cakes"}
                self.availableChallenges["buildGooProducer"] = {"text":"build goo producer"}
                self.knownBlueprints.append("GooProducer")
                del self.availableChallenges["processBioMass"]

        elif selection == "producePressCakes": # from processBioMass
            if self.countInInventoryOrRoom(src.items.PressCake) < 4:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce press cakes\nstatus: challenge in progress. Try with 4 press cake in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce press cake\nstatus: challenge completed.\n\n")
                del self.availableChallenges["producePressCakes"]

                self.knownBlueprints.append("GooDispenser")
                self.knownBlueprints.append("GooFlask")

        elif selection == "buildGooProducer": # from processBioMass
            if not self.checkInInventoryOrInRoom(src.items.GooProducer):
                self.submenue = interaction.TextMenu("\n\nchallenge: build goo producer\nstatus: challenge in progress. Try with goo producer in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: build goo producer\nstatus: challenge completed.\n\n")
                del self.availableChallenges["buildGooProducer"]

        elif selection == "createMap": # from root3
            if not self.checkInInventoryOrInRoom(src.items.Map):
                self.submenue = interaction.TextMenu("\n\nchallenge: create map\nstatus: challenge in progress. Try with map in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: create map\nstatus: challenge completed.\n\n")
                self.availableChallenges["createMapWithPaths"] = {"text":"create map with routes"}
                del self.availableChallenges["createMap"]

        elif selection == "createMapWithPaths": # from createMap
            itemFound = False
            for item in self.character.inventory + self.room.itemsOnFloor:
                if isinstance(item,src.items.Map) and item.routes:
                    itemFound = True
                    break
            if not itemFound:
                self.submenue = interaction.TextMenu("\n\nchallenge: create map with paths\nstatus: challenge in progress. Try with map with paths in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: create map with paths\nstatus: challenge completed.\n\n")
                del self.availableChallenges["createMapWithPaths"]

        #<=
        #- produceFilledGooDispenser
            #- > strengthen mold growth
            #- R Container
            #- R BloomContainer
            #- R GrowthTank
        #- autoScribe 
            #- > go to tile center
            #- copy commmand
                #- > decide inventory full
                #- > decide inventory empty
                #- > activate 4 directions
        #- gather sick bloom
            #- gather coal
                #- build fire crystals
            #- > go to food
            #- > decide food
            #- X tile completely covered in mold
                #- X tile with 9 living blooms
                    #- X tile with 3 living sick blooms
            #- X goto north west edge
                #- X goto north east edge
                    #- X goto south east edge
                        #- X goto south west edge
                        #- > go to west tile border
                        #- > go to north tile border
                        #- > go to east tile border
                        #- > go to south tile border
            #- gather 9 sick bloom

        # => proudce 3 goo flasks 

        elif selection == "produceFilledGooDispenser": # NOT ASSIGNED
            itemFound = False
            for item in self.character.inventory + self.room.itemsOnFloor:
                if isinstance(item,src.items.GooDispenser) and item.charges > 0:
                    itemFound = True
                    break
            if not itemFound:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce goo\nstatus: challenge in progress. Try again with a goo dispenser with at least one charge in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce goo\nstatus: challenge completed.\n\nreward:\nNew Blueprint reciepe for growth tank\nCommand \"STIMULATE MOLD GROWTh\" dropped to the south\n\n")

                self.knownBlueprints.append("GrowthTank")
                self.knownBlueprints.append("Container")
                self.knownBlueprints.append("BloomContainer")

                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","x","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d",
                                       "a","j","a","j",
                                       "w","j","w","j","w","j","w","j","o","p","x","$","=","s","s",
                                       "s","j","s","j","s","j","s","j","o","p","x","$","=","w","w",
                                       "a","j","a","j",
                                       "w","j","w","j","w","j","w","j","o","p","x","$","=","s","s",
                                       "s","j","s","j","s","j","s","j","o","p","x","$","=","w","w",
                                       "$","=","d","d",
                                       "w","j","w","j","w","j","w","j","o","p","x","$","=","s","s",
                                       "s","j","s","j","s","j","s","j","o","p","x","$","=","w","w",
                                       "d","j","d","j",
                                       "w","j","w","j","w","j","w","j","o","p","x","$","=","s","s",
                                       "s","j","s","j","s","j","s","j","o","p","x","$","=","w","w",
                                       "d","j","d","j",
                                       "w","j","w","j","w","j","w","j","o","p","x","$","=","s","s",
                                       "s","j","s","j","s","j","s","j","o","p","x","$","=","w","w",
                                       "$","=","a","a"])
                newCommand.extraName = "STIMULATE MOLD GROWTh"
                newCommand.description = "using this command will make you move around and pick mold to make it grow.\nIf there are things lying around they might be activated."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                del self.availableChallenges["produceFilledGooDispenser"]

        elif selection == "produceAutoScribe": # from root 4
            if not self.checkInInventoryOrInRoom(src.items.AutoScribe):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce auto scribe\nstatus: challenge in progress. Try with auto scribe in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce auto scribe\nstatus: challenge completed.\nreward: \"GO TO TILE CENTEr\" command dropped to south/below\n\n")
                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","x","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"])
                newCommand.extraName = "GO TO TILE CENTEr"
                newCommand.description = "using this command will make you move to the center of the tile. If the path is blocked the command will not work properly."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])
                self.availableChallenges["copyCommand"] = {"text":"copy command"}
                del self.availableChallenges["produceAutoScribe"]

        elif selection == "copyCommand": # from produceAutoScribe
            itemCount = 0
            for item in self.character.inventory + self.room.itemsOnFloor:
                if isinstance(item,src.items.Command) and item.command == ["o","p","x","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"]:
                    itemCount += 1

            if not itemCount > 2:
                self.submenue = interaction.TextMenu("\n\nchallenge: copy command\nstatus: challenge in progress. Try again with 3 copies of the \"GO TO TILE CENTEr\" command\n\ncomment:\nuse the auto scribe to copy commands.\nthe \"GO TO TILE CENTEr\" command was dropped as reward for the \"produce auto scribe\" challenge.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce auto scribe\nstatus: challenge completed.\n\n")

                newCommand = Command(creator=self)
                newCommand.setPayload(["%","i","a","d"])
                newCommand.extraName = "DECIDE INVENTORY EMPTY EAST WESt"
                newCommand.description = "using this command will make you move west in case your inventory is empty and will move you east otherwise"
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["%","I","a","d"])
                newCommand.extraName = "DECIDE INVENTORY FULL EAST WESt"
                newCommand.description = "using this command will make you move west in case your inventory is completely filled and will move you east otherwise"
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["w","%","b","d","s"])
                newCommand.extraName = "DECIDE NORTH BLOCKED EAST STAy"
                newCommand.description = "using this command will make you move east in case the field to the north is not walkable and will make you stay in place otherwise"
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])
        
                newCommand = Command(creator=self)
                newCommand.setPayload(["w","j"])
                newCommand.extraName = "ACTIVATE NORTh"
                newCommand.description = "using this command will make you activate to the north."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["s","j"])
                newCommand.extraName = "ACTIVATE SOUTh"
                newCommand.description = "using this command will make you activate to the south."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["d","j"])
                newCommand.extraName = "ACTIVATE EASt"
                newCommand.description = "using this command will make you activate to the east."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["a","j"])
                newCommand.extraName = "ACTIVATE WESt"
                newCommand.description = "using this command will make you activate to the west."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                del self.availableChallenges["copyCommand"]
        
        # copy command
        elif selection == "gatherSickBloom": # from root 4
            if not self.checkInInventoryOrInRoom(src.items.SickBloom):
                self.submenue = interaction.TextMenu("\n\nchallenge: gather sick bloom\nstatus: challenge in progress. Try with sick bloom in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather sick bloom\nstatus: challenge completed.\n\n")
                self.availableChallenges["gatherCoal"] = {"text":"gather coal"}
                self.availableChallenges["challengerExplore1"] = {"text":"explore mold"}
                self.availableChallenges["challengerGoTo1"] = {"text":"explore terrain"}
                self.availableChallenges["gatherSickBlooms"] = {"text":"gather sick blooms"}

                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","f","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"])
                newCommand.extraName = "GOTO FOOd"
                newCommand.description = "using this command will make you go to a food source nearby."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1

                newCommand = Command(creator=self)
                newCommand.setPayload(["%","F","a","d"])
                newCommand.extraName = "DECIDE FOOD NEARBY WEST EASt"
                newCommand.description = "using this command will make you go west in case there is a food source nearby and to the east otherwise."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1

                self.container.addItems([newCommand])

                del self.availableChallenges["gatherSickBloom"]

        elif selection == "gatherCoal": # from gatherSickBloom
            if not self.checkInInventoryOrInRoom(src.items.Coal):
                self.submenue = interaction.TextMenu("\n\nchallenge: gather coal\nstatus: challenge in progress. Try with coal in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather coal\nstatus: challenge completed.\n\n")
                self.availableChallenges["produceFireCrystals"] = {"text":"produce fire crystals"}
                self.knownBlueprints.append("FireCrystals")

                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","C","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"])
                newCommand.extraName = "GOTO FOOd"
                newCommand.description = "using this command will make you go to a food source nearby."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1

                newCommand = Command(creator=self)
                newCommand.setPayload(["%","F","a","d"])
                newCommand.extraName = "DECIDE FOOD NEARBY WEST EASt"
                newCommand.description = "using this command will make you go west in case there is a food source nearby and to the east otherwise."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1

                del self.availableChallenges["gatherCoal"]

        elif selection == "produceFireCrystals": # from gatherCoal
            if not self.checkInInventoryOrInRoom(src.items.FireCrystals):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce fire crystals\nstatus: challenge in progress. Try with fire crystals in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce fire crystals\nstatus: challenge completed.\n\n")
                del self.availableChallenges["produceFireCrystals"]

        elif selection == "gatherSickBlooms": # from gatherSickBloom
            if self.countInInventoryOrRoom(src.items.SickBloom) < 9:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather sick blooms\nstatus: challenge in progress. Try with 9 sick blooms in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather sick blooms\nstatus: challenge completed.\n\n")
                del self.availableChallenges["gatherSickBlooms"]

        elif selection == "challengerExplore1": # from gatherSickBloom
            secret = "epxplore1:-)"
            if not "explore" in self.challengeInfo["challengerGiven"]:
                new = PortableChallenger(creator=self)
                new.xPosition = self.xPosition
                new.yPosition = self.yPosition+1
                new.secret = secret
                new.challenges = ["3livingSickBlooms","9livingBlooms","fullMoldCover"]
                self.submenue = interaction.TextMenu("\n\nchallenge: explore mold\nstatus: challenge in progress. A portable challanger was outputted to the south. \nUse it and complete its challenges. Return afterwards.\n\ncomment: do not loose or destroy the challenger\n\n")
                self.challengeInfo["challengerGiven"].append("explore")
                self.container.addItems([new])
            else:
                itemFound = None
                for item in self.character.inventory + self.room.itemsOnFloor:
                    if item.type == "PortableChallenger" and item.done and item.secret == secret:
                        itemFound = item

                if not itemFound:
                    self.submenue = interaction.TextMenu("\n\nchallenge: explore mold\nstatus: challenge in progress. \nUse the portable challenger and complete its challenges.\nTry again with the completed portable challenger in you inventory.\n\n")
                else:
                    self.submenue = interaction.TextMenu("\n\nchallenge: explore mold\nstatus: challenge completed.\n\n")
                    self.character.inventory.remove(itemFound)
                    del self.availableChallenges["challengerExplore1"]
        elif selection == "challengerGoTo1": # from gatherSickBloom
            secret = "goto1:-)"
            if not "goto" in self.challengeInfo["challengerGiven"]:
                new = PortableChallenger(creator=self)
                new.xPosition = self.xPosition
                new.yPosition = self.yPosition+1
                new.secret = secret
                new.challenges = ["gotoWestSouthTile","gotoEastSouthTile","gotoEastNorthTile","gotoWestNorthTile"]
                self.container.addItems([new])

                self.submenue = interaction.TextMenu("\n\nchallenge: explore terrain\nstatus: challenge in progress. A portable challanger was outputted to the south. \nUse it and complete its challenges. Return afterwards.\n\n")
                self.challengeInfo["challengerGiven"].append("goto")
            else:
                itemFound = None
                for item in self.character.inventory + self.room.itemsOnFloor:
                    if item.type == "PortableChallenger" and item.done and item.secret == secret:
                        itemFound = item

                if not itemFound:
                    self.submenue = interaction.TextMenu("\n\nchallenge: explore terrain\nstatus: challenge in progress. \nUse the portable challenger and complete its challenges.\nTry again with the completed portable challenger in you inventory.\n\n")
                else:
                    self.submenue = interaction.TextMenu("\n\nchallenge: explore terrain\nstatus: challenge completed.\n\n")
                    self.character.inventory.remove(itemFound)
                    del self.availableChallenges["challengerGoTo1"]

                    newCommand = Command(creator=self)
                    newCommand.setPayload(["@","$","=","S","E","L","F","x","a"])
                    newCommand.extraName = "GOTO WEST BORDEr"
                    newCommand.description = "using this command will make you go the west tile edge."
                    newCommand.xPosition = self.xPosition
                    newCommand.yPosition = self.yPosition+1

                    newCommand = Command(creator=self)
                    newCommand.setPayload(["$",">","x","$","x","=","1","4","@","$","x","-","S","E","L","F","x","$","=","x","a","<","x"])
                    newCommand.extraName = "GOTO EAST BORDEr"
                    newCommand.description = "using this command will make you go the east tile edge."
                    newCommand.xPosition = self.xPosition
                    newCommand.yPosition = self.yPosition+1

                    newCommand = Command(creator=self)
                    newCommand.setPayload(["@","$","=","S","E","L","F","y","w"])
                    newCommand.extraName = "GOTO NORTH BORDEr"
                    newCommand.description = "using this command will make you go the north tile edge."
                    newCommand.xPosition = self.xPosition
                    newCommand.yPosition = self.yPosition+1

                    newCommand = Command(creator=self)
                    newCommand.setPayload(["$",">","y","$","y","=","1","4","@","$","y","-","S","E","L","F","y","$","=","y","s","<","y"])
                    newCommand.extraName = "GOTO SOUTH BORDEr"
                    newCommand.description = "using this command will make you go the south tile edge."
                    newCommand.xPosition = self.xPosition
                    newCommand.yPosition = self.yPosition+1

        # build room
        # build map to room
        # goto map center
        # build working map (drop marker in 5 rooms with requirement, make random star movement)
        # tile with 9 living sick blooms
        # gather posion bloom
        #X clear tile x/y
            #> floor right empty
            # build room
        # upgrade BloomContainer 3
        # upgrade Sheet to 4
        # upgrade Machine
        #(=> produce goo flask with >100 charges)
        #(=> build mini mech)

        #- build growth tank
            #- build NPC
                #> go to scrap
                #> go to character
                #- gather corpse
                    #> go to corpse
                    #> decide corpse
        # build item upgrader
            # upgrade Command to 4
        # memory cell
            # learn command
        # => learn 25 commands 

        elif selection == "produceMemoryCell": # from root 4
            if self.countInInventoryOrRoom(src.items.MemoryCell) < 9:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather sick blooms\nstatus: challenge in progress. Try with 9 sick blooms in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather sick blooms\nstatus: challenge completed.\n\n")
                del self.availableChallenges["gatherSickBlooms"]


        elif selection == "produceFloorPlates": # from produceRoomBuilder
            if self.countInInventoryOrRoom(src.items.FloorPlate) < 9:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce floor plates\nstatus: challenge in progress. Try with 9 floor plates in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce floor plates\nstatus: challenge completed.\n\n")
                del self.availableChallenges["produceFloorPlates"]


        elif selection == "produceRoomBuilder": # from root4
            if not self.checkInInventoryOrInRoom(src.items.RoomBuilder):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce room builder\nstatus: challenge in progress. Try with room builder in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce room builder\nstatus: challenge completed.\n\n")
                self.availableChallenges["produceFloorPlates"] = {"text":"produce floor plates"}
                del self.availableChallenges["produceRoomBuilder"]


        elif selection == "gatherPoisonBloom": # NOT ASSIGNED
            if self.countInInventoryOrRoom(src.items.PoisonBloom) < 9:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather poison bloom\nstatus: challenge in progress. Try with poison bloom in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather poison bloom\nstatus: challenge completed.\n\n")
                self.availableChallenges["gatherPoisonBlooms"] = {"text":"gather poison blooms"}
                del self.availableChallenges["gatherPoisonBloom"]

        elif selection == "gatherPoisonBlooms": # from gatherPoisonBloom
            if self.countInInventoryOrRoom(src.items.PoisonBloom) < 5:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather poison bloom\nstatus: challenge in progress. Try with 5 poison blooms in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather poison bloom\nstatus: challenge completed.\n\n")
                del self.availableChallenges["gatherPoisonBlooms"]

        elif selection == "produceGrowthTank": # NOT ASSIGNED
            if not self.checkInInventoryOrInRoom(src.items.GrowthTank):
                self.submenue = interaction.TextMenu("\n\nchallenge: produce growth tank\nstatus: challenge in progress. Try with growth tank in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: produce growth tank\nstatus: challenge completed.\n\n")
                self.availableChallenges["spawnNPC"] = {"text":"spawn NPC"}
                del self.availableChallenges["produceGrowthTank"]

        elif selection == "spawnNPC": # from produceGrowthTank
            if len(self.room.characters) < 2:
                self.submenue = interaction.TextMenu("\n\nchallenge: spawn NPC\nstatus: challenge in progress. Try with a NPC in the room.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: spawn NPC\nstatus: challenge completed.\n\n")

        elif selection == "gatherCorpse": # from spawnNPC
            if not self.checkInInventoryOrInRoom(src.items.Corpse):
                self.submenue = interaction.TextMenu("\n\nchallenge: gather corpse\nstatus: challenge in progress. Try with corpse in your inventory.\n\n")
            else:
                self.submenue = interaction.TextMenu("\n\nchallenge: gather corpse\nstatus: challenge completed.\n\n")
                
                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","M","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"])
                newCommand.extraName = "GOTO CORPSe"
                newCommand.description = "using this command will make you go to a corpse nearby."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1

                newCommand = Command(creator=self)
                newCommand.setPayload(["%","M","a","d"])
                newCommand.extraName = "DECIDE CORPSE NEARBY WEST EASt"
                newCommand.description = "using this command will make you go west in case there is a corpse nearby and to the east otherwise."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1

                del self.availableChallenges["gatherCorpse"]




        self.character.macroState["submenue"] = self.submenue


    def countInInventory(self,itemType):
        num = 0 
        for item in self.character.inventory:
            if isinstance(item,itemType):
                num += 1
        return num

    def countInInventoryOrRoom(self,itemType):
        num = self.countInInventory(itemType)
        for item in self.room.itemsOnFloor:
            if isinstance(item,itemType):
                num += 1
        return num

    def basicInfo(self):
        itemsLeft = ["Tank","Heater","Connector","pusher","puller","Frame"]

    def checkListAgainstInventory(self,itemTypes):
        for item in self.character.inventory:
            if item.type in itemTypes:
                itemTypes.remove(item.type)
        return itemTypes

    def checkListAgainstInventoryOrIsRoom(self,itemTypes):
        itemTypes = self.checkListAgainstInventory(itemType)
        if itemTypes:
            for item in self.room.itemsOnFloor:
                if item.type in itemTypes:
                    itemTypes.remove(item.type)
        return itemTypes

    def checkInInventory(self,itemType):
        for item in self.character.inventory:
            if isinstance(item,itemType):
                return True
        return False

    def checkInInventoryOrInRoom(self,itemType):
        if self.checkInInventory(itemType):
            return True
        for item in self.room.itemsOnFloor:
            if isinstance(item,itemType):
                return True

        return False

    def basicInfo(self):

        options = []

        options.append(("movement","movement"))
        options.append(("interaction","interaction"))

        if self.gooChallengeDone: 
            options.append(("machines","machines"))

        if self.gooChallengeDone: 
            options.append(("food","food"))

        if self.blueprintChallengeDone: 
            options.append(("automation","automation"))

        if self.machineChallengeDone: 
            options.append(("blueprints","blueprint reciepes"))

        self.submenue = interaction.SelectionMenu("select the information you need",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level1_selection

    def level1_selection(self):

        selection = self.submenue.getSelection()

        if selection == "movement":
            self.submenue = interaction.TextMenu("\n\n * press ? for help\n\n * press a to move left/west\n * press w to move up/north\n * press s to move down/south\n * press d to move right/east\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "interaction":
            self.submenue = interaction.TextMenu("\n\n * press k to pick up\n * press l to pick up\n * press i to view inventory\n * press @ to view your stats\n * press j to activate \n * press e to examine\n * press ? for help\n\nMove onto an item and press the key to interact with it. Move against big items and press the key to interact with it\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "machines":
            options = []

            options.append(("level1_machines_bars","metal bar production"))
            if self.metalbarChallengeDone:
                options.append(("level1_machines_simpleItem","simple item production"))
            if self.sheetChallengeDone:
                options.append(("level1_machines_machines","machine production"))
            if self.machineChallengeDone:
                options.append(("level1_machines_machineMachines","machine machine production"))
                options.append(("level1_machines_blueprints","blueprint production"))
                #options.append(("level1_machines_food","food production"))
                #options.append(("level1_machines_energy","energy production"))

            self.submenue = interaction.SelectionMenu("select the information you need",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stepLevel1Machines
        elif selection == "food":
            options = []

            options.append(("food_basics","food basics"))
            if "food/moldfarming" in self.knownInfos:
                options.append(("food_moldfarming","mold farming"))

            self.submenue = interaction.SelectionMenu("select the information you need",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stepLevel1Food
        elif selection == "automation":
            options = []

            options.append(("commands","creating commands"))
            if self.commandChallengeDone: 
                options.append(("multiplier","multiplier"))
            if self.activateChallengeDone:
                options.append(("notes","notes"))
            if self.blueprintChallengeDone:
                options.append(("maps","maps"))

            self.submenue = interaction.SelectionMenu("select the information you need",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stepLevel1Automation
        elif selection == "blueprints":
            text = "\n\nknown blueprint recieps:\n\n"

            shownText = False
            if "Rod" in self.knownBlueprints:
                text += " * rod             = rod\n"
                shownText = True
            if "Radiator" in self.knownBlueprints:
                text += " * radiator        = radiator\n"
                shownText = True
            if "Mount" in self.knownBlueprints:
                text += " * mount           = mount\n"
                shownText = True
            if "Stripe" in self.knownBlueprints:
                text += " * stripe          = stripe\n"
                shownText = True
            if "Bolt" in self.knownBlueprints:
                text += " * bolt            = bolt\n"
                shownText = True
            if "Sheet" in self.knownBlueprints:
                text += " * sheet           = sheet\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "Frame" in self.knownBlueprints:
                text += " * frame           = rod + metal bars\n"
                shownText = True
            if "Heater" in self.knownBlueprints:
                text += " * heater          = radiator + metal bars\n"
                shownText = True
            if "Connector" in self.knownBlueprints:
                text += " * connector       = mount + metal bars\n"
                shownText = True
            if "Pusher" in self.knownBlueprints:
                text += " * pusher          = stripe + metal bars\n"
                shownText = True
            if "Puller" in self.knownBlueprints:
                text += " * puller          = bolt + metal bars\n"
                shownText = True
            if "Tank" in self.knownBlueprints:
                text += " * tank            = sheet + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"
            
            shownText = False
            if "Case" in self.knownBlueprints:
                text += " * case            = frame + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "Wall" in self.knownBlueprints:
                text += " * wall            = metal bars\n"
                shownText = True
            if "Door" in self.knownBlueprints:
                text += " * door            = connector\n"
                shownText = True
            if "FloorPlate" in self.knownBlueprints:
                text += " * floor plate     = sheet + rod + bolt\n"
                shownText = True
            if "RoomBuilder" in self.knownBlueprints:
                text += " * room builder    = puller\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "BloomShredder" in self.knownBlueprints:
                text += " * bloom shredder  = bloom\n"
                shownText = True
            if "BioPress" in self.knownBlueprints:
                text += " * bio press       = bio mass\n"
                shownText = True
            if "GooFlask" in self.knownBlueprints:
                text += " * goo flask       = tank\n"
                shownText = True
            if "GooDispenser" in self.knownBlueprints:
                text += " * goo dispenser   = flask\n"
                shownText = True
            if "SporeExtractor" in self.knownBlueprints:
                text += " * spore extractor = bloom + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "GooProducer" in self.knownBlueprints:
                text += " * goo producer    = press cake\n"
                shownText = True
            if "GrowthTank" in self.knownBlueprints:
                text += " * growth tank     = goo flask\n"
                shownText = True
            if "FireCrystals" in self.knownBlueprints:
                text += " * fire crystals   = coal + sick bloom\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "ScrapCompactor" in self.knownBlueprints:
                text += " * scrap compactor = scrap\n"
                shownText = True
            if "Scraper" in self.knownBlueprints:
                text += " * scraper         = scrap + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "Container" in self.knownBlueprints:
                text += " * container       = case + sheet\n"
                shownText = True
            if "BloomContainer" in self.knownBlueprints:
                text += " * bloom container = case + sheet + bloom\n"
                shownText = True
            if shownText:
                text += "\n"

            text += "\n\n"
            self.submenue = interaction.TextMenu(text)
            self.character.macroState["submenue"] = self.submenue

    def stepLevel1Food(self):

        selection = self.submenue.getSelection()

        if selection == "food_basics":
            self.submenue = interaction.TextMenu("\n\nYou need to eat/drink regulary to not starve\nIf you do not drink for 1000 ticks you will starve,\n\nMost actions will take a tick. So you will need to drink every 1000 steps or you will starve.\n\nDrinking/Eating usually happens automatically as long as you have something eatable in you inventory.\n\nYou check your satiation in your character screen or on the lower right edge of the screen\n\nThe most common food is goo stored in a goo flask. Every sip from a goo flask gains you 1000 satiation.\nWith a maximum or 100 charges a full goo flask can hold enough food for up to 100000 moves.\n\n")
            self.character.macroState["submenue"] = self.submenue
        if selection == "food_moldfarming":
            self.submenue = interaction.TextMenu("\n\nMold is a basis for goo production and can be eaten directly.\nMold grows in patches and develop blooms.\nMold blooms can be collected and give 100 satiation when eaten or be processed into goo.\n\ngoo production:\n * Blooms can be processed into bio mass using the bloom shredder.\n * Bio mass can be processed into press cakes using the bio press.\n * press cake can be used to produce goo\n * The goo producer needs a goo dispenser to store the goo in.\n * The goodispenser allows you fill your flask.\n\nNew Mold patches can be started using mold spores. Growth in stagnant mold patches can be restarted by picking some sprouts or blooms\n\n")
            self.character.macroState["submenue"] = self.submenue

    def stepLevel1Automation(self):

        selection = self.submenue.getSelection()

        if selection == "commands":
            self.submenue = interaction.TextMenu("\n\nCommands are a way of automating actions. A character will run a command after activating it.\n\nThe easiest way of creating a command is:\n * drop a sheet on the floor\n * activate the sheet on the floor\n * select \"create a written command\"\n * select \"start recording\"\n * do the action\n * return to the sheet on the ground\n * activate the sheet again\n\nTo do the recorded action activate the command on the floor.\nWhile running the command you are not able the control your character and the game will speed up the longer the command runs.\n\nYou can press ctrl-d to abort running a commmand.")
            self.character.macroState["submenue"] = self.submenue
        if selection == "multiplier":
            self.submenue = interaction.TextMenu("\n\nThe multiplier allow to do something x times. For example walking 5 steps to the right, waiting 100 turns, activating commands 3 times\n\nTo use multiplier type in the number of times you want to do something and the action.\n\nexamples:\n\n5d => 5 steps to the right\n100. => wait a hundred turns\n3j => activating a command you are standing on 3 times\n\n")
            self.character.macroState["submenue"] = self.submenue
        if selection == "notes":
            self.submenue = interaction.TextMenu("\n\nNotes do not do anything except holding a text.\n\nYou can use this to place reminder on how things work and similar\n\nnotes can be created from sheets\n\n")
            self.character.macroState["submenue"] = self.submenue
        if selection == "maps":
            self.submenue = interaction.TextMenu("\n\nMaps allow for easier movement on a wider scale. Maps store routes between points.\n\nIf you are at the starting point of a route you can use the map to walk to the routes end point\nFor example if a map holds the route between point a and b you can use the map to travel to point b if you are at point a.\nMarking the startpoints of your routes is recomended, since you have stand at the exact coordinate to walk a route,\n\nYou create a route by: \n * moving to the start location of the route.\n * using the map\n * select the \"add route\" option\n * move to your target location\n * use the map again\n * select the \"add route\" option again.\n\nSince recording routes behaves like recording commands you can include actions like opening/closing doors or getting equipment.\nThe routes are not adapting to change and a closed door might disrupt your route.\n\n")
            self.character.macroState["submenue"] = self.submenue

    def stepLevel1Machines(self):

        selection = self.submenue.getSelection()

        if selection == "level1_machines_bars":
            self.submenue = interaction.TextMenu("\n\nMetal bars are used to produce most things. You can produce metal bars by using a scrap compactor.\nA scrap compactor is represented by RC. Place the scrap to the left/west of the scrap compactor.\nActivate it to produce a metal bar. The metal bar will be outputted to the right/east of the scrap compactor.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_simpleItem":
            self.submenue = interaction.TextMenu("\n\nMost items are produced in machines. A machine usually produces only one type of item.\nThese machines are shown as X\\. Place raw materials to the west/left/north/above of the machine and activate it to produce the item.\n\nYou can examine machines to get a more detailed descripton.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_food":
            self.submenue = interaction.TextMenu("\n\nFood production is based on vat maggots. Vat maggots can be harvested from trees.\nActivate the tree and a vat maggot will be dropped to the east of the tree.\n\nvat maggots are processed into bio mass using a maggot fermenter.\nPlace 10 vat maggots left/west to the maggot fermenter and activate it to produce 1 bio mass.\n\nThe bio mass is processed into press cake using a bio press.\nPlace 10 biomass left/west to the bio press and activate it to produce one press cake.\n\nThe press cake is processed into goo by a goo producer. Place 10 press cakes west/left to the goo producer and a goo dispenser to the right/east of the goo producer.\nActivate the goo producer to add a charge to the goo dispenser.\n\nIf the goo dispenser is charged, you can fill your flask by having it in your inventory and activating the goo dispenser.\n\n")
        elif selection == "level1_machines_machines":
            self.submenue = interaction.TextMenu("\n\nThe machines are produced by a machine-machine. The machine machines are shown as M\\\nMachine-machines require blueprints to produce machines.\n\nTo produce a machine for producing rods for example a blueprint for rods is required.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_blueprints":
            self.submenue = interaction.TextMenu("\n\nBlueprints are produced by a blueprinter.\nThe blueprinter takes items and a sheet as input and produces blueprints.\n\nDifferent items or combinations of items produce blueprints for different things.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_machineMachines":
            self.submenue = interaction.TextMenu("\n\nMachine-machines can only be produced by the production artwork. The production artwork is represented by ßß.\n\n")
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

    def getState(self):
        state = super().getState()
        state["availableChallenges"] = self.availableChallenges
        state["knownBlueprints"] = self.knownBlueprints
        state["knownInfos"] = self.knownInfos
        return state

    def getDiffState(self):
        state = super().getDiffState()
        state["availableChallenges"] = self.availableChallenges
        state["knownBlueprints"] = self.knownBlueprints
        state["knownInfos"] = self.knownInfos
        return state

    def setState(self,state):
        super().setState(state)
        self.availableChallenges = state["availableChallenges"]
        self.knownBlueprints = state["knownBlueprints"]
        self.knownInfos = state["knownInfos"]

    def getLongInfo(self):
        text = """

This machine hold the information and practices needed to build a base.

Activate/Apply it to complete challenges and gain more information.

"""
        return text

class PortableChallenger(Item):
    type = "PortableChallenger"

    def __init__(self,xPosition=None,yPosition=None, name="PortableChallenger",creator=None,noId=False):
        super().__init__(displayChars.simpleRunner,xPosition,yPosition,name=name,creator=creator)
        self.challenges = []
        self.done = False
        self.walkable = True
        self.bolted = False
        self.secret = ""

        self.attributesToStore.extend([
                "challenges","done","secret"])
        self.initialState = self.getState()

    def apply(self,character):
        super().apply(character,silent=True)

        if self.done:
            self.submenue = interaction.TextMenu("all challenges completed return to auto tutor")
        else:
            if self.challenges[-1] == "gotoEastNorthTile":
                if not (character.room == None and character.xPosition//15 == 13 and character.yPosition//15 == 1):
                    text = "challenge: go to the most east north tile\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition//15 < 13:
                        text += "go futher east\n"
                    if character.yPosition//15 > 1:
                        text += "go futher north\n"

                    self.submenue = interaction.TextMenu(text)
                else:
                    self.submenue = interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "gotoWestNorthTile":
                if not (character.room == None and character.xPosition//15 == 1 and character.yPosition//15 == 1):
                    text = "challenge: go to the most west north tile\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition//15 > 1:
                        text += "go futher west\n"
                    if character.yPosition//15 > 1:
                        text += "go futher north\n"

                    self.submenue = interaction.TextMenu(text)
                else:
                    self.submenue = interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "gotoWestSouthTile":
                if not (character.room == None and character.xPosition//15 == 1 and character.yPosition//15 == 13):
                    text = "challenge: go to the most west south\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition//15 > 1:
                        text += "go futher west\n"
                    if character.yPosition//15 < 13:
                        text += "go futher south\n"

                    self.submenue = interaction.TextMenu(text)
                else:
                    self.submenue = interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "gotoEastSouthTile":
                if not (character.room == None and character.xPosition//15 == 13 and character.yPosition//15 == 13):
                    text = "challenge: go to the most east south\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition//15 < 13:
                        text += "go futher east\n"
                    if character.yPosition//15 < 13:
                        text += "go futher south\n"

                    self.submenue = interaction.TextMenu(text)
                else:
                    self.submenue = interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "9livingBlooms":
                baseCoordinateX = character.xPosition-(character.xPosition%15)
                baseCoordinateY = character.yPosition-(character.yPosition%15)

                numFound = 0
                for extraX in range(1,14):
                    for extraY in range(1,14):
                        for item in character.container.getItemByPosition((baseCoordinateX+extraX,baseCoordinateY+extraY)):
                            if item.type == "Bloom" and item.dead == False:
                                numFound += 1

                if not numFound >= 9:
                    self.submenue = interaction.TextMenu("challenge: find 9 living blooms\n\nchallenge in progress:\ngo to tile with 9 living blooms on it and activate challenger")
                else:
                    self.submenue = interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "3livingSickBlooms":
                baseCoordinateX = character.xPosition-(character.xPosition%15)
                baseCoordinateY = character.yPosition-(character.yPosition%15)

                numFound = 0
                for extraX in range(1,14):
                    for extraY in range(1,14):
                        for item in character.container.getItemByPosition((baseCoordinateX+extraX,baseCoordinateY+extraY)):
                            if item.type == "SickBloom" and item.dead == False:
                                numFound += 1

                if not numFound >= 3:
                    self.submenue = interaction.TextMenu("challenge: find 3 living sick blooms\n\nchallenge in progress:\ngo to tile with 3 living sick blooms on it and activate challenger")
                else:
                    self.submenue = interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "fullMoldCover":
                baseCoordinateX = character.xPosition-(character.xPosition%15)
                baseCoordinateY = character.yPosition-(character.yPosition%15)

                emptyFound = False
                for extraX in range(1,14):
                    for extraY in range(1,14):
                        hasMold = False
                        for item in character.container.getItemByPosition((baseCoordinateX+extraX,baseCoordinateY+extraY)):
                            if item.type in ["Mold","Sprout","Sprout2","Bloom","SickBloom","PoisonBloom","Bush","EncrustedBush","PoisonBush","EncrustedPoisonBush"]:
                                hasMold = True
                        if not hasMold:
                            emptyFound = True

                if emptyFound:
                    self.submenue = interaction.TextMenu("challenge: find tile completely covered in mold\n\nchallenge in progress:\ngo to a tile completed covered in mold and activate challenger")
                else:
                    self.submenue = interaction.TextMenu("challenge done")
                    self.challenges.pop()
            else:
                self.submenue = interaction.TextMenu("unkown challenge")

        character.macroState["submenue"] = self.submenue

        if not len(self.challenges):
            self.done = True

    def getLongInfo(self):
        text = """
item:

description:
TBD

%s
        """%(str(self.challenges))


class SimpleRunner(Item):
    type = "SimpleRunner"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="SimpleRunner",creator=None,noId=False):
        super().__init__(displayChars.simpleRunner,xPosition,yPosition,name=name,creator=creator)
        self.command = None

        self.attributesToStore.extend([
                "command"])
        self.initialState = self.getState()

    def apply(self,character):
        super().apply(character,silent=True)

        if self.command == None:
            if not len(character.macroState["macros"]):
                character.messages.append("no macro found - record a macro to store it in this machine")

            options = []
            for key,value in character.macroState["macros"].items():
                compressedMacro = ""
                for keystroke in value:
                    if len(keystroke) == 1:
                        compressedMacro += keystroke
                    else:
                        compressedMacro += "/"+keystroke+"/"
                options.append((key,compressedMacro))

            self.submenue = interaction.SelectionMenu("select the macro you want to store",options)
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.storeMacro

            self.character = character
        else:
            convertedCommand = []
            for item in self.command:
                convertedCommand.append((item,["norecord"]))
            character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

    def storeMacro(self):
        key = self.submenue.selection

        if not key in self.character.macroState["macros"]:
            self.character.messages.append("command not found in macro")
            return
            
        import copy
        self.command = copy.deepcopy(self.character.macroState["macros"][key])
        self.character.messages.append("you store the command into the machine")

class MacroRunner(Item):
    type = "MacroRunner"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MacroRunner",creator=None,noId=False):
        super().__init__(displayChars.macroRunner,xPosition,yPosition,name=name,creator=creator)
        self.command = None

        self.attributesToStore.extend([
                "command"])
        self.initialState = self.getState()

    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        if self.command == None:
            if not len(character.macroState["macros"]):
                character.messages.append("no macro found - record a macro to store it in this machine")

            options = []
            for key,value in character.macroState["macros"].items():
                compressedMacro = ""
                for keystroke in value:
                    if len(keystroke) == 1:
                        compressedMacro += keystroke
                    else:
                        compressedMacro += "/"+keystroke+"/"
                options.append((key,compressedMacro))

            self.submenue = interaction.SelectionMenu("select the macro you want to store",options)
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.storeMacro

            self.character = character
        else:
            import copy
            convertedCommand = []
            for item in self.command:
                convertedCommand.append((item,["norecord"]))
            character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

    def storeMacro(self):
        key = self.submenue.selection

        if not key in self.character.macroState["macros"]:
            self.character.messages.append("command not found in macro")
            return
            
        import copy
        self.command = copy.deepcopy(self.character.macroState["macros"][key])
        self.character.messages.append("you store the command into the machine")


'''
'''
class BluePrinter(Item):
    type = "BluePrinter"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="BluePrinter",creator=None,noId=False):
        super().__init__(displayChars.blueprinter,xPosition,yPosition,name=name,creator=creator)
        self.submenue = None
        self.text = None

        self.reciepes = [
                [["MemoryCell","Tank"],"MemoryBank"],
                [["MemoryCell","Puller"],"MemoryDump"],
                [["MemoryCell","Heater"],"SimpleRunner"],
                [["MemoryCell","Pusher"],"MemoryStack"],
                [["MemoryCell","Connector"],"MemoryReset"],

                [["Case","Sheet","Bloom"],"BloomContainer"],
                [["Case","Sheet"],"Container"],

                [["Sheet","pusher"],"Sorter"],
                [["Sheet","puller"],"Mover"],
                [["Stripe","Connector"],"RoomControls"],
                [["GooFlask","Tank"],"GrowthTank"],
                [["Radiator","Heater"],"StasisTank"],
                [["Mount","Tank"],"MarkerBean"],
                [["Bolt","Tank"],"PositioningDevice"],
                [["Bolt","puller"],"Watch"],
                [["Bolt","Heater"],"BackTracker"],
                [["Bolt","pusher"],"Tumbler"],
                [["Sheet","Heater"],"ItemUpgrader"],
                [["Sheet","Connector"],"ItemDowngrader"],
                [["Scrap","MetalBars"],"Scraper"],
                [["Tank","Connector"],"ReactionChamber"],

                [["Frame","MetalBars"],"Case"],
                [["Frame"],"PocketFrame"],
                [["Connector","MetalBars"],"MemoryCell"],

                [["Sheet","MetalBars"],"Tank"],
                [["Radiator","MetalBars"],"Heater"],
                [["Mount","MetalBars"],"Connector"],
                [["Stripe","MetalBars"],"pusher"],
                [["Bolt","MetalBars"],"puller"],
                [["Rod","MetalBars"],"Frame"],

                [["Bloom","MetalBars"],"SporeExtractor"],
                [["Sheet","Rod","Bolt"],"FloorPlate"],
                [["Coal","SickBloom"],"FireCrystals"],

                [["Command"],"AutoScribe"],
                [["Corpse"],"CorpseShredder"],

                [["Tank"],"GooFlask"],
                [["Heater"],"Boiler"],
                [["Connector"],"Door"],
                [["pusher"],"Drill"],
                [["puller"],"RoomBuilder"],

                [["Explosive"],"Bomb"],
                [["Bomb"],"Mortar"],

                [["Sheet"],"Sheet"],
                [["Radiator"],"Radiator"],
                [["Mount"],"Mount"],
                [["Stripe"],"Stripe"],
                [["Bolt"],"Bolt"],
                [["Rod"],"Rod"],

                [["Scrap"],"ScrapCompactor"],
                [["Coal"],"Furnace"],
                [["BluePrint"],"BluePrinter"],
                [["MetalBars"],"Wall"],

                [["GooFlask"],"GooDispenser"],
                [["Bloom"],"BloomShredder"],
                [["VatMaggot"],"MaggotFermenter"],
                [["BioMass"],"BioPress"],
                [["PressCake"],"GooProducer"],
            ]

    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.messages.append("this machine can only be used within rooms")
            return

        sheet = None
        if (self.xPosition,self.yPosition-1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                if item.type == "Sheet":
                    sheet = item
                    break

        if not sheet:
            character.messages.append("no sheet - place sheet to the top/north")
            return

        inputThings = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            inputThings.extend(self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)])
        if (self.xPosition,self.yPosition+1) in self.room.itemByCoordinates:
            inputThings.extend(self.room.itemByCoordinates[(self.xPosition,self.yPosition+1)])

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

            targetFull = False
            if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True

            if targetFull:
                character.messages.append("the target area is full, the machine does not produce anything")
                return

            self.room.addItems([new])

            for itemType in reciepeFound[0]:
                self.room.removeItem(abstractedInputThings[itemType]["item"])
            self.room.removeItem(sheet)
            character.messages.append("you create a blueprint for "+reciepe[1])
            character.messages.append("items used: "+", ".join(reciepeFound[0]))
        else:
            character.messages.append("unable to produce blueprint from given items")
            return

    def getLongInfo(self):
        text = """

This machine creates Blueprints.

The Blueprinter has two inputs
It needs a sheet on the north to print the blueprint onto.
The items from the blueprint reciepe need to be added to the west or south.

"""
        return text

'''
'''
class BluePrint(Item):
    type = "BluePrint"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="BluePrint",creator=None,noId=False):
        super().__init__(displayChars.blueprint,xPosition,yPosition,name=name,creator=creator)

        self.endProduct = None
        self.walkable = True
        self.baseName = name
        self.level = 1

        self.attributesToStore.extend([
                "endProduct","level"])

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

    def getLongInfo(self):
        text = """
item: Blueprint

decription:
This Blueprint holds the information on how to produce an item in machine readable form.

It needs to be loaded into a machine machine.
After loading the blueprint the machine machine is able to produce a machine that produces the the item the blue

this blueprint is for %s

This is a level %s item

"""%(self.endProduct,self.level)
        return text


'''
'''
class CoalMine(Item):
    type = "CoalMine"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="coal mine",creator=None,noId=False):
        super().__init__(displayChars.coalMine,xPosition,yPosition,name=name,creator=creator)

        self.bolted = True
        self.walkable = False

    def apply(self,character):
        if self.room:
            character.messages.append("this item cannot be used within rooms")
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.terrain.itemByCoordinates:
            if len(self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.messages.append("the target area is full, the machine does not produce anything")
            return

        character.messages.append("you mine a piece of coal")

        # spawn new item
        new = Coal(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.terrain.addItems([new])

    def getLongInfo(self):
        text = """
item: CoalMine

description:
Use it to mine coal. The coal will be dropped to the east/rigth.

"""
        return text


'''
'''
class StasisTank(Item):
    type = "StasisTank"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="stasis tank",creator=None,noId=False):
        self.character = None
        super().__init__(displayChars.stasisTank,xPosition,yPosition,name=name,creator=creator)

        self.bolted = True
        self.walkable = False
        self.character = None

    def apply(self,character):
        if not self.room:
            character.messages.append("you can not use item outside of rooms")
            return

        if self.character and self.character.stasis:
            self.room.addCharacter(self.character,self.xPosition,self.yPosition+1)
            self.character.stasis = False
            self.character = None
        else:
            options = []
            options.append(("enter","yes"))
            options.append(("noEnter","no"))
            self.submenue = interaction.SelectionMenu("The stasis tank is empty. You will not be able to leave it on your on.\nDo you want to enter it?",options)
            self.character = character
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.enterSelection

    def enterSelection(self):
        if self.submenue.selection == "enter":
            self.character.stasis = True
            self.room.removeCharacter(self.character)
            self.character.messages.append("you entered the stasis tank. You will not be able to move until somebody activates it")
        else:
            self.character.messages.append("you do not enter the stasis tank")

    def getDiffState(self):
        state = super().getDiffState()

        if self.character:
            state["character"] = self.character.getState()
        else:
            state["character"] = None

        return state

    def getState(self):
        state = super().getState()

        if self.character:
            state["character"] = self.character.getState()
        else:
            state["character"] = None

        return state

    def setState(self,state):
        super().setState(state)

        if "character" in state and state["character"]:
            char = characters.Character(creator=void)
            char.setState(state["character"])
            loadingRegistry.register(char)

            self.character = char
        else:
            state["character"] = None

    def getLongInfo(self):
        text = """

This machine allow to enter stasis. In stasis you do not need food and can not do anything.

You cannot leave the stasis tank on your own.

If the stasis tank is empty you can activate it to enter the stasis tank.

If the stasis tank is occupied, you can activate it to eject the character from the tank.
The ejected character will be placed to the south of the stasis tank and will start to act again.

"""
        return text
        

'''
'''
class PositioningDevice(Item):
    type = "PositioningDevice"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="positioning device",creator=None,noId=False):
        super().__init__(displayChars.positioningDevice,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def apply(self,character):

        if not "x" in character.registers:
            character.registers["x"] = [0]
        character.registers["x"][-1] = character.xPosition
        if not "y" in character.registers:
            character.registers["y"] = [0]
        character.registers["y"][-1] = character.yPosition

        character.messages.append("your position is %s/%s"%(character.xPosition,character.yPosition,))

    def getLongInfo(self):
        text = """

this device allows you to determine your postion. Use it to get your position.

use it to determine your position. Your position will be shown as a message.

Also the position will be written to your registers.
The x-position will be written to the register x.
The y-position will be written to the register y.

"""
        return text

'''
'''
class Watch(Item):
    type = "Watch"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="watch",creator=None,noId=False):
        super().__init__(displayChars.watch,xPosition,yPosition,name=name,creator=creator)

        self.creationTime = 0
        self.maxSize = 100

        self.attributesToStore.extend([
               "creationTime"])

        self.initialState = self.getState()

        self.bolted = False
        self.walkable = True
        try:
            self.creationTime = gamestate.tick
        except:
            pass

    def apply(self,character):

        time = gamestate.tick-self.creationTime
        while time > self.maxSize:
            self.creationTime += self.maxSize
            time -= self.maxSize

        if not "t" in character.registers:
            character.registers["t"] = [0]
        character.registers["t"][-1] = gamestate.tick-self.creationTime

        character.messages.append("it shows %s ticks"%(character.registers["t"][-1]))

    def getLongInfo(self):
        text = """
This device tracks ticks since creation. You can use it to measure time.
Activate it to get a message with the number of ticks passed.
Also the number of ticks will be written to the register t.
"""
        return text

'''
'''
class BackTracker(Item):
    type = "BackTracker"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="back tracker",creator=None,noId=False):
        super().__init__(displayChars.backTracker,xPosition,yPosition,name=name,creator=creator)

        self.initialState = self.getState()

        self.attributesToStore.extend([
               "command"])

        self.tracking = False
        self.tracked = None
        self.walkable = True
        self.command = []

        self.addListener(self.registerDrop,"dropped")
        self.addListener(self.registerPickUp,"pickUp")

    def apply(self,character):

        if self.tracking:
            self.tracked.delListener(self.registerMovement,"moved")
            character.messages.append("backtracking")
            self.tracking = False

            convertedCommand = []
            for item in self.command:
                convertedCommand.append((item,["norecord"]))

            character.messages.append("runs the stored path")
            character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
            self.command = []
        else:
            self.tracked = character
            self.tracked.addListener(self.registerMovement,"moved")

            character.messages.append("it starts to track")
            self.tracking = True

    def getLongInfo(self):
        text = """

This device tracks ticks since creation. You can use it to measure time.

Activate it to get a message with the number of ticks passed.

Also the number of ticks will be written to the register t.

"""
        return text

    def registerPickUp(self,param):
        if self.tracked:
            self.tracked.messages.append("pickUp")
            self.tracked.messages.append(param)

    def registerDrop(self,param):
        if self.tracked:
            self.tracked.messages.append("drop")
            self.tracked.messages.append(param)

    def registerMovement(self,param):
        if self.tracked:
            self.tracked.messages.append("mov")
            self.tracked.messages.append(param)

        mov = ""
        if param == "north":
            mov = "s"
        elif param == "south":
            mov = "w"
        elif param == "west":
            mov = "d"
        elif param == "east":
            mov = "a"
        self.command.insert(0,mov)

'''
'''
class Tumbler(Item):
    type = "Tumbler"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="tumbler",creator=None,noId=False):
        super().__init__(displayChars.tumbler,xPosition,yPosition,name=name,creator=creator)

        self.initialState = self.getState()

        self.strength = 7
        self.tracking = False
        self.tracked = None
        self.walkable = True
        self.command = []

    def apply(self,character):

        direction = gamestate.tick%33%4
        strength = gamestate.tick%self.strength+1

        direction = ["w","a","s","d"][direction]
        convertedCommands = [(direction,["norecord"])] * strength
        character.macroState["commandKeyQueue"] = convertedCommands + character.macroState["commandKeyQueue"]

        character.messages.append("tumbling %s %s "%(direction,strength))
        self.tracking = True

    def getLongInfo(self):
        text = """

This device tracks ticks since creation. You can use it to measure time.

Activate it to get a message with the number of ticks passed.

Also the number of ticks will be written to the register t.

"""
        return text

'''
'''
class GlobalMacroStorage(Item):
    type = "GlobalMacroStorage"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="global macro storage",creator=None,noId=False):
        super().__init__(displayChars.globalMacroStorage,xPosition,yPosition,name=name,creator=creator)

        self.initialState = self.getState()

    def apply(self,character):

        self.character = character

        options = []
        options.append(("load","load macro from global storage"))
        options.append(("store","add macro to the global storage"))
        self.submenue = interaction.SelectionMenu("what do you want to do",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.actionSelection

    def actionSelection(self):
        selection =  self.submenue.getSelection()
        if selection == "load":
            try:
                with open("globalStorage.json","r") as globalStorageFile:
                    globalStorage = json.loads(globalStorageFile.read())
            except:
                globalStorage = []

            counter = 1

            options = []
            for entry in globalStorage:
                options.append((counter,entry["name"]))
                counter += 1
            self.submenue = interaction.SelectionMenu("what macro do you want to load?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.load

        if selection == "store":
            self.submenue = interaction.InputMenu("supply a name/description for the macro")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.store

    def load(self):
        try:
            with open("globalStorage.json","r") as globalStorageFile:
                globalStorage = json.loads(globalStorageFile.read())
        except:
            globalStorage = []

        rawMacros = globalStorage[self.submenue.getSelection()-1]["macro"]
        parsedMacros = {}

        state = "normal"
        for key,value in rawMacros.items():
            parsedMacro = []
            for char in value:
                if state == "normal":
                    if char == "/":
                        state = "multi"
                        combinedKey = ""
                        continue
                    parsedMacro.append(char)
                if state == "multi":
                    if char == "/":
                        state = "normal"
                        parsedMacro.append(combinedKey)
                    else:
                        combinedKey += char
            parsedMacros[key] = parsedMacro

        self.character.macroState["macros"] = parsedMacros
        self.character.messages.append("you load the macro %s from the macro storage"%(globalStorage[self.submenue.getSelection()-1]["name"]))

    def store(self):
        try:
            with open("globalStorage.json","r") as globalStorageFile:
                globalStorage = json.loads(globalStorageFile.read())
        except:
            globalStorage = []

        compressedMacros = {}
        for key,value in self.character.macroState["macros"].items():
            compressedMacro = ""
            for keystroke in value:
                if len(keystroke) == 1:
                    compressedMacro += keystroke
                else:
                    compressedMacro += "/"+keystroke+"/"
            compressedMacros[key] = compressedMacro

        globalStorage.append({"name":self.submenue.text,"macro":compressedMacros})

        with open("globalStorage.json","w") as globalStorageFile:
            globalStorageFile.write(json.dumps(globalStorage, indent = 10, sort_keys = True))

        self.character.messages.append("you store the macro in the global macro storage")

    def getLongInfo(self):
        text = """

This device is a one of a kind machine. It allows to store and load marcos between gamestates.

"""
        return text

'''
'''
class Case(Item):
    type = "Case"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="case",creator=None,noId=False):
        super().__init__(displayChars.case,xPosition,yPosition,name=name,creator=creator)
        self.initialState = self.getState()

    def getLongInfo(self):
        text = """

A case. Is complex building item. It is used to build bigger things.

"""
        return text

'''
'''
class PocketFrame(Item):
    type = "PocketFrame"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="pocket frame",creator=None,noId=False):
        super().__init__(displayChars.pocketFrame,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.initialState = self.getState()

    def getLongInfo(self):
        text = """

A pocket frame. Is complex building item. It is used to build smaller things.

"""
        return text

'''
'''
class MemoryCell(Item):
    type = "MemoryCell"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="memory cell",creator=None,noId=False):
        super().__init__(displayChars.memoryCell,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True

        self.initialState = self.getState()

    def getLongInfo(self):
        text = """

A memory cell. Is complex building item. It is used to build logic items.

"""
        return text

class Bomb(Item):
    type = "Bomb"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="bomb",creator=None,noId=False):

        super().__init__(displayChars.bomb,xPosition,yPosition,creator=creator,name=name)
        
        self.bolted = False
        self.walkable = True

        self.initialState = self.getState()

    def getLongInfo(self):

        text = """

A simple Bomb. It explodes when destroyed.

The explosion will damage/destroy everything on the current tile or the container.

Activate it to trigger a exlosion.

"""
        return text

    def apply(self,character):
        self.destroy()

    def destroy(self, generateSrcap=True):
        xPosition = self.xPosition
        yPosition = self.yPosition

        new = Explosion(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        new.bolted = False
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition-1
        new.yPosition = self.yPosition
        new.bolted = False
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition-1
        new.bolted = False
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition+1
        new.bolted = False
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        super().destroy()

        """
        if xPosition and yPosition:
            for item in self.container.itemByCoordinates[(xPosition,yPosition)]:
                if item == self:
                    continue
                if item.type == "Explosion":
                    continue
                item.destroy()
        """

        self.container.addItems([new])

class Explosive(Item):
    type = "Explosive"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="explosive",creator=None,noId=False):

        super().__init__(displayChars.bomb,xPosition,yPosition,creator=creator,name=name)
        
        self.bolted = False
        self.walkable = True

        self.initialState = self.getState()

    def getLongInfo(self):

        text = """

A Explosive. Simple building material. Used to build bombs.

"""
        return text

class Mortar(Item):
    type = "Mortar"
    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="mortar",creator=None,noId=False):

        super().__init__(displayChars.mortar,xPosition,yPosition,creator=creator,name=name)
        
        self.bolted = False
        self.loaded = False
        self.loadedWith = None
        self.precision = 5

        self.attributesToStore.extend([
               "loaded","precision"])

        self.initialState = self.getState()

    def apply(self,character):
        if not self.loaded:
            itemFound = None
            for item in character.inventory:
                if item.type == "Bomb":
                    itemFound = item
                    continue

            if not itemFound:
                character.messages.append("could not load mortar. no bomb in inventory")
                return

            character.messages.append("you load the mortar")

            character.inventory.remove(itemFound)
            self.loadedWith = itemFound
            self.loaded = True
        else:
            if not self.loadedWith:
                self.loaded = False
                return
            character.messages.append("you fire the mortar")
            bomb = self.loadedWith
            self.loadedWith = None
            self.loaded = False

            bomb.yPosition = self.yPosition
            bomb.xPosition = self.xPosition
            bomb.bolted = False

            distance = 10
            if (gamestate.tick+self.yPosition+self.xPosition)%self.precision == 0:
                character.messages.append("you missfire (0)")
                self.precision += 10
                distance -= gamestate.tick%10-10//2
                character.messages.append((distance,gamestate.tick%10,10//2))
            elif (gamestate.tick+self.yPosition+self.xPosition)%self.precision == 1:
                character.messages.append("you missfire (1)")
                self.precision += 5
                distance -= gamestate.tick%7-7//2
                character.messages.append((distance,gamestate.tick%7,7//2))
            elif (gamestate.tick+self.yPosition+self.xPosition)%self.precision < 10:
                character.messages.append("you missfire (10)")
                self.precision += 2
                distance -= gamestate.tick%3-3//2
                character.messages.append((distance,gamestate.tick%3,3//2))
            elif (gamestate.tick+self.yPosition+self.xPosition)%self.precision < 100:
                character.messages.append("you missfire (100)")
                self.precision += 1
                distance -= gamestate.tick%2-2//2
                character.messages.append((distance,gamestate.tick%2,2//2))

            bomb.yPosition += distance

            self.container.addItems([bomb])

            bomb.destroy()

    def getLongInfo(self):

        text = """

A mortar. Load it with bombs and activate it to fire.

It fires 10 steps to the south. Its current precision is """+str(self.precision)+""".

"""
        return text

class Chute(Item):
    type = "Chute"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="chute",creator=None,noId=False):

        super().__init__(displayChars.fireCrystals,xPosition,yPosition,creator=creator,name=name)

    def apply(self,character):
        if character.inventory:
            item = character.inventory[-1]
            character.inventory.remove(item)
            item.xPosition = self.xPosition+1
            item.yPosition = self.yPosition

            self.room.addItems([item])

class FireCrystals(Item):
    type = "FireCrystals"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="fireCrystals",creator=None,noId=False):

        super().__init__(displayChars.fireCrystals,xPosition,yPosition,creator=creator,name=name)
        self.walkable = True

    def apply(self,character):
        character.messages.append("The fire crystals start sparkling")
        self.startExploding()

    def startExploding(self):
        event = src.events.RunCallbackEvent(gamestate.tick+2+(2*self.xPosition+3*self.yPosition+gamestate.tick)%10,creator=self)
        event.setCallback({"container":self,"method":"explode"})
        self.container.addEvent(event)

    def explode(self):
        self.destroy()

    def destroy(self, generateSrcap=False):
        if not self.xPosition or not self.yPosition:
            return

        new = Explosion(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition-1
        new.yPosition = self.yPosition
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition-1
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition+1
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        super().destroy(generateSrcap=False)

class ReactionChamber(Item):
    type = "ReactionChamber"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="reactionChamber",creator=None,noId=False):
        super().__init__(displayChars.reactionChamber,xPosition,yPosition,creator=creator,name=name)
        contains = ""
        
    def apply(self,character):

        options = []
        options.append(("add","add"))
        options.append(("boil","boil"))
        options.append(("mix","mix"))
        self.submenue = interaction.SelectionMenu("select the item to produce",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doAction

    def doAction(self):
        selection = self.submenue.selection
        if (selection == "add"):
            #self.add()
            pass
        if (selection == "mix"):
            self.mix()
        if (selection == "boil"):
            self.boil()

    def add(self,chemical):
        if len(self.contains) >= 10:
            self.character.messages.append("the reaction chamber is full")
            return

        self.character.messages.append("you add a "+chemical.type+" to the reaction chamber")

    def mix(self,granularity=9):
        if len(self.contains) < 10:
            self.character.messages.append("the reaction chamber is not full")
            return
            
        self.character.messages.append("the reaction chambers contents are mixed with granularity %s"%(granularity))

    def boil(self):

        self.character.messages.append("the reaction chambers contents are boiled")
        self.contents = self.contents[19]+self.contents[0:19]
    
    def getLongInfo(self):

        text = """

A raction chamber. It is used to mix chemicals together.

contains:

"""+self.contains

        return text


class ReactionChamber_2(Item):
    type = "ReactionChamber_2"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="reactionChamber_2",creator=None,noId=False):

        super().__init__(displayChars.reactionChamber,xPosition,yPosition,creator=creator,name=name)
        
    def apply(self,character):

        coalFound = None
        flaskFound = None

        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if item.type in "Coal":
                    coalFound = item
                if item.type in "GooFlask" and item.uses == 100:
                    flaskFound = item

        if not coalFound or not flaskFound:
            character.messages.append("reagents not found. place coal and a full goo flask to the left/west")
            return

        self.room.removeItem(coalFound)
        self.room.removeItem(flaskFound)
        
        explosive = Explosive(creator=self)
        explosive.xPosition = self.xPosition+1
        explosive.yPosition = self.yPosition
        explosive.bolted = False

        byProduct = FireCrystals(creator=self)
        byProduct.xPosition = self.xPosition
        byProduct.yPosition = self.yPosition+1
        byProduct.bolted = False

        self.room.addItems([byProduct,explosive])
    
    def getLongInfo(self):

        text = """

A raction chamber. It is used to mix chemicals together.

"""
        return text

class Explosion(Item):
    type = "Explosion"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="explosion",creator=None,noId=False):
        super().__init__(displayChars.explosion,xPosition,yPosition,creator=creator,name=name)

    def pickUp(self,character):
        pass
    def apply(self,character):
        self.explode()
        pass
    def drop(self,character):
        pass
    def explode(self):

        if self.xPosition and self.yPosition:
            for character in self.container.characters:
                if (character.xPosition == self.xPosition and character.yPosition == self.yPosition):
                    character.die()

            for item in self.container.getItemByPosition((self.xPosition,self.yPosition)):
                if item == self:
                    continue
                if item.type == "Explosion":
                    continue
                item.destroy()

        self.container.removeItem(self)

class Chemical(Item):
    type = "Chemical"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.fireCrystals,xPosition,yPosition,creator=creator,name="chemical")
        self.composition = b"cccccggggg"

    def apply(self,character):
        import hashlib

        results = []
        counter = 0

        import random

        while 1:

            tmp = random.choice(["mix","shift"])

            if tmp == "mix":
                self.mix(character)
            elif tmp == "switch":
                self.mix(character)
            elif tmp == "shift":
                self.shift()

            test = hashlib.sha256(self.composition[0:9])
            character.messages.append(counter)

            result = int(test.digest()[-1])
            result2 = int(test.digest()[-2])
            if result < 15:
                character.messages.append(test.digest())
                character.messages.append(result)
                character.messages.append(result2)
                break

            counter += 1

        #character.messages.append(results)

    def shift(self):
        self.composition = self.composition[1:]+self.composition[0:1]

    def mix(self,character):
        part1 = self.composition[0:5]
        part2 = self.composition[5:10]

        self.composition = part1[0:1]+part2[0:1]+part1[1:2]+part2[1:2]+part1[2:3]+part2[2:3]+part1[3:4]+part2[3:4]+part1[4:5]+part2[4:5]

class Spawner(Item):
    type = "Spawner"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.fireCrystals,xPosition,yPosition,creator=creator,name="spawner")
        self.charges = 1

    def apply(self,character):
        corpses = []
        for item in character.inventory:
            if item.type == "Corpse":
                corpses.append(item)

        for corpse in corpses:
            self.charges += 1
            character.inventory.remove(corpse)

        if self.charges:
            event = src.events.RunCallbackEvent(gamestate.tick+100,creator=self)
            event.setCallback({"container":self,"method":"spawn"})
            self.terrain.addEvent(event)

    def spawn(self):
        if not self.charges:
            return

        character = characters.Character(displayChars.staffCharactersByLetter["a".lower()],self.xPosition+1,self.yPosition,name="a",creator=self)

        character.solvers = [
                  "SurviveQuest",
                  "Serve",
                  "NaiveMoveQuest",
                  "MoveQuestMeta",
                  "NaiveActivateQuest",
                  "ActivateQuestMeta",
                  "NaivePickupQuest",
                  "NaiveDropQuest",
                  "PickupQuestMeta",
                  "DrinkQuest",
                  "ExamineQuest",
                  "FireFurnaceMeta",
                  "CollectQuestMeta",
                  "WaitQuest"
                  "NaiveDropQuest",
                  "DropQuestMeta",
                  "NaiveMurderQuest",
                ]

        character.inventory.append(Tumbler(None,None,creator=self))
        character.inventory.append(BackTracker(None,None,creator=self))
        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                    splittedCommand.append(char)
            return splittedCommand

        character.macroState["macros"]["WALKTo"] = splitCommand("$=aa$=ww$=ss$=dd")
        """
        character.macroState["macros"]["MURDEr"] = splitCommand("ope_WALKTomijj_u")
        character.macroState["macros"]["u"] = splitCommand("%E_i_o")
        character.macroState["macros"]["i"] = splitCommand("_MURDEr")
        character.macroState["macros"]["o"] = splitCommand("%c_p_a")
        character.macroState["macros"]["p"] = splitCommand("_GETBODYs")
        character.macroState["macros"]["a"] = splitCommand("ijj_u")
        character.macroState["macros"]["s"] = splitCommand("_u")
        character.macroState["macros"]["GETBODYs"] = splitCommand("opM_WALKTokijsjajijsjijj_u")
        character.macroState["macros"]["STARt"] = splitCommand("ijsj_a")
        character.macroState["macros"]["m"] = splitCommand("_STARt")
        """
        character.macroState["macros"]["_GOTOTREe"] = splitCommand("opt_WALKTo")
        character.macroState["macros"]["_RANDOMWALk"] = splitCommand("ijj")
        character.macroState["macros"]["_a"] = splitCommand("_RANDOMWALk")
        character.macroState["macros"]["m"] = splitCommand("ijj_GOTOTREe")

        character.macroState["commandKeyQueue"] = [("_",[]),("m",[])]
        character.satiation = 100000
        self.container.addCharacter(character,self.xPosition+1,self.yPosition)

        event = src.events.RunCallbackEvent(gamestate.tick+100,creator=self)
        event.setCallback({"container":self,"method":"spawn"})
        self.terrain.addEvent(event)

        self.charges -= 1

    def getLongInfo(self):
        return """
item: Spawner

description:
spawner with %s charges
"""%(self.charges)

class MoldSpore(Item):
    type = "MoldSpore"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.moldSpore,xPosition,yPosition,creator=creator,name="mold spore")
        self.walkable = True
        self.bolted = False

    def apply(self,character):
        self.startSpawn()
        character.messages.append("you activate the mold spore")

    def startSpawn(self):
        event = src.events.RunCallbackEvent(gamestate.tick+(2*self.xPosition+3*self.yPosition+gamestate.tick)%10,creator=self)
        event.setCallback({"container":self,"method":"spawn"})
        self.terrain.addEvent(event)

    def spawn(self):
        new = itemMap["Mold"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        new.startSpawn()
        self.destroy(generateSrcap=False)

    def getLongInfo(self):
        return """
item: MoldSpore

description:
This is a mold spore 

put it on the ground and activate it to plant it
"""

class Mold(Item):
    type = "Mold"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.moss,xPosition,yPosition,creator=creator,name="mold")
        self.charges = 2
        self.walkable = True
        self.attributesToStore.extend([
               "charges"])
        self.initialState = self.getState()


    def apply(self,character):
        character.satiation += 2
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateSrcap=False)
        character.messages.append("you eat the mold and gain 2 satiation")

    def startSpawn(self):
        if self.charges:
            if not (self.xPosition and self.yPosition and self.terrain):
                return
            event = src.events.RunCallbackEvent(gamestate.tick+(2*self.xPosition+3*self.yPosition+gamestate.tick)%1000,creator=self)
            event.setCallback({"container":self,"method":"spawn"})
            self.terrain.addEvent(event)

    def spawn(self):
        if self.charges:
            if not (self.xPosition and self.yPosition):
                return
            direction = (2*self.xPosition+3*self.yPosition+gamestate.tick)%4
            import random
            direction = random.choice([0,1,2,3])
            if direction == 0:
                newPos = (self.xPosition,self.yPosition+1)
            if direction == 1:
                newPos = (self.xPosition+1,self.yPosition)
            if direction == 2:
                newPos = (self.xPosition,self.yPosition-1)
            if direction == 3:
                newPos = (self.xPosition-1,self.yPosition)

            #if (((newPos[0]%15 == 0 or newPos[0]%15 == 14) and not (newPos[1]%15 in (8,))) or
            #    ((newPos[1]%15 == 0 or newPos[1]%15 == 14) and not (newPos[0]%15 in (8,)))):
            #    return

            itemList = self.container.getItemByPosition(newPos)
            if not len(itemList):
                new = itemMap["Mold"](creator=self)
                new.xPosition = newPos[0]
                new.yPosition = newPos[1]
                self.container.addItems([new])
                new.startSpawn()
            elif len(itemList) > 0:
                if itemList[-1].type == "Mold":
                    self.charges += itemList[-1].charges//2
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["Sprout"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "Sprout":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["Sprout2"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])
                elif itemList[-1].type == "Sprout2":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["Bloom"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])
                    new.startSpawn()
                elif itemList[-1].type == "Bloom":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["SickBloom"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])
                    new.startSpawn()
                elif itemList[-1].type == "Corpse":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["PoisonBloom"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "SickBloom":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["Bush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "PoisonBloom":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["PoisonBush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "Bush":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["EncrustedBush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                    new = itemMap["Bush"](creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition
                    self.container.addItems([new])
                    self.container.removeItem(self)

                elif itemList[-1].type == "EncrustedBush":
                    new = itemMap["Bush"](creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition
                    self.container.addItems([new])
                    self.container.removeItem(self)

                elif itemList[-1].type in ["PoisonBush","EncrustedPoisonBush"]:
                    new = itemMap["PoisonBloom"](creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition
                    self.container.addItems([new])
                    self.container.removeItem(self)

                elif itemList[-1].type in ["Coal"]:
                    itemList[-1].destroy(generateSrcap=False)

                    new = itemMap["Bush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type in ["MoldFeed"]:
                    itemList[-1].destroy(generateSrcap=False)

                    new = itemMap["Bloom"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

        self.charges -= 1
        if self.charges:
            self.startSpawn()

    def getLongInfo(self):
        return """
item: Mold

description:
This is a patch of mold

you can eat it to gain 2 satiation.
"""

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

class Sprout(Item):
    type = "Sprout"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.sprout,xPosition,yPosition,creator=creator,name="sprout")
        self.walkable = True

    def apply(self,character):
        character.satiation += 10
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateSrcap=False)
        character.messages.append("you eat the sprout and gain 10 satiation")

    def getLongInfo(self):
        return """
item: Sprout

description:
This is a mold patch that shows the first sign of a bloom.

you can eat it to gain 10 satiation.
"""

    def destroy(self, generateSrcap=True):

        new = itemMap["Mold"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        new.startSpawn()

        super().destroy(generateSrcap=False)

class Sprout2(Item):
    type = "Sprout2"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.sprout2,xPosition,yPosition,creator=creator,name="sprout2")
        self.walkable = True

    def apply(self,character):
        character.satiation += 25
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateSrcap=False)
        character.messages.append("you eat the sprout and gain 25 satiation")

    def getLongInfo(self):
        return """
item: Sprout2

description:
This is a mold patch that developed a bloom sprout.

you can eat it to gain 25 satiation.
"""

    def destroy(self, generateSrcap=True):

        new = itemMap["Mold"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        new.startSpawn()

        super().destroy(generateSrcap=False)

class Bloom(Item):
    type = "Bloom"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.bloom,xPosition,yPosition,creator=creator,name="bloom")
        self.bolted = False
        self.walkable = True
        self.dead = False
        self.attributesToStore.extend([
               "dead"])
        self.initialState = self.getState()

    def apply(self,character):
        if self.dead:
            character.satiation += 100
            self.destroy(generateSrcap=False)
            character.messages.append("you eat the dead bloom and gain 100 satiation")
        else:
            character.satiation += 115
            if character.satiation > 1000:
                character.satiation = 1000
            self.destroy(generateSrcap=False)
            character.messages.append("you eat the bloom and gain 115 satiation")

    def startSpawn(self):
        if not self.dead:
            event = src.events.RunCallbackEvent(gamestate.tick+(2*self.xPosition+3*self.yPosition+gamestate.tick)%10000,creator=self)
            event.setCallback({"container":self,"method":"spawn"})
            self.terrain.addEvent(event)

    def pickUp(self,character):
        self.bolted = False
        self.localSpawn()
        self.dead = True
        super().pickUp(character)

    def spawn(self):
        if self.dead:
            return
        if not (self.xPosition and self.yPosition):
            return
        direction = (2*self.xPosition+3*self.yPosition+gamestate.tick)%4
        import random
        direction = (random.randint(1,13),random.randint(1,13))
        newPos = (self.xPosition-self.xPosition%15+direction[0],self.yPosition-self.yPosition%15+direction[1])

        if not (newPos in self.container.itemByCoordinates and len(self.container.itemByCoordinates[newPos])):
            new = itemMap["Mold"](creator=self)
            new.xPosition = newPos[0]
            new.yPosition = newPos[1]
            self.container.addItems([new])
            new.startSpawn()

    def localSpawn(self):
        if not self.dead:
            new = itemMap["Mold"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            new.charges = 4
            self.container.addItems([new])
            new.startSpawn()

    def getLongInfo(self):
        satiation = 115
        if self.dead:
            satiation = 100
        return """
item: Bloom

description:
This is a mold bloom. 

you can eat it to gain %s satiation.
"""%(satiation)

    def destroy(self, generateSrcap=True):
        self.localSpawn()

        super().destroy(generateSrcap=False)

class SickBloom(Item):
    type = "SickBloom"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.sickBloom,xPosition,yPosition,creator=creator,name="sick bloom")
        self.walkable = True
        self.charges = 1
        self.dead = False
        self.attributesToStore.extend([
               "charges","dead"])
        self.initialState = self.getState()

    def apply(self,character):
        if self.charges and not self.dead:
            if isinstance(character,src.characters.Monster):
                if character.phase == 1:
                    character.satiation += 300
                    if character.satiation > 1000:
                        character.satiation = 1000
                    self.spawn()
                    self.charges -= 1
                    self.dead = True
                elif character.phase == 2:
                    character.enterPhase3()
                    self.charges -= 1
                    self.destroy(generateSrcap=False)
                else:
                    character.satiation += 400
                    self.charges -= 1
            else:
                self.spawn()
                character.satiation += 100
                if character.satiation > 1000:
                    character.satiation = 1000
        else:
            character.satiation += 100
            if character.satiation > 1000:
                character.satiation = 1000
            self.destroy(generateSrcap=False)
        character.messages.append("you eat the sick bloom and gain 100 satiation")

    def pickUp(self,character):
        self.bolted = False
        self.dead = True
        self.charges = 0
        super().pickUp(character)

    def startSpawn(self):
        event = src.events.RunCallbackEvent(gamestate.tick+(2*self.xPosition+3*self.yPosition+gamestate.tick)%2500,creator=self)
        event.setCallback({"container":self,"method":"spawn"})
        self.terrain.addEvent(event)

    def spawn(self):
        if not self.charges:
            return

        if self.dead:
            return

        character = characters.Monster(creator=self)

        character.solvers = [
                  "NaiveActivateQuest",
                  "ActivateQuestMeta",
                  "NaivePickupQuest",
                  "NaiveMurderQuest",
                ]

        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                    splittedCommand.append(char)
            return splittedCommand

        character.macroState["macros"]["w"] = splitCommand("wj")
        character.macroState["macros"]["a"] = splitCommand("aj")
        character.macroState["macros"]["s"] = splitCommand("sj")
        character.macroState["macros"]["d"] = splitCommand("dj")

        counter = 1
        command = ""
        import random
        directions =["w","a","s","d"]
        while counter < 8:
            command += "j%s_%s"%(random.randint(1,counter*4),directions[random.randint(0,3)])
            counter += 1
        character.macroState["macros"]["m"] = splitCommand(command+"_m")

        character.macroState["commandKeyQueue"] = [("_",[]),("m",[])]
        character.satiation = 10
        self.container.addCharacter(character,self.xPosition,self.yPosition)

        self.charges -= 1

    def getLongInfo(self):
        satiation = 115
        if self.dead:
            satiation = 100
        return """
item: SickBloom

description:
This is a mold bloom. Its spore sacks are swollen and developed a protective shell

you can eat it to gain %s satiation.
"""%(satiation)

    def destroy(self, generateSrcap=True):

        if not self.dead:
            new = itemMap["Mold"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])
            new.startSpawn()

        super().destroy(generateSrcap=False)

class PoisonBloom(Item):
    type = "PoisonBloom"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.poisonBloom,xPosition,yPosition,creator=creator,name="poison bloom")
        self.walkable = True
        self.dead = False
        self.attributesToStore.extend([
               "dead"])

    def apply(self,character):

        character.die()

        if not self.dead:
            new = itemMap["PoisonBush"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])

        character.messages.append("you eat the poison bloom and die")

        self.destroy(generateSrcap=False)

    def pickUp(self,character):
        self.bolted = False
        self.dead = True
        self.charges = 0
        super().pickUp(character)

    def getLongInfo(self):
        return """
name: poison bloom

description:
This is a mold bloom. Its spore sacks shriveled and are covered in green slime.

You can eat it to die.
"""%(satiation)

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

class PoisonBush(Item):
    type = "PoisonBush"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.poisonBush,xPosition,yPosition,creator=creator,name="poison bush")
        self.walkable = False
        self.charges = 0
        self.attributesToStore.extend([
               "charges"])
        self.initialState = self.getState()

    def apply(self,character):
        self.charges += 1
        if 100 > character.satiation:
            character.satiation = 0
        else:
            character.satiation -= 100

        if self.charges > 10:
            
            new = itemMap["EncrustedPoisonBush"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])
            
            self.container.removeItem(self)

        character.messages.append("you give your blood to the poison bush")

    def spawn(self,distance=1):
        if not (self.xPosition and self.yPosition):
            return
        direction = (2*self.xPosition+3*self.yPosition+gamestate.tick)%4
        import random
        direction = (random.randint(1,distance+1),random.randint(1,distance+1))
        newPos = (self.xPosition+direction[0]-5,self.yPosition+direction[1]-5)

        if newPos[0] < 1 or newPos[1] < 1 or newPos[0] > 15*15-2 or newPos[1] > 15*15-2:
            return

        if not (newPos in self.container.itemByCoordinates and len(self.container.itemByCoordinates[newPos])):
            new = itemMap["PoisonBloom"](creator=self)
            new.xPosition = newPos[0]
            new.yPosition = newPos[1]
            self.container.addItems([new])

    def getLongInfo(self):
        return "poison charges: %s"%(self.charges)

    def getLongInfo(self):
        return """
item: Poison Bush

description:
This a cluster of blooms with a network veins connecting them. Its spore sacks shriveled and are covered in green slime.

actions:
You can use it to loose 100 satiation.
"""%(satiation)

    def destroy(self, generateSrcap=True):
        new = itemMap["FireCrystals"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])

        character = characters.Exploder(creator=self)

        character.solvers = [
                  "NaiveActivateQuest",
                  "ActivateQuestMeta",
                  "NaivePickupQuest",
                  "NaiveMurderQuest",
                ]

        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                    splittedCommand.append(char)
            return splittedCommand

        command = ""
        if gamestate.tick%4 == 0:
            command += "A"
        if gamestate.tick%4 == 1:
            command += "W"
        if gamestate.tick%4 == 2:
            command += "S"
        if gamestate.tick%4 == 3:
            command += "D"

        if self.xPosition%4 == 0:
            command += "A"
        if self.xPosition%4 == 1:
            command += "W"
        if self.xPosition%4 == 2:
            command += "S"
        if self.xPosition%4 == 3:
            command += "D"

        if self.yPosition%4 == 0:
            command += "A"
        if self.yPosition%4 == 1:
            command += "W"
        if self.yPosition%4 == 2:
            command += "S"
        if self.yPosition%4 == 3:
            command += "D"

        character.macroState["macros"]["m"] = splitCommand(command+"_m")

        character.macroState["commandKeyQueue"] = [("_",[]),("m",[])]
        character.satiation = 100
        self.container.addCharacter(character,self.xPosition,self.yPosition)

        super().destroy(generateSrcap=False)

class EncrustedPoisonBush(Item):
    type = "EncrustedPoisonBush"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.encrustedPoisonBush,xPosition,yPosition,creator=creator,name="test")
        self.walkable = False

    def apply(self,character):
        if 100 > character.satiation:
            character.satiation = 0
        else:
            character.satiation -= 100

        character.messages.append("you give your blood to the encrusted poison bush and loose 100 satiation")

    def getLongInfo(self):
        return """
item: EncrustedPoisonBush

description:
This is a cluster of blooms. The veins developed a protecive shell and are dense enough to form a solid wall.
Its spore sacks shriveled and are covered in green slime.

actions:
You can use it to loose 100 satiation.
"""%(satiation)

    def destroy(self, generateSrcap=True):
        new = itemMap["FireCrystals"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        #new.startExploding()

        character = characters.Monster(creator=self)

        character.solvers = [
                  "NaiveActivateQuest",
                  "ActivateQuestMeta",
                  "NaivePickupQuest",
                  "NaiveMurderQuest",
                ]

        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                    splittedCommand.append(char)
            return splittedCommand

        command = "opc"
        if gamestate.tick%2:
            command += "$=aam$=ddm"
            command += "$=wwm$=ssm"
        else:
            command += "$=wwm$=ssm"
            command += "$=aam$=ddm"

        command += "_m"
        character.macroState["macros"]["m"] = splitCommand(command)

        character.macroState["commandKeyQueue"] = [("_",[]),("m",[])]
        character.satiation = 100
        self.container.addCharacter(character,self.xPosition,self.yPosition)

        super().destroy(generateSrcap=False)

class Bush(Item):
    type = "Bush"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.bush,xPosition,yPosition,creator=creator,name="bush")
        self.walkable = False
        self.charges = 10
        self.attributesToStore.extend([
               "charges"])
        self.initialState = self.getState()

    def apply(self,character):
        if self.charges > 10:
            new = itemMap["EncrustedBush"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])

            self.container.removeItem(self)

            character.messages.append("the bush encrusts")

        if self.charges:
            character.satiation += 5
            self.charges -= 1
            character.messages.append("you eat from the bush and gain 5 satiation")
        else:
            self.destroy()

    def getLongInfo(self):
        return "charges: %s"%(self.charges)

    def getLongInfo(self):
        return """
item: Bush

description:
This a patch of mold with multiple blooms and a network vains connecting them.

actions:
If you can eat it to gain 5 satiation.
"""%(satiation)

    def destroy(self, generateSrcap=True):
        new = itemMap["Coal"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        super().destroy(generateSrcap=False)

class EncrustedBush(Item):
    type = "EncrustedBush"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.encrustedBush,xPosition,yPosition,creator=creator,name="encrusted bush")
        self.walkable = False

    def getLongInfo(self):
        return """
item: EncrustedBush

description:
This is a cluster of blooms. The veins developed a protecive shell and are dense enough to form a solid wall.
Its spore sacks shriveled and are covered in green slime.

actions:
You can use it to loose 100 satiation.
"""%(satiation)

    def destroy(self, generateSrcap=True):
        new = itemMap["Coal"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])

        character = characters.Monster(creator=self)

        character.solvers = [
                  "NaiveActivateQuest",
                  "ActivateQuestMeta",
                  "NaivePickupQuest",
                  "NaiveMurderQuest",
                ]

        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                    splittedCommand.append(char)
            return splittedCommand

        character.macroState["macros"]["w"] = splitCommand("wj")
        character.macroState["macros"]["a"] = splitCommand("aj")
        character.macroState["macros"]["s"] = splitCommand("sj")
        character.macroState["macros"]["d"] = splitCommand("dj")

        counter = 1
        command = ""
        import random
        directions =["w","a","s","d"]
        while counter < 8:
            command += "j%s_%s"%(random.randint(1,counter*4),directions[random.randint(0,3)])
            counter += 1
        character.macroState["macros"]["m"] = splitCommand(command+"_m")

        character.macroState["commandKeyQueue"] = [("_",[]),("m",[])]
        character.satiation = 10
        self.container.addCharacter(character,self.xPosition,self.yPosition)

        super().destroy(generateSrcap=False)

class MoldFeed(Item):
    type = "MoldFeed"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.moldFeed,xPosition,yPosition,creator=creator,name="mold feed")
        self.walkable = True
        self.bolted = False

    def getLongInfo(self):
        return """
item: MoldFeed

description:

This is a good base for mold growth. If mold grows onto it, it will grow into a bloom.
"""

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

class SeededMoldFeed(Item):
    type = "SeededMoldFeed"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.seededMoldFeed,xPosition,yPosition,creator=creator,name="seeded mold feed")
        self.walkable = True
        self.bolted = False

    def apply(self,character):
        self.startSpawn()
        character.messages.append("you activate the seeded mold feed")

    def startSpawn(self):
        event = src.events.RunCallbackEvent(gamestate.tick+(2*self.xPosition+3*self.yPosition+gamestate.tick)%10,creator=self)
        event.setCallback({"container":self,"method":"spawn"})
        self.terrain.addEvent(event)

    def spawn(self):
        new = itemMap["Mold"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        new.charges = 8
        new.startSpawn()
        self.destroy(generateSrcap=False)

    def getLongInfo(self):
        return """
item: SeededMoldFeed

description:

This is mold feed mixed with mold spores. 
Place it on the ground and activate it to start mold growth.
The seeded mold feed grows stronger then a mold spore on its own.
"""

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

class BloomContainer(Item):
    type = "BloomContainer"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.bloomContainer,xPosition,yPosition,creator=creator,name="bloom container")

        self.charges = 0
        self.maxCharges = 15
        self.level = 1

        self.attributesToStore.extend([
               "charges","maxCharges","level"])
        self.initialState = self.getState()

    def getLongInfo(self):
        return """
item: BloomContainer

description:
The bloom container is used to carry an store blooms.

it has %s blooms (charges) in it. It can hold a maximum of %s blooms.

This is a level %s item.

actions:

= loading blooms =
prepare by placing the bloom container on the ground and placing blooms around the container.
Activate the bloom container and select the option "load bloom" to load the blooms into the container.

= unload blooms =
prepare by placing the bloom container on the ground.
Activate the bloom container and select the option "unload bloom" to unload the blooms to the east.
"""%(self.charges,self.maxCharges,self.level)

    def apply(self,character):
        options = []
        options.append(("load","load blooms"))
        options.append(("unload","unload blooms"))
        self.submenue = interaction.SelectionMenu("select the item to produce",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doSelection
        self.character = character

    def doSelection(self):
        selection = self.submenue.selection
        if selection == "load":
            if self.charges >= self.maxCharges:
                self.character.messages.append("bloom container full. no blooms loaded")
                return

            blooms = []
            positions = [(self.xPosition+1,self.yPosition),(self.xPosition-1,self.yPosition),(self.xPosition,self.yPosition+1),(self.xPosition,self.yPosition-1),]
            for position in positions:
                for item in self.container.getItemByPosition(position):
                    if item.type == "Bloom":
                        blooms.append(item)

            if not blooms:
                self.character.messages.append("no blooms to load")
                return

            for bloom in blooms:
                if self.charges >= self.maxCharges:
                    self.character.messages.append("bloom container full. not all blooms loaded")
                    return

                self.container.removeItem(bloom)
                self.charges += 1

            self.character.messages.append("blooms loaded")
            return

        elif selection == "unload":

            if self.charges == 0:
                self.character.messages.append("no blooms to unload")
                return
            
            foundWalkable = 0
            foundNonWalkable = 0
            for item in self.container.getItemByPosition((self.xPosition+1,self.yPosition)):
                if item.walkable:
                    foundWalkable += 1
                else:
                    foundNonWalkable += 1
            
            if foundWalkable > 0 or foundNonWalkable >= 15:
                self.character.messages.append("target area full. no blooms unloaded")
                return

            toAdd = []
            while foundNonWalkable <= 15 and self.charges:
                new = Bloom(creator=self)
                new.xPosition = self.xPosition+1
                new.yPosition = self.yPosition
                new.dead = True

                toAdd.append(new)
                self.charges -= 1
            self.container.addItems(toAdd)

class Container(Item):
    type = "Container"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        self.contained = []
        super().__init__(displayChars.container,xPosition,yPosition,creator=creator,name="container")

        self.charges = 0
        self.maxItems = 10
        self.level = 1

        self.attributesToStore.extend([
               "charges","maxCharges","level"])
        self.initialState = self.getState()

    def getLongInfo(self):
        text = """
item: Container

description:
The container is used to carry and store small items.

it holds the items. It can hold a maximum of %s items.

This is a level %s item.

"""%(self.maxItems,self.level)

        if self.contained:
            for item in self.contained:
                text += """
* %s
%s"""%(item.name,item.description)
        else:
            text += """
the container is empty
"""

        text += """ 

actions:

= load items =
prepare by placing the bloom container on the ground and placing the items to the east of the container.
Activate the bloom container and select the option "load items" to load the blooms into the container.

= unload items =
prepare by placing the container on the ground.
Activate the container and select the option "unload items" to unload the items.
"""
        return text
            
    def getState(self):
        state = super().getState()
        state["contained"] = []
        for item in self.contained:
            state["contained"].append(item.getState())
        return state

    def getDiffState(self):
        state = super().getDiffState()
        state["contained"] = []
        for item in self.contained:
            state["contained"].append(item.getState())
        return state

    def setState(self,state):
        super().setState(state)
        
        if "contained" in state:
            for item in state["contained"]:
                self.contained.append(getItemFromState(item))

    def apply(self,character):
        options = []
        options.append(("load","load items"))
        options.append(("unload","unload items"))
        self.submenue = interaction.SelectionMenu("select the item to produce",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doSelection
        self.character = character

    def doSelection(self):
        selection = self.submenue.selection
        if selection == "load":
            if len(self.contained) >= self.maxItems:
                self.character.messages.append("container full. no items loaded")
                return

            items = []
            for item in self.container.getItemByPosition((self.xPosition-1,self.yPosition)):
                if item.walkable:
                    items.append(item)


            if not items:
                self.character.messages.append("no small items to load")
                return

            for item in items:
                if len(self.contained) >= self.maxItems:
                    self.character.messages.append("container full. not all items loaded")
                    return

                self.contained.append(item)

                self.container.removeItem(item)
                self.charges += 1

            self.character.messages.append("items loaded")
            return

        elif selection == "unload":

            if self.charges == 0:
                self.character.messages.append("no items to unload")
                return
            
            foundWalkable = 0
            foundNonWalkable = 0
            for item in self.container.getItemByPosition((self.xPosition+1,self.yPosition)):
                if item.walkable:
                    foundWalkable += 1
                else:
                    foundNonWalkable += 1
            
            if foundWalkable > 0 or foundNonWalkable >= 15:
                self.character.messages.append("target area full. no items unloaded")
                return

            toAdd = []
            while foundNonWalkable <= 15 and self.contained:
                new = self.contained.pop()
                new.xPosition = self.xPosition+1
                new.yPosition = self.yPosition

                toAdd.append(new)
            self.container.addItems(toAdd)


class TrailHead(Item):
    type = "TrailHead"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(displayChars.floor_node,xPosition,yPosition,creator=creator,name="encrusted bush")
        self.walkable = False
        targets = []

    def getLongInfo(self):
        return """
item: TrailHead

description:
You can use it to create paths
"""

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
            "Display":RoomControls,
            "RoomControls":RoomControls,
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
            "Mount":Mount,
            "Tank":Tank,
            "Frame":Frame,
            "Radiator":Radiator,
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
            "InfoScreen":AutoTutor,
            "AutoTutor":AutoTutor,
            "CoalMine":CoalMine,
            "RoomBuilder":RoomBuilder,
            "BluePrinter":BluePrinter,
            "BluePrint":BluePrint,
            "StasisTank":StasisTank,
            "PositioningDevice":PositioningDevice,
            "Watch":Watch,
            "SimpleRunner":SimpleRunner,
            "MemoryStack":MemoryStack,
            "MemoryReset":MemoryReset,
            "BackTracker":BackTracker,
            "Tumbler":Tumbler,
            "ItemUpgrader":ItemUpgrader,
            "ItemDowngrader":ItemDowngrader,
            "GlobalMacroStorage":GlobalMacroStorage,
            "MacroRunner":MacroRunner,
            "GameTestingProducer":GameTestingProducer,
            "MemoryCell":MemoryCell,
            "Case":Case,
            "Command":Command,
            "Note":Note,
            "PocketFrame":PocketFrame,
            "Bomb":Bomb,
            "Mortar":Mortar,
            "Explosive":Explosive,
            "ReactionChamber":ReactionChamber,
            "Explosion":Explosion,
            "Chute":Chute,
            "Chemical":Chemical,
            "Spawner":Spawner,
            "Moss":Mold,
            "Mold":Mold,
            "MossSeed":MoldSpore,
            "MoldSpore":MoldSpore,
            "Bloom":Bloom,
            "Sprout":Sprout,
            "Sprout2":Sprout2,
            "SickBloom":SickBloom,
            "PoisonBloom":PoisonBloom,
            "Bush":Bush,
            "PoisonBush":PoisonBush,
            "EncrustedBush":EncrustedBush,
            "BloomShredder":BloomShredder,
            "SporeExtractor":SporeExtractor,
            "Test":EncrustedPoisonBush,
            "EncrustedPoisonBush":EncrustedPoisonBush,
            "AutoScribe":AutoScribe,
            "FloorPlate":FloorPlate,
            "CommandBook":CommandBook,
            "FireCrystals":FireCrystals,
            "Map":Map,
            "Mover":Mover,
            "PortableChallenger":PortableChallenger,
            "MoldFeed":MoldFeed,
            "SeededMoldFeed":SeededMoldFeed,
            "BloomContainer":BloomContainer,
            "Container":Container,
            "CorpseShredder":CorpseShredder,
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
            "RoomControls":RoomControls,
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
            "Command":Command,
            "Rod":Rod,
            "Heater":Heater,
            "Mount":Mount,
            "Tank":Tank,
            "Radiator":Radiator,
            "MaggotFermenter":MaggotFermenter,
            "BioPress":BioPress,
            "GooProducer":GooProducer,
            "GooDispenser":GooDispenser,
            "GooFlask":GooFlask,
            "Sorter":Sorter,
            "MemoryBank":MemoryBank,
            "MemoryDump":MemoryDump,
            "MemoryStack":MemoryStack,
            "PocketFrame":PocketFrame,
        }

'''
get item instances from dict state
'''
def getItemFromState(state):
    item = itemMap[state["type"]](creator=void,noId=True)
    item.setState(state)
    if "id" in state:
        item.id = state["id"]
    loadingRegistry.register(item)
    return item

