import src


class EncrustedPoisonBush(src.items.Item):
    type = "EncrustedPoisonBush"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.encrustedPoisonBush)
        self.name = "encrusted poison bush"
        self.walkable = False

    def apply(self, character):
        if 100 > character.satiation:
            character.satiation = 0
        else:
            character.satiation -= 100

        character.addMessage(
            "you give your blood to the encrusted poison bush and loose 100 satiation"
        )

    def getLongInfo(self):
        return """
item: EncrustedPoisonBush

description:
This is a cluster of blooms. The veins developed a protecive shell and are dense enough to form a solid wall.
Its spore sacks shriveled and are covered in green slime.

actions:
You can use it to loose 100 satiation.
"""

    def destroy(self, generateSrcap=True):
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

        super().destroy(generateSrcap=False)


src.items.addType(EncrustedPoisonBush)
