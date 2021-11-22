import src

'''
'''
class Tumbler(src.items.Item):
    type = "Tumbler"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self):
        super().__init__(display=src.canvas.displayChars.tumbler)

        self.name = "tumbler"

        self.strength = 7
        self.tracking = False
        self.tracked = None
        self.walkable = True
        self.command = []

    def apply(self,character):

        direction = src.gamestate.gamestate.tick%33%4
        strength = src.gamestate.gamestate.tick%self.strength+1

        direction = ["w","a","s","d"][direction]
        command = direction * strength

        character.runCommandString(command)

        character.addMessage("tumbling %s %s "%(direction,strength))
        self.tracking = True

    def getLongInfo(self):
        text = """

This device tracks ticks since creation. You can use it to measure time.

Activate it to get a message with the number of ticks passed.

Also the number of ticks will be written to the register t.

"""
        return text

src.items.addType(Tumbler)
