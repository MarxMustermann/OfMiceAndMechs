import src.items as items

# HACK: common variables with modules
showCinematic = None
loop = None
callShow_or_exit = None

############################################################
###
##  the base class for all quests
#
############################################################

class Quest(object):
    # set up a bit state, nothing special
    def __init__(self,followUp=None,startCinematics=None,lifetime=0):
        self.followUp = followUp # deprecate?
        self.character = None # should be more general like owner as preparation for room quests
        self.listener = [] # the list of things caring about this quest. The owner for example
        self.active = False # active as in started
        self.completed = False # active as in started
        self.startCinematics = startCinematics # deprecate?
        self.endCinematics = None # deprecate?
        self.startTrigger = None # deprecate?
        self.endTrigger = None # deprecate?
        self.paused = False

        self.lifetime = lifetime

    # check whether the quest is solved or not (and trigger teardown if quest is solved)
    def triggerCompletionCheck(self):
        if not self.active:
            return 
        pass

    # do one action to solve the quest, is intended to be overwritten heavily. returns None if there can't be done anything
    # should be rewritten so it returns an actual list of steps
    def solver(self,character):
        if self.paused:
            return True
        else:
            return character.walkPath()

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False
    
    # do the teardown of the quest
    def postHandler(self):
        if self.completed:
            debugMessages.append("this should not happen (posthandler called on completed quest ("+str(self)+")) "+str(self.character))
            if self.character and self in self.character.quests:
                startNext = False
                if self.character.quests[0] == self:
                    startNext = True
                self.character.quests.remove(self)

                if startNext:
                    if self.followUp:
                        self.character.assignQuest(self.followUp,active=True)
                    else:
                        self.character.startNextQuest()
            return

        self.completed = True

        # TODO: handle quests with no assigned character
        if self.character and self in self.character.quests:
            startNext = False
            if self.character.quests[0] == self:
                startNext = True
            self.character.quests.remove(self)

            if startNext:
                self.character.startNextQuest()

        # these should be a unified way to to this. probably an event
        if self.endTrigger:
            self.endTrigger()
        if self.endCinematics:
            showCinematic(self.endCinematics)            
            loop.set_alarm_in(0.0, callShow_or_exit, '.')

        self.deactivate()

        # these should be a unified way to to this. probably an event
        if self.character:
            if self.followUp:
                self.character.assignQuest(self.followUp,active=True)
            else:
                self.character.startNextQuest()

    # ideally this would be a contructor param, but this may be used for reassigning quests
    def assignToCharacter(self,character):
        self.character = character
        self.recalculate()
        if self.active:
            self.character.setPathToQuest(self)

    # recalculate the internal state of the quest
    # this is usually called as a listener function
    # also used when the player moves leaves the path
    def recalculate(self):
        if not self.active:
            return 

        self.triggerCompletionCheck()

    # handle a change in external state
    def changed(self):
        # call the listener functions
        # should probably be an event not a function
        for listener in self.listener:
            listener()

    # wrapper to start or stop listening for changes
    def addListener(self,listenFunction):
        if not listenFunction in self.listener:
            self.listener.append(listenFunction)
    def delListener(self,listenFunction):
        if listenFunction in self.listener:
            self.listener.remove(listenFunction)

    # simple activate/deactivate trigger
    def activate(self):
        self.active = True

        # these should be a unified way to to this. probably an event
        if self.startTrigger:
            self.startTrigger()
        if self.startCinematics:
            showCinematic(self.startCinematics)            
            loop.set_alarm_in(0.0, callShow_or_exit, '.')

        if self.lifetime:
            messages.append("add endQuestEvent")
            class endQuestEvent(object):
                def __init__(subself,tick):
                    subself.tick = tick

                def handleEvent(subself):
                    messages.append("endQuestEvent triggered")
                    self.postHandler()

            self.character.room.addEvent(endQuestEvent(self.character.room.timeIndex+self.lifetime))

        self.recalculate()
        self.changed()

    def deactivate(self):
        self.active = False
        self.changed()

############################################################
###
##  the basic most quests like moving or activating something
#
############################################################

class MoveQuest(Quest):
    def __init__(self,room,x,y,followUp=None,startCinematics=None):
        self.dstX = x
        self.dstY = y
        self.targetX = x
        self.targetY = y
        self.room = room
        self.description = "please go to coordinate "+str(self.dstX)+"/"+str(self.dstY)    
        super().__init__(followUp,startCinematics=startCinematics)

    # success is standing in the right place. should probably check for correct room, too
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

        if not self.room:
            return
        if not self.character:
            return

        if self.room == self.character.room:
            self.dstX = self.targetX
            self.dstY = self.targetY
        elif self.character.room and self.character.quests and self.character.quests[0] == self:
            self.character.assignQuest(LeaveRoomQuest(self.character.room),active=True)
        elif not self.character.room and self.character.quests and self.character.quests[0] == self:
            self.character.assignQuest(EnterRoomQuest(self.room),active=True)
            pass
        super().recalculate()

class ActivateQuest(Quest):
    def __init__(self,toActivate,followUp=None,desiredActive=True,startCinematics=None):
        self.toActivate = toActivate
        self.toActivate.addListener(self.recalculate)
        self.toActivate.addListener(self.triggerCompletionCheck)
        self.dstX = self.toActivate.xPosition
        self.dstY = self.toActivate.yPosition
        self.desiredActive = desiredActive
        self.description = "please activate the "+self.toActivate.name+" ("+str(self.toActivate.xPosition)+"/"+str(self.toActivate.yPosition)+")"
        super().__init__(followUp,startCinematics=startCinematics)

    def triggerCompletionCheck(self):
        if self.toActivate.activated == self.desiredActive:
            self.postHandler()

    def recalculate(self):
        if not self.active:
            return

        if ((not self.character.room) or (not self.character.room == self.toActivate.room)) and self.character.quests[0] == self:
            self.character.assignQuest(EnterRoomQuest(self.toActivate.room),active=True)

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

    def solver(self,character):
        if super().solver(character):
            self.toActivate.apply(character)
            return True

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
                for item in character.room.itemByCoordinates[(character.xPosition,character.yPosition)]:
                    item.close()
                if character.yPosition == 0:
                    character.path.append((character.xPosition,character.yPosition-1))
                elif character.yPosition == character.room.sizeY-1:
                    character.path.append((character.xPosition,character.yPosition+1))
                if character.xPosition == 0:
                    character.path.append((character.xPosition-1,character.yPosition))
                elif character.xPosition == character.room.sizeX-1:
                    character.path.append((character.xPosition+1,character.yPosition))
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
        self.description = "please enter the room: "+room.name+" "+str(room.xPosition)+" "+str(room.yPosition)
        self.room = room
        self.dstX = self.room.walkingAccess[0][0]+room.xPosition*15+room.offsetX
        self.dstY = self.room.walkingAccess[0][1]+room.yPosition*15+room.offsetY
        super().__init__(followUp,startCinematics=startCinematics)

    def assignToCharacter(self,character):
        super().assignToCharacter(character)
        character.addListener(self.recalculate)

    def solver(self,character):
        if character.walkPath():
            return True
        return False

    def recalculate(self):
        if not self.active:
            return 

        if self.character.room and not self.character.room == self.room and self.character.quests[0] == self:
            self.character.assignQuest(LeaveRoomQuest(self.character.room),active=True)

        super().recalculate()

    def postHandler(self):
        if self.character.yPosition in (self.character.room.walkingAccess):
            for item in self.character.room.itemByCoordinates[self.character.room.walkingAccess[0]]:
                item.close()

        super().postHandler()

    def triggerCompletionCheck(self):
        if not self.active:
            return 

        if self.character.room == self.room:
            self.postHandler()

class PickupQuest(Quest):
    def __init__(self,toPickup,followUp=None,startCinematics=None):
        self.toPickup = toPickup
        self.toPickup.addListener(self.recalculate)
        self.toPickup.addListener(self.triggerCompletionCheck)
        self.dstX = self.toPickup.xPosition
        self.dstY = self.toPickup.yPosition
        self.description = "please pick up the "+self.toPickup.name+" ("+str(self.toPickup.xPosition)+"/"+str(self.toPickup.yPosition)+")"
        super().__init__(followUp,startCinematics=startCinematics)

    def triggerCompletionCheck(self):
        if self.active:
            if self.toPickup in self.character.inventory:
                self.postHandler()

    def recalculate(self):
        if self.active:
            if (self.toPickup.room and ((not self.character.room) or (not self.character.room == self.toPickup.room)) and self.active):
                self.character.assignQuest(EnterRoomQuest(self.toPickup.room),active=True)
            if ((not self.toPickup.room) and self.character.room and self.active):
                self.character.assignQuest(LeaveRoomQuest(self.character.room),active=True)

            if hasattr(self,"dstX"):
                del self.dstX
            if hasattr(self,"dstY"):
                del self.dstY
            if hasattr(self,"toPickup"):
                if hasattr(self.toPickup,"xPosition"):
                    self.dstX = self.toPickup.xPosition
                if hasattr(self.toPickup,"xPosition"):
                    self.dstY = self.toPickup.yPosition
            super().recalculate()

    def solver(self,character):
        if super().solver(character):
            self.toPickup.pickUp(character)
            return True

class DropQuest(Quest):
    def __init__(self,toDrop,room,xPosition,yPosition,followUp=None,startCinematics=None):
        self.toDrop = toDrop
        self.toDrop.addListener(self.recalculate)
        self.toDrop.addListener(self.triggerCompletionCheck)
        self.dstX = xPosition
        self.dstY = yPosition
        self.room = room
        self.description = "please drop the "+self.toDrop.name+" at ("+str(self.dstX)+"/"+str(self.dstY)+")"
        super().__init__(followUp,startCinematics=startCinematics)

    def triggerCompletionCheck(self):
        correctPosition = False
        try:
            if self.toDrop.xPosition == self.dstX and self.toDrop.yPosition == self.dstY:
                correctPosition = True
        except:
            pass

        if correctPosition:
            self.postHandler()

    def recalculate(self):
        if ((not self.character.room) or (not self.character.room == self.room)) and self.character.quests[0] == self:
            self.character.assignQuest(EnterRoomQuest(self.room),active=True)

        if not self.active:
            return

        super().recalculate()

class CollectQuest(Quest):
    def __init__(self,toFind="canBurn",startCinematics=None):
        self.toFind = toFind
        self.description = "please fetch things with property: "+toFind
        foundItem = None

        super().__init__(startCinematics=startCinematics)

    def triggerCompletionCheck(self):
        if not self.active:
            return 

        if not self.character:
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

        if foundItem:
            self.postHandler()

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
                    hasProperty = getattr(item,"contains_"+self.toFind)
                except:
                    continue
                
                if hasProperty:
                    foundItem = item
                    # This line ist good but looks bad in current setting. reactivate later
                    #break

            if foundItem:
                self.dstX = foundItem.xPosition
                self.dstY = foundItem.yPosition
        except:
            pass
        super().recalculate()

class FillPocketsQuest(CollectQuest):
    def triggerCompletionCheck(self):
        if not self.active:
            return 

        if not self.character:
            return

        if len(self.character.inventory) < 11:
            return

        super().triggerCompletionCheck()

class WaitQuest(Quest):
    def __init__(self,followUp=None,startCinematics=None,lifetime=None):
        self.description = "please wait"
        super().__init__(lifetime=lifetime)

    def solver(self,character):
        return True

class WaitForDeactivationQuest(Quest):
    def __init__(self,item,followUp=None,startCinematics=None,lifetime=None):
        item.addListener(self.recalculate)
        self.item = item
        self.description = "please wait for deactivation of "+self.item.description
        self.item.addListener(self.recalculate)
        super().__init__(lifetime=lifetime)
        self.pause()

    def recalculate(self):
        super().recalculate()

    def triggerCompletionCheck(self):
        if not self.item.activated:
            self.postHandler()

    def solver(self,character):
        return True


############################################################
###
##  furnace specific quests
#
############################################################

class FireFurnace(Quest):
    def __init__(self,furnace,followUp=None,startCinematics=None,lifetime=None):
        self.furnace = furnace
        self.furnace.addListener(self.recalculate)
        self.description = "please fire the "+self.furnace.name+" ("+str(self.furnace.xPosition)+"/"+str(self.furnace.yPosition)+")"
        self.dstX = self.furnace.xPosition
        self.dstY = self.furnace.yPosition
        self.desiredActive = True
        self.collectQuest = None
        self.activateFurnaceQuest = None
        super().__init__(followUp,startCinematics=startCinematics)

    def assignToCharacter(self,character):
        super().assignToCharacter(character)
        character.addListener(self.recalculate)

    def triggerCompletionCheck(self):
        if not self.active:
            return 

        if self.furnace.activated == self.desiredActive:
            self.postHandler()

    def recalculate(self):
        if not self.active:
            return 

        if self.furnace.activated:
            super().recalculate()
            return 

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
            if not self.collectQuest:
                self.collectQuest = CollectQuest()
                self.character.assignQuest(self.collectQuest,active=True)
            return

        if not self.activateFurnaceQuest:
            self.activateFurnaceQuest = ActivateQuest(self.furnace,desiredActive=True)
            self.character.assignQuest(self.activateFurnaceQuest,active=True)
            return

        self.triggerCompletionCheck()
        super().recalculate()

class KeepFurnacesFired(Quest):
    def __init__(self,furnaces,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        self.furnaces = furnaces
        self.failTrigger = failTrigger
        self.keepFurnaceFiredQuests = {}
        self.metaQuest = None
        self.metaQuest2 = None
        self.fetchQuest = None
        self.description = "please fire the furnaces"
        self.furnaces[0].addListener(self.recalculate)
        super().__init__(followUp=followUp,startCinematics=startCinematics,lifetime=lifetime)

    def solver(self,character):
        return True

    def recalculate(self):
        if not self.active:
            return 

        self.pause()
        """
        LEVEL2:
        """
        if self.metaQuest2 and self.metaQuest2.completed:
            self.metaQuest2 = None

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

        if len(self.character.inventory) <= 11-len(self.furnaces) and (not self.fetchQuest or not self.fetchQuest.active):
            quest = FillPocketsQuest()
            self.character.assignQuest(quest,active=True)
            self.fetchQuest = quest
            self.unpause()
        
        super().recalculate()


class KeepFurnaceFired(Quest):
    def __init__(self,furnace,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        self.furnace = furnace
        self.furnace.addListener(self.recalculate)
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

    def assignToCharacter(self,character):
        super().assignToCharacter(character)
        character.addListener(self.recalculate)

        self.boilers = self.furnace.boilers
        if self.boilers:
            for boiler in self.boilers:
                def fail():
                    self.fail(boiler)
                boiler.addListener(fail)

    def fail(self,boiler):
        if not self.active:
            return 

        if not boiler.isBoiling:
            if self.failTrigger:
                self.failTrigger()

    def triggerCompletionCheck(self):
        if not self.active:
            return 
        
    def recalculate(self):
        if not self.active:
            return 

        self.unpause()

        if self.collectQuest and not self.collectQuest.active:
            self.collectQuest = None
        if self.activateFurnaceQuest and not self.activateFurnaceQuest.active:
            self.activateFurnaceQuest = None

        if self.furnace.activated:
            if not self.collectQuest and not len(self.character.inventory) > self.inventoryThreshold and self.character.quests[0] == self:
                self.collectQuest = FillPocketsQuest()
                self.collectQuest.activate()
                self.character.assignQuest(self.collectQuest,active=True)
            else:
                self.pause()

            super().recalculate()
            return 

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
            if not self.collectQuest:
                self.collectQuest = FillPocketsQuest()
                self.character.assignQuest(self.collectQuest,active=True)
            super().recalculate()
            return

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

class MetaQuest(Quest):
    def __init__(self,quests,startCinematics=None,looped=False):
        self.subQuestsOrig = quests.copy()
        self.subQuests = quests
        self.subQuests[0].addListener(self.triggerCompletionCheck)
        self.looped = looped
        super().__init__(startCinematics=startCinematics)

    @property
    def dstX(self):
        try:
            return self.subQuests[0].dstX
        except:
            return self.character.xPosition

    @property
    def dstY(self):
        try:
            return self.subQuests[0].dstY
        except:
            return self.character.yPosition

    @property
    def description(self):
        try:
            out =  "meta:\n"
            for quest in self.subQuests:
                out += "    * "+quest.description+"\n"
            return out
            return self.subQuests[0].description
        except:
            return ""

    def assignToCharacter(self,character):
        if self.subQuests:
            self.subQuests[0].assignToCharacter(character)
        super().assignToCharacter(character)

    def triggerCompletionCheck(self):
        if self.subQuests and not self.subQuests[0].active:
            self.subQuests.remove(self.subQuests[0])

        if len(self.subQuests):
            if not self.subQuests[0].active:
                self.subQuests[0].assignToCharacter(self.character)
                self.subQuests[0].activate()
                self.subQuests[0].addListener(self.triggerCompletionCheck)
        else:
            if not self.looped:
                self.postHandler()
            else:
                self.subQuests = self.subQuestsOrig.copy()

                self.subQuests[0].assignToCharacter(self.character)
                self.subQuests[0].activate()
                self.subQuests[0].addListener(self.triggerCompletionCheck)

    def activate(self):
        if len(self.subQuests):
            self.subQuests[0].activate()
        super().activate()

    def deactivate(self):
        if len(self.subQuests):
            self.subQuests[0].deactivate()
        super().deactivate()

class MetaQuest2(Quest):
    def __init__(self,quests,startCinematics=None,looped=False,lifetime=None):
        self.subQuests = quests

        for quest in self.subQuests:
            quest.addListener(self.triggerCompletionCheck)

        self.lastActive = None

        self.metaDescription = "meta"

        super().__init__(startCinematics=startCinematics,lifetime=lifetime)

    @property
    def dstX(self):
        if not self.lastActive:
            return None
        try:
            return self.lastActive.dstX
        except Exception as e:
            return None

    @property
    def dstY(self):
        if not self.lastActive:
            return None
        try:
            return self.lastActive.dstY
        except Exception as e:
            #messages.append(e)
            return None

    @property
    def description(self):
            out = ""+self.metaDescription+":\n"
            for quest in self.subQuests:
                questDescription = "\n    ".join(quest.description.split("\n"))+"\n"
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
            return out
            return self.subQuests[0].description

    def assignToCharacter(self,character):
        super().assignToCharacter(character)

        for quest in self.subQuests:
                quest.assignToCharacter(self.character)

    def recalculate(self):
        for quest in self.subQuests:
            if quest.completed:
                self.subQuests.remove(quest)

        foundQuest = False
        for quest in self.subQuests:
            if not quest.paused:
                self.lastActive = quest
                foundQuest = True
                break

        if not foundQuest:
            self.lastActive = None

        super().recalculate()

    def triggerCompletionCheck(self):
        if not self.subQuests:
                self.postHandler()

    def activate(self):
        super().activate()
        for quest in self.subQuests:
            if not quest.active:
                quest.activate()

    def deactivate(self):
        for quest in self.subQuests:
            if quest.active:
                quest.deactivate()
        super().deactivate()

    def solver(self,character):
        for quest in self.subQuests:
            if quest.active:
                return quest.solver(character)


class KeepFurnacesFiredMeta(MetaQuest2):
    def __init__(self,furnaces,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        questList = []
        skillLevel = 20
        if len(furnaces) < skillLevel:
            questList.append(KeepFurnacesFired(furnaces))
        else:
            for furnace in furnaces[skillLevel:]:
                quest = KeepFurnaceFired(furnace)
                questList.append(quest)
            questList.append(KeepFurnacesFired(furnaces[:skillLevel]))
        super().__init__(questList)
        self.metaDescription = "KeepFurnacesFiredMeta"

class KeepFurnaceFiredMeta(MetaQuest2):
    def __init__(self,furnace,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        self.questList = []
        self.fireFurnaceQuest = None
        self.waitQuest = None
        self.furnace = furnace
        super().__init__(self.questList,lifetime=lifetime)
        self.furnace.addListener(self.recalculate)
        self.metaDescription = "KeepFurnaceFiredMeta"

    def recalculate(self):
        if not self.character:
            super().recalculate()
            return

        if self.furnace.activated:
            self.pause()
        else:
            self.unpause()

        if self.fireFurnaceQuest and self.fireFurnaceQuest.completed:
            self.fireFurnaceQuest = None

        if not self.fireFurnaceQuest and not self.furnace.activated:
            self.fireFurnaceQuest = FireFurnaceMeta(self.furnace)
            self.fireFurnaceQuest.assignToCharacter(self.character)
            self.fireFurnaceQuest.activate()
            self.fireFurnaceQuest.addListener(self.recalculate)
            self.questList.append(self.fireFurnaceQuest)
            self.changed()

        if not self.questList:
            self.waitQuest = WaitForDeactivationQuest(self.furnace)
            self.waitQuest.assignToCharacter(self.character)
            self.waitQuest.activate()
            self.waitQuest.addListener(self.recalculate)
            self.questList.insert(0,self.waitQuest)
            self.changed()

        super().recalculate()

    def triggerCompletionCheck(self):
        pass

class FireFurnaceMeta(MetaQuest2):
    def __init__(self,furnace,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        self.activateQuest = None
        self.collectQuest = None
        self.questList = []
        self.furnace = furnace
        super().__init__(self.questList)
        self.metaDescription = "FireFurnaceMeta"+str(self)

    def recalculate(self):
        if self.collectQuest and self.collectQuest.completed:
            self.collectQuest = None

        if not self.collectQuest:
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
                self.collectQuest = CollectQuest()
                self.collectQuest.assignToCharacter(self.character)
                self.collectQuest.addListener(self.recalculate)
                self.questList.insert(0,self.collectQuest)
                self.collectQuest.activate()
                self.changed()

                if self.activateQuest:
                    self.activateQuest.pause()

        if self.activateQuest and not self.collectQuest:
            self.activateQuest.unpause()

        if not self.activateQuest and not self.collectQuest and not self.furnace.activated:
            self.activateQuest = ActivateQuest(self.furnace)
            self.activateQuest.assignToCharacter(self.character)
            self.questList.append(self.activateQuest)
            self.activateQuest.activate()
            self.activateQuest.addListener(self.recalculate)
            self.changed()

        super().recalculate()

    def assignToCharacter(self,character):
        character.addListener(self.recalculate)
        super().assignToCharacter(character)

    def triggerCompletionCheck(self):
        if self.furnace.activated:
            self.postHandler()
            
        super().triggerCompletionCheck()

class PatrolQuest(MetaQuest):
    def __init__(self,waypoints=[],startCinematics=None,looped=True,lifetime=None):
        quests = []

        for waypoint in waypoints:
            quest = MoveQuest(waypoint[0],waypoint[1],waypoint[2])
            quests.append(quest)

        self.lifetime = lifetime

        super().__init__(quests,startCinematics=startCinematics,looped=looped)

    def activate(self):
        if self.lifetime:
            class endQuestEvent(object):
                def __init__(subself,tick):
                    subself.tick = tick

                def handleEvent(subself):
                    self.postHandler()

            self.character.room.addEvent(endQuestEvent(self.character.room.timeIndex+self.lifetime))

        super().activate()

class ExamineQuest(Quest):
    def __init__(self,waypoints=[],startCinematics=None,looped=True,lifetime=None):
        self.lifetime = lifetime
        self.description = "please examine your environment"
        super().__init__(startCinematics=startCinematics)

    def activate(self):
        if self.lifetime:
            class endQuestEvent(object):
                def __init__(subself,tick):
                    subself.tick = tick

                def handleEvent(subself):
                    self.postHandler()

            self.character.room.addEvent(endQuestEvent(self.character.room.timeIndex+self.lifetime))

        super().activate()

class RefillDrinkQuest(ActivateQuest):
    def __init__(self,startCinematics=None):
        super().__init__(toActivate=terrain.tutorialVatProcessing.gooDispenser,desiredActive=True,startCinematics=startCinematics)

    def triggerCompletionCheck(self):
        for item in self.character.inventory:
            if isinstance(item,items.GooFlask):
                if item.uses > 90:
                    self.postHandler()

class DrinkQuest(Quest):
    def __init__(self,startCinematics=None):
        self.description = "please drink"
        super().__init__(startCinematics=startCinematics)

    def assignToCharacter(self,character):
        character.addListener(self.recalculate)
        super().assignToCharacter(character)

    def solver(self,character):
        for item in character.inventory:
            if isinstance(item,items.GooFlask):
                if item.uses > 0:
                    item.apply(character)
                    self.postHandler()
                    break

    def triggerCompletionCheck(self):
        if self.character.satiation > 30:
            self.postHandler()
            
        super().triggerCompletionCheck()

class SurviveQuest(Quest):
    def __init__(self,startCinematics=None,looped=True,lifetime=None):
        self.description = "survive"
        self.drinkQuest = None
        self.refillQuest = None
        super().__init__(startCinematics=startCinematics)

    def assignToCharacter(self,character):
        super().assignToCharacter(character)
        character.addListener(self.recalculate)

    def recalculate(self):
        if self.drinkQuest and self.drinkQuest.completed:
            self.drinkQuest = None
        if self.refillQuest and self.refillQuest.completed:
            self.refillQuest = None

        for item in self.character.inventory:
            if isinstance(item,items.GooFlask):
                if item.uses < 10 and not self.refillQuest:
                    self.refillQuest = RefillDrinkQuest()
                    self.character.assignQuest(self.refillQuest,active=True)


        if self.character.satiation < 31:
            if not self.drinkQuest:
                self.drinkQuest = DrinkQuest()
                self.character.assignQuest(self.drinkQuest,active=True)

class HopperDuty(Quest):
    def __init__(self,startCinematics=None,looped=True,lifetime=None):
        self.description = "hopper duty"
        super().__init__(startCinematics=startCinematics)

class ClearRubble(MetaQuest2):
    def __init__(self,followUp=None,startCinematics=None,failTrigger=None,lifetime=None):
        questList = []
        for item in terrain.itemsOnFloor:
            if isinstance(item,items.Scrap):
                questList.append(PickupQuest(item))
        super().__init__(questList)
        self.metaDescription = "clear rubble"
