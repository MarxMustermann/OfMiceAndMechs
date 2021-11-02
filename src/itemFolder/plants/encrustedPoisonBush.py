import src

class EncrustedPoisonBush(src.items.Item):
    """
    ingame item that blocks paths and is hard to remove
    """

    type = "EncrustedPoisonBush"
    name = "encrusted poison bush"
    walkable = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.encrustedPoisonBush)

    def apply(self, character):
        """
        handle a character trying to use this item
        by stealing the characters blood

        Parameters:
            character: the character trying to us the item
        """
        
        if 100 > character.satiation:
            character.satiation = 0
        else:
            character.satiation -= 100

        character.addMessage(
            "you give your blood to the encrusted poison bush and loose 100 satiation"
        )

    def getLongInfo(self):
        """
        returns a longer than normal description text

        Parameters:
            the description text
        """
        
        text = super().getLongInfo()

        text += """
description:
This is a cluster of blooms. The veins developed a protecive shell and are dense enough to form a solid wall.
Its spore sacks shriveled and are covered in green slime.

actions:
You can use it to loose 100 satiation.
"""
        return text

    def destroy(self, generateScrap=True):
        """
        destroy this item and spawn a moster

        Parameters:
            generateScrap: flag to toggle leaving residue
        """

        new = itemMap["FireCrystals"]()
        self.container.addItem(new,self.getPosition())
        # new.startExploding()

        character = src.characters.Monster()

        character.solvers = [
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaiveExamineQuest",
            "ExamineQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "NaiveMurderQuest",
            "NaiveDropQuest",
        ]

        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                splittedCommand.append(char)
            return splittedCommand

        command = "opc"
        if src.gamestate.gamestate.tick % 2:
            command += "$=aam$=ddm"
            command += "$=wwm$=ssm"
        else:
            command += "$=wwm$=ssm"
            command += "$=aam$=ddm"

        command += "_m"
        character.macroState["macros"]["m"] = splitCommand(command)

        character.macroState["commandKeyQueue"] = [("_", []), ("m", [])]
        character.satiation = 100
        self.container.addCharacter(character, self.xPosition, self.yPosition)

        super().destroy(generateScrap=False)

src.items.addType(EncrustedPoisonBush)
