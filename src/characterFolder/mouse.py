import src

# bad code: animals should not be characters. This means it is possible to chat with a mouse
class Mouse(src.characters.Character):
    """
    the class for mice. Intended to be used for manipulating the gamestate used for example to attack the player
    """


    def __init__(
        self,
        display="🝆 ",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Mouse",
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
        self.charType = "Mouse"
        self.vanished = False

        self.personality["autoAttackOnCombatSuccess"] = 1
        self.personality["abortMacrosOnAttack"] = True
        self.health = 10
        self.faction = "mice"

        self.solvers.extend(["NaiveMurderQuest"])

        self.baseDamage = 1
        self.randomBonus = 0
        self.bonusMultiplier = 0
        self.staggerResistant = 0

    def vanish(self):
        """
        make the mouse disapear
        """
        # remove self from map
        self.container.removeCharacter(self)
        self.vanished = True

src.characters.add_character(Mouse)
