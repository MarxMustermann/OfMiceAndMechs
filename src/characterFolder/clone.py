
import src

class Clone(src.characters.Character):
    """
    the "human" player class
    """

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

        self.charType = "Clone"

    def die(self, reason=None, addCorpse=True, killer=None):
        if not addCorpse:
            super().die(reason=reason, addCorpse=addCorpse, killer=killer)
            return

        self.container.addItem(src.items.itemMap["Implant"](), self.getPosition())
        super().die(reason=reason, addCorpse=addCorpse, killer=killer)


src.characters.add_character(Clone)
