"""
quests and quest related code

"""

import random
import time

import src.cinematics
import src.events
import src.gamestate
import src.interaction

# HACK: common variables with modules
mainChar = None


"""
the base class for all quests
"""
class Quest:
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

        self.lifetime = lifetime
        self.lifetimeEvent = None
        self.startTick = src.gamestate.gamestate.tick

        # set id
        self.id = str(random.random())+str(time.time())
        self.reroll()

        self.shortCode = "?"

    def callIndirect(self, callback, extraParams={}):
        """
        call a callback that is stored in a savable format

        Parameters:
            callback: the callback to call
            extraParams: some additional parameters
        """

        if not isinstance(callback, dict):
            # bad code: direct function calls are deprecated, but not completely removed
            callback()
        else:
            if "container" not in callback:
                return
            container = callback["container"]
            function = getattr(container, callback["method"])

            if "params" in callback:
                callback["params"].update(extraParams)
                function(callback["params"])
            else:
                function()

    def callIndirect(self, callback, extraParams={}):
        """
        call a callback that is stored in a savable format

        Parameters:
            callback: the callback to call
            extraParams: some additional parameters
        """

        if not isinstance(callback, dict):
            # bad code: direct function calls are deprecated, but not completely removed
            callback()
        else:
            if "container" not in callback:
                return
            container = callback["container"]
            function = getattr(container, callback["method"])

            if "params" in callback:
                callback["params"].update(extraParams)
                function(callback["params"])
            else:
                function()

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
        deregister callback from being notified if an event occurs

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
        self.changed("failed",{"reason":reason,"quest":self})
        if reason and self.character:
            self.character.addMessage(f"failed quest {self.description} because of {reason}")
        if self.failTrigger:
            self.failTrigger()
        if self.reputationReward:
            self.reputationReward *= -2
        self.postHandler()

    def handleTimeOut(self):
        self.fail()

    def render(self,depth=0,cursor=None,sidebared=False):
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

        # save state and register
        self.type = "MetaQuestSequence"

    def postHandler(self):
        for quest in self.subQuests:
            quest.postHandler()
        super().postHandler()

    def render(self,depth=0,cursor=None,sidebared=False):
        description = [self.description]

        #if not depth == 0 and sidebared:
        #    description = ["..."]

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

            numIndents = depth + 1
            """
            if sidebared:
                numIndents = 1
                if not quest.subQuests and quest.active:
                    numIndents = 2
            """
            numSpaces = 4
            if sidebared:
                numSpaces = 1
            description.append(["\n"]+[" "*numSpaces*numIndents]+quest.render(depth=depth+1,cursor=newCursor,sidebared=sidebared))
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

        if self.subQuests:
            subQuest = self.subQuests[0]
            if not subQuest.active:
                subQuest.activate()
                return
            if subQuest.character != self.character:
                subQuest.assignToCharacter(self.character)
                return

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
        if addFront and len(self.subQuests) > 1:
            self.subQuests[1].deactivate()

    """
    activate self and first subquest
    """

    def activate(self):
        if len(self.subQuests) and not self.subQuests[0].active:
            self.subQuests[0].activate()
        super().activate()

    """
    forward solver from first subquest
    """

    def solver(self, character):
        # remove completed quests
        while self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

        if self.triggerCompletionCheck(character):
            return

        if self.subQuests:
            subQuest = self.subQuests[0]
            if not subQuest.active:
                subQuest.activate()
                return
            if subQuest.character != character:
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
        if len(self.subQuests) and self.subQuests[0].active:
            self.subQuests[0].deactivate()
        super().deactivate()

    def getSolvingCommandString(self,character,dryRun=True):
        if self.subQuests:
            commandString = self.subQuests[0].getSolvingCommandString(character,dryRun=dryRun)
            if commandString:
                return commandString
        return super().getSolvingCommandString(character)

# map strings to Classes
questMap = {
    "Quest": Quest,
    "MetaQuestSequence": MetaQuestSequence,
}

def addType(toRegister):
    """
    add a item type to the item map
    This is used to be able to store the item classes without knowing where everything exactly is.
    Each item needs to actively register here or it will not be available.
    """
    questMap[toRegister.type] = toRegister
