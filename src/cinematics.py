import urwid

cinematicQueue = []
quests = None
main = None
loop = None
callShow_or_exit = None
messages = None
advanceGame = None

class ScrollingTextCinematic(object):
    def __init__(self,text,rusty=False):
        self.text = text
        self.position = 0
        self.endPosition = len(self.text)
        self.alarm = None
        self.endTrigger = None
        self.rusty = rusty

    def advance(self):
        if self.position > self.endPosition:
            return
        
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
            baseText = self.text[0:self.position]
            if self.text[self.position] in ("\n"):
                self.alarm = loop.set_alarm_in(0.5, callShow_or_exit, '~')
            else:
                self.alarm = loop.set_alarm_in(0.05, callShow_or_exit, '~')
            addition = " "
        else:
            baseText = self.text
            addition = "\n\n-- press space to proceed -- "
            self.alarm = loop.set_alarm_in(1, callShow_or_exit, '~')
        if self.rusty:
            base = convert(baseText)
        else:
            base = [baseText]
        base.append(addition)
        main.set_text(base)
        header.set_text("")

        self.position += 1

    def abort(self):
        try: 
            loop.remove_alarm(self.alarm)
        except:
            pass
        if self.endTrigger:
            self.endTrigger()

class ShowGameCinematic(object):
    def __init__(self,turns,tickSpan = None):
        self.turns = turns
        self.endTrigger = None
        self.tickSpan = tickSpan

    def advance(self):
        if not self.turns:
            loop.set_alarm_in(0.0, callShow_or_exit, ' ')
            return
                
        advanceGame()
        self.turns -= 1
        if self.tickSpan:
            loop.set_alarm_in(self.tickSpan, callShow_or_exit, '.')
        return True

    def abort(self):
        while self.turns > 0:
            self.turns -= 1
            advanceGame()
        if self.endTrigger:
            self.endTrigger()

class SelectionCinematic(object):
    def __init__(self,text, options, niceOptions):
        self.showSubmenu = True
        self.options = options
        self.niceOptions = niceOptions
        self.text = text
        self.selected = None
        self.submenue= None

    def advance(self):
        text = """
please answer the question:

what is your name?"""

        self.submenue = interaction.Test1Menu(self.text, self.options, self.niceOptions)
        interaction.submenue = self.submenue
        interaction.submenue.followUp = self.abort
        self.showSubmenu = False
        return True

    def abort(self):
        global cinematicQueue
        cinematicQueue = cinematicQueue[1:]
        if self.followUp:
            self.selected = self.submenue.selection
            self.followUp()
        if cinematicQueue:
            cinematicQueue[0].advance()
        loop.set_alarm_in(0.0, callShow_or_exit, '~')

class ShowMessageCinematic(object):
    def __init__(self,message):
        self.message = message
        self.breakCinematic = False

    def advance(self):
        if self.breakCinematic:
            loop.set_alarm_in(0.0, callShow_or_exit, ' ')
            return False

        messages.append(self.message)
        loop.set_alarm_in(0.0, callShow_or_exit, '~')
        self.breakCinematic = True
        return True

    def abort(self):
        pass

def showCinematic(text,rusty=False):
    cinematicQueue.append(ScrollingTextCinematic(text,rusty))
