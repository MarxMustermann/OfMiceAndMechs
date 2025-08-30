import src

class Monk(src.monster.Monster):
    """
    """

    def __init__(
        self,
        display="mo",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="monk",
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
        self.charType = "Monk"
        self.specialDisplay = (src.interaction.urwid.AttrSpec((100,100,255),"black"),"mo")

        
        self.health = 100
        self.baseDamage = 10
        self.maxHealth = 100
        self.godMode = True
        self.movementSpeed = 1.2
        if src.gamestate.gamestate.difficulty == "difficult":
            self.health = 300
            self.baseDamage = 70
            self.maxHealth = 300
            self.godMode = True
            self.movementSpeed = 0.8

src.characters.add_character(Monk)
