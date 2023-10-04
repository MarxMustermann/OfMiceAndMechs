import random
import string

import src


class Cocoon(src.items.Item):

    type = "Cocoon"
    name = "cocoon"
    description = "This is a cocoon"

    def __init__(self, noId=False):
        """
        set up internal state
        """

        super().__init__(display="oo")
        self.walkable = True
        self.charges = 0

    def render(self):
        if self.charges == 0:
            return "oo"
        if self.charges == 1:
            return "öö"
        if self.charges == 2:
            return "ÖÖ"

    def spawn(self,triggerCharacter=None):
        """
        spawn a monster
        """

        if self.charges == 0:
            character = src.characters.Maggot()
        elif self.charges == 1:
            character = src.characters.Monster()
            quest = src.quests.questMap["SecureTile"](toSecure=self.getBigPosition(),strict=True)
            quest.autoSolve = True
            quest.assignToCharacter(character)
            character.quests.append(quest)
            quest.activate()
        else:
            character = src.characters.Monster()
            character.movementSpeed = 0.4
            quest = src.quests.questMap["ClearTerrain"]()
            quest.autoSolve = True
            quest.assignToCharacter(character)
            character.quests.append(quest)
            quest.activate()
            if triggerCharacter:
                quest = src.quests.questMap["Huntdown"](target=triggerCharacter)
                quest.autoSolve = True
                quest.assignToCharacter(character)
                character.quests.append(quest)
                quest.activate()

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

        character.faction = 'mold_'+("".join(random.choice(string.ascii_letters) for _ in range(1,10)))
        character.timeTaken = 5

        if self.container:
            self.container.addCharacter(character, self.xPosition, self.yPosition)
        self.destroy()

    def pickUp(self, character):
        """
        handle getting picked up by a character

        Parameters:
            character: the character trying topick up the item
        """

        self.spawn(character)

    def apply(self, character):
        """
        handle getting eaten by a character

        Parameters:
            character: the character trying to use this item
        """

        self.spawn(character)

    def destroy(self, generateScrap=True):
        """
        destroy this item

        Parameters:
            generateScrap: flag to toggle leaving residue
        """
        super().destroy(generateScrap=False)

src.items.addType(Cocoon)
