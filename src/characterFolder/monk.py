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

        self.hasMagic = True
        
        self.health = 200
        self.baseDamage = 20
        self.maxHealth = 200
        self.godMode = True
        self.movementSpeed = 1.2
        if src.gamestate.gamestate.difficulty == "difficult":
            self.health = 600
            self.baseDamage = 140
            self.maxHealth = 600
            self.godMode = True
            self.movementSpeed = 0.8

    def getLoreDescription(self):
        return f"From far away you only see a tattered blue robe. If you look closer you see nothing under the robe."

    def getFunctionalDescription(self):
        return f"The Monks are pretty dangerous enemies"

    def description(self):
        return self.getLoreDescription()+"\n\n---- "+self.getFunctionalDescription()

src.characters.add_character(Monk)
