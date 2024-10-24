import random

import src


class Maggot(src.characters.Character):
    """
    A maggot
    intended as something to be hatched
    not really used right now
    """

    def __init__(
        self,
        display="o=",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Maggot",
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
        self.solvers.append("NaiveActivateQuest")
        self.solvers.append("NaiveMurderQuest")
        self.maxHealth = random.randint(5,15)
        self.health = self.maxHealth

        self.satiation = 10

        self.charType = "Maggot"

    def advance(self,advanceMacros=False):
        """
        overwrite behavior to just kill everything else
        """

        if self.timeTaken > 1:
            return
        if src.gamestate.gamestate.tick % 2 != 0:
            return

        self.satiation -= 1
        if self.satiation < 0:
            self.die(reason="starved")
            return

        terrain = self.getTerrain()
        characters = terrain.charactersByTile.get(self.getBigPosition(),[])
        directions = []
        for character in characters:
            if character != self:
                if character.xPosition < self.xPosition:
                    directions.append("a")
                    directions.append("a")
                    directions.append("a")
                elif character.xPosition > self.xPosition:
                    directions.append("d")
                    directions.append("d")
                    directions.append("d")
                elif character.yPosition > self.yPosition:
                    directions.append("s")
                    directions.append("s")
                    directions.append("s")
                elif character.yPosition < self.yPosition:
                    directions.append("w")
                    directions.append("w")
                    directions.append("w")

        if not directions:
            directions = ["w","a","s","d"]

        direction = random.choice(directions)
        self.runCommandString(direction+"jm")

    def die(self, reason=None, addCorpse=True, killer=None):
        """
        leave a special corpse
        """

        if self.xPosition and self.container:
            new = src.items.itemMap["VatMaggot"]()
            self.container.addItem(new,self.getPosition())

        super().die(reason=reason, addCorpse=False, killer=killer)


src.characters.add_character(Maggot)
