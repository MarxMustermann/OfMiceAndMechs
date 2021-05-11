import src

'''
'''
class MemoryBank(Item):
    type = "MemoryBank"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MemoryBank",creator=None,noId=False):

        self.macros = {}

        self.baseName = name

        super().__init__(src.canvas.displayChars.memoryBank,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
                "macros"])

        self.setDescription()

    def setDescription(self):
        addition = ""
        if self.macros:
            addition = " (imprinted)"
        self.description = self.baseName+addition

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        import copy
        if self.macros:
            character.addMessage("you overwrite your macros with the ones in your memory bank")
            character.macroState["macros"] = copy.deepcopy(self.macros)
        else:
            character.addMessage("you store your macros in the memory bank")
            self.macros = copy.deepcopy(character.macroState["macros"])

        self.setDescription()

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

src.items.addType(MemoryBank)
