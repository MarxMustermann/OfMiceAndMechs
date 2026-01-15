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
        level = 1,
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
        self.level = level

        baseMovementSpeed = 1
        baseAttackSpeed = 1
        baseRawDamage = 2
        basehealth = 10

        self.movementSpeed = baseMovementSpeed
        self.baseAttackSpeed = baseAttackSpeed

        self.maxHealth = basehealth+basehealth*0.25*self.level
        self.health = self.maxHealth
        self.baseDamage = baseRawDamage+(baseRawDamage*0.5*self.level)

    def changed(self, tag="default", info=None):
        if tag == "pickup bolted fail":
            info["item"].destroy()
        super().changed(tag, info)

    def die(self, reason=None, addCorpse=True, killer=None):
        super().die(reason, addCorpse=False, killer=killer)

    def render(self):
        try:
            self.level
        except:
            self.level = 1
        if not self.level:
            self.level = 1
        shade = int(255-((255/7)*self.level))
        return (src.interaction.urwid.AttrSpec((255,shade,shade),"#000"), "st")

src.characters.add_character(Mechanical_Crawler)
