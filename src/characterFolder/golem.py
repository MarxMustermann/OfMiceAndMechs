import src

class Golem(src.monster.Monster):
    """
    the class for animated statues
    intended as temple guards
    """

    def __init__(
        self,
        display="@@",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Golem",
        creator=None,
        characterId=None,
        multiplier = 1,
        runModifier = 0
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
        self.charType = "Golem"
        self.specialDisplay = (src.interaction.urwid.AttrSpec(src.interaction.urwid.AttrSpec.interpolate((255,255,255),(255, 16, 8),src.helpers.clamp(multiplier / 4,0.0,1.0)),"black"),"@@")
        self.baseDamage = int(10+multiplier)
        self.baseDamage = int(self.baseDamage*(1-runModifier))
        self.maxHealth = int(60*multiplier)
        self.maxHealth = int(self.maxHealth*(1+runModifier))
        self.health = self.maxHealth
        self.godMode = True
        self.movementSpeed = 1.3-0.1*multiplier


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

src.characters.add_character(Golem)
