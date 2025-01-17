import src

class Mechanical_Crawler(src.monster.Monster):
    """
    the class for a small statue
    is intended as temple guard
    """
    def __init__(
        self,
        display="st",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="mechanical crawler",
        creator=None,
        characterId=None,
        multiplier = 1,
        runModifier = 0
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
        self.charType = "Mechanical crawler"
        self.specialDisplay = (src.interaction.urwid.AttrSpec(src.interaction.urwid.AttrSpec.interpolate((255,255,255),(255, 16, 8),src.helpers.clamp(multiplier / 4,0.0,1.0)),"black"),"st")
        self.baseDamage = int(4+multiplier)
        self.baseDamage = int(self.baseDamage*(1+runModifier))
        self.maxHealth = int(20*multiplier)
        self.maxHealth = int(self.maxHealth*(1-runModifier))
        self.health = self.maxHealth
        self.godMode = True
        self.movementSpeed = 1.0*0.9**multiplier


    def changed(self, tag="default", info=None):
        if tag == "pickup bolted fail":
            info["item"].destroy()
        super().changed(tag, info)

    def die(self, reason=None, addCorpse=True, killer=None):
        super().die(reason, addCorpse=False, killer=killer)

src.characters.add_character(Mechanical_Crawler)
