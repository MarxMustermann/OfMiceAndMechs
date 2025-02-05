import src

class Spider(src.monster.Monster):
    """
    A spider
    should hang out in abandoned room and such
    """

    def __init__(
        self,
        display="SP",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Spider",
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

        self.charType = "Spider"
        self.specialDisplay = (src.interaction.urwid.AttrSpec("#731", "black"), "SP")
        self.baseDamage = 10
        self.health = 50
        self.maxHealth = 50
        if src.gamestate.gamestate.difficulty == "difficult":
            self.baseDamage *= 2
            self.health *= 2
            self.maxHealth = 2
        self.autoAdvance = True

        self.solvers = [
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "NaiveMurderQuest",
        ]

        self.defending = None

    def render(self):
        """
        force static render
        """
        return "SP"

    def generateQuests(self):

        quest = src.quests.questMap["SecureTile"](toSecure=self.getBigPosition(),wandering=True, endWhenCleared=False,alwaysHuntDown=True)
        quest.autoSolve = True
        quest.assignToCharacter(self)
        quest.activate()
        self.quests.append(quest)

        return super().generateQuests()

    def applyNativeMeleeAttackEffects(self,target):
        target.statusEffects.append(src.statusEffects.statusEffectMap["Slowed"](duration=2,slowDown=0.1,reason="You were bitten by a Spider"))
        super().applyNativeMeleeAttackEffects(target)

    @staticmethod
    def lootTable():
        return [(None, 9),(src.items.itemMap["SpiderEye"], 1)]

src.characters.add_character(Spider)
