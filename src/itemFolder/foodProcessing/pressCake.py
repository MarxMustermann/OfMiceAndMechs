import src

'''
'''
class PressCake(src.items.Item):
    type = "PressCake"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="press cake",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.pressCake,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: PressCake

description:
A press cake is basis for food production.

Can be processed into goo by a goo producer.
"""
        return text

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # change state
        character.satiation = 1000
        character.changed()
        self.destroy(generateSrcap=False)
        character.addMessage("you eat the press cake and gain 1000 satiation")

src.items.addType(PressCake)
