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
        if character.rank == 6:
            enemies = self.getEnemiesWithTag("blocker")
            if enemies:
                quest = src.quests.questMap["KillGuards"]()
                if character.quests and isinstance(character.quests[0],src.quests.questMap["BeUsefull"]):
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests[0].addQuest(quest)
                else:
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests.insert(0,quest)
                text = """
Eliminate the siege guard.

There is a group of enemies near entry of the base.
They guard the entrance of the base against outbreak or resupplies.
The guards are shown as white <-

Eliminate them to start breaking up the innermost siege ring.
"""
                submenue = src.interaction.TextMenu(text)
                character.addMessage(text)
                character.macroState["submenue"] = submenue
                character.changed("got quest assigned")
                return

            enemies = self.getEnemiesWithTag("lurker")
            if enemies:
                quest = src.quests.SecureTile(endWhenCleared=True, description="clear lurkers on tile ", reputationReward=50, rewardText="clearing lurkers")
                quest.setParameters({"targetPosition":random.choice(enemies).getBigPosition()})
                quest.assignToCharacter(character)
                quest.activate()
                if character.quests and isinstance(character.quests[0],src.quests.questMap["BeUsefull"]):
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests[0].addQuest(quest)
                else:
                    character.quests.insert(0,quest)
                text = """
Eliminate the lurkers

There are enemy units scattered around the terrain.
Eliminate those groups of enemies to further our ability to move.
The lurkers are shown as white ss.

Eliminate them to build on breaking up the innermost siege ring.
"""
                character.addMessage("----------------"+text+"-----------------")

                submenue = src.interaction.TextMenu(text)
                character.addMessage(text)
                character.macroState["submenue"] = submenue
                character.changed("got quest assigned")
                return

            quest = src.quests.CleanTraps(reputationReward=50)
            quest.assignToCharacter(character)
            quest.activate()
            if character.quests and isinstance(character.quests[0],src.quests.questMap["BeUsefull"]):
                quest.assignToCharacter(character)
                quest.activate()
                character.quests[0].addQuest(quest)
            else:
                character.quests.insert(0,quest)
            text = """
Clean the traps

The trap rooms are the bases first line of defence.
The trap rooms work by shocking enemies that step on the floor.
This does not work when items are lying on the floor.

Often corpses litter the trap rooms and reduce the traps effectiveness.
Clear the trap rooms to ensure that the bases first line of defence works.
"""
            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.addMessage(text)
            character.macroState["submenue"] = submenue
            character.changed("got quest assigned")

        elif character.rank == 5:
            currentTerrain = character.getTerrain()
            rooms = currentTerrain.getRoomsByTag("cargo")
            items = []
            if rooms:
                items = rooms[0].itemsOnFloor
            foundItems = False
            for item in items:
                if item.type in ("Sword","Armor",):
                    foundItems = True
                    break

            if foundItems:
                quest = src.quests.questMap["SecureCargo"]()
                if character.quests and isinstance(character.quests[0],src.quests.questMap["BeUsefull"]):
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests[0].addQuest(quest)
                else:
                    character.quests.insert(0,quest)
                text = """
Secure the cargo

There was a supply run intended for the base.
It got ambushed and the suplies were left there.
Go there and fetch the weapons and armor.

    """
                character.addMessage("----------------"+text+"-----------------")

                submenue = src.interaction.TextMenu(text)
                character.addMessage(text)
                character.macroState["submenue"] = submenue
                character.changed("got quest assigned")
                return

            terrain = character.getTerrain()
            rooms = terrain.getRoomsByTag("farm")

            nearestDistance = None
            candidates = []
            for room in rooms:
                for item in room.itemsOnFloor:
                    if item.type in ("Scrap",):
                        continue
                    if item.bolted:
                        continue
                    
                    distance = abs(room.xPosition-7)+abs(room.yPosition-7)
                    if nearestDistance == None or distance < nearestDistance:
                        candidates = []
                        nearestDistance = distance

                    if distance > nearestDistance:
                        continue

                    candidates.append(room)

            if candidates:
                room = random.choice(candidates)
                quest = src.quests.questMap["LootRoom"](roomPos=room.getPosition(),description="loot farm")
                if character.quests and isinstance(character.quests[0],src.quests.questMap["BeUsefull"]):
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests[0].addQuest(quest)
                else:
                    character.quests.insert(0,quest)
                text = """
Secure goo flasks

The ruined farms still have useful items in them.
Secure the farms on the position %s and loot the items there.

"""%(room.getPosition(),)
                character.addMessage("----------------"+text+"-----------------")

                submenue = src.interaction.TextMenu(text)
                character.addMessage(text)
                character.macroState["submenue"] = submenue
                character.changed("got quest assigned")
                return

        elif character.rank == 4:
            enemies = self.getEnemiesWithTag("patrol")
            if enemies:
                quest = src.quests.questMap["KillPatrolers"]()
                if character.quests and isinstance(character.quests[0],src.quests.questMap["BeUsefull"]):
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests[0].addQuest(quest)
                else:
                    character.quests.insert(0,quest)
                text = """
Eliminate the patrolers

There are groups of enemies patroling around the base.
They make movement around the base harder and hinder operations outside the base.
The patrols are shown as white X-

Eliminate them to break up the second siege ring.

"""

                character.addMessage("----------------"+text+"-----------------")

                submenue = src.interaction.TextMenu(text)
                character.addMessage(text)
                character.macroState["submenue"] = submenue
                character.changed("got quest assigned")
                return

            enemies = self.getEnemiesWithTag("hiveGuard")
            if enemies:
                enemiesMap = {}
                for enemy in enemies:
                    pos = enemy.getBigPosition()
                    if not pos in enemiesMap:
                        enemiesMap[pos] = 0
                    enemiesMap[pos] += 1

                lowestEnemyAmount = None
                candidates = []
                for (key, value) in enemiesMap.items():
                    if lowestEnemyAmount == None or value < lowestEnemyAmount:
                        candidates = []
                        lowestEnemyAmount = value

                    if value > lowestEnemyAmount:
                        continue

                    candidates.append(key)

                pos = random.choice(candidates)

                minDistance = None
                for candidate in candidates:
                    distance = abs(candidate[0]-7)+abs(candidate[1]-7)
                    if minDistance == None or distance < minDistance:
                        minDistance = distance
                        pos = candidate

                quest = src.quests.SecureTile(endWhenCleared=True, description="clear hive guards from tile ", reputationReward=150, rewardText="clearing hive guards")
                quest.setParameters({"targetPosition":pos})
                quest.assignToCharacter(character)
                quest.activate()
                if character.quests and isinstance(character.quests[0],src.quests.questMap["BeUsefull"]):
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests[0].addQuest(quest)
                else:
                    character.quests.insert(0,quest)
                text = """
Eliminate the hive guards

To stop the siege the hives must be destroyed.
Eliminate the hive guards to lighten their defence.

---

The hives spawn a big wave of enemies at the beginning of each epoch.
So try to not be nearby at that point.

"""
                character.addMessage("----------------"+text+"-----------------")

                submenue = src.interaction.TextMenu(text)
                character.addMessage(text)
                character.macroState["submenue"] = submenue
                character.changed("got quest assigned")
                return


        elif character.rank == 3:
            foundSpawner = False
            terrain = character.getTerrain()
            for room in terrain.rooms:
                items = room.getItemByPosition((6,6,0))
                for item in items:
                    if isinstance(item, src.items.itemMap["MonsterSpawner"]):
                        foundSpawner = True
                        break

            if foundSpawner:
                quest = src.quests.questMap["DestroySpawners"]()
                if character.quests and isinstance(character.quests[0],src.quests.questMap["BeUsefull"]):
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests[0].addQuest(quest)
                else:
                    character.quests.insert(0,quest)
                text = """
Destroy the hives to end the siege

The waves of enemies spawn from hives.
The hives are located inbetween the overrun farms.
Destroy the hives to end the siege.

---

The waves spawn at tick 0 of each epoch from the hives.
Try to not get caught up in the waves.

"""
            else:
                quest = src.quests.questMap["ClearTerrain"]()
                if character.quests and isinstance(character.quests[0],src.quests.questMap["BeUsefull"]):
                    quest.assignToCharacter(character)
                    quest.activate()
                    character.quests[0].addQuest(quest)
                else:
                    character.quests.insert(0,quest)
                text = """
kill all remaining enemies
"""

            character.addMessage("----------------"+text+"-----------------")
            character.addMessage(text)
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            character.changed("got quest assigned")
            return
        
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

                if character.quests and isinstance(character.quests[0],src.quests.questMap["BeUsefull"]):
                    character.quests[0].addQuest(containerQuest)
                else:
                    character.quests.insert(0,containerQuest)
                character.changed("got quest assigned")
                return

        for line in src.gamestate.gamestate.terrainMap:
            for terrain in line:
                if isinstance(terrain,src.terrains.Ruin):
                    quest = src.quests.LootRuin()
                    quest.setParameters({"targetPosition":(terrain.xPosition,terrain.yPosition,0)})
                    quest.assignToCharacter(character)
                    quest.activate()

                    if character.quests and isinstance(character.quests[0],src.quests.questMap["BeUsefull"]):
                        quest.assignToCharacter(character)
                        quest.activate()
                        character.quests[0].addQuest(quest)
                    else:
                        character.quests.insert(0,quest)
                    character.changed("got quest assigned")
                    return
        """

        character.addMessage("no quest assigned")
        return

src.items.addType(QuestArtwork)
