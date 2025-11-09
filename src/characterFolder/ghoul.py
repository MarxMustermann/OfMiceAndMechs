import src

class Ghoul(src.characters.Character):
    """
    """

    def __init__(
        self,
        display="@ ",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Ghoul",
        creator=None,
        characterId=None,
    ):
        """
        basic state setting
        """
        if quests is None:
            quests = []
        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
        )
        self.solvers.append("NaiveActivateQuest")
        self.solvers.append("NaiveMurderQuest")

        self.charType = "Ghoul"

    def getOwnAction(self):
        """
        disable own actions
        """
        self.hasOwnAction = 0
        return "."

    def heal(self, amount, reason=None):
        """
        disable healing
        """
        self.addMessage("ghouls don't heal")

    def hurt(self, damage, reason=None, actor=None):
        """
        half the damage taken
        """
        super().hurt(max(1,damage//2),reason=reason,actor=actor)

    def die(self, reason=None, killer = None, addCorpse=True, corpseType="MoldFeed"):
        return super().die(reason=reason,killer=killer,addCorpse=addCorpse,corpseType=corpseType)

    def getLoreDescription(self):
        return f"You see an Ghul. They have the form of a Clone, but you can see no humanity in their eyes.\nTheir food habits also make every room they are in smell like Corpse."

    def getFunctionalDescription(self):
        return f"Ghuls are great workforce when their automation system has been set up properly"

    def description(self):
        return self.getLoreDescription()+"\n\n---- "+self.getFunctionalDescription()

src.characters.add_character(Ghoul)
