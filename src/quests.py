"""
quests and quest related code

"""

# import basic libs
import json
import random
import uuid
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


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IMPORTANT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# quests below the point are not in use and need to be reintegrated
# this will require heavy rewrites, so please ignore unless you plan to rewrite
# the last few lines of this file are in use

############################################################
#
#   building block quests
#   not intended for direct use unless you know what you are doing
#
############################################################

"""
the base class for all quests
"""


class Quest(src.saveing.Saveable):
    """
    straightforward state initialization
    """

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

    def triggerCompletionCheck(self):

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

    def fail(self):
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

        if self.active:
            description = ["> "]+description
        elif self.completed:
            description = ["X "]+description
        else:
            description = ["x "]+description

        if cursor == None:
            color = "#fff"
        elif cursor == []:
            color = "#0f0"
        else:
            color = "#070"

        counter = 0
        for quest in self.subQuests:
            if cursor and counter == cursor[0]:
                newCursor = cursor[1:]
            else:
                newCursor = None

            description.append(["\n"]+["     "*(depth+1)]+quest.render(depth=depth+1,cursor=newCursor))
        return [[(src.interaction.urwid.AttrSpec(color, "default"), description)]]

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

    def triggerCompletionCheck(self):

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
            if self.triggerCompletionCheck():
                return

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
        super().getSolvingCommandString(character)

class ClearTerrain(MetaQuestSequence):
    def __init__(self, description="clear terrain", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "ClearTerrain"

    def generateTextDescription(self):
        text = """
Clear the whole terrain from enemies.

Just clear the whole terrain tile for tile.
"""

    def triggerCompletionCheck(self,character=None):
        if not character:
            return
        if not character.container:
            return

        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain = character.container

        for otherChar in terrain.characters:
            if otherChar.faction == character.faction:
                continue
            return
        for room in terrain.rooms:
            for otherChar in room.characters:
                if otherChar.faction == character.faction:
                    continue
                return

        super().triggerCompletionCheck()
        return False

    def solver(self, character):
        if len(self.subQuests):
            return super().solver(character)
        else:
            self.triggerCompletionCheck(character)

            if character.yPosition%15 == 14:
                character.runCommandString("w")
                return
            if character.yPosition%15 == 0:
                character.runCommandString("s")
                return
            if character.xPosition%15 == 14:
                character.runCommandString("a")
                return
            if character.xPosition%15 == 0:
                character.runCommandString("d")
                return

            if isinstance(character.container,src.rooms.Room):
                terrain = character.container.container
            else:
                terrain = character.container

            steps = ["clearOutside","clearRooms"]
            if random.random() < 0.3:
                steps = ["clearRooms","clearOutside"]

            for step in steps:
                if step == "clearRooms":
                    for otherChar in terrain.characters:
                        if otherChar.faction == character.faction:
                            continue
                        quest = src.quests.SecureTile(toSecure=(otherChar.xPosition//15,otherChar.yPosition//15),endWhenCleared=True)
                        quest.assignToCharacter(character)
                        quest.activate()
                        self.addQuest(quest)
                        return
                if step == "clearOutside":
                    for room in terrain.rooms:
                        for otherChar in room.characters:
                            if otherChar.faction == character.faction:
                                continue
                            self.addQuest(src.quests.SecureTile(toSecure=room.getPosition(),endWhenCleared=True))
                            return

class DestroyRoom(MetaQuestSequence):
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
                self.addQuest(src.quests.RunCommand(command=13*command))
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

class ControlBase(MetaQuestSequence):
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

class PrepareAttack(MetaQuestSequence):
    def __init__(self, description="prepare attack", creator=None, command=None, lifetime=None, targetPosition=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "PrepareAttack"
        self.shortCode = "P"
        self.targetPosition = targetPosition

    def generateTextDescription(self):
        (numCharges,discard,numItemsOnFloor) = self.getTrapInfo(self.character)
        numGuards = len(self.getGuards(self.character))
        text = """
When you destroy the hive the hive guards will become agitated.
This means they will start to attack everybody on this terrain.
Likely that means a wave of insects is rushing at the base.
This can overwhelm the bases defences and cause damage.

Before starting the attack prepare for that wave.
Ensure the trap rooms are maintaned to kill the incoming guards.
Destroying the hive will agitate hive guards within a distance of 3 tiles.
Killing those insects before killing the hive will reduce the waves size.
So you have two ways you can prepare for the wave.

This quest will end when you have prepared enough.
Your current prepardness score is %s, bring it to below 0.


The formula for the preparedness score is:
    10*numGuards-numCharges+numItemsOnFloor*20 = 10*%s-%s+%s*20 = %s"""%(self.getPreparednessScore(self.character),numGuards,numCharges,numItemsOnFloor,self.getPreparednessScore(self.character),)
        text += """



This quest works a bit different to previous quests.
It can handle mutiple subquests at once.
The idea is to issue orders to the NPCs to mainain the traps and
Attack the hive guards while you are waiting for the work complete.
"""
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return 

        foundSpawner = False
        terrain = character.getTerrain()
        rooms = terrain.getRoomByPosition(self.targetPosition)
        for room in rooms:
            items = room.getItemByPosition((6,6,0))
            for item in items:
                if isinstance(item, src.items.itemMap["MonsterSpawner"]) and not item.disabled:
                    foundSpawner = True

        if not foundSpawner:
            self.postHandler()
            return True

        # end when preparedness reached
        if self.getPreparednessScore(character) < 0:
            self.postHandler()
            return True
        return False

    def getPreparednessScore(self,character):
        numGuards = len(self.getGuards(character))
        (numCharges,discard,numItemsOnFloor) = self.getTrapInfo(character)
        rating = 10*numGuards-numCharges+numItemsOnFloor*20
        return rating

    def getTrapInfo(self,character):
        terrain = character.getTerrain()
        numCharges = 0
        maxCharges = 0
        numItemsOnFloor = 0
        for room in terrain.rooms:
            if not isinstance(room,src.rooms.TrapRoom):
                continue
            numCharges += room.electricalCharges
            maxCharges += room.maxElectricalCharges

            for item in room.itemsOnFloor:
                if item.bolted:
                    continue
                if item.getPosition() == (None,None,None):
                    continue
                numItemsOnFloor += 1
        return (numCharges,maxCharges,numItemsOnFloor)

    def getGuards(self,character):
        terrain = character.getTerrain()
        guards = []
        for otherChar in terrain.characters:
            if not otherChar.faction == "invader":
                continue

            distance = otherChar.getBigDistance(self.targetPosition)
            if distance > 3:
                continue
            if not otherChar.tag == "hiveGuard":
                continue
            guards.append(otherChar)

        for room in terrain.rooms:
            if not otherChar.faction == "invader":
                continue

            distance = room.getDistance(self.targetPosition)
            if distance > 3:
                continue
            if not otherChar.tag == "hiveGuard":
                continue
            guards.append(otherChar)
        return guards

    def solver(self, character):
        self.triggerCompletionCheck(character)

        if not self.subQuests:
            (numCharges,numMaxCharges,numItemsOnFloor) = self.getTrapInfo(character)
            guards = self.getGuards(character)

            if guards:
                toSecure = []
                for guard in guards:
                    pos = guard.getBigPosition()
                    if pos in toSecure:
                        continue
                    toSecure.append(pos)
                self.addQuest(SecureTiles(toSecure=toSecure))
            if numItemsOnFloor > 0:
                self.addQuest(CleanTraps())
            if numCharges < numMaxCharges:
                self.addQuest(ReloadTraps())
            return

        # remove completed quests
        toRemove = []
        for quest in self.subQuests:
            if quest.completed:
                toRemove.append(quest)
        for quest in toRemove:
            self.subQuests.remove(quest)

        for subQuest in self.subQuests:
            if not subQuest.active:
                subQuest.activate()
                return
            if not (subQuest.character == character):
                subQuest.assignToCharacter(character)
                return
            if subQuest.isPaused():
                continue
            subQuest.solver(character)
            return
        character.runCommandString("10.")

class ManageBase(MetaQuestSequence):
    def __init__(self, description="manage base", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "ManageBase"
        self.shortCode = "M"

        self.addQuest(ReloadTraps())
        self.addQuest(CleanTraps())

    def solver(self, character):
        return super().solver(character)

class ReloadTraproom(MetaQuestSequence):
    def __init__(self, description="reload traproom", creator=None, command=None, lifetime=None, targetPosition=None, noDelegate=False):
        super().__init__(creator=creator, lifetime=lifetime)
        self.baseDescription = description
        self.metaDescription = self.baseDescription+" %s"%(targetPosition,)
        self.type = "ReloadTraproom"
        self.shortCode = "R"

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

        self.tuplesToStore.append("targetPosition")

        self.timesDelegated = 0
        self.noDelegate = noDelegate

    def generateTextDescription(self):
        text = """
Reload the trap room on tile %s."""
        if self.character.rank == 3:
            text = """
Ensure that the trap room on %s is reloaded.

Since you are the commander of the base you can make other people do it.
Send the rank 5-6 NPCs and proceed to do something else in the meantime.


You can send NPCs to do tasks in rooms by using the room menu.
It work like this:
* go to the room
* press r to open room menu
* press o to issue command for this room
* press t to issue the order to reload the trap room.
* select the group to execute the order

After you do this the NPCs should stop what they are doing and start working on the new order.
If the task is not completed after some time, reload the trap room yourself.
Use the shockers in the trap room for this.
"""%(self.targetPosition,)
        else:
            text = """
Reload the trap room on %s.

Do this by using the shockers in the trap rooms.
Activate the shockers with lightning rods in your inventory.

This will reload the trap room and consume the lightning rods.
"""%(self.targetPosition,)
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return 

        if self.getRoomCharged(character):
            super().triggerCompletionCheck()
            return

        return

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
            self.metaDescription = self.baseDescription+" %s"%(self.targetPosition,)
        return super().setParameters(parameters)

    def solver(self, character):
        self.triggerCompletionCheck(character=character)

        if not self.subQuests:
            if (not self.noDelegate) and character.rank == 3 and self.timesDelegated < 2:
                if not (character.getBigPosition() == (self.targetPosition[0],self.targetPosition[1],0)):
                    quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                    self.addQuest(quest)
                    return

                if not isinstance(character.container,src.rooms.Room):
                    if character.yPosition%15 == 14:
                        character.runCommandString("w")
                        return
                    if character.yPosition%15 == 0:
                        character.runCommandString("s")
                        return
                    if character.xPosition%15 == 14:
                        character.runCommandString("a")
                        return
                    if character.xPosition%15 == 0:
                        character.runCommandString("d")
                        return

                quest = src.quests.questMap["WaitQuest"](lifetime=200, creator=self)
                quest.assignToCharacter(character)
                self.addQuest(quest, addFront=False)
                quest = src.quests.RunCommand(command="rot"+9*"s"+"j",description="send clones to reload trap room")
                quest.activate()
                quest.assignToCharacter(character)
                self.addQuest(quest)

                self.timesDelegated += 1
                return

            if not isinstance(character.container,src.rooms.Room):
                if character.yPosition%15 == 14:
                    character.runCommandString("w")
                    return
                if character.yPosition%15 == 0:
                    character.runCommandString("s")
                    return
                if character.xPosition%15 == 14:
                    character.runCommandString("a")
                    return
                if character.xPosition%15 == 0:
                    character.runCommandString("d")
                    return

            terrain = character.getTerrain()

            rooms = terrain.getRoomByPosition(self.targetPosition)
            room = None
            if rooms:
                room = rooms[0]

            if not room == character.container:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                self.addQuest(quest)
                return

            character.addMessage("should recharge now")

            foundCharger = None
            for item in room.itemsOnFloor:
                if not item.bolted:
                    continue
                if not item.type == "Shocker":
                    continue
                foundCharger = item

            if character.inventory and character.inventory[-1].type == "LightningRod":
                chargerPos = foundCharger.getPosition()
                characterPos = character.getPosition()
                if chargerPos == (characterPos[0]-1,characterPos[1],characterPos[2]):
                    quest = src.quests.questMap["RunCommand"](command=10*"Ja")
                    quest.activate()
                    self.addQuest(quest)
                elif chargerPos == (characterPos[0]+1,characterPos[1],characterPos[2]):
                    quest = src.quests.questMap["RunCommand"](command=10*"Jd")
                    quest.activate()
                    self.addQuest(quest)
                elif chargerPos == (characterPos[0],characterPos[1]-1,characterPos[2]):
                    quest = src.quests.questMap["RunCommand"](command=10*"Jw")
                    quest.activate()
                    self.addQuest(quest)
                elif chargerPos == (characterPos[0],characterPos[1]+1,characterPos[2]):
                    quest = src.quests.questMap["RunCommand"](command=10*"Js")
                    quest.activate()
                    self.addQuest(quest)
                else:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=foundCharger.getPosition(),ignoreEndBlocked=True)
                    quest.activate()
                    quest.assignToCharacter(character)
                    self.addQuest(quest)
                return

            if character.getFreeInventorySpace() < 1:
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                quest.activate()
                quest.assignToCharacter(character)
                self.addQuest(quest)
                return

            if foundCharger:
                source = None
                for sourceCandidate in random.sample(list(room.sources),len(room.sources)):
                    if not sourceCandidate[1] == "LightningRod":
                       continue 

                    sourceRoom = room.container.getRoomByPosition(sourceCandidate[0])
                    if not sourceRoom:
                        continue

                    sourceRoom = sourceRoom[0]
                    if not sourceRoom.getNonEmptyOutputslots(itemType=sourceCandidate[1]):
                        continue

                    source = sourceCandidate
                if source:
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=foundCharger.getPosition(),ignoreEndBlocked=True))
                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                    self.addQuest(src.quests.questMap["FetchItems"](toCollect="LightningRod"))
                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=source[0]))
                    return

        super().solver(character)

    def getRoomCharged(self,character):
        
        terrain = character.getTerrain()

        rooms = terrain.getRoomByPosition(self.targetPosition)
        room = None
        if rooms:
            room = rooms[0]

        try:
            if room.electricalCharges < room.maxElectricalCharges:
                return False
            return True
        except:
            pass

        return False

class ReloadTraps(MetaQuestSequence):
    def __init__(self, description="reload traps", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "ReloadTraps"
        self.shortCode = "R"

    def generateTextDescription(self):
        text = """
Reload all trap rooms.

Trap rooms that need to be reloaded:

"""
        for traproom in self.getUnfilledTrapRooms(self.character):
            text += str(traproom.getPosition())+"\n"
        return text

    def triggerCompletionCheck(self,character=None):

        if not character:
            return 

        if not self.getUnfilledTrapRooms(character):
            super().triggerCompletionCheck()
            return

        return

    def getUnfilledTrapRooms(self,character):
        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain = character.container

        foundTraprooms = []
        for room in terrain.rooms:
            if not isinstance(room,src.rooms.TrapRoom):
                continue

            if room.electricalCharges > room.maxElectricalCharges-30:
                continue

            foundTraprooms.append(room)
        
        return foundTraprooms

    def solver(self, character):
        self.triggerCompletionCheck(character)

        if self.completed:
            return

        if not self.subQuests:
            room = random.choice(self.getUnfilledTrapRooms(character))
                
            quest = ReloadTraproom(targetPosition=room.getPosition())
            self.addQuest(quest)
            return

        return super().solver(character)

class DefendBase(MetaQuestSequence):
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

class BreakSiege(MetaQuestSequence):
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

class AssignStaff(MetaQuestSequence):
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
                subQuest = GoToTile(targetPosition=(7,7,0))
                self.addQuest(subQuest)
                subQuest.activate()
                subQuest.assignToCharacter(character)
                return

            charPos = character.getPosition()
            if not charPos == (1,2,0):
                subQuest = GoToPosition(targetPosition=(1,2,0))
                self.addQuest(subQuest)
                subQuest.activate()
                subQuest.assignToCharacter(character)
                return

            if not self.generatedCode:
                subQuest = RunCommand(command=list("Jw.sjdjdjaasddddjdjaaaaa")+["esc"])
                self.addQuest(subQuest)
                subQuest.activate()
                subQuest.assignToCharacter(character)
                self.generatedCode = True
                return

        return super().solver(character)

class DestroyRooms(MetaQuestSequence):
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

class EnterRoom(MetaQuestSequence):
    def __init__(self, description="enter room", creator=None, command=None, lifetime=None):
        super().__init__([], creator=creator, lifetime=lifetime)
        self.metaDescription = description

    def generateTextDescription(self):
        return """
Enter the room.

This quest is a workaround quest.
This means it is needed for other quests to work,
but has no purpose on its own.

So just complete the quest and don't think about it too much."""

    def triggerCompletionCheck(self,character=None):
        return

    def enteredRoom(self,character=None):
        self.postHandler()
        return

    def solver(self,character):
        if character.xPosition%15 == 0:
            character.runCommandString("d")
        if character.xPosition%15 == 14:
            character.runCommandString("a")
        if character.yPosition%15 == 0:
            character.runCommandString("s")
        if character.yPosition%15 == 14:
            character.runCommandString("w")

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.enteredRoom, "entered room")

        super().assignToCharacter(character)

class Equip(MetaQuestSequence):
    def __init__(self, description="equip", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.type = "Equip"

        self.shortCode = "e"

    def generateTextDescription(self):
        sword = src.items.itemMap["Sword"]()
        armor = src.items.itemMap["Armor"]()
        return ["""
The world is a dangerous place.
You need to be able to defend yourself.
Equip yourself with weapons preferably a sword (""",sword.render(),""") and armor (""",armor.render(),""").

You can try to find euqipment in storage.
Alternatively fetch your equipment directly from the production line.
If you find some other source for equipment, that is fine, too.

Take care to select a good weapon and armor.
The differences are significant.

Armor can absorb 1 to 5 damage depending on quality.
Swords can range from 10 to 25 damage per hit.
"""]

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def handleMoved(self,extraInfo=None):
        self.subQuestCompleted()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "equipedItem")
        self.startWatching(character,self.handleMoved, "moved")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return 

        if character.armor and character.weapon:
            self.postHandler()
            return

        return

    def clearCompletedSubquest(self):
        while self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

    def subQuestCompleted(self,extraInfo=None):
        self.clearCompletedSubquest() 
        if not self.subQuests:
            self.generateSubquests(self.character)

    def getSolvingCommandString(self,character,dryRun=True):
        offsets = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
        for offset in offsets:
            pos = character.getPosition(offset=offset)
            items = character.container.getItemByPosition(pos)
            if not items:
                continue

            shouldGrab = False
            if not character.armor and items[0].type == "Armor":
                shouldGrab = True
            if not character.weapon and (items[0].type == "Sword" or items[0].type == "Rod"):
                shouldGrab = True

            if not shouldGrab:
                continue

            if offset == (0,0,0):
                return "j"
            if offset == (1,0,0):
                return "Jd"
            if offset == (-1,0,0):
                return "Ja"
            if offset == (0,1,0):
                return "Js"
            if offset == (0,-1,0):
                return "Jw"
        return super().getSolvingCommandString(character,dryRun=dryRun)

    def generateSubquests(self,character):
        toSearchFor = []
        if not character.armor:
            toSearchFor.append("Armor")
        if not character.weapon:
            toSearchFor.append("Sword")
            toSearchFor.append("Rod")
        if not toSearchFor:
            return

        if not isinstance(character.container,src.rooms.Room):
            if character.yPosition%15 == 14 or character.yPosition%15 == 0 or character.xPosition%15 == 14 or character.xPosition%15 == 0:
                quest = EnterRoom()
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                self.startWatching(quest,self.subQuestCompleted,"completed")
                return
                
            self.addQuest(GoHome())
            return
        room = character.container

        for itemType in toSearchFor:
            sourceSlots = room.getNonEmptyOutputslots(itemType=itemType)
            if sourceSlots:
                break

        if not sourceSlots:
            source = None
            for itemType in toSearchFor:
                for candidate in room.sources:
                    if not candidate[1] == itemType:
                        continue

                    sourceRoom = room.container.getRoomByPosition(candidate[0])
                    if not sourceRoom:
                        continue

                    sourceRoom = sourceRoom[0]
                    sourceSlots = sourceRoom.getNonEmptyOutputslots(itemType=itemType)
                    if not sourceSlots:
                        continue

                    source = candidate
                    break
                if source:
                    break
            if not source:
                character.runCommandString(".14.")
                return

            description="go to weapon production "
            if source[0] == (8,9,0):
                description="go storage room "

            quest = GoToTile(targetPosition=source[0],description=description)
            quest.assignToCharacter(character)
            self.startWatching(quest,self.subQuestCompleted,"completed")
            quest.activate()
            self.addQuest(quest)
            return

        characterPos = character.getPosition()
        command = None
        if sourceSlots[0][0] == (characterPos[0],characterPos[1],characterPos[2]):
            command = "j"
        elif sourceSlots[0][0] == (characterPos[0]-1,characterPos[1],characterPos[2]):
            command = "Ja"
        elif sourceSlots[0][0] == (characterPos[0],characterPos[1]-1,characterPos[2]):
            command = "Jw"
        elif sourceSlots[0][0] == (characterPos[0],characterPos[1]+1,characterPos[2]):
            command = "Js"
        elif sourceSlots[0][0] == (characterPos[0],characterPos[1]-1,characterPos[2]):
            command = "Js"

        if command:
            return
        else:
            quest = GoToPosition(targetPosition=sourceSlots[0][0],description="go to "+itemType,ignoreEndBlocked=True)
            quest.assignToCharacter(character)
            quest.activate()
            self.addQuest(quest)
            self.startWatching(quest,self.subQuestCompleted,"completed")
            return

    def solver(self, character):
        self.activate()
        self.triggerCompletionCheck(character)
        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return

        if not self.subQuests:
            command = self.getSolvingCommandString(character,dryRun=False)
            if command:
                character.runCommandString(command)
                return
            
        return super().solver(character)

class RunCommand(MetaQuestSequence):
    def __init__(self, description="press ", creator=None, command=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.command = None
        self.ranCommand = False
        self.metaDescription = description+" "+"".join(command)
        self.type = "RunCommand"

        self.shortCode = "c"

        if command:
            self.setParameters({"command":command})

    def generateTextDescription(self):
        return """
This quest wants you to press the following keys:

%s

To be honest:
This quest is deprecated and should be removed.
If you see this that means that did not happen, yet.
This stuff does not work very well, so just do exactly that.
Do nothing else like moving around.

good luck!
"""%(self.command,)

    def setParameters(self,parameters):
        if "command" in parameters:
            self.command = parameters["command"]
        return super().setParameters(parameters)

    def triggerCompletionCheck(self,character=None):
        if self.ranCommand:
            self.postHandler()
            return

        return

    def getSolvingCommandString(self,character,dryRun=True):
        return self.command

    def solver(self, character):
        self.activate()
        self.triggerCompletionCheck(character)

        if not self.ranCommand:
            character.runCommandString(self.command)
            self.ranCommand = True
        self.triggerCompletionCheck(character)

class ProtectSuperior(MetaQuestSequence):
    def __init__(self, description="protect superior", toProtect=None):
        questList = []
        super().__init__(questList)
        self.metaDescription = description

        self.type = "ProtectSuperior"
        self.lastSuperiorPos = None
        self.delegatedTask = False

    def triggerCompletionCheck(self,character=None):
        return False

    def checkDoRecalc(self,character):
        if not self.lastSuperiorPos == self.getSuperiorsTileCoordinate(character):
            self.clearSubQuests()

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append((self.getSuperiorsTileCoordinate(character),"target"))
        return result

    def getSuperiorsTileCoordinate(self,character):
        return character.superior.getBigPosition()

    def solver(self, character):
        if not (character.superior or character.superior.dead):
            self.fail()
            return True
        
        if self.delegatedTask == False and character.rank < 6:
            command = ".QSNProtectSuperior\n ."
            character.runCommandString(command)
            self.delegatedTask = True
            return

        self.checkDoRecalc(character)

        if self.subQuests:
            return super().solver(character)

        if character.container == character.superior.container and self.getSuperiorsTileCoordinate(character) == character.getBigPosition():
            if character.container.getEnemiesOnTile(character):
                character.runCommandString("gg")
                return
            character.runCommandString("5.")
            return
        
        self.lastSuperiorPos = self.getSuperiorsTileCoordinate(character)
        self.addQuest(GoToTile(targetPosition=self.lastSuperiorPos,paranoid=True))
        return

class DrawFloorPlan(MetaQuestSequence):
    def __init__(self, description="draw floor plan", creator=None, targetPosition=None,toRestock=None,allowAny=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.type = "DrawFloorPlan"
        self.shortCode = "d"

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

    def solver(self, character):
        self.activate()
        self.assignToCharacter(character)
        if self.subQuests:
            return super().solver(character)

        if not character.inventory or not character.inventory[-1].type == "Painter":
            character.addMessage("no painter")
            self.addQuest(src.quests.questMap["FetchItems"](toCollect="Painter",amount=1))
            return
        painter = character.inventory[-1]

        if not isinstance(character.container,src.rooms.Room):
            if character.xPosition%15 == 0:
                character.runCommandString("d")
            if character.xPosition%15 == 14:
                character.runCommandString("a")
            if character.yPosition%15 == 0:
                character.runCommandString("s")
            if character.yPosition%15 == 14:
                character.runCommandString("w")
            return


        if not character.container.floorPlan:
            self.fail()
            return

        if character.container.floorPlan.get("walkingSpace"):
            if not painter.paintMode == "walkingSpace":
                self.addQuest(RunCommand(command="lcmwalkingSpace\nk"))
                return

            walkingSpace = character.container.floorPlan["walkingSpace"].pop()

            if walkingSpace[0] == 0 or walkingSpace[0] == 12 or walkingSpace[1] == 0 or walkingSpace[1] == 12:
                return
            self.addQuest(src.quests.questMap["RunCommand"](command="ljk"))
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=walkingSpace))

            if painter.paintExtraInfo:
                self.addQuest(src.quests.questMap["RunCommand"](command="lcck"))

            return

        if character.container.floorPlan.get("inputSlots"):
            if not painter.paintMode == "inputSlot":
                self.addQuest(src.quests.questMap["RunCommand"](command="lcminputSlot\nk"))
                return

            inputSlot = character.container.floorPlan["inputSlots"][-1]

            if not painter.paintType == inputSlot[1]:
                self.addQuest(src.quest.questMap["RunCommand"](command="lct%s\nk"%(inputSlot[1],)))
                return

            character.container.floorPlan["inputSlots"].pop()

            self.addQuest(src.quests.questMap["RunCommand"](command="ljk"))
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=inputSlot[0]))

            if painter.paintExtraInfo:
                self.addQuest(src.quests.questMap["RunCommand"](command="lcck"))

            return

        if character.container.floorPlan.get("outputSlots"):
            if not painter.paintMode == "outputSlot":
                self.addQuest(src.quests.questMap["RunCommand"](command="lcmoutputSlot\nk"))
                return

            outputSlot = character.container.floorPlan["outputSlots"][-1]

            if not painter.paintType == outputSlot[1]:
                self.addQuest(src.quests.questMap["RunCommand"](command="lct%s\nk"%(outputSlot[1],)))
                return

            character.container.floorPlan["outputSlots"].pop()

            self.addQuest(src.quests.questMap["RunCommand"](command="ljk"))
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=outputSlot[0]))

            if painter.paintExtraInfo:
                self.addQuest(src.quests.questMap["RunCommand"](command="lcck"))

            return

        if character.container.floorPlan.get("storageSlots"):
            if not painter.paintMode == "storageSlot":
                self.addQuest(src.quests.questMap["RunCommand"](command="lcmstorageSlot\nk"))
                return

            storageSlot = character.container.floorPlan["storageSlots"][-1]

            if not painter.paintType == storageSlot[1]:
                self.addQuest(src.quests.questMap["RunCommand"](command="lct%s\nk"%(storageSlot[1],)))
                return
            
            character.container.floorPlan["storageSlots"].pop()

            self.addQuest(src.quests.questMap["RunCommand"](command="ljk"))
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=storageSlot[0]))

            if painter.paintExtraInfo:
                self.addQuest(src.quests.questMap["RunCommand"](command="lcck"))

            return

        if character.container.floorPlan.get("buildSites"):

            buildingSite = character.container.floorPlan["buildSites"][-1]

            character.container.floorPlan["buildSites"].pop()

            self.addQuest(src.quests.questMap["RunCommand"](command="ljk"))
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=buildingSite[0]))

            for (key,value) in buildingSite[2].items():
                valueType = ""
                if key == "command":
                    value = "".join(value)

                if key == "commands":
                    value = json.dumps(value)
                    valueType = "json"

                if key == "settings":
                    value = json.dumps(value)
                    valueType = "json"


                if isinstance(value,int):
                    valueType = "int"

                self.addQuest(src.quests.questMap["RunCommand"](command="lce%s\n%s\n%s\nk"%(key,valueType,value)))

            if not painter.paintMode == "buildSite":
                self.addQuest(src.quests.questMap["RunCommand"](command="lcmbuildSite\nk"))

            if not painter.paintType == buildingSite[1]:
                self.addQuest(src.quests.questMap["RunCommand"](command="lct%s\nk"%(buildingSite[1],)))

            if painter.paintExtraInfo:
                self.addQuest(src.quests.questMap["RunCommand"](command="lcck"))

            return

        character.container.floorPlan = None
        self.postHandler()
        return

class RestockRoom(MetaQuestSequence):
    def __init__(self, description="restock room", creator=None, targetPosition=None,toRestock=None,allowAny=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.toRestock = None
        self.allowAny = allowAny

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})
        if toRestock:
            self.setParameters({"toRestock":toRestock})
        if allowAny:
            self.setParameters({"allowAny":allowAny})
        self.type = "RestockRoom"

        self.shortCode = "r"

    def generateTextDescription(self):
        return """
Restock the room with items from your inventory.
Place the items in the correct input stockpile."""

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
        if "toRestock" in parameters and "toRestock" in parameters:
            self.toRestock = parameters["toRestock"]
        if "allowAny" in parameters and "allowAny" in parameters:
            self.allowAny = parameters["allowAny"]
        return super().setParameters(parameters)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if isinstance(character.container,src.rooms.Room):
            room = character.container

            foundNeighbour = None
            inputSlots = room.getEmptyInputslots(itemType=self.toRestock,allowAny=self.allowAny)
            for slot in inputSlots:
                for direction in ((-1,0),(1,0),(0,-1),(0,1)):
                    neighbour = (slot[0][0]-direction[0],slot[0][1]-direction[1],slot[0][2])
                    if not neighbour in room.walkingSpace:
                        continue
                    foundNeighbour = (neighbour,direction)
                    break
            if not foundNeighbour:
                character.addMessage("no neighbour")
                self.postHandler()
                return

        if not self.getNumDrops(character):
            self.postHandler()
            return
        return

    def getNumDrops(self,character):
        numDrops = 0
        for item in reversed(character.inventory):
            if not item.type == self.toRestock:
                break
            numDrops += 1
        return numDrops

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

    def getSolvingCommandString(self,character,dryRun=True):
        if self.subQuests:
            return super().getSolvingCommandString(character,dryRun=dryRun)

        self.triggerCompletionCheck(character)

        if isinstance(character.container,src.rooms.Room):
            room = character.container

            if not hasattr(room,"inputSlots"):
                return "..23.."

            inputSlots = room.getEmptyInputslots(itemType=self.toRestock,allowAny=self.allowAny)
            random.shuffle(inputSlots)

            # find neighboured input fields
            foundDirectDrop = None
            for direction in ((-1,0),(1,0),(0,-1),(0,1),(0,0)):
                neighbour = (character.xPosition+direction[0],character.yPosition+direction[1],character.zPosition)
                for inputSlot in inputSlots:
                    if neighbour == inputSlot[0]:
                        foundDirectDrop = (neighbour,direction,inputSlot)
                        break

            if foundDirectDrop:
                dropContent = room.getItemByPosition(foundDirectDrop[0])
                if not dropContent or not dropContent[0].type == "Scrap":
                    maxSpace = foundDirectDrop[2][2].get("maxAmount")
                    if not maxSpace:
                        maxSpace = 25
                    if not dropContent:
                        spaceTaken = 0
                    else:
                        spaceTaken = len(dropContent)
                    numToDrop = min(maxSpace-spaceTaken,self.getNumDrops(character))

                    if foundDirectDrop[1] == (-1,0):
                        return "La"*numToDrop
                    if foundDirectDrop[1] == (1,0):
                        return "Ld"*numToDrop
                    if foundDirectDrop[1] == (0,-1):
                        return "Lw"*numToDrop
                    if foundDirectDrop[1] == (0,1):
                        return "Ls"*numToDrop
                    if foundDirectDrop[1] == (0,0):
                        return "l"*numToDrop
                else:
                    if foundDirectDrop[1] == (-1,0):
                        return "Ja"*10
                    if foundDirectDrop[1] == (1,0):
                        return "Jd"*10
                    if foundDirectDrop[1] == (0,-1):
                        return "Jw"*10
                    if foundDirectDrop[1] == (0,1):
                        return "Js"*10
                    if foundDirectDrop[1] == (0,0):
                        return "l"*self.getNumDrops(character)

            foundNeighbour = None
            for slot in inputSlots:
                for direction in ((-1,0),(1,0),(0,-1),(0,1)):
                    neighbour = (slot[0][0]-direction[0],slot[0][1]-direction[1],slot[0][2])
                    if not neighbour in room.walkingSpace:
                        continue
                    foundNeighbour = (neighbour,direction)
                    break
                if foundNeighbour:
                    break

            if not foundNeighbour:
                return "..24.."

            if not dryRun:
                quest = GoToPosition()
                quest.assignToCharacter(character)
                quest.setParameters({"targetPosition":foundNeighbour[0]})
                quest.activate()
                self.addQuest(quest)

                return "."
            return str(foundNeighbour)

        charPos = (character.xPosition%15,character.yPosition%15,character.zPosition%15)
        if charPos == (7,0,0):
            return "s"
        if charPos == (7,14,0):
            return "w"
        if charPos == (0,7,0):
            return "d"
        if charPos == (14,7,0):
            return "a"

    def solver(self, character):
        self.activate()
        self.assignToCharacter(character)
        if self.subQuests:
            return super().solver(character)

        commandString = self.getSolvingCommandString(character,dryRun=False)
        self.reroll()
        if commandString:
            character.runCommandString(commandString)
            return False
        else:
            return True

class GatherScrap(MetaQuestSequence):
    def __init__(self, description="gather scrap", creator=None, targetPosition=None,lifetime=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

        self.tuplesToStore.append("targetPosition")

        self.type = "GatherScrap"

    def generateTextDescription(self):
        scrap1 = src.items.itemMap["Scrap"](amount=1)
        scrap2 = src.items.itemMap["Scrap"](amount=6)
        scrap3 = src.items.itemMap["Scrap"](amount=20)
        return ["""
Fill your inventory with scrap.
Scrap can be found in scrapfields and
looks like this: """,scrap1.render()," or ",scrap2.render()," or ",scrap3.render(),"""


Scrapfields are shown on the minimap as white ss"""]

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
        return super().setParameters(parameters)

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if self.completed:
            return

        if not character:
            return

        if not character.getFreeInventorySpace() < 1:
            return

        if not character.inventory[-1].type == "Scrap":
            return

        self.postHandler()

    def solver(self, character):

        self.triggerCompletionCheck(character)

        if self.subQuests:
            return super().solver(character)

        if character.getFreeInventorySpace() < 1:
            if not character.inventory[-1].type == "Scrap":
                self.addQuest(ClearInventory())
                return

        items = character.container.getItemByPosition(character.getPosition())
        if items:
            if items[-1].type == "Scrap":
                character.runCommandString("k"*min(10-len(character.inventory),items[-1].amount))
                return

        # check for direct scrap
        foundScrap = None
        toCheckFrom = [character.getPosition()]
        pathMap = {toCheckFrom[0]:[]}
        directions = [(-1,0),(1,0),(0,1),(0,-1)]
        while len(toCheckFrom):
            random.shuffle(directions)
            pos = toCheckFrom.pop()
            for direction in directions:
                foundScrap = None

                oldPos = pos
                newPos = (pos[0]+direction[0],pos[1]+direction[1],pos[2])
                if newPos[0]%15 < 1 or newPos[0]%15 > 13 or newPos[1]%15 < 1 or newPos[1]%15 > 13:
                    continue

                items = character.container.getItemByPosition(newPos)
                if items:
                    if items[0].type == "Scrap":
                        foundScrap = (oldPos,newPos,direction)
                        break

                if character.container.getPositionWalkable(newPos) and not newPos in pathMap:
                    toCheckFrom.append(newPos)
                    pathMap[newPos] = pathMap[oldPos]+[direction]
            if foundScrap:
                break

        if not foundScrap:
            room = character.container
            if not isinstance(room,src.rooms.Room):
                return

            source = None
            for potentialSource in random.sample(list(room.sources),len(room.sources)):
                if potentialSource[1] == "rawScrap":
                    source = potentialSource
                    break

            if source == None:
                self.fail()
                return

            quest = GoToTile(targetPosition=(source[0][0],source[0][1],0),description="go to scrap field")
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        command = ""

        for step in pathMap[foundScrap[0]]:
            if step == (-1,0):
                command += "a"
            if step == (1,0):
                command += "d"
            if step == (0,-1):
                command += "w"
            if step == (0,1):
                command += "s"

        if foundScrap[2] == (-1,0):
            pickUpCommand = "Ka"
        if foundScrap[2] == (1,0):
            pickUpCommand = "Kd"
        if foundScrap[2] == (0,1):
            pickUpCommand = "Ks"
        if foundScrap[2] == (0,-1):
            pickUpCommand = "Kw"
        if foundScrap[2] == (0,0):
            pickUpCommand = "k"

        command += pickUpCommand*min(10-len(character.inventory),character.container.getItemByPosition(foundScrap[1])[0].amount)
        character.runCommandString(command)

class CleanTraps(MetaQuestSequence):

    def __init__(self, description="clean traps", creator=None, reputationReward=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reputationReward = reputationReward

        self.type = "CleanTraps"

    def generateTextDescription(self):
        text = """
Clean all trap room.

Items like corpses cluttering the trap rooms are a problem.
The traps work by shocking enemies when they step on the floor.
For this to work they need to directly step onto the floor.
Item lying on the floor prevent that.

So clean all trap rooms.

Trap rooms that need to be cleaned are:

"""
        for traproom in self.getClutteredTraprooms(self.character):
            text += str(traproom.getPosition())+"\n"
        return text

    def triggerCompletionCheck(self,character=None):

        if not character:
            return

        if not self.getClutteredTraprooms(character):
            self.postHandler()
            return True

        return

    def getClutteredTraprooms(self,character):

        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain  = character.container

        filledTraproom = []
        for room in terrain.rooms:
            if isinstance(room,src.rooms.TrapRoom):
                for item in room.itemsOnFloor:
                    if item.bolted:
                        continue
                    if item.getPosition() == (None, None, None):
                        continue
                    filledTraproom.append(room)
                    break
        
        return filledTraproom 

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        if not self.subQuests:
            for room in self.getClutteredTraprooms(character):
                quest = src.quests.ClearTile(targetPosition=room.getPosition())
                quest.activate()
                quest.assignToCharacter(character)
                self.addQuest(quest)

        super().solver(character)

    def postHandler(self):
        if self.reputationReward and self.character:
            text = "cleaning the trap rooms"
            self.character.awardReputation(amount=self.reputationReward, reason=text)
        super().postHandler()

class OperateMachine(MetaQuestSequence):
    def __init__(self, description="operate machine", creator=None, targetPosition=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition

    def handleOperatedMachine(self, extraInfo):
        if self.completed:
            1/0

        if extraInfo["machine"].getPosition() == self.targetPosition:
            self.postHandler()
            return

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.handleOperatedMachine, "operated machine")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        return """
operate the machine on %s
"""%(self.targetPosition,)

    def triggerCompletionCheck(self):
        return False

    def generateSubquests(self,character=None):
        if character == None:
            return

        pos = character.getPosition()
        if not self.targetPosition in (pos,(pos[0],pos[1],pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            self.addQuest(GoToPosition(targetPosition=self.targetPosition,ignoreEndBlocked=True))
            return

    def getSolvingCommandString(self, character, dryRun=True):
        pos = character.getPosition()
        if (pos[0],pos[1],pos[2]) == self.targetPosition:
            return "j"
        if (pos[0]-1,pos[1],pos[2]) == self.targetPosition:
            return "Ja"
        if (pos[0]+1,pos[1],pos[2]) == self.targetPosition:
            return "Jd"
        if (pos[0],pos[1]-1,pos[2]) == self.targetPosition:
            return "Jw"
        if (pos[0],pos[1]+1,pos[2]) == self.targetPosition:
            return "Js"
        super().getSolvingCommandString(character,dryRun=dryRun)

    def solver(self, character):
        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return
        command = self.getSolvingCommandString(character,dryRun=False)
        if command:
            character.runCommandString(command)
            return
        super().solver(character)

class ClearInventory(MetaQuestSequence):
    def __init__(self, description="clear inventory", creator=None, targetPosition=None, returnToTile=True):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.returnToTile = False
        if returnToTile:
            self.setParameters({"returnToTile":returnToTile})

        self.type = "ClearInventory"
        self.tileToReturnTo = None

    def generateTextDescription(self):
        return """
You should clear your inventory.

The storage room is a good place to put your items.
Put the items into the stockpiles to make then accessible to the base.



To see your items open the your inventory by pressing i."""

    def droppedItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def handleTileChange(self):
        self.triggerCompletionCheck(self.character)

    def activate(self):
        if self.character:
            if self.returnToTile and not self.tileToReturnTo:
                self.tileToReturnTo = self.character.getBigPosition()
            self.triggerCompletionCheck(self.character)
        super().activate()

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.droppedItem, "dropped")
        self.startWatching(character,self.handleTileChange, "changedTile")

        if self.active:
            if self.returnToTile and not self.tileToReturnTo:
                self.tileToReturnTo = character.getBigPosition()
            self.triggerCompletionCheck(character)
        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if not character.inventory:
            if self.returnToTile and not character.getBigPosition() == self.tileToReturnTo:
                return
            self.postHandler()
            return
        return

    def solver(self, character):
        self.triggerCompletionCheck(character)

        if self.returnToTile and not self.tileToReturnTo:
            self.tileToReturnTo = character.getBigPosition()

        if not self.subQuests:
            if not isinstance(character.container,src.rooms.Room):
                if character.yPosition%15 == 14:
                    character.runCommandString("w")
                    return
                if character.yPosition%15 == 0:
                    character.runCommandString("s")
                    return
                if character.xPosition%15 == 14:
                    character.runCommandString("a")
                    return
                if character.xPosition%15 == 0:
                    character.runCommandString("d")
                    return


            # clear inventory local
            room = character.getRoom()
            if len(character.inventory) and room:
                emptyInputSlots = room.getEmptyInputslots(character.inventory[-1].type, allowAny=True)
                if emptyInputSlots:
                    quest = RestockRoom(toRestock=character.inventory[-1].type, allowAny=True)
                    self.addQuest(quest)
                    quest.assignToCharacter(character)
                    quest.activate()
                    return True

            if not "HOMEx" in character.registers:
                return True

            if character.inventory:
                homeRoom = character.getHomeRoom()

                if not hasattr(homeRoom,"storageRooms") or not homeRoom.storageRooms:
                    return True
                quest = GoToTile(targetPosition=(homeRoom.storageRooms[0].xPosition,homeRoom.storageRooms[0].yPosition,0))
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return True

            if self.returnToTile and not character.getBigPosition() == self.returnToTile:
                quest = GoToTile(targetPosition=self.tileToReturnTo)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return True

            return False

        super().solver(character)

    def setParameters(self,parameters):
        if "returnToTile" in parameters and "returnToTile" in parameters:
            self.returnToTile = parameters["returnToTile"]
        return super().setParameters(parameters)

class ClearTile(MetaQuestSequence):
    def __init__(self, description="clean tile", creator=None, targetPosition=None, noDelegate=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description

        self.type = "ClearTile"
        self.timesDelegated = 0

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

        self.tuplesToStore.append("targetPosition")
        self.noDelegate = noDelegate

    def generateTextDescription(self):
        if self.character.rank == 3:
            text = """
Ensure that the trap room on %s is cleaned.

Since you are the commander of the base you can make other people do it.
Send the rank 5-6 NPCs and proceed to do something else in the meantime.

You can send NPCs to do tasks in rooms by using the room menu.
It work like this:
* go to the room
* press r to open room menu
* press o to issue command for this room
* press c for issuing the order to clean traps
* select the group to execute the order

After you do this the NPCs should stop what they are doing and start working on the new order.
If the task is not completed after some time, reload the trap room yourself.
Use the shockers in the trap room for this."""%(self.targetPosition,)
        else:
            text = """
Clean the room on tile %s.

Remove all items from the walkways."""%(self.targetPosition,)
        return text

    def triggerCompletionCheck(self,character=None):

        if not character:
            return

        if not self.getLeftoverItems(character):
            self.postHandler()
            return

        return

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
            self.metaDescription = self.baseDescription+" "+str(self.targetPosition)
        return super().setParameters(parameters)

    def solver(self, character):
        self.triggerCompletionCheck(character=character)

        if not self.subQuests:
            if (not self.noDelegate) and character.rank == 3 and self.timesDelegated < 2:
                if not (character.getBigPosition() == (self.targetPosition[0],self.targetPosition[1],0)):
                    quest = src.quests.GoToTile(targetPosition=self.targetPosition)
                    self.addQuest(quest)
                    return

                if not isinstance(character.container,src.rooms.Room):
                    if character.yPosition%15 == 14:
                        character.runCommandString("w")
                        return
                    if character.yPosition%15 == 0:
                        character.runCommandString("s")
                        return
                    if character.xPosition%15 == 14:
                        character.runCommandString("a")
                        return
                    if character.xPosition%15 == 0:
                        character.runCommandString("d")
                        return

                quest = WaitQuest(lifetime=200, creator=self)
                quest.assignToCharacter(character)
                self.addQuest(quest)
                quest = src.quests.RunCommand(command="roc"+9*"s"+"j",description="send clones to clean tile")
                quest.activate()
                quest.assignToCharacter(character)
                self.addQuest(quest)

                self.timesDelegated += 1
                return
            if not character.getFreeInventorySpace() > 0:
                quest = src.quests.questMap["ClearInventory"]()
                self.addQuest(quest)
                return
            if not isinstance(character.container,src.rooms.Room):
                if character.yPosition%15 == 14:
                    character.runCommandString("w")
                    return
                if character.yPosition%15 == 0:
                    character.runCommandString("s")
                    return
                if character.xPosition%15 == 14:
                    character.runCommandString("a")
                    return
                if character.xPosition%15 == 0:
                    character.runCommandString("d")
                    return

            if not (character.getBigPosition() == (self.targetPosition[0],self.targetPosition[1],0)):
                quest = src.quests.GoToTile(targetPosition=self.targetPosition)
                self.addQuest(quest)
                return

            charPos = character.getPosition()
            
            offsets = [(0,0,0),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)]
            foundOffset = None
            foundItems = None
            for offset in offsets:
                checkPos = (charPos[0]+offset[0],charPos[1]+offset[1],charPos[2]+offset[2])
                items = character.container.getItemByPosition(checkPos)
                if not items:
                    continue
                if items[0].bolted:
                    continue
                foundOffset = offset
                foundItems = items

            if foundOffset:
                if foundOffset == (0,0,0):
                    command = "k"
                elif foundOffset == (1,0,0):
                    command = "Kd"
                elif foundOffset == (-1,0,0):
                    command = "Ka"
                elif foundOffset == (0,1,0):
                    command = "Ks"
                elif foundOffset == (0,-1,0):
                    command = "Kw"

                quest = src.quests.RunCommand(command=command*len(foundItems))
                quest.activate()
                quest.assignToCharacter(character)
                self.addQuest(quest)
                return

            items = self.getLeftoverItems(character)
            if items:
                item = random.choice(items)

                quest = src.quests.GoToPosition(targetPosition=item.getPosition(),ignoreEndBlocked=True)
                self.addQuest(quest)
                return

        super().solver(character)

    def getLeftoverItems(self,character):
        
        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain  = character.container

        rooms = terrain.getRoomByPosition(self.targetPosition)
        room = None
        if rooms:
            room = rooms[0]

        if room.floorPlan:
            return []

        foundItems = []
        for position in random.sample(list(room.walkingSpace)+[(6,0,0),(0,6,0),(12,6,0),(6,12,0)],len(room.walkingSpace)+4):
            items = room.getItemByPosition(position)

            if not items:
                continue
            if items[0].bolted:
                continue

            foundItems.append(items[0])

        return foundItems

class GetBodyGuards(MetaQuestSequence):
    def __init__(self, description="get body guards"):
        questList = []
        super().__init__(questList)
        self.metaDescription = description

    def generateTextDescription(self):
        numMaxPosSubordinates = self.character.getNumMaxPosSubordinates()
        numSubordinates = self.character.getNumSubordinates()
        extraS = "s"
        if numSubordinates == 1:
            extraS = ""
        text = ("""
Since you are rank %s you can have %s subordinate"""+extraS+""".
You currently only have %s subordinates.
""")%(self.character.rank, numMaxPosSubordinates, numSubordinates, )

        if (numMaxPosSubordinates-numSubordinates) == 1:
            extra = "a "
            if numSubordinates > 0:
                extra = "one more "
            text += """
Get """+extra+"""body guard to replenish your subordinates."""
        else:
            extra = ""
            if numSubordinates > 0:
                extra = "more "
            text += """
Get """+extra+""" body guards to replenish your subordinates."""
        text += """
Body guards will follow you around and will try to protect you."""

        text += """


Go to the personnel artwork in the command centre.
Use it to gain a new body guard."""
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        if not self.active:
            return False
        if self.completed:
            1/0

        numMaxPosSubordinates = self.character.getNumMaxPosSubordinates()
        numSubordinates = self.character.getNumSubordinates()
        if not numMaxPosSubordinates > numSubordinates:
            self.postHandler()
            return True

        personnelArtwork = self.getPersonnelArtwork(character)
        if personnelArtwork and personnelArtwork.charges < 1:
            self.fail()
            return True

        return False

    def getPersonnelArtwork(self,character):
        homeRoom = character.getHomeRoom()
        if not homeRoom:
            return None
        return homeRoom.getItemByType("PersonnelArtwork")
        
    def generateSubquests(self,character):
        if not self.active:
            return

        if self.completed:
            1/0

        if self.subQuests:
            return

        if not character.getIsHome():
            quest = GoHome(description="go to command centre")
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        personnelArtwork = self.getPersonnelArtwork(character)
        if personnelArtwork and character.getDistance(personnelArtwork.getPosition()) > 1:
            quest = GoToPosition(description="go to personnel artwork",targetPosition=personnelArtwork.getPosition(),ignoreEndBlocked=True)
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

    def getSolvingCommandString(self,character,dryRun=True):
        personnelArtwork = self.getPersonnelArtwork(character)
        if not personnelArtwork:
            1/0
            return
        offset = character.getOffset(personnelArtwork.getPosition())
        baseCommand = None
        if offset == (0,0,0):
            baseCommand = "j"
        if offset == (-1,0,0):
            baseCommand = "Jd."
        if offset == (0,-1,0):
            baseCommand = "Js."
        if offset == (1,0,0):
            baseCommand = "Ja."
        if offset == (0,1,0):
            baseCommand = "Jw."

        if baseCommand:
            return baseCommand+"sj"

    def handleGotBodyguard(self,extraInfo=None):
        if not self.active:
            return
        if self.completed:
            1/0
        self.triggerCompletionCheck(self.character)

    def handleTileChange(self,extraInfo=None):
        if not self.active:
            return
        if self.completed:
            1/0

        if self.triggerCompletionCheck(self.character):
            return

        self.generateSubquests(self.character)

    def assignToCharacter(self,character):
        if self.character:
            return

        self.startWatching(character,self.handleTileChange, "changedTile")
        self.startWatching(character,self.handleTileChange, "got subordinate")

        return super().assignToCharacter(character)

    def solver(self,character):
        if self.triggerCompletionCheck(character):
            return

        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return

        super().solver(character)

class StandAttention(MetaQuestSequence):

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
            quest = GoToPosition()
            quest.assignToCharacter(character)
            if not character.registers.get("ATTNPOSx") or not character.registers.get("ATTNPOSy"):
                return
            targetpos = (character.registers["ATTNPOSx"],character.registers["ATTNPOSy"],0)
            quest.setParameters({"targetPosition":targetpos})
            self.addQuest(quest)

            quest = GoToPosition()
            quest.assignToCharacter(character)
            quest.setParameters({"targetPosition":(6,6,0)})
            self.addQuest(quest)


            quest = GoHome()
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

class GatherItems(Quest):

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
                            self.addQuest(RunCommand(command="Jd"+teleportCommand))
                        elif charPos == (itemPos[0],itemPos[1]-1,itemPos[2]):
                            self.addQuest(RunCommand(command="Js"+teleportCommand))
                        elif charPos == (itemPos[0]+1,itemPos[1],itemPos[2]):
                            self.addQuest(RunCommand(command="Ja"+teleportCommand))
                        elif charPos == (itemPos[0],itemPos[1]+1,itemPos[2]):
                            self.addQuest(RunCommand(command="Jw"+teleportCommand))
                        else:
                            quest = GoToPosition(targetPosition=itemPos,ignoreEndBlocked=True)
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
                quest = GoToTile(targetPosition=room.getPosition())
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)
                return

class LootRuin(MetaQuestSequence):
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
                quest = TeleportToTerrain(targetPosition=self.targetPosition)
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)
                return

            quest = ClearTerrain()
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()

class ObtainAllSpecialItems(Quest):

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

    def triggerCompletionCheck(self):
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
                            newQuest = GoHome()
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
                                newQuest = GoHome()
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


class MetaQuestParralel(Quest):
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
    assign self and subquests to character
    """

    def assignToCharacter(self, character):
        if self.character:
            return

        super().assignToCharacter(character)

        # assign subquests
        for quest in self.subQuests:
            quest.assignToCharacter(self.character)

        self.recalculate()

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

    def triggerCompletionCheck(self):
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


class NaiveMoveQuest(Quest):
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

    def triggerCompletionCheck(self):

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


class NaiveEnterRoomQuest(Quest):
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

    def triggerCompletionCheck(self):

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


class NaivePickupQuest(Quest):
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

    def triggerCompletionCheck(self):

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


class NaiveGetQuest(Quest):
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

    def triggerCompletionCheck(self):
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


class NaiveGetReward(Quest):
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

    def triggerCompletionCheck(self):
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


class NaiveMurderQuest(Quest):
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


class NaiveKnockOutQuest(Quest):
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

    def triggerCompletionCheck(self):
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


class NaiveWakeUpQuest(Quest):
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


class NaiveActivateQuest(Quest):
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

    def triggerCompletionCheck(self):
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


class NaiveDropQuest(Quest):
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


class NaiveDelegateQuest(Quest):
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

    def triggerCompletionCheck(self):
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


class WaitQuest(Quest):
    """
    straightforward state initialization
    """

    def __init__(
        self, followUp=None, startCinematics=None, lifetime=None, creator=None
    ):
        self.description = "wait"
        super().__init__(lifetime=lifetime, creator=creator)

        # save initial state and register
        self.type = "WaitQuest"

    """
    do nothing
    """

    def generateTextDescription(self):
        text = """
Wait."""
        if self.lifetimeEvent:
            text += """

This quest will end in %s ticks"""%(str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick),) 
        return text

    def isPaused(self):
        if not self.completed and self.active:
            return True
        return False

    def getSolvingCommandString(self, character, dryRun=True):
        if self.lifetimeEvent:
            return str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)+"."
        else:
            return "10."

    def solver(self, character):
        commandString = self.getSolvingCommandString(character,dryRun=False)
        self.randomSeed = random.random()
        if commandString:
            character.runCommandString(commandString)
            return False
        else:
            return True


"""
wait till something was deactivated
"""


class WaitForDeactivationQuest(Quest):
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

    def triggerCompletionCheck(self):
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


class WaitForQuestCompletion(Quest):
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

    def triggerCompletionCheck(self):
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


class DrinkQuest(Quest):
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

    def triggerCompletionCheck(self):
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


class SurviveQuest(Quest):
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


class EnterRoomQuestMeta(MetaQuestSequence):
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


class MoveQuestMeta(MetaQuestSequence):
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


class DropQuestMeta(MetaQuestSequence):
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


class PickupQuestMeta(MetaQuestSequence):
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


class ActivateQuestMeta(MetaQuestSequence):
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


class RefillDrinkQuest(ActivateQuestMeta):
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

    def triggerCompletionCheck(self):
        for item in self.character.inventory:
            if isinstance(item, src.items.GooFlask):
                if item.uses > 99:
                    self.postHandler()


"""
collect items with some quality
"""


class CollectQuestMeta(MetaQuestSequence):
    """
    state initialization
    """

    def __init__(self, toFind="canBurn", startCinematics=None, creator=None):
        super().__init__([], creator=creator)
        self.toFind = toFind
        self.activateQuest = None
        self.waitQuest = WaitQuest(creator=self)
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


class GetQuest(MetaQuestSequence):
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

    def triggerCompletionCheck(self):

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


class GetReward(MetaQuestSequence):
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


class MurderQuest(MetaQuestSequence):
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


class KnockOutQuest(MetaQuestSequence):
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


class WakeUpQuest(MetaQuestSequence):
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


class FillPocketsQuest(MetaQuestSequence):
    """
    state initialization
    """

    def __init__(
        self, followUp=None, startCinematics=None, lifetime=None, creator=None
    ):
        self.waitQuest = WaitQuest(creator=self)
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


class LeaveRoomQuest(Quest):
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

    def triggerCompletionCheck(self):

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


class PatrolQuest(MetaQuestSequence):
    """
    state initialization
    """

    def __init__(self, description="patrol", waypoints=None, lifetime=None):
        questList = []
        super().__init__(questList, lifetime=lifetime)

        self.metaDescription = description

        # save initial state and register
        self.type = "PatrolQuest"
        self.waypointIndex = 0
        self.waypoints = waypoints

    def triggerCompletionCheck(self, character=None):
        return False

    def solver(self,character):
        if not self.subQuests:
            """
            quest = GoToTile(targetPosition=self.waypoints[self.waypointIndex],paranoid=True)
            quest.assignToCharacter(character)
            quest.activate()
            self.addQuest(quest)
            """

            quest = SecureTile(toSecure=self.waypoints[self.waypointIndex],endWhenCleared=True)
            quest.assignToCharacter(character)
            quest.activate()
            self.addQuest(quest)


            self.waypointIndex += 1
            if self.waypointIndex >= len(self.waypoints):
                self.waypointIndex = 0
            return
        super().solver(character)

"""
quest to examine the environment
bad pattern: has no solver
"""


class ExamineQuest(Quest):
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

    def triggerCompletionCheck(self):
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


class FetchFurniture(MetaQuestParralel):
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


class PlaceFurniture(MetaQuestParralel):
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


class ConstructRoom(MetaQuestParralel):
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

    def triggerCompletionCheck(self):
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


class TransportQuest(MetaQuestSequence):
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


class StoreCargo(MetaQuestSequence):
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


class MoveToStorage(MetaQuestSequence):
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


class HandleDelivery(MetaQuestSequence):
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


class KeepFurnacesFiredMeta(MetaQuestParralel):
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


class KeepFurnaceFiredMeta(MetaQuestSequence):
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

    def triggerCompletionCheck(self):
        return


"""
fire a furnace once
"""


class FireFurnaceMeta(MetaQuestSequence):
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

    def triggerCompletionCheck(self):
        if self.furnace.activated:
            self.postHandler()

        super().triggerCompletionCheck()


"""
Fill a growth tank
"""


class FillGrowthTankMeta(MetaQuestSequence):
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

    def triggerCompletionCheck(self):
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


class HopperDuty(MetaQuestSequence):
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
            self.addQuest(WaitQuest(lifetime=10, creator=self), addFront=False)


"""
clear the rubble from the mech
bad pattern: there is no way to determine what is to be picked up
"""


class ClearRubble(MetaQuestParralel):
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


class RoomDuty(MetaQuestParralel):
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

    def triggerCompletionCheck(self):
        return


"""
dummy quest for following somebodies orders
"""


class Serve(MetaQuestParralel):
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

    def triggerCompletionCheck(self):
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

class DeliverSpecialItem(Quest):
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

class GoToTile(Quest):
    def __init__(self, description="go to tile", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.targetPosition = None
        self.showCoordinates = showCoordinates
        self.description = description
        self.metaDescription = description
        self.path = None
        self.expectedPosition = None
        self.lastPos = None
        self.lastDirection = None
        self.smallPath = None
        self.paranoid = paranoid
        self.sentSubordinates = False

        if targetPosition: 
            self.setParameters({"targetPosition":targetPosition})

        self.attributesToStore.extend([
            "hasListener","paranoid","sentSubordinates" ])

        self.tupleListsToStore.extend([
            "path", "smallPath" ])

        self.tuplesToStore.extend([
            "targetPosition","expectedPosition","lastPos","lastDirection"])

        self.type = "GoToTile"

        self.shortCode = "G"

    def generateTextDescription(self):
        return """
Go to tile %s

This is a pretty common quest.
You have to go from one place to another pretty often.



Quests like this can be pretty boring.
Press c now to use auto move to complete this quest.
Press crtl-d to stop your character from moving.%s
"""%(self.targetPosition,self.showCoordinates,)

    def getQuestMarkersSmall(self,character,dryRun=True,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []
        self.getSolvingCommandString(character, dryRun=dryRun)
        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if self.smallPath:
            pos = (character.xPosition,character.yPosition)
            for step in self.smallPath:
                pos = (pos[0]+step[0],pos[1]+step[1])
                result.append((pos,"path"))
        return result

    def getQuestMarkersTile(self,character):
        if self.character.xPosition%15 == 0 or  self.character.yPosition%15 == 0 or self.character.xPosition%15 == 14 or self.character.yPosition%15 == 14:
            return []
        result = super().getQuestMarkersTile(character)
        self.getSolvingCommandString(character)
        if self.expectedPosition:
            result.append((self.expectedPosition,"path"))
        if self.path:
            if self.expectedPosition:
                pos = self.expectedPosition
            elif isinstance(character.container,src.rooms.Room):
                pos = (character.container.xPosition,character.container.yPosition)
            else:
                pos = (character.xPosition//15,character.yPosition//15)
            for step in reversed(self.path):
                pos = (pos[0]+step[0],pos[1]+step[1])
                result.append((pos,"path"))
        result.append((self.targetPosition,"target"))
        return result

    def handleMoved(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        converedDirection = None
        if extraInfo[1] == "west":
            converedDirection = (-1,0)
        if extraInfo[1] == "east":
            converedDirection = (1,0)
        if extraInfo[1] == "north":
            converedDirection = (0,-1)
        if extraInfo[1] == "south":
            converedDirection = (0,1)
        if self.smallPath:
            if converedDirection == self.smallPath[0]:
                self.smallPath = self.smallPath[1:]
                return
            else:
                self.smallPath = None

        self.triggerCompletionCheck(extraInfo[0])

    def handleTileChange(self):
        pos = self.character.getBigPosition()
        if pos == self.lastPos:
            return
        self.lastPos = pos

        converedDirection = None
        if self.character.xPosition%15 == 0:
            converedDirection = (1,0)
        if self.character.yPosition%15 == 0:
            converedDirection = (0,1)
        if self.character.xPosition%15 in (13,14):
            converedDirection = (-1,0)
        if self.character.yPosition%15 in (13,14):
            converedDirection = (0,-1)
        if self.path:
            if converedDirection == self.path[-1]:
                self.expectedPosition = None
                self.path = self.path[:-1]
                return
            else:
                self.path = None
                self.getSolvingCommandString(self.character,dryRun=False)
                return
        return

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleMoved, "moved")
        self.startWatching(character,self.handleTileChange, "changedTile")

        super().assignToCharacter(character)

    def triggerCompletionCheck(self, character=None):
        if not self.targetPosition:
            return False
        if not character:
            return False
        if not self.active:
            return
        if isinstance(character.container,src.rooms.Room):
            if character.container.xPosition == self.targetPosition[0] and character.container.yPosition == self.targetPosition[1]:
                self.postHandler()
                return True
        elif character.xPosition//15 == self.targetPosition[0] and character.yPosition//15 == self.targetPosition[1]:
            self.postHandler()
            return True
        return False

    def solver(self, character):
        self.activate()
        self.assignToCharacter(character)
        self.smallPath = None
        self.triggerCompletionCheck(character)
        commandString = self.getSolvingCommandString(character,dryRun=False)
        self.randomSeed = random.random()
        if commandString:
            character.runCommandString(commandString)
            return False
        else:
            return True

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            if not len(parameters["targetPosition"]) > 2:
                parameters["targetPosition"] = (parameters["targetPosition"][0],parameters["targetPosition"][1],0)
            self.targetPosition = parameters["targetPosition"]
            self.description = self.metaDescription
            if self.showCoordinates:
                self.description += " %s"%(self.targetPosition,)
        return super().setParameters(parameters)

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

    def reroll(self):
        self.path = None
        super().reroll()

    def getSolvingCommandString(self, character, dryRun = True):
        if not self.targetPosition:
            return ".10.."

        if self.smallPath:
            command = ""
            for step in self.smallPath:
                if step == (-1,0):
                    command += "a"
                elif step == (1,0):
                    command += "d"
                elif step == (0,-1):
                    command += "w"
                elif step == (0,1):
                    command += "s"

            return command

        if character.macroState.get("submenue"):
            return ["esc"]

        localRandom = random.Random(self.randomSeed)
        if isinstance(character.container, src.rooms.Room):
            if not self.paranoid and localRandom.random() < 0.5 and "fighting" in self.character.skills:
                for otherCharacter in character.container.characters:
                    if otherCharacter.faction == character.faction:
                        continue
                    return "gg"

            charPos = (character.xPosition,character.yPosition,0)
            tilePos = (character.container.xPosition,character.container.yPosition,0)

            direction = None
            path = self.path
            """
            if self.expectedPosition and not (tilePos == self.expectedPosition):
                if tilePos == self.lastPos:
                    direction = self.lastDirection
                else:
                    path = None
            """

            targetPos = (self.targetPosition[0],self.targetPosition[1],0)
            if not path:
                basePath = character.container.container.getPath(tilePos,targetPos,localRandom=localRandom,character=character)
                if not basePath:
                    return ".14..."
                path = list(reversed(basePath))

            if not dryRun:
                self.path = path

            if not path:
                return ".13.."

            if not direction:
                direction = path[-1]

            """
            if self.paranoid:
                if not self.sentSubordinates and character.subordinates:
                    if not dryRun:
                        self.sentSubordinates = True
                    command = "QSNSecureTile\n%s,%s\nlifetime:40; ."%(tilePos[0]+direction[0],tilePos[1]+direction[1],)
                    return command
                if not dryRun:
                    self.sentSubordinates = False
            """

            if direction == (1,0):
                if charPos == (12,6,0):
                    return "d"
                (command,self.smallPath) = character.container.getPathCommandTile(charPos,(12,6,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(charPos,(12,6,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    return ".19.."
                return command
            if direction == (-1,0):
                if charPos == (0,6,0):
                    return "a"
                (command,self.smallPath) = character.container.getPathCommandTile(charPos,(0,6,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(charPos,(0,6,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    return ".18.."
                return command
            if direction == (0,1):
                if charPos == (6,12,0):
                    return "s"
                (command,self.smallPath) = character.container.getPathCommandTile(charPos,(6,12,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(charPos,(6,12,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    return ".17.."
                return command
            if direction == (0,-1):
                if charPos == (6,0,0):
                    return "w"
                (command,self.smallPath) = character.container.getPathCommandTile(charPos,(6,0,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(charPos,(6,0,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    return ".16.."
                return command
            return ".15.."
        else:
            if not self.paranoid and localRandom.random() < 0.5 and "fighting" in self.character.skills:
                for otherCharacter in character.container.characters:
                    if not (otherCharacter.xPosition//15 == character.xPosition//15 and otherCharacter.yPosition//15 == character.yPosition//15):
                        continue
                    if otherCharacter.faction == character.faction:
                        continue
                    return "gg"

            tilePos = (character.xPosition//15,character.yPosition//15,0)
            charPos = (character.xPosition%15,character.yPosition%15,0)

            direction = None
            path = self.path
            """
            if self.expectedPosition and not (tilePos == self.expectedPosition):
                if tilePos == self.lastPos:
                    direction = self.lastDirection
                else:
                    path = None
            """

            targetPos = (self.targetPosition[0],self.targetPosition[1],0)
            if not path and not direction:
                basePath = character.container.getPath(tilePos,targetPos,localRandom=localRandom)
                if not basePath:
                    return ".3.."
                path = list(reversed(basePath))

            if not dryRun:
                self.path = path

            if not path and not direction:
                return ".26.."

            if direction == None:
                if charPos == (0,7,0):
                    return "d"
                if charPos == (7,14,0):
                    return "w"
                if charPos == (7,0,0):
                    return "s"
                if charPos == (14,7,0):
                    return "a"

            if not direction:
                direction = path[-1]

            """
            if self.paranoid:
                if not self.sentSubordinates and character.subordinates:
                    if not dryRun:
                        self.sentSubordinates = True
                    command = "QSNSecureTile\n%s,%s\nlifetime:40; ."%(tilePos[0]+direction[0],tilePos[1]+direction[1],)
                    return command
                self.sentSubordinates = False
            """

            if direction == (1,0):
                if charPos == (13,7,0):
                    return "d"
                if charPos == (14,7,0):
                    return "d"
                (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(13,7,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(13,7,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    items = character.container.getItemByPosition(character.getPosition(offset=(1,0,0)))
                    if not items:
                        return "d"
                    else:
                        dropDirection = random.choice(["l","La","Ls","Lw"])
                        return "dk"+dropDirection
                    return ".12.."
                return command
            if direction == (-1,0):
                if charPos == (1,7,0):
                    return "a"
                if charPos == (0,7,0):
                    return "a"
                (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(1,7,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(1,7,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    items = character.container.getItemByPosition(character.getPosition(offset=(-1,0,0)))
                    if not items:
                        return "a"
                    else:
                        dropDirection = random.choice(["l","Ls","Lw","Ld"])
                        return "ak"+dropDirection
                    return ".12.."
                return command
            if direction == (0,1):
                if charPos == (7,13,0):
                    return "s"
                if charPos == (7,14,0):
                    return "s"
                (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(7,13,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(7,13,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    items = character.container.getItemByPosition(character.getPosition(offset=(0,1,0)))
                    if not items:
                        return "s"
                    else:
                        dropDirection = random.choice(["l","La","Lw","Ld"])
                        return "sk"+dropDirection
                    return ".12.."
                return command
            if direction == (0,-1):
                if charPos == (7,1,0):
                    return "w"
                if charPos == (7,0,0):
                    return "w"
                (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(7,1,0),localRandom=localRandom,character=character)
                if not command:
                    (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,(7,1,0),localRandom=localRandom,tryHard=True,character=character)
                if not command and not dryRun:
                    self.path = None
                    self.lastDirection = None
                    items = character.container.getItemByPosition(character.getPosition(offset=(0,-1,0)))
                    if not items:
                        return "w"
                    else:
                        dropDirection = random.choice(["l","La","Ls","Ld"])
                        return "wk"+dropDirection
                    return ".12.."
                return command
            return ".17.."
        return ".20.."

class ReachOutStory(MetaQuestSequence):
    def __init__(self, description="reach out to implant", creator=None):
        questList = []
        super().__init__(creator=creator)
        self.metaDescription = description

    def solver(self,character):
        self.triggerCompletionCheck()
        self.generateSubquests()

        if not self.subQuests:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                return
            
        super().solver(character)

    def triggerCompletionCheck(self):
        return

    def handleQuestsOpened(self,extraInfo=None):
        self.postHandler()

    def assignToCharacter(self,character):
        if self.character:
            return

        self.startWatching(character,self.handleQuestsOpened,"opened quest menu")
        return super().assignToCharacter(character)

    def getSolvingCommandString(self,character,dryRun=True):
        if character.macroState.get("submenue"):
            return ["esc"]
        else:
            return "q"

class InitialLeaveRoomStory(GoToTile):
    def __init__(self, description="go to tile", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        super().__init__(description=description, creator=creator, lifetime=lifetime, targetPosition=targetPosition, paranoid=paranoid, showCoordinates=showCoordinates)
        self.direction = direction

    def generateTextDescription(self):
        door = src.items.itemMap["Door"]()
        door.open = True
        return ["""
You reach out to your implant and it answers.
It whispers, but you understand clearly:

You are safe. You are in a farming complex.
Something is not right, though.
It looks freshly seeded, but the ghul is not active.

You can not stay here forever, so start moving and leave this room.
Use the wasd movement keys to move.
Pass through the door (""",door.render(),""") in the """+self.direction+""". 



Right now you are looking at the quest menu.
Detailed instructions and explainations are shown here.
For now ignore the options below and press esc to continue.

"""]

class EscapeAmbushStory(GoToTile):
    def __init__(self, description="go to tile", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        super().__init__(description=description, creator=creator, lifetime=lifetime, targetPosition=targetPosition, paranoid=paranoid, showCoordinates=showCoordinates)
        self.direction = direction

    def generateTextDescription(self):
        door = src.items.itemMap["Door"]()
        door.open = True
        enemyDirection = " the south and east"
        if self.character.getBigPosition()[1] == 13:
            enemyDirection = " the east"
        return ["""
You reach out to your implant and it answers.
It whispers, but you understand clearly:


This room is not a safe place to stay.
Enemies are on their way to hunt you down.
They look like [- and come from """+enemyDirection+""".

So get moving and leave this room.
Use the wasd movement keys to move.
Pass through the door (""",door.render(),""") in the """+self.direction+""". 



Right now you are looking at the quest menu.
Detailed instructions and explainations are shown here.
For now ignore the options below and press esc to continue.

"""]

    def triggerCompletionCheck(self,character=None):
        if not character:
            return
        if isinstance(character.container,src.rooms.Room):
            return False
        self.postHandler()

class GoToTileStory(GoToTile):
    def __init__(self, description="go to tile", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True, direction=None):
        super().__init__(description=description, creator=creator, lifetime=lifetime, targetPosition=targetPosition, paranoid=paranoid, showCoordinates=showCoordinates)
        self.direction = direction

    def generateTextDescription(self):
        command = ""
        if self.direction == "south":
            command = "s"
        if self.direction == "north":
            command = "w"
        if self.direction == "west":
            command = "a"
        if self.direction == "east":
            command = "d"

        item1 = src.items.itemMap["Scrap"](amount=6)
        item2 = src.items.itemMap["LandMine"]()
        return ["""
Go one tile to the """+self.direction+""".
The quest ends when you do that.
This quest is part of the quest to reach the base.

Avoid fighting with the enemies, you are not equipped for it.
Also avoid running into obstacles (""",item1.render(),""")
and try not to step on the land mines (""",item2.render(),""").


The playing field is divided into tiles by the blue borders.
You can pass from tile to tile using the pathway in the middle.
So go to the """+self.direction+""" side of this tile and press """+command+""" to switch tile.

Those suggested action on how to do this are shown during normal gameplay on the left.
Following that suggestion should avoid the obstacles and most landmines.
The suggestion doesn't avoid enemies and might even run into them.
So use the suggested keystrokes as orientation and don't follow them blindly.



Press a to move the quest cursor back to the main quest
"""%(self.getSolvingCommandString(self.character))]

class TakeOverBase(MetaQuestSequence):
    def __init__(self, description="join base"):
        super().__init__()
        self.metaDescription = description

    def getSolvingCommandString(self,character,dryRun=True):
        if not self.subQuests:
            if character.macroState["submenue"]:
                return ["esc"]
        return super().getSolvingCommandString(character,dryRun=dryRun)

    def generateTextDescription(self):
        return """
There is no commander. This is a problem.

Insects are growing within the hives in the abbandoned farms.
Without a commander the hives will continue growing.
Sooner or later their attacks will break the bases defences.

Also the base is in maintenance mode.
So leaving is not an option. You are stuck here. 
It is not safe here, but it is safer in the base than outside.

So stay here until those issues are resolved.
Join the crew of this base and help defend it against the insects.
The harder you work the safer you will be.


press d to get a description on how to join the base
"""

    def generateSubquests(self,character=None):
        if not self.subQuests:
            if self.character.rank == None:
                quest = Assimilate()
                quest.assignToCharacter(self.character)
                quest.activate()
                self.addQuest(quest)
                quest.generateSubquests(character)
                return
        super().generateSubquests()

    def solver(self,character):
        if not self.subQuests:
            self.generateSubquests(character)
            return
        return super().solver(character)

    def triggerCompletionCheck(self):
        return

class ChangeJob(MetaQuestSequence):
    def __init__(self, description="take on new duty"):
        super().__init__()
        self.metaDescription = description
        self.type = "ChangeJob"

        self.addQuest(Assimilate(description="set new duties"))
        self.addQuest(TrainSkill())

    def generateTextDescription(self):
        return """
Retrain for a different duty.

Use the basic trainer to learn a new skill.
Reset your duties at the assimilator aftwerward.
"""

class TrainSkill(MetaQuestSequence):
    def __init__(self, description="train skill"):
        super().__init__()
        self.metaDescription = description
        self.type = "TrainSkill"

    def generateTextDescription(self):
        if not self.character.skills:
            return """
Without skills you are useless to the base.
Train a skill or the base won't accept you.

Activate the basic trainer in the command centre to start training a skill"""
        else:
            return """
Skills are what part of what makes you useful to the base.
Train an additional skill.
This will allow you to do a different duty.

Activate the basic trainer in the command centre to start training a skill"""


    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

    def handleSkillLearned(self,extraInfo):
        self.postHandler()

    def generateSubquests(self,character):
        if not self.active:
            return
        if self.completed:
            1/0

        if self.subQuests:
            return

        if not isinstance(character.container, src.rooms.Room):
            quest = GoHome(description="go back to command centre")
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        room = character.container

        for item in room.getItemsByType("BasicTrainer",needsBolted=True):
            if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                return
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                return
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                return
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                return
            quest = GoToPosition(targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to basic trainer  ")
            quest.activate()
            quest.assignToCharacter(character)
            self.addQuest(quest)
            return
        quest = GoHome(description="go to command centre")
        self.addQuest(quest)
        quest.assignToCharacter(character)
        quest.activate()
        return

    def getSolvingCommandString(self,character,dryRun=True):
        if not self.subQuests:
            submenue = character.macroState.get("submenue")
            if submenue:
                if isinstance(submenue,src.interaction.SelectionMenu):
                    return ["enter"]
                return ["esc"]
            room = character.container

            if not isinstance(character.container, src.rooms.Room):
                return super().getSolvingCommandString(character,dryRun=dryRun)

            for item in room.itemsOnFloor:
                if not item.bolted:
                    continue
                if not item.type == "BasicTrainer":
                    continue

                if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                    return "Ja"
                if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                    return "Jd"
                if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                    return "Jw"
                if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                    return "Js"

        return super().getSolvingCommandString(character,dryRun=dryRun)

    def solver(self,character):
        self.triggerCompletionCheck(character)
        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return

        if not self.subQuests:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                return
            
        super().solver(character)

    def handleMovement(self, extraInfo):
        if not self.active:
            return

        self.generateSubquests(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleMovement, "moved")
        self.startWatching(character,self.handleSkillLearned, "learnedSkill")

        super().assignToCharacter(character)

class Assimilate(MetaQuestSequence):
    def __init__(self, description="integrate into the base"):
        super().__init__()
        self.metaDescription = description
        self.type = "Assimilate"

    def triggerCompletionCheck(self,character=None):
        return False

    def generateTextDescription(self):
        if self.character.rank == None:
            return """
When the base grows or clones are dying, replacement personel is needed.
The base can create new clones, but they need to be integrated into the bases sytems.
Every base should have an assimilator for exactly that purpose.

There is an assimilatior in the command centre.
Activate the assimilator to get integrated into the base."""
        else:
            return """
Use the assimilator to get further instructions.
The assimilator is in the command centre.
"""

    def generateSubquests(self,character):
        if not self.active:
            return

        while self.subQuests:
            self.subQuests[-1].triggerCompletionCheck(character)
            if not self.subQuests:
                break
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return

        room = character.container

        if not isinstance(character.container, src.rooms.Room):
            quest = GoHome(description="go to command centre")
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        for item in room.itemsOnFloor:
            if not item.bolted:
                continue
            if not item.type == "Assimilator":
                continue

            if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                #quest = RunCommand(command=list("Ja.")+["enter"]*6,description="activate the assimilator \nby pressing")
                #quest.activate()
                #self.addQuest(quest)
                return
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                #quest = RunCommand(command=list("Jd.")+["enter"]*6,description="activate the assimilator \nby pressing")
                #quest.activate()
                #self.addQuest(quest)
                return
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                #quest = RunCommand(command=list("Jw.")+["enter"]*6,description="activate the assimilator \nby pressing")
                #quest.activate()
                #self.addQuest(quest)
                return
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                #quest = RunCommand(command=list("Js.")+["enter"]*6,description="activate the assimilator \nby pressing")
                #quest.activate()
                #self.addQuest(quest)
                return
            quest = GoToPosition(targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to assimilator ")
            quest.active = True
            quest.assignToCharacter(character)
            self.addQuest(quest)
            return
        self.addQuest(GoToTile(targetPosition=(7,7,0),description="go to command centre"))
        return

    def getSolvingCommandString(self,character,dryRun=True):
        if not self.subQuests:
            submenue = character.macroState.get("submenue")
            if submenue:
                if isinstance(submenue,src.interaction.SelectionMenu):
                    return ["enter"]
                return ["esc"]

            room = character.container

            if not isinstance(character.container, src.rooms.Room):
                return super().getSolvingCommandString(character,dryRun=dryRun)

            for item in room.itemsOnFloor:
                if not item.bolted:
                    continue
                if not item.type == "Assimilator":
                    continue

                if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                    return list("Ja")
                if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                    return list("Jd")
                if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                    return list("Jw")
                if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                    return list("Js")

        return super().getSolvingCommandString(character,dryRun=dryRun)

    def solver(self,character):
        if not self.subQuests:
            self.generateSubquests(character)

        if not self.subQuests:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                return
            
        super().solver(character)

    def handleMovement(self, extraInfo):
        if not self.active:
            return

        self.generateSubquests(extraInfo[0])

    def handleTileChange(self):
        if self.completed:
            1/0

        for quest in self.subQuests:
            quest.postHandler()

        self.subQuests = []

    def handleChangedDuties(self,character=None):
        self.postHandler()

    def assignToCharacter(self, character):
        self.startWatching(character,self.handleMovement, "moved")
        self.startWatching(character,self.handleTileChange, "changedTile")
        self.startWatching(character,self.handleChangedDuties, "changed duties")

        super().assignToCharacter(character)

class ActivateEpochArtwork(MetaQuestSequence):
    def __init__(self, description="activate epoch artwork",epochArtwork=None):
        questList = []
        super().__init__(questList)
        self.metaDescription = description
        self.type = "ActivateEpochArtwork"
        self.epochArtwork = epochArtwork

        self.startWatching(epochArtwork,self.handleEpochrArtworkUsed, "epoch artwork used")

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((7,7,0),"target"))
        return result

    def generateTextDescription(self):
        return """
You reached the base and you are safe for now.
The farms have been neglected and hives have developed.
But it has defences.

Find out who is commanding this base.
Maybe you will be safe for longer here.



Go to the command centre and activate the epoch artwork.
That should reveal who is commanding this base.



You can move using full tiles by pressing WASD. Your character will automove.
This is a lot less keys to press, but should only be done in safe areas.
Remember to press ctrl-d if you lose control over your character.
"""


    def handleEpochrArtworkUsed(self,extraInfo):
        if extraInfo[0] == self.character:
            self.postHandler()

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        return False

    def solver(self,character):
        self.triggerCompletionCheck(character)
        self.generateSubquests(character)

        if not self.subQuests:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                return
            
        super().solver(character)

    def getSolvingCommandString(self,character,dryRun=True):
        if character.macroState.get("submenue"):
            return ["esc"]
        directions = {

                (7,5,0):"south",
                (7,6,0):"west",
                (8,6,0):"south",
                (6,6,0):"south",
                (8,7,0):"south",
                (6,7,0):"south",
                (8,8,0):"south",
                (6,8,0):"south",
                (8,9,0):"west",
                (6,9,0):"east",
                (7,9,0):"north",
                (7,8,0):"north",
                }

        direction = directions.get(character.getBigPosition())
        if direction:
            if direction == "north":
                return "W"
            if direction == "south":
                return "S"
            if direction == "west":
                return "A"
            if direction == "east":
                return "D"

        if not self.subQuests:
            if character.getPosition() == (6,7,0):
                return "Jw"
        return super().getSolvingCommandString(character,dryRun=dryRun)

    def generateSubquests(self,character,silent=False):
        
        if not self.active:
            return
        if self.completed:
            return

        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return

        pos = character.getBigPosition()

        if pos == (7,7,0):
            if not character.getPosition() == (6,7,0):
                quest = GoToPosition(targetPosition=(6,7,0), description="go to epoch artwork")
                quest.activate()
                self.addQuest(quest)
                return
            return

        directions = {

                (7,5,0):"south",
                (7,6,0):"west",
                (8,6,0):"south",
                (6,6,0):"south",
                (8,7,0):"south",
                (6,7,0):"south",
                (8,8,0):"south",
                (6,8,0):"south",
                (8,9,0):"west",
                (6,9,0):"east",
                (7,9,0):"north",
                (7,8,0):"north",
                }

        direction = directions.get(pos)
        if direction == None:
            return

        if direction == "north":
            targetPos = (pos[0],pos[1]-1,pos[2])
        if direction == "south":
            targetPos = (pos[0],pos[1]+1,pos[2])
        if direction == "west":
            targetPos = (pos[0]-1,pos[1],pos[2])
        if direction == "east":
            targetPos = (pos[0]+1,pos[1],pos[2])

        if not silent:
            character.addMessage("move one tile to the "+direction)
        quest = src.quests.GoToTile(description="go one tile "+direction,targetPosition=targetPos,showCoordinates=False)
        self.addQuest(quest)
        quest.activate()

    def handleMovement(self, extraInfo):
        if self.completed:
            1/0

        if not self.active:
            return

        self.generateSubquests(extraInfo[0],silent=True)

    def handleTileChange(self):
        if self.completed:
            1/0

        for quest in self.subQuests:
            quest.postHandler()

        self.subQuests = []

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleMovement, "moved")
        self.startWatching(character,self.handleTileChange, "changedTile")

        super().assignToCharacter(character)

class ReachBase(MetaQuestSequence):
    def __init__(self, description="reach base",storyText=None):
        super().__init__()
        self.metaDescription = description
        self.type = "ReachBase"
        self.lastDirection = None
        self.storyText = storyText

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((7,6,0),"target"))
        return result

    def solver(self,character):
        self.generateSubquests(character)

        if not self.subQuests:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                return
            
        super().solver(character)

    def generateTextDescription(self):

        text = """
You reach out to your implant and in answers:"""
        if self.storyText:
            text += """
%s"""%(self.storyText,)
        else:
            text += """

There is a base in the north. The base belongs to your faction.
Enter the base to get into the safety of the bases defences.


The entry is on the northern side of the base.
You need to go around the base to actually enter it.
You are likely getting chased and the area is overrun with insects.
So you have to be careful."""

        text += """

You have to cross several tiles to find your path to the entry of the base.
Currently the sugggested next step is to go one tile to the %s.
Following the suggestions will guide you into the base.
It might also steer you into groups of enemies on the way.
So watch the environment and don't follow all suggestions blindly.



You can see description for sub quests.
Press d now to move the quest cursor to select the sub quest.
"""%(self.lastDirection,)
        return text

    def generateSubquests(self,character):
        if self.subQuests:
            return

        if not self.active:
            return
        if self.completed:
            return

        if character.getPosition() == (7,0,0):
            quest = src.quests.RunCommand(command="s")
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            return
        pos = character.getBigPosition()
        if pos == (7,6,0):
            self.postHandler()
            return

        if pos == (9,5,0):
            direction = "north"
        elif pos[1] > 10:
            if pos[0] == 7:
                direction = "west"
            elif pos[0] < 7:
                if pos[0] == 6:
                    direction = "north"
                else:
                    direction = "east"
            else:
                direction = "west"
        elif pos[1] > 6:
            if pos[0] <= 7:
                if pos[0] <= 4:
                    direction = "north"
                else:
                    direction = "west"
            elif pos[0] >= 10:
                direction = "north"
            else:
                direction = "east"
        elif pos[1] == 6:
            if pos[0] <= 7:
                if pos[0] == 4:
                    direction = "north"
                elif pos[0] == 5:
                    direction = "north"
                else:
                    direction = "east"
            else:
                direction = "north"
        elif pos[1] == 4:
            if pos[0] < 7:
                direction = "east"
            elif pos[0] < 7:
                direction = "west"
            else:
                direction = "south"
        else:
            if pos[0] < 4:
                direction = "south"
            elif pos[0] < 7:
                direction = "east"
            elif pos[0] == 7:
                direction = "south"
            else:
                direction = "west"

        if direction == "north":
            targetPos = (pos[0],pos[1]-1,pos[2])
        if direction == "south":
            targetPos = (pos[0],pos[1]+1,pos[2])
        if direction == "west":
            targetPos = (pos[0]-1,pos[1],pos[2])
        if direction == "east":
            targetPos = (pos[0]+1,pos[1],pos[2])

        extra = ""
        if self.lastDirection == direction:
            extra = "another "
        character.addMessage("move "+extra+"one tile to the "+direction)
        self.lastDirection = direction
        quest = src.quests.GoToTileStory(description="go one tile to the "+direction,targetPosition=targetPos,showCoordinates=False,direction=direction)
        self.addQuest(quest)
        quest.assignToCharacter(character)
        quest.activate()

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if character.getBigPosition() == (7,6,0):
            self.postHandler()
            return
        return False

    def handleMovement(self, extraInfo):
        if not self.active:
            return
        if self.completed:
            1/0

        if self.triggerCompletionCheck(self.character):
            return
        self.generateSubquests(extraInfo[0])

    def handleTileChange(self):
        if not self.active:
            return
        if self.completed:
            1/0

        for quest in self.subQuests:
            quest.postHandler()

        self.subQuests = []

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleMovement, "moved")
        self.startWatching(character,self.handleTileChange, "changedTile")

        super().assignToCharacter(character)

class Huntdown(MetaQuestSequence):
    def __init__(self, description="huntdown", target=None, lifetime=None):
        questList = []
        super().__init__(questList,lifetime=lifetime)
        self.metaDescription = description
        self.type = "Huntdown"
        self.target = target

    def triggerCompletionCheck(self):
        if self.target and self.target.dead:
            self.postHandler()
            return True
        return False

    def solver(self,character):
        self.triggerCompletionCheck()

        if not self.subQuests:
            if isinstance(character.container, src.rooms.Room):
                charPos = (character.container.xPosition,character.container.yPosition,0)
            else:
                charPos = (character.xPosition//15,character.yPosition//15,0)

            if not self.target.container:
                character.runCommandString("10.")
                return

            if isinstance(self.target.container, src.rooms.Room):
                targetPos = (self.target.container.xPosition,self.target.container.yPosition,0)
            else:
                targetPos = (self.target.xPosition//15,self.target.yPosition//15,0)

            if targetPos == (0,0,0):
                return

            if character.yPosition%15 == 0:
                character.runCommandString("s")
                return
            if character.yPosition%15 == 14:
                character.runCommandString("w")
                return
            if character.xPosition%15 == 0:
                character.runCommandString("d")
                return
            if character.xPosition%15 == 14:
                character.runCommandString("a")
                return

            if not charPos == targetPos:
                if abs(charPos[0]-targetPos[0])+abs(charPos[1]-targetPos[1]) == 1:
                    newPos = targetPos
                else:
                    self.fail()
                    return

                quest = GoToTile(paranoid=True)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                quest.setParameters({"targetPosition":newPos})
                return
            else:
                character.runCommandString("gg")
                return

        super().solver(character)

class DestroySpawner(MetaQuestSequence):
    def __init__(self, description="destroy hive",targetPosition=None):
        super().__init__()
        self.metaDescription = description+" %s"%(targetPosition,)
        self.type = "DestroySpawner"
        self.targetPosition = targetPosition

    def generateTextDescription(self):
        text = """
Destroy the hive on tile %s.


To destroy the hive, go to the monster spawner (MS) in the middle of the hive and activate it.
You may want to plan an escape route."""%(self.targetPosition,)
        return text

    def handleSpawnerKill(self):
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self,character):
        if self.character:
            return

        foundSpawner = False
        terrain = character.getTerrain()
        rooms = terrain.getRoomByPosition(self.targetPosition)
        for room in rooms:
            items = room.getItemByPosition((6,6,0))
            for item in items:
                if isinstance(item, src.items.itemMap["MonsterSpawner"]):
                    foundSpawner = item

        if foundSpawner:
            self.startWatching(foundSpawner,self.handleSpawnerKill, "spawner will be destroyed")
        
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if not self.active:
            return

        foundSpawner = False
        terrain = character.getTerrain()
        rooms = terrain.getRoomByPosition(self.targetPosition)
        for room in rooms:
            items = room.getItemByPosition((6,6,0))
            for item in items:
                if isinstance(item, src.items.itemMap["MonsterSpawner"]) and not item.disabled:
                    foundSpawner = True

        if not foundSpawner:
            self.postHandler()
            return True
        return

    def solver(self,character):
        if self.triggerCompletionCheck(character):
            return
        if not self.subQuests:
            if not character.getBigPosition() == self.targetPosition:
                quest = GoToTile(targetPosition=self.targetPosition)
                self.addQuest(quest)
                return
            if character.getDistance((6,6,0)) > 1:
                quest = GoToPosition(targetPosition=(6,6,0),ignoreEndBlocked=True)
                self.addQuest(quest)
                return

            offset = (6-character.xPosition,6-character.yPosition,0-character.zPosition)
            commandMap = {
                    (1,0,0):"Jd",
                    (0,1,0):"Js",
                    (-1,0,0):"Ja",
                    (0,-1,0):"Jw",
                    (0,0,0):"j",
                }
            
            if offset in commandMap:
                quest = src.quests.RunCommand(command=commandMap[offset])
                self.addQuest(quest)
                return

        super().solver(character)


class DestroySpawners(MetaQuestSequence):
    def __init__(self, description="destroy hives"):
        super().__init__()
        self.metaDescription = description
        self.type = "DestroySpawners"

    def generateTextDescription(self):
        hiveText = """Insects near to the hive"""
        text = []
        text.extend(["""
Hives have developed in the abbandoned farms.
Insect grow there and attack the base.
Put an end to those attacks by destroying those hives.

Keep in mind that destroying the hives will agitate the insects.
"""+hiveText+""" will try to kill anybody on the terrain.

This will likely result in a wave of enemies attacking the base.
This may destroy the base so prepare for that attack.

There are hives on the following tiles:

"""])
        for spawner in self.getSpawners(self.character):
            text.extend([str(spawner.getPosition()),"\n"])
        text.extend(["""
The Hives are shown on the minimap as: """,(src.interaction.urwid.AttrSpec("#484", "black"), "##")])
        return text

    def getSpawners(self,character):
        currentTerrain = character.getTerrain()
        spawnersFound = []
        for room in currentTerrain.rooms:
            for item in room.getItemByPosition((6,6,0)):
                if isinstance(item, src.items.itemMap["MonsterSpawner"]):
                    spawnersFound.append(item.container)

        return spawnersFound

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if not self.getSpawners(character):
            self.postHandler()
            return True
        return

    def solver(self,character):
        if self.triggerCompletionCheck(character):
            return

        if not self.subQuests:
            quest = Heal()
            self.addQuest(quest)
            quest = GetEpochReward(doEpochEvaluation=True)
            self.addQuest(quest)
            spawner = random.choice(self.getSpawners(character))
            quest = DestroySpawner(targetPosition=spawner.getPosition())
            self.addQuest(quest)
            quest = PrepareAttack(targetPosition=spawner.getPosition())
            self.addQuest(quest)
        super().solver(character)

class Heal(MetaQuestSequence):
    def __init__(self, description="heal"):
        super().__init__()
        self.metaDescription = description
        self.type = "heal"

    def generateTextDescription(self):
        text = """
You are hurt. Heal yourself.

You can heal yourself using vials.
Use vials to heal yourself.

Press JH to auto heal.
"""
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        foundVial = None
        for item in character.inventory:
            if item.type == "Vial" and item.uses > 0:
                foundVial = item

        if not foundVial:
            self.postHandler()
            return True

        if character.health < character.maxHealth:
            return False

        self.postHandler()
        return True

    def getSolvingCommandString(self,character,dryRun=True):
        if not dryRun:
            self.triggerCompletionCheck(character)
        return "JH"

    def solver(self,character):
        command = self.getSolvingCommandString(character,dryRun=False)
        if command:
            character.runCommandString(command)
            return
        if self.triggerCompletionCheck(character):
            return
        return super().solver(character)

class LootRoom(MetaQuestSequence):
    def __init__(self, description="loot room", roomPos = None):
        super().__init__()
        self.baseDescription = description
        self.metaDescription = self.baseDescription+" %s"%(roomPos,)
        self.type = "LootRoom"
        self.roomPos = roomPos

    def generateTextDescription(self):
        return """
Loot a room. Take everything that is valuable and bring it home.


Go to the room on tile %s and take everything not bolted and valuable.
Clear your inventory afterwards to complete the quest."""%(self.roomPos,)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if len(character.inventory) > 0:
            return False

        if not self.getLoot(character):
            character.awardReputation(amount=200, reason="looted a room")
            self.postHandler()
            return True

        return False

    def solver(self,character):
        self.triggerCompletionCheck(character)

        if not self.subQuests:
            if not character.getFreeInventorySpace() > 0:
                quest = ClearInventory(returnToTile=False)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return
            if not character.getBigPosition() == self.roomPos:
                if len(character.inventory) > 0:
                    quest = ClearInventory(returnToTile=False)
                    self.addQuest(quest)
                    quest.assignToCharacter(character)
                    quest.activate()
                    return
                quest = SecureTile(toSecure=self.roomPos,endWhenCleared=True)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return
            item = self.getLoot(character)
            if not item:
                if len(character.inventory) > 0:
                    quest = ClearInventory(returnToTile=False)
                    self.addQuest(quest)
                    quest.assignToCharacter(character)
                    quest.activate()
                    return

            self.addQuest(RunCommand(command="k", description="pick up loot"))
            self.addQuest(GoToPosition(targetPosition=item.getPosition(),description="go to loot"))
            return

        super().solver(character)

    def getLoot(self,character):
        currentTerrain = character.getTerrain()
        rooms = currentTerrain.getRoomByPosition(self.roomPos)
        if not rooms:
            return None

        for item in rooms[0].itemsOnFloor:
            if item.type in ("Scrap",):
                continue
            if not item.bolted:
                return item

        return None

    def droppedItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.droppedItem, "dropped")

        return super().assignToCharacter(character)

class SecureTiles(MetaQuestSequence):
    def __init__(self, description="secure tiles", toSecure=None):
        super().__init__()
        self.metaDescription = description
        self.type = "SecureTiles"
        self.toSecure = toSecure

    def generateTextDescription(self):
        text = """
Secure a group of tiles.

Secure the following tiles:

"""
        for tile in self.toSecure:
            text += str(tile)+"\n"
        return text

    def triggerCompletionCheck(self,character=None):
        if self.toSecure:
            return False

        self.postHandler()
        return True

    def solver(self,character):
        self.triggerCompletionCheck(character)
        if not self.subQuests:
            targetPosition = self.toSecure.pop()
            quest = src.quests.SecureTile(toSecure=targetPosition,endWhenCleared=True)
            quest.assignToCharacter(character)
            quest.activate()
            self.addQuest(quest)
            return
        super().solver(character)

class SecureTile(GoToTile):
    def __init__(self, description="secure tile", toSecure=None, endWhenCleared=False, reputationReward=0,rewardText=None):
        super().__init__(description=description,targetPosition=toSecure)
        self.metaDescription = description
        self.type = "SecureTile"
        self.endWhenCleared = endWhenCleared
        self.reputationReward = reputationReward
        self.rewardText = rewardText
        self.huntdownCooldown = 0

    def generateTextDescription(self):
        text  = """
Secure the tile %s.

This means you should go to the tile and kill all enemies you find."""%(self.targetPosition,)
        if not self.endWhenCleared:
            text = "\n"+text+"\n\nStay there and kill all enemies arriving"
        else:
            text = "\n"+text+"\n\nthe quest will end after you do this"
        text += """

You can attack enemies by walking into them.
But you can use your environment to your advantage, too.
Try luring enemies into landmines or detonating some bombs."""

        return text

    def wrapedTriggerCompletionCheck2(self, extraInfo):
        self.triggerCompletionCheck(extraInfo["character"])

    def handleTileChange2(self):
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.wrapedTriggerCompletionCheck2, "character died on tile")
        self.startWatching(character,self.handleTileChange2, "changedTile")

        super().assignToCharacter(character)

    def postHandler(self,character=None):
        if self.reputationReward and character:
            if self.rewardText:
                text = self.rewardText
            else:
                text = "securing a tile"
            character.awardReputation(amount=50, reason=text)
        super().postHandler()

    def triggerCompletionCheck(self,character=None):

        if not character:
            return False

        if not self.endWhenCleared:
            return False

        if isinstance(character.container,src.rooms.Room):
            if character.container.xPosition == self.targetPosition[0] and character.container.yPosition == self.targetPosition[1]:
                foundEnemy = None
                for enemy in character.container.characters:
                    if enemy.faction == character.faction:
                        continue
                    foundEnemy = enemy
                if not foundEnemy:
                    self.postHandler(character)
                    return True
        else:
            if character.xPosition//15 == self.targetPosition[0] and character.yPosition//15 == self.targetPosition[1]:
                foundEnemy = None
                for enemy in character.container.characters:
                    if not (enemy.xPosition//15 == character.xPosition//15 and enemy.yPosition//15 == character.yPosition//15):
                        continue
                    if enemy.faction == character.faction:
                        continue
                    foundEnemy = enemy
                if not foundEnemy:
                    self.postHandler(character)
                    return True

        return False

    def solver(self,character):
        if self.completed:
            return
        if not self.active:
            return

        if self.triggerCompletionCheck(character):
            return

        try:
            self.huntdownCooldown -= 1
        except:
            self.huntdownCooldown = 0
        if self.huntdownCooldown < 0:
            enemies = character.getNearbyEnemies()
            if enemies:
                self.huntdownCooldown = 100
                if random.random() < 0.3:
                    quest = Huntdown(target=random.choice(enemies))
                    quest.autoSolve = True
                    character.assignQuest(quest,active=True)
                    return

        super().solver(character)

class GoToPosition(Quest):
    def __init__(self, description="go to position", creator=None,targetPosition=None,ignoreEnd=False,ignoreEndBlocked=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.targetPosition = None
        self.description = description
        self.metaDescription = description
        self.hasListener = False
        self.ignoreEndBlocked = False
        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})
        if ignoreEndBlocked:
            self.setParameters({"ignoreEndBlocked":ignoreEndBlocked})
        self.type = "GoToPosition"

        self.tuplesToStore.append("targetPosition")
        
        self.shortCode = "g"
        self.smallPath = []

    def generateTextDescription(self):
        extraText = ""
        if self.ignoreEndBlocked:
            extraText = """

The position you should go might be blocked.
So it is enough to go next to the target position to end this quest.
"""

        text = """
go to position %s in the same room you are in.

This quest ends after you do this."""%(self.targetPosition,) 
        return text

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        self.getSolvingCommandString(character)
        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if self.smallPath:
            if isinstance(character.container,src.rooms.Room):
                pos = (character.xPosition,character.yPosition)
            else:
                pos = (character.xPosition%15,character.yPosition%15)
            for step in self.smallPath:
                pos = (pos[0]+step[0],pos[1]+step[1])
                result.append((pos,"path"))
        return result

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return
        if self.completed:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")

        super().assignToCharacter(character)

    def getSolvingCommandString(self, character, dryRun=True):
        if character.macroState.get("submenue"):
            return ["esc"]
        if character.xPosition%15 == 0:
            return "d"
        if character.xPosition%15 == 14:
            return "a"
        if character.yPosition%15 == 0:
            return "s"
        if character.yPosition%15 == 14:
            return "w"
        if not self.targetPosition:
            return ".12.."

        localRandom = random.Random(self.randomSeed)

        if isinstance(character.container,src.rooms.Room):
            (command,self.smallPath) = character.container.getPathCommandTile(character.getPosition(),self.targetPosition,localRandom=localRandom,ignoreEndBlocked=self.ignoreEndBlocked,character=character)
            if not command:
                (command,self.smallPath) = character.container.getPathCommandTile(character.getPosition(),self.targetPosition,localRandom=localRandom,tryHard=True,ignoreEndBlocked=self.ignoreEndBlocked,character=character)
            if not command:
                return None
            return command
        else:
            charPos = (character.xPosition%15,character.yPosition%15,character.zPosition%15)
            tilePos = (character.xPosition//15,character.yPosition//15,character.zPosition//15)

            (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,self.targetPosition,localRandom=localRandom,ignoreEndBlocked=self.ignoreEndBlocked,character=character)
            if not command:
                (command,self.smallPath) = character.container.getPathCommandTile(tilePos,charPos,self.targetPosition,localRandom=localRandom,tryHard=True,ignoreEndBlocked=self.ignoreEndBlocked,character=character)
            if not command:
                return None
            return command

    def triggerCompletionCheck(self, character=None):
        if not self.targetPosition:
            return False
        if not character:
            return False
        if not self.active:
            return

        if character.xPosition%15 == self.targetPosition[0] and character.yPosition%15 == self.targetPosition[1]:
            self.postHandler()
            return True
        if self.ignoreEndBlocked:
            if abs(character.xPosition%15-self.targetPosition[0])+abs(character.yPosition%15-self.targetPosition[1]) == 1:
                self.postHandler()
                return True
        return False

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
            self.description = self.metaDescription+" %s"%(self.targetPosition,)
        if "ignoreEndBlocked" in parameters and "ignoreEndBlocked" in parameters:
            self.ignoreEndBlocked = parameters["ignoreEndBlocked"]
        return super().setParameters(parameters)

    def solver(self, character):
        self.triggerCompletionCheck(character)
        commandString = self.getSolvingCommandString(character)
        self.randomSeed = random.random()
        if commandString:
            character.runCommandString(commandString)
            return False
        else:
            self.fail()
            return True

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

class GoHome(MetaQuestSequence):
    def __init__(self, description="go home", creator=None, paranoid=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.baseDescription = description
        # save initial state and register
        self.type = "GoHome"
        self.addedSubQuests = False
        self.paranoid = paranoid
        self.cityLocation = None

        self.attributesToStore.extend([
            "hasListener","addedSubQuests","paranoid"])

        self.tuplesToStore.append("cityLocation")

    def generateTextDescription(self):
        return """
Go home.

You consider the command center of the base your home.
That command centre holds the assimilator and
other important artworks like the quest artwork.

Many activities can be started from the command centre.
Go there and be ready for action.



Quests like this can be pretty boring.
Press c now to use auto move to complete this quest.
Be careful with auto move, while danger is nearby. 
Press crtl-d to stop your character from moving.
"""

    def triggerCompletionCheck(self, character=None):
        if not character:
            return
        if not self.cityLocation:
            return

        if isinstance(character.container, src.rooms.Room):
            if (character.container.xPosition == self.cityLocation[0] and character.container.yPosition == self.cityLocation[1]):
                character.reputation += 1
                self.postHandler()

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return
        self.reroll()

        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        self.setHomeLocation(character)

        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")

        super().assignToCharacter(character)

    def setHomeLocation(self,character):
        self.cityLocation = (character.registers["HOMEx"],character.registers["HOMEy"])
        self.metaDescription = self.baseDescription+" %s/%s"%(self.cityLocation[0],self.cityLocation[1],)

    def generateSubquests(self,character):
        if not self.addedSubQuests:

            quest = GoToTile(paranoid=self.paranoid)
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            quest.setParameters({"targetPosition":(self.cityLocation[0],self.cityLocation[1])})

            self.addedSubQuests = True
            return True
        if self.triggerCompletionCheck(character):
            return True
        return False

    def solver(self, character):
        if self.generateSubquests(character):
            return False

        if self.subQuests:
            return super().solver(character)

        character.runCommandString(self.getSolvingCommandString(character))
        return False

    def getSolvingCommandString(self,character,dryRun=True):
        if self.subQuests:
            return self.subQuests[0].getSolvingCommandString(character,dryRun=dryRun)
        else:
            charPos = (character.xPosition%15,character.yPosition%15,0)
            if charPos in ((0,7,0),(0,6,0)):
                return "d"
            if charPos in ((7,14,0),(6,12,0)):
                return "w"
            if charPos in ((7,0,0),(6,0,0)):
                return "s"
            if charPos in ((14,7,0),(12,6,0)):
                return "a"

class GrabSpecialItem(Quest):
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

class EnterEnemyCity(MetaQuestSequence):
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

class ObtainSpecialItem(MetaQuestSequence):

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

    def triggerCompletionCheck(self):
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

                quest = Equip(lifetime=400)
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

                #quest = StandAttention()
                #self.addQuest(quest)
                homeLocation = (character.registers["HOMEx"],character.registers["HOMEy"])

                # order is reverse to order in code

                # return the loot
                quest = DeliverSpecialItem()
                self.addQuest(quest)
                quest.itemID = self.itemID

                quest = GoToTile()
                quest.setParameters({"targetPosition":(homeLocation[0],homeLocation[1]+1)})
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)

                quest = GoHome(paranoid=self.paranoid)
                self.addQuest(quest)

                quest = GoToTile(paranoid=self.paranoid)
                quest.setParameters({"targetPosition":(self.itemLocation[0],self.itemLocation[1]-3)})
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)

                lifetime = None
                if self.initialLifetime:
                    lifetime = self.initialLifetime//2

                # grab the item
                quest = GrabSpecialItem(lifetime=lifetime)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                quest.itemID = self.itemID

                # enter the city
                quest = EnterEnemyCity(lifetime=lifetime)
                self.addQuest(quest)
                quest.setCityLocation(self.itemLocation)
                quest.assignToCharacter(character)
                quest.activate()

                # enter the city
                quest = GoToTile(lifetime=lifetime,paranoid=self.paranoid)
                quest.setParameters({"targetPosition":(self.itemLocation[0],self.itemLocation[1])})
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)

                # go near enemy city
                quest = GoToTile(lifetime=lifetime,paranoid=self.paranoid)
                quest.setParameters({"targetPosition":(self.itemLocation[0],self.itemLocation[1]-3)})
                quest.assignToCharacter(character)
                quest.activate()
                quest.reputationReward = 30
                self.addQuest(quest)

                # leave city
                quest = GoToTile(lifetime=lifetime,paranoid=False)
                quest.setParameters({"targetPosition":(homeLocation[0],homeLocation[1]-2)})
                quest.assignToCharacter(character)
                quest.activate()
                self.addQuest(quest)

                quest = Equip(lifetime=300)
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
class DummyQuest(Quest):
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

    def triggerCompletionCheck(self):
        return

class GetEpochReward(MetaQuestSequence):
    def __init__(self, description="spend epoch reward", creator=None, doEpochEvaluation=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

        self.doEpochEvaluation = doEpochEvaluation
        self.type = "GetEpochReward"
        self.gotEpochEvaluation = False

    def getSolvingCommandString(self,character,dryRun=True):
        if character.getBigPosition() == (7,7,0):
            if character.getPosition() == (6,7,0):
                if self.doEpochEvaluation and not self.gotEpochEvaluation:
                    return list("Jw."+"ssj")+3*["enter"]+["esc"]
                else:
                    return list("Jw."+"sj"+"sj")+["enter"]+["esc"]
        return super().getSolvingCommandString(character)

    def generateTextDescription(self):
        text = ""
        if self.doEpochEvaluation and not self.gotEpochEvaluation:
            text += """
You completed a task for the epoch artwork.
Get a epoch review to get credited with the glass tears you earned.
Use the epoch artwork to get the epoch review.

"""
        text += """
You accumulated some glass tears.
You can use them at the epoch artwork to buy upgrades for yourself and the base.


In auto mode this quest will use the auto spend option.
That option will spend your glass tears on something.
So you might want to check out the other option and buy useful stuff.


Use the epoch artwork to spend your glass tears.
"""
        return text

    def triggerCompletionCheck(self, character=None):
        if not character:
            return

        if self.doEpochEvaluation and not self.gotEpochEvaluation:
            return

        if self.getEpochQuestCharges(character) < 10:
            self.postHandler()
            return

        if (character.health >= character.maxHealth and
            character.weapon and character.weapon.baseDamage >= 25 and
            character.armor and character.armor.armorValue >= 5):
            self.postHandler()
            return

        return

    def handleGotEpochEvaluation(self):
        self.gotEpochEvaluation = True
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleGotEpochEvaluation, "got epoch evaluation")

        super().assignToCharacter(character)

    def getEpochQuestCharges(self,character):
        room = character.getHomeRoom()
        epochArtwork = room.getItemByPosition((6,6,0))[0]
        return epochArtwork.charges

    def generateSubquests(self,character): 
        
        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return

        pos = character.getBigPosition()

        if pos == (7,7,0):
            if not character.getPosition() == (6,7,0):
                quest = GoToPosition(targetPosition=(6,7,0), description="go to epoch artwork")
                quest.activate()
                self.addQuest(quest)
                return

            return

        directions = {
                (7,5,0):"south",
                (7,6,0):"west",
                (8,6,0):"south",
                (6,6,0):"south",
                (8,7,0):"south",
                (6,7,0):"south",
                (8,8,0):"south",
                (6,8,0):"south",
                (8,9,0):"west",
                (6,9,0):"east",
                (7,9,0):"north",
                (7,8,0):"north",
                }

        quest = src.quests.GoHome(description="go to command centre")
        self.addQuest(quest)

        return

    def solver(self,character):
        self.triggerCompletionCheck(character)
        self.generateSubquests(character)

        super().solver(character)

class DoEpochChallenge(MetaQuestSequence):
    def __init__(self, description="do epoch challenge", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

        self.type = "DoEpochChallenge"

    def generateTextDescription(self):
        text = """
Complete a task for the epoch artwork.

Use the epoch artwork to fetch a task and complete it.
"""
        return text

    """
    never complete
    """
    def triggerCompletionCheck(self, character=None):
        return

    def getSolvingCommandString(self,character,dryRun=True):
        pos = character.getBigPosition()
        if pos == (7,7,0):
            if character.getPosition() == (6,7,0):
                return list("Jw.")+["enter"]*2
        return super().getSolvingCommandString(character)

    def generateSubquests(self,character): 
        
        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return

        pos = character.getBigPosition()

        if pos == (7,7,0):
            if not character.getPosition() == (6,7,0):
                quest = GoToPosition(targetPosition=(6,7,0), description="go to epoch artwork")
                quest.activate()
                self.addQuest(quest)
                return
            return

        quest = src.quests.GoHome(description="go to command centre")
        self.addQuest(quest)
        quest.assignToCharacter(character)
        quest.activate()
        return

    def solver(self,character):
        if self.triggerCompletionCheck(character):
            return
        if not self.subQuests:
            self.generateSubquests(character)

            if self.subQuests:
                return

        """
        command = self.getSolvingCommandString(character)
        if command:
            character.runCommandString(command)
            return
        """

        super().solver(character)

# every epoch:
#  go to epoch artwork and fetch epoch challenge
#  defend base
#  get rewards/punishment
class EpochQuest(MetaQuestSequence):
    """
    state initialization
    """

    def __init__(self, description="epoch quest", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

        # save initial state and register
        self.type = "EpochQuest"

        #quest = DefendBase()
        #self.subQuests.append(quest)

        #quest = ManageBase()
        #self.subQuests.append(quest)

        quest = DoEpochChallenge()
        self.subQuests.append(quest)
        quest.activate()

    def generateTextDescription(self):
        text = """
When you were promoted to commander of this base you recieved the burden of the epoch quest.

This means you will have to complete the tasks the epoch artwork gives you.

Completing tasks will reward you with glass tears.
Those glass tears can be used to upgrade your character or your base.


Use the epoch artwork to get tasks and collect your rewards.
"""
        return text

    """
    never complete
    """
    def triggerCompletionCheck(self):
        return

# map strings to Classes
questMap = {
    "Quest": Quest,
    "EnterEnemyCity": EnterEnemyCity,
    "MetaQuestSequence": MetaQuestSequence,
    "MetaQuestParralel": MetaQuestParralel,
    "NaiveMoveQuest": NaiveMoveQuest,
    "NaiveEnterRoomQuest": NaiveEnterRoomQuest,
    "NaivePickupQuest": NaivePickupQuest,
    "NaiveGetQuest": NaiveGetQuest,
    "NaiveGetReward": NaiveGetReward,
    "NaiveMurderQuest": NaiveMurderQuest,
    "NaiveActivateQuest": NaiveActivateQuest,
    "NaiveDropQuest": NaiveDropQuest,
    "NaiveDelegateQuest": NaiveDelegateQuest,
    "WaitQuest": WaitQuest,
    "WaitForDeactivationQuest": WaitForDeactivationQuest,
    "WaitForQuestCompletion": WaitForQuestCompletion,
    "DrinkQuest": DrinkQuest,
    "SurviveQuest": SurviveQuest,
    "EnterRoomQuestMeta": EnterRoomQuestMeta,
    "MoveQuestMeta": MoveQuestMeta,
    "DropQuestMeta": DropQuestMeta,
    "PickupQuestMeta": PickupQuestMeta,
    "ActivateQuestMeta": ActivateQuestMeta,
    "RefillDrinkQuest": RefillDrinkQuest,
    "CollectQuestMeta": CollectQuestMeta,
    "GetQuest": GetQuest,
    "GetReward": GetReward,
    "MurderQuest": MurderQuest,
    "FillPocketsQuest": FillPocketsQuest,
    "LeaveRoomQuest": LeaveRoomQuest,
    "PatrolQuest": PatrolQuest,
    "ExamineQuest": ExamineQuest,
    "FetchFurniture": FetchFurniture,
    "PlaceFurniture": PlaceFurniture,
    "ConstructRoom": ConstructRoom,
    "TransportQuest": TransportQuest,
    "StoreCargo": StoreCargo,
    "MoveToStorage": MoveToStorage,
    "HandleDelivery": HandleDelivery,
    "KeepFurnacesFiredMeta": KeepFurnacesFiredMeta,
    "KeepFurnaceFiredMeta": KeepFurnaceFiredMeta,
    "FireFurnaceMeta": FireFurnaceMeta,
    "FillGrowthTankMeta": FillGrowthTankMeta,
    "HopperDuty": HopperDuty,
    "ClearRubble": ClearRubble,
    "RoomDuty": RoomDuty,
    "Serve": Serve,
    "DummyQuest": DummyQuest,
    "ObtainSpecialItem": ObtainSpecialItem,
    "ObtainAllSpecialItems": ObtainAllSpecialItems,
    "EnterEnemyCity": EnterEnemyCity,
    "DeliverSpecialItem": DeliverSpecialItem,
    "GoHome": GoHome,
    "GatherItems": GatherItems,
    "GrabSpecialItem": GrabSpecialItem,
    "StandAttention": StandAttention,
    "ProtectSuperior": ProtectSuperior,
    "SecureTile": SecureTile,
    "GoToTile": GoToTile,
    "Equip": Equip,
    "RestockRoom": RestockRoom,
    "GoToPosition": GoToPosition,
    "GatherScrap": GatherScrap,
    "ClearTerrain": ClearTerrain,
    "TeleportToTerrain": TeleportToTerrain,
    "LootRuin": LootRuin,
    "DestroyRooms": DestroyRooms,
    "DestroyRoom": DestroyRoom,
    "ManageBase": ManageBase,
    "DefendBase": DefendBase,
    "BreakSiege": BreakSiege,
    "ControlBase": ControlBase,
    "AssignStaff": AssignStaff,
    "CleanTraps": CleanTraps,
    "ReloadTraps": ReloadTraps,
    "ClearInventory": ClearInventory,
    "DestroySpawners": DestroySpawners,
    "TakeOverBase": TakeOverBase,
    "Assimilate": Assimilate,
    "TrainSkill": TrainSkill,
    "LootRoom": LootRoom,
    "EpochQuest": EpochQuest,
    "ClearTile": ClearTile,
    "ReloadTraproom": ReloadTraproom,
    "GetBodyGuards": GetBodyGuards,
    "OperateMachine": OperateMachine,
    "ChangeJob": ChangeJob,
    "RunCommand":RunCommand,
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
