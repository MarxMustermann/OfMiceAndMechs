import src

class KillPatrolers(src.quests.MetaQuestSequence):
    type = "KillPatrolers"

    def __init__(self, description="kill patrolers"):
        super().__init__()
        self.metaDescription = description

    def generateTextDescription(self):
        out = """
There are groups of enemies patrolling around the base.
They make movement around the base harder and hinder operations outside the base.
The patrols are shown as white X-

Ambush them in front of the base to break up the second siege ring."""

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

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if not self.active:
            return False

        if not self.getPatrolers(character):
            character.awardReputation(amount=400, reason="killing the patrolers")
            self.postHandler()
            return True

        return False

    def solver(self,character):
        self.triggerCompletionCheck(character)

        if not self.subQuests:
            quest = src.quests.questMap["SecureTile"](toSecure=(7,4,0),endWhenCleared=False,description="ambush patrolers on tile ")
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            return

        super().solver(character)

    def getPatrolers(self,character):
        enemies = []
        currentTerrain = character.getTerrain()

        foundEnemy = False
        for enemy in currentTerrain.characters:
            if enemy.tag == "patrol":
                enemies.append(enemy)
        for room in currentTerrain.rooms:
            for enemy in room.characters:
                if enemy.tag == "patrol":
                    enemies.append(enemy)

        return enemies

    def wrapedTriggerCompletionCheck2(self, extraInfo):
        self.triggerCompletionCheck(extraInfo["character"])

    def handleTileChange(self):
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck2, "character died on tile")
        self.startWatching(character,self.handleTileChange, "changedTile")

        super().assignToCharacter(character)

src.quests.addType(KillPatrolers)
