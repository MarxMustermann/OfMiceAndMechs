import src
from src.CharcFolder.Monster import Monster


class Spider(Monster):
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
        self.specialDisplay = (src.characters.urwid.AttrSpec("#731", "black"), "SP")
        self.baseDamage = 10
        self.health = 50
        self.maxHealth = 50
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


src.characters.add_character(Spider)
