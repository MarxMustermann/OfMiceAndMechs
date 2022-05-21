import src
import random
import copy
import json

class EpochArtwork(src.items.Item):
    """
    """


    type = "EpochArtwork"

    def __init__(self, epochLength, name="EpochArtwork", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="EA", name=name)

        self.applyOptions.extend(
                        [
                                                                ("dummy", "dummy"),
                        ]
                        )
        self.applyMap = {
                        }
        self.firstUse = True
        self.epochLength = epochLength

    def apply(self,character):
        if self.firstUse:
            self.getEpochReward(character)
            self.firstUse = False

            self.changed("first use")

            quest = src.quests.DummyQuest("defend against the siege")
            character.assignQuest(quest)
            character.registers["HOMEx"] = 7
            character.registers["HOMEy"] = 7
            return
        super().apply(character)

    def getEpochReward(self,character):
        text = """
* Authorisation accepted *

You are now the commander of this outpost. Your task is to lead the defence of this outpost.

You are beeing sieged and your command is to hold the position and go down in glory.

Waves will appear every %s ticks. Each wave will be stronger than the last.

Defend yourself and surive as long as possible. To help you with that you got the universal leaders blessing.
"""%(self.epochLength,)

        character.baseDamage += 40
        character.addMessage("your base damage increased by 40")
        character.maxHealth += 1000
        character.health += 1000
        character.addMessage("your base damage increased by 1000")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        return

src.items.addType(EpochArtwork)
