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
            self.maxHealth *= 2

        self.solvers = [
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "NaiveMurderQuest",
        ]

        self.defending = None
        self.autoAdvance = True

    def render(self):
        """
        force static render
        """
        return "sp"

    def getLoreDescription(self):
        return [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You see a Spiderling."),"\n\nIt balances on its many legs almost drowning in the mud.\n\nIts many eyes follow every of your movements.\nSome show an expression of fear and some an expression of disgust."]

    def getFunctionalDescription(self):
        return (src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),f"Spiderlings are weak and not fast and have little HP.")

    def description(self):
        return [self.getLoreDescription(),"\n\n---- ",self.getFunctionalDescription()]

    def generateQuests(self):

        quest = src.quests.questMap["SecureTile"](toSecure=self.getBigPosition(),wandering=True, endWhenCleared=False,neverHuntDown=True)
        quest.autoSolve = True
        quest.assignToCharacter(self)
        quest.activate()
        self.quests.append(quest)

        return super().generateQuests()

src.characters.add_character(Spiderling)
