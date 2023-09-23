import src
import random

class KillGuards(src.quests.MetaQuestSequence):
    type = "KillGuards"

    def __init__(self, description="kill guards"):
        super().__init__()
        self.metaDescription = description

    def generateTextDescription(self):
        out = """
Eliminate the siege guard.

There is a group of enemies near entry of the base.
They guard the entrance of the base against outbreak or resupplies.
The guards are shown as white <-

Eliminate them to start breaking up the innermost siege ring.
Remove guards from the tiles (7,4,0) and (6,5,0)"""

        if not self.subQuests:
            out += """

This quest currently has no sub quests.
Press r to generate subquest and receive detailed instructions
"""
        return out

    def postHandler(self):
        if self.character == src.gamestate.gamestate.mainChar:
            src.gamestate.gamestate.save()
        super().postHandler()

    def solver(self,character):
        if self.triggerCompletionCheck(character):
            return

        if not self.subQuests:
            guard = random.choice(self.getGuards(character))
            quest = src.quests.questMap["SecureTile"](toSecure=guard.getBigPosition(),endWhenCleared=True,description="kill guards on tile ")
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            return
        super().solver(character)

    def wrapedTriggerCompletionCheck2(self, extraInfo):
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo["character"])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck2, "character died on tile")

        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if not self.getGuards(character):
            character.awardReputation(amount=250, reason="killing the guards")
            self.postHandler()
            return True

        return False

    def getGuards(self,character):
        enemies = []
        currentTerrain = character.getTerrain()

        foundEnemy = False
        for enemy in currentTerrain.characters:
            if enemy.tag == "blocker":
                enemies.append(enemy)
        for room in currentTerrain.rooms:
            for enemy in room.characters:
                if enemy.tag == "blocker":
                    enemies.append(enemy)

        return enemies

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        positions = []
        for guard in self.getGuards(character):
            pos = guard.getBigPosition()
            if not pos in positions:
                positions.append(pos)

        for pos in positions:
            result.append((pos,"target"))
        return result

src.quests.addType(KillGuards)
