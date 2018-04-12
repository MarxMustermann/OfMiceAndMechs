import urwid

cinematicQueue = []
quests = None
main = None
loop = None
callShow_or_exit = None
messages = None
advanceGame = None

class InformationTransfer(object):
    def __init__(self,information):
        self.position = 0
        self.information = list(information.items())

    def advance(self):
        if self.position < len(self.information):
            header.set_text(self.information[self.position][0])
            main.set_text(self.information[self.position][1])

            self.position += 1

            self.alarm = loop.set_alarm_in(0.2, callShow_or_exit, '~')
            return False
        else:
            header.set_text("")
            main.set_text("done")
            self.alarm = loop.set_alarm_in(0.2, callShow_or_exit, ' ')
            return False

    def abort(self):
        try: 
            loop.remove_alarm(self.alarm)
        except:
            pass

class MessageZoomCinematic(object):
    def __init__(self):
        self.screensize = loop.screen.get_cols_rows()
        self.right = self.screensize[0]
        self.left = 0
        self.top = self.screensize[1]
        self.bottom = 0
        self.alarm = None
        self.turnOffCounter = 10
        self.turnOnCounter = 10
        self.text = None

    def advance(self):
        if not self.text:
            self.text = interaction.renderMessages().split("\n")

        if self.turnOnCounter:
            self.turnOnCounter -= 1
            header.set_text("\n"+"\n".join(self.text))
            main.set_text("")
            self.alarm = loop.set_alarm_in(0.2, callShow_or_exit, '~')
            return False

        textWithDeco = ""
        for line in self.text:
            textWithDeco += " "*self.left+"┃ "+line+"\n"
        for i in range(0,self.top-2-len(self.text)):
            textWithDeco += " "*self.left+"┃\n"
        textWithDeco += " "*self.left+"┗"+"━"*(self.right-1)
        header.set_text(textWithDeco)
        main.set_text("")
        questWidth = (self.screensize[0]//3)*2+4
        if self.right > questWidth:
            if self.right > questWidth+5:
                self.left += 2
                self.right -= 2
            else:
                self.left += 1
                self.right -= 1
        if self.top > 7:
            self.top -= 1
            self.bottom += 1

        if not self.right > questWidth and not self.top > 8:
            if self.turnOffCounter:
                self.turnOffCounter -= 1
            else:
                self.alarm = loop.set_alarm_in(0.2, callShow_or_exit, ' ')
                return False

        self.alarm = loop.set_alarm_in(0.2, callShow_or_exit, '~')

    def abort(self):
        try: 
            loop.remove_alarm(self.alarm)
        except:
            pass
        pass

class ScrollingTextCinematic(object):
    def __init__(self,text,rusty=False):
        self.text = text
        self.position = 0
        self.alarm = None
        self.endTrigger = None
        self.rusty = rusty

        def flattenToPeseudoString(urwidText):
            if isinstance(urwidText,str):
                return list(urwidText)
            elif isinstance(urwidText,list):
                result = []
                for item in urwidText:
                    result.extend(flattenToPeseudoString(item))
                return result
            else:
                result = []
                for item in flattenToPeseudoString(urwidText[1]):
                    result.append((urwidText[0],item))
                return result
        
        self.text = flattenToPeseudoString(self.text)
        self.endPosition = len(self.text)

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
            if isinstance(self.text[self.position],str) and self.text[self.position] in ("\n"):
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

class ShowQuestExecution(object):
    def __init__(self,quest,tickSpan = None):
        self.quest = quest
        self.endTrigger = None
        self.tickSpan = tickSpan

    def advance(self):
        if self.quest.completed:
            loop.set_alarm_in(0.0, callShow_or_exit, ' ')
            return

        advanceGame()
        if self.tickSpan:
            loop.set_alarm_in(self.tickSpan, callShow_or_exit, '.')
        return True

    def abort(self):
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
