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
        self.godMode = True
        self.waitLength = 15

        modifier = multiplier
        shade = 255-(17*modifier)
        self.specialDisplay = (src.interaction.urwid.AttrSpec((255,shade,shade),"#000"), "st")

        baseMovementSpeed = 2
        baseAttackSpeed = 2
        baseRawDamage = 2
        basehealth = 10

        self.modifier = modifier
        self.maxHealth = basehealth+basehealth*0.25*modifier
        self.health = self.maxHealth
        self.movementSpeed = baseMovementSpeed-(baseMovementSpeed*0.5/15*modifier)
        self.baseAttackSpeed = baseAttackSpeed-(baseAttackSpeed*0.5/15*modifier)
        self.rawBaseDame = baseRawDamage+(baseRawDamage*0.5*modifier)
        self.baseDamage = baseRawDamage+(baseRawDamage*0.5*modifier)

    def changed(self, tag="default", info=None):
        if tag == "pickup bolted fail":
            info["item"].destroy()
        super().changed(tag, info)

    def die(self, reason=None, addCorpse=True, killer=None):
        super().die(reason, addCorpse=False, killer=killer)

src.characters.add_character(Mechanical_Crawler)
