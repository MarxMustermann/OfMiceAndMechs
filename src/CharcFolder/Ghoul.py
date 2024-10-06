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

src.characters.add_character(Ghoul)
