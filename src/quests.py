import src.items as items
import src.saveing as saveing
import json

# HACK: common variables with modules
showCinematic = None
loop = None
callShow_or_exit = None

############################################################
###
##  building block quests
#   not intended for direct use unless you know what you are dooing
#
############################################################

'''
the base class for all quests
'''
class Quest(saveing.Saveable):
    '''
    straightforward state initialization
    '''
    def __init__(self,followUp=None,startCinematics=None,lifetime=0,creator=None):
        super().__init__()

        # set basic attributes
        self.type = "Quest"
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

        self.attributesToStore.append("type")
        self.attributesToStore.append("active")
        self.attributesToStore.append("completed")
        self.attributesToStore.append("reputationReward")
        self.attributesToStore.append("lifetime")
        self.callbacksToStore.append("endTrigger")

        self.lifetime = lifetime
        self.lifetimeEvent = None

        # set id
        self.id = {
                    "counter":creator.getCreationCounter()
                  }
        self.id["creator"] = creator.id
        self.id = json.dumps(self.id, sort_keys=True).replace("\\","")

        # save initial state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    get difference in state since creation
    '''
    def getDiffState(self):
        result = super().getDiffState()
        # bad code: repeated store none or id scheme
        character = None
        if self.character:
            character = self.character.id
        if not character == self.initialState["character"]:
            result["character"] = character
        return result

    '''
    get state as dict
    '''
    def getState(self):
        state = super().getState()
        
        if self.character:
            state["character"] = self.character.id
        else:
            state["character"] = None
        return state

    '''
    set state as dict
    '''
    def setState(self,state):
       super().setState(state)

       if "character" in state and state["character"]:
           '''
           set value
           '''
           def setCharacter(character):
               self.character = character
           loadingRegistry.callWhenAvailable(state["character"],setCharacter)

    '''
    register callback
    '''
    def startWatching(self, target, callback):
        target.addListener(callback)
        self.watched.append((target,callback))
    
    '''
    unregister callback
    '''
    def stopWatching(self, target, callback):
        target.delListener(callback)
        self.watched.remove((target,callback))

    '''
    unregister all callback
    '''
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
        if self.reputationReward:
            self.reputationReward *= -2
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
        # stop listening
        self.stopWatchingAll()

        # smooth over impossible states
        if not self.active:
            debugMessages.append("this should not happen (posthandler called on inactive quest ("+str(self)+")) "+str(self.character))
            return
        if not self.character:
            debugMessages.append("this should not happen (posthandler called on quest without character ("+str(self)+")) "+str(self.character))
            # trigger follow up functions
            if self.endTrigger:
                self.callIndirect(self.endTrigger)
            if self.endCinematics:
                showCinematic(self.endCinematics)            
                loop.set_alarm_in(0.0, callShow_or_exit, '.')
            
            # deactivate
            self.deactivate()

            return
        if self.completed:
            debugMessages.append("this should not happen (posthandler called on completed quest ("+str(self)+")) "+str(self.character))
            if self in self.character.quests:
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
        if not self.type in self.character.questsDone:
            self.character.questsDone.append(self.type)

        if self in self.character.quests:
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
            self.callIndirect(self.endTrigger)
        if self.endCinematics:
            showCinematic(self.endCinematics)            
            loop.set_alarm_in(0.0, callShow_or_exit, '.')

        # deactivate
        self.deactivate()

        # start next quest
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

    def timeOut(self):
        self.fail()

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
        if self.lifetime and not self.lifetimeEvent:
            self.lifetimeEvent = events.EndQuestEvent(gamestate.tick+self.lifetime,callback={"container":self,"method":"timeOut"},creator=self)
            self.character.addEvent(self.lifetimeEvent)

        # recalculate and notify listeners
        self.recalculate()
        self.changed()

    '''
    switch from active to just existing
    '''
    def deactivate(self):
        self.active = False
        if self.lifetimeEvent and self.character and self.lifetimeEvent in self.character.events:
            self.character.removeEvent(self.lifetimeEvent)
            self.lifetimeEvent = None
        self.changed()

'''
a container quest containing a list of quests that have to be handled in sequence
'''
class MetaQuestSequence(Quest):
    '''
    state initialization
    bad code: quest param does not work anymore and should be removed
    '''
    def __init__(self,quests,startCinematics=None,lifetime=None,creator=None):
        # set state
        self.metaDescription = "meta"
        self.subQuestsOrig = quests.copy()
        self.subQuests = quests
        super().__init__(startCinematics=startCinematics,lifetime=lifetime,creator=creator)
        
        # listen to subquests
        if len(self.subQuests):
            self.startWatching(self.subQuests[0],self.recalculate)

        # save state and register
        self.type = "MetaQuestSequence"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    get difference in state since creation
    '''
    def getDiffState(self):
        state = super().getDiffState()
        if not self.metaDescription == state["metaDescription"]:
            state["metaDescription"] = self.metaDescription

        # store quests
        (questStates,changedQuests,newQuests,removedQuests) = self.getDiffList(self.subQuests,self.initialState["subQuests"]["ids"])
        quests = {}
        if changedQuests:
            quests["changed"] = changedQuests
        if newQuests:
            quests["new"] = newQuests
        if removedQuests:
            quests["removed"] = removedQuests
        if questStates:
            quests["states"] = questStates
        if questStates or removedQuests:
            state["subQuests"] = quests

        return state

    '''
    get state as dict
    '''
    def getState(self):
        state = super().getState()

        # store attributes
        state["metaDescription"] = self.metaDescription

        # store sub quests
        state["subQuests"] = {}
        state["subQuests"]["ids"] = []
        state["subQuests"]["states"] = {}
        for quest in self.subQuests:
            state["subQuests"]["ids"].append(quest.id)
            state["subQuests"]["states"][quest.id] = quest.getState()

        return state
    
    '''
    set state as dict
    '''
    def setState(self,state):
        super().setState(state)
        # load attributes
        if "metaDescription" in state:
            self.metaDescription = state["metaDescription"]
                    
        # load sub quests
        if "subQuests" in state:
            if "ids" in state["subQuests"]:
                # load static quest list
                for thingId in state["subQuests"]["ids"]:
                    # bad code: current list should be emptied instead of skipping
                    skip = False
                    for thing in self.subQuests:
                       if thingId == thing.id:
                           skip = True
                           continue
                    if skip:
                        continue
                    
                    # create and add quest
                    thingState = state["subQuests"]["states"][thingId]
                    thing = getQuestFromState(thingState)
                    thing.setState(thingState)
                    self.subQuests.append(thing)
            if "changed" in state["subQuests"]:
                # update changed quests
                for thing in self.quests:
                    if thing.id in state["subQuests"]["states"]:
                        thing.setState(state["subQuests"]["states"][thing.id])
            if "removed" in state["subQuests"]:
                # remove quests
                for thing in self.quests:
                    if thing.id in state["subQuests"]["removed"]:
                        self.quests.remove(thing)
            if "new" in state["subQuests"]:
                # add new quests
                for thingId in state["subQuests"]["new"]:
                    thingState = state["subQuests"]["states"][thingId]
                    thing = getQuestFromState(thingState)
                    thing.setState(thingState)
                    self.subQuests.append(thing)

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
            debugMessages.append("triggerCompletionCheck called on inactive "+str(self))
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
            debugMessages.append("triggerCompletionCheck called on inactive "+str(self))
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
                self.character.recalculatePath()
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

        if self.character:
            self.subQuests[0].assignToCharacter(self.character)
            self.character.recalculatePath()

        # listen to quest
        self.startWatching(self.subQuests[0],self.recalculate)

        # deactivate last active quest
        if addFront:
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
    def __init__(self,quests,startCinematics=None,looped=False,lifetime=None,creator=None):
        self.subQuests = quests
        self.lastActive = None
        self.metaDescription = "meta"

        super().__init__(startCinematics=startCinematics,lifetime=lifetime,creator=creator)

        # listen to subquests
        for quest in self.subQuests:
            self.startWatching(quest,self.recalculate)

        # store initial state and register
        self.type = "MetaQuestParralel"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    get difference in state since creation
    '''
    def getDiffState(self):
        state = super().getDiffState()

        # store attributes
        if not self.metaDescription == self.initialState["metaDescription"]:
            state["metaDescription"] = self.metaDescription
        # bad code: repeated store none or id scheme
        lastActive = None
        if self.lastActive:
            lastActive = lastActive.id
        if not lastActive == self.initialState["lastActive"]:
            state["lastActive"] = lastActive

        # store quests
        (questStates,changedQuests,newQuests,removedQuests) = self.getDiffList(self.subQuests,self.initialState["subQuests"]["ids"])
        quests = {}
        if changedQuests:
            quests["changed"] = changedQuests
        if newQuests:
            quests["new"] = newQuests
        if removedQuests:
            quests["removed"] = removedQuests
        if questStates:
            quests["states"] = questStates
        if questStates or removedQuests:
            state["subQuests"] = quests

        return state

    '''
    get state as dict
    '''
    def getState(self):
        state = super().getState()
        state["metaDescription"] = self.metaDescription
        state["subQuests"] = {}
        state["subQuests"]["ids"] = []
        state["subQuests"]["states"] = {}
        for quest in self.subQuests:
            state["subQuests"]["ids"].append(quest.id)
            state["subQuests"]["states"][quest.id] = quest.getState()
        if self.lastActive:
            state["lastActive"] = self.lastActive.id
        else:
            state["lastActive"] = None
        return state
    
    '''
    set state as dict
    '''
    def setState(self,state):
        super().setState(state)
                    
        # load quests
        if "subQuests" in state:
            if "ids" in state["subQuests"]:
                # load static quest list
                for thingId in state["subQuests"]["ids"]:
                    # bad code: current list should be emptied instead of skipping
                    skip = False
                    for thing in self.subQuests:
                       if thingId == thing.id:
                           skip = True
                           continue
                    if skip:
                        continue
                    
                    # create and add quest
                    thingState = state["subQuests"]["states"][thingId]
                    thing = getQuestFromState(thingState)
                    thing.setState(thingState)
                    self.subQuests.append(thing)
            if "changed" in state["subQuests"]:
                # update changed quests
                for thing in self.quests:
                    if thing.id in state["subQuests"]["states"]:
                        thing.setState(state["subQuests"]["states"][thing.id])
            if "removed" in state["subQuests"]:
                # remove quests
                for thing in self.quests:
                    if thing.id in state["subQuests"]["removed"]:
                        self.quests.remove(thing)
            if "new" in state["subQuests"]:
                # add new quests
                for thingId in state["subQuests"]["new"]:
                    thingState = state["subQuests"]["states"][thingId]
                    thing = getQuestFromState(thingState)
                    thing.setState(thingState)
                    self.subQuests.append(thing)

        # load attributes
        if "metaDescription" in state:
            self.metaDescription = state["metaDescription"]
        # bad code: repetetive load from id or none pattern
        if "lastActive" in state:
            if state["lastActive"]:
                '''
                set value
                '''
                def setState(thing):
                    self.lastActive = thing
                loadingRegistry.callWhenAvailable(state["lastActive"],setState)
            else:
                state["lastActive"] = None
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
        # add actual quest name
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

        # add subquest
        counter = 0
        for quest in self.subQuests:
            if asList:
                questDescription = []

                # indicate state by arrow type
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

                # set colors
                if colored:
                    import urwid
                    if active and quest == self.lastActive:
                        color = "#0f0"
                    else:
                        color = "#090"
                    deko = (urwid.AttrSpec(color,"default"),deko)

                # add subquest desription
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
                # add subquest desription
                questDescription = "\n    ".join(quest.getDescription().split("\n"))+"\n"

                # indicate state by arrow type
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
            # show subquest description
            questDescription = "\n    ".join(quest.description.split("\n"))+"\n"
            
            # indicate state by arrow type
            if quest == self.lastActive:
                if quest.active:
                    out += "  ->"+questDescription
                else:
                    if debug:
                        out += "YYYY"+questDescription
                        debugMessages.append(" impossible quest state")
            elif quest.paused:
                out += "  - "+questDescription
            elif quest.active:
                out += "  * "+questDescription
            else:
                if debug:
                    out += "XXXX"+questDescription
                    debugMessages.append(" impossible quest state")
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
        self.subQuests.insert(0,quest)
        self.startWatching(quest,self.recalculate)

'''
make a character move somewhere. It assumes nothing goes wrong. 
You probably want to use MoveQuestMeta instead
'''
class NaiveMoveQuest(Quest):
    '''
    straightfoward state setting
    '''
    def __init__(self,room=None,x=None,y=None,sloppy=False,followUp=None,startCinematics=None,creator=None):
        self.dstX = x
        self.dstY = y
        self.room = room
        self.sloppy = sloppy
        self.description = "please go to coordinate "+str(self.dstX)+"/"+str(self.dstY)    
        super().__init__(followUp,startCinematics=startCinematics,creator=creator)

        # save initial state and register
        self.type = "NaiveMoveQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    check if character is in the right place
    '''
    def triggerCompletionCheck(self):
        # a inactive quest cannot complete
        if not self.active:
            debugMessages.append("triggerCompletionCheck called on inactive "+str(self))
            return 

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
    get difference in state since creation
    '''
    def getDiffState(self):
        state = super().getDiffState()
        room = None
        if hasattr(self,"room") and self.room:
            room = None # bad code: should be the room id
        if not room == self.initialState["room"]:
            state["room"] = room.id
        if not self.dstX == self.initialState["dstX"]:
            state["dstX"] = self.dstX
        if not self.dstY == self.initialState["dstY"]:
            state["dstY"] = self.dstY
        if not self.description == self.initialState["description"]:
            state["description"] = self.description
        if not self.sloppy == self.initialState["sloppy"]:
            state["sloppy"] = self.sloppy
        return state

    '''
    get state as dict
    '''
    def getState(self):
        # bad code: repeated store id or none pattern
        state = super().getState()
        if hasattr(self,"room") and self.room:
            state["room"] = self.room.id
        else:
            state["room"] = None
        state["dstX"] = self.dstX
        state["dstY"] = self.dstY
        state["description"] = self.description
        state["sloppy"] = self.sloppy
        return state

    '''
    set state as dict
    '''
    def setState(self,state):
        super().setState(state)
        # bad code: repetetive load from id or none pattern
        if "room" in state:
            if state["room"]:
                '''
                set value
                '''
                def setRoom(room):
                    self.room = room
                loadingRegistry.callWhenAvailable(state["room"],setRoom)
                pass
            else:
                self.room = None

        # load attributes
        if "dstX" in state:
            self.dstX = state["dstX"]
        if "dstY" in state:
            self.dstY = state["dstY"]
        if "description" in state:
            self.description = state["description"]
        if "sloppy" in state:
            self.sloppy = state["sloppy"]

        if "character" in state and state["character"]:
           '''
           set value
           '''
           def watchCharacter(character):
               self.startWatching(character,self.recalculate)
           loadingRegistry.callWhenAvailable(state["character"],watchCharacter)

'''
quest to enter a room. It assumes nothing goes wrong. 
You probably want to use EnterRoomQuestMeta instead
'''
class NaiveEnterRoomQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,room,followUp=None,startCinematics=None,creator=None):
        self.description = "please enter the room: "+room.name+" "+str(room.xPosition)+" "+str(room.yPosition)
        self.room = room
        # set door as target
        self.dstX = self.room.walkingAccess[0][0]+room.xPosition*15+room.offsetX
        self.dstY = self.room.walkingAccess[0][1]+room.yPosition*15+room.offsetY
        super().__init__(followUp,startCinematics=startCinematics,creator=creator)

        # save initial state and register
        self.type = "NaiveEnterRoomQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    assign character and 
    '''
    def assignToCharacter(self,character):
        super().assignToCharacter(character)
        self.startWatching(character,self.recalculate)

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
The naive pickup quest. It assumes nothing goes wrong. 
You probably want to use PickupQuest instead
'''
class NaivePickupQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,toPickup,followUp=None,startCinematics=None,creator=None):
        self.toPickup = toPickup
        self.dstX = self.toPickup.xPosition
        self.dstY = self.toPickup.yPosition
        super().__init__(followUp,startCinematics=startCinematics,creator=creator)
        self.startWatching(self.toPickup,self.recalculate)
        self.startWatching(self.toPickup,self.triggerCompletionCheck)
        self.description = "naive pickup"

        # save initial state and register
        self.type = "NaivePickupQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)
   
    '''
    check whether item is in characters inventory
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
    def __init__(self,questDispenser,assign=True,followUp=None,startCinematics=None,creator=None):
        self.questDispenser = questDispenser
        self.quest = None
        self.assign = assign
        super().__init__(followUp,startCinematics=startCinematics,creator=creator)
        self.description = "naive get quest"

        # save initial state and register
        self.type = "NaiveGetQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    check whether the chracter has gotten a quest
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
    def __init__(self,quest,followUp=None,startCinematics=None,creator=None):
        super().__init__(followUp,startCinematics=startCinematics,creator=creator)
        self.quest = quest
        self.description = "naive get reward"
        self.done = False

        # save initial state and register
        self.type = "NaiveGetReward"
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
    bad code: rewarding should be handled within the quest
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
    def __init__(self,toKill,followUp=None,startCinematics=None,creator=None):
        self.toKill = toKill
        super().__init__(followUp,startCinematics=startCinematics,creator=creator)
        self.description = "naive murder"

        # save initial state and register
        self.type = "NaiveMurderQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
The naive quest to knock out someone. It assumes nothing goes wrong. 
You probably want to use KnockOutQuest instead
'''
class NaiveKnockOutQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,target,followUp=None,startCinematics=None,creator=None):
        self.target = target
        super().__init__(followUp,startCinematics=startCinematics,creator=creator)
        self.description = "naive knock out"

        # save initial state and register
        self.type = "NaiveKnockOutQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    check whether target is dead
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if self.target.unconcious:
                self.postHandler()

    '''
    knock the target out
    bad code: murdering should happen within a character
    '''
    def solver(self,character):
        self.target.fallUnconcious()
        self.triggerCompletionCheck()
        return True

'''
The naive quest to wape up someone. It assumes nothing goes wrong. 
You probably want to use WakeUpQuest instead
'''
class NaiveWakeUpQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,target,followUp=None,startCinematics=None,creator=None):
        self.target = target
        super().__init__(followUp,startCinematics=startCinematics,creator=creator)
        self.description = "naive wake up"

        # save initial state and register
        self.type = "NaiveWakeUpQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    check whether target is dead
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if not self.target.unconcious:
                self.postHandler()
            elif self.target.dead:
                self.fail()

    '''
    knock the target out
    '''
    def solver(self,character):
        self.target.wakeUp()
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
    def __init__(self,toActivate=None,followUp=None,startCinematics=None,creator=None):
        self.toActivate = toActivate
        super().__init__(followUp,startCinematics=startCinematics,creator=creator)
        self.activated = False

        # save initial state and register
        self.type = "NaiveActivateQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

        self.description = "naive activate "+str(self.toActivate)

    '''
    callback for activation
    checks if the activated item is the item to activate
    '''
    def registerActivation(self,info):
        if self.toActivate == info:
            self.activated = True
            self.triggerCompletionCheck()

    '''
    watch for the character activate something
    '''
    def activate(self):
        super().activate()
        self.character.addListener(self.registerActivation,"activate")

    '''
    check whether target was activated
    uses internal state
    '''
    def triggerCompletionCheck(self):
        if self.active:
            if self.activated:
                self.postHandler()

    '''
    get difference in state since creation
    '''
    def getDiffState(self):
        state = super().getDiffState()
        toActivate = None
        if hasattr(self,"toActivate") and self.toActivate:
            toActivate = self.toActivate.id
        if not toActivate == self.initialState["toActivate"]:
            state["toActivate"] = toActivate
        return state

    '''
    get state as dict
    '''
    def getState(self):
        state = super().getState()
        if hasattr(self,"toActivate") and self.toActivate:
            state["toActivate"] = self.toActivate.id
        else:
            state["toActivate"] = None
        return state
    
    '''
    set state as dict
    '''
    def setState(self,state):
        super().setState(state)
        if "toActivate" in state:
            # bad code: repetetive load from id or none pattern
            if state["toActivate"]:
                '''
                set value
                '''
                def setState(thing):
                    self.toActivate = thing
                loadingRegistry.callWhenAvailable(state["toActivate"],setState)
            else:
                self.toActivate = None

        # add listener
        if self.active and self.character:
            self.character.addListener(self.registerActivation,"activate")

    '''
    activate the target
    bad code: activate event should be sent from character
    '''
    def solver(self,character):
        self.toActivate.apply(character)
        character.changed("activate",self.toActivate)
        return True

'''
The naive quest to drop something. It assumes nothing goes wrong. 
You probably want to use DropQuest instead
'''
class NaiveDropQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,toDrop,room,xPosition,yPosition,followUp=None,startCinematics=None,creator=None):
        self.dstX = xPosition
        self.dstY = yPosition
        self.room = room
        self.toDrop = toDrop
        super().__init__(followUp,startCinematics=startCinematics,creator=creator)
        self.startWatching(self.toDrop,self.recalculate)
        self.startWatching(self.toDrop,self.triggerCompletionCheck)
        self.description = "naive drop"
        self.dropped = False

        # save initial state and register
        self.type = "NaiveDropQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    check whether item was dropped
    '''
    def triggerCompletionCheck(self):
        if self.active:
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
You probably want to use DelegateQuest instead
'''
class NaiveDelegateQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,quest,creator=None):
        super().__init__(creator=creator)
        self.quest = quest
        self.description = "naive delegate quest"
        self.startWatching(self.quest,self.triggerCompletionCheck)

        # save initial state and register
        self.type = "NaiveDelegateQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)
    
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

############################################################
###
##  wait quests
#
############################################################

'''
wait until quest is aborted
'''
class WaitQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,followUp=None,startCinematics=None,lifetime=None,creator=None):
        self.description = "please wait"
        super().__init__(lifetime=lifetime,creator=creator)

        # save initial state and register
        self.type = "WaitQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
    def __init__(self,item,followUp=None,startCinematics=None,lifetime=None,creator=None):
        self.item = item
        self.description = "please wait for deactivation of "+self.item.description

        super().__init__(lifetime=lifetime,creator=creator)

        # listen to item
        self.startWatching(self.item,self.recalculate)
        self.pause() # bad code: why pause by default

        # save initial state and register
        self.type = "WaitForDeactivationQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
    def __init__(self,quest,creator=None):
        self.quest = quest
        self.description = "please wait for the quest to completed"
        super().__init__(creator=creator)
        self.startWatching(self.quest,self.triggerCompletionCheck)

        # save initial state and register
        self.type = "WaitForQuestCompletion"
        self.initialState = self.getState()
        loadingRegistry.register(self)

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

###############################################################
###
##     common actions
#
###############################################################

'''
quest to drink something
'''
class DrinkQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,startCinematics=None,creator=None):
        self.description = "please drink"
        super().__init__(startCinematics=startCinematics,creator=creator)

        # save initial state and register
        self.type = "DrinkQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
    check if the character is still thirsty
    '''
    def triggerCompletionCheck(self):
        if self.character.satiation > 800:
            self.postHandler()
            
        super().triggerCompletionCheck()

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)
        if state["character"]:
            self.startWatching(self.character,self.recalculate)


'''
ensure own survival
'''
class SurviveQuest(Quest):
    '''
    straightforward state initialization
    '''
    def __init__(self,startCinematics=None,looped=True,lifetime=None,creator=None):
        self.description = "survive"
        self.drinkQuest = None
        self.refillQuest = None
        super().__init__(startCinematics=startCinematics,creator=creator)

        # save initial state and register
        self.type = "SurviveQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
                    self.refillQuest = RefillDrinkQuest(creator=self)
                    self.character.assignQuest(self.refillQuest,active=True)

        # drink
        if self.character.satiation < 301:
            if not self.drinkQuest:
                self.drinkQuest = DrinkQuest(creator=self)
                self.character.assignQuest(self.drinkQuest,active=True)

'''
quest for entering a room
'''
class EnterRoomQuestMeta(MetaQuestSequence):
    '''
    basic state initialization
    '''
    def __init__(self,room,followUp=None,startCinematics=None,creator=None):
        super().__init__([],creator=creator)
        self.room = room
        self.addQuest(NaiveEnterRoomQuest(room,creator=self))
        self.recalculate()
        self.metaDescription = "enterroom Meta"
        self.leaveRoomQuest = None

        # save initial state and register
        self.type = "EnterRoomQuestMeta"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    add quest to leave room if needed
    '''
    def recalculate(self):
        if not self.active:
            return 
        if self.leaveRoomQuest and self.leaveRoomQuest.completed:
            self.leaveRoomQuest = None
        if not self.leaveRoomQuest and self.character.room and not self.character.room == self.room:
            self.leaveRoomQuest = LeaveRoomQuest(self.character.room,creator=self)
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
    def __init__(self,room=None,x=None,y=None,sloppy=False,followUp=None,startCinematics=None,creator=None,lifetime=None):
        super().__init__([],creator=creator,lifetime=lifetime)
        if not ( x == None and y == None ):
            self.moveQuest = NaiveMoveQuest(room,x,y,sloppy=sloppy,creator=self)
            self.questList = [self.moveQuest]
        else:
            self.questList = []
        self.enterRoomQuest = None
        self.leaveRoomQuest = None
        self.room = room
        for quest in reversed(self.questList):
            self.addQuest(quest)
        self.metaDescription = "move meta"

        # save initial state and register
        self.type = "MoveQuestMeta"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    move to correct room if nesseccary
    '''
    def recalculate(self):
        if self.active:
            # leave wrong room
            if self.leaveRoomQuest and self.leaveRoomQuest.completed:
                self.leaveRoomQuest = None
            if not self.leaveRoomQuest and (not self.room and self.character.room):
                self.leaveRoomQuest = LeaveRoomQuest(self.character.room,creator=self)
                self.addQuest(self.leaveRoomQuest)

            # enter correct room
            if self.enterRoomQuest and self.enterRoomQuest.completed:
                self.enterRoomQuest = None
            if (not self.enterRoomQuest and (self.room and ((not self.character.room) or (not self.character.room == self.room)))):
                self.enterRoomQuest = EnterRoomQuestMeta(self.room,creator=self)
                self.addQuest(self.enterRoomQuest)
        super().recalculate()
    
    '''
    assign to character and listen to character
    '''
    def assignToCharacter(self,character):
        self.startWatching(character,self.recalculate)
        super().assignToCharacter(character)

    '''
    get difference in state since creation
    '''
    def getDiffState(self):
        state = super().getDiffState()
        #bad code: repeated pattern
        room = None
        if hasattr(self,"room") and self.room:
            room = None
        if not room == self.initialState["room"]:
            state["room"] = room.id
        return state

    '''
    get state as dict
    '''
    def getState(self):
        #bad code: repeated pattern
        state = super().getState()
        if hasattr(self,"room") and self.room:
            state["room"] = self.room.id
        else:
            state["room"] = None
        return state

    '''
    set state as dict
    '''
    def setState(self,state):
        super().setState(state)
        if "room" in state:
            # bad code: repetetive load from id or none pattern
            if state["room"]:
                '''
                set value
                '''
                def setRoom(room):
                    self.room = room
                loadingRegistry.callWhenAvailable(state["room"],setRoom)
                pass
            else:
                self.room = None

        if "character" in state and state["character"]:
           '''
           set value
           '''
           def watchCharacter(character):
               self.startWatching(character,self.recalculate)
           loadingRegistry.callWhenAvailable(state["character"],watchCharacter)

'''
drop a item somewhere
'''
class DropQuestMeta(MetaQuestSequence):
    '''
    generate quests to move and drop item
    '''
    def __init__(self,toDrop,room,xPosition,yPosition,followUp=None,startCinematics=None,creator=None):
        super().__init__([],creator=creator)
        self.toDrop = toDrop
        self.moveQuest = MoveQuestMeta(room,xPosition,yPosition,creator=self)
        self.questList = [self.moveQuest,NaiveDropQuest(toDrop,room,xPosition,yPosition,creator=self)]
        self.room = room
        self.xPosition = xPosition
        self.yPosition = yPosition
        for quest in reversed(self.questList):
            self.addQuest(quest)
        self.metaDescription = "drop Meta"

        # save initial state and register
        self.type = "DropQuestMeta"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    re-add the movement quest if neccessary
    '''
    def recalculate(self):
        if self.active:
            if self.moveQuest and self.moveQuest.completed:
                self.moveQuest = None
            if not self.moveQuest and not (self.room == self.character.room and self.xPosition == self.character.xPosition and self.yPosition == self.character.yPosition):
                self.moveQuest = MoveQuestMeta(self.room,self.xPosition,self.yPosition,creator=self)
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
    def __init__(self,toPickup,followUp=None,startCinematics=None,creator=None):
        super().__init__([],creator=creator)
        self.toPickup = toPickup
        self.sloppy = not self.toPickup.walkable
        self.moveQuest = MoveQuestMeta(self.toPickup.room,self.toPickup.xPosition,self.toPickup.yPosition,sloppy=self.sloppy,creator=self)
        self.questList = [self.moveQuest,NaivePickupQuest(self.toPickup,creator=self)]
        for quest in reversed(self.questList):
            self.addQuest(quest)
        self.metaDescription = "pickup Meta"

        # save initial state and register
        self.type = "PickupQuestMeta"
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
                    if self.toPickup.xPosition == None or self.toPickup.yPosition == None:
                        reAddMove = False
                    elif not (self.toPickup.room == self.character.room and self.toPickup.xPosition == self.character.xPosition and self.toPickup.yPosition == self.character.yPosition):
                        reAddMove = True
                else:
                    if self.toPickup.xPosition == None or self.toPickup.yPosition == None:
                        reAddMove = False
                    elif not (self.toPickup.room == self.character.room and (
                                                             (self.toPickup.xPosition-self.character.xPosition in (-1,0,1) and self.toPickup.yPosition == self.character.yPosition) or 
                                                             (self.toPickup.yPosition-self.character.yPosition in (-1,0,1) and self.toPickup.xPosition == self.character.xPosition))):
                        reAddMove = True

                # re add the movement
                if reAddMove:
                    self.moveQuest = MoveQuestMeta(self.toPickup.room,self.toPickup.xPosition,self.toPickup.yPosition,sloppy=self.sloppy,creator=self)
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
    def __init__(self,toActivate=None,followUp=None,desiredActive=True,startCinematics=None,creator=None):
        super().__init__([],creator=creator)
        self.toActivate = toActivate
        if toActivate:
            self.sloppy = not self.toActivate.walkable
            self.moveQuest = MoveQuestMeta(toActivate.room,toActivate.xPosition,toActivate.yPosition,sloppy=self.sloppy,creator=self)
            self.questList = [self.moveQuest,NaiveActivateQuest(toActivate,creator=self)]
        else:
            self.sloppy = False
            self.questList = []

        for quest in reversed(self.questList):
            self.addQuest(quest)
        self.metaDescription = "activate Quest"

        # save initial state and register
        self.type = "ActivateQuestMeta"
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
                    if not hasattr(self.toActivate,"xPosition") or not hasattr(self.toActivate,"yPosition"):
                        reAddMove = False
                    elif not (self.toActivate.room == self.character.room and self.toActivate.xPosition == self.character.xPosition and self.toActivate.yPosition == self.character.yPosition):
                        reAddMove = True
                else:
                    if not hasattr(self.toActivate,"xPosition") or not hasattr(self.toActivate,"yPosition"):
                        reAddMove = False
                    elif not (self.toActivate.room == self.character.room and (
                                                             (self.toActivate.xPosition-self.character.xPosition in (-1,0,1) and self.toActivate.yPosition == self.character.yPosition) or 
                                                             (self.toActivate.yPosition-self.character.yPosition in (-1,0,1) and self.toActivate.xPosition == self.character.xPosition))):
                        reAddMove = True

                # re add the movement
                if reAddMove:
                    self.moveQuest = MoveQuestMeta(self.toActivate.room,self.toActivate.xPosition,self.toActivate.yPosition,sloppy=self.sloppy,creator=self)
                    self.addQuest(self.moveQuest)
        super().recalculate()
        
    '''
    get difference in state since creation
    '''
    def getDiffState(self):
        state = super().getDiffState()
        #bad code: repeated pattern
        sloppy = None
        if hasattr(self,"sloppy") and self.sloppy:
            sloppy = self.sloppy
        if not sloppy == self.initialState["sloppy"]:
            state["sloppy"] = sloppy
        #bad code: repeated pattern
        moveQuest = None
        if hasattr(self,"moveQuest") and self.moveQuest:
            moveQuest = self.moveQuest.id
        if not moveQuest == self.initialState["moveQuest"]:
            state["moveQuest"] = moveQuest
        #bad code: repeated pattern
        toActivate = None
        if hasattr(self,"toActivate") and self.toActivate:
            toActivate = self.toActivate.id
        if not toActivate == self.initialState["toActivate"]:
            state["toActivate"] = toActivate
        return state

    '''
    get state as dict
    '''
    def getState(self):
        state = super().getState()
        #bad code: repeated pattern
        if hasattr(self,"sloppy") and self.sloppy:
            state["sloppy"] = self.sloppy
        else:
            self.sloppy = None
        #bad code: repeated pattern
        if hasattr(self,"moveQuest") and self.moveQuest:
            state["moveQuest"] = self.moveQuest.id
        else:
            state["moveQuest"] = None
        #bad code: repeated pattern
        if hasattr(self,"toActivate") and self.toActivate:
            state["toActivate"] = self.toActivate.id
        else:
            state["toActivate"] = None
        return state
    
    '''
    set state as dict
    '''
    def setState(self,state):
        super().setState(state)
        if "sloppy" in state:
            self.sloppy = state["sloppy"]
        if "moveQuest" in state:
            # bad code: repetetive load from id or none pattern
            if state["moveQuest"]:
                '''
                set value
                '''
                def setState(quest):
                    self.moveQuest = quest
                loadingRegistry.callWhenAvailable(state["moveQuest"],setState)
            else:
                self.moveQuest = None
        if "toActivate" in state:
            # bad code: repetetive load from id or none pattern
            if state["toActivate"]:
                '''
                set value
                '''
                def setState(thing):
                    self.toActivate = thing
                loadingRegistry.callWhenAvailable(state["toActivate"],setState)
            else:
                self.toActivate = None

    def activate(self):
        self.startWatching(self.character,self.recalculate)
        super().activate()

'''
quest to refill the goo flask
'''
class RefillDrinkQuest(ActivateQuestMeta):
    '''
    call superconstructor with modified parameters
    '''
    def __init__(self,startCinematics=None,creator=None):
        super().__init__(toActivate=terrain.tutorialVatProcessing.gooDispenser,desiredActive=True,startCinematics=startCinematics,creator=creator)

        # save initial state and register
        self.type = "RefillDrinkQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    check whether the character has a filled goo flask
    '''
    def triggerCompletionCheck(self):
        for item in self.character.inventory:
            if isinstance(item,items.GooFlask):
                if item.uses > 90:
                    self.postHandler()

'''
collect items with some quality
'''
class CollectQuestMeta(MetaQuestSequence):
    '''
    state initialization
    '''
    def __init__(self,toFind="canBurn",startCinematics=None,creator=None):
        super().__init__([],creator=creator)
        self.toFind = toFind
        self.activateQuest = None
        self.waitQuest = WaitQuest(creator=self)
        self.questList = [self.waitQuest]
        for quest in reversed(self.questList):
            self.addQuest(quest)
        self.metaDescription = "fetch Quest Meta"

        # save initial state and register
        self.type = "CollectQuestMeta"
        self.initialState = self.getState()
        loadingRegistry.register(self)
    
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
                self.activeQuest = ActivateQuestMeta(foundItem,creator=self)
                self.addQuest(self.activeQuest)

            # terminate when done
            if self.waitQuest and foundItem:
                quest = self.waitQuest
                self.subQuests.remove(quest)
                quest.postHandler()
                self.waitQuest = None

        super().assignToCharacter(character)

'''
a quest for fetching a quest from a quest dispenser
'''
class GetQuest(MetaQuestSequence):
    '''
    generate quests to move to the quest dispenser and get the quest
    '''
    def __init__(self,questDispenser,assign=False,followUp=None,startCinematics=None,creator=None):
        super().__init__([],creator=creator)
        self.questDispenser = questDispenser
        self.moveQuest = MoveQuestMeta(self.questDispenser.room,self.questDispenser.xPosition,self.questDispenser.yPosition,sloppy=True,creator=self)
        self.getQuest = NaiveGetQuest(questDispenser,assign=assign,creator=self)
        self.questList = [self.moveQuest,self.getQuest]
        for quest in reversed(self.questList):
            self.addQuest(quest)
        self.metaDescription = "get Quest"

        # save initial state and register
        self.type = "GetQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
    def __init__(self,questDispenser,quest,assign=False,followUp=None,startCinematics=None,creator=None):
        super().__init__([],creator=creator)
        self.questDispenser = questDispenser
        self.moveQuest = MoveQuestMeta(self.questDispenser.room,self.questDispenser.xPosition,self.questDispenser.yPosition,sloppy=True,creator=self)
        self.getQuest = NaiveGetReward(quest,creator=self)
        self.questList = [self.moveQuest,self.getQuest]
        self.actualQuest = quest

        for quest in reversed(self.questList):
            self.addQuest(quest)

        self.metaDescription = "get Reward"

        # save initial state and register
        self.type = "GetReward"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    assign to character and spawn a chat option to collect reward
    bad code: spawning the chat should happen in activate
    '''
    def assignToCharacter(self,character):
        '''
        the chat for collecting the reward
        '''
        class RewardChat(interaction.SubMenu):
             id = "RewardChat"
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
    def __init__(self,toKill,followUp=None,startCinematics=None,creator=None,lifetime=None):
        super().__init__([],creator=creator,lifetime=lifetime)
        self.toKill = toKill
        self.moveQuest = MoveQuestMeta(self.toKill.room,self.toKill.xPosition,self.toKill.yPosition,sloppy=False,creator=self)
        self.questList = [self.moveQuest,NaiveMurderQuest(toKill,creator=self)]
        self.lastPos = (self.toKill.room,self.toKill.xPosition,self.toKill.yPosition)
        self.metaDescription = "murder"
        for quest in reversed(self.questList):
            self.addQuest(quest)
        self.startWatching(self.toKill,self.recalculate)

        # save initial state and register
        self.type = "MurderQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    adjust movement to follow target
    '''
    def recalculate(self):
        if self.active:
            pos = (self.toKill.room,self.toKill.xPosition,self.toKill.yPosition)
            if not (pos == self.lastPos) and not self.toKill.dead:
                self.lastPos = pos
                self.moveQuest.deactivate()
                if self.moveQuest in self.subQuests:
                        self.subQuests.remove(self.moveQuest)
                self.moveQuest = MoveQuestMeta(self.toKill.room,self.toKill.xPosition,self.toKill.yPosition,sloppy=True,creator=self)
                self.addQuest(self.moveQuest)
        super().recalculate()

'''
the quest for murering somebody
'''
class KnockOutQuest(MetaQuestSequence):
    '''
    generate quests for moving to and murdering the target
    '''
    def __init__(self,target,followUp=None,startCinematics=None,creator=None,lifetime=None):
        super().__init__([],creator=creator,lifetime=lifetime)
        self.target = target
        self.moveQuest = MoveQuestMeta(self.target.room,self.target.xPosition,self.target.yPosition,sloppy=True,creator=self)
        self.questList = [self.moveQuest,NaiveKnockOutQuest(target,creator=self)]
        self.lastPos = (self.target.room,self.target.xPosition,self.target.yPosition)
        self.metaDescription = "knock out"
        for quest in reversed(self.questList):
            self.addQuest(quest)
        self.startWatching(self.target,self.recalculate)

        # save initial state and register
        self.type = "MurderQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    adjust movement to follow target
    '''
    def recalculate(self):
        if self.active:
            pos = (self.target.room,self.target.xPosition,self.target.yPosition)
            if not (pos == self.lastPos) and not self.target.dead:
                self.lastPos = pos
                self.moveQuest.deactivate()
                if self.moveQuest in self.subQuests:
                        self.subQuests.remove(self.moveQuest)
                self.moveQuest = MoveQuestMeta(self.target.room,self.target.xPosition,self.target.yPosition,sloppy=True,creator=self)
                self.addQuest(self.moveQuest)
        super().recalculate()

'''
the quest for waking somebody
'''
class WakeUpQuest(MetaQuestSequence):
    '''
    generate quests for moving to and the tking up the target
    '''
    def __init__(self,target,followUp=None,startCinematics=None,creator=None,lifetime=None):
        super().__init__([],creator=creator,lifetime=lifetime)
        self.target = target
        self.moveQuest = MoveQuestMeta(self.target.room,self.target.xPosition,self.target.yPosition,sloppy=True,creator=self)
        self.questList = [self.moveQuest,NaiveWakeUpQuest(target,creator=self)]
        self.lastPos = (self.target.room,self.target.xPosition,self.target.yPosition)
        self.metaDescription = "wake up somebody"
        for quest in reversed(self.questList):
            self.addQuest(quest)
        self.startWatching(self.target,self.recalculate)

        # save initial state and register
        self.type = "WakeUpQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    adjust movement to follow target
    '''
    def recalculate(self):
        if self.active:
            pos = (self.target.room,self.target.xPosition,self.target.yPosition)
            if not (pos == self.lastPos):
                self.lastPos = pos
                self.moveQuest.deactivate()
                if self.moveQuest in self.subQuests:
                        self.subQuests.remove(self.moveQuest)
                self.moveQuest = MoveQuestMeta(self.target.room,self.target.xPosition,self.target.yPosition,sloppy=True,creator=self)
                self.addQuest(self.moveQuest)
        super().recalculate()

'''
fill inventory with something
bad code: only fetches fuel
'''
class FillPocketsQuest(MetaQuestSequence):
    '''
    state initialization
    '''
    def __init__(self,followUp=None,startCinematics=None,lifetime=None,creator=None):
        self.waitQuest = WaitQuest(creator=self)
        self.questList = [self.waitQuest]
        self.collectQuest = None
        super().__init__(self.questList,creator=creator)
        self.metaDescription = "fill pockets"

        # save initial state and register
        self.type = "FillPocketsQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    add collect quest till inventory is full
    '''
    def recalculate(self):
        # do nothing on not really active quests
        if not self.active:
            debugMessages.append("triggerCompletionCheck called on inactive "+str(self))
            return 
        if not self.character:
            debugMessages.append("triggerCompletionCheck called without character on "+str(self))
            return

        # remove completed quests
        if self.collectQuest and self.collectQuest.completed:
            self.collectQuest = None

        # add collect quest
        if len(self.character.inventory) < 11 and not self.collectQuest:
            self.collectQuest = CollectQuestMeta(creator=self)
            self.addQuest(self.collectQuest)

        # remove wait quest on first occasion
        if self.waitQuest:
            self.waitQuest.postHandler()
            self.waitQuest = None

        super().recalculate()

'''
quest to leave the room
'''
class LeaveRoomQuest(Quest):
    def __init__(self,room,followUp=None,startCinematics=None,creator=None):
        self.room = room
        self.description = "please leave the room."
        self.dstX = self.room.walkingAccess[0][0]
        self.dstY = self.room.walkingAccess[0][1]
        super().__init__(followUp,startCinematics=startCinematics,creator=creator)

        # save initial state and register
        self.type = "LeaveRoomQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    move to door and step out of the room
    '''
    def solver(self,character):
        if super().solver(character):
            if character.room:
                # close door
                for item in character.room.itemByCoordinates[(character.xPosition,character.yPosition)]:
                    if isinstance(item,items.Door):
                        item.close()

                # add step out of the room
                if character.yPosition == 0:
                    character.path.append((character.xPosition,character.yPosition-1))
                elif character.yPosition == character.room.sizeY-1:
                    character.path.append((character.xPosition,character.yPosition+1))
                elif character.xPosition == 0:
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
        # do nothing on invalid quest
        if not self.active:
            debugMessages.append("triggerCompletionCheck called on inactive "+str(self))
            return 
        if not self.character:
            debugMessages.append("triggerCompletionCheck called without character on "+str(self))
            return

        # trigger followup when done
        if not self.character.room == self.room:
            self.postHandler()

'''
patrol along a cirqular path
bad code: this quest is not used and may be broken
'''
class PatrolQuest(MetaQuestSequence):
    '''
    state initialization
    '''
    def __init__(self,waypoints=[],startCinematics=None,looped=True,lifetime=None,creator=None):
        # bad code: superconstructor doesn't actually process the looped parameter
        super().__init__(quests,startCinematics=startCinematics,looped=looped,creator=creator)

        # add movement between waypoints
        quests = []
        for waypoint in waypoints:
            quest = MoveQuestMeta(waypoint[0],waypoint[1],waypoint[2],creator=self)
            self.addQuest(quest)

        self.lifetime = lifetime

        # save initial state and register
        self.type = "PatrolQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    activate and prepare termination after lifespan
    '''
    def activate(self):
        if self.lifetime:
            '''
            event for wrapping up the quest
            '''
            class endQuestEvent(events.Event):
                '''
                state initialization
                '''
                def __init__(subself,tick,creator=None):
                    super().__init__(tick,creator=creator)
                    subself.tick = tick

                '''
                wrap up the quest
                '''
                def handleEvent(subself):
                    self.postHandler()
            self.character.room.addEvent(endQuestEvent(self.character.room.timeIndex+self.lifetime,creator=self))

        super().activate()

'''
quest to examine the environment
bad pattern: has no solver
'''
class ExamineQuest(Quest):
    '''
    state initialization
    '''
    def __init__(self,startCinematics=None,completionThreshold=5,creator=None):
        self.completionThreshold = completionThreshold
        self.description = "please examine your environment"
        self.examinedItems = []
        super().__init__(startCinematics=startCinematics,creator=creator)
        self.attributesToStore.append("completionThreshold")

        # save initial state and register
        self.type = "ExamineQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    check if some items were observed
    '''
    def triggerCompletionCheck(self):
        if len(self.examinedItems) >= 5:
            self.postHandler()

    '''
    activate and prepare termination after lifespan
    '''
    def activate(self):
        self.character.addListener(self.registerExaminination,"examine")
        super().activate()

    '''
    callback for the character examining things
    increases the counter of observed items
    '''
    def registerExaminination(self,item):
        itemType = type(item)
        if not itemType in self.examinedItems:
            self.examinedItems.append(itemType)
        self.triggerCompletionCheck()

    def setState(self,state):
        super().setState(state)
        if self.active and self.character:
            self.character.addListener(self.registerExaminination,"examine")

##############################################################################
###
## construction quests
#
#############################################################################

'''
move some furniture to the construction room
bad code: name lies somewhat
'''
class FetchFurniture(MetaQuestParralel):
    '''
    create subquest to move each piece of scrap to the metalworkshop
    '''
    def __init__(self,constructionSite,storageRooms,toFetch,followUp=None,startCinematics=None,failTrigger=None,lifetime=None,creator=None):
        super().__init__([],creator=creator)
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
            questList.append(TransportQuest(selectedItem,(constructionSite,dropoffs[counter][1],dropoffs[counter][0]),creator=self))
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
            questList.append(PickupQuestMeta(item,creator=self))
        counter = 0
        for item in toFetch:
            questList.append(DropQuestMeta(item,constructionSite,dropoffs[counter][1],dropoffs[counter][0],creator=self))
            counter += 1
        for item in toFetch:
            self.itemsInStore.append(item)
        """

        for quest in reversed(questList):
            self.addQuest(quest)

        self.metaDescription = "fetch furniture"

        # save initial state and register
        self.type = "FetchFurniture"
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
place furniture within a contruction site
'''
class PlaceFurniture(MetaQuestParralel):
    '''
    generates quests picking up the furniture and dropping it at the right place
    bad code: generating transport quests would me better
    '''
    def __init__(self,constructionSite,itemsInStore,followUp=None,startCinematics=None,failTrigger=None,lifetime=None,creator=None):
        super().__init__([],creator=creator)
        self.questList = []

        # handle each item
        counter = 0
        while counter < len(itemsInStore):
            # get item to place
            if not constructionSite.itemsInBuildOrder:
                break
            toBuild = constructionSite.itemsInBuildOrder.pop()

            # pick up item
            quest = PickupQuestMeta(itemsInStore[counter],creator=self)
            self.questList.append(quest)
            self.startWatching(quest,self.recalculate)

            # drop item
            quest = DropQuestMeta(itemsInStore[counter],constructionSite,toBuild[0][1],toBuild[0][0],creator=self)
            self.questList.append(quest)
            self.startWatching(quest,self.recalculate)
            counter += 1 

        for quest in reversed(self.questList):
            self.addQuest(quest)

        self.metaDescription = "place furniture"

        # save initial state and register
        self.type = "PlaceFurniture"
        self.initialState = self.getState()
        loadingRegistry.register(self)
          
'''
construct a room
'''
class ConstructRoom(MetaQuestParralel):
    '''
    straightforward state initialization
    '''
    def __init__(self,constructionSite,storageRooms,followUp=None,startCinematics=None,failTrigger=None,lifetime=None,creator=None):

        self.questList = []

        self.constructionSite = constructionSite
        self.storageRooms = storageRooms
        self.itemsInStore = []

        self.didFetchQuest = False
        self.didPlaceQuest = False

        super().__init__(self.questList,creator=creator)
        self.metaDescription = "construct room"

        # save initial state and register
        self.type = "ConstructRoom"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    add quests to fetch and place furniture
    '''
    def recalculate(self):
        if not self.questList or self.questList[0].completed:
            if not self.didFetchQuest:
                # fetch some furniture from storage
                self.didFetchQuest = True
                self.didPlaceQuest = False
                self.fetchquest = FetchFurniture(self.constructionSite,self.storageRooms,self.constructionSite.itemsInBuildOrder,creator=self)
                self.addQuest(self.fetchquest)
                self.itemsInStore = self.fetchquest.itemsInStore
            elif not self.didPlaceQuest:
                # place furniture in desired position
                self.didPlaceQuest = True
                self.placeQuest = PlaceFurniture(self.constructionSite,self.itemsInStore,creator=self)
                self.addQuest(self.placeQuest)
                if self.constructionSite.itemsInBuildOrder:
                    self.didFetchQuest = False
        super().recalculate()

    '''
    do not terminate until all fetching and placing was done
    '''
    def triggerCompletionCheck(self):
        if not self.didFetchQuest or not self.didPlaceQuest:
            return
        super().triggerCompletionCheck()

#########################################################################
###
##   logistics related quests
#
#########################################################################

'''
transport an item to a position
'''
class TransportQuest(MetaQuestSequence):
    '''
    generate quest for picking up the item
    '''
    def __init__(self,toTransport,dropOff,followUp=None,startCinematics=None,lifetime=None,creator=None):
        super().__init__([],creator=creator)
        self.toTransport = toTransport
        self.dropOff = dropOff
        self.questList = []
        quest = PickupQuestMeta(self.toTransport,creator=self)
        quest.endTrigger = self.addDrop # add drop quest in follow up
        self.questList.append(quest)
        for quest in reversed(self.questList):
            self.addQuest(quest)
        self.metaDescription = "transport"

        # save initial state and register
        self.type = "TransportQuest"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    drop the item after picking it up
    '''
    def addDrop(self):
        self.addQuest(DropQuestMeta(self.toTransport,self.dropOff[0],self.dropOff[1],self.dropOff[2],creator=self))

'''
move items from permanent storage to accesible storage
'''
class StoreCargo(MetaQuestSequence):
    '''
    generate quests for transporting each item
    '''
    def __init__(self,cargoRoom,storageRoom,followUp=None,startCinematics=None,lifetime=None,creator=None):
        super().__init__([],creator=creator)
        self.questList = []

        # determine how many items should be moved
        amount = len(cargoRoom.storedItems)
        freeSpace = len(storageRoom.storageSpace)
        if freeSpace < amount:
            amount = freeSpace

        # add transport quest for each item
        startIndex = len(storageRoom.storedItems)
        counter = 0
        questList = []
        while counter < amount:
            location = storageRoom.storageSpace[counter]
            questList.append(TransportQuest(cargoRoom.storedItems.pop(),(storageRoom,location[0],location[1]),creator=self))
            counter += 1

        for quest in reversed(questList):
            self.addQuest(quest)

        self.metaDescription = "store cargo"

        # save initial state and register
        self.type = "StoreCargo"
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
move items to accessible storage
'''
class MoveToStorage(MetaQuestSequence):
    '''
    generate the quests to transport each item
    '''
    def __init__(self, items, storageRoom, creator=None):
        super().__init__([],creator=creator)
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
            self.addQuest(TransportQuest(items.pop(),(storageRoom,location[0],location[1]),creator=self))
            counter += 1

        self.metaDescription = "move to storage"

        # save initial state and register
        self.type = "MoveToStorage"
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
handle a delivery
bad pattern: the quest is tailored to a story, it should be more abstracted
bad pattern: the quest can only be solved by delegation
'''
class HandleDelivery(MetaQuestSequence):
    '''
    state initialization
    '''
    def __init__(self, cargoRooms=[],storageRooms=[],creator=None):
        self.cargoRooms = cargoRooms
        self.storageRooms = storageRooms
        self.questList = []
        super().__init__(self.questList,creator=creator)
        self.addNewStorageRoomQuest()
        self.metaDescription = "ensure the cargo is moved to storage"

        # save initial state and register
        self.type = "HandleDelivery"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    def activate(self):
        super().activate()
        if self.character:
            for sub in self.character.subordinates:
                sub.addListener(self.rescueSub,"fallen unconcious")

    def rescueSub(self,character):
        self.addQuest(WakeUpQuest(character,creator=self),addFront=True)
       
    '''
    wait the cargo to be moved to storage
    '''
    def waitForQuestCompletion(self):
        quest = WaitForQuestCompletion(self.quest,creator=self)
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
        self.quest = StoreCargo(room,self.storageRooms.pop(),creator=self)
        quest = NaiveDelegateQuest(self.quest,creator=self)
        quest.endTrigger = self.waitForQuestCompletion
        self.addQuest(quest)

############################################################
###
##  furnace specific quests
#
############################################################

'''
fire a list of furnaces an keep them fired
'''
class KeepFurnacesFiredMeta(MetaQuestParralel):
    '''
    add a quest to keep each furnace fired
    '''
    def __init__(self,furnaces,followUp=None,startCinematics=None,failTrigger=None,lifetime=None,creator=None):
        questList = []
        for furnace in furnaces:
            questList.append(KeepFurnaceFiredMeta(furnace))
        super().__init__(questList,creator=creator)
        self.metaDescription = "KeepFurnacesFiredMeta"

        # save initial state and register
        self.type = "KeepFurnacesFiredMeta"
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
fire a furnace an keep it fired
'''
class KeepFurnaceFiredMeta(MetaQuestSequence):
    '''
    basic state initialization
    '''
    def __init__(self,furnace,followUp=None,startCinematics=None,failTrigger=None,lifetime=None,creator=None):
        self.questList = []
        self.fireFurnaceQuest = None
        self.waitQuest = None
        self.furnace = furnace
        super().__init__(self.questList,lifetime=lifetime,creator=creator)
        self.metaDescription = "KeepFurnaceFiredMeta"

        # listen to furnace
        self.startWatching(self.furnace,self.recalculate)

        # save initial state and register
        self.type = "KeepFurnaceFiredMeta"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    add sub quests
    '''
    def recalculate(self):
        if not self.character:
            return

        # add fireing the furnace if needed
        if self.fireFurnaceQuest and self.fireFurnaceQuest.completed:
            self.fireFurnaceQuest = None
        if not self.fireFurnaceQuest and not self.furnace.activated:
            self.fireFurnaceQuest = FireFurnaceMeta(self.furnace,creator=self)
            self.addQuest(self.fireFurnaceQuest)
            self.unpause()

        # add waitquest if needed
        if self.waitQuest and self.waitQuest.completed:
            self.waitQuest = None
        if not self.waitQuest and not self.fireFurnaceQuest:
            if self.furnace.activated:
                self.waitQuest = WaitForDeactivationQuest(self.furnace,creator=self)
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
    def __init__(self,furnace,followUp=None,startCinematics=None,failTrigger=None,lifetime=None,creator=None):
        self.activateQuest = None
        self.collectQuest = None
        self.questList = []
        self.furnace = furnace
        super().__init__(self.questList,creator=creator)
        self.metaDescription = "FireFurnaceMeta"+str(self)

        # save initial state and register
        self.type = "FireFurnaceMeta"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    collect coal and fire furnace
    '''
    def recalculate(self):
        # smooth over impossible state
        if not self.active:
            debugMessages.append("triggerCompletionCheck called on inactive "+str(self))
            return
        if not self.character:
            debugMessages.append("triggerCompletionCheck called without character on "+str(self))
            return

        # add wuest th collect fuel if needed
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
                self.collectQuest = CollectQuestMeta(creator=self)
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
            self.activateQuest = ActivateQuestMeta(self.furnace,creator=self)
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

##############################################################################
###
## actual tasks
#
#############################################################################

'''
basically janitor duty
'''
class HopperDuty(MetaQuestSequence):
    '''
    straightforward state initialization
    '''
    def __init__(self,waitingRoom,startCinematics=None,looped=True,lifetime=None,creator=None):
        super().__init__([],startCinematics=startCinematics,creator=creator)
        self.getQuest = GetQuest(waitingRoom.secondOfficer,assign=False,creator=self)
        self.getQuest.endTrigger = self.setQuest
        self.addQuest(self.getQuest)
        self.metaDescription = "hopper duty"
        self.recalculate()
        self.actualQuest = None
        self.rewardQuest = None
        self.waitingRoom = waitingRoom

        # save initial state and register
        self.type = "HopperDuty"
        self.initialState = self.getState()
        loadingRegistry.register(self)

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
                self.rewardQuest = GetReward(self.waitingRoom.secondOfficer,self.actualQuest,creator=self)
                self.actualQuest = None
                self.addQuest(self.rewardQuest,addFront=False)

            # remove completed quest
            if self.rewardQuest and self.rewardQuest.completed:
                self.rewardQuest = None

            # add quest to get a new quest
            if not self.getQuest and not self.actualQuest and not self.rewardQuest:
                self.getQuest = GetQuest(self.waitingRoom.secondOfficer,assign=False,creator=self)
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
            self.addQuest(WaitQuest(lifetime=10,creator=self),addFront=False)
    
'''
clear the rubble from the mech
bad pattern: there is no way to determine
'''
class ClearRubble(MetaQuestParralel):
    '''
    create subquest to move each piece of scrap to the metalworkshop
    '''
    def __init__(self,followUp=None,startCinematics=None,failTrigger=None,lifetime=None,creator=None):
        super().__init__([],creator=creator)
        questList = []
        for item in terrain.itemsOnFloor:
            if isinstance(item,items.Scrap):
                self.addQuest(TransportQuest(item,(terrain.metalWorkshop,7,1),creator=self))
        self.metaDescription = "clear rubble"

        # save initial state and register
        self.type = "ClearRubble"
        self.initialState = self.getState()
        loadingRegistry.register(self)

'''
dummy quest for doing the room duty
'''
class RoomDuty(MetaQuestParralel):
    '''
    state initialization
    '''
    def __init__(self, cargoRooms=[],storageRooms=[],creator=None):
        self.questList = []
        super().__init__(self.questList,creator=creator)
        self.metaDescription = "room duty"

        # save initial state and register
        self.type = "RoomDuty"
        self.initialState = self.getState()
        loadingRegistry.register(self)

    '''
    never complete
    '''
    def triggerCompletionCheck(self):
        return 

'''
dummy quest for following somebodies orders
'''
class Serve(MetaQuestParralel):
    '''
    state initialization
    '''
    def __init__(self, superior=None, creator=None):
        self.questList = []
        self.superior = superior
        super().__init__(self.questList,creator=creator)
        self.metaDescription = "serve"

        # save initial state and register
        self.type = "Serve"
        self.initialState = self.getState()
        loadingRegistry.register(self)

        if superior:
            self.metaDescription += " "+superior.name

    '''
    get difference in state since creation
    '''
    def getDiffState(self):
        state = super().getDiffState()
        if not self.metaDescription == state["superior"]:
            state["superior"] = self.metaDescription
        return state

    '''
    get state as dict
    '''
    def getState(self):
        state = super().getState()
        if self.superior:
            state["superior"] = self.superior.id
        else:
            state["superior"] = None
        return state
    
    '''
    set state as dict
    '''
    def setState(self,state):
        super().setState(state)
        if "superior" in state:
            # bad code: repetetive load from id or none pattern
            if state["superior"]:
                '''
                set value
                '''
                def setSuperior(superior):
                    self.superior = superior
                loadingRegistry.callWhenAvailable(state["superior"],setSuperior)
                pass
            else:
                self.superior = None

    '''
    never complete
    '''
    def triggerCompletionCheck(self):
        return 

# map strings to Classes
questMap = {
              "Quest":Quest,
              "MetaQuestSequence":MetaQuestSequence,
              "MetaQuestParralel":MetaQuestParralel,
              "NaiveMoveQuest":NaiveMoveQuest,
              "NaiveEnterRoomQuest":NaiveEnterRoomQuest,
              "NaivePickupQuest":NaivePickupQuest,
              "NaiveGetQuest":NaiveGetQuest,
              "NaiveGetReward":NaiveGetReward,
              "NaiveMurderQuest":NaiveMurderQuest,
              "NaiveActivateQuest":NaiveActivateQuest,
              "NaiveDropQuest":NaiveDropQuest,
              "NaiveDelegateQuest":NaiveDelegateQuest,
              "WaitQuest":WaitQuest,
              "WaitForDeactivationQuest":WaitForDeactivationQuest,
              "WaitForQuestCompletion":WaitForQuestCompletion,
              "DrinkQuest":DrinkQuest,
              "SurviveQuest":SurviveQuest,
              "EnterRoomQuestMeta":EnterRoomQuestMeta,
              "MoveQuestMeta":MoveQuestMeta,
              "DropQuestMeta":DropQuestMeta,
              "PickupQuestMeta":PickupQuestMeta,
              "ActivateQuestMeta":ActivateQuestMeta,
              "RefillDrinkQuest":RefillDrinkQuest,
              "CollectQuestMeta":CollectQuestMeta,
              "GetQuest":GetQuest,
              "GetReward":GetReward,
              "MurderQuest":MurderQuest,
              "FillPocketsQuest":FillPocketsQuest,
              "LeaveRoomQuest":LeaveRoomQuest,
              "PatrolQuest":PatrolQuest,
              "ExamineQuest":ExamineQuest,
              "FetchFurniture":FetchFurniture,
              "PlaceFurniture":PlaceFurniture,
              "ConstructRoom":ConstructRoom,
              "TransportQuest":TransportQuest,
              "StoreCargo":StoreCargo,
              "MoveToStorage":MoveToStorage,
              "HandleDelivery":HandleDelivery,
              "KeepFurnacesFiredMeta":KeepFurnacesFiredMeta,
              "KeepFurnaceFiredMeta":KeepFurnaceFiredMeta,
              "FireFurnaceMeta":FireFurnaceMeta,
              "HopperDuty":HopperDuty,
              "ClearRubble":ClearRubble,
              "RoomDuty":RoomDuty,
              "Serve":Serve,
}

'''
get quest instance from state dict
'''
def getQuestFromState(state):
    quest = questMap[state["type"]](creator=void)
    quest.setState(state)
    loadingRegistry.register(quest)
    return quest
