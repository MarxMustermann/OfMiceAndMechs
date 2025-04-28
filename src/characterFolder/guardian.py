import src

class Guardian(src.monster.Monster):
    """
    the class for animated statues
    intended as temple guards
    """

    def __init__(
        self,
        display="&&",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Guardian",
        creator=None,
        characterId=None,
    ):
        """
        basic state setting

        Parameters:
            display: how the mouse should look like
            xPosition: obsolete, ignore
            yPosition: obsolete, ignore
            quests: obsolete, ignore
            automated: obsolete, ignore
            name: obsolete, ignore
            creator: obsolete, ignore
            characterId: obsolete, ignore
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
        self.charType = "Guardian"
        self.specialDisplay = "&&"
        self.baseDamage = 200
        self.maxHealth = 2000
        self.health = self.maxHealth
        self.godMode = True
        self.movementSpeed = 0.3


    def changed(self, tag="default", info=None):
        if tag == "pickup bolted fail":
            info["item"].destroy()
        super().changed(tag, info)

    def getCorpse(self):
        return None

    def die(self, reason=None, addCorpse=True, killer=None):
        """
        die without leaving a corpse
        """
        super().die(reason, addCorpse=True, killer=killer)

    @staticmethod
    def lootTable():
        return [(None, 6),(src.items.itemMap["Grindstone"], 4)]

src.characters.add_character(Guardian)
