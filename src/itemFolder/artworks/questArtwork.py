import src
import random


class QuestArtwork(src.items.Item):
    """
    ingame item spawning quests and giving rewards
    used to add more excitement and ressources to the game
    """

    type = "QuestArtwork"

    def __init__(self):
        """
        call superclass constructor with modified parameters
        """

        super().__init__(display="QA")

        self.name = "quest artwork"

        self.applyOptions.extend(
                [
                    ("getQuest", "get quest"),
                ]
            )
        self.applyMap = {
            "getQuest": self.getQuest,
        }
        self.numQuestsGiven = 0

        self.attributesToStore.extend(
                [
                    "numQuestsGiven",
                ]
            )

        self.description = """
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This artwork generates and can assign quests."""
        self.usageInfo = """
Use it to generate a quest and assign it to you."""
        

    def getEnemiesWithTag(self,tag):
        enemies = []
        currentTerrain = self.container.container

        foundEnemy = False
        for enemy in currentTerrain.characters:
            if enemy.tag == tag:
                enemies.append(enemy)
        for room in currentTerrain.rooms:
            for enemy in room.characters:
                if enemy.tag == tag:
                    enemies.append(enemy)

        return enemies

    def getQuest(self, character):
        print(character.rank)
        if character.rank == 6:
            enemies = self.getEnemiesWithTag("blocker")
            if enemies:
                quest = src.quests.questMap["KillGuards"]()
                if character.quests and isinstance(character.quests[0],src.quests.BeUsefull):
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests[0].addQuest(quest)
                else:
                    character.quests.insert(0,quest)
                text = """
Eliminate the siege guard.

There is a group of enemies near entry of the base.
They guard the entrance of the base against outbreak or resupplies.
The guards are shown as white <-

Eliminate them to start breaking up the innermost siege ring.
"""
                submenue = src.interaction.TextMenu(text)
                character.macroState["submenue"] = submenue
                character.changed("got quest assigned")
                return

            enemies = self.getEnemiesWithTag("lurker")
            if enemies:
                quest = src.quests.SecureTile(endWhenCleared=True, description="clear lurkers on tile ", reputationReward=50, rewardText="clearing lurkers")
                quest.setParameters({"targetPosition":enemies[0].getBigPosition()})
                quest.assignToCharacter(character)
                quest.activate()
                if character.quests and isinstance(character.quests[0],src.quests.BeUsefull):
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests[0].addQuest(quest)
                else:
                    character.quests.insert(0,quest)
                text = """
Eliminate the lurkers

There are enemy units scattered around the terrain.
Eliminate those groups of enemies to further our ability to move.
The guards are shown as white ss.

Eliminate them to build on breaking up the innermost siege ring.
"""
                submenue = src.interaction.TextMenu(text)
                character.macroState["submenue"] = submenue
                character.changed("got quest assigned")
                return

        elif character.rank == 5:
            enemies = self.getEnemiesWithTag("patrol")
            if enemies:
                quest = src.quests.questMap["KillPatrolers"]()
                if character.quests and isinstance(character.quests[0],src.quests.BeUsefull):
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests[0].addQuest(quest)
                else:
                    character.quests.insert(0,quest)
                text = """
Eliminate the patrolers

Eliminate them to start breaking up the innermost siege ring.
"""
                submenue = src.interaction.TextMenu(text)
                character.macroState["submenue"] = submenue
                character.changed("got quest assigned")
                return

        elif character.rank == 4:
            """
            for room in self.container.container.rooms:
                for target in room.characters:
                    if target.faction == character.faction:
                        continue
                    containerQuest = src.quests.MetaQuestSequence()
                    quest = src.quests.GoToTile()
                    quest.setParameters({"targetPosition":(self.container.xPosition,self.container.yPosition)})
                    quest.assignToCharacter(character)
                    containerQuest.addQuest(quest)
                    quest = src.quests.SecureTile(endWhenCleared=True)
                    quest.setParameters({"targetPosition":(room.xPosition,room.yPosition)})
                    quest.assignToCharacter(character)
                    quest.activate()
                    containerQuest.addQuest(quest)
                    containerQuest.assignToCharacter(character)
                    containerQuest.activate()

                    if character.quests and isinstance(character.quests[0],src.quests.BeUsefull):
                        character.quests[0].addQuest(containerQuest)
                    else:
                        character.quests.insert(0,containerQuest)
                    character.changed("got quest assigned")
                    return
            """
            quest = src.quests.questMap["SecureCargo"]()
            if character.quests and isinstance(character.quests[0],src.quests.BeUsefull):
                quest.assignToCharacter(character)
                quest.activate()
                character.quests[0].addQuest(quest)
            else:
                character.quests.insert(0,quest)
            text = """
Destroy the spawners to end the siege

"""
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            character.changed("got quest assigned")
            return
        elif character.rank == 3:
            quest = src.quests.questMap["DestroySpawners"]()
            if character.quests and isinstance(character.quests[0],src.quests.BeUsefull):
                quest.assignToCharacter(character)
                quest.activate()
                character.quests[0].addQuest(quest)
            else:
                character.quests.insert(0,quest)
            text = """
Destroy the spawners to end the siege

"""
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            character.changed("got quest assigned")
            return

        for line in src.gamestate.gamestate.terrainMap:
            for terrain in line:
                if isinstance(terrain,src.terrains.Ruin):
                    quest = src.quests.LootRuin()
                    quest.setParameters({"targetPosition":(terrain.xPosition,terrain.yPosition,0)})
                    quest.assignToCharacter(character)
                    quest.activate()

                    if character.quests and isinstance(character.quests[0],src.quests.BeUsefull):
                        quest.assignToCharacter(character)
                        quest.activate()
                        character.quests[0].addQuest(quest)
                    else:
                        character.quests.insert(0,quest)
                    character.changed("got quest assigned")
                    return

        character.addMessage("no quest assigned")
        return

src.items.addType(QuestArtwork)
