"""
quests and quest related code
"""

# import basic libs
import json

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

############################################################
#
#   building block quests
#   not intended for direct use unless you know what you are doing
#
############################################################


class MurderQuest2(src.saveing.Saveable):
    """
    straightforward state initialization
    """

    def __init__(
        self,
        followUp=None,
        startCinematics=None,
        lifetime=None,
        creator=None,
        failTrigger=None,
    ):
        super().__init__()
        self.completed = False
        self.active = False
        self.toKill = None
        self.type = "murder"
        self.character = None
        self.information = None
        self.watched = []

        # set id
        import uuid

        self.id = uuid.uuid4().hex

        self.attributesToStore.extend(["completed", "active", "information", "type"])
        self.objectsToStore.extend(["character", "toKill"])

    """
    set state as dict
    """

    def setState(self, state):
        super().setState(state)

        # set character
        if "toKill" in state and state["toKill"]:
            """
            set value
            """

            def watchCharacter(character):
                self.setTarget(character)

            src.saveing.loadingRegistry.callWhenAvailable(
                state["toKill"], watchCharacter
            )

    """
    register callback
    """

    def startWatching(self, target, callback, tag=""):
        target.addListener(callback, tag)
        self.watched.append((target, callback))

    """
    unregister callback
    """

    def stopWatching(self, target, callback, tag=""):
        target.delListener(callback, tag)
        self.watched.remove((target, callback))

    def setTarget(self, target):
        self.toKill = target
        self.startWatching(target, self.handleKill, "died")

    def handleKill(self, info):
        self.completed = True
        self.character.addMessage("handle kill")

    def assignToCharacter(self, character):
        self.character = character

    def activate(self):
        pass

    def getDescription(self, asList=False, colored=False, active=False):
        text = "%s %s" % (
            self.type,
            self.toKill.charType,
        )
        if self.completed:
            text += " (completed)"
        else:
            text += " (not completed)"

        if self.information:
            text += " %s" % (self.information,)
        return text


"""
the base class for all quests
"""


class Quest(src.saveing.Saveable):
    """
    straightforward state initialization
    """

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
        self.type = "Quest"
        self.followUp = followUp  # deprecate?
        self.character = (
            None  # should be more general like owner as preparation for room quests
        )
        self.listener = (
            []
        )  # the list of things caring about this quest. The owner for example
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

        # set up saving
        # bad code: extend would be better
        self.attributesToStore.append("type")
        self.attributesToStore.append("active")
        self.attributesToStore.append("completed")
        self.attributesToStore.append("reputationReward")
        self.attributesToStore.append("lifetime")
        self.attributesToStore.extend(["dstX", "dstY"])
        self.callbacksToStore.append("endTrigger")
        self.objectsToStore.append("character")
        self.objectsToStore.append("target")
        self.objectsToStore.append("lifetimeEvent")

        self.lifetime = lifetime
        self.lifetimeEvent = None

        # set id
        import uuid

        self.id = uuid.uuid4().hex

    """
    register callback
    """

    def startWatching(self, target, callback):
        target.addListener(callback)
        self.watched.append((target, callback))

    """
    unregister callback
    """

    def stopWatching(self, target, callback):
        target.delListener(callback)
        self.watched.remove((target, callback))

    """
    unregister all callback
    """

    def stopWatchingAll(self):
        for listenItem in self.watched[:]:
            self.stopWatching(listenItem[0], listenItem[1])

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

    """
    get the quests description
    bad code: colored and asList are somewhat out of place
    """

    def getDescription(self, asList=False, colored=False, active=False):
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
                return [[self.description, "\n"]]
        else:
            return self.description

    """
    tear the quest down
    """

    def postHandler(self):
        # stop listening
        self.stopWatchingAll()

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "this should not happen (posthandler called on inactive quest ("
                + str(self)
                + ")) "
                + str(self.character)
            )
            return

        # smooth over impossible state
        if not self.character:
            src.interaction.debugMessages.append(
                "this should not happen (posthandler called on quest without character ("
                + str(self)
                + ")) "
                + str(self.character)
            )

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
            src.interaction.debugMessages.append(
                "this should not happen (posthandler called on completed quest ("
                + str(self)
                + ")) "
                + str(self.character)
            )
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

        # flag self as completed
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

        # deactivate
        self.deactivate()

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

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on inactive quest: " + str(self)
            )
            return

        self.triggerCompletionCheck()

    """
    notify listeners that something changed
    bad code: should be extra class
    """

    def changed(self):
        # call the listener functions
        # should probably be an event not a function
        for listener in self.listener:
            listener()

    """
    add a callback to be called if the quest changes
    bad code: should be extra class
    """

    def addListener(self, listenFunction):
        if listenFunction not in self.listener:
            self.listener.append(listenFunction)

    """
    remove a callback 
    bad code: should be extra class
    """

    def delListener(self, listenFunction):
        if listenFunction in self.listener:
            self.listener.remove(listenFunction)

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
            self.lifetimeEvent = src.events.EndQuestEvent(
                src.gamestate.gamestate.tick + self.lifetime,
                callback={"container": self, "method": "timeOut"},
                creator=self,
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


"""
a container quest containing a list of quests that have to be handled in sequence
"""


class MetaQuestSequence(Quest):
    """
    state initialization
    bad code: quest parameter does not work anymore and should be removed
    """

    def __init__(
        self,
        quests=[],
        followUp=None,
        failTrigger=None,
        startCinematics=None,
        lifetime=None,
        creator=None,
    ):
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

            # update changed quests
            if "changed" in state["subQuests"]:
                for thing in self.subQuests:
                    if thing.id in state["subQuests"]["states"]:
                        thing.setState(state["subQuests"]["states"][thing.id])

            # remove quests
            if "removed" in state["subQuests"]:
                for thing in self.subQuests:
                    if thing.id in state["subQuests"]["removed"]:
                        self.subQuests.remove(thing)

            # add new quests
            if "new" in state["subQuests"]:
                for thingId in state["subQuests"]["new"]:
                    thingState = state["subQuests"]["states"][thingId]
                    thing = getQuestFromState(thingState)
                    thing.setState(thingState)
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
        # add name of the actual quest
        out = self.metaDescription + ":\n"
        if self.lifetimeEvent:
            out += (
                " ("
                + str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)
                + " / "
                + str(self.lifetime)
                + ")"
            )
        for quest in self.subQuests:
            # add quests
            if quest.active:
                out += "    > " + "\n      ".join(quest.description.split("\n")) + "\n"
            else:
                out += "    x " + "\n      ".join(quest.description.split("\n")) + "\n"
        return out

    """
    get a more detailed description 
    bad code: asList and colored are out of place
    bad code: the asList and colored mixup leads to ugly code
    """

    def getDescription(self, asList=False, colored=False, active=False):
        # add name of the actual quest
        if asList:
            if colored:
                import urwid

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
                        "\n",
                    ]
                ]
            else:
                out = [[self.metaDescription + ":", "\n"]]
        else:
            out = self.metaDescription + ":\n"

        # add remaining time
        if self.lifetimeEvent:
            out += (
                " ("
                + str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)
                + " / "
                + str(self.lifetime)
                + ")"
            )

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

    """
    assign self and first subquest to character
    """

    def assignToCharacter(self, character):
        for quest in self.subQuests:
            quest.assignToCharacter(character)
        super().assignToCharacter(character)

    """
    check if there are quests left
    """

    def triggerCompletionCheck(self):

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "triggerCompletionCheck called on inactive " + str(self)
            )
            return

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

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "recalculate called on inactive " + str(self)
            )
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

    def addQuest(self, quest, addFront=True):
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
        if self.subQuests[0]:
            self.startWatching(self.subQuests[0], self.recalculate)

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
        if len(self.subQuests):
            self.subQuests[0].solver(character)

    """
    deactivate self and first subquest
    """

    def deactivate(self):
        if len(self.subQuests):
            if self.subQuests[0].active:
                self.subQuests[0].deactivate()
        super().deactivate()


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
        self.objectsToStore.append("lastActive")
        while "dstX" in self.attributesToStore:
            self.attributesToStore.remove("dstX")
        while "dstY" in self.attributesToStore:
            self.attributesToStore.remove("dstY")

        # store initial state and register
        self.type = "MetaQuestParralel"

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
        super().assignToCharacter(character)
        self.startWatching(character, self.recalculate)

    """
    close door and call superclass
    """

    def postHandler(self):
        # smooth over impossible state
        if not self.character.room:
            src.interaction.debugMessages.append(
                "posthandler called without beeing in a room"
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

    def __init__(self, quest=None, followUp=None, startCinematics=None, creator=None):
        super().__init__(followUp, startCinematics=startCinematics, creator=creator)
        self.quest = quest
        self.description = "naive get reward"
        self.done = False

        # set metadata for saving
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

        self.toKill.addListener(self.triggerCompletionCheck, "died")

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
        self.target.addListener(self.triggerCompletionCheck, "woke up")
        self.target.addListener(self.triggerCompletionCheck, "died")

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
        super().activate()
        self.character.addListener(self.registerActivation, "activate")

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
            self.character.addListener(self.registerActivation, "activate")

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
        self.character.addListener(self.triggerCompletionCheck, "drop")

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
        self.description = "please wait"
        super().__init__(lifetime=lifetime, creator=creator)

        # save initial state and register
        self.type = "WaitQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)

    """
    do nothing
    """

    def solver(self, character):
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
        super().assignToCharacter(character)
        self.startWatching(character, self.recalculate)

    """
    spawn quests to take care of basic needs
    """

    def recalculate(self):

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
                if self.character == mainChar:
                    self.addMessage("you need to drink")
                self.drinkQuest = DrinkQuest(creator=self)
                self.character.assignQuest(self.drinkQuest, active=True)


"""
quest for entering a room
"""


class EnterRoomQuestMeta(MetaQuestSequence):
    """
    basic state initialization
    """

    def __init__(self, room=None, followUp=None, startCinematics=None, creator=None):
        super().__init__([], creator=creator)
        self.room = room
        if room:
            self.addQuest(NaiveEnterRoomQuest(room, creator=self))
        self.recalculate()
        self.metaDescription = "enterroom Meta"
        self.leaveRoomQuest = None

        # set metadata for saving
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
        self.objectsToStore.append("questDispenser")

        # save initial state and register
        self.type = "GetQuest"

    """
    check if a quest was aquired
    """

    def triggerCompletionCheck(self):

        # smooth over impossible state
        if not self.active:
            src.interaction.debugMessages.append(
                "triggerCompletionCheck called on inactive quest: " + str(self)
            )
            return

        # check completion condition
        if not self.quest:
            src.interaction.debugMessages.append(
                "triggerCompletionCheck called on quest without quest: " + str(self)
            )
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
bad code: this quest is not used and may be broken
"""


class PatrolQuest(MetaQuestSequence):
    """
    state initialization
    """

    def __init__(
        self,
        waypoints=[],
        startCinematics=None,
        looped=True,
        lifetime=None,
        creator=None,
    ):
        # bad code: superconstructor doesn't actually process the looped parameter
        super().__init__(
            quests,
            startCinematics=startCinematics,
            looped=looped,
            creator=creator,
            lifetime=lifetime,
        )

        # add movement between waypoints
        quests = []
        for waypoint in waypoints:
            quest = MoveQuestMeta(waypoint[0], waypoint[1], waypoint[2], creator=self)
            self.addQuest(quest)

        # save initial state and register
        self.type = "PatrolQuest"
        self.initialState = self.getState()
        src.saveing.loadingRegistry.register(self)


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
        self.character.addListener(self.registerExaminination, "examine")
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

        self.character.addListener(self.registerExaminination, "examine")

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
                sub.addListener(self.rescueSub, "fallen unconcious")

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

        self.objectsToStore.append("furnace")

        # listen to furnace
        self.startWatching(self.furnace, self.recalculate)

        # save initial state and register
        self.type = "KeepFurnaceFiredMeta"

    """
    add sub quests
    """

    def recalculate(self):
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
        self.objectsToStore.append("furnace")

        # save initial state and register
        self.type = "FireFurnaceMeta"

    """
    collect coal and fire furnace
    """

    def recalculate(self):

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
        character.addListener(self.recalculate)
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
        self.objectsToStore.append("growthTank")

        # save initial state and register
        self.type = "FillGrowthTankMeta"

    """
    fetch goo and refill the machine
    """

    def recalculate(self):

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
        character.addListener(self.recalculate)
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

    """
    never complete
    """

    def triggerCompletionCheck(self):
        return


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


# map strings to Classes
questMap = {
    "Quest": Quest,
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
    "MurderQuest2": MurderQuest2,
    "murder": MurderQuest2,
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
}

"""
get quest instance from state dict
"""


def getQuestFromState(state):
    quest = questMap[state["type"]]()
    quest.setState(state)
    src.saveing.loadingRegistry.register(quest)
    return quest
