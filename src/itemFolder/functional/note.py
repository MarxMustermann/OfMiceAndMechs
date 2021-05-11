import src

'''
'''
class Note(src.items.Item):
    type = "Note"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Note",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.note,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.text = ""

        self.attributesToStore.extend([
                "text"])

    def getLongInfo(self):

        text = """
A Note. It has a text on it. You can activate it to read it.

it holds the text:

"""+self.text+"""

"""
        return text

    def apply(self,character):
        super().apply(character,silent=True)

        submenue = src.interaction.OneKeystrokeMenu("the note has the text: \n\n\n%s"%(self.text,))
        character.macroState["submenue"] = submenue

    def setText(self,text):
        self.text = text

src.items.addType(Note)

