import src

class MechanicalGuard(src.monster.Monster):
    """
    the class for animated statues
    intended as temple guards
    """

    def __init__(
        self,
        display="MG",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="MechanicalGuard",
        creator=None,
        characterId=None,
        level = 1,
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
        self.charType = "MechanicalGuard"
        self.godMode = True
        self.waitLength = 20
        self.level = level

        baseMovementSpeed = 1
        baseAttackSpeed = 1
        baseRawDamage = 4
        basehealth = 20

        self.movementSpeed = baseMovementSpeed
        self.baseAttackSpeed = baseAttackSpeed

        self.baseDamage = round(baseRawDamage+(baseRawDamage*0.5*self.level),2)
        self.maxHealth = int(basehealth+basehealth*0.25*self.level)
        self.health = self.maxHealth
        self.autoAdvance = True

    def getCorpse(self):
        return None

    def die(self, reason=None, addCorpse=True, killer=None):
        """
        die without leaving a corpse
        """
        super().die(reason, addCorpse=True, killer=killer)

    @staticmethod
    def lootTable():
        return [(src.items.itemMap["Grindstone"], 1)]

    def getLoreDescription(self):
        return [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),f"You see a MechanicalGuard.")," It moves with mechanical force.\nSome of the MechanicalGuards are ancient, some look like new."]

    def getFunctionalDescription(self):
        return (src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),f"Some MechanicalGuards are stronger than others, but are not special otherwise.")

    def description(self):
        return [self.getLoreDescription(),"\n\n---- ",self.getFunctionalDescription()]

    def render(self):
        try:
            self.level
        except:
            self.level = 1
        if not self.level:
            self.level = 1
        shade = int(255-((255/7)*self.level))
        return (src.interaction.urwid.AttrSpec((255,shade,shade),"#000"), "MG")

    def generateQuests(self):

        quest = src.quests.questMap["SecureTile"](toSecure=self.getBigPosition(),wandering=True, endWhenCleared=False,neverHuntDown=True)
        quest.autoSolve = True
        quest.assignToCharacter(self)
        quest.activate()
        self.quests.append(quest)

        return super().generateQuests()

src.characters.add_character(MechanicalGuard)
