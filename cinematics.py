cinematicQueue = []
quests = None
main = None
loop = None
callShow_or_exit = None
messages = None
advanceGame = None

class ScrollingTextCinematic(object):
	def __init__(self,text):
		self.text = text+"\n\n-- press space to proceed -- "
		self.position = 0
		self.endPosition = len(self.text)

	def advance(self):
		if self.position >= self.endPosition:
			return

		main.set_text(self.text[0:self.position])
		if self.text[self.position] in ("\n"):
			loop.set_alarm_in(0.5, callShow_or_exit, '~')
		else:
			loop.set_alarm_in(0.05, callShow_or_exit, '~')
		self.position += 1

class ShowGameCinematic(object):
	def __init__(self,turns):
		self.turns = turns

	def advance(self):
		if not self.turns:
			loop.set_alarm_in(0.0, callShow_or_exit, ' ')
			return
				
		self.turns -= 1
		advanceGame()

class ShowMessageCinematic(object):
	def __init__(self,message):
		self.message = message
		self.breakCinematic = False

	def advance(self):
		if self.breakCinematic:
			loop.set_alarm_in(0.0, callShow_or_exit, ' ')
			return
		messages.append(self.message)
		loop.set_alarm_in(0.0, callShow_or_exit, '~')
		self.breakCinematic = True

def showCinematic(text):
	cinematicQueue.append(ScrollingTextCinematic(text))
