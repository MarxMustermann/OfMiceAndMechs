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
        self.maxHealth = 1000
        self.hasSpecialAttacks = True
        self.hasPushbackAttack = True
        self.health = self.maxHealth
        self.godMode = True
        self.movementSpeed = 0.1
        self.baseAttackSpeed = 0.1
        self.specialCharges = 0
        self.rawBaseDame = 20
        self.baseDamage = 20

    def hurt(self, damage, reason=None, actor=None):
        try:
            self.rawBaseDame
        except:
            self.rawBaseDame = 20

        self.specialCharges += 2
        self.baseDamage = self.rawBaseDame * (1 + self.specialCharges)

        super().hurt(damage,reason=reason,actor=actor)

    def advance(self,advanceMacros=False):
        try:
            self.specialCharges
        except:
            self.specialCharges = 0
        try:
            self.rawBaseDame
        except:
            self.rawBaseDame = 20

        if self.specialCharges > 0:
            self.specialCharges -= 1
            self.baseDamage = self.rawBaseDame * (1 + self.specialCharges)
        super().advance(advanceMacros=advanceMacros)

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

    def render(self):
        """
        force static render
        """

        try:
            self.specialCharges
        except:
            self.specialCharges = 0

        color = (255,255,255)
        if self.specialCharges > 1:
            color = (255,max(0,255-self.baseDamage),max(0,255-self.baseDamage))
        return (src.interaction.urwid.AttrSpec(color, "black"), "&&")

src.characters.add_character(Guardian)
