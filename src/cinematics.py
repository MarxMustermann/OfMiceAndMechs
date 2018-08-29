import urwid

"""
bad code: containers for global state
"""
cinematicQueue = []
quests = None
main = None
loop = None
callShow_or_exit = None
messages = None
advanceGame = None

"""
the base class for all Cinamatics. Nothing fancy
"""
class BasicCinematic(object):
    def __init__(self):
        # initialize basic state
        self.background = False
        self.followUp = None
        self.skipable = False
        self.overwriteFooter = True
        self.footerText = ""
        self.endTrigger = None

    def advance(self):
        return False

    def abort(self):
        pass

"""
this is a single use cinematic basically. It flashes some info too fast to read to sybolise information transfer to the implant
bad code: should be abstracted and called with a parameter instead of single use special class
bad code: the triggered state has no obvious pupose and should be rewritten/removed
"""
class InformationTransfer(BasicCinematic):
    """
    almost straightforward state initilisation with the information as parameter
    """
    def __init__(self,information):
        super().__init__()

        self.position = 0
        self.information = list(information.items())

        self.triggered = False

    """
    blink a piece of information
    """
    def advance(self):
        super().advance()

        if self.position < len(self.information):
            # show the current information
            header.set_text(self.information[self.position][0])
            main.set_text(self.information[self.position][1]) 

            # trigger showing the next information
            self.position += 1
            self.alarm = loop.set_alarm_in(0.2, callShow_or_exit, '~')
            return False
        elif not self.triggered:
            # bad code: unknown purpose
            header.set_text("")
            main.set_text("done")
            self.triggered = True
            self.skipable = True

            # trigger the end of the cinematic
            self.alarm = loop.set_alarm_in(0, callShow_or_exit, ' ')
            return False
        else:
            return False

    """
    stop rendering
    """
    def abort(self):
        super().abort()

        # clean up
        try: 
            loop.remove_alarm(self.alarm)
        except:
            pass

"""
this is a single use cinematic that collapses a full screen message display into the in game message window
bad code: this should be abstracted to have a zoom in/out for various things like the quest menu
"""
class MessageZoomCinematic(BasicCinematic):
    """
    almost straightforward state initialization
    """
    def __init__(self):
        super().__init__()

        # bad code: the screensize can change while the cinematic is running
        self.screensize = loop.screen.get_cols_rows()
        self.right = self.screensize[0]
        self.left = 0
        self.top = self.screensize[1]
        self.bottom = 0
        self.alarm = None
        self.turnOffCounter = 10
        self.turnOnCounter = 10
        self.text = None

    """
    render the message window smaller each step
    """
    def advance(self):
        super().advance()

        # get the text of the message window if it wasn't retrieved yet
        if not self.text:
            self.text = interaction.renderMessages().split("\n")

        # wait for some time till actually doing something
        if self.turnOnCounter:
            self.turnOnCounter -= 1
            header.set_text("\n"+"\n".join(self.text))
            main.set_text("")
            self.alarm = loop.set_alarm_in(0.2, callShow_or_exit, '~')
            return False

        # add borders to the text
        textWithDeco = ""
        for line in self.text:
            textWithDeco += " "*self.left+"┃ "+line+"\n"
        for i in range(0,self.top-2-len(self.text)):
            textWithDeco += " "*self.left+"┃\n"
        textWithDeco += " "*self.left+"┗"+"━"*(self.right-1)

        # reduce the size till the border fits the 
        # bad code: the dimension of the message box is calculated based on assumtions. Size should be asked from the message box
        header.set_text(textWithDeco)
        main.set_text("")
        questWidth = (self.screensize[0]//3)*2+4
        if self.right > questWidth:
            if self.right > questWidth+5:
                # fast shrinking
                self.left += 2
                self.right -= 2
            else:
                # slow shrinking
                self.left += 1
                self.right -= 1
        if self.top > 7:
            self.top -= 1
            self.bottom += 1

        if not self.right > questWidth and not self.top > 8:
            # wait for some time and stop the cinematic
            if self.turnOffCounter:
                self.turnOffCounter -= 1
            else:
                self.alarm = loop.set_alarm_in(0.2, callShow_or_exit, ' ')
                self.skipable = True
                return False

        # trigger the next movement
        self.alarm = loop.set_alarm_in(0.2, callShow_or_exit, '~')

    """
    stop rendering
    """
    def abort(self):
        super().abort()

        # clean up
        try: 
            loop.remove_alarm(self.alarm)
        except:
            pass
        
        # trigger follow up functions
        if self.endTrigger:
            self.endTrigger()

"""
a cinematic showing a text in various ways
"""
class TextCinematic(BasicCinematic):
    """
    straightforward state initialization
    options include a rusty look and scrolling
    """
    def __init__(self,text,rusty=False, autocontinue=False, scrolling=False):
        super().__init__()

        self.text = text
        self.position = 0
        self.alarm = None
        self.endTrigger = None
        self.rusty = rusty
        self.autocontinue = autocontinue
        if not rusty:
           self.footerText = "press any key to speed up cutscene (not space)"
        else:
           self.footerText = ""

        """
        split a mix of strings and uwid formating into a list where each element contains exactly
        one character and its formating
        bad code: this should not be an inline function but accessible as a helper
        """
        def flattenToPeseudoString(urwidText):
            if isinstance(urwidText,str):
                # split strings
                return list(urwidText)
            elif isinstance(urwidText,list):
                # recursively handle list items
                result = []
                for item in urwidText:
                    result.extend(flattenToPeseudoString(item))
                return result
            elif isinstance(urwidText,int):
                # resolve references
                result = flattenToPeseudoString(displayChars.indexedMapping[urwidText][1])
                return result
            else:
                # handle formatters
                result = []
                for item in flattenToPeseudoString(urwidText[1]):
                    result.append((urwidText[0],item))
                return result

        # flatten text and text information
        self.text = flattenToPeseudoString(self.text)
        self.endPosition = len(self.text)
        if not scrolling:
            self.position = self.endPosition
            
    '''
    render and advance the state
    '''
    def advance(self):
        super().advance()

        # do nothing if done
        # bad code: this should be unnecessary
        if self.position > self.endPosition:
            return

        '''
        add rusty colors to a string
        bad code: this should be a generally available function not an inline function
        '''
        def convert(payload):
            converted = []
            colours = ['#f50',"#a60","#f80","#fa0","#860"]
            counter = 0
            for char in payload:
                counter += 1
                if len(char):
                    converted.append((urwid.AttrSpec(colours[counter*7%5],'default'),char))
            return converted

        if self.position < self.endPosition:
            # scroll the text in char by char
            baseText = self.text[0:self.position]
            if isinstance(self.text[self.position],str) and self.text[self.position] in ("\n"):
                self.alarm = loop.set_alarm_in(0.5, callShow_or_exit, '~')
            else:
                self.alarm = loop.set_alarm_in(0.05, callShow_or_exit, '~')
            addition = ""
        else:
            # show the complete text
            baseText = self.text
            self.skipable = True
            if not self.autocontinue:
                self.footerText = "press space to proceed"
                self.alarm = loop.set_alarm_in(0, callShow_or_exit, '~')
            else:
                self.alarm = loop.set_alarm_in(0, callShow_or_exit, ' ')

        # show the complete text
        if self.rusty:
            base = convert(baseText)
        else:
            base = [baseText]

        # actually display
        base.append("")
        main.set_text(base)
        header.set_text("")

        # scroll further
        # bad code: should hang around with the other scrolling stuff
        self.position += 1

    '''
    stop the cinematic
    '''
    def abort(self):
        super().abort()

        # clean up
        try: 
            loop.remove_alarm(self.alarm)
        except:
            pass

        # trigger follow up actions
        if self.endTrigger:
            self.endTrigger()

'''
a cinematic that shows the execution of a quest
bad pattern: locking the players controls without ingame reason results breaking the users expectation
'''
class ShowQuestExecution(BasicCinematic):
    '''
    straightforward initialization with options like a character to do the quest or making
    it run in the background. A second setup happens when the cinematic actually starts
    '''
    def __init__(self,quest,tickSpan = None, assignTo = None, background = False, container=None):
        super().__init__()

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

    '''
    assign the quest
    '''
    def setup(self):
        self.wasSetup = True
        if self.assignTo:
            if not self.container:
                self.assignTo.assignQuest(self.quest,active=True)
            else:
                self.container.addQuest(self.quest)
                self.container.recalculate()

    '''
    advance and show game
    '''
    def advance(self):
        super().advance()

        # do setup the first run
        if not self.wasSetup:
            self.setup()

        # abort if quest is done
        if self.quest.completed:
            loop.set_alarm_in(0.0, callShow_or_exit, ' ')
            self.skipable = True
            return True

        advanceGame()

        # trigger next state
        if self.alarm:
            loop.remove_alarm(self.alarm)
        if self.tickSpan and self.active:
            self.alarm = loop.set_alarm_in(self.tickSpan, callShow_or_exit, '.')
        else:
            self.alarm = loop.set_alarm_in(0.5, callShow_or_exit, '~')
        return True

    '''
    finish quest and clean up
    '''
    def abort(self):
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
            self.endTrigger()
        
'''
shows the game
bad pattern: locking the players controls without ingame reason results breaking the users expectation
'''
class ShowGameCinematic(BasicCinematic):
    '''
    straightforward state initialization
    '''
    def __init__(self,turns,tickSpan = None):
        super().__init__()

        self.turns = turns
        self.endTrigger = None
        self.tickSpan = tickSpan
        self.overwriteFooter = False

    '''
    advance the game
    '''
    def advance(self):
        super().advance()

        # abort when done
        if not self.turns:
            loop.set_alarm_in(0.0, callShow_or_exit, ' ')
            self.skipable = True
            return
                
        # advance the game
        advanceGame()

        #trigger next step
        self.turns -= 1
        if self.tickSpan:
            loop.set_alarm_in(self.tickSpan, callShow_or_exit, '.')

        return True

    '''
    advance game and abort
    '''
    def abort(self):
        super().abort()

        # advance game until desired step
        # bug?: abort is retriggered from within advance
        while self.turns > 0:
            self.turns -= 1
            advanceGame()

        # trigger follow up options
        if self.endTrigger:
            self.endTrigger()

'''
triggers a chat
'''
class ChatCinematic(BasicCinematic):
    def __init__(self):
        super().__init__()

        self.submenue = interaction.ChatMenu()

    '''
    triggers a chat and aborts
    '''
    def advance(self):
        super().abort()

        # bad code: hooks the submenue directly into the interaction
        interaction.submenue = self.submenue
        interaction.submenue.followUp = self.abort

        # bad code: removes itself directly from the cinematics queue without using a abstracted function
        global cinematicQueue
        cinematicQueue = cinematicQueue[1:]
        if self.followUp:
            self.followUp()
        if cinematicQueue:
            cinematicQueue[0].advance()
        loop.set_alarm_in(0.0, callShow_or_exit, '~')
        return True

'''
this cinematic offers the user a choice and calls a trigger depending on this choice
bad pattern: choices should be in game actions not magic cutscene choices
'''
class SelectionCinematic(BasicCinematic):
    '''
    straightforward state initialization
    '''
    def __init__(self,text, options, niceOptions, followUps=None):
        super().__init__()

        self.options = options
        self.niceOptions = niceOptions
        self.followUps = followUps
        self.text = text
        self.selected = None
        self.submenue= None

    '''
    set up and do nothing
    bad code: this is the core function. It should do something
    '''
    def advance(self):
        super().advance()

        self.setUp()
        return True

    '''
    show the selection menue
    '''
    def setUp(self):
        self.submenue = interaction.SelectionMenu(self.text, self.options, self.niceOptions)
        interaction.submenue = self.submenue
        interaction.submenue.followUp = self.abort

    '''
    get the selection and trigger the corresponding callback
    '''
    def abort(self):
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
                self.followUps[self.selected]()
            else:
                self.followUps[list(self.options.values())[0]]
        else:
            if self.followUp:
                self.followUp()

        # bad code: trigger next cinematic ans redraw
        if cinematicQueue:
            cinematicQueue[0].advance()
        loop.set_alarm_in(0.0, callShow_or_exit, '~')

'''
this cutscenes shows some message 
'''
class ShowMessageCinematic(BasicCinematic):
    def __init__(self,message):
        super().__init__()

        self.message = message
        self.breakCinematic = False
        self.overwriteFooter = False

    def advance(self):
        super().advance()

        if self.breakCinematic:
            loop.set_alarm_in(0.0, callShow_or_exit, ' ')
            self.skipable = True
            return False

        messages.append(self.message)
        loop.set_alarm_in(0.0, callShow_or_exit, '~')
        self.breakCinematic = True
        return True

'''
shortcut for adding a textcinematic
bad code: this should be a generalised wrapper for adding cinematics
'''
def showCinematic(text,rusty=False,autocontinue=False,scrolling=False):
    cinematicQueue.append(TextCinematic(text,rusty,autocontinue,scrolling))
