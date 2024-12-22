import src
import random

class Adventure(src.quests.MetaQuestSequence):
    type = "Adventure"

    def __init__(self, description="adventure", creator=None, lifetime=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.visited_terrain = []
        self.track = []
        self.terrainInfo = {}

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.getBigPosition()[0] == 0:
            return (None, ("d","enter the terrain"))
        if character.getBigPosition()[0] == 14:
            return (None, ("a","enter the terrain"))
        if character.getBigPosition()[1] == 0:
            return (None, ("s","enter the terrain"))
        if character.getBigPosition()[1] == 14:
            return (None, ("w","enter the terrain"))
        
        currentTerrain = character.getTerrain()

        if character.getFreeInventorySpace() < 2:
            if currentTerrain.tag == "shrine":
                quest = src.quests.questMap["GoHome"]()
                return ([quest],None)
        try:
            self.visited_terrain
        except:
            self.visited_terrain = []

        candidates = []
        for x in range(1,14):
            for y in range(1,14):
                if (x, y, 0) in self.visited_terrain:
                    continue
                candidates.append((x, y, 0))

        homeCoordinate = (character.registers["HOMETx"], character.registers["HOMETy"], 0)
        candidates.remove(homeCoordinate)

        if len(candidates):
            random.shuffle(candidates)
            candidates.sort(key=lambda x: src.helpers.distance_between_points(character.getTerrainPosition(), x)+random.random())
            targetTerrain = candidates[0]
            if not dryRun:
                self.visited_terrain.append(targetTerrain)
            quest = src.quests.questMap["AdventureOnTerrain"](targetTerrain=targetTerrain)
            return ([quest], None)

        if dryRun:
            self.fail()
        return (None, None)

    def generateTextDescription(self):
        text = ["""
Go out and adventure.

track:

"""]
        homeCoordinate = (self.character.registers["HOMETx"], self.character.registers["HOMETy"], 0)
        characterCoordinate = self.character.getTerrain().getPosition()

        rawMap = []
        for y in range(15):
            rawMap.append([])
            for x in range(15):
                if x == 0 or y == 0 or x == 14 or y == 14:
                    rawMap[y].append("~~")
                else:
                    rawMap[y].append("  ")
            rawMap[y].append("\n")

        for (pos,info) in self.terrainInfo.items():
            if info["tag"] == "nothingness":
                rawMap[pos[1]][pos[0]] = src.canvas.displayChars.dirt
            elif info["tag"] == "shrine":
                rawMap[pos[1]][pos[0]] = (src.interaction.urwid.AttrSpec("#999", "black"),"\\/")
            elif info["tag"] == "ruin":
                rawMap[pos[1]][pos[0]] = (src.interaction.urwid.AttrSpec("#666", "black"),"&%")
            else:
                rawMap[pos[1]][pos[0]] = info["tag"][:2]
        rawMap[homeCoordinate[1]][homeCoordinate[0]] = "HH"
        rawMap[characterCoordinate[1]][characterCoordinate[0]] = "@@"

        text.extend(rawMap)
        text.extend("\n")
        text.extend("0: Home base\n")
    
        counter = 1
        for item in self.track:
            text.append(f"{counter}: {item}\n")
            counter += 1
        return text

    def handleChangedTerrain(self,extraInfo):
        terrain = extraInfo["character"].getTerrain()
        pos = terrain.getPosition()
        tag = terrain.tag
        self.track.append({"pos":pos,"tag":tag})
        self.terrainInfo[pos] = {"tag":tag}

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleChangedTerrain, "changedTerrain")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        currentTerrain = character.getTerrain()
        if not currentTerrain.xPosition == character.registers["HOMETx"]:
            return False
        if not currentTerrain.yPosition == character.registers["HOMETy"]:
            return False

        if not character.getFreeInventorySpace() < 2:
            return False

        self.postHandler()
        return True

src.quests.addType(Adventure)
