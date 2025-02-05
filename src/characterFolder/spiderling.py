import src

class Spiderling(src.monster.Monster):
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
        self.specialDisplay = (src.interaction.urwid.AttrSpec("#d62", "black"), "sp")
        self.baseDamage = 8
        self.health = 5
        self.maxHealth = 5
        if src.gamestate.gamestate.difficulty == "difficult":
            self.baseDamage *= 2
            self.health *= 2
            self.maxHealth = 2

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
