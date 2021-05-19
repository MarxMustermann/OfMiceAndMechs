import src

class PoisonBush(src.items.Item):
    """
    a hard to remove poison plant
    """

    type = "PoisonBush"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.poisonBush)
        self.name = "poison brush"
        self.description = ""
        self.usageInfo = """
You can use it to loose 100 satiation.
"""

        self.walkable = False
        self.charges = 0
        self.attributesToStore.extend(["charges"])

    def apply(self, character):
        """
        handle a character trying to use this item
        by killing the character

        Parameters:
            character: the character trying to use this item
        """

        self.charges += 1
        if 100 > character.satiation:
            character.satiation = 0
        else:
            character.satiation -= 100

        if self.charges > 10:

            new = itemMap["EncrustedPoisonBush"]()
            self.container.addItem(new,self.getPosition())

            self.container.removeItem(self)

        character.addMessage("you give your blood to the poison bush")

    def spawn(self, distance=1):
        """
        spawn a new poison bloom

        Parameters:
            distance: the spawning distance
        """

        if not (self.xPosition and self.yPosition):
            return
        direction = (
            2 * self.xPosition + 3 * self.yPosition + src.gamestate.gamestate.tick
        ) % 4
        direction = (random.randint(1, distance + 1), random.randint(1, distance + 1))
        newPos = (self.xPosition + direction[0] - 5, self.yPosition + direction[1] - 5, self.zPosition)

        if (
            newPos[0] < 1
            or newPos[1] < 1
            or newPos[0] > 15 * 15 - 2
            or newPos[1] > 15 * 15 - 2
        ):
            return

        if not (
            newPos in self.container.itemByCoordinates
            and len(self.container.itemByCoordinates[newPos])
        ):
            new = itemMap["PoisonBloom"]()
            self.container.addItem(new,newPos)

    def getLongInfo(self):
        """
        returns a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += "poison charges: %s" % (self.charges)
        return text

    def destroy(self, generateSrcap=True):
        """
        destroy the item and leave a exploding thing

        Parameters:
            generateSrcap: flag to toggle leaving residue
        """

        new = itemMap["FireCrystals"]()
        self.container.addItem(new,self.getPosition())

        character = characters.Exploder()

        character.solvers = [
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaiveExamineQuest",
            "ExamineQuestMeta",
            "NaivePickupQuest",
            "NaiveMurderQuest",
            "DrinkQuest",
            "NaiveExamineQuest",
            "ExamineQuestMeta",
        ]

        character.faction = "monster"

        command = ""
        if src.gamestate.gamestate.tick % 4 == 0:
            command += "A"
        if src.gamestate.gamestate.tick % 4 == 1:
            command += "W"
        if src.gamestate.gamestate.tick % 4 == 2:
            command += "S"
        if src.gamestate.gamestate.tick % 4 == 3:
            command += "D"

        if self.xPosition % 4 == 0:
            command += "A"
        if self.xPosition % 4 == 1:
            command += "W"
        if self.xPosition % 4 == 2:
            command += "S"
        if self.xPosition % 4 == 3:
            command += "D"

        if self.yPosition % 4 == 0:
            command += "A"
        if self.yPosition % 4 == 1:
            command += "W"
        if self.yPosition % 4 == 2:
            command += "S"
        if self.yPosition % 4 == 3:
            command += "D"

        character.macroState["macros"]["m"] = list(command + "_m")

        character.macroState["commandKeyQueue"] = [("_", []), ("m", [])]
        character.satiation = 100
        self.container.addCharacter(character, self.xPosition, self.yPosition)

        super().destroy(generateSrcap=False)

src.items.addType(PoisonBush)
