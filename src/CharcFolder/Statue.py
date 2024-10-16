import src
from src.CharcFolder.Monster import Monster


class Statue(Monster):
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
        name="Statue",
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
        self.charType = "Statue"
        self.specialDisplay = (src.characters.urwid.AttrSpec(src.characters.urwid.AttrSpec.interpolate((255,255,255),(255, 16, 8),src.helpers.clamp(multiplier / 4,0.0,1.0)),"black"),"@@")
        self.baseDamage = int(5+multiplier)
        self.baseDamage = int(self.baseDamage*(1-runModifier))
        self.maxHealth = int((20+10)*multiplier)
        self.maxHealth = int(self.maxHealth*(1+runModifier))
        self.health = self.maxHealth
        self.godMode = True
        self.movementSpeed = 1.3-0.1*multiplier


    def changed(self, tag="default", info=None):
        if tag == "pickup bolted fail":
            info["item"].destroy()
        super().changed(tag, info)

    def die(self, reason=None, addCorpse=True):
        """
        die without leaving a corpse
        """
        super().die(reason, addCorpse=False)

src.characters.add_character(Statue)
