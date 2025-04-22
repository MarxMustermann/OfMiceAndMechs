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
        self.specialDisplay = (src.interaction.urwid.AttrSpec((46, 99, 67), "black"), "/>")

        self.baseDamage = 5
        self.baseDamage = int(self.baseDamage * (1 - runModifier))

        self.maxHealth = int(100 * multiplier)
        self.maxHealth = int(self.maxHealth * (1 + runModifier))
        self.health = self.maxHealth

        if src.gamestate.gamestate.difficulty == "difficult":
            self.baseDamage *= 2
            self.health *= 2
            self.maxHealth *= 2

        self.godMode = True
        self.movementSpeed = 2.2

    def changed(self, tag="default", info=None):
        if tag == "pickup bolted fail":
            info["item"].destroy()
        super().changed(tag, info)

    @staticmethod
    def lootTable():
        return [(None, 1), (src.items.itemMap["ChitinPlates"], 1)]


src.characters.add_character(ShieldBug)
