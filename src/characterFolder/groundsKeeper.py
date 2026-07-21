import src

class GroundsKeeper(src.characters.characterMap["Clone"]):
    '''
    the "human" player class
    '''
    def __init__(
        self,
        display="@@",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name=None,
        creator=None,
        characterId=None,
        firstname=None
    ):
        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
            firstname=firstname
        )
        self.charType = "GroundsKeeper"

# register the creature type
src.characters.add_character(GroundsKeeper)
