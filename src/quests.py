import src.items as items

# HACK: common variables with modules
showCinematic = None
loop = None
callShow_or_exit = None

'''
the base class for all quests
'''
class Quest(object):
    '''
    straightforward state initialization
    '''
    def __init__(self,followUp=None,startCinematics=None,lifetime=0):
        self.followUp = followUp # deprecate?
        self.character = None # should be more general like owner as preparation for room quests
        self.listener = [] # the list of things caring about this quest. The owner for example
        self.active = False # active as in started
        self.completed = False 
        self.startCinematics = startCinematics # deprecate?
        self.endCinematics = None # deprecate?
        self.startTrigger = None # deprecate?
        self.endTrigger = None # deprecate?
        self.paused = False
        self.reputationReward = 0
        self.watched = []

        self.lifetime = lifetime

    def startWatching(self, target, callback):
        target.addListener(callback)
        self.watched.append((target,callback))
    
    def stopWatching(self, target, callback):
        target.delListener(callback)
        self.watched.remove((target,callback))

    def stopWatchingAll(self):
        for listenItem in self.watched[:]:
            self.stopWatching(listenItem[0],listenItem[1])


    '''
    check whether the quest is solved or not (and trigger teardown if quest is solved)
    '''
    def triggerCompletionCheck(self):
        if not self.active:
            return 
        pass

    '''
    do one action to solve the quest, is intended to be overwritten heavily. returns None if there can't be done anything
    should be rewritten so it returns an actual list of steps
    '''
    def solver(self,character):
        if self.paused:
            return True
        else:
            return character.walkPath()

    '''
    pause the quest
    '''
    def pause(self):
        self.paused = True

    '''
    unpause the quest
    '''
    def unpause(self):
        self.paused = False

    '''
    handle a failure to resolve te quest
    '''
    def fail(self):
        self.postHandler()
    
    '''
    get the quests description
    bad code: colored and asList are somewhat out of place
    '''
    def getDescription(self,asList=False,colored=False,active=False):
        if asList:
            if colored:
                import urwid
                if active:
                    color = "#0f0"
                else:
                    color = "#090"
                return [[(urwid.AttrSpec(color,"default"),self.description),"\n"]]
            else:
                return [[self.description,"\n"]]
        else:
            return self.description

    '''
    tear the quest down
    bad code: self.character should be checked at the beginning
    '''
    def postHandler(self):
        self.stopWatchingAll()

        if not self.active:
            debugMessages.append("this should not happen (posthandler called on inactive quest ("+str(self)+")) "+str(self.character))
            return

        if self.completed:
            debugMessages.append("this should not happen (posthandler called on completed quest ("+str(self)+")) "+str(self.character))
            if self.character and self in self.character.quests:
                # remove quest
                startNext = False
                if self.character.quests[0] == self:
                    startNext = True
                self.character.quests.remove(self)

                # start next quest
                if startNext:
                    if self.followUp:
                        self.character.assignQuest(self.followUp,active=True)
                    else:
                        self.character.startNextQuest()
            return

        # flag self as completed
        self.completed = True

        # TODO: handle quests with no assigned character
        if self.character and self in self.character.quests:
            # remove self from characters quest list
            # bad code: direct manipulation
            startNext = False
            if self.character.quests[0] == self:
                startNext = True
            self.character.quests.remove(self)

            # start next quest
            if startNext:
                self.character.startNextQuest()

        # trigger follow ups
        # these should be a unified way to to this. probably an event
        if self.endTrigger:
            self.endTrigger()
        if self.endCinematics:
            showCinematic(self.endCinematics)            
            loop.set_alarm_in(0.0, callShow_or_exit, '.')

        # dactivate
        self.deactivate()

        # start next quest
        if self.character:
            if self.followUp:
                self.character.assignQuest(self.followUp,active=True)
            else:
                self.character.startNextQuest()

    '''
    assign the quest to a character
    bad code: this would be a contructor param, but this may be used for reassigning quests
    '''
    def assignToCharacter(self,character):
        self.character = character
        self.recalculate()
        if self.active:
            self.character.setPathToQuest(self)

    '''
    recalculate the internal state of the quest
    this is usually called as a listener function
    also used when the player moves leaves the path
    '''
    def recalculate(self):
        if not self.active:
            return 

        self.triggerCompletionCheck()

    '''
    notify listeners that something changed
    '''
    def changed(self):
        # call the listener functions
        # should probably be an event not a function
        for listener in self.listener:
            listener()

    '''
    add a callback to be called if the quest changes
    '''
    def addListener(self,listenFunction):
        if not listenFunction in self.listener:
            self.listener.append(listenFunction)

    '''
    remove a callback to be called if the quest changes
    '''
    def delListener(self,listenFunction):
        if listenFunction in self.listener:
            self.listener.remove(listenFunction)

    '''
    switch from just existing to active
    '''
    def activate(self):
        # flag self as active
        self.active = True

        # trigger startup actions
        # bad code: these should be a unified way to to this. probably an event
        if self.startTrigger:
            self.startTrigger()
        if self.startCinematics:
            showCinematic(self.startCinematics)            
            loop.set_alarm_in(0.0, callShow_or_exit, '.')

        # add automatic termination
        if self.lifetime:
            '''
            the event for automatically terminating the quest
            '''
            class endQuestEvent(object):
                '''
                straightforward state setting
                '''
                def __init__(subself,tick):
                    subself.tick = tick

                '''
                terminate the quest
                '''
                def handleEvent(subself):
                    self.postHandler()

            self.character.addEvent(endQuestEvent(gamestate.tick+self.lifetime))

        # recalculate uns notify listeners
        self.recalculate()
        self.changed()

    '''
    switch from active to just existing
    '''
    def deactivate(self):
        self.active = False
        self.changed()

############################################################
###
##  the basic most quests like moving or activating something
#
############################################################

'''
make a character move somewhere
bad code: is to be replaced by MoveQuestMeta but switch is not done yet
'''
class MoveQuest(Quest):
    '''
    straightfoward state setting
    '''
    def __init__(self,room,x,y,sloppy=False,followUp=None,startCinematics=None):
        self.dstX = x
        self.dstY = y
        self.targetX = x
        self.targetY = y
        self.room = room
        self.sloppy = sloppy
        self.description = "please go to coordinate "+str(self.dstX)+"/"+str(self.dstY)    
        super().__init__(followUp,startCinematics=startCinematics)
        self.listeningTo = []

    '''
    check if character is in the right place
    bad code: should check for correct room, too
    '''
    def triggerCompletionCheck(self):
        # a inactive quest cannot complete
        if not self.active:
            # bad code: should write a "this should not happen" log entry
            return 
        if hasattr(self,"dstX") and hasattr(self,"dstY"): # bad code: should do nothing
            if not self.sloppy:
                # check for exact position
                if self.character.xPosition == self.dstX and self.character.yPosition == self.dstY and self.character.room == self.room:
                    self.postHandler()
            else:
                # check for neighbouring position
                if self.character.room == self.room and((self.character.xPosition-self.dstX in (1,0,-1) and self.character.yPosition == self.dstY) or (self.character.yPosition-self.dstY in (1,0,-1) and self.character.xPosition == self.dstX)):
                    self.postHandler()

    '''
    assign to character and add listener
    bad code: should be more specific regarding what to listen
    '''
    def assignToCharacter(self,character):
        super().assignToCharacter(character)
        self.startWatching(character,self.recalculate)

    '''
    split up the quest into subquest if nesseccary
    bad code: action does not fit to the methods name
    '''
    def recalculate(self):
        # do not recalculate inactive quests
        # bad code: should log a warning
        if not self.active:
            return 

        # delete current target position
        if hasattr(self,"dstX"):
            del self.dstX
        if hasattr(self,"dstY"):
            del self.dstY

        # do not try to move character if there is no character
        # bad code: should log a warning
        if not self.character:
            return

        if (self.room == self.character.room):
            # set target coordinates to the actual target
            self.dstX = self.targetX
            self.dstY = self.targetY

        elif self.character.room and self.character.quests and self.character.quests[0] == self:
            # make the character leave the room
            # bad code: adds a new quest instead of using sub quests
            self.character.assignQuest(LeaveRoomQuest(self.character.room),active=True)
        elif not self.character.room and self.character.quests and self.character.quests[0] == self:
            # make the character enter the correct room
            # bad code: adds a new quest instead of using sub quests
            self.character.assignQuest(EnterRoomQuest(self.room),active=True)
            pass # bad code: does nothing
        super().recalculate()

'''
quest to activate something
bad code: is to be replaced by ActivateQuestMeta but switch is not done yet
'''
class ActivateQuest(Quest):
    '''
    straightfoward state setting
    '''
    def __init__(self,toActivate,followUp=None,desiredActive=True,startCinematics=None):
        self.toActivate = toActivate
        self.dstX = self.toActivate.xPosition
        self.dstY = self.toActivate.yPosition
        self.desiredActive = desiredActive
        self.description = "please activate the "+self.toActivate.name+" ("+str(self.toActivate.xPosition)+"/"+str(self.toActivate.yPosition)+")"
        super().__init__(followUp,startCinematics=startCinematics)
        self.startWatching(self.toActivate,self.recalculate)
        self.startWatching(self.toActivate,self.triggerCompletionCheck)

    '''
    check if target has the desired state
    '''
    def triggerCompletionCheck(self):
        if self.toActivate.activated == self.desiredActive:
            self.postHandler()

    '''
    split the quest into sub quests
    bad code: 
    '''
    def recalculate(self):
        # do not recalculate inactive quests
        if not self.active:
            return

        # go to the room the item is in
        if ((not self.character.room) or (not self.character.room == self.toActivate.room)) and self.character.quests[0] == self:
            self.character.assignQuest(EnterRoomQuest(self.toActivate.room),active=True)

        # remove current destination
        if hasattr(self,"dstX"):
            del self.dstX
        if hasattr(self,"dstY"):
            del self.dstY

        # set item to activate as target
        if hasattr(self,"toActivate"):
            if hasattr(self.toActivate,"xPosition"):
                self.dstX = self.toActivate.xPosition
            if hasattr(self.toActivate,"xPosition"):
                self.dstY = self.toActivate.yPosition

        super().recalculate()

    '''
    walk path and then activate
    '''
    def solver(self,character):
        if super().solver(character):
            self.toActivate.apply(character)
            return True

'''
quest to leave the room
'''
class LeaveRoomQuest(Quest):
    def __init__(self,room,followUp=None,startCinematics=None):
        self.room = room
        self.description = "please leave the room."
        self.dstX = self.room.walkingAccess[0][0]
        self.dstY = self.room.walkingAccess[0][1]
        super().__init__(followUp,startCinematics=startCinematics)

    '''
    move to door and step out of the room
    '''
    def solver(self,character):
        if super().solver(character):
            if character.room:
                # close door
                for item in character.room.itemByCoordinates[(character.xPosition,character.yPosition)]:
                    item.close()

                # add step out of the room
                if character.yPosition == 0:
                    character.path.append((character.xPosition,character.yPosition-1))
                elif character.yPosition == character.room.sizeY-1:
                    character.path.append((character.xPosition,character.yPosition+1))
                if character.xPosition == 0: #bad code: should be elif
                    character.path.append((character.xPosition-1,character.yPosition))
                elif character.xPosition == character.room.sizeX-1:
                    character.path.append((character.xPosition+1,character.yPosition))
                character.walkPath()
                return False
            return True

    '''
    assign to and listen to character
    '''
    def assignToCharacter(self,character):

        super().assignToCharacter(character)
        self.startWatching(character,self.recalculate)

        super().recalculate()

    '''
    check if the character left the room
    '''
    def triggerCompletionCheck(self):
        # do nothing on inactive quest
        if not self.active:
            return 

        # do nothing without character
        if not self.character:
            return

        # trigger followup when done
        if not self.character.room == self.room:
            self.postHandler()

'''
quest to enter a room
bad code: is to be repaced by EnterRoomQuestMeta but switch is not done yet
'''
class EnterRoomQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,room,followUp=None,startCinematics=None):
        self.description = "please enter the room: "+room.name+" "+str(room.xPosition)+" "+str(room.yPosition)
        self.room = room
        # set door as target
        self.dstX = self.room.walkingAccess[0][0]+room.xPosition*15+room.offsetX
        self.dstY = self.room.walkingAccess[0][1]+room.yPosition*15+room.offsetY
        super().__init__(followUp,startCinematics=startCinematics)

    '''
    assign character and 
    '''
    def assignToCharacter(self,character):
        super().assignToCharacter(character)
        self.startWatching(character,self.recalculate)

    '''
    walk to target
    bad code: does nothing?
    '''
    def solver(self,character):
        if character.walkPath():
            return True
        return False

    '''
    leave room and go to target
    '''
    def recalculate(self):
        if not self.active:
            return 

        if self.character.room and not self.character.room == self.room and self.character.quests[0] == self:
            self.character.assignQuest(LeaveRoomQuest(self.character.room),active=True)

        super().recalculate()

    '''
    close door and call superclass
    '''
    def postHandler(self):
        if self.character.yPosition in (self.character.room.walkingAccess):
            for item in self.character.room.itemByCoordinates[self.character.room.walkingAccess[0]]:
                item.close()

        super().postHandler()

    '''
    check if the character is in the correct roon
    '''
    def triggerCompletionCheck(self):
        # bad code: 
        if not self.active:
            return 

        # start teardown when done
        if self.character.room == self.room:
            self.postHandler()

'''
quest to pick up an item
bad code: is to be replaced by PickupQuestMeta but switch is not done yet
'''
class PickupQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,toPickup,followUp=None,startCinematics=None):
        self.toPickup = toPickup
        self.startWatching(self.toPickup,self.recalculate)
        self.startWatching(self.toPickup,self.triggerCompletionCheck)
        self.dstX = self.toPickup.xPosition
        self.dstY = self.toPickup.yPosition
        self.description = "please pick up the "+self.toPickup.name+" ("+str(self.toPickup.xPosition)+"/"+str(self.toPickup.yPosition)+")"
        super().__init__(followUp,startCinematics=startCinematics)

    '''
    check whether the item is in the mainchars inventory
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if self.toPickup in self.character.inventory:
                self.postHandler()

    '''
    set item as target
    '''
    def recalculate(self):
        if self.active:
            # remove current target
            if hasattr(self,"dstX"):
                del self.dstX
            if hasattr(self,"dstY"):
                del self.dstY

            # set item as target
            if hasattr(self,"toPickup"):
                if hasattr(self.toPickup,"xPosition"):
                    self.dstX = self.toPickup.xPosition
                if hasattr(self.toPickup,"xPosition"):
                    self.dstY = self.toPickup.yPosition
            super().recalculate()

    '''
    move to target and pick up
    '''
    def solver(self,character):
        if super().solver(character) or (len(character.path) == 1 and self.toPickup.walkable == False):
            self.toPickup.pickUp(character)
            self.triggerCompletionCheck()
            return True

'''
The naive pickup quest. It assumes nothing goes wrong. 
You probably want to use PickupQuest instead
'''
class NaivePickupQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,toPickup,followUp=None,startCinematics=None):
        self.toPickup = toPickup
        self.dstX = self.toPickup.xPosition
        self.dstY = self.toPickup.yPosition
        super().__init__(followUp,startCinematics=startCinematics)
        self.startWatching(self.toPickup,self.recalculate)
        self.startWatching(self.toPickup,self.triggerCompletionCheck)
        self.description = "naive pickup"
   
    '''
    check wnether item is in characters inventory
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if self.toPickup in self.character.inventory:
                self.postHandler()

    '''
    pick up the item
    '''
    def solver(self,character):
        self.toPickup.pickUp(character)
        return True

'''
The naive quest to get a quest from somebody. It assumes nothing goes wrong. 
You probably want to use GetQuest instead
'''
class NaiveGetQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,questDispenser,assign=True,followUp=None,startCinematics=None):
        self.questDispenser = questDispenser
        self.quest = None
        self.assign = assign
        super().__init__(followUp,startCinematics=startCinematics)
        self.description = "naive get quest"

    '''
    check wnether the chracter has gotten a quest
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if self.quest:
                self.postHandler()

    '''
    get quest directly from quest dispenser
    '''
    def solver(self,character):
        # get quest
        self.quest = self.questDispenser.getQuest()

        # fail if there is no quest
        if not self.quest:
            self.fail()
            return True

        # assign quest
        if self.assign:
            self.character.assignQuest(self.quest,active=True)

        # trigger cleanuo
        self.triggerCompletionCheck()
        return True

'''
The naive quest to fetch the reward for a quest. It assumes nothing goes wrong. 
You probably want to use GetReward instead
'''
class NaiveGetReward(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,quest,followUp=None,startCinematics=None):
        super().__init__(followUp,startCinematics=startCinematics)
        self.quest = quest
        self.description = "naive get reward"
        self.done = False

    '''
    check for a done flag
    bad code: general pattern is to actually check if the reward was given
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if self.done:
                self.postHandler()

    '''
    assign reward
    bad code: rwarding should be handled within the quest
    '''
    def solver(self,character):
        character.reputation += self.quest.reputationReward
        if character == mainChar:
            messages.append("you were awarded "+str(self.quest.reputationReward)+" reputation")
        self.done = True
        self.triggerCompletionCheck()
        return True

'''
The naive quest to murder someone. It assumes nothing goes wrong. 
You probably want to use MurderQuest instead
'''
class NaiveMurderQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,toKill,followUp=None,startCinematics=None):
        self.toKill = toKill
        super().__init__(followUp,startCinematics=startCinematics)
        self.description = "naive murder"

    '''
    check whether target is dead
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if self.toKill.dead:
                self.postHandler()

    '''
    kill the target
    bad code: murdering should happen within a character
    '''
    def solver(self,character):
        self.toKill.die()
        self.triggerCompletionCheck()
        return True

'''
The naive quest to activate something. It assumes nothing goes wrong. 
You probably want to use ActivateQuest instead
'''
class NaiveActivateQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,toActivate,followUp=None,startCinematics=None):
        self.toActivate = toActivate
        super().__init__(followUp,startCinematics=startCinematics)
        self.description = "naive activate "+str(self.toActivate)
        self.activated = False

    def registerActivation(self,info):
        if self.toActivate == info:
            self.activated = True
            self.triggerCompletionCheck()

    def assignToCharacter(self,character):
        super().assignToCharacter(character)
        self.character.addListener(self.registerActivation,"activate")

    '''
    check wnether target was activated
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if self.activated:
                self.postHandler()

    '''
    activate the target
    bad code: sucess state is used instead of state checking
    '''
    def solver(self,character):
        self.toActivate.apply(character)
        return True

'''
The naive quest to drop something. It assumes nothing goes wrong. 
You probably want to use ActivateQuest instead
'''
class NaiveDropQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,toDrop,room,xPosition,yPosition,followUp=None,startCinematics=None):
        self.dstX = xPosition
        self.dstY = yPosition
        self.room = room
        self.toDrop = toDrop
        super().__init__(followUp,startCinematics=startCinematics)
        self.startWatching(self.toDrop,self.recalculate)
        self.startWatching(self.toDrop,self.triggerCompletionCheck)
        self.description = "naive drop"
        self.dropped = False

    '''
    check wnether item was dropped
    '''
    def triggerCompletionCheck(self):
        if self.active:
            # bad code: commented out code
            """
            does this make sense to use for naive?
            correctPosition = False
            try:
                if self.toDrop.xPosition == self.dstX and self.toDrop.yPosition == self.dstY:
                    correctPosition = True
            except:
                pass

            if correctPosition:
                messages.append("droped at correct location")
                self.postHandler()
            """
            if self.dropped:
                self.postHandler()

    '''
    drop item
    bad code: success attribute instead of checking world state
    '''
    def solver(self,character):
        self.dropped = True
        character.drop(self.toDrop)
        return True

'''
The naive quest to drop something. It assumes nothing goes wrong. 
You probably want to use ActivateQuest instead
'''
class NaiveDelegateQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,quest):
        super().__init__()
        self.quest = quest
        self.description = "naive delegate quest"
        self.startWatching(self.quest,self.triggerCompletionCheck)
    
    '''
    check if the quest has a character assigned
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if self.quest.character:
                self.postHandler()

    '''
    assign quest to first subordinate
    '''
    def solver(self,character):
        character.subordinates[0].assignQuest(self.quest,active=True)
        return True

'''
quest to drop something somewhere
bad code: this is to be replaced by DropQuestMeta but switch is not done yet
'''
class DropQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,toDrop,room,xPosition,yPosition,followUp=None,startCinematics=None):
        self.toDrop = toDrop
        self.startWatching(self.toDrop,self.recalculate)
        self.startWatching(self.toDrop,self.triggerCompletionCheck)
        self.dstX = xPosition
        self.dstY = yPosition
        self.room = room
        self.description = "please drop the "+self.toDrop.name+" at ("+str(self.dstX)+"/"+str(self.dstY)+")"
        super().__init__(followUp,startCinematics=startCinematics)

    '''
    check whether item is placed correctly
    '''
    def triggerCompletionCheck(self):
        correctPosition = False
        # bad code: this exception handling is confusing
        try:
            if self.toDrop.xPosition == self.dstX and self.toDrop.yPosition == self.dstY and self.toDrop.room == self.room:
                correctPosition = True
        except:
            pass
        if correctPosition:
            self.postHandler()

    '''
    move to target and drop item
    '''
    def solver(self,character):
        if super().solver(character):
            if self.toDrop in character.inventory:
                self.character.drop(self.toDrop)
                self.triggerCompletionCheck()
                return True
            else:
                return False

'''
quest to collect a item with some property
bad code: this is to be replaced by CollectQuestMeta but switch is not done yet
'''
class CollectQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,toFind="canBurn",startCinematics=None):
        self.toFind = toFind
        self.description = "please fetch things with property: "+toFind
        foundItem = None

        super().__init__(startCinematics=startCinematics)

    '''
    check if item to collect is in inventory
    '''
    def triggerCompletionCheck(self):
        # do not check if not properly active
        if not self.active:
            return 
        if not self.character:
            return

        # search inventory for item 
        foundItem = None
        for item in self.character.inventory:
            hasProperty = False
            try:
                hasProperty = getattr(item,self.toFind)
            except:
                continue
            if hasProperty:
                foundItem = item

        # trigger cleanup if item was found
        if foundItem:
            self.postHandler()

    '''
    assign to character and listen to the character
    '''
    def assignToCharacter(self,character):
        super().assignToCharacter(character)
        self.startWatching(self.character,self.recalculate)

    '''
    set target to item with correct property
    '''
    def recalculate(self):
        # bad code: remove current position
        if hasattr(self,"dstX"):
            del self.dstX
        if hasattr(self,"dstY"):
            del self.dstY

        # do nothing if inactive
        if not self.active:
            return 

        try:
            # bad code: confusing excetion handling
            for item in self.character.room.itemsOnFloor:
                hasProperty = False
                try:
                    hasProperty = getattr(item,"contains_"+self.toFind)
                except:
                    continue
                if hasProperty:
                    foundItem = item
                    # commented out code
                    # This line ist good but looks bad in current setting. reactivate later
                    #break

            # set target to item
            if foundItem:
                self.dstX = foundItem.xPosition
                self.dstY = foundItem.yPosition
        except:
            pass
        super().recalculate()

'''
wait until quest is aborted
'''
class WaitQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,followUp=None,startCinematics=None,lifetime=None):
        self.description = "please wait"
        super().__init__(lifetime=lifetime)

    '''
    do nothing
    '''
    def solver(self,character):
        return True

'''
wait till something was deactivated
'''
class WaitForDeactivationQuest(Quest):
    '''
    state initialization
    '''
    def __init__(self,item,followUp=None,startCinematics=None,lifetime=None):
        self.item = item
        self.description = "please wait for deactivation of "+self.item.description

        # listen to item
        self.startWatching(self.item,self.recalculate)

        super().__init__(lifetime=lifetime)
        self.pause() # bad code: why pause by default

    '''
    check if item is inactive
    '''
    def triggerCompletionCheck(self):
        if not self.item.activated:
            self.postHandler()

    '''
    do nothing
    '''
    def solver(self,character):
        return True

'''
wail till a specific quest was completed
'''
class WaitForQuestCompletion(Quest):
    '''
    state initialization
    '''
    def __init__(self,quest):
        self.quest = quest
        self.startWatching(self.quest,self.triggerCompletionCheck)
        self.description = "please wait for the quest to completed"
        super().__init__()

    '''
    check if the quest was completed
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if self.quest.completed:
                self.postHandler()

    '''
    do nothing
    '''
    def solver(self,character):
        return True

############################################################
###
##  furnace specific quests
#
############################################################

'''
the quest to fire a furnace
bad code: is to be replaced FireFurnaceMeta but switch is not done yet
'''
class FireFurnace(Quest):
    '''
    state initialization
    '''
    def __init__(self,furnace,followUp=None,startCinematics=None,lifetime=None):
        self.furnace = furnace
        self.description = "please fire the "+self.furnace.name+" ("+str(self.furnace.xPosition)+"/"+str(self.furnace.yPosition)+")"
        self.dstX = self.furnace.xPosition
        self.dstY = self.furnace.yPosition
        self.desiredActive = True
        self.collectQuest = None
        self.activateFurnaceQuest = None
        super().__init__(followUp,startCinematics=startCinematics)
        self.startWatching(self.furnace,self.recalculate)

    '''
    assign to character and listen to character
    '''
    def assignToCharacter(self,character):
        super().assignToCharacter(character)
        self.startWatching(self.character,self.recalculate)

    '''
    check wnether furnace is active
    '''
    def triggerCompletionCheck(self):
        if not self.active:
            return 

        if self.furnace.activated == self.desiredActive:
            self.postHandler()

    '''
    collect fuel and activate furnace
    '''
    def recalculate(self):
        # do nothing on inactive quest
        if not self.active:
            return 

        # call superclass handler when done
        if self.furnace.activated:
            super().recalculate()
            return 

        # check if the character has fuel in inventory
        foundItem = None
        for item in self.character.inventory:
            try:
                canBurn = item.canBurn
            except:
                continue
            if not canBurn:
                continue
            foundItem = item

        # add fuel colloction quest
        if not foundItem:
            if not self.collectQuest:
                self.collectQuest = CollectQuestMeta()
                self.character.assignQuest(self.collectQuest,active=True)
            return

        # add activate quest
        if not self.activateFurnaceQuest:
            self.activateFurnaceQuest = ActivateQuestMeta(self.furnace,desiredActive=True)
            self.character.assignQuest(self.activateFurnaceQuest,active=True)
            return

        # tear down when done
        self.triggerCompletionCheck()
        super().recalculate()

'''
the quest to fire a list of furnaces and keep them fired
bad code: is to be replaced KeepFurnacesFiredMeta but switch is not done yet
'''
class KeepFurnacesFired(Quest):
    '''
    state initialization
    '''
    def __init__(self,furnaces,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        self.furnaces = furnaces
        self.failTrigger = failTrigger
        self.keepFurnaceFiredQuests = {}
        self.metaQuest = None
        self.metaQuest2 = None
        self.fetchQuest = None
        self.description = "please fire the furnaces"
        self.startWatching(self.furnaces[0],self.recalculate)
        super().__init__(followUp=followUp,startCinematics=startCinematics,lifetime=lifetime)

    '''
    do nothing
    '''
    def solver(self,character):
        return True

    '''
    collect coal and fire furnaces
    '''
    def recalculate(self):
        # do nothing on inactive quest
        if not self.active:
            return 

        # be inactive by default
        self.pause() 
        
        """
        LEVEL2:
        """
        # remove sub quest
        if self.metaQuest2 and self.metaQuest2.completed:
            self.metaQuest2 = None

        # add activate quest and unpause
        # bad code: useless if
        if not self.metaQuest2:
            for furnace in reversed(self.furnaces):
                if not furnace.activated:
                    quest = ActivateQuest(furnace)
                    if not self.metaQuest2:
                        self.metaQuest2 = quest
                    self.character.assignQuest(quest,active=True)
                    self.unpause()
        else:
            self.unpause()

        # bad code: commented out code
        """
        LEVEL1:
        if not self.metaQuest:
            for furnace in self.furnaces[2:]:
                if not furnace in self.keepFurnaceFiredQuests:
                    quest = KeepFurnaceFired(furnace)
                    quest.inventoryThreshold = 11-len(self.furnaces)
                    self.character.assignQuest(quest,active=True)

                    self.keepFurnaceFiredQuests[furnace] = quest
            self.metaQuest = True
        """

        # collect coal if there is nothing to do
        if len(self.character.inventory) <= 11-len(self.furnaces) and (not self.fetchQuest or not self.fetchQuest.active):
            quest = FillPocketsQuest()
            self.character.assignQuest(quest,active=True)
            self.fetchQuest = quest
            self.unpause()
        
        super().recalculate()

'''
fire a furnace and keep it burning
bad code: is to be replaced KeepFurnaceFiredMeta but switch is not done yet
'''
class KeepFurnaceFired(Quest):
    '''
    state initialization
    '''
    def __init__(self,furnace,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        self.furnace = furnace
        self.startWatching(self.furnace,self.recalculate)
        self.description = "please fire the "+self.furnace.name+" ("+str(self.furnace.xPosition)+"/"+str(self.furnace.yPosition)+")"
        self.dstX = self.furnace.xPosition
        self.dstY = self.furnace.yPosition
        self.desiredActive = True
        self.collectQuest = None
        self.activateFurnaceQuest = None
        self.boilers = None
        self.failTrigger = failTrigger
        self.inventoryThreshold = 2
        super().__init__(followUp,startCinematics=startCinematics,lifetime=lifetime)

    '''
    assign to character and listen to the character
    '''
    def assignToCharacter(self,character):
        super().assignToCharacter(character)

        # listen to character
        self.startWatching(self.character,self.recalculate)

        # store and listen to affected boilers
        self.boilers = self.furnace.boilers
        if self.boilers:
            for boiler in self.boilers:
                def fail():
                    self.fail(boiler)
                self.startWatching(self.boiler,fail)

    '''
    check if a boiler stopped boiling and trigger the callback
    bad code: should be called checkFail or something
    '''
    def fail(self,boiler):
        # do nothing on inactive quest
        if not self.active:
            return 

        # actually fail if a boiler stopped boiling
        if not boiler.isBoiling:
            if self.failTrigger:
                self.failTrigger()

    '''
    never complete
    '''
    def triggerCompletionCheck(self):
        if not self.active:
            return 
        
    '''
    never complete
    '''
    def recalculate(self):
        # do nothing on inactive quest
        if not self.active:
            return 

        # be unpaused by default
        self.unpause()

        # remove inactive subquests
        if self.collectQuest and not self.collectQuest.active:
            self.collectQuest = None
        if self.activateFurnaceQuest and not self.activateFurnaceQuest.active:
            self.activateFurnaceQuest = None

        # collect fuel if there is nothing better to do
        if self.furnace.activated:
            if not self.collectQuest and not len(self.character.inventory) > self.inventoryThreshold and self.character.quests[0] == self:
                self.collectQuest = FillPocketsQuest()
                self.collectQuest.activate()
                self.character.assignQuest(self.collectQuest,active=True)
            else:
                self.pause()

            super().recalculate()
            return 

        # search characters inventory for fuel
        foundItem = None
        for item in self.character.inventory:
            try:
                canBurn = item.canBurn
            except:
                continue
            if not canBurn:
                continue
            foundItem = item

        # fetch coal
        if not foundItem:
            if not self.collectQuest:
                self.collectQuest = FillPocketsQuest()
                self.character.assignQuest(self.collectQuest,active=True)
            super().recalculate()
            return

        # activate furnace
        if not self.activateFurnaceQuest and not self.collectQuest:
            self.activateFurnaceQuest = ActivateQuest(self.furnace)
            self.character.assignQuest(self.activateFurnaceQuest,active=True)
            super().recalculate()
            return

        super().recalculate()

############################################################
###
##  experimental quests
#
############################################################

'''
a container quest containing a list of quests that have to be handled in sequence
'''
class MetaQuestSequence(Quest):
    '''
    state initialization
    '''
    def __init__(self,quests,startCinematics=None):
        # listen to subquests
        self.subQuestsOrig = quests.copy()
        self.subQuests = quests
        super().__init__(startCinematics=startCinematics)
        self.listeningTo = []
        self.metaDescription = "meta"
        
        # listen to subquests
        if len(self.subQuests):
            self.startWatching(self.subQuests[0],self.recalculate)

    '''
    get target position from first subquest
    bad code: should use a position object
    '''
    @property
    def dstX(self):
        try:
            return self.subQuests[0].dstX
        except:
            return self.character.xPosition

    '''
    get target position from first subquest
    bad code: should use a position object
    '''
    @property
    def dstY(self):
        try:
            return self.subQuests[0].dstY
        except:
            return self.character.yPosition

    '''
    render description as simple string
    '''
    @property
    def description(self):
        # add name of the actual quest
        out =  self.metaDescription+":\n"
        for quest in self.subQuests:
            # add quests
            if quest.active:
                out += "    > "+"\n      ".join(quest.description.split("\n"))+"\n"
            else:
                out += "    x "+"\n      ".join(quest.description.split("\n"))+"\n"
        return out

    '''
    get a more detailed description 
    bad code: asList and colored are out of place
    bad code: the asList and colored mixup leads to ugly code
    '''
    def getDescription(self,asList=False,colored=False,active=False):
        # add name of the actual quest
        if asList:
            if colored:
                import urwid
                if active:
                    color = "#0f0"
                else:
                    color = "#090"
                out = [[[(urwid.AttrSpec(color,"default"),self.metaDescription+":")],"\n"]]
            else:
                out = [[self.metaDescription+":","\n"]]
        else:
            out =  self.metaDescription+":\n"
        for quest in self.subQuests:
            # add quests
            if asList:
                first = True
                colored = colored
                if quest.active:
                    if colored:
                        import urwid
                        if active:
                            color = "#0f0"
                        else:
                            color = "#090"
                        deko = (urwid.AttrSpec(color,"default"),"  > ")
                    else:
                        deko = "  > "
                else:
                    deko = "  x "
                for item in quest.getDescription(asList=asList,colored=colored,active=active):
                    if not first:
                        deko = "    "
                    out.append([deko,item])
                    first = False
                    colored = False
            else:
                if quest.active:
                    out += "    > "+"\n      ".join(quest.getDescription().split("\n"))+"\n"
                else:
                    out += "    x "+"\n      ".join(quest.getDescription().split("\n"))+"\n"
        return out

    '''
    assign self and first subquest to character
    '''
    def assignToCharacter(self,character):
        if self.subQuests:
            self.subQuests[0].assignToCharacter(character)
        super().assignToCharacter(character)

    '''
    check if there are quests left
    '''
    def triggerCompletionCheck(self):

        # do nothing on inactive quest
        if not self.active:
            return

        # remove completed quests
        if self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

        # wrap up when out of subquests
        if not len(self.subQuests):
            self.postHandler()

    '''
    ensure first quest is active
    '''
    def recalculate(self):
        # do nothing on inactive quest
        if not self.active:
            return 

        # remove completed quests
        if self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

        # start first quest
        if len(self.subQuests):
            if not self.subQuests[0].character:
                self.subQuests[0].assignToCharacter(self.character)
            if not self.subQuests[0].active:
                self.subQuests[0].activate()
            if self.subQuests and not (self.subQuests[0],self.recalculate) in self.listeningTo:
                self.startWatching(self.subQuests[0],self.recalculate)
        super().recalculate()

        # check for completeion
        self.triggerCompletionCheck()

    '''
    add a quest
    '''
    def addQuest(self,quest,addFront=True):
        # add quest
        if addFront:
            self.subQuests.insert(0,quest)
        else:
            self.subQuests.append(quest)

        # listen to quest
        self.startWatching(self.subQuests[0],self.recalculate)

        # deactivate last active quest
        # bad code: should only happen on addFront
        if len(self.subQuests) > 1:
            self.subQuests[1].deactivate()

    '''
    activate self and first subquest
    '''
    def activate(self):
        if len(self.subQuests):
            if not self.subQuests[0].active:
                self.subQuests[0].activate()
        super().activate()

    '''
    forward solver from first subquest
    '''
    def solver(self,character):
        if len(self.subQuests):
            self.subQuests[0].solver(character)

    '''
    deactivate self and first subquest
    '''
    def deactivate(self):
        if len(self.subQuests):
            if self.subQuests[0].active:
                self.subQuests[0].deactivate()
        super().deactivate()

'''
a container quest containing a list of quests that have to be handled in any order
'''
class MetaQuestParralel(Quest):
    '''
    state initialization
    '''
    def __init__(self,quests,startCinematics=None,looped=False,lifetime=None):
        self.subQuests = quests
        self.lastActive = None
        self.metaDescription = "meta"

        super().__init__(startCinematics=startCinematics,lifetime=lifetime)

        # listen to subquests
        for quest in self.subQuests:
            self.startWatching(quest,self.recalculate)

    '''
    forward position from last active quest
    '''
    @property
    def dstX(self):
        if not self.lastActive:
            return None
        try:
            return self.lastActive.dstX
        except Exception as e:
            return None

    '''
    forward position from last active quest
    '''
    @property
    def dstY(self):
        if not self.lastActive:
            return None
        try:
            return self.lastActive.dstY
        except Exception as e:
            #messages.append(e)
            return None

    '''
    get a more detailed description 
    bad code: asList and colored are out of place
    bad code: the asList and colored mixup leads to ugly code
    '''
    def getDescription(self,asList=False,colored=False,active=False):
        if asList:
            if colored:
                import urwid
                if active:
                    color = "#0f0"
                else:
                    color = "#090"
                out = [[(urwid.AttrSpec(color,"default"),self.metaDescription+":"),"\n"]]
            else:
                out = [[self.metaDescription+":\n"]]
        else:
            out = ""+self.metaDescription+":\n"

        counter = 0
        for quest in self.subQuests:
            if asList:
                questDescription = []

                if quest == self.lastActive:
                    if quest.active:
                        deko = " -> "
                    else:
                        deko = "YYYY"
                elif quest.paused:
                    deko = "  - "
                elif quest.active:
                    deko = "  * "
                else:
                    deko = "XXXX"

                if colored:
                    import urwid
                    if active and quest == self.lastActive:
                        color = "#0f0"
                    else:
                        color = "#090"
                    deko = (urwid.AttrSpec(color,"default"),deko)

                first = True
                if quest == self.lastActive:
                    descriptions = quest.getDescription(asList=asList,colored=colored,active=active)
                else:
                    descriptions = quest.getDescription(asList=asList,colored=colored)
                for item in descriptions:
                    if not first:
                        deko = "    "
                    out.append([deko,item])
                    first = False
            else:
                questDescription = "\n    ".join(quest.getDescription().split("\n"))+"\n"
                if quest == self.lastActive:
                    if quest.active:
                        out += "  ->"+questDescription
                    else:
                        out += "YYYY"+questDescription
                elif quest.paused:
                    out += "  - "+questDescription
                elif quest.active:
                    out += "  * "+questDescription
                else:
                    out += "XXXX"+questDescription
            counter += 1
        return out

    '''
    render description as simple string
    '''
    @property
    def description(self):
        # add the name of the main quest
        out = ""+self.metaDescription+":\n"
        for quest in self.subQuests:
            # show subquests
            questDescription = "\n    ".join(quest.description.split("\n"))+"\n"
            if quest == self.lastActive:
                if quest.active:
                    out += "  ->"+questDescription
                else:
                    # bad code: debug out in ui
                    out += "YYYY"+questDescription
            elif quest.paused:
                out += "  - "+questDescription
            elif quest.active:
                out += "  * "+questDescription
            else:
                # bad code: debug out in ui
                out += "XXXX"+questDescription
        return out

    '''
    assign self and subquests to character
    '''
    def assignToCharacter(self,character):
        super().assignToCharacter(character)

        for quest in self.subQuests:
                quest.assignToCharacter(self.character)

        self.recalculate()

    '''
    make first unpaused quest active
    '''
    def recalculate(self):
        # remove completed sub quests
        for quest in self.subQuests:
            if quest.completed:
                self.subQuests.remove(quest)

        # find first unpaused quest
        activeQuest = None
        for quest in self.subQuests:
            if not quest.paused:
                activeQuest = quest
                break

        # make the quest active
        if not activeQuest == self.lastActive:
            self.lastActive = activeQuest
        if self.lastActive:
            activeQuest.recalculate()

        super().recalculate()

    '''
    check if there are quests left to do
    '''
    def triggerCompletionCheck(self):
        if not self.subQuests:
                self.postHandler()

    '''
    activate self and subquests
    '''
    def activate(self):
        super().activate()
        for quest in self.subQuests:
            if not quest.active:
                quest.activate()

    '''
    deactivate self and subquests
    '''
    def deactivate(self):
        for quest in self.subQuests:
            if quest.active:
                quest.deactivate()
        super().deactivate()

    '''
    forward the first solver found
    '''
    def solver(self,character):
        for quest in self.subQuests:
            if quest.active and not quest.paused:
                return quest.solver(character)

    '''
    add new quest
    '''
    def addQuest(self,quest):
        if self.character:
            quest.assignToCharacter(self.character)
        if self.active:
            quest.activate()
        quest.recalculate()
        self.questList.insert(0,quest)
        self.startWatching(quest,self.recalculate)

'''
fire a list of furnaces an keep them fired
'''
class KeepFurnacesFiredMeta(MetaQuestParralel):
    '''
    add a quest to keep each furnace fired
    '''
    def __init__(self,furnaces,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        questList = []
        for furnace in furnaces:
            questList.append(KeepFurnaceFiredMeta(furnace))
        super().__init__(questList)
        self.metaDescription = "KeepFurnacesFiredMeta"

'''
fire a furnace an keep it fired
'''
class KeepFurnaceFiredMeta(MetaQuestSequence):
    '''
    '''
    def __init__(self,furnace,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        self.questList = []
        self.fireFurnaceQuest = None
        self.waitQuest = None
        self.furnace = furnace
        super().__init__(self.questList,lifetime=lifetime)
        self.metaDescription = "KeepFurnaceFiredMeta"

        # listen to furnace
        self.startWatching(self.furnace,self.recalculate)

    def recalculate(self):
        if not self.character:
            return

        if self.fireFurnaceQuest and self.fireFurnaceQuest.completed:
            self.fireFurnaceQuest = None

        if not self.fireFurnaceQuest and not self.furnace.activated:
            self.fireFurnaceQuest = FireFurnaceMeta(self.furnace)
            self.addQuest(self.fireFurnaceQuest)
            self.unpause()

        if self.waitQuest and self.waitQuest.completed:
            self.waitQuest = None

        if not self.waitQuest and not self.fireFurnaceQuest:
            if self.furnace.activated:
                self.waitQuest = WaitForDeactivationQuest(self.furnace)
                self.startWatching(self.waitQuest,self.recalculate)
                self.addQuest(self.waitQuest)
                self.pause()
            else:
                self.unpause()

        super().recalculate()
    
    '''
    never complete
    '''
    def triggerCompletionCheck(self):
        return

'''
fire a furnace once
'''
class FireFurnaceMeta(MetaQuestSequence):
    '''
    state initialization
    '''
    def __init__(self,furnace,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        self.activateQuest = None
        self.collectQuest = None
        self.questList = []
        self.furnace = furnace
        super().__init__(self.questList)
        self.metaDescription = "FireFurnaceMeta"+str(self)

    '''
    collect coal and fire furnace
    '''
    def recalculate(self):
        # remove completed quest
        if self.collectQuest and self.collectQuest.completed:
            self.collectQuest = None

        if not self.collectQuest:
            # search for fuel in inventory
            foundItem = None
            for item in self.character.inventory:
                try:
                    canBurn = item.canBurn
                except:
                    continue
                if not canBurn:
                    continue
                foundItem = item

            if not foundItem:
                # collect fuel
                self.collectQuest = CollectQuestMeta()
                self.collectQuest.assignToCharacter(self.character)
                self.startWatching(self.collectQuest,self.recalculate)
                self.questList.insert(0,self.collectQuest)
                self.collectQuest.activate()
                self.changed()

                # pause quest to fire furnace
                if self.activateQuest:
                    self.activateQuest.pause()

        # unpause quest to fire furnace if coal is avalable
        if self.activateQuest and not self.collectQuest:
            self.activateQuest.unpause()

        # add quest to fire furnace
        if not self.activateQuest and not self.collectQuest and not self.furnace.activated:
            self.activateQuest = ActivateQuestMeta(self.furnace)
            self.activateQuest.assignToCharacter(self.character)
            self.questList.append(self.activateQuest)
            self.activateQuest.activate()
            self.startWatching(self.activateQuest,self.recalculate)
            self.changed()

        super().recalculate()

    '''
    assign to character and listen to character
    '''
    def assignToCharacter(self,character):
        character.addListener(self.recalculate)
        super().assignToCharacter(character)

    '''
    check if furnace is burning
    '''
    def triggerCompletionCheck(self):
        if self.furnace.activated:
            self.postHandler()
            
        super().triggerCompletionCheck()

'''
patrol along a cirqular path
bad code: this quest is not used and may be broken
'''
class PatrolQuest(MetaQuestSequence):
    '''
    state initialization
    '''
    def __init__(self,waypoints=[],startCinematics=None,looped=True,lifetime=None):
        # add movement between waypoints
        quests = []
        for waypoint in waypoints:
            quest = MoveQuest(waypoint[0],waypoint[1],waypoint[2])
            quests.append(quest)

        self.lifetime = lifetime

        # bad code: superconstructor doesn't actually process the looped parameter
        super().__init__(quests,startCinematics=startCinematics,looped=looped)

    '''
    activate and prepare termination after lifespan
    '''
    def activate(self):
        if self.lifetime:
            '''
            event for wrapping up the quest
            '''
            class endQuestEvent(object):
                '''
                state initialization
                '''
                def __init__(subself,tick):
                    subself.tick = tick

                '''
                wrap up the quest
                '''
                def handleEvent(subself):
                    self.postHandler()
            self.character.room.addEvent(endQuestEvent(self.character.room.timeIndex+self.lifetime))

        super().activate()

'''
quest to examine the environment
'''
class ExamineQuest(Quest):
    '''
    state initialization
    '''
    def __init__(self,waypoints=[],startCinematics=None,looped=True,lifetime=None):
        self.lifetime = lifetime
        self.description = "please examine your environment"
        super().__init__(startCinematics=startCinematics)

    '''
    activate and prepare termination after lifespan
    '''
    def activate(self):
        if self.lifetime:
            '''
            event for wrapping up the quest
            '''
            class endQuestEvent(object):
                '''
                state initialization
                '''
                def __init__(subself,tick):
                    subself.tick = tick

                '''
                wrap up the quest
                '''
                def handleEvent(subself):
                    self.postHandler()

            self.character.room.addEvent(endQuestEvent(self.character.room.timeIndex+self.lifetime))

        super().activate()

'''
quest to refill the goo flask
'''
class RefillDrinkQuest(ActivateQuest):
    '''
    call superconstructor with modified parameters
    '''
    def __init__(self,startCinematics=None):
        super().__init__(toActivate=terrain.tutorialVatProcessing.gooDispenser,desiredActive=True,startCinematics=startCinematics)

    '''
    check wnether the character has a filled goo flask
    '''
    def triggerCompletionCheck(self):
        for item in self.character.inventory:
            if isinstance(item,items.GooFlask):
                if item.uses > 90:
                    self.postHandler()

'''
quest to drink something
'''
class DrinkQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,startCinematics=None):
        self.description = "please drink"
        super().__init__(startCinematics=startCinematics)

    '''
    assign to character and listen to character
    '''
    def assignToCharacter(self,character):
        self.startWatching(character,self.recalculate)
        super().assignToCharacter(character)

    '''
    drink something
    '''
    def solver(self,character):
        for item in character.inventory:
            if isinstance(item,items.GooFlask):
                if item.uses > 0:
                    item.apply(character)
                    self.postHandler()
                    break

    '''
    check if the character is still thursty
    '''
    def triggerCompletionCheck(self):
        if self.character.satiation > 800:
            self.postHandler()
            
        super().triggerCompletionCheck()

'''
ensure own survival
'''
class SurviveQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,startCinematics=None,looped=True,lifetime=None):
        self.description = "survive"
        self.drinkQuest = None
        self.refillQuest = None
        super().__init__(startCinematics=startCinematics)

    '''
    assign to character and listen to the character
    '''
    def assignToCharacter(self,character):
        super().assignToCharacter(character)
        self.startWatching(character,self.recalculate)

    '''
    spawn quests to take care of basic needs
    '''
    def recalculate(self):
        # remove completed quests
        if self.drinkQuest and self.drinkQuest.completed:
            self.drinkQuest = None
        if self.refillQuest and self.refillQuest.completed:
            self.refillQuest = None

        # refill flask
        for item in self.character.inventory:
            if isinstance(item,items.GooFlask):
                if item.uses < 10 and not self.refillQuest:
                    self.refillQuest = RefillDrinkQuest()
                    self.character.assignQuest(self.refillQuest,active=True)

        # drink
        if self.character.satiation < 31:
            if not self.drinkQuest:
                self.drinkQuest = DrinkQuest()
                self.character.assignQuest(self.drinkQuest,active=True)

'''
'''
class HopperDuty(MetaQuestSequence):
    '''
    straightforward state initialization
    '''
    def __init__(self,waitingRoom,startCinematics=None,looped=True,lifetime=None):
        self.getQuest = GetQuest(waitingRoom.secondOfficer,assign=False)
        self.getQuest.endTrigger = self.setQuest
        questList = [self.getQuest]
        super().__init__(questList,startCinematics=startCinematics)
        self.metaDescription = "hopper duty"
        self.recalculate()
        self.actualQuest = None
        self.rewardQuest = None
        self.waitingRoom = waitingRoom

    '''
    get quest, do it, collect reward - repeat
    '''
    def recalculate(self):
        if self.active:
            # remove completed quest
            if self.getQuest and self.getQuest.completed:
                self.getQuest = None

            # add quest to fetch reward
            if self.actualQuest and self.actualQuest.completed and not self.rewardQuest:
                self.rewardQuest = GetReward(self.waitingRoom.secondOfficer,self.actualQuest)
                self.actualQuest = None
                self.addQuest(self.rewardQuest,addFront=False)

            # remove completed quest
            if self.rewardQuest and self.rewardQuest.completed:
                self.rewardQuest = None

            # add quest to get a new quest
            if not self.getQuest and not self.actualQuest and not self.rewardQuest:
                self.getQuest = GetQuest(self.waitingRoom.secondOfficer,assign=False)
                self.getQuest.endTrigger = self.setQuest # call handling directly though the trigger mechanism
                self.addQuest(self.getQuest,addFront=False)

            super().recalculate()

    '''
    add the actual quest as subquest
    '''
    def setQuest(self):
        self.actualQuest = self.getQuest.quest
        if self.actualQuest:
            self.addQuest(self.actualQuest,addFront=False)
        else:
            self.addQuest(WaitQuest(lifetime=10),addFront=False)
    
'''
clear the rubble from the mech
bad pattern: there is no way to determine
'''
class ClearRubble(MetaQuestParralel):
    '''
    create subquest to move each piece of scrap to the metalworkshop
    '''
    def __init__(self,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        questList = []
        for item in terrain.itemsOnFloor:
            if isinstance(item,items.Scrap):
                questList.append(TransportQuest(item,(terrain.metalWorkshop,7,1)))
        super().__init__(questList)
        self.metaDescription = "clear rubble"

'''
move some furniture to the construction room
bad code: name lies somewhat
'''
class FetchFurniture(MetaQuestParralel):
    '''
    create subquest to move each piece of scrap to the metalworkshop
    '''
    def __init__(self,constructionSite,storageRooms,toFetch,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        questList = []
        dropoffs = [(4,4),(5,4),(5,5),(5,6),(4,6),(3,6),(3,5),(3,4)]
        self.itemsInStore = []
        thisToFetch = toFetch[:]

        # calculate how many items should be moved
        counter = 0
        maxNum = len(toFetch)
        if maxNum > len(dropoffs):
            maxNum = len(dropoffs)

        fetchType = None
        while counter < maxNum:
            # set item to search for
            if not fetchType:
                if not thisToFetch:
                    break
                fetchType = thisToFetch.pop()

            # search for item in storage rooms
            selectedItem = None
            for storageRoom in storageRooms:
                for item in storageRoom.storedItems:
                    if isinstance(item,fetchType[1]):
                        selectedItem = item
                        storageRoom.storedItems.remove(selectedItem)
                        storageRoom.storageSpace.append((selectedItem.xPosition,selectedItem.yPosition))
                        fetchType = None
                        break
                if selectedItem:
                    break

            if not selectedItem:
                # do nothing
                break

            # add quest to transport the item
            questList.append(TransportQuest(selectedItem,(constructionSite,dropoffs[counter][1],dropoffs[counter][0])))
            self.itemsInStore.append(selectedItem)

            counter += 1

        # bad code: commented out code
        """
        SMART WAY (cheating)
        counter = 0
        maxNum = len(toFetch)
        if maxNum > len(dropoffs):
            maxNum = len(dropoffs)
        toFetch = []
        while counter < maxNum:
            if not storageRoom.storedItems:
                break

            item = storageRoom.storedItems.pop()
            toFetch.append(item)
            counter += 1
    
        for item in toFetch:
            questList.append(PickupQuestMeta(item))
        counter = 0
        for item in toFetch:
            questList.append(DropQuestMeta(item,constructionSite,dropoffs[counter][1],dropoffs[counter][0]))
            counter += 1
        for item in toFetch:
            self.itemsInStore.append(item)
        """

        super().__init__(questList)
        self.metaDescription = "fetch furniture"

'''
place furniture within a contruction site
'''
class PlaceFurniture(MetaQuestParralel):
    '''
    generates quests picking up the furniture and dropping it at the right place
    bad code: generating transport quests would me better
    '''
    def __init__(self,constructionSite,itemsInStore,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        self.questList = []

        # handle each item
        counter = 0
        while counter < len(itemsInStore):
            # get item to place
            if not constructionSite.itemsInBuildOrder:
                break
            toBuild = constructionSite.itemsInBuildOrder.pop()

            # pick up item
            quest = PickupQuest(itemsInStore[counter])
            self.questList.append(quest)
            self.startWatching(quest,self.recalculate)

            # drop item
            quest = DropQuest(itemsInStore[counter],constructionSite,toBuild[0][1],toBuild[0][0])
            self.questList.append(quest)
            self.startWatching(quest,self.recalculate)
            counter += 1 

        super().__init__(self.questList)
        self.metaDescription = "place furniture"

'''
quest for entering a room
'''
class EnterRoomQuestMeta(MetaQuestSequence):
    '''
    basic state initialization
    '''
    def __init__(self,room,followUp=None,startCinematics=None):
        self.room = room
        self.questList = [EnterRoomQuest(room)]
        super().__init__(self.questList)
        self.recalculate()
        self.metaDescription = "enterroom Meta"
        self.leaveRoomQuest = None

    '''
    add quest to leave room if needed
    '''
    def recalculate(self):
        if not self.active:
            return 
        if self.leaveRoomQuest and self.leaveRoomQuest.completed:
            self.leaveRoomQuest = None
        if not self.leaveRoomQuest and self.character.room and not self.character.room == self.room:
            self.leaveRoomQuest = LeaveRoomQuest(self.character.room)
            self.addQuest(self.leaveRoomQuest)

        super().recalculate()

    '''
    assign quest and listen to character
    '''
    def assignToCharacter(self,character):
        self.startWatching(character,self.recalculate)
        super().assignToCharacter(character)

'''
move to a position
'''
class MoveQuestMeta(MetaQuestSequence):
    '''
    state initialization
    '''
    def __init__(self,room,x,y,sloppy=False,followUp=None,startCinematics=None):
        self.moveQuest = MoveQuest(room,x,y,sloppy=sloppy)
        self.questList = [self.moveQuest]
        self.enterRoomQuest = None
        self.leaveRoomQuest = None
        self.room = room
        super().__init__(self.questList)
        self.metaDescription = "move meta"

    '''
    move to correct room if nesseccary
    '''
    def recalculate(self):
        if self.active:
            # leave wrong room
            if self.leaveRoomQuest and self.leaveRoomQuest.completed:
                self.leaveRoomQuest = None
            if not self.leaveRoomQuest and (not self.room and self.character.room):
                self.leaveRoomQuest = LeaveRoomQuest(self.character.room)
                self.addQuest(self.leaveRoomQuest)

            # enter correct room
            if self.enterRoomQuest and self.enterRoomQuest.completed:
                self.enterRoomQuest = None
            if (not self.enterRoomQuest and (self.room and ((not self.character.room) or (not self.character.room == self.room)))):
                self.enterRoomQuest = EnterRoomQuestMeta(self.room)
                self.addQuest(self.enterRoomQuest)
        super().recalculate()
    
    '''
    assign to character and listen to character
    '''
    def assignToCharacter(self,character):
        self.startWatching(character,self.recalculate)
        super().assignToCharacter(character)

'''
drop a item somewhere
'''
class DropQuestMeta(MetaQuestSequence):
    '''
    generate quests to move and drop item
    '''
    def __init__(self,toDrop,room,xPosition,yPosition,followUp=None,startCinematics=None):
        self.toDrop = toDrop
        self.moveQuest = MoveQuestMeta(room,xPosition,yPosition)
        self.questList = [self.moveQuest,NaiveDropQuest(toDrop,room,xPosition,yPosition)]
        self.room = room
        self.xPosition = xPosition
        self.yPosition = yPosition
        super().__init__(self.questList)
        self.metaDescription = "drop Meta"

    '''
    re-add the movement quest if neccessary
    '''
    def recalculate(self):
        if self.active:
            if self.moveQuest and self.moveQuest.completed:
                self.moveQuest = None
            if not self.moveQuest and not (self.room == self.character.room and self.xPosition == self.character.xPosition and self.yPosition == self.character.yPosition):
                self.moveQuest = MoveQuestMeta(self.room,self.xPosition,self.yPosition)
                self.addQuest(self.moveQuest)
        super().recalculate()

    '''
    assign to character and listen to character
    '''
    def assignToCharacter(self,character):
        self.startWatching(character,self.recalculate)
        super().assignToCharacter(character)

'''
pick up an item
'''
class PickupQuestMeta(MetaQuestSequence):
    '''
    generate quests to move and pick up 
    '''
    def __init__(self,toPickup,followUp=None,startCinematics=None):
        self.toPickup = toPickup
        self.sloppy = not self.toPickup.walkable
        self.moveQuest = MoveQuestMeta(self.toPickup.room,self.toPickup.xPosition,self.toPickup.yPosition,sloppy=self.sloppy)
        self.questList = [self.moveQuest,NaivePickupQuest(self.toPickup)]
        super().__init__(self.questList)
        self.metaDescription = "pickup Meta"

    '''
    re-add the movement quest if neccessary
    '''
    def recalculate(self):
        if self.active:
            # remove completed quests
            if self.moveQuest and self.moveQuest.completed:
                self.moveQuest = None

            if not self.moveQuest:
                # check whether it is neccessary to re add the movement
                reAddMove = False
                if not self.sloppy:
                    if not hasattr(self.toPickup,"xPosition") or not hasattr(self.toPickup,"yPosition"):
                        reAddMove = False
                    elif not (self.toPickup.room == self.character.room and self.toPickup.xPosition == self.character.xPosition and self.toPickup.yPosition == self.character.yPosition):
                        reAddMove = True
                else:
                    if not hasattr(self.toPickup,"xPosition") or not hasattr(self.toPickup,"yPosition"):
                        reAddMove = False
                    elif not (self.toPickup.room == self.character.room and (
                                                             (self.toPickup.xPosition-self.character.xPosition in (-1,0,1) and self.toPickup.yPosition == self.character.yPosition) or 
                                                             (self.toPickup.yPosition-self.character.yPosition in (-1,0,1) and self.toPickup.xPosition == self.character.xPosition))):
                        reAddMove = True

                # re add the movement
                if reAddMove:
                    self.moveQuest = MoveQuestMeta(self.toPickup.room,self.toPickup.xPosition,self.toPickup.yPosition,sloppy=self.sloppy)
                    self.addQuest(self.moveQuest)
        super().recalculate()

    '''
    assign to character and listen to character
    '''
    def assignToCharacter(self,character):
        self.startWatching(character,self.recalculate)
        super().assignToCharacter(character)

'''
activate an item
'''
class ActivateQuestMeta(MetaQuestSequence):
    '''
    generate quests to move and activate
    '''
    def __init__(self,toActivate,followUp=None,desiredActive=True,startCinematics=None):
        self.toActivate = toActivate
        self.moveQuest = MoveQuestMeta(toActivate.room,toActivate.xPosition,toActivate.yPosition,sloppy=True)
        self.questList = [self.moveQuest,NaiveActivateQuest(toActivate)]
        super().__init__(self.questList)
        self.metaDescription = "activate Quest"

'''
collect items with some quality
'''
class CollectQuestMeta(MetaQuestSequence):
    '''
    state initialization
    '''
    def __init__(self,toFind="canBurn",startCinematics=None):
        self.toFind = toFind
        self.activateQuest = None
        self.waitQuest = WaitQuest()
        self.questList = [self.waitQuest]
        super().__init__(self.questList)
        self.metaDescription = "fetch Quest Meta"
    
    '''
    assign to character and add the quest to fetch from a pile
    bad code: only works within room and with piles
    '''
    def assignToCharacter(self,character):
        if character.room:
            # search for an item 
            # bad code: should prefer coal
            foundItem = None
            for item in character.room.itemsOnFloor:
                hasProperty = False
                try:
                    hasProperty = getattr(item,"contains_"+self.toFind)
                except:
                    continue
                        
                if hasProperty:
                    foundItem = item
                    # This line ist good but looks bad in current setting. reactivate later
                    #break

            # activate the pile
            if foundItem:
                self.activeQuest = ActivateQuestMeta(foundItem)
                self.addQuest(self.activeQuest)

            # terminate when done
            if self.waitQuest and foundItem:
                quest = self.waitQuest
                self.waitQuest = None
                quest.postHandler()

        super().assignToCharacter(character)

'''
a quest for fetching a quest from a quest dispenser
'''
class GetQuest(MetaQuestSequence):
    '''
    generate quests to move to the quest dispenser and get the quest
    '''
    def __init__(self,questDispenser,assign=False,followUp=None,startCinematics=None):
        self.questDispenser = questDispenser
        self.moveQuest = MoveQuestMeta(self.questDispenser.room,self.questDispenser.xPosition,self.questDispenser.yPosition,sloppy=True)
        self.getQuest = NaiveGetQuest(questDispenser,assign=assign)
        self.questList = [self.moveQuest,self.getQuest]
        super().__init__(self.questList)
        self.metaDescription = "get Quest"

    '''
    check if a quest was aquired
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if self.quest:
                self.postHandler()
        super().triggerCompletionCheck()

    '''
    forward quest from subquest
    '''
    @property
    def quest(self):
        return self.getQuest.quest

'''
get the reward for a completed quest
'''
class GetReward(MetaQuestSequence):
    def __init__(self,questDispenser,quest,assign=False,followUp=None,startCinematics=None):
        self.questDispenser = questDispenser
        self.moveQuest = MoveQuestMeta(self.questDispenser.room,self.questDispenser.xPosition,self.questDispenser.yPosition,sloppy=True)
        self.getQuest = NaiveGetReward(quest)
        self.questList = [self.moveQuest,self.getQuest]
        self.actualQuest = quest

        super().__init__(self.questList)
        self.metaDescription = "get Reward"

    '''
    assign to character and spawn a chat option to collect reward
    bad code: spawning the chat should happen in activate
    '''
    def assignToCharacter(self,character):
        '''
        the chat for collecting the reward
        '''
        class RewardChat(interaction.SubMenu):
             dialogName = "i did the task: "+self.actualQuest.description.split("\n")[0]
             '''
             call superclass with less params
             '''
             def __init__(subSelf,partner):
                 super().__init__()
             
             '''
             call the solver to assign reward
             bad code: calling the solver seems like bad idea
             '''
             def handleKey(subSelf, key):
                 subSelf.persistentText = "here is your reward"
                 subSelf.set_text(subSelf.persistentText)
                 self.getQuest.solver(self.character)
                 if self.moveQuest:
                     self.moveQuest.postHandler()
                 subSelf.done = True
                 return True

        # add chat option
        if character == mainChar:
            self.rewardChat = RewardChat
            self.questDispenser.basicChatOptions.append(self.rewardChat)
        super().assignToCharacter(character)

    '''
    remove the reward chat option and do the usual wrap up
    '''
    def postHandler(self):
        if self.character == mainChar:
            self.questDispenser.basicChatOptions.remove(self.rewardChat)
        super().postHandler()

'''
the quest for murering somebody
'''
class MurderQuest(MetaQuestSequence):
    '''
    generate quests for moving to and murdering the target
    '''
    def __init__(self,toKill,followUp=None,startCinematics=None):
        self.toKill = toKill
        self.moveQuest = MoveQuestMeta(self.toKill.room,self.toKill.xPosition,self.toKill.yPosition,sloppy=True)
        self.questList = [self.moveQuest,NaiveMurderQuest(toKill)]
        self.lastPos = (self.toKill.room,self.toKill.xPosition,self.toKill.yPosition)
        super().__init__(self.questList)
        self.metaDescription = "murder"
        self.startWatching(self.toKill,self.recalculate)

    '''
    adjust movement to follow target
    '''
    def recalculate(self):
        if self.active:
            pos = (self.toKill.room,self.toKill.xPosition,self.toKill.yPosition)
            if not (pos == self.lastPos) and not self.toKill.dead:
                self.lastPos = pos
                self.moveQuest.deactivate()
                if self.moveQuest in self.questList:
                        self.questList.remove(self.moveQuest)
                self.moveQuest = MoveQuestMeta(self.toKill.room,self.toKill.xPosition,self.toKill.yPosition,sloppy=True)
                self.addQuest(self.moveQuest)
        super().recalculate()
          
'''
construct a room
'''
class ConstructRoom(MetaQuestParralel):
    '''
    straightforward state initialization
    '''
    def __init__(self,constructionSite,storageRooms,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):

        self.questList = []

        self.constructionSite = constructionSite
        self.storageRooms = storageRooms
        self.itemsInStore = []

        self.didFetchQuest = False
        self.didPlaceQuest = False

        super().__init__(self.questList)
        self.metaDescription = "construct room"

    '''
    add quests to fetch and place furniture
    '''
    def recalculate(self):
        if not self.questList or self.questList[0].completed:
            if not self.didFetchQuest:
                # fetch some furniture from storage
                self.didFetchQuest = True
                self.didPlaceQuest = False
                self.fetchquest = FetchFurniture(self.constructionSite,self.storageRooms,self.constructionSite.itemsInBuildOrder)
                self.addQuest(self.fetchquest)
                self.itemsInStore = self.fetchquest.itemsInStore
            elif not self.didPlaceQuest:
                # place furniture in desired position
                self.didPlaceQuest = True
                self.placeQuest = PlaceFurniture(self.constructionSite,self.itemsInStore)
                self.addQuest(self.placeQuest)
                if self.constructionSite.itemsInBuildOrder:
                    self.didFetchQuest = False
        super().recalculate()

    '''
    do not terminate until all fetching and placing was done
    '''
    def triggerCoppletionCheck(self):
        if not self.didFetchQuest or not self.didPlaceQuest:
            return
        super().triggerCoppletionCheck()

'''
transport an item to a position
'''
class TransportQuest(MetaQuestSequence):
    '''
    generate quest for picking up the item
    '''
    def __init__(self,toTransport,dropOff,followUp=None,startCinematics=None,lifetime=None):
        self.toTransport = toTransport
        self.dropOff = dropOff
        self.questList = []
        quest = PickupQuestMeta(self.toTransport)
        quest.endTrigger = self.addDrop # add drop quest in follow up
        self.questList.append(quest)
        super().__init__(self.questList)
        self.metaDescription = "transport"

    '''
    drop the item after picking it up
    '''
    def addDrop(self):
        self.addQuest(DropQuestMeta(self.toTransport,self.dropOff[0],self.dropOff[1],self.dropOff[2]))

'''
fill inventory with something
bad code: only fetches fuel
'''
class FillPocketsQuest(MetaQuestSequence):
    '''
    state initialization
    '''
    def __init__(self,followUp=None,startCinematics=None,lifetime=None):
        self.waitQuest = WaitQuest()
        self.questList = [self.waitQuest]
        self.collectQuest = None
        super().__init__(self.questList)
        self.metaDescription = "fill pockets"

    '''
    add collect quest till inventory is full
    '''
    def recalculate(self):
        # do nothing on not really active quests
        if not self.active:
            return 
        if not self.character:
            return

        # remove completed quests
        if self.collectQuest and self.collectQuest.completed:
            self.collectQuest = None

        # add collect quest
        if len(self.character.inventory) < 11 and not self.collectQuest:
            self.collectQuest = CollectQuestMeta()
            self.addQuest(self.collectQuest)

        # remove wait quest on first occasion
        if self.waitQuest:
            self.waitQuest.postHandler()
            self.waitQuest = None

        super().recalculate()

'''
move items from permanent storage to accesible storage
'''
class StoreCargo(MetaQuestSequence):
    '''
    generate quests for transporting each item
    '''
    def __init__(self,cargoRoom,storageRoom,followUp=None,startCinematics=None,lifetime=None):
        self.questList = []

        # determine how many items should be moved
        amount = len(cargoRoom.storedItems)
        freeSpace = len(storageRoom.storageSpace)
        if freeSpace < amount:
            amount = freeSpace

        # add transport quest for each item
        startIndex = len(storageRoom.storedItems)
        counter = 0
        while counter < amount:
            location = storageRoom.storageSpace[counter]
            self.questList.append(TransportQuest(cargoRoom.storedItems.pop(),(storageRoom,location[0],location[1])))
            counter += 1

        super().__init__(self.questList)
        self.metaDescription = "store cargo"

'''
move items to accessible storage
'''
class MoveToStorage(MetaQuestSequence):
    '''
    generate the quests to transport each item
    '''
    def __init__(self, items, storageRoom):
        self.questList = []
            
        # determine how many items should be moved
        amount = len(items)
        freeSpace = len(storageRoom.storageSpace)
        if freeSpace < amount:
            amount = freeSpace

        # add transport quest for each item
        startIndex = len(storageRoom.storedItems)
        counter = 0
        while counter < amount:
            location = storageRoom.storageSpace[counter]
            self.questList.append(TransportQuest(items.pop(),(storageRoom,location[0],location[1])))
            counter += 1
        super().__init__(self.questList)

        self.metaDescription = "move to storage"

'''
handle a delivery
bad pattern: the quest is tailored to a story, it should be more abstracted
bad pattern: the quest can only be solved by delegation
'''
class HandleDelivery(MetaQuestSequence):
    '''
    state initialization
    '''
    def __init__(self, cargoRooms=[],storageRooms=[]):
        self.cargoRooms = cargoRooms
        self.storageRooms = storageRooms
        self.questList = []
        super().__init__(self.questList)
        self.addNewStorageRoomQuest()
        self.metaDescription = "ensure the cargo is moved to storage"
       
    '''
    wait the cargo to be moved to storage
    '''
    def waitForQuestCompletion(self):
        quest = WaitForQuestCompletion(self.quest)
        quest.endTrigger = self.addNewStorageRoomQuest
        self.addQuest(quest)

    '''
    delegate moving the cargo to storage
    '''
    def addNewStorageRoomQuest(self):
        # stop when all cargo has been handled
        if not self.cargoRooms:
            return

        # remove empty cargo room
        if not self.cargoRooms[0].storedItems:
            self.cargoRooms.pop()

        # stop when all cargo has been handled
        if not self.cargoRooms:
            return

        # add quest to delegate moving the cargo to somebody
        room = self.cargoRooms[0]
        self.quest = StoreCargo(room,self.storageRooms.pop())
        quest = NaiveDelegateQuest(self.quest)
        quest.endTrigger = self.waitForQuestCompletion
        self.addQuest(quest)

    '''
    does nothing
    bad code: misspelled method name. does nothing
    '''
    def triggerCoppletionCheck(self):
        return False

'''
dummy quest for doing the room duty
'''
class RoomDuty(MetaQuestParralel):
    '''
    state initialization
    '''
    def __init__(self, cargoRooms=[],storageRooms=[]):
        self.questList = []
        super().__init__(self.questList)
        self.metaDescription = "room duty"

    '''
    do nothing
    '''
    def recalculate(self):
        return 

    '''
    never complete
    '''
    def triggerCoppletionCheck(self):
        return 

'''
dummy quest for following somebodies orders
'''
class Serve(MetaQuestParralel):
    '''
    state initialization
    '''
    def __init__(self, cargoRooms=[],storageRooms=[]):
        self.questList = []
        super().__init__(self.questList)
        self.metaDescription = "serve"

    '''
    do nothing
    '''
    def recalculate(self):
        return 

    '''
    never complete
    '''
    def triggerCoppletionCheck(self):
        return 
