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
        self.godMode = True
        self.waitLength = 20

        modifier = multiplier
        shade = 255-(17*modifier)
        self.specialDisplay = (src.interaction.urwid.AttrSpec((255,shade,shade),"#000"), "@@")

        baseMovementSpeed = 2
        baseAttackSpeed = 2
        baseRawDamage = 4
        basehealth = 20

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

    def getLoreDescription(self):
        return f"You see a Golem. It moves with mechanical force.\nSome of the Golems are rusting hulks, but some are finely tuned killing machines"

    def getFunctionalDescription(self):
        return f"Some Golems are stronger than others, but are not special otherwise."

    def description(self):
        return self.getLoreDescription()+"\n\n---- "+self.getFunctionalDescription()

src.characters.add_character(Golem)
