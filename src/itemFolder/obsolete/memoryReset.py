import src

'''
'''
class MemoryReset(src.items.Item):
    type = "MemoryReset"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self):

        super().__init__(display=src.canvas.displayChars.memoryReset)

        self.name = "memory stack"


    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        character.addMessage("you clear your macros")

        character.macroState["macros"] = {}
        character.registers = {}

src.items.addType(MemoryReset)
