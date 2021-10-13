import src

class Coal(src.items.Item):
    """
    ingame item mainly used as fuel
    """

    type = "Coal"

    def __init__(self):
        """
        set up internal state
        """

        self.canBurn = True
        super().__init__(display=src.canvas.displayChars.coal)

        self.name = "coal"
        self.description = "used as an energy source"
        self.walkable = True
        self.bolted = False

    def destroy(self, generateScrap=True):
        """
        destroy without residue

        Parameters:
            generateScrap: flag to leave no residue
        """

        super().destroy(generateScrap=False)

    # bad code: evolution should be handled by the monster dooing the evolution?
    def apply(self,character):
        """
        handle a character trying to use the item
        trigger an

        Parameters:
            character: the character that is trying to use the item
        """

        if not self.xPosition:
            return

        if isinstance(character,src.characters.Monster) and character.phase == 1 and ((src.gamestate.gamestate.tick+self.xPosition)%10 == 5):
            newChar = src.characters.Exploder()
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
            self.destroy(generateScrap=False)
        else:
            super().apply(character)

src.items.addType(Coal)
