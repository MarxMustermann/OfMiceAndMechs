import src
from src.CharcFolder.Monster import Monster


class Spiderling(Monster):
    """
    A spider
    should hang out in abandoned room and such
    """

    def __init__(
        self,
        display="sp",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Spiderling",
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

        self.charType = "Spiderling"
        self.specialDisplay = "sp"
        self.baseDamage = 4
        self.health = 10
        self.maxHealth = 10

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
        return "sp"

src.characters.add_character(Spiderling)