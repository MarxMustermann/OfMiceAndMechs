import src

class ShieldBug(src.characters.characterMap["Insect"]):
    def __init__(
        self,
        display="/>",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="ShieldBug",
        creator=None,
        characterId=None,
        multiplier=1,
        runModifier=0,
    ):
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
        self.charType = "Insect"
        self.specialDisplay = (src.characters.urwid.AttrSpec((46, 99, 67), "black"), "/>")

        self.baseDamage = 5
        self.baseDamage = int(self.baseDamage * (1 - runModifier))

        self.maxHealth = int(100 * multiplier)
        self.maxHealth = int(self.maxHealth * (1 + runModifier))
        self.health = self.maxHealth

        self.godMode = True
        self.movementSpeed = 2.2

    @staticmethod
    def lootTable():
        return [(None, 1), (src.items.itemMap["CitinPlates"], 1)]


src.characters.add_character(ShieldBug)
