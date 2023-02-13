"""
quests and quest related code

"""

# import basic libs
import json
import random
import time

# import basic internal libs
import src.items
import src.saveing
import src.chats
import src.events
import src.interaction
import src.cinematics
import src.gamestate

# HACK: common variables with modules
mainChar = None


"""
the base class for all quests
"""
class Quest(src.saveing.Saveable):
    type = "Quest"
    hasParams = False

    def __init__(
        self,
        followUp=None,
        startCinematics=None,
        lifetime=None,
        creator=None,
        failTrigger=None,
    ):

        super().__init__()

        # set basic attributes
        self.followUp = followUp  # deprecate?
        self.character = (
            None  # should be more general like owner as preparation for room quests
        )
        self.listeners = {"default": []}
        self.active = False  # active as in started
        self.completed = False
        self.startCinematics = startCinematics  # deprecate?
        self.endCinematics = None  # deprecate?
        self.startTrigger = None  # deprecate?
        self.endTrigger = None  # deprecate?
        self.failTrigger = failTrigger  # deprecate?
        self.paused = False
        self.reputationReward = 0
        self.watched = []
        self.randomSeed = None
        self.autoSolve = False
        self.selfAssigned = False

        # set up saving
        # bad code: extend would be better
        self.attributesToStore.append("type")
        self.attributesToStore.append("active")
        self.attributesToStore.append("completed")
        self.attributesToStore.append("reputationReward")
        self.attributesToStore.append("lifetime")
        self.attributesToStore.append("description")
        self.attributesToStore.extend(["dstX", "dstY"])
        self.callbacksToStore.append("endTrigger")
        self.objectsToStore.append("character")
        self.objectsToStore.append("target")
        self.objectsToStore.append("lifetimeEvent")

        self.lifetime = lifetime
        self.lifetimeEvent = None
        self.startTick = src.gamestate.gamestate.tick

        # set id
        self.id = str(random.random())+str(time.time())
        self.reroll()

        self.shortCode = "?"

    def generateTextDescription(self):
        return "missing description for "+str(self)

    def isPaused(self):
        return False

    def getQuestMarkersSmall(self,character,renderForTile=False):
        return []

    def getQuestMarkersTile(self,character):
        return []

    def getRequiredParameters(self):
        return []
    
    def getOptionalParameters(self):
        return [{"name":"lifetime","type":"int","default":None}]

    def setParameters(self,parameters):
        if "lifetime" in parameters:
            self.lifetime = parameters["lifetime"]
    
    def reroll(self):
        self.randomSeed = random.random()

    def getActiveQuest(self):
        return self

    def getActiveQuests(self):
        return [self]

    def generateSubquests(self,character=None):
        pass

    def startWatching(self, target, callback, tag=""):
        """
        register callback to be notified if an event occours

        Parameters:
            target: the thing that is watching
            callback: the callback to call
            tag: the type of event to listen for
        """

        if tag == "":
            1/0

        target.addListener(callback, tag)
        self.watched.append((target, callback,tag))

    def stopWatching(self, target, callback, tag=""):
        """
        deregister callback from beeing notified if an event occours

        Parameters:
            target: the thing that is watching
            callback: the callback to call
            tag: the type of event to listen for
        """

        if tag == "":
            1/0

        try:
            target.delListener(callback, tag)
        except:
            pass
        try:
            self.watched.remove((target, callback, tag))
        except:
            pass

    """
    unregister all callback
    """

    def stopWatchingAll(self):
        for listenItem in self.watched[:]:
            self.stopWatching(listenItem[0], listenItem[1], listenItem[2])

    # bad pattern: is repeated in items etc
    def addListener(self, listenFunction, tag="default"):
        """
        register a callback function for notifications
        if something wants to wait for the character to die it should register as listener

        Parameters:
            listenFunction: the function that should be called if the listener is triggered
            tag: a tag determining what kind of event triggers the listen function. For example "died"
        """
        # create container if container doesn't exist
        # bad performance: string comparison, should use enums. Is this slow in python?
        if tag not in self.listeners:
            self.listeners[tag] = []

        # added listener function
        if listenFunction not in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    # bad pattern: is repeated in items etc
    def delListener(self, listenFunction, tag="default"):
        """
        deregister a callback function for notifications

        Parameters:
            listenFunction: the function that would be called if the listener is triggered
            tag: a tag determining what kind of event triggers the listen function. For example "died"
        """

        if not tag in self.listeners:
            return

        # remove listener
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        # clear up dict
        # bad performance: probably better to not clean up and recreate
        if not self.listeners[tag]:
            del self.listeners[tag]

    # bad code: probably misnamed
    def changed(self, tag="default", info=None):
        """
        call callbacks functions that did register for listening to events

        Parameters:
            tag: the tag determining what kind of event triggers the listen function. For example "died"
            info: additional information
        """

        # do nothing if nobody listens
        if tag not in self.listeners:
            return

        # call each listener
        for listenFunction in self.listeners[tag]:
            if info is None:
                listenFunction()
            else:
                try:
                    listenFunction(info)
                except:
                    2/0
                listenFunction(info)

    """
    check whether the quest is solved or not (and trigger teardown if quest is solved)
    """

    def triggerCompletionCheck(self,character=None):

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "triggerCompletionCheck called on inactive quest: " + str(self)
            )
            return

        pass

    """
    do one action to solve the quest, is intended to be overwritten heavily. returns None if there can't be done anything
    bad code: should be rewritten so it returns an actual list of steps
    """

    def solver(self, character):
        if self.paused:
            return True
        else:
            return character.walkPath()

    """
    pause the quest
    """

    def pause(self):
        self.paused = True

    """
    unpause the quest
    """

    def unpause(self):
        self.paused = False

    """
    handle a failure to resolve te quest
    """

    def fail(self,reason=None):
        if reason and self.character:
            self.character.addMessage("failed quest because of %s"%(reason,))
        if self.failTrigger:
            self.failTrigger()
        if self.reputationReward:
            self.reputationReward *= -2
        self.postHandler()

    def handleTimeOut(self):
        self.fail()

    def render(self,depth=0,cursor=None):
        description = self.description
        if self.active:
            description = "> "+description
        elif self.completed:
            description = "X "+description
        else:
            description = "x "+description

        if cursor == None:
            color = "#fff"
        elif cursor == []:
            color = "#0f0"
        else:
            color = "#0b0"
        return [[(src.interaction.urwid.AttrSpec(color, "default"), description)]]

    """
    get the quests description
    bad code: colored and asList are somewhat out of place
    """
    def getDescription(self, asList=False, colored=False, active=False):
        colored = False

        if not hasattr(self,"description"):
            return "broken"

        if asList:
            if colored:
                import urwid

                if active:
                    color = "#0f0"
                else:
                    color = "#090"
                description = self.description
                if self.lifetimeEvent:
                    description += (
                        " ("
                        + str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)
                        + " / "
                        + str(self.lifetime)
                        + ")"
                    )
                return [[(urwid.AttrSpec(color, "default"), description), "\n"]]
            else:
                description = self.description
                if self.lifetimeEvent:
                    description += (
                        " ("
                        + str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)
                        + " / "
                        + str(self.lifetime)
                        + ")"
                    )
                return [[description, "\n"]]
        else:
            description = self.description
            if self.lifetimeEvent:
                description += (
                    " ("
                    + str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)
                    + " / "
                    + str(self.lifetime)
                    + ")")
            return description

    """
    tear the quest down
    """

    def postHandler(self):
        # stop listening
        self.stopWatchingAll()

        # smooth over impossible state
        if not self.active:
            return

        # smooth over impossible state
        if not self.character:
            # trigger follow up functions
            if self.endTrigger:
                self.callIndirect(self.endTrigger)
            if self.endCinematics:
                src.cinematics.showCinematic(self.endCinematics)
                src.interaction.loop.set_alarm_in(
                    0.0, src.interaction.callShow_or_exit, "."
                )

            # deactivate
            self.deactivate()

            return

        # smooth over impossible state
        if self.completed:
            return

            if self in self.character.quests:
                # remove quest
                startNext = False
                if self.character.quests[0] == self:
                    startNext = True
                self.character.quests.remove(self)

                # start next quest
                if startNext:
                    if self.followUp:
                        self.character.assignQuest(self.followUp, active=True)
                    else:
                        self.character.startNextQuest()
            return

        # deactivate
        self.deactivate()

        # flag self as completed
        if not self.completed:
            self.changed("completed",(self,))
        self.completed = True

        # add quest type to quests done
        if self.type not in self.character.questsDone:
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
            src.cinematics.showCinematic(self.endCinematics)
            src.interaction.loop.set_alarm_in(
                0.0, src.interaction.callShow_or_exit, "."
            )

        # start next quest
        if self.followUp:
            self.character.assignQuest(self.followUp, active=True)
        else:
            self.character.startNextQuest()

    """
    assign the quest to a character
    bad code: this would be a constructor param, but this may be used for reassigning quests
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        # extend characters solvers with this quest
        if self.type not in character.solvers:
            character.solvers.append(self.type)

        # set character
        self.character = character
        self.recalculate()

        # set path
        if self.active:
            self.character.setPathToQuest(self)

    """
    recalculate the internal state of the quest
    this is usually called as a listener function
    also used when the player moves leave the path
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.active:
            #src.interaction.debugMessages.append(
            #    "recalculate called on inactive quest: " + str(self)
            #)
            return

        self.triggerCompletionCheck()

    """
    fail on timeout
    """

    def timeOut(self):
        self.fail()

    """
    switch from just existing to active
    """

    def activate(self):
        # flag self as active
        self.active = True

        # trigger startup actions
        # bad code: these should be a unified way to to this. probably an event
        if self.startTrigger:
            self.startTrigger()
        if self.startCinematics:
            src.cinematics.showCinematic(self.startCinematics)
            src.interaction.loop.set_alarm_in(
                0.0, src.interaction.callShow_or_exit, "."
            )

        # add automatic termination
        if self.lifetime and not self.lifetimeEvent:
            if self.startTick + self.lifetime < src.gamestate.gamestate.tick:
                self.timeOut()
                return
            self.lifetimeEvent = src.events.EndQuestEvent(
                self.startTick + self.lifetime,
                callback={"container": self, "method": "timeOut"},
            )
            self.character.addEvent(self.lifetimeEvent)

        # recalculate and notify listeners
        self.recalculate()
        self.changed()

    """
    switch from active to just existing
    """

    def deactivate(self):
        self.active = False
        if (
            self.lifetimeEvent
            and self.character
            and self.lifetimeEvent in self.character.events
        ):
            self.character.removeEvent(self.lifetimeEvent)
            self.lifetimeEvent = None
        self.changed()

    """
    get the current state
    """

    def getState(self):
        state = super().getState()
        if self.endTrigger:
            if not isinstance(self.endTrigger, dict):
                state["endTrigger"] = str(self.endTrigger)
            else:
                state["endTrigger"] = {
                    "container": self.endTrigger["container"].id,
                    "method": self.endTrigger["method"],
                }
        return state

    def getSolvingCommandString(self,character,dryRun=True):
        return None

class MetaQuestSequence(Quest):
    """
    state initialization
    bad code: quest parameter does not work anymore and should be removed
    """

    def __init__(
        self,
        quests=None,
        followUp=None,
        failTrigger=None,
        startCinematics=None,
        lifetime=None,
        creator=None,
    ):
        if not quests:
            quests = []
        # set state
        self.metaDescription = "meta"
        self.subQuestsOrig = quests.copy()
        self.subQuests = quests
        super().__init__(
            startCinematics=startCinematics,
            lifetime=lifetime,
            creator=creator,
            followUp=followUp,
            failTrigger=failTrigger,
        )

        # listen to subquests
        if len(self.subQuests):
            self.startWatching(self.subQuests[0], self.recalculate)

        # set meta information for saving
        self.attributesToStore.append("metaDescription")
        while "dstX" in self.attributesToStore:
            self.attributesToStore.remove("dstX")
        while "dstY" in self.attributesToStore:
            self.attributesToStore.remove("dstY")

        # save state and register
        self.type = "MetaQuestSequence"

    def render(self,depth=0,cursor=None):
        description = [self.description]

        if cursor == None:
            color = "#fff"
        elif cursor == []:
            color = "#0f0"
        else:
            color = "#070"

        if self.active:
            description = ["> "]+description
        elif self.completed:
            description = ["X "]+description
        elif self.isPaused():
            description = ["# "]+description
        else:
            description = ["x "]+description
        description = [[(src.interaction.urwid.AttrSpec(color, "default"), description)]]

        counter = 0
        for quest in self.subQuests:
            if cursor and counter == cursor[0]:
                newCursor = cursor[1:]
            else:
                newCursor = None

            description.append(["\n"]+["     "*(depth+1)]+quest.render(depth=depth+1,cursor=newCursor))
            counter += 1
        return description

    def isPaused(self):
        if not self.subQuests:
            return False
        return self.subQuests[0].isPaused()

    def getActiveQuest(self):
        if self.subQuests:
            return self.subQuests[0].getActiveQuest()
        else:
            return self

    def getActiveQuests(self):
        if self.subQuests:
            return self.subQuests[0].getActiveQuests()+[self]
        else:
            return [self]

    def clearSubQuests(self):
        for quest in self.subQuests:
            quest.fail()
        self.subQuests = []

    """
    get state as dict
    """

    def getState(self):
        state = super().getState()

        # store sub quests
        state["subQuests"] = {}
        state["subQuests"]["ids"] = []
        state["subQuests"]["states"] = {}
        for quest in self.subQuests:
            if quest:
                state["subQuests"]["ids"].append(quest.id)
                state["subQuests"]["states"][quest.id] = quest.getState()

        return state

    """
    set state as dict
    """

    def setState(self, state):
        super().setState(state)

        # load sub quests
        if "subQuests" in state:
            # load static quest list
            if "ids" in state["subQuests"]:
                self.subQuests = []
                for thingId in state["subQuests"]["ids"]:
                    # create and add quest
                    thingState = state["subQuests"]["states"][thingId]
                    thing = getQuestFromState(thingState)
                    self.subQuests.append(thing)
                    self.startWatching(self.subQuests[-1], self.recalculate)

        # listen to subquests
        if len(self.subQuests):
            self.startWatching(self.subQuests[0], self.recalculate)

    """
    get target position from first subquest
    bad code: should use a position object
    """

    @property
    def dstX(self):
        try:
            return self.subQuests[0].dstX
        except:
            return self.character.xPosition

    """
    get target position from first subquest
    bad code: should use a position object
    """

    @property
    def dstY(self):
        try:
            return self.subQuests[0].dstY
        except:
            return self.character.yPosition

    """
    render description as simple string
    bad code: missing timout information
    """

    @property
    def description(self):
        return self.metaDescription

    """
    @property
    def description(self,sane=False):
        # add name of the actual quest
        out = self.metaDescription
        if self.lifetimeEvent:
            out += (
                " (%s/%s)"%(str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick),str(self.lifetime))
            )
        out += ":\n"

        for quest in self.subQuests:
            # add quests
            if quest.active:
                out += "    > " + "\n      ".join(quest.description.split("\n")) + "\n"
            else:
                if quest.completed:
                    out += "    x " + "\n      ".join(quest.description.split("\n")) + "\n"
                else:
                    out += "    o " + "\n      ".join(quest.description.split("\n")) + "\n"
        return out

    get a more detailed description 
    bad code: asList and colored are out of place
    bad code: the asList and colored mixup leads to ugly code
    """

    '''
    def getDescription(self, asList=False, colored=False, active=False):
        # add name of the actual quest
        if asList:
            if colored:
                urwid = src.interaction.urwid

                if active:
                    color = "#0f0"
                else:
                    color = "#090"
                out = [
                    [
                        [
                            (
                                urwid.AttrSpec(color, "default"),
                                self.metaDescription + ":",
                            )
                        ],
                    ]
                ]
            else:
                out = [[self.metaDescription + ":"]]
        else:
            out = self.metaDescription + ":"

        # add remaining time
        if self.lifetimeEvent:
            out += " (%s/%s)"%(self.lifetimeEvent.tick - src.gamestate.gamestate.tick, self.lifetime)

        if asList:
            out.append("\n")
        else:
            out += ":\n"

        # add quests
        for quest in self.subQuests:
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
                        deko = (urwid.AttrSpec(color, "default"), "  > ")
                    else:
                        deko = "  > "
                else:
                    deko = "  x "
                for item in quest.getDescription(
                    asList=asList, colored=colored, active=active
                ):
                    if not first:
                        deko = "    "
                    out.append([deko, item])
                    first = False
                    colored = False
            else:
                if quest.active:
                    out += (
                        "    > "
                        + "\n      ".join(quest.getDescription().split("\n"))
                        + "\n"
                    )
                else:
                    out += (
                        "    x "
                        + "\n      ".join(quest.getDescription().split("\n"))
                        + "\n"
                    )
        return out
    '''

    """
    assign self and first subquest to character
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        for quest in self.subQuests:
            quest.assignToCharacter(character)
        super().assignToCharacter(character)

    """
    check if there are quests left
    """

    def triggerCompletionCheck2(self,extraInfo):
        self.stopWatching(extraInfo[0],self.triggerCompletionCheck2,"completed")
        self.triggerCompletionCheck()

        if extraInfo[0] in self.subQuests:
            self.subQuests.remove(extraInfo[0])

    def triggerCompletionCheck(self,character=None):

        # smooth over impossible state
        if not self.active:
            return

        self.generateSubquests()

        # remove completed quests
        if self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

        # wrap up when out of subquests
        if not len(self.subQuests):
            self.postHandler()

    """
    ensure first quest is active
    """

    def recalculate(self):
        return

        # smooth over impossible state
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
                if not self.character.dead:
                    self.character.recalculatePath()
        super().recalculate()

        # check for completion
        self.triggerCompletionCheck()

    """
    add a quest
    """

    def addQuest(self, quest, addFront=True, noActivate=False, noAssign=False):
        if not noActivate and not quest.active and (addFront or not self.subQuests):
            quest.activate()
        if not noAssign and not quest.character and self.character:
            quest.assignToCharacter(self.character)

        # add quest
        if addFront:
            self.subQuests.insert(0, quest)
        else:
            self.subQuests.append(quest)

        # reset characters path
        if self.character:
            self.subQuests[0].assignToCharacter(self.character)
            self.character.recalculatePath()

        # listen to subquest
        self.startWatching(quest, self.triggerCompletionCheck2, "completed")

        # deactivate last active quest
        if addFront:
            if len(self.subQuests) > 1:
                self.subQuests[1].deactivate()

    """
    activate self and first subquest
    """

    def activate(self):
        if len(self.subQuests):
            if not self.subQuests[0].active:
                self.subQuests[0].activate()
        super().activate()

    """
    forward solver from first subquest
    """

    def solver(self, character):
        # remove completed quests
        if self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

        if self.triggerCompletionCheck(character):
            return

        if len(self.subQuests):
            subQuest = self.subQuests[0]
            if not subQuest.active:
                subQuest.activate()
                return
            if not (subQuest.character == character):
                subQuest.assignToCharacter(character)
                return
            self.subQuests[0].solver(character)
        else:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)

    """
    deactivate self and first subquest
    """

    def deactivate(self):
        if len(self.subQuests):
            if self.subQuests[0].active:
                self.subQuests[0].deactivate()
        super().deactivate()

    def getSolvingCommandString(self,character,dryRun=True):
        if self.subQuests:
            commandString = self.subQuests[0].getSolvingCommandString(character,dryRun=dryRun)
            if commandString:
                return commandString
        return super().getSolvingCommandString(character)















class delDestroyRoom(MetaQuestSequence):
    def __init__(self, description="destroyRoom", creator=None, command=None, lifetime=None, targetPosition=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "DestroyRoom"
        self.shortCode = "D"

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append((self.targetPosition,"target"))
        return result

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain = character.container

        if not terrain.getRoomByPosition(self.targetPosition):
            self.postHandler()
            return
        return

    def solver(self, character):
        if isinstance(character.container,src.rooms.Room):
            character.container.damage()
            character.die()
            return

        charpos = (character.xPosition//15,character.yPosition//15)

        roomsOnTile = character.container.getRoomByPosition(charpos)
        if roomsOnTile:
            roomsOnTile[0].damage()
            character.die()
            return

        if not self.subQuests:

            direction = None 
            if charpos[0] > self.targetPosition[0]:
                direction = (-1,0)
                command = "a"
            if charpos[0] < self.targetPosition[0]:
                direction = (+1,0)
                command = "d"
            if charpos[1] > self.targetPosition[1]:
                direction = (0,-1)
                command = "w"
            if charpos[1] < self.targetPosition[1]:
                direction = (0,+1)
                command = "s"
            
            if direction:
                self.addQuest(src.quests.questMap["RunCommand"](command=13*command))
            return
        return super().solver(character)

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
        return super().setParameters(parameters)

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

class delControlBase(MetaQuestSequence):
    def __init__(self, description="control base", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "ControlBase"
        self.shortCode = "C"

    def triggerCompletionCheck(self,character=None):
        if not character:
            return 
        return

    def solver(self, character):
        return super().solver(character)

class delDefendBase(MetaQuestSequence):
    def __init__(self, description="defend base", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "DefendBase"
        self.shortCode = "D"

    def triggerCompletionCheck(self,character=None):
        if not character:
            return 
        return
        super().triggerCompletionCheck()
    
    def generateSubquests(self,character):
        self.subQuests.append(CleanTraps())

    def solver(self, character):
        if not self.subQuests:
            self.generateSubquests(character)
            return
        self.triggerCompletionCheck(character)
        return super().solver(character)

class delBreakSiege(MetaQuestSequence):
    def __init__(self, description="break siege", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "BreakSiege"
        self.shortCode = "B"

    def triggerCompletionCheck(self,character=None):
        if not character:
            return 

        return

    def solver(self, character):
        return super().solver(character)

class delAssignStaff(MetaQuestSequence):
    def __init__(self, description="assign staff", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "AssignStaff"
        self.shortCode = "A"

        self.generatedCode = False

    def triggerCompletionCheck(self,character=None):
        if not self.generatedCode:
            return

        if self.subQuests:
            return

        super().triggerCompletionCheck()

    def solver(self, character):
        if not self.subQuests:
            if isinstance(character.container,src.rooms.Room):
                charPos = character.container.getPosition()
            else:
                charPos = character.getBigPosition()

            if not charPos == (7,7,0):
                subQuest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0))
                self.addQuest(subQuest)
                subQuest.activate()
                subQuest.assignToCharacter(character)
                return

            charPos = character.getPosition()
            if not charPos == (1,2,0):
                subQuest = src.quests.questMap["GoToPosition"](targetPosition=(1,2,0))
                self.addQuest(subQuest)
                subQuest.activate()
                subQuest.assignToCharacter(character)
                return

            if not self.generatedCode:
                subQuest = src.quests.questMap["RunCommand"](command=list("Jw.sjdjdjaasddddjdjaaaaa")+["esc"])
                self.addQuest(subQuest)
                subQuest.activate()
                subQuest.assignToCharacter(character)
                self.generatedCode = True
                return

        return super().solver(character)

class delDestroyRooms(MetaQuestSequence):
    def __init__(self, description="destroyRooms", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "DestroyRooms"
        self.shortCode = "D"

    def triggerCompletionCheck(self,character=None):
        if not character:
            return 

        if isinstance(character.container,src.rooms.Room):
            return

        if not character.container.rooms:
            self.postHandler()
            return

        return

    def solver(self, character):

        if not self.subQuests:
            if isinstance(character.container,src.rooms.Room):
                terrain = character.container.container
            else:
                terrain = character.container

            roomCandidates = []
            for room in terrain.rooms:
                if room.bio:
                    continue
                roomCandidates.append(room)

            targetRoom = random.choice(roomCandidates)
            character.addMessage("should attack room")
            character.addMessage(targetRoom.getPosition())

            self.addQuest(src.quests.DestroyRoom(targetPosition=targetRoom.getPosition()))

            return
        return super().solver(character)

class delStandAttention(MetaQuestSequence):

    """
    state initialization
    """

    def __init__(self, description="wait for orders", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.addedSubQuests = False

        # save initial state and register
        self.type = "StandAttention"

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        super().assignToCharacter(character)


    def triggerCompletionCheck(self,character=None):
        return

    def generateSubquests(self,character):
        if not self.addedSubQuests:
            quest = src.quests.questMap["GoToPosition"]()
            quest.assignToCharacter(character)
            if not character.registers.get("ATTNPOSx") or not character.registers.get("ATTNPOSy"):
                return
            targetpos = (character.registers["ATTNPOSx"],character.registers["ATTNPOSy"],0)
            quest.setParameters({"targetPosition":targetpos})
            self.addQuest(quest)

            quest = src.quests.questMap["GoToPosition"]()
            quest.assignToCharacter(character)
            quest.setParameters({"targetPosition":(6,6,0)})
            self.addQuest(quest)


            quest = src.quests.questMap["GoHome"]()
            quest.assignToCharacter(character)
            quest.activate()
            quest.generateSubquests(character)
            self.addQuest(quest)

    def getSolvingCommandString(self, character, dryRun=True):
        if self.lifetimeEvent:
            return "10."
            return str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)+"."
        else:
            return "10."

    def solver(self, character):
        if self.subQuests:
            super().solver(character)
        else:
            commandString = self.getSolvingCommandString(character,dryRun=dryRun)
            self.randomSeed = random.random()
            if commandString:
                character.runCommandString(commandString)
                return False
            else:
                return True

class delGatherItems(Quest):

    """
    state initialization
    """

    def __init__(self, description="gather items", creator=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.description = description

        # save initial state and register
        self.type = "GatherItems"

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if len(character.inventory) > 9:
            self.postHandler()
            return True

        return

    def timeOut(self):
        self.postHandler()

    def solver(self, character):
        character.runCommandString(".30.")
        return False

class TeleportToTerrain(MetaQuestSequence):
    def __init__(self, description="teleport to terrain", creator=None, targetPosition=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

    def triggerCompletionCheck(self,character=None):
        if not character:
            return
        if not character.container:
            return
        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain = character.container

        if (terrain.xPosition, terrain.yPosition,0) == self.targetPosition:
            self.postHandler()
            return
        return False

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
        return super().setParameters(parameters)

    def solver(self, character):
        if len(self.subQuests):
            self.subQuests[0].solver(character)
        else:
            self.triggerCompletionCheck(character)

            charPos = character.getPosition()
            charPos = (charPos[0]%15,charPos[1]%15,charPos[2]%15)
            if charPos == (7,0,0):
                character.runCommandString("s")
                return 
            if charPos == (7,14,0):
                character.runCommandString("w")
                return
            if charPos == (0,7,0):
                character.runCommandString("d")
                return 
            if charPos == (14,7,0):
                character.runCommandString("a")
                return

            if isinstance(character.container,src.rooms.Room):
                if isinstance(character.container,src.rooms.TeleporterRoom):
                    charPos = character.getPosition()
                    for item in character.container.itemsOnFloor:
                        if not item.type == "TeleporterArtwork":
                            continue
                        itemPos = item.getPosition()
                        teleportCommand = ".j"+str(self.targetPosition[0])+","+str(self.targetPosition[1])+"\n"
                        if charPos == (itemPos[0]-1,itemPos[1],itemPos[2]):
                            self.addQuest(src.quests.questMap["RunCommand"](command="Jd"+teleportCommand))
                        elif charPos == (itemPos[0],itemPos[1]-1,itemPos[2]):
                            self.addQuest(src.quests.questMap["RunCommand"](command="Js"+teleportCommand))
                        elif charPos == (itemPos[0]+1,itemPos[1],itemPos[2]):
                            self.addQuest(src.quests.questMap["RunCommand"](command="Ja"+teleportCommand))
                        elif charPos == (itemPos[0],itemPos[1]+1,itemPos[2]):
                            self.addQuest(src.quests.questMap["RunCommand"](command="Jw"+teleportCommand))
                        else:
                            quest = src.quests.questMap["GoToPosition"](targetPosition=itemPos,ignoreEndBlocked=True)
                            quest.assignToCharacter(character)
                            quest.activate()
                            self.addQuest(quest)
                    return
                terrain = character.container.container
            else:
                terrain = character.container

            for room in terrain.rooms:
                if not isinstance(room,src.rooms.TeleporterRoom):
                    continue
                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)
                return

class delLootRuin(MetaQuestSequence):
    def __init__(self, description="loot ruin", creator=None, targetPosition=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

    def triggerCompletionCheck(self,character=None):
        return False

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
            self.metaDescription = self.baseDescription+" "+str(self.targetPosition)
        return super().setParameters(parameters)

    def solver(self, character):
        if len(self.subQuests):
            self.subQuests[0].solver(character)
        else:
            self.triggerCompletionCheck(character)

            if isinstance(character.container,src.rooms.Room):
                terrain = character.container.container
            else:
                terrain = character.container

            if not (terrain.xPosition,terrain.yPosition,0) == self.targetPosition:
                quest = src.quests.questMap["TeleportToTerrain"](targetPosition=self.targetPosition)
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)
                return

            quest = src.quests.questMap["ClearTerrain"]()
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()

class delObtainAllSpecialItems(Quest):

    """
    state initialization
    """

    def __init__(self, description="obtain all special items", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.description = description
        self.homePos = None
        self.priorityObtainID = None
        self.priorityObtainLocation = None
        self.didDelegate = False
        self.resetDelegations = False
        self.epochLength = None

        # save initial state and register
        self.type = "ObtainAllSpecialItems"

    """
    never complete
    """

    def setPriorityObtain(self, itemID, itemLocation, epochLength=None):
        if self.didDelegate:
            self.resetDelegations = True
            
        self.priorityObtainID = itemID
        if epochLength:
            self.epochLength = epochLength
        self.priorityObtainLocation = itemLocation
        self.description = "obtain all special items, especially #%s from %s"%(itemID,itemLocation)
        self.didDelegate = False
        self.aborted = False

    def triggerCompletionCheck(self,character=None):
        return

    def solver(self, character):
        if self.didDelegate:
            if self.aborted:
                character.runCommandString("gg.")
                return
                
            deadchars = 0
            for subordinate in character.subordinates:
                if not subordinate or subordinate.dead:
                    deadchars += 1+3*(1+3)
                    continue
                for subsubordinate in subordinate.subordinates:
                    if not subsubordinate or subsubordinate.dead:
                        deadchars += 1+3
                        continue
                    for worker in subsubordinate.subordinates:
                        if not worker or worker.dead:
                            deadchars += 1
                            continue

            if deadchars > 20:
                for subordinate in character.subordinates:
                    if not subordinate or subordinate.dead:
                        continue
                    for subsubordinate in subordinate.subordinates:
                        if not subsubordinate or subsubordinate.dead:
                            continue

                        subsubordinate.addMessage("The losses were too high, the attack was recalled")
                        subsubordinate.addMessage("abort")

                        for quest in subsubordinate.quests:
                            if not isinstance(subsubordinate.quests[0], Serve):
                                continue
                            quest.cancelOrders()
                            self.aborted = True
                            newQuest = src.quests.questMap["GoHome"]()
                            quest.addQuest(newQuest)
                            break

                        for worker in subsubordinate.subordinates:
                            if not worker or worker.dead:
                                continue

                            worker.addMessage("The losses were too high, the attack was recalled")
                            worker.addMessage("abort")
                            for quest in worker.quests:
                                if not isinstance(worker.quests[0], Serve):
                                    continue
                                quest.cancelOrders()
                                self.aborted = True
                                newQuest = src.quests.questMap["BeUsefull"]()
                                quest.addQuest(newQuest)
                                newQuest = src.quests.questMap["GoHome"]()
                                quest.addQuest(newQuest)
                                break
            return False

        if self.resetDelegations:
            for npc in character.subordinates:
                if not npc or not npc.quests or not isinstance(npc.quests[0], Serve):
                    continue
                serveQuest = npc.quests[0]
                serveQuest.subQuests = []
            self.resetDelegations = False

        if not self.priorityObtainID or not self.priorityObtainLocation:
            character.runCommandString("10.")
            return False

        lifetime = None
        if self.epochLength:
            lifetime=self.epochLength-100
        command = ".QSNObtainSpecialItem\n%s\n%s,%s\nlifetime:%s; ."%(self.priorityObtainID,self.priorityObtainLocation[0],self.priorityObtainLocation[1],lifetime,)
        character.runCommandString(command)

        self.didDelegate = True

        return False

"""
a container quest containing a list of quests that have to be handled in any order
"""


class delMetaQuestParralel(Quest):
    """
    state initialization
    """
    def __init__(
        self, quests, startCinematics=None, looped=False, lifetime=None, creator=None
    ):
        self.subQuests = quests
        self.lastActive = None
        self.metaDescription = "meta"

        super().__init__(
            startCinematics=startCinematics, lifetime=lifetime, creator=creator
        )

        # listen to subquests
        for quest in self.subQuests:
            self.startWatching(quest, self.recalculate)

        # set metadata for saving
        self.attributesToStore.append("metaDescription")
        while "dstX" in self.attributesToStore:
            self.attributesToStore.remove("dstX")
        while "dstY" in self.attributesToStore:
            self.attributesToStore.remove("dstY")
        self.objectsToStore.append("lastActive")

        # store initial state and register
        self.type = "MetaQuestParralel"

    def getActiveQuest(self):
        if self.subQuests:
            return self.subQuests[0].getActiveQuest()
        return self

    def getActiveQuests(self):
        if self.subQuests:
            return self.subQuests[0].getActiveQuests()+[self]
        return [self]

    """
    get state as dict
    """

    def getState(self):
        state = super().getState()

        # store subquests
        state["subQuests"] = {}
        state["subQuests"]["ids"] = []
        state["subQuests"]["states"] = {}
        for quest in self.subQuests:
            state["subQuests"]["ids"].append(quest.id)
            state["subQuests"]["states"][quest.id] = quest.getState()

        return state

    """
    set state as dict
    """

    def setState(self, state):
        super().setState(state)

        # load quests
        if "subQuests" in state:

            # load static quest list
            if "ids" in state["subQuests"]:
                # remove old quests
                for quest in self.subQuests[:]:
                    quest.deactivate()
                    quest.completed = False
                    self.subQuests.remove(quest)

                # load quest
                for thingId in state["subQuests"]["ids"]:
                    # create and add quest
                    thingState = state["subQuests"]["states"][thingId]
                    thing = getQuestFromState(thingState)
                    self.subQuests.append(thing)
                    self.startWatching(self.subQuests[-1], self.recalculate)

            # update changed quests
            if "changed" in state["subQuests"]:
                for thing in self.quests:
                    if thing.id in state["subQuests"]["states"]:
                        thing.setState(state["subQuests"]["states"][thing.id])

            # remove quests
            if "removed" in state["subQuests"]:
                for thing in self.quests:
                    if thing.id in state["subQuests"]["removed"]:
                        self.quests.remove(thing)

            # add new quests
            if "new" in state["subQuests"]:
                for thingId in state["subQuests"]["new"]:
                    thingState = state["subQuests"]["states"][thingId]
                    thing = getQuestFromState(thingState)
                    thing.setState(thingState)
                    self.subQuests.append(thing)
                    self.startWatching(self.subQuests[-1], self.recalculate)

    """
    forward position from last active quest
    """

    @property
    def dstX(self):
        if not self.lastActive:
            return None
        try:
            return self.lastActive.dstX
        except Exception as e:
            src.interaction.debugMessages.append(
                "exception during fetching dstX (" + str(e) + ")"
            )
            return None

    """
    forward position from last active quest
    """

    @property
    def dstY(self):
        if not self.lastActive:
            return None
        try:
            return self.lastActive.dstY
        except Exception as e:
            src.interaction.debugMessages.append(
                "exception during fetching dstY (" + str(e) + ")"
            )
            return None

    """
    get a more detailed description 
    bad code: asList and colored are out of place
    bad code: the asList and colored mixup leads to ugly code
    """

    def getDescription(self, asList=False, colored=False, active=False):
        colored = False
        # add actual quest name
        if asList:
            if colored:
                import urwid

                if active:
                    color = "#0f0"
                else:
                    color = "#090"
                out = [
                    [
                        (urwid.AttrSpec(color, "default"), self.metaDescription + ":"),
                        "\n",
                    ]
                ]
            else:
                out = [[self.metaDescription + ":\n"]]
        else:
            out = "" + self.metaDescription + ":\n"
        if self.lifetimeEvent:
            out += (
                " ("
                + str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)
                + " / "
                + str(self.lifetime)
                + ")"
            )

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
                        deko = "YYYY"  # bad code: impossible state
                elif quest.paused:
                    deko = "  - "
                elif quest.active:
                    deko = "  * "
                else:
                    deko = "XXXX"  # bad code: impossible state

                # set colors
                if colored:
                    import urwid

                    if active and quest == self.lastActive:
                        color = "#0f0"
                    else:
                        color = "#090"
                    deko = (urwid.AttrSpec(color, "default"), deko)

                # add subquest description
                first = True
                if quest == self.lastActive:
                    descriptions = quest.getDescription(
                        asList=asList, colored=colored, active=active
                    )
                else:
                    descriptions = quest.getDescription(asList=asList, colored=colored)
                for item in descriptions:
                    if not first:
                        deko = "    "
                    out.append([deko, item])
                    first = False
            else:
                # add subquest description
                questDescription = (
                    "\n    ".join(quest.getDescription().split("\n")) + "\n"
                )

                # indicate state by arrow type
                if quest == self.lastActive:
                    if quest.active:
                        out += "  ->" + questDescription
                    else:
                        out += "YYYY" + questDescription  # bad code: impossible state
                elif quest.paused:
                    out += "  - " + questDescription
                elif quest.active:
                    out += "  * " + questDescription
                else:
                    out += "XXXX" + questDescription  # bad code: impossible state
            counter += 1
        return out

    """
    render description as simple string
    """

    @property
    def description(self):
        # add the name of the main quest
        out = "" + self.metaDescription + ":\n"

        # add the remaining lifetime
        if self.lifetimeEvent:
            out += (
                " ("
                + str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)
                + " / "
                + str(self.lifetime)
                + ")"
            )

        # add subquests
        for quest in self.subQuests:
            # show subquest description
            questDescription = "\n    ".join(quest.description.split("\n")) + "\n"

            # indicate state by arrow type
            if quest == self.lastActive:
                if quest.active:
                    out += "  ->" + questDescription
                else:
                    if src.interaction.debug:
                        out += "YYYY" + questDescription
                        src.interaction.debugMessages.append(" impossible quest state")
            elif quest.paused:
                out += "  - " + questDescription
            elif quest.active:
                out += "  * " + questDescription
            else:
                if src.interaction.debug:
                    out += "XXXX" + questDescription
                    src.interaction.debugMessages.append(" impossible quest state")
        return out

    """
    make first unpaused quest active
    """

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

    """
    check if there are quests left to do
    """

    def triggerCompletionCheck(self,character=None):
        if not self.subQuests:
            self.postHandler()

    """
    activate self and subquests
    """

    def activate(self):
        super().activate()
        for quest in self.subQuests:
            if not quest.active:
                quest.activate()

    """
    deactivate self and subquests
    """

    def deactivate(self):
        for quest in self.subQuests:
            if quest.active:
                quest.deactivate()
        super().deactivate()

    """
    forward the first solver found
    """

    def solver(self, character):
        for quest in self.subQuests:
            if quest.active and not quest.paused:
                return quest.solver(character)

    """
    add new quest
    """

    def addQuest(self, quest):
        if self.character:
            quest.assignToCharacter(self.character)
        if self.active:
            quest.activate()
        quest.recalculate()
        self.subQuests.insert(0, quest)
        self.startWatching(quest, self.recalculate)


"""
make a character move somewhere. It assumes nothing goes wrong. 
You probably want to use MoveQuestMeta instead
"""


class delNaiveMoveQuest(Quest):
    """
    straightfoward state setting
    """

    def __init__(
        self,
        room=None,
        x=None,
        y=None,
        sloppy=False,
        followUp=None,
        startCinematics=None,
        creator=None,
    ):
        self.dstX = x
        self.dstY = y
        self.room = room
        self.sloppy = sloppy
        self.description = (
            "please go to coordinate " + str(self.dstX) + "/" + str(self.dstY)
        )
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)

        # set metadata for saving
        self.attributesToStore.extend(["description", "sloppy"])
        self.objectsToStore.append("room")

        # save initial state and register
        self.type = "NaiveMoveQuest"

    """
    check if character is in the right place
    """

    def triggerCompletionCheck(self,character=None):

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "triggerCompletionCheck called on inactive " + str(self)
            )
            return

        """
        check if questlist is cyclic
        """

        def checkRecursive(questList):
            for quest in questList:
                if quest == self:
                    return True
                try:
                    if checkRecursive(quest.subQuests):
                        return True
                except:
                    pass
            return False

        # smooth over impossible state
        found = checkRecursive(self.character.quests)
        if not found:
            src.interaction.debugMessages.append("impossible state")
            src.interaction.debugMessages.append(self.id)
            src.interaction.debugMessages.append(self.character)
            return

        # check for exact position
        if not self.sloppy:
            if (
                self.character.xPosition == self.dstX
                and self.character.yPosition == self.dstY
                and self.character.room == self.room
            ):
                self.postHandler()
        # check for neighbouring position
        else:
            if self.character.room == self.room and (
                (
                    self.character.xPosition - self.dstX in (1, 0, -1)
                    and self.character.yPosition == self.dstY
                )
                or (
                    self.character.yPosition - self.dstY in (1, 0, -1)
                    and self.character.xPosition == self.dstX
                )
            ):
                self.postHandler()

    """
    assign to character and add listener
    bad code: should be more specific regarding what to listen
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        super().assignToCharacter(character)
        self.startWatching(character, self.recalculate)

    """
    set state as dict
    """

    def setState(self, state):
        super().setState(state)

        # set character
        if "character" in state and state["character"]:
            """
            set value
            """

            def watchCharacter(character):
                self.startWatching(character, self.recalculate)

            src.saveing.loadingRegistry.callWhenAvailable(
                state["character"], watchCharacter
            )


"""
quest to enter a room. It assumes nothing goes wrong. 
You probably want to use EnterRoomQuestMeta instead
"""


class delNaiveEnterRoomQuest(Quest):
    """
    straightforward state initialization
    """

    def __init__(self, room=None, followUp=None, startCinematics=None, creator=None):
        self.room = room
        if room:
            self.dstX = (
                self.room.walkingAccess[0][0] + room.xPosition * 15 + room.offsetX
            )
            self.dstY = (
                self.room.walkingAccess[0][1] + room.yPosition * 15 + room.offsetY
            )
        else:
            self.dstX = 0
            self.dstY = 0
        self.description = "please enter the room: "

        # set door as target
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)

        self.objectsToStore.append("room")
        self.attributesToStore.extend(["dstX", "dstY", "description"])

        # save initial state and register
        self.type = "NaiveEnterRoomQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

        if room:
            self.description = (
                "please enter the room: "
                + room.name
                + " "
                + str(room.xPosition)
                + " "
                + str(room.yPosition)
            )

    """
    assign character and 
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        super().assignToCharacter(character)
        self.startWatching(character, self.recalculate)

    """
    close door and call superclass
    """

    def postHandler(self):
        # smooth over impossible state
        if not self.character.room:
            src.interaction.debugMessages.append(
                "postHandler called without beeing in a room"
            )
            return

        # bad code: is broken
        if self.character.yPosition in (self.character.room.walkingAccess):
            for item in self.character.room.itemByCoordinates[
                self.character.room.walkingAccess[0]
            ]:
                item.close()

        super().postHandler()

    """
    check if the character is in the correct roon
    """

    def triggerCompletionCheck(self,character=None):

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "triggerCompletionCheck called on inactive quest"
            )
            return

        # start teardown when done
        if self.character.room == self.room:
            self.postHandler()

    def setState(self, state):
        super().setState(state)

        # set character
        if "character" in state and state["character"]:
            """
            set value
            """

            def watchCharacter(character):
                self.startWatching(character, self.recalculate)

            src.saveing.loadingRegistry.callWhenAvailable(
                state["character"], watchCharacter
            )


"""
The naive pickup quest. It assumes nothing goes wrong. 
You probably want to use PickupQuest instead
"""


class delNaivePickupQuest(Quest):
    """
    straightforward state initialization
    """
    objectsToStore = []

    def __init__(
        self, toPickup=None, followUp=None, startCinematics=None, creator=None
    ):
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)
        self.toPickup = toPickup
        if toPickup:
            self.dstX = self.toPickup.xPosition
            self.dstY = self.toPickup.yPosition
            self.startWatching(self.toPickup, self.recalculate)
            self.startWatching(self.toPickup, self.triggerCompletionCheck)
        else:
            self.dstX = 0
            self.dstY = 0
        self.description = "naive pickup"

        # set metadata for saving
        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("toPickup")

        # save initial state and register
        self.type = "NaivePickupQuest"

    """
    check whether item is in characters inventory
    """

    def triggerCompletionCheck(self,character=None):

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "triggerCompletionCheck called on inactive quest"
            )
            return

        # check completion condition
        if self.toPickup not in self.character.inventory:
            return

        # do follow up
        self.postHandler()

    """
    pick up the item
    """

    def solver(self, character):
        # wait if the item is inaccessible
        if not self.toPickup.room and not self.toPickup.terrain:
            return True

        self.toPickup.pickUp(character)
        return True

    """
    set state as dict
    """

    def setState(self, state):
        super().setState(state)

        if "toPickup" in state and state["toPickup"]:
            """
            set value
            """

            def watchThing(thing):
                self.startWatching(thing, self.recalculate)
                self.startWatching(thing, self.triggerCompletionCheck)

            src.saveing.loadingRegistry.callWhenAvailable(state["toPickup"], watchThing)


"""
The naive quest to get a quest from somebody. It assumes nothing goes wrong. 
You probably want to use GetQuest instead
"""


class delNaiveGetQuest(Quest):
    """
    straightforward state initialization
    """

    def __init__(
        self,
        questDispenser=None,
        assign=True,
        followUp=None,
        startCinematics=None,
        creator=None,
    ):
        self.questDispenser = questDispenser
        self.quest = None
        self.assign = assign
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)
        self.description = "naive get quest"

        # set metadata for saving
        self.objectsToStore.append("questDispenser")
        self.attributesToStore.append("assign")

        # save initial state and register
        self.type = "NaiveGetQuest"

    """
    check whether the character has gotten a quest
    """

    def triggerCompletionCheck(self,character=None):
        if self.active:
            if self.quest:
                self.postHandler()

    """
    get quest directly from quest dispenser
    """

    def solver(self, character):
        # get quest
        self.quest = self.questDispenser.getQuest()

        # fail if there is no quest
        if not self.quest:
            self.fail()
            return True

        # assign quest
        if self.assign:
            self.character.assignQuest(self.quest, active=True)

        # trigger cleanup
        self.triggerCompletionCheck()
        return True


"""
The naive quest to fetch the reward for a quest. It assumes nothing goes wrong. 
You probably want to use GetReward instead
"""


class delNaiveGetReward(Quest):
    """
    straightforward state initialization
    """
    objectsToStore = []

    def __init__(self, quest=None, followUp=None, startCinematics=None, creator=None):
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)
        self.quest = quest
        self.description = "naive get reward"
        self.done = False

        # set metadata for saving
        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("quest")

        # save initial state and register
        self.type = "NaiveGetReward"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    check for a done flag
    bad code: general pattern is to actually check if the reward was given
    """

    def triggerCompletionCheck(self,character=None):
        if self.active:
            if self.done:
                self.postHandler()

    """
    assign reward
    bad code: rewarding should be handled within the quest
    """

    def solver(self, character):
        if self.quest:
            if self.quest.reputationReward < 0:
                self.character.revokeReputation(
                    -self.quest.reputationReward, reason="failing to complete a quest"
                )
            else:
                self.character.awardReputation(
                    self.quest.reputationReward, reason="completing a quest"
                )
        self.done = True
        self.triggerCompletionCheck()
        return True


"""
The naive quest to murder someone. It assumes nothing goes wrong. 
You probably want to use MurderQuest instead
"""


class delNaiveMurderQuest(Quest):
    """
    straightforward state initialization
    """

    def __init__(self, toKill=None, followUp=None, startCinematics=None, creator=None):
        self.toKill = toKill
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)
        self.description = "naive murder"

        # save initial state and register
        self.type = "NaiveMurderQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

        self.startWatching(self.toKill,self.triggerCompletionCheck, "died")

    """
    check whether target is dead
    """

    def triggerCompletionCheck(self, extra=None):
        if self.active:
            if self.toKill.dead:
                self.postHandler()

    """
    kill the target
    bad code: murdering should happen within a character
    """

    def solver(self, character):
        self.toKill.die()
        self.triggerCompletionCheck()
        return True


"""
The naive quest to knock out someone. It assumes nothing goes wrong. 
You probably want to use KnockOutQuest instead
"""


class delNaiveKnockOutQuest(Quest):
    """
    straightforward state initialization
    """

    def __init__(self, target=None, followUp=None, startCinematics=None, creator=None):
        self.target = target
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)
        self.description = "naive knock out"

        # save initial state and register
        self.type = "NaiveKnockOutQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    check whether target is dead
    """

    def triggerCompletionCheck(self,character=None):
        if self.active:
            if self.target.unconcious:
                self.postHandler()

    """
    knock the target out
    """

    def solver(self, character):
        self.target.fallUnconcious()
        self.triggerCompletionCheck()
        return True


"""
The naive quest to wake up someone. It assumes nothing goes wrong. 
You probably want to use WakeUpQuest instead
"""


class delNaiveWakeUpQuest(Quest):
    """
    straightforward state initialization
    """

    def __init__(self, target=None, followUp=None, startCinematics=None, creator=None):
        self.target = target
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)
        self.description = "naive wake up"

        # save initial state and register
        self.type = "NaiveWakeUpQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    check whether target is dead
    """

    def triggerCompletionCheck(self, discardParam=None):
        if self.active:
            if not self.target.unconcious:
                self.postHandler()
            elif self.target.dead:
                self.fail()

    """
    start listening to target
    """

    def activate(self):
        super().activate()
        self.startWatching(self.target,self.triggerCompletionCheck, "woke up")
        self.startWatching(self.target,self.triggerCompletionCheck, "died")

    """
    knock the target out
    """

    def solver(self, character):
        self.target.wakeUp()
        self.triggerCompletionCheck()
        return True


"""
The naive quest to activate something. It assumes nothing goes wrong. 
You probably want to use ActivateQuest instead
"""


class delNaiveActivateQuest(Quest):
    """
    straightforward state initialization
    """
    def __init__(
        self, toActivate=None, followUp=None, startCinematics=None, creator=None
    ):
        self.toActivate = toActivate
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)
        self.activated = False

        # set metadata for saving
        self.objectsToStore.append("toActivate")
        self.attributesToStore.append("description")

        # save initial state and register
        self.type = "NaiveActivateQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

        if self.toActivate:
            self.description = "naive activate " + str(self.toActivate.name)
        else:
            self.description = "naive activate"

    """
    callback for activation
    checks if the activated item is the item to activate
    """

    def registerActivation(self, info):
        if self.toActivate == info:
            self.activated = True
            self.triggerCompletionCheck()

    """
    watch for the character activate something
    """

    def activate(self):
        if self.active:
            return

        super().activate()
        self.startWatching(self.character,self.registerActivation, "activate")

    """
    check whether target was activated
    bad code: uses internal state
    """

    def triggerCompletionCheck(self,character=None):
        if self.active:
            if self.activated:
                self.postHandler()

    """
    set state as dict
    """

    def setState(self, state):
        super().setState(state)

        # add listener
        if self.active and self.character:
            self.startWatching(self.character,self.registerActivation, "activate")

    """
    activate the target
    bad code: activate event should be sent from character
    """

    def solver(self, character):
        self.toActivate.apply(character)
        character.changed("activate", self.toActivate)
        return True


"""
The naive quest to drop something. It assumes nothing goes wrong. 
You probably want to use DropQuest instead
bad code: does not register a manual drop
"""


class delNaiveDropQuest(Quest):
    """
    straightforward state initialization
    """
    objectsToStore = []

    def __init__(
        self,
        toDrop=None,
        room=None,
        xPosition=None,
        yPosition=None,
        followUp=None,
        startCinematics=None,
        creator=None,
    ):
        self.dstX = xPosition
        self.dstY = yPosition
        self.room = room
        self.toDrop = toDrop
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)
        if toDrop:
            self.startWatching(self.toDrop, self.recalculate)
            self.startWatching(self.toDrop, self.triggerCompletionCheck)
        self.description = "naive drop"
        self.dropped = False

        # set metadata for saving
        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("toDrop")
            self.objectsToStore.append("room")

        # save initial state and register
        self.type = "NaiveDropQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    check whether item was dropped
    """

    def triggerCompletionCheck(self, ingoreParam=None):
        if self.active:
            if (
                self.toDrop.xPosition == self.dstX
                and self.toDrop.xPosition == self.dstX
                and self.toDrop.room == self.room
            ):
                self.postHandler()

    """
    watch for the character to drop something
    """

    def activate(self):
        super().activate()
        if self.active:
            return

        self.startWatching(self.character,self.triggerCompletionCheck, "drop")

    """
    drop item
    """

    def solver(self, character):
        if self.toDrop not in character.inventory:
            self.fail()
            src.interaction.debugMessages.append(
                "NaiveDropQuest tried to drop item not in characters inventory"
            )
            return True

        character.drop(self.toDrop)
        return True


"""
The naive quest to drop something. It assumes nothing goes wrong. 
You probably want to use DelegateQuest instead
"""


class delNaiveDelegateQuest(Quest):
    """
    straightforward state initialization
    """

    def __init__(self, quest=None, creator=None):
        super().__init__(creator=creator)
        self.quest = quest
        self.description = "naive delegate quest"
        self.startWatching(self.quest, self.triggerCompletionCheck)

        # save initial state and register
        self.type = "NaiveDelegateQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    check if the quest has a character assigned
    """

    def triggerCompletionCheck(self,character=None):
        if self.active:
            if self.quest.character:
                self.postHandler()

    """
    assign quest to first subordinate
    """

    def solver(self, character):
        character.subordinates[0].assignQuest(self.quest, active=True)
        if self.quest.reputationReward:
            character.subordinates[0].rewardReputation(
                self.quest.reputationReward, "completing a quest for somebody"
            )
            character.revokeReputation(
                self.quest.reputationReward, "having somebody complete a quest for you"
            )
        return True


############################################################
#
#   wait quests
#
############################################################

"""
wait until quest is aborted
"""



"""
wait till something was deactivated
"""


class delWaitForDeactivationQuest(Quest):
    """
    state initialization
    """

    def __init__(
        self,
        item=None,
        followUp=None,
        startCinematics=None,
        lifetime=None,
        creator=None,
    ):
        self.item = item
        self.description = "please wait for deactivation of " + self.item.description

        super().__init__(lifetime=lifetime, creator=creator)

        # listen to item
        self.startWatching(self.item, self.recalculate)
        self.pause()  # bad code: why pause by default

        # save initial state and register
        self.type = "WaitForDeactivationQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    check if item is inactive
    """

    def triggerCompletionCheck(self,character=None):
        if not self.item.activated:
            self.postHandler()

    """
    do nothing
    """

    def solver(self, character):
        return True


"""
wail till a specific quest was completed
"""


class delWaitForQuestCompletion(Quest):
    """
    state initialization
    """

    def __init__(self, quest=None, creator=None):
        self.quest = quest
        self.description = "please wait for the quest to completed"
        super().__init__(creator=creator)
        self.startWatching(self.quest, self.triggerCompletionCheck)

        # save initial state and register
        self.type = "WaitForQuestCompletion"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    check if the quest was completed
    """

    def triggerCompletionCheck(self,character=None):
        if self.active:
            if self.quest.completed:
                self.postHandler()

    """
    do nothing
    """

    def solver(self, character):
        return True


###############################################################
#
#      common actions
#
###############################################################

"""
quest to drink something
"""


class delDrinkQuest(Quest):
    """
    straightforward state initialization
    """

    def __init__(self, startCinematics=None, creator=None):
        self.description = "please drink"
        super().__init__(startCinematics=startCinematics, creator=creator)

        # save initial state and register
        self.type = "DrinkQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    assign to character and listen to character
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.recalculate)
        super().assignToCharacter(character)

    """
    drink something
    """

    def solver(self, character):
        for item in character.inventory:
            if isinstance(item, src.items.GooFlask):
                if item.uses > 0:
                    item.apply(character)
                    self.postHandler()
                    break

    """
    check if the character is still thirsty
    """

    def triggerCompletionCheck(self,character=None):
        if self.character.satiation > 800:
            self.postHandler()

        super().triggerCompletionCheck()

    """
    start watching
    """

    def setState(self, state):
        super().setState(state)
        if state["character"]:
            if self.character:
                self.startWatching(self.character, self.recalculate)


"""
ensure own survival
"""


class delSurviveQuest(Quest):
    """
    straightforward state initialization
    """

    def __init__(self, startCinematics=None, looped=True, lifetime=None, creator=None):
        self.description = "survive"
        self.drinkQuest = None
        self.refillQuest = None
        super().__init__(startCinematics=startCinematics, creator=creator)

        # save initial state and register
        self.type = "SurviveQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    assign to character and listen to the character
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        super().assignToCharacter(character)
        self.startWatching(character, self.recalculate)

    """
    spawn quests to take care of basic needs
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on inactive quest: " + str(self)
            )
            return

        # handle edge case
        if not self.character:
            src.interaction.debugMessages.append(
                "recalculate called on quest without character: " + str(self)
            )
            return

        # remove completed quests
        if self.drinkQuest and self.drinkQuest.completed:
            self.drinkQuest = None
        if self.refillQuest and self.refillQuest.completed:
            self.refillQuest = None

        # add quest to refill flask
        for item in self.character.inventory:
            if isinstance(item, src.items.GooFlask):
                if item.uses < 10 and not self.refillQuest:
                    if (
                        not src.gamestate.gamestate.terrain.wakeUpRoom
                        or not src.gamestate.gamestate.terrain.wakeUpRoom.gooDispenser
                    ):
                        return
                    self.refillQuest = RefillDrinkQuest(creator=self)
                    self.character.assignQuest(self.refillQuest, active=True)

        # add quest to drink
        if self.character.satiation < 301:
            if not self.drinkQuest:
                self.drinkQuest = DrinkQuest(creator=self)
                self.character.assignQuest(self.drinkQuest, active=True)


"""
quest for entering a room
"""


class delEnterRoomQuestMeta(MetaQuestSequence):
    """
    basic state initialization
    """
    objectsToStore = []

    def __init__(self, room=None, followUp=None, startCinematics=None, creator=None):
        super().__init__([], creator=creator)
        self.room = room
        if room:
            self.addQuest(NaiveEnterRoomQuest(room, creator=self))
        self.recalculate()
        self.metaDescription = "enterroom Meta"
        self.leaveRoomQuest = None

        # set metadata for saving
        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("room")
            self.objectsToStore.append("leaveRoomQuest")

        # save initial state and register
        self.type = "EnterRoomQuestMeta"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    add quest to leave room if needed
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on inactive quest: " + str(self)
            )
            return

        # add quest to leave room
        if self.leaveRoomQuest and self.leaveRoomQuest.completed:
            self.leaveRoomQuest = None
        if (
            not self.leaveRoomQuest
            and self.character.room
            and not self.character.room == self.room
        ):
            self.leaveRoomQuest = LeaveRoomQuest(self.character.room, creator=self)
            self.addQuest(self.leaveRoomQuest)

        super().recalculate()

    """
    assign quest and listen to character
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.recalculate)
        super().assignToCharacter(character)

    """
    """

    def setState(self, state):
        super().setState(state)
        if "character" in state and state["character"]:
            """
            set value
            """

            def watchCharacter(character):
                self.startWatching(character, self.recalculate)

            src.saveing.loadingRegistry.callWhenAvailable(
                state["character"], watchCharacter
            )


"""
move to a position
"""


class delMoveQuestMeta(MetaQuestSequence):
    """
    state initialization
    """
    def __init__(
        self,
        room=None,
        x=None,
        y=None,
        sloppy=False,
        followUp=None,
        startCinematics=None,
        creator=None,
        lifetime=None,
    ):
        super().__init__([], creator=creator, lifetime=lifetime)
        if not (x is None and y is None):
            self.moveQuest = NaiveMoveQuest(room, x, y, sloppy=sloppy, creator=self)
            questList = [self.moveQuest]
        else:
            questList = []
        self.enterRoomQuest = None
        self.leaveRoomQuest = None
        self.room = room
        for quest in reversed(questList):
            self.addQuest(quest)
        self.metaDescription = "move meta"

        # set metadata for saving
        self.attributesToStore.append("sloppy")
        self.objectsToStore.append("room")
        self.objectsToStore.extend(["enterRoomQuest", "leaveRoomQuest"])

        # save initial state and register
        self.type = "MoveQuestMeta"

    """
    move to correct room if nesseccary
    """

    def recalculate(self):
        return

        # handle impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on non active quest: " + str(self)
            )
            return

        # leave wrong room
        if self.leaveRoomQuest and self.leaveRoomQuest.completed:
            self.leaveRoomQuest = None
        if not self.leaveRoomQuest and (not self.room and self.character.room):
            self.leaveRoomQuest = LeaveRoomQuest(self.character.room, creator=self)
            self.addQuest(self.leaveRoomQuest)

        # enter correct room
        if self.enterRoomQuest and self.enterRoomQuest.completed:
            self.enterRoomQuest = None
        if not self.enterRoomQuest and (
            self.room
            and (not self.character.room or not self.character.room == self.room)
        ):
            self.enterRoomQuest = EnterRoomQuestMeta(self.room, creator=self)
            self.addQuest(self.enterRoomQuest)

        super().recalculate()

    """
    assign to character and listen to character
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.recalculate)
        super().assignToCharacter(character)

    """
    set state as dict
    """

    def setState(self, state):
        super().setState(state)

        if "character" in state and state["character"]:
            """
            set value
            """

            def watchCharacter(character):
                self.startWatching(character, self.recalculate)

            src.saveing.loadingRegistry.callWhenAvailable(
                state["character"], watchCharacter
            )


"""
drop a item somewhere
"""


class delDropQuestMeta(MetaQuestSequence):
    """
    generate quests to move and drop item
    """

    def __init__(
        self,
        toDrop=None,
        room=None,
        xPosition=None,
        yPosition=None,
        followUp=None,
        startCinematics=None,
        creator=None,
    ):
        super().__init__([], creator=creator)
        self.toDrop = toDrop
        if toDrop:
            self.moveQuest = MoveQuestMeta(room, xPosition, yPosition, creator=self)
            questList = [
                self.moveQuest,
                NaiveDropQuest(toDrop, room, xPosition, yPosition, creator=self),
            ]
        else:
            questList = []
        self.room = room
        self.xPosition = xPosition
        self.yPosition = yPosition
        for quest in reversed(questList):
            self.addQuest(quest)
        self.metaDescription = "drop Meta"

        # set metadata for saving
        self.objectsToStore.append("toDrop")
        self.objectsToStore.append("moveQuest")
        self.objectsToStore.append("room")
        self.attributesToStore.extend(["xPosition", "yPosition"])

        # save initial state and register
        self.type = "DropQuestMeta"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    re-add the movement quest if neccessary
    """

    def recalculate(self):
        return

        # handle impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on non active quest: " + str(self)
            )
            return

        # add quest to move to dropoff
        if self.moveQuest and self.moveQuest.completed:
            self.moveQuest = None
        if not self.moveQuest and not (
            self.room == self.character.room
            and self.xPosition == self.character.xPosition
            and self.yPosition == self.character.yPosition
        ):
            self.moveQuest = MoveQuestMeta(
                self.room, self.xPosition, self.yPosition, creator=self
            )
            self.addQuest(self.moveQuest)

        super().recalculate()

    """
    assign to character and listen to character
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.recalculate)
        super().assignToCharacter(character)


"""
pick up an item
"""


class delPickupQuestMeta(MetaQuestSequence):
    """
    generate quests to move and pick up
    """

    def __init__(
        self, toPickup=None, followUp=None, startCinematics=None, creator=None
    ):
        super().__init__([], creator=creator)
        self.toPickup = toPickup
        if toPickup:
            self.sloppy = not self.toPickup.walkable
            self.moveQuest = MoveQuestMeta(
                self.toPickup.room,
                self.toPickup.xPosition,
                self.toPickup.yPosition,
                sloppy=self.sloppy,
                creator=self,
            )
            questList = [self.moveQuest, NaivePickupQuest(self.toPickup, creator=self)]
        else:
            self.sloppy = True
            self.moveQuest = None
            questList = []
        for quest in reversed(questList):
            self.addQuest(quest)
        self.metaDescription = "pickup Meta"

        # set metadata for saving
        self.attributesToStore.append("sloppy")
        self.objectsToStore.append("toPickup")
        self.objectsToStore.append("moveQuest")

        # save initial state and register
        self.type = "PickupQuestMeta"

    """
    re-add the movement quest if neccessary
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on non active quest: " + str(self)
            )
            return

        # handle edge case
        if not self.toPickup:
            src.interaction.debugMessages.append("Pickup quest with nothing to pick up")
            return

        # add quest to move to target
        if self.moveQuest and self.moveQuest.completed:
            self.moveQuest = None
        if not self.moveQuest:
            # check whether it is necessary to re add the movement
            reAddMove = False
            if not self.sloppy:
                if self.toPickup.xPosition is None or self.toPickup.yPosition is None:
                    reAddMove = False
                elif not (
                    self.toPickup.room == self.character.room
                    and self.toPickup.xPosition == self.character.xPosition
                    and self.toPickup.yPosition == self.character.yPosition
                ):
                    reAddMove = True
            else:
                if self.toPickup.xPosition is None or self.toPickup.yPosition is None:
                    reAddMove = False
                elif not (
                    self.toPickup.room == self.character.room
                    and (
                        (
                            self.toPickup.xPosition - self.character.xPosition
                            in (-1, 0, 1)
                            and self.toPickup.yPosition == self.character.yPosition
                        )
                        or (
                            self.toPickup.yPosition - self.character.yPosition
                            in (-1, 0, 1)
                            and self.toPickup.xPosition == self.character.xPosition
                        )
                    )
                ):
                    reAddMove = True

            # re add the movement
            if reAddMove:
                self.moveQuest = MoveQuestMeta(
                    self.toPickup.room,
                    self.toPickup.xPosition,
                    self.toPickup.yPosition,
                    sloppy=self.sloppy,
                    creator=self,
                )
                self.addQuest(self.moveQuest)

        super().recalculate()

    """
    assign to character and listen to character
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.recalculate)
        super().assignToCharacter(character)

    """
    set state as dict
    """

    def setState(self, state):
        super().setState(state)

        if "character" in state and state["character"]:
            """
            set value
            """

            def watchCharacter(character):
                self.startWatching(character, self.recalculate)

            src.saveing.loadingRegistry.callWhenAvailable(
                state["character"], watchCharacter
            )


"""
activate an item
"""


class delActivateQuestMeta(MetaQuestSequence):
    """
    generate quests to move and activate
    """

    def __init__(
        self,
        toActivate=None,
        followUp=None,
        desiredActive=True,
        startCinematics=None,
        creator=None,
    ):
        super().__init__([], creator=creator)
        self.toActivate = toActivate
        if toActivate:
            self.sloppy = not self.toActivate.walkable
            self.moveQuest = MoveQuestMeta(
                toActivate.room,
                toActivate.xPosition,
                toActivate.yPosition,
                sloppy=self.sloppy,
                creator=self,
            )
            questList = [self.moveQuest, NaiveActivateQuest(toActivate, creator=self)]
        else:
            self.sloppy = False
            questList = []

        for quest in reversed(questList):
            self.addQuest(quest)
        self.metaDescription = "activate Quest"

        # set metadata for saving
        self.attributesToStore.append("sloppy")
        self.objectsToStore.append("moveQuest")
        self.objectsToStore.append("toActivate")

        # save initial state and register
        self.type = "ActivateQuestMeta"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    re-add the movement quest if neccessary
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.toActivate:
            src.interaction.debugMessages.append("Pickup quest with nothing to pick up")
            return

        # add quest to move to target
        if self.moveQuest and self.moveQuest.completed:
            self.moveQuest = None
        if self.moveQuest and self.moveQuest not in self.subQuests:
            tmp = self.moveQuest
            self.moveQuest = None
            tmp.deactivate()
        if not self.moveQuest:
            # check whether it is necessary to re add the movement
            reAddMove = False
            if (
                hasattr(self.toActivate, "xPosition")
                and hasattr(self.toActivate, "yPosition")
                and not self.toActivate.xPosition is None
                and not self.toActivate.yPosition is None
            ):
                if not self.sloppy:
                    if not (
                        self.toActivate.room == self.character.room
                        and self.toActivate.xPosition == self.character.xPosition
                        and self.toActivate.yPosition == self.character.yPosition
                    ):
                        reAddMove = True
                else:
                    if not (
                        self.toActivate.room == self.character.room
                        and (
                            (
                                self.toActivate.xPosition - self.character.xPosition
                                in (-1, 0, 1)
                                and self.toActivate.yPosition
                                == self.character.yPosition
                            )
                            or (
                                self.toActivate.yPosition - self.character.yPosition
                                in (-1, 0, 1)
                                and self.toActivate.xPosition
                                == self.character.xPosition
                            )
                        )
                    ):
                        reAddMove = True

            # re add the movement
            if reAddMove:
                self.moveQuest = MoveQuestMeta(
                    self.toActivate.room,
                    self.toActivate.xPosition,
                    self.toActivate.yPosition,
                    sloppy=self.sloppy,
                    creator=self,
                )
                self.addQuest(self.moveQuest)

        super().recalculate()

    """
    start to watch the character
    """

    def activate(self):
        self.startWatching(self.character, self.recalculate)
        super().activate()

    """
    set state from dictionary
    """

    def setState(self, state):
        super().setState(state)
        if self.active:
            self.startWatching(self.character, self.recalculate)


"""
quest to refill the goo flask
"""


class delRefillDrinkQuest(delActivateQuestMeta):
    """
    call superconstructor with modified parameters
    """

    def __init__(self, startCinematics=None, creator=None):
        super().__init__(
            toActivate=src.gamestate.gamestate.terrain.wakeUpRoom.gooDispenser,
            desiredActive=True,
            startCinematics=startCinematics,
            creator=creator,
        )  # bad code: it should select a dispenser that is nearby or something

        # save initial state and register
        self.type = "RefillDrinkQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    check whether the character has a filled goo flask
    """

    def triggerCompletionCheck(self,character=None):
        for item in self.character.inventory:
            if isinstance(item, src.items.GooFlask):
                if item.uses > 99:
                    self.postHandler()


"""
collect items with some quality
"""


class delCollectQuestMeta(MetaQuestSequence):
    """
    state initialization
    """

    def __init__(self, toFind="canBurn", startCinematics=None, creator=None):
        super().__init__([], creator=creator)
        self.toFind = toFind
        self.activateQuest = None
        self.waitQuest = src.quests.questMap["WaitQuest"](creator=self)
        questList = [self.waitQuest]
        # bad code: looping over one entry
        for quest in reversed(questList):
            self.addQuest(quest)
        self.metaDescription = "fetch Quest Meta"

        # save initial state and register
        self.type = "CollectQuestMeta"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    assign to character and add the quest to fetch from a pile
    bad code: only works within room and with piles
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        # handle edge case
        if not character.room:
            src.interaction.debugMessages.append("encountered NIY on collect quest")
            self.postHandler()
            return

        # search for an item
        foundItem = None
        for item in character.room.itemsOnFloor:
            hasProperty = False
            if hasattr(item, "contains_" + self.toFind):
                hasProperty = getattr(item, "contains_" + self.toFind)

            if hasProperty:
                foundItem = item
                break

        # add quest to activate the pile
        if foundItem:
            self.activeQuest = ActivateQuestMeta(foundItem, creator=self)
            self.addQuest(self.activeQuest)

        # terminate when done
        if self.waitQuest and foundItem:
            quest = self.waitQuest
            self.subQuests.remove(quest)
            quest.postHandler()
            self.waitQuest = None

        super().assignToCharacter(character)


"""
a quest for fetching a quest from a quest dispenser
"""


class delGetQuest(MetaQuestSequence):
    """
    generate quests to move to the quest dispenser and get the quest
    """
    objectsToStore = []

    def __init__(
        self,
        questDispenser=None,
        assign=False,
        followUp=None,
        startCinematics=None,
        creator=None,
    ):
        super().__init__([], creator=creator)
        self.questDispenser = questDispenser
        # bad code: semi optional argument
        if questDispenser:
            self.moveQuest = MoveQuestMeta(
                self.questDispenser.room,
                self.questDispenser.xPosition,
                self.questDispenser.yPosition,
                sloppy=True,
                creator=self,
            )
        else:
            self.moveQuest = MoveQuestMeta(creator=self)
        self.getQuest = NaiveGetQuest(questDispenser, assign=assign, creator=self)
        questList = [self.moveQuest, self.getQuest]
        # bad code: repetitive code
        for quest in reversed(questList):
            self.addQuest(quest)
        self.metaDescription = "get Quest"

        # set metainformation for saving
        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("questDispenser")

        # save initial state and register
        self.type = "GetQuest"

    """
    check if a quest was aquired
    """

    def triggerCompletionCheck(self,character=None):

        # smooth over impossible state
        if not self.active:
            return

        # check completion condition
        if not self.quest:
            super().triggerCompletionCheck()
            return

        self.postHandler()

    """
    forward quest from subquest
    """

    @property
    def quest(self):
        return self.getQuest.quest


"""
get the reward for a completed quest
"""


class delGetReward(MetaQuestSequence):
    def __init__(
        self,
        questDispenser=None,
        quest=None,
        assign=False,
        followUp=None,
        startCinematics=None,
        creator=None,
    ):
        super().__init__([], creator=creator)
        self.questDispenser = questDispenser
        # bad code: semi optional argument
        if questDispenser:
            self.moveQuest = MoveQuestMeta(
                self.questDispenser.room,
                self.questDispenser.xPosition,
                self.questDispenser.yPosition,
                sloppy=True,
                creator=self,
            )
        else:
            self.moveQuest = None
        self.getQuest = NaiveGetReward(quest, creator=self)
        questList = [self.moveQuest, self.getQuest]
        self.actualQuest = quest
        self.addedRewardChat = False

        # bad code: repetitive code
        for quest in reversed(questList):
            self.addQuest(quest)

        self.metaDescription = "get Reward"

        # set metainformation for saving
        self.objectsToStore.append("questDispenser")
        self.attributesToStore.append("addedRewardChat")

        # save initial state and register
        self.type = "GetReward"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    assign to character and spawn a chat option to collect reward
    bad code: spawning the chat should happen in activate
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        # handle impossible states
        if not self.actualQuest:
            src.interaction.debugMessages.append(
                "this should not happen (rewardchat without quest"
            )

        # add chat option
        if character == mainChar and not self.addedRewardChat:
            self.addedRewardChat = True
            self.rewardChat = src.chats.RewardChat
            self.questDispenser.basicChatOptions.append(
                {
                    "dialogName": "i did the task: "
                    + self.actualQuest.description.split("\n")[0],
                    "chat": src.chats.RewardChat,
                    "params": {"quest": self, "character": self.character},
                }
            )

        super().assignToCharacter(character)

    """
    remove the reward chat option and do the usual wrap up
    """

    def postHandler(self):

        # remove the quests chat option
        if self.character == mainChar:
            # bad code: repetitive code
            toRemove = None
            for chat in self.questDispenser.basicChatOptions:
                if isinstance(chat, dict):
                    if (
                        chat["chat"] == src.chats.RewardChat
                        and chat["params"]["quest"] == self
                    ):
                        toRemove = chat

            if toRemove:
                self.questDispenser.basicChatOptions.remove(toRemove)

        super().postHandler()


"""
the quest for murdering somebody
"""


class delMurderQuest(MetaQuestSequence):
    """
    generate quests for moving to and murdering the target
    """

    def __init__(
        self,
        toKill=None,
        followUp=None,
        startCinematics=None,
        creator=None,
        lifetime=None,
    ):
        super().__init__([], creator=creator, lifetime=lifetime)
        self.toKill = toKill
        # bad code: semi optional parameter
        if toKill:
            self.moveQuest = MoveQuestMeta(
                self.toKill.room,
                self.toKill.xPosition,
                self.toKill.yPosition,
                sloppy=False,
                creator=self,
            )
            questList = [self.moveQuest, NaiveMurderQuest(toKill, creator=self)]
            self.lastPos = (
                self.toKill.room,
                self.toKill.xPosition,
                self.toKill.yPosition,
            )
            self.startWatching(self.toKill, self.recalculate)
        else:
            self.moveQuest = MoveQuestMeta(
                self.toKill.room,
                self.toKill.xPosition,
                self.toKill.yPosition,
                sloppy=False,
                creator=self,
            )
            questList = [self.moveQuest, NaiveMurderQuest(toKill, creator=self)]
            self.lastPos = (
                self.toKill.room,
                self.toKill.xPosition,
                self.toKill.yPosition,
            )
        self.metaDescription = "murder " + toKill.name

        # bad code: repetitive code
        for quest in reversed(questList):
            self.addQuest(quest)

        # save initial state and register
        self.type = "MurderQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    adjust movement to follow target
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on inactive quest: " + str(self)
            )
            return

        # reset target
        # bad code: frozen npc while reorienting
        pos = (self.toKill.room, self.toKill.xPosition, self.toKill.yPosition)
        if not (pos == self.lastPos) and not self.toKill.dead:
            self.lastPos = pos
            self.moveQuest.deactivate()
            if self.moveQuest in self.subQuests:
                self.subQuests.remove(self.moveQuest)
            self.moveQuest = MoveQuestMeta(
                self.toKill.room,
                self.toKill.xPosition,
                self.toKill.yPosition,
                sloppy=True,
                creator=self,
            )
            self.addQuest(self.moveQuest)
        super().recalculate()


"""
the quest for knocking out somebody
"""


class delKnockOutQuest(MetaQuestSequence):
    """
    generate quests for moving to and kocking out the target
    """

    def __init__(
        self,
        target=None,
        followUp=None,
        startCinematics=None,
        creator=None,
        lifetime=None,
    ):
        super().__init__([], creator=creator, lifetime=lifetime)
        self.target = target
        self.moveQuest = MoveQuestMeta(
            self.target.room,
            self.target.xPosition,
            self.target.yPosition,
            sloppy=True,
            creator=self,
        )
        questList = [self.moveQuest, NaiveKnockOutQuest(target, creator=self)]
        self.lastPos = (self.target.room, self.target.xPosition, self.target.yPosition)
        self.metaDescription = "knock out"
        # bad code: repetitive code
        for quest in reversed(questList):
            self.addQuest(quest)
        self.startWatching(self.target, self.recalculate)

        # save initial state and register
        self.type = "KnockOutQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    adjust movement to follow target
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on inactive quest: " + str(self)
            )
            return

        # reset target if it moved
        pos = (self.target.room, self.target.xPosition, self.target.yPosition)
        if not (pos == self.lastPos) and not self.target.dead:
            self.lastPos = pos
            self.moveQuest.deactivate()
            if self.moveQuest in self.subQuests:
                self.subQuests.remove(self.moveQuest)
            self.moveQuest = MoveQuestMeta(
                self.target.room,
                self.target.xPosition,
                self.target.yPosition,
                sloppy=True,
                creator=self,
            )
            self.addQuest(self.moveQuest)
        super().recalculate()


"""
the quest for waking somebody
"""


class delWakeUpQuest(MetaQuestSequence):
    """
    generate quests for moving to and waking up the target
    """

    def __init__(
        self,
        target=None,
        followUp=None,
        startCinematics=None,
        creator=None,
        lifetime=None,
    ):
        super().__init__([], creator=creator, lifetime=lifetime)
        self.target = target
        self.moveQuest = MoveQuestMeta(
            self.target.room,
            self.target.xPosition,
            self.target.yPosition,
            sloppy=True,
            creator=self,
        )
        questList = [self.moveQuest, NaiveWakeUpQuest(target, creator=self)]
        self.lastPos = (self.target.room, self.target.xPosition, self.target.yPosition)
        self.metaDescription = "wake up somebody"
        # bad code: repetitive code
        for quest in reversed(questList):
            self.addQuest(quest)
        self.startWatching(self.target, self.recalculate)

        # save initial state and register
        self.type = "WakeUpQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    adjust movement to follow target
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on inactive quest: " + str(self)
            )
            return

        pos = (self.target.room, self.target.xPosition, self.target.yPosition)
        if not (pos == self.lastPos):
            self.lastPos = pos
            self.moveQuest.deactivate()
            if self.moveQuest in self.subQuests:
                self.subQuests.remove(self.moveQuest)
            self.moveQuest = MoveQuestMeta(
                self.target.room,
                self.target.xPosition,
                self.target.yPosition,
                sloppy=True,
                creator=self,
            )
            self.addQuest(self.moveQuest)

        super().recalculate()


"""
fill inventory with something
bad code: only fetches fuel
"""


class delFillPocketsQuest(MetaQuestSequence):
    """
    state initialization
    """

    def __init__(
        self, followUp=None, startCinematics=None, lifetime=None, creator=None
    ):
        self.waitQuest = src.quests.questMap["WaitQuest"](creator=self)
        questList = [self.waitQuest]
        self.collectQuest = None
        super().__init__(questList, creator=creator)
        self.metaDescription = "fill pockets"

        # save initial state and register
        self.type = "FillPocketsQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    add collect quest till inventory is full
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on inactive " + str(self)
            )
            return

        # handle edge case
        if not self.character:
            src.interaction.debugMessages.append(
                "recalculate called without character on " + str(self)
            )
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


"""
quest to leave the room
"""


class delLeaveRoomQuest(Quest):
    objectsToStore = []
    def __init__(self, room=None, followUp=None, startCinematics=None, creator=None):
        self.room = room
        self.description = "please leave the room."
        # bad code: semi optional parameter
        if room:
            self.dstX = self.room.walkingAccess[0][0]
            self.dstY = self.room.walkingAccess[0][1]
        else:
            self.dstX = 0
            self.dstY = 0
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)

        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("room")

        # save initial state and register
        self.type = "LeaveRoomQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    move to door and step out of the room
    """

    def solver(self, character):
        # bad code: solver execution should be split from the rest of the logic
        if super().solver(character):
            if not character.room:
                return True

            # close door
            for item in character.room.itemByCoordinates[
                (character.xPosition, character.yPosition)
            ]:
                if isinstance(item, src.items.Door):
                    item.close()

            # add step out of the room
            if character.yPosition == 0:
                character.path.append((character.xPosition, character.yPosition - 1))
            elif character.yPosition == character.room.sizeY - 1:
                character.path.append((character.xPosition, character.yPosition + 1))
            elif character.xPosition == 0:
                character.path.append((character.xPosition - 1, character.yPosition))
            elif character.xPosition == character.room.sizeX - 1:
                character.path.append((character.xPosition + 1, character.yPosition))
            character.walkPath()
            return False

    """
    assign to and listen to character
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        super().assignToCharacter(character)
        self.startWatching(character, self.recalculate)

        super().recalculate()

    """
    check if the character left the room
    """

    def triggerCompletionCheck(self,character=None):

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "triggerCompletionCheck called on inactive " + str(self)
            )
            return

        # handle edge case
        if not self.character:
            src.interaction.debugMessages.append(
                "triggerCompletionCheck called without character on " + str(self)
            )
            return

        # trigger followup when done
        if not self.character.room == self.room:
            self.postHandler()


"""
patrol along a circular path
"""


"""
quest to examine the environment
bad pattern: has no solver
"""


class delExamineQuest(Quest):
    """
    state initialization
    """

    def __init__(self, startCinematics=None, completionThreshold=5, creator=None):
        self.completionThreshold = completionThreshold
        self.description = "please examine your environment"
        self.examinedItems = []
        super().__init__(startCinematics=startCinematics, creator=creator)
        self.attributesToStore.append("completionThreshold")

        # save initial state and register
        self.type = "ExamineQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    check if some items were observed
    """

    def triggerCompletionCheck(self,character=None):
        # bad code: fixed threshold
        if len(self.examinedItems) >= 5:
            self.postHandler()

    """
    activate and start watching character
    """

    def activate(self):
        if self.active:
            return

        self.startWatching(self.character,self.registerExaminination, "examine")
        super().activate()

    """
    callback for the character examining things
    increases the counter of observed items
    """

    def registerExaminination(self, item):
        itemType = type(item)
        if itemType in self.examinedItems:
            return

        self.examinedItems.append(itemType)
        self.triggerCompletionCheck()

    """
    set up listener
    """

    def setState(self, state):
        super().setState(state)

        # smooth over impossible state
        if not self.active:
            return
        if not self.character:
            return

        self.startWatching(self.character,self.registerExaminination, "examine")

    def solver(self, character):
        # bad code: only pretends to solve the quest
        self.examinedItems = [None, None, None, None, None]
        self.triggerCompletionCheck()


##############################################################################
#
#  construction quests
#
#############################################################################

"""
move some furniture to the construction room
bad code: name lies somewhat
"""


class delFetchFurniture(delMetaQuestParralel):
    """
    create subquest to move each piece of scrap to the metalworkshop
    """

    def __init__(
        self,
        constructionSite=None,
        storageRooms=None,
        toFetch=None,
        followUp=None,
        startCinematics=None,
        failTrigger=None,
        lifetime=None,
        creator=None,
    ):
        super().__init__([], creator=creator)
        questList = []
        # bad code: hardcoded dropoffs
        dropoffs = [(4, 4), (5, 4), (5, 5), (5, 6), (4, 6), (3, 6), (3, 5), (3, 4)]
        self.itemsInStore = []
        thisToFetch = toFetch[:]

        # calculate how many items should be moved
        counter = 0
        maxNum = len(toFetch)
        if maxNum > len(dropoffs):
            maxNum = len(dropoffs)

        # generate quests for fetching furniture
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
                    if isinstance(item, fetchType[1]):
                        selectedItem = item
                        storageRoom.storedItems.remove(selectedItem)
                        storageRoom.storageSpace.append(
                            (selectedItem.xPosition, selectedItem.yPosition)
                        )
                        fetchType = None
                        break
                if selectedItem:
                    break

            if not selectedItem:
                # do nothing
                break

            # add quest to transport the item
            questList.append(
                TransportQuest(
                    selectedItem,
                    (constructionSite, dropoffs[counter][1], dropoffs[counter][0]),
                    creator=self,
                )
            )
            self.itemsInStore.append(selectedItem)

            counter += 1

        # bad code: repetitive code
        for quest in reversed(questList):
            self.addQuest(quest)

        self.metaDescription = "fetch furniture"

        # save initial state and register
        self.type = "FetchFurniture"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)


"""
place furniture within a contruction site
"""


class delPlaceFurniture(delMetaQuestParralel):
    """
    generates quests picking up the furniture and dropping it at the right place
    bad code: generating transport quests would be better
    """

    def __init__(
        self,
        constructionSite=None,
        itemsInStore=None,
        followUp=None,
        startCinematics=None,
        failTrigger=None,
        lifetime=None,
        creator=None,
    ):
        super().__init__([], creator=creator)
        questList = []

        # handle each item
        counter = 0
        while counter < len(itemsInStore):
            # get item to place
            if not constructionSite.itemsInBuildOrder:
                break
            toBuild = constructionSite.itemsInBuildOrder.pop()

            # move item
            quest = TransportQuestMeta(
                itemsInStore[counter],
                (constructionSite, toBuild[0][1], toBuild[0][0]),
                creator=self,
            )
            questList.append(quest)
            self.startWatching(quest, self.recalculate)
            counter += 1

        # bad code: repetitive code
        for quest in reversed(questList):
            self.addQuest(quest)

        self.metaDescription = "place furniture"

        # save initial state and register
        self.type = "PlaceFurniture"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)


"""
construct a room
bad code: is broken
"""


class delConstructRoom(delMetaQuestParralel):
    """
    straightforward state initialization
    """

    def __init__(
        self,
        constructionSite=None,
        storageRooms=None,
        followUp=None,
        startCinematics=None,
        failTrigger=None,
        lifetime=None,
        creator=None,
    ):

        questList = []

        self.constructionSite = constructionSite
        self.storageRooms = storageRooms
        self.itemsInStore = []

        self.didFetchQuest = False
        self.didPlaceQuest = False

        super().__init__(questList, creator=creator)
        self.metaDescription = "construct room"

        # save initial state and register
        self.type = "ConstructRoom"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    add quests to fetch and place furniture
    """

    def recalculate(self):
        return

        # bad code: questlist isn't even defined here
        if not questList or questList[0].completed:
            if not self.didFetchQuest:
                # fetch some furniture from storage
                self.didFetchQuest = True
                self.didPlaceQuest = False
                self.fetchquest = FetchFurniture(
                    self.constructionSite,
                    self.storageRooms,
                    self.constructionSite.itemsInBuildOrder,
                    creator=self,
                )
                self.addQuest(self.fetchquest)
                self.itemsInStore = self.fetchquest.itemsInStore
            elif not self.didPlaceQuest:
                # place furniture in desired position
                self.didPlaceQuest = True
                self.placeQuest = PlaceFurniture(
                    self.constructionSite, self.itemsInStore, creator=self
                )
                self.addQuest(self.placeQuest)
                if self.constructionSite.itemsInBuildOrder:
                    self.didFetchQuest = False
        super().recalculate()

    """
    do not terminate until all fetching and placing was done
    """

    def triggerCompletionCheck(self,character=None):
        if not self.didFetchQuest or not self.didPlaceQuest:
            return
        super().triggerCompletionCheck()


#########################################################################
#
#    logistics related quests
#
#########################################################################

"""
transport an item to a position
"""


class delTransportQuest(MetaQuestSequence):
    """
    generate quest for picking up the item
    """
    objectsToStore = []

    def __init__(
        self,
        toTransport=None,
        dropOff=None,
        followUp=None,
        startCinematics=None,
        lifetime=None,
        creator=None,
    ):
        self.dropOff = dropOff
        super().__init__([], creator=creator)
        self.toTransport = toTransport
        questList = []
        quest = PickupQuestMeta(self.toTransport, creator=self)
        quest.endTrigger = {"container": self, "method": "addDrop"}
        questList.append(quest)
        for quest in reversed(questList):
            self.addQuest(quest)
        self.metaDescription = "transport"

        # set meta information for saving
        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("toTransport")

        # save initial state and register
        self.type = "TransportQuest"

    """
    drop the item after picking it up
    """

    def addDrop(self):
        if not self.dropOff:
            return

        self.addQuest(
            DropQuestMeta(
                self.toTransport,
                self.dropOff[0],
                self.dropOff[1],
                self.dropOff[2],
                creator=self,
            )
        )

    """
    set internal state from dictionary
    """

    def setState(self, state):
        super().setState(state)

        self.dropOff = []
        self.dropOff.append(None)
        self.dropOff.append(state["dropOff"][1])
        self.dropOff.append(state["dropOff"][2])

        """
        set value
        """

        def addRoom(room):
            self.dropOff[0] = room

        src.saveing.loadingRegistry.callWhenAvailable(state["dropOff"][0], addRoom)

    """
    get state as dictionary
    """

    def getState(self):
        state = super().getState()

        if self.dropOff and self.dropOff[0]:
            state["dropOff"] = []
            state["dropOff"].append(self.dropOff[0].id)
            state["dropOff"].append(self.dropOff[1])
            state["dropOff"].append(self.dropOff[2])

        return state


"""
move items from permanent storage to accesible storage
"""


class delStoreCargo(MetaQuestSequence):
    """
    generate quests for transporting each item
    """

    def __init__(
        self,
        cargoRoom=None,
        storageRoom=None,
        followUp=None,
        startCinematics=None,
        lifetime=None,
        creator=None,
    ):
        super().__init__([], creator=creator)
        questList = []

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
            questList.append(
                TransportQuest(
                    cargoRoom.storedItems.pop(),
                    (storageRoom, location[0], location[1]),
                    creator=self,
                )
            )
            counter += 1

        # bad code: repetitive code
        for quest in reversed(questList):
            self.addQuest(quest)

        self.metaDescription = "store cargo"

        # save initial state and register
        self.type = "StoreCargo"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)


"""
move items to accessible storage
"""


class delMoveToStorage(MetaQuestSequence):
    """
    generate the quests to transport each item
    """

    def __init__(self, items=None, storageRoom=None, creator=None, lifetime=None):
        super().__init__([], creator=creator, lifetime=lifetime)
        questList = []

        # bad code: semi optional parameter
        if items:

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
                self.addQuest(
                    TransportQuest(
                        items.pop(),
                        (storageRoom, location[0], location[1]),
                        creator=self,
                    )
                )
                counter += 1

        self.metaDescription = "move to storage"

        # save initial state and register
        self.type = "MoveToStorage"


"""
handle a delivery
bad pattern: the quest is tailored to a story, it should be more abstracted
bad pattern: the quest can only be solved by delegation
"""


class delHandleDelivery(MetaQuestSequence):
    """
    state initialization
    """

    def __init__(self, cargoRooms=[], storageRooms=[], creator=None):
        self.cargoRooms = cargoRooms
        self.storageRooms = storageRooms
        questList = []
        super().__init__(questList, creator=creator)
        self.addNewStorageRoomQuest()
        self.metaDescription = "ensure the cargo is moved to storage"

        # save initial state and register
        self.type = "HandleDelivery"

    """
    listen to subordinates
    """

    def activate(self):
        super().activate()
        if self.character:
            for sub in self.character.subordinates:
                self.startWatching(sub,self.rescueSub, "fallen unconcious")

    """
    wake up subordinate
    """

    def rescueSub(self, character):
        self.addQuest(WakeUpQuest(character, creator=self), addFront=True)

    """
    wait the cargo to be moved to storage
    """

    def waitForQuestCompletion(self):
        quest = WaitForQuestCompletion(self.quest, creator=self)
        quest.endTrigger = self.addNewStorageRoomQuest
        self.addQuest(quest)

    """
    delegate moving the cargo to storage
    """

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
        self.quest = StoreCargo(room, self.storageRooms.pop(), creator=self)
        self.quest.reputationReward = 5
        quest = NaiveDelegateQuest(self.quest, creator=self)
        quest.endTrigger = self.waitForQuestCompletion
        self.addQuest(quest)


############################################################
#
#   furnace specific quests
#
############################################################

"""
fire a list of furnaces an keep them fired
"""


class delKeepFurnacesFiredMeta(delMetaQuestParralel):
    """
    add a quest to keep each furnace fired
    """

    def __init__(
        self,
        furnaces=None,
        followUp=None,
        startCinematics=None,
        failTrigger=None,
        lifetime=None,
        creator=None,
    ):
        questList = []
        for furnace in furnaces:
            questList.append(KeepFurnaceFiredMeta(furnace))
        # bad code: the questlist parameter is deprecated
        super().__init__(questList, creator=creator)
        self.metaDescription = "KeepFurnacesFiredMeta"

        # save initial state and register
        self.type = "KeepFurnacesFiredMeta"


"""
fire a furnace an keep it fired
"""


class delKeepFurnaceFiredMeta(MetaQuestSequence):
    """
    basic state initialization
    """
    objectsToStore = []

    def __init__(
        self,
        furnace=None,
        followUp=None,
        startCinematics=None,
        failTrigger=None,
        lifetime=None,
        creator=None,
    ):
        questList = []
        self.fireFurnaceQuest = None
        self.waitQuest = None
        self.furnace = furnace
        super().__init__(
            questList,
            lifetime=lifetime,
            creator=creator,
            followUp=followUp,
            startCinematics=startCinematics,
            failTrigger=failTrigger,
        )
        self.metaDescription = "KeepFurnaceFiredMeta"

        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("furnace")

        # listen to furnace
        self.startWatching(self.furnace, self.recalculate)

        # save initial state and register
        self.type = "KeepFurnaceFiredMeta"

    """
    add sub quests
    """

    def recalculate(self):
        return

        # handle impossible state
        if not self.character:
            # bad code: should log
            return

        # add firing the furnace if needed
        if self.fireFurnaceQuest and self.fireFurnaceQuest.completed:
            self.fireFurnaceQuest = None
        if not self.fireFurnaceQuest and not self.furnace.activated:
            self.fireFurnaceQuest = FireFurnaceMeta(self.furnace, creator=self)
            self.addQuest(self.fireFurnaceQuest)
            self.unpause()

        # wait for the furnace to burn out if needed
        if self.waitQuest and self.waitQuest.completed:
            self.waitQuest = None
        if not self.waitQuest and not self.fireFurnaceQuest:
            if self.furnace.activated:
                self.waitQuest = WaitForDeactivationQuest(self.furnace, creator=self)
                self.startWatching(self.waitQuest, self.recalculate)
                self.addQuest(self.waitQuest)
                self.pause()
            else:
                self.unpause()

        super().recalculate()

    """
    never complete
    """

    def triggerCompletionCheck(self,character=None):
        return


"""
fire a furnace once
"""


class delFireFurnaceMeta(MetaQuestSequence):
    """
    state initialization
    """
    objectsToStore = []

    def __init__(
        self,
        furnace=None,
        followUp=None,
        startCinematics=None,
        failTrigger=None,
        lifetime=None,
        creator=None,
    ):
        self.activateQuest = None
        self.collectQuest = None
        self.furnace = furnace
        super().__init__([], creator=creator)
        self.metaDescription = "FireFurnaceMeta"

        # set meta information for saving
        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("furnace")

        # save initial state and register
        self.type = "FireFurnaceMeta"

    """
    collect coal and fire furnace
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on inactive " + str(self)
            )
            return

        # handle edge case
        if not self.character:
            src.interaction.debugMessages.append(
                "recalculate called without character on " + str(self)
            )
            return

        # add quest to collect fuel if needed
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
                self.startWatching(self.collectQuest, self.recalculate)
                self.subQuests.insert(0, self.collectQuest)
                self.collectQuest.activate()
                self.changed()

                # pause quest to fire furnace
                if self.activateQuest:
                    self.activateQuest.pause()

        # unpause quest to fire furnace if coal is available
        if self.activateQuest and not self.collectQuest:
            self.activateQuest.unpause()

        # add quest to fire furnace
        if (
            not self.activateQuest
            and not self.collectQuest
            and not self.furnace.activated
        ):
            self.activateQuest = ActivateQuestMeta(self.furnace, creator=self)
            self.activateQuest.assignToCharacter(self.character)
            self.activateQuest.activate()
            self.subQuests.append(self.activateQuest)
            self.startWatching(self.activateQuest, self.recalculate)
            self.changed()

        super().recalculate()

    """
    set internal state from dictionary
    """

    def setState(self, state):
        super().setState(state)

        if "furnace" in state and state["furnace"]:
            """
            set value
            """

            def watch(thing):
                self.startWatching(thing, self.triggerCompletionCheck)

            src.saveing.loadingRegistry.callWhenAvailable(state["furnace"], watch)

    """
    assign to character and listen to character
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.recalculate)
        super().assignToCharacter(character)

    """
    check if furnace is burning
    """

    def triggerCompletionCheck(self,character=None):
        if self.furnace.activated:
            self.postHandler()

        super().triggerCompletionCheck()


"""
Fill a growth tank
"""


class delFillGrowthTankMeta(MetaQuestSequence):
    """
    state initialization
    """
    objectsToStore = []

    def __init__(
        self,
        growthTank=None,
        followUp=None,
        startCinematics=None,
        failTrigger=None,
        lifetime=None,
        creator=None,
    ):
        self.activateQuest = None
        self.refillQuest = None
        self.growthTank = growthTank
        super().__init__([], creator=creator)
        self.metaDescription = "FillGrowthTankMeta"

        # set meta information for saving
        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("growthTank")

        # save initial state and register
        self.type = "FillGrowthTankMeta"

    """
    fetch goo and refill the machine
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on inactive " + str(self)
            )
            return

        # handle edge case
        if not self.character:
            src.interaction.debugMessages.append(
                "recalculate called without character on " + str(self)
            )
            return

        if not self.activateQuest:
            self.activateQuest = ActivateQuestMeta(self.growthTank, creator=self)
            self.addQuest(self.activateQuest)

        hasFullFlask = False
        for item in self.character.inventory:
            if isinstance(item, src.items.GooFlask):
                if item.uses < 10:
                    continue
                hasFullFlask = True

        if self.refillQuest and self.refillQuest.completed:
            self.refillQuest = None
        if not hasFullFlask and not self.refillQuest:
            self.refillQuest = RefillDrinkQuest(creator=self)
            self.addQuest(self.refillQuest)

        super().recalculate()

    """
    set internal state from dictionary
    """

    def setState(self, state):
        super().setState(state)

        if "growthTank" in state and state["growthTank"]:
            """
            set value
            """

            def watch(thing):
                self.startWatching(thing, self.triggerCompletionCheck)

            src.saveing.loadingRegistry.callWhenAvailable(state["growthTank"], watch)

    """
    assign to character and listen to character
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.recalculate)
        super().assignToCharacter(character)

    """
    check if furnace is burning
    """

    def triggerCompletionCheck(self,character=None):
        if not self.growthTank.filled:
            return

        super().triggerCompletionCheck()


##############################################################################
#
#  actual tasks
#
#############################################################################

"""
basically janitor duty
"""


class delHopperDuty(MetaQuestSequence):
    """
    straightforward state initialization
    """
    objectsToStore = []

    def __init__(
        self,
        waitingRoom=None,
        startCinematics=None,
        looped=True,
        lifetime=None,
        creator=None,
    ):
        super().__init__([], startCinematics=startCinematics, creator=creator)
        if waitingRoom:
            self.getQuest = GetQuest(
                waitingRoom.secondOfficer, assign=False, creator=self
            )
        else:
            self.getQuest = GetQuest(creator=self)
        self.getQuest.endTrigger = {"container": self, "method": "setQuest"}
        self.addQuest(self.getQuest)
        self.metaDescription = "hopper duty"
        self.recalculate()
        self.actualQuest = None
        self.rewardQuest = None
        self.waitingRoom = waitingRoom

        # set meta information for saving
        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("actualQuest")
            self.objectsToStore.append("rewardQuest")
            self.objectsToStore.append("getQuest")
            self.objectsToStore.append("waitingRoom")

        # save initial state and register
        self.type = "HopperDuty"

    """
    get quest, do it, collect reward - repeat
    """

    def recalculate(self):
        return

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on inactive quest: " + str(self)
            )
            return

        # remove completed quest
        if self.getQuest and self.getQuest.completed:
            self.getQuest = None

        # add quest to fetch reward
        if self.actualQuest and self.actualQuest.completed and not self.rewardQuest:
            self.rewardQuest = GetReward(
                self.waitingRoom.secondOfficer, self.actualQuest, creator=self
            )
            self.rewardQuest.assignToCharacter(self.character)
            self.actualQuest = None
            self.addQuest(self.rewardQuest, addFront=False)

        # remove completed quest
        if self.rewardQuest and self.rewardQuest.completed:
            self.rewardQuest = None

        # add quest to get a new quest
        if not self.getQuest and not self.actualQuest and not self.rewardQuest:
            self.getQuest = GetQuest(
                self.waitingRoom.secondOfficer, assign=False, creator=self
            )
            self.getQuest.assignToCharacter(self.character)
            self.getQuest.endTrigger = {"container": self, "method": "setQuest"}
            self.addQuest(self.getQuest, addFront=False)

        super().recalculate()

    """
    add the actual quest as subquest
    """

    def setQuest(self):
        self.actualQuest = self.getQuest.quest
        if self.actualQuest:
            self.addQuest(self.actualQuest, addFront=False)
        else:
            self.addQuest(src.quests.questMap["WaitQuest"](lifetime=10, creator=self), addFront=False)


"""
clear the rubble from the mech
bad pattern: there is no way to determine what is to be picked up
"""


class delClearRubble(delMetaQuestParralel):
    """
    create subquest to move each piece of scrap to the metal workshop
    """

    def __init__(
        self,
        followUp=None,
        startCinematics=None,
        failTrigger=None,
        lifetime=None,
        creator=None,
    ):
        super().__init__([], creator=creator)
        questList = []
        for item in src.gamestate.gamestate.terrain.itemsOnFloor:
            if isinstance(item, src.items.Scrap):
                self.addQuest(
                    TransportQuest(
                        item,
                        (src.gamestate.gamestate.terrain.metalWorkshop, 7, 1),
                        creator=self,
                    )
                )
        self.metaDescription = "clear rubble"

        # save initial state and register
        self.type = "ClearRubble"


"""
dummy quest for doing the room duty
"""


class delRoomDuty(delMetaQuestParralel):
    """
    state initialization
    """

    def __init__(self, cargoRooms=[], storageRooms=[], creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = "room duty"

        # save initial state and register
        self.type = "RoomDuty"

    """
    never complete
    """

    def triggerCompletionCheck(self,character=None):
        return


"""
dummy quest for following somebodies orders
"""


class delServe(delMetaQuestParralel):
    """
    state initialization
    """
    def __init__(self, superior=None, creator=None):
        self.objectsToStore = []
        questList = []
        self.superior = superior
        super().__init__(questList, creator=creator)
        self.metaDescription = "serve"


        # set meta information for saving
        self.objectsToStore.append("superior")

        # save initial state and register
        self.type = "Serve"

        if superior:
            self.metaDescription += " " + superior.name

    def cancelOrders(self):
        for quest in self.subQuests:
            quest.fail()

    """
    never complete
    """

    def triggerCompletionCheck(self,character=None):
        return

    def solver(self,character):
        if not hasattr(character,"superior") or not character.superior or character.superior.dead:
            character.die(reason="superior died")
            return
        if not self.subQuests:
            character.runCommandString(".gg.")
            return
        super().solver(character)

    def setState(self,state):
        super().setState(state)

class delDeliverSpecialItem(Quest):
    def __init__(self, description="deliverSpecialItem", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.description = description
        # save initial state and register
        self.type = "DeliverSpecialItem"
        self.itemID = None
        self.hadItem = None
        self.gaveReward = False

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")

        super().assignToCharacter(character)


    def triggerCompletionCheck(self, character=None):
        if not character:
            return

        foundItem = None
        for item in character.inventory:
            if not item.type == "SpecialItem":
                continue

            if not self.itemID == None and not self.itemID == item.itemID:
                continue

            foundItem = item
            self.itemID = item.itemID

        if not foundItem:
            self.fail()
            return True

        if not character.container:
            return
        if not isinstance(character.container, src.rooms.Room):
            return
        if not self.itemID:
            return

        foundItemSlot = None
        for item in character.container.itemsOnFloor:
            if not item.type == "SpecialItemSlot":
                continue

            if not item.itemID == self.itemID:
                continue

            foundItemSlot = item

        if not foundItemSlot:
            return

        if foundItemSlot.hasItem:
            if self.hadItem:
                if not self.gaveReward:
                    character.reputation += 1000
                    self.gaveReward = True
                self.postHandler()
            else:
                self.fail()
            return True

    def solver(self,character):
        command = self.getSolvingCommandString(character, dryRun = False)

        if not command:
            command = ".46.."

        character.runCommandString(command)
        return False

    def getSolvingCommandString(self, character, dryRun = True):

        if self.triggerCompletionCheck(character):
            return
        if not character.container:
            return
        if not isinstance(character.container, src.rooms.Room):
            charPos = (character.xPosition%15,character.yPosition%15,0)
            if charPos == (7,0,0):
                return "s"
            return

        foundItem = None
        for item in character.inventory:
            if not item.type == "SpecialItem":
                continue

            if not self.itemID == None and not self.itemID == item.itemID:
                continue

            foundItem = item
            self.itemID = item.itemID

        if not foundItem:
            self.hadItem = False
            self.fail()
            return None

        self.hadItem = True
        foundItemSlot = None
        for item in character.container.itemsOnFloor:
            if not item.type == "SpecialItemSlot":
                continue

            if not item.itemID == foundItem.itemID:
                continue

            foundItemSlot = item

        if not foundItemSlot:
            self.fail()
            return None

        command = ""
        command += "w"*(character.yPosition-foundItemSlot.yPosition)
        command += "s"*(foundItemSlot.yPosition-character.yPosition)
        command += "a"*(character.xPosition-foundItemSlot.xPosition)
        command += "d"*(foundItemSlot.xPosition-character.xPosition)
        command += "j"
        command += "sd"

        return command

class delGrabSpecialItem(Quest):
    def __init__(self, description="grab special item", creator=None,lifetime=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.description = description
        # save initial state and register
        self.type = "GrabSpecialItem"
        self.itemID = None

        self.attributesToStore.extend([
            "itemID","hasListener"])

    def triggerCompletionCheck(self, character=None):
        if not character:
            return

        itemFound = None
        for item in character.inventory:
            if not item.type == "SpecialItem":
                continue
            if not item.itemID == self.itemID:
                continue
            itemFound = item
            break
        
        if not itemFound:
            return

        self.postHandler()

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")

        super().assignToCharacter(character)

    def solver(self,character):
        if not character.container or not isinstance(character.container, src.rooms.Room):
            self.fail()
            return

        for item in character.container.itemsOnFloor:
            if not item.type in ("SpecialItemSlot","SpecialItem",):
                continue
            if item.type == "SpecialItemSlot":
                if not item.hasItem:
                    continue
            if not item.itemID == self.itemID:
                continue

            character.runCommandString("k")

            if item.type == "SpecialItemSlot":
                if item.xPosition == 1:
                    character.runCommandString("d")
                else:
                    character.runCommandString("s")

                character.runCommandString("j")

            character.runCommandString("a"*(character.xPosition-item.xPosition))
            character.runCommandString("d"*(item.xPosition-character.xPosition))
            character.runCommandString("w"*(character.yPosition-item.yPosition))
            character.runCommandString("s"*(item.yPosition-character.yPosition))
            return False
        self.fail()
        return

class delEnterEnemyCity(MetaQuestSequence):
    def __init__(self, description="enter enemy city", creator=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        # save initial state and register
        self.type = "EnterEnemyCity"
        self.cityLocation = None
        self.centerFailCounter = 0
        self.rewardedNearby = False

        self.attributesToStore.extend([
            "rewardedNearby","centerFailCounter","hasListener"])
        self.tuplesToStore.extend(["cityLocation"])

    def triggerCompletionCheck(self, character=None, direction=None):
        if not character:
            return
        if not self.cityLocation:
            return

        if isinstance(character.container, src.rooms.Room):
            #if (character.container.terrain.xPosition == self.cityLocation[0] and character.container.terrain.yPosition == self.cityLocation[1]):
            if not (character.container.terrain):
                return
            if not (character.container.terrain.xPosition == 7 and character.container.terrain.yPosition == 6):
                return
            if (character.container.xPosition == self.cityLocation[0] and character.container.yPosition == self.cityLocation[1]):
                self.postHandler()
            if not self.rewardedNearby and abs(character.xPosition//15-self.cityLocation[0])+abs(character.yPosition//15-self.cityLocation[1]) == 1:
                character.awardReputation(amount=5, reason="getting near the enemy city", carryOver=True)
                self.rewardedNearby = True

    def timeOut(self):
        if not self.rewardedNearby:
            self.character.revokeReputation(amount=5, reason="not getting near the enemy city")
        super().timeOut()

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return

        self.reroll()
        self.triggerCompletionCheck(extraInfo[0])

    def setCityLocation(self, cityLocation):
        self.cityLocation = cityLocation
        self.metaDescription = "enter enemy city %s"%(self.cityLocation,)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        
        super().assignToCharacter(character)

    def getSolvingCommandString(self, character, realRun = False, dryRun=True):
        localRandom = random.Random(self.randomSeed)

        if isinstance(character.container, src.rooms.Room):
            if not character.container.terrain:
                return None

            if (not (character.container.xPosition == self.cityLocation[0] and character.container.yPosition == self.cityLocation[1])):
                if not (character.xPosition == 6 and character.yPosition == 6):

                    if character.xPosition < 6:
                        return "d"*(6-character.xPosition)
                    if character.xPosition > 6:
                        return "a"*(character.xPosition-6)
                    if character.yPosition < 6:
                        return "s"*(6-character.yPosition)
                    if character.yPosition > 6:
                        return "w"*(character.yPosition-6)
                else:
                    pos = (character.container.xPosition,character.container.yPosition)
                    if pos == (self.cityLocation[0]+1,self.cityLocation[1]):
                        return "15a"
                    if pos == (self.cityLocation[0]-1,self.cityLocation[1]):
                        return "15d"
                    if pos == (self.cityLocation[0]+1,self.cityLocation[1]-1):
                        return "15s"
                    if pos == (self.cityLocation[0]-1,self.cityLocation[1]-1):
                        return "15s"
                    if pos == (self.cityLocation[0]+1,self.cityLocation[1]-2):
                        return "15s"
                    if pos == (self.cityLocation[0]-1,self.cityLocation[1]-2):
                        return "15s"
                    if pos == (self.cityLocation[0],self.cityLocation[1]-2):
                        return localRandom.choice(["15a","15d"])
                    if pos == (self.cityLocation[0],self.cityLocation[1]-3):
                        return "15s"

                    directions = ["w","a","s","d"]
                    if character.container.xPosition < self.cityLocation[0]:
                        directions.extend(["d"]*(self.cityLocation[0]-character.container.xPosition))
                    if character.container.xPosition > self.cityLocation[0]:
                        directions.extend(["a"]*(character.container.xPosition-self.cityLocation[0]))
                    if character.container.yPosition < self.cityLocation[1]:
                        directions.extend(["s"]*(self.cityLocation[1]-character.container.yPosition))
                    if character.container.yPosition > self.cityLocation[1]:
                        directions.extend(["w"]*(character.container.yPosition-self.cityLocation[1]))
                    direction = localRandom.choice(directions)
                    return "13"+direction
            else:
                self.triggerCompletionCheck(character)
        else:
            if isinstance(character.container, src.terrains.Terrain):
                characterTerrainPos = (character.container.xPosition,character.container.yPosition)

                if character.xPosition%15 < 7:
                    if realRun:
                        self.centerFailCounter += 1
                    if self.centerFailCounter < 10:
                        return "."+"d"*(7-character.xPosition%15)
                    else:
                        self.centerFailCounter = 0
                        return "20"+random.choice(("a","w","s","d",))
                if character.xPosition%15 > 7:
                    if realRun:
                        self.centerFailCounter += 1
                    if self.centerFailCounter < 10:
                        return "."+"a"*(character.xPosition%15-7)
                    else:
                        self.centerFailCounter = 0
                        return "20"+random.choice(("a","w","s","d",))
                if character.yPosition%15 < 7:
                    if realRun:
                        self.centerFailCounter += 1
                    if self.centerFailCounter < 10:
                        return "."+"s"*(7-character.yPosition%15)
                    else:
                        self.centerFailCounter = 0
                        return "20"+random.choice(("a","w","s","d",))
                if character.yPosition%15 > 7:
                    if realRun:
                        self.centerFailCounter += 1
                    if self.centerFailCounter < 10:
                        return "."+"w"*(character.yPosition%15-7)
                    else:
                        self.centerFailCounter = 0
                        return "20"+random.choice(("a","w","s","d",))
                self.centerFailCounter = 0

                directions = []
                if character.xPosition//15 > self.cityLocation[0]:
                    directions.extend(["a"]*(character.xPosition//15-self.cityLocation[0]))
                if character.xPosition//15 < self.cityLocation[0]:
                    directions.extend(["d"]*(self.cityLocation[0]-character.xPosition//15))
                if character.yPosition//15 > self.cityLocation[1]:
                    directions.extend(["w"]*(character.yPosition//15-self.cityLocation[1]))
                if character.yPosition//15 < self.cityLocation[1]:
                    directions.extend(["s"]*(self.cityLocation[1]-character.yPosition//15))

                if not directions:
                    return None

                direction = localRandom.choice(directions)
                commandString = ".13"+direction
                if 1==1 or not len(directions) == 2:
                    commandString += ".gg."
                return commandString
            else:
                return None

    def solver(self, character):
        commandString = self.getSolvingCommandString(character,realRun=True)
        self.randomSeed = random.randint(1,2000000)
        if commandString:
            character.runCommandString(commandString)
            return False
        else:
            return True

class delObtainSpecialItem(MetaQuestSequence):

    hasParams = True

    def __init__(self, description="obtain special item", creator=None, lifetime=None, paranoid=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.homePos = None
        self.itemID = None
        self.itemLocation = None
        self.didDelegate = False
        self.didItemCheck = False
        self.addedSubQuests = False
        self.resetDelegations = False
        self.initialLifetime = lifetime
        self.paranoid = paranoid
        self.strategy = None

        # save initial state and register
        self.type = "ObtainSpecialItem"
    
        self.attributesToStore.extend([
            "itemID","didDelegate","didItemCheck","addedSubQuests",
            "resetDelegations","initialLifetime","paranoid","strategy"])
        self.tuplesToStore.append("itemLocation")

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"itemLocation","type":"coordinate"})
        parameters.append({"name":"itemID","type":"int"})
        return parameters

    def triggerCompletionCheck(self,character=None):
        if not self.addedSubQuests:
            return
        super().triggerCompletionCheck()

    def getOptionalParameters(self):
        result = super().getOptionalParameters()
        result.append({"name":"avoidEnemies","type":"bool","default":None})
        return result

    def setParameters(self,parameters):
        if "itemLocation" in parameters and "itemID" in parameters:
            self.setToObtain(parameters["itemID"],parameters["itemLocation"])
        if "lifetime" in parameters:
            self.initialLifetime = parameters["lifetime"]
        super().setParameters(parameters)

    def setToObtain(self, itemID, itemLocation):
        self.itemID = itemID
        self.itemLocation = itemLocation
        self.metaDescription = "obtain special item #%s from %s"%(self.itemID,self.itemLocation)
        self.didDelegate = False

    def activate(self):
        return super().activate()

    def generateSubquests(self,character,strategy=None):
        if self.addedSubQuests and not len(self.subQuests):
            self.fail()
            return False
        if not self.addedSubQuests:
            if character.rank < 6 and not strategy == "attack enemy city":
                quest = src.quests.questMap["BeUsefull"]()
                self.addQuest(quest)

                quest = src.quests.questMap["Equip"](lifetime=400)
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)

            else:
                if character.rank < 6:
                    self.paranoid = True

                if strategy == "fortify base":
                    quest = src.quests.questMap["BeUsefull"]()
                    quest.assignToCharacter(character)
                    quest.activate()
                    self.addQuest(quest)

                    character.revokeReputation(amount=10,reason="not participating in the attack")

                    self.addedSubQuests = True
                    return

                #quest = src.quests.questMap["StandAttention"]()
                #self.addQuest(quest)
                homeLocation = (character.registers["HOMEx"],character.registers["HOMEy"])
                homeLocationTerrain = (character.registers["HOMETx"],character.registers["HOMETy"])

                # order is reverse to order in code

                # return the loot
                quest = DeliverSpecialItem()
                self.addQuest(quest)
                quest.itemID = self.itemID

                quest = src.quests.questMap["GoToTile"]()
                quest.setParameters({"targetPosition":(homeLocation[0],homeLocation[1]+1)})
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)

                quest = src.quests.questMap["GoHome"](paranoid=self.paranoid)
                self.addQuest(quest)

                quest = src.quests.questMap["GoToTile"](paranoid=self.paranoid)
                quest.setParameters({"targetPosition":(self.itemLocation[0],self.itemLocation[1]-3)})
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)

                lifetime = None
                if self.initialLifetime:
                    lifetime = self.initialLifetime//2

                # grab the item
                quest = src.quests.questMap["GrabSpecialItem"](lifetime=lifetime)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                quest.itemID = self.itemID

                # enter the city
                quest = src.quests.questMap["EnterEnemyCity"](lifetime=lifetime)
                self.addQuest(quest)
                quest.setCityLocation(self.itemLocation)
                quest.assignToCharacter(character)
                quest.activate()

                # enter the city
                quest = src.quests.questMap["GoToTile"](lifetime=lifetime,paranoid=self.paranoid)
                quest.setParameters({"targetPosition":(self.itemLocation[0],self.itemLocation[1])})
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)

                # go near enemy city
                quest = src.quests.questMap["GoToTile"](lifetime=lifetime,paranoid=self.paranoid)
                quest.setParameters({"targetPosition":(self.itemLocation[0],self.itemLocation[1]-3)})
                quest.assignToCharacter(character)
                quest.activate()
                quest.reputationReward = 30
                self.addQuest(quest)

                # leave city
                quest = src.quests.questMap["GoToTile"](lifetime=lifetime,paranoid=False)
                quest.setParameters({"targetPosition":(homeLocation[0],homeLocation[1]-2)})
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)

                quest = src.quests.questMap["Equip"](lifetime=300)
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)

            self.addedSubQuests = True

    def solver(self, character):
        if character.rank < 6:
            if self.didDelegate:
                self.generateSubquests(character)
                return super().solver(character)

            if character.rank == 5:
                strategy = character.freeWillDecison(["delegate attack","attack enemy city","fortify base"],(3,1,1))[0]
            elif character.rank == 4:
                strategy = character.freeWillDecison(["delegate attack","attack enemy city","fortify base"],(8,1,1))[0]
            elif character.rank == 3:
                strategy = character.freeWillDecison(["delegate attack","attack enemy city","fortify base"],(12,1,1))[0]
            else:
                strategy = "unknown"

            if strategy == "attack enemy city":
                command = ".QSNEquip\nlifetime:300; ."
                character.runCommandString(command)

                command = ".QSNProtectSuperior\n ."
                character.runCommandString(command)

                self.didDelegate = True
                self.generateSubquests(character,strategy=strategy)

                return False

            command = ".QSNObtainSpecialItem\n%s\n%s,%s\nlifetime:%s; ."%(self.itemID,self.itemLocation[0],self.itemLocation[1],self.initialLifetime,)
            character.runCommandString(command)

            if not character.rank < 4:
                command = ".QSNBeUsefull\nlifetime:%s; ."%(self.initialLifetime,)
                character.runCommandString(command)

            self.metaDescription = "obtain special item #%s from %s (delegated)"%(self.itemID,self.itemLocation)
            self.didDelegate = True
        else:
            if not self.strategy:
                self.strategy = character.freeWillDecison(["attack enemy city","fortify base"],(2,1))[0]

            self.generateSubquests(character,strategy=self.strategy)
            return super().solver(character)

        return False

"""
dummy quest
"""
class delDummyQuest(Quest):
    """
    state initialization
    """

    def __init__(self, description="dummy quest", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.description = description

        # save initial state and register
        self.type = "DummyQuest"

    """
    never complete
    """

    def triggerCompletionCheck(self,character=None):
        return

# map strings to Classes
questMap = {
    "Quest": Quest,
    #"EnterEnemyCity": EnterEnemyCity,
    "MetaQuestSequence": MetaQuestSequence,
    #"MetaQuestParralel": MetaQuestParralel,
    #"NaiveMoveQuest": NaiveMoveQuest,
    #"NaiveEnterRoomQuest": NaiveEnterRoomQuest,
    #"NaivePickupQuest": NaivePickupQuest,
    #"NaiveGetQuest": NaiveGetQuest,
    #"NaiveGetReward": NaiveGetReward,
    #"NaiveMurderQuest": NaiveMurderQuest,
    #"NaiveActivateQuest": NaiveActivateQuest,
    #"NaiveDropQuest": NaiveDropQuest,
    #"NaiveDelegateQuest": NaiveDelegateQuest,
    #"WaitForDeactivationQuest": WaitForDeactivationQuest,
    #"WaitForQuestCompletion": WaitForQuestCompletion,
    #"DrinkQuest": DrinkQuest,
    #"SurviveQuest": SurviveQuest,
    #"EnterRoomQuestMeta": EnterRoomQuestMeta,
    #"MoveQuestMeta": MoveQuestMeta,
    #"DropQuestMeta": DropQuestMeta,
    #"PickupQuestMeta": PickupQuestMeta,
    #"ActivateQuestMeta": ActivateQuestMeta,
    #"RefillDrinkQuest": RefillDrinkQuest,
    #"CollectQuestMeta": CollectQuestMeta,
    #"GetQuest": GetQuest,
    #"GetReward": GetReward,
    #"MurderQuest": MurderQuest,
    #"FillPocketsQuest": FillPocketsQuest,
    #"LeaveRoomQuest": LeaveRoomQuest,
    #"ExamineQuest": ExamineQuest,
    #"FetchFurniture": FetchFurniture,
    #"PlaceFurniture": PlaceFurniture,
    #"ConstructRoom": ConstructRoom,
    #"TransportQuest": TransportQuest,
    #"StoreCargo": StoreCargo,
    #"MoveToStorage": MoveToStorage,
    #"HandleDelivery": HandleDelivery,
    #"KeepFurnacesFiredMeta": KeepFurnacesFiredMeta,
    #"KeepFurnaceFiredMeta": KeepFurnaceFiredMeta,
    #"FireFurnaceMeta": FireFurnaceMeta,
    #"FillGrowthTankMeta": FillGrowthTankMeta,
    #"HopperDuty": HopperDuty,
    #"ClearRubble": ClearRubble,
    #"RoomDuty": RoomDuty,
    #"Serve": Serve,
    #"DummyQuest": DummyQuest,
    #"ObtainSpecialItem": ObtainSpecialItem,
    #"ObtainAllSpecialItems": ObtainAllSpecialItems,
    #"EnterEnemyCity": EnterEnemyCity,
    #"DeliverSpecialItem": DeliverSpecialItem,
    #"GatherItems": GatherItems,
    #"GrabSpecialItem": GrabSpecialItem,
    #"StandAttention": StandAttention,
    "TeleportToTerrain": TeleportToTerrain,
    #"LootRuin": LootRuin,
    #"DestroyRooms": DestroyRooms,
    #"DestroyRoom": DestroyRoom,
    #"DefendBase": DefendBase,
    #"BreakSiege": BreakSiege,
    #"ControlBase": ControlBase,
    #"AssignStaff": AssignStaff,
}

def addType(toRegister):
    """
    add a item type to the item map
    This is used to be able to store the item classes without knowing where everything exactly is.
    Each item needs to actively register here or it will not be available.
    """
    questMap[toRegister.type] = toRegister


def getQuestFromState(state):
    """
    get quest instance from state dict

    Parameters:
        state: the state to load
    Returns:
        the quest
    """

    quest = questMap[state["type"]]()
    quest.setState(state)
    src.saveing.loadingRegistry.register(quest)
    return quest
