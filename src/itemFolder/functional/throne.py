import src
import random

class Throne(src.items.Item):
    """
    ingame item ment to be placed by characters and to mark things with
    """

    type = "Throne"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        self.activated = False
        super().__init__("TT")
        self.walkable = False
        self.bolted = False
        self.name = "throne"
        self.description = """
A throne. Take control over the throne to win the game.
"""
        self.wavesSpawned = 0
        self.lastWave = None
        self.maxWaves = 5

    def apply(self,character):
        self.maxWaves = 5

        if self.wavesSpawned == 0:
            hasAllSpecialItems = True
            currentTerrain = character.getTerrain()

            terrainPos = (currentTerrain.xPosition,currentTerrain.yPosition)

            foundMissingHeart = False
            for god in src.gamestate.gamestate.gods.values():
                if god["lastHeartPos"] == terrainPos:
                    continue
                foundMissingHeart = True

            if foundMissingHeart:
                character.addMessage("you need to control all GlassHearts")
                return

            if character == src.gamestate.gamestate.mainChar:
                text = f"""
You control all GlassHearts and activate the throne.
But it does not accept you, yet.

Instead it spawns a wave of enemies.
Defeat {self.maxWaves} waves of enemies and it will accept you.

If you don't trigger a wave each epoch it will be trigerred automatically.
Each wave will be stronger than the last.

= press enter to continue =
"""
                src.interaction.showInterruptText(text)
                self.handleEpochChange()
        elif self.wavesSpawned == self.maxWaves:
            text = """
The Throne accept you and take control.
You hereby win the game congratz.

No more waves are triggered and you reached the end of the main game loop.
The game will keep running so that you can extend your base and build stuff until the game lags.

You may or may not find experimental content from this point on.

= press enter to continue =
"""
            src.interaction.showInterruptText(text)
        else:
            enemiesFound = False
            for otherCharacter in self.getTerrain().characters:
                if not character.faction == otherCharacter.faction:
                    enemiesFound = True
                    break

            for room in self.getTerrain().rooms:
                for otherCharacter in room.characters:
                    if not character.faction == otherCharacter.faction:
                        enemiesFound = True
                        break

            if enemiesFound:
                text = "you need to clear all enemies to trigger the next wave"
                character.showTextMenu(text)
                return

            self.spawnWave()

            text = """
A new wave has spawned.
"""
            character.showTextMenu(text)

    def spawnWave(self):
        if self.wavesSpawned == self.maxWaves:
            return

        self.lastWave = src.gamestate.gamestate.tick
        self.wavesSpawned += 1
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

                for _i in range(numSpectres):
                    enemy = src.characters.Monster(6,6)
                    #enemy.health = int(src.gamestate.gamestate.tick//(15*15*15)*1.5**numGlassHeartsOnPos)//2+1
                    enemy.health = int(10*1.2**numGlassHeartsOnPos)
                    enemy.maxHealth = enemy.health
                    #enemy.baseDamage = int((5+(src.gamestate.gamestate.tick//(15*15*15))/10)*1.1**numGlassHeartsOnPos)
                    enemy.baseDamage = int(5+1*1.1**numGlassHeartsOnPos)
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

                    enemy = src.characters.Monster(6,6)
                    #enemy.health = int(src.gamestate.gamestate.tick//(15*15*15)*1.5**numGlassHeartsOnPos)*2
                    enemy.health = int(10*1.5**numGlassHeartsOnPos)
                    enemy.maxHealth = enemy.health
                    #enemy.baseDamage = int((5+(src.gamestate.gamestate.tick//(15*15*15))/10)*1.1**numGlassHeartsOnPos)
                    enemy.baseDamage = int(5+3*1.1**numGlassHeartsOnPos)
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

    def handleEpochChange(self):
        if self.wavesSpawned == self.maxWaves:
            return

        if self.lastWave == None:
            self.spawnWave()

        if (src.gamestate.gamestate.tick-self.lastWave) >= (15*15*15):
            self.spawnWave()

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(15*15*15-src.gamestate.gamestate.tick%(15*15*15)))
        event.setCallback({"container": self, "method": "handleEpochChange"})
        self.container.addEvent(event)

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Thone")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Thone")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(Throne)
