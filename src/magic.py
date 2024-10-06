import src

import random

def spawnRoom(terrain,roomType):

    pass

def spawnWaves():
    for (godId,god) in src.gamestate.gamestate.gods.items():
        if ( (god["lastHeartPos"][0] != god["home"][0]) or
             (god["lastHeartPos"][1] != god["home"][1])):

            terrain = src.gamestate.gamestate.terrainMap[god["lastHeartPos"][1]][god["lastHeartPos"][0]]

            spectreHome = (god["home"][0],god["home"][1],0)

            numEnemies = 1
            numSpectres = 0
            numSpectres += numEnemies

            numGlassHeartsOnPos = 0
            for checkGod in src.gamestate.gamestate.gods.values():
                if god["lastHeartPos"] == checkGod["lastHeartPos"]:
                    numGlassHeartsOnPos += 1

            multipliers = (1.2,1.1,1.5,1.1)
            baseHealth = 50
            baseDamage = 5
            if src.gamestate.gamestate.difficulty == "easy":
                baseHealth = 10
                baseDamage = 3
                multipliers = (1.02,1.01,1.05,1.01)
            elif src.gamestate.gamestate.difficulty == "difficulty":
                baseHealth = 100
                baseDamage = 10
                multipliers = (1.7,1.5,2,1.5)

            for _i in range(numSpectres):
                enemy = src.characters.characterMap["Monster"](6,6)
                enemy.health = int(baseHealth*2*multipliers[0]**numGlassHeartsOnPos)
                enemy.maxHealth = enemy.health
                enemy.baseDamage = int(baseDamage+1*multipliers[1]**numGlassHeartsOnPos)
                enemy.faction = "spectre"
                enemy.tag = "spectre"
                enemy.name = "stealerSpectre"
                enemy.movementSpeed = 2
                enemy.registers["HOMETx"] = spectreHome[0]
                enemy.registers["HOMETy"] = spectreHome[1]
                enemy.registers["HOMEx"] = 7
                enemy.registers["HOMEy"] = 7
                enemy.personality["moveItemsOnCollision"] = False

                numTries = 0
                while True:
                    numTries += 1

                    bigPos = (random.randint(1,13),random.randint(1,13),0)
                    rooms = terrain.getRoomByPosition(bigPos)
                    if rooms:
                        if numTries < 10:
                            continue
                        rooms[0].addCharacter(enemy,6,6)
                        break
                    else:
                        terrain.addCharacter(enemy,15*bigPos[0]+7,15*bigPos[1]+7)
                        break

                quest = src.quests.questMap["DelveDungeon"](targetTerrain=(terrain.xPosition,terrain.yPosition,0),itemID=godId)
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                quest = src.quests.questMap["GoHome"]()
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                quest = src.quests.questMap["Vanish"]()
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)

                enemy = src.characters.characterMap["Monster"](6,6)
                #enemy.health = int(src.gamestate.gamestate.tick//(15*15*15)*1.5**numGlassHeartsOnPos)*2
                enemy.health = int(baseHealth*multipliers[2]**numGlassHeartsOnPos)
                enemy.maxHealth = enemy.health
                #enemy.baseDamage = int((5+(src.gamestate.gamestate.tick//(15*15*15))/10)*1.1**numGlassHeartsOnPos)
                enemy.baseDamage = int(baseDamage+3*multipliers[3]**numGlassHeartsOnPos)
                enemy.faction = "spectre"
                enemy.tag = "spectre"
                enemy.name = "killerSpectre"
                enemy.movementSpeed = 1.8
                enemy.registers["HOMETx"] = spectreHome[0]
                enemy.registers["HOMETy"] = spectreHome[1]
                enemy.registers["HOMEx"] = 7
                enemy.registers["HOMEy"] = 7
                enemy.personality["moveItemsOnCollision"] = False

                numTries = 0
                while True:
                    numTries += 1

                    bigPos = (random.randint(1,13),random.randint(1,13),0)
                    rooms = terrain.getRoomByPosition(bigPos)
                    if rooms:
                        if numTries < 10:
                            continue
                        rooms[0].addCharacter(enemy,6,6)
                        break
                    else:
                        terrain.addCharacter(enemy,15*bigPos[0]+7,15*bigPos[1]+7)
                        break

                quest = src.quests.questMap["ClearTerrain"]()
                quest.autoSolve = True
                quest.assignToCharacter(enemy)
                quest.activate()
                enemy.quests.append(quest)
