"""
cinematics and related code belong here
"""

# import basic libs
import json

# import basic internal libs
import src.chats
import src.saveing
import src.logger
import src.interaction
import src.gamestate
import src.urwidSpecials

cinematicQueue = []

class BasicCinematic(src.saveing.Saveable):
    """
    the base class for all Cinamatics
    """

    def __init__(self):
        """
        basic state setting and id generation
        """

        self.attributesToStore = super().attributesToStore[:]
        self.callbacksToStore = []
        self.objectsToStore = []
        self.tupleDictsToStore = []
        self.tupleListsToStore = []

        super().__init__()

        # initialize basic state
        self.background = False
        self.followUp = None
        self.skipable = False
        self.overwriteFooter = True
        self.footerText = ""
        self.endTrigger = None
        self.type = "BasicCinematic"
        self.aborted = False

        # add save information
        self.attributesToStore.extend(
            ["background", "overwriteFooter", "footerText", "type", "skipable"]
        )
        self.callbacksToStore.append("endTrigger")

        # generate unique id
        import uuid

        self.id = uuid.uuid4().hex

    def advance(self):
        """
        do nothing
        """

        return False

    def abort(self):
        """
        set aborted flag
        """

        self.aborted = True
        pass

    def addSubmenuToCinematicQueue(self):
        """
        adds self to the list of cinematics
        """

        # bad code: hooks the submenu directly into the interaction
        src.interaction.submenue = self.submenue
        src.interaction.submenue.followUp = self.abort

# obsolete: only used in old storymode
# bad code: should be abstracted and called with a parameter instead of single use special class
class InformationTransfer(BasicCinematic):
    """
    this is a single use cinematic basically. It flashes some info too fast to read in order to symbolise information transfer to the implant
    """

    def __init__(self, information={}):
        """
        initialise own state

        Parameters:
            information: the information to show
        """
        super().__init__()

        self.position = 0
        self.information = list(information.items())

        self.triggered = False
        self.type = "InformationTransfer"

        self.attributesToStore.extend(["information"])


    def advance(self):
        """
        show a piece of information or a really short time
        """

        super().advance()

        # show the information
        if self.position < len(self.information):
            # show the current piece of information
            src.interaction.header.set_text(self.information[self.position][0])
            src.interaction.main.set_text(self.information[self.position][1])

            # trigger showing the next information
            self.position += 1
            self.alarm = src.interaction.loop.set_alarm_in(
                0.2, src.interaction.callShow_or_exit, "~"
            )
            return False

        # show the information
        if not self.triggered:
            # show final message and wait for input
            self.footerText = "press space to proceed"
            src.interaction.header.set_text("")
            src.interaction.main.set_text("InformationTransfer done")
            self.triggered = True
            self.skipable = True
            return False

        return False

    def abort(self):
        """
        stop rendering
        """

        super().abort()

        # clean up
        try:
            src.interaction.loop.remove_alarm(self.alarm)
        except:
            src.logger.debugMessages.append("removed non existant alarm")

# obsolete: only used in old storymode
# bad code: this should be abstracted to have a zoom in/out for various things like the quest menu
class MessageZoomCinematic(BasicCinematic):
    """
    this is a single use cinematic that collapses a full screen message display into the in-game message window
    """

    def __init__(self):
        """
        almost straightforward state initialization
        """

        super().__init__()

        # bad code: the screensize can change while the cinematic is running
        self.screensize = src.interaction.loop.screen.get_cols_rows()
        self.right = self.screensize[0]
        self.left = 0
        self.top = self.screensize[1]
        self.bottom = 0
        self.alarm = None
        self.turnOffCounter = 10
        self.turnOnCounter = 10
        self.text = None
        self.type = "MessageZoomCinematic"

    def advance(self):
        """
        render the message window smaller each step
        """

        super().advance()
        src.gamestate.gamestate.mainChar.terrain = None

        # get the text of the message window if it wasn't retrieved yet
        if not self.text:
            self.text = src.interaction.renderMessages().split("\n")

        # wait for some time till actually doing something
        if self.turnOnCounter:
            self.turnOnCounter -= 1
            src.interaction.header.set_text("\n" + "\n".join(self.text))
            src.interaction.main.set_text("")
            self.alarm = src.interaction.loop.set_alarm_in(
                0.2, src.interaction.callShow_or_exit, "~"
            )
            return False

        # add borders to the text
        # bad code: design elements should be in config
        textWithDeco = ""
        for line in self.text:
            textWithDeco += " " * self.left + "┃ " + line + "\n"
        for i in range(0, self.top - 2 - len(self.text)):
            textWithDeco += " " * self.left + "┃\n"
        textWithDeco += " " * self.left + "┗" + "━" * (self.right - 1)

        # reduce the size till the border fits the message boxes borders
        # bad code: the dimension of the message box is calculated based on assumptions. Size should be asked from the message box
        src.interaction.header.set_text(textWithDeco)
        src.interaction.main.set_text("")
        questWidth = (self.screensize[0] // 3) * 2 + 4
        # shrink X axis
        if self.right > questWidth:
            # fast shrinking
            if self.right > questWidth + 5:
                self.left += 2
                self.right -= 2
            # slow shrinking
            else:
                self.left += 1
                self.right -= 1
        # shrink Y axis
        if self.top > 7:
            self.top -= 1
            self.bottom += 1

        # stop when done
        if not self.right > questWidth and not self.top > 8:
            # wait for some time
            if self.turnOffCounter:
                self.turnOffCounter -= 1
            # stop the cinematic
            else:
                self.alarm = src.interaction.loop.set_alarm_in(
                    0.2, src.interaction.callShow_or_exit, " "
                )
                self.skipable = True
                return False

        # trigger the next movement
        self.alarm = src.interaction.loop.set_alarm_in(
            0.2, src.interaction.callShow_or_exit, "~"
        )

    def abort(self):
        """
        stop rendering
        """

        super().abort()

        # clean up
        try:
            src.interaction.loop.remove_alarm(self.alarm)
        except:
            src.logger.debugMessages.append("removed non existant alarm")

        # trigger follow up functions
        if self.endTrigger:
            self.callIndirect(self.endTrigger)

class TextCinematic(BasicCinematic):
    """
    a cinematic showing a text in various ways
    """
    def __init__(
        self, text="", rusty=False, autocontinue=False, scrolling=False
    ):
        """
        initialise internal state

        Parameters:
            text: the text to show
            rusty: show the text in a rusty style
            autocontinue: autoplay the animation
            scrolling: flag for building up the text slowly
        """

        super().__init__()

        self.text = text
        self.position = 0
        self.alarm = None
        self.endTrigger = None
        self.rusty = rusty
        self.autocontinue = autocontinue
        self.type = "TextCinematic"
        self.firstRun = True

        # add interaction instructions
        if not rusty:
            self.footerText = "press any key to speed up cutscene (not space)"
        else:
            self.footerText = ""

        # flatten text and text information
        import src.urwidSpecials

        self.text = src.urwidSpecials.flattenToPeseudoString(self.text)
        self.endPosition = len(self.text)
        if not scrolling:
            self.position = self.endPosition

        # add meta information for saving
        self.attributesToStore.extend(
            ["text", "endPosition", "position", "rusty", "autocontinue"]
        )

    def advance(self):
        """
        render and advance the state
        """

        super().advance()

        repeat = False
        if self.firstRun:
            repeat = True

        # do nothing if done
        if self.position > self.endPosition and not self.firstRun:
            return
        self.firstRun = False

        # scroll the text in char by char
        if self.position < self.endPosition:
            baseText = self.text[0: self.position]
            if src.interaction.loop:
                if (
                    isinstance(self.text[self.position], str)
                    and self.text[self.position] in "\n"
                ):
                    self.alarm = src.interaction.loop.set_alarm_in(
                        0.5, src.interaction.callShow_or_exit, "~"
                    )
                else:
                    self.alarm = src.interaction.loop.set_alarm_in(
                        0.05, src.interaction.callShow_or_exit, "~"
                    )
            else:
                 src.interaction.callShow_or_exit(None,"~")
            addition = ""

        # show the complete text
        else:
            baseText = self.text
            self.skipable = True
            if not self.autocontinue:
                self.footerText = "press space to proceed"
                if src.interaction.loop:
                    self.alarm = src.interaction.loop.set_alarm_in(
                        0, src.interaction.callShow_or_exit, "~"
                    )
            else:
                if src.interaction.loop:
                    self.alarm = src.interaction.loop.set_alarm_in(
                        0, src.interaction.callShow_or_exit, " "
                    )

        # set or not set rusty colors
        if self.rusty:
            try:
                base = src.urwidSpecials.makeRusty(baseText)
            except:
                base = [baseText]
        else:
            base = [baseText]

        # actually display
        base.append("")
        src.interaction.main.set_text(base)
        src.interaction.header.set_text("")

        # scroll further
        self.position += 1

    def abort(self):
        """
        stop the cinematic
        """

        super().abort()

        # clean up
        try:
            src.interaction.loop.remove_alarm(self.alarm)
        except:
            src.logger.debugMessages.append("removed non existant alarm")

        # trigger follow up actions
        if self.endTrigger:
            self.callIndirect(self.endTrigger)

# bad pattern: locking the players controls without ingame reason results breaking the users expectation
# obsolete: only used in old storymode
class ShowQuestExecution(BasicCinematic):
    """
    a cinematic that shows the execution of a quest
    """

    def __init__(
        self,
        quest=None,
        tickSpan=None,
        assignTo=None,
        background=False,
        container=None,
    ):
        """
        initialise internal state

        Parameters:
            quest: the quest to show
            tickSpan: how long each tick should be
            assignTo: the character to assign the quest to
            background: useless - please ignore
            container: a quest add the quest to
        """

        super().__init__()

        # set meta information for saving
        self.objectsToStore.append("assignTo")
        self.objectsToStore.append("container")
        self.attributesToStore.append("wasSetup")

        self.quest = quest
        self.endTrigger = None
        self.tickSpan = tickSpan
        self.wasSetup = False
        self.assignTo = assignTo
        self.background = background
        self.active = True
        if assignTo and not assignTo.automated:
            self.background = True
            self.active = False
        self.alarm = None
        self.skipable = True
        self.overwriteFooter = False
        self.container = container
        self.type = "ShowQuestExecution"

    def setState(self, state):
        """
        load state from semi serialised state

        Parameters:
            state: the state to set
        """

        super().setState(state)

        # set quest related attributes
        if "quest" in state and state["quest"]:
            if isinstance(state["quest"], str):
                """
                set value
                """

                def setQuest(quest):
                    self.quest = quest

                loadingRegistry.callWhenAvailable(state["quest"], setQuest)
            else:
                import src.quest

                self.quest = src.quests.getQuestFromState(state["quest"])
        else:
            self.quest = None

    def getState(self):
        """
        get state in semi serialised form

        Returns:
            the state
        """

        state = super().getState()

        # get quest related attributes
        if self.quest.character:
            # store reference
            state["quest"] = self.quest.id
        else:
            # store state
            state["quest"] = self.quest.getState()
        return state

    def setup(self):
        """
        assign the quest
        """

        self.wasSetup = True
        if self.assignTo:
            if not self.container:
                self.assignTo.assignQuest(self.quest, active=True)
            else:
                self.container.addQuest(self.quest)
                self.container.recalculate()

    def advance(self):
        """
        advance and show game
        """
        
        super().advance()

        # do setup on the first run
        if not self.wasSetup:
            self.setup()

        # abort if quest is done
        if self.quest.completed:
            src.interaction.loop.set_alarm_in(
                0.0, src.interaction.callShow_or_exit, " "
            )
            self.skipable = True
            return True

        # do one step
        src.interaction.advanceGame()

        # trigger next state
        if self.alarm:
            src.interaction.loop.remove_alarm(self.alarm)
        if self.tickSpan and self.active:
            self.alarm = src.interaction.loop.set_alarm_in(
                self.tickSpan, src.interaction.callShow_or_exit, "."
            )
        else:
            self.alarm = src.interaction.loop.set_alarm_in(
                0.5, src.interaction.callShow_or_exit, "~"
            )
        return True

    def abort(self):
        """
        finish quest and clean up
        """

        super().abort()

        # do setup if not done yet
        if not self.wasSetup:
            self.setup()

        # finish the quest
        # bad code: this has no time limit and is known to hang up the game if the quest cannot be completed
        disableAutomated = False
        while not self.quest.completed:
            if not self.quest.character.automated:
                disableAutomated = True
                self.quest.character.automated = True

            self.advance()
        if disableAutomated:
            self.quest.character.automated = False

        # trigger follow up actions
        if self.endTrigger:
            self.callIndirect(self.endTrigger)

# bad pattern: locking the players controls without ingame reason results breaking the users expectation
# obsolete: only used in old storymode
class ShowGameCinematic(BasicCinematic):
    """
    shows the game and does nothing with the player
    """

    def __init__(self, turns=0, tickSpan=None):
        """
        initialise internal state

        Parameters:
            turns: how many turns the game should be shown
            tickSpan: how long each tick should take
        """
        super().__init__()

        self.turns = turns
        self.endTrigger = None
        self.tickSpan = tickSpan
        self.overwriteFooter = False
        self.type = "ShowGameCinematic"

    def advance(self):
        """
        advance the game
        """

        super().advance()

        # abort when done
        if not self.turns:
            src.interaction.loop.set_alarm_in(
                0.0, src.interaction.callShow_or_exit, " "
            )
            self.skipable = True
            return

        # advance the game
        advanceGame()

        # trigger next step
        self.turns -= 1
        if self.tickSpan:
            src.interaction.loop.set_alarm_in(
                self.tickSpan, src.interaction.callShow_or_exit, "."
            )

        return True

    def abort(self):
        """
        advance game and abort
        """

        super().abort()

        # advance game until desired step
        # bug?: abort is retriggered from within advance
        while self.turns > 0:
            self.turns -= 1
            advanceGame()

        # trigger follow up options
        if self.endTrigger:
            self.callIndirect(self.endTrigger)

# obsolete: only used in old storymode
class ChatCinematic(BasicCinematic):
    """
    triggers a chat
    """

    def __init__(self):
        """
        initialise internal state
        """
        super().__init__()

        self.submenue = src.chats.ChatMenu()
        self.type = "ChatCinematic"


    def advance(self):
        """
        trigger a chat and abort

        Returns:
            flag showing completion
        """

        super().abort()

        self.addSubmenuToCinematicQueue()

        # bad code: removes itself directly from the cinematics queue without using a abstracted function
        global cinematicQueue
        cinematicQueue = cinematicQueue[1:]
        if self.followUp:
            self.followUp()
        if cinematicQueue:
            cinematicQueue[0].advance()
        src.interaction.loop.set_alarm_in(0.0, src.interaction.callShow_or_exit, "~")
        return True

# bad pattern: choices should be in game actions not magic cutscene choices
# obsolete: only used in old storymode
class SelectionCinematic(BasicCinematic):
    """
    this cinematic offers the user a choice and calls a callback depending on this choice
    """
    def __init__(
        self, text=None, options=None, followUps=None, default=None
    ):
        """
        initialise internal state

        Parameters:
            text: the text shown for the selection
            options: the options to selet from
            followUps: the functions to be called depending on the selection
            default: the default selection
        """

        super().__init__()

        self.options = options
        self.default = default
        self.followUps = followUps
        self.text = text
        self.selected = None
        self.submenue = None
        self.type = "SelectionCinematic"

        # add meta information for saving
        self.attributesToStore.append("text")


    #bad code: this is the core function. It should do something
    def advance(self):
        """
        set up and do nothing
        """

        super().advance()

        self.setUp()
        return True

    def setState(self, state):
        """
        set state from semi serialised form

        Parameters:
            state: the state
        """

        super().setState(state)

        # set quest related attributes
        if "options" in state and state["options"]:
            self.options = state["options"]
        if "followUps" in state and state["followUps"]:
            self.followUps = state["followUps"]
            for (key, value) in state["followUps"].items():
                state["followUps"][key] = self.deserializeCallback(value)

    def getState(self):
        """
        get state in semi serialised form

        Returns:
            the state
        """

        state = super().getState()

        # get quest related attributes
        followUps = {}
        for (key, value) in self.followUps.items():
            followUps[key] = self.serializeCallback(value)

        state["followUps"] = followUps
        state["options"] = self.options
        return state

    def setUp(self):
        """
        show the selection menue
        """

        self.submenue = src.interaction.SelectionMenu(
            self.text, self.options, default=self.default
        )
        self.addSubmenuToCinematicQueue()

    def abort(self):
        """
        get the selection and trigger the corresponding callback
        """

        super().abort()

        # bad code: remove from the cinematic queue directly
        global cinematicQueue
        cinematicQueue = cinematicQueue[1:]

        # set up
        if not self.submenue:
            self.setUp()

        # trigger followup
        self.selected = self.submenue.selection
        if self.followUps:
            if self.selected:
                self.callIndirect(self.followUps[self.selected])
            else:
                self.followUps[list(self.options.values())[0]]
        else:
            if self.followUp:
                self.followUp()

        src.interaction.loop.set_alarm_in(0.0, src.interaction.callShow_or_exit, "~")

# obsolete: only used in old storymode
class ShowMessageCinematic(BasicCinematic):
    """
    this cutscenes shows some message 
    """

    def __init__(self, message=""):
        """
        initialise internal state

        Parameters:
            message: the message to show
        """

        super().__init__()

        self.message = message
        self.breakCinematic = False
        self.overwriteFooter = False
        self.type = "ShowMessageCinematic"

    def advance(self):
        """
        show message and abort
        """

        super().advance()

        # abort
        if self.breakCinematic:
            src.interaction.loop.set_alarm_in(
                0.0, src.interaction.callShow_or_exit, " "
            )
            self.skipable = True
            return False

        # add message
        src.gamestate.gamestate.mainChar.addMessage(self.message)
        src.interaction.loop.set_alarm_in(0.0, src.interaction.callShow_or_exit, "~")
        self.breakCinematic = True
        return True

# bad code: this should be a generalised wrapper for adding cinematics
def showCinematic(text, rusty=False, autocontinue=False, scrolling=False):
    """
    shortcut for adding a textcinematic

    Parameters:
            rusty: show the text in a rusty style
            autocontinue: autoplay the animation
            scrolling: flag for building up the text slowly
    """

    cinematicQueue.append(TextCinematic(text, rusty, autocontinue, scrolling))


# map of string the cinematic classes
cinematicMap = {
    "BasicCinematic": BasicCinematic,
    "InformationTransfer": InformationTransfer,
    "MessageZoomCinematic": MessageZoomCinematic,
    "TextCinematic": TextCinematic,
    "ShowQuestExecution": ShowQuestExecution,
    "ShowGameCinematic": ShowGameCinematic,
    "ChatCinematic": ChatCinematic,
    "SelectionCinematic": SelectionCinematic,
    "ShowMessageCinematic": ShowMessageCinematic,
}

def getCinematicFromState(state):
    """
    spawner for cinematics from dicts

    Parameters:
        state: the state to set
    """

    cinematic = cinematicMap[state["type"]]()
    cinematic.setState(state)
    return cinematic
