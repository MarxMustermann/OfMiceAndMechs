
import src
from src.CharcFolder.Monster import Monster


class Exploder(Monster):
    """
    a monster that explodes on death
    """

    def __init__(
        self,
        display="🝆~",
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

        self.charType = "Exploder"

        self.explode = True

    def render(self):
        """
        render the monster explecitly
        """
        return src.canvas.displayChars.monster_exploder

    def die(self, reason=None, addCorpse=True, killer = None):
        """
        create an explosion on death

        Parameters:
            reason: the reason for dieing
            addCorpse: flag indicating wether a corpse should be added
        """

        if self.xPosition and self.container:
            new = src.items.itemMap["FireCrystals"]()
            self.container.addItem(new,self.getPosition())
            if self.explode:
                new.startExploding()

        super().die(reason=reason, addCorpse=False, killer=killer)


src.characters.add_character(Exploder)
