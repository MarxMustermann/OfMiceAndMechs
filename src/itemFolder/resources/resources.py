import src

'''
'''
class PocketFrame(src.items.ItemNew):
    type = "PocketFrame"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="pocket frame",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.pocketFrame,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True

    def getLongInfo(self):
        text = """

A pocket frame. Is complex building item. It is used to build smaller things.

"""
        return text

'''
basic item with different appearance
'''
class Coal(src.items.Item):
    type = "Coal"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Coal",creator=None,noId=False):
        self.canBurn = True
        super().__init__(src.canvas.displayChars.coal,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False

    def getLongInfo(self):
        text = """
item: Coal

description:
Coal is used as an energy source. It can be used to fire furnaces.

"""
        return text

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

    def apply(self,character):
        if not self.xPosition:
            return

        if isinstance(character,src.characters.Monster) and character.phase == 1 and ((gamestate.tick+self.xPosition)%10 == 5):
            newChar = characters.Exploder(creator=self)
            import copy
            newChar.macroState = character.macroState
            character.macroState = {}
            newChar.satiation = character.satiation
            newChar.explode = False

            newChar.solvers = [
                      "NaiveActivateQuest",
                      "ActivateQuestMeta",
                      "NaiveExamineQuest",
                      "ExamineQuestMeta",
                      "NaivePickupQuest",
                      "NaiveMurderQuest",
                      "DrinkQuest",
                      "NaiveDropQuest",
                    ]

            self.container.addCharacter(newChar,self.xPosition,self.yPosition)
            character.die()
            self.destroy(generateSrcap=False)
        else:
            super().apply(character)

