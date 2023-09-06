import src

class ProtectSuperior(src.quests.MetaQuestSequence):
    type = "ProtectSuperior"

    def __init__(self, description="protect superior", toProtect=None):
        questList = []
        super().__init__(questList)
        self.metaDescription = description

        self.lastSuperiorPos = None
        self.delegatedTask = False

    def triggerCompletionCheck(self,character=None):
        return False

    def checkDoRecalc(self,character):
        if character.superior.dead:
            self.fail()
            return

        if not character.getTerrain() == character.superior.getTerrain():
            return

        if not self.lastSuperiorPos == self.getSuperiorsTileCoordinate(character):
            self.clearSubQuests()

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append((self.getSuperiorsTileCoordinate(character),"target"))
        return result

    def getSuperiorsTileCoordinate(self,character):
        return character.superior.getBigPosition()

    def solver(self, character):
        character.timeTaken += 0.1
        if not (character.superior or character.superior.dead):
            self.fail()
            return True
        
        """
        if self.delegatedTask == False and character.rank < 6:
            command = ".QSNProtectSuperior\n ."
            character.runCommandString(command)
            self.delegatedTask = True
            return
        """

        self.checkDoRecalc(character)

        if self.subQuests:
            return super().solver(character)

        if not character.getTerrain() == character.superior.getTerrain():
            targetTerrain = character.superior.getTerrain()
            if not targetTerrain:
                character.timeTaken += 0.5
                return
            pos = (targetTerrain.xPosition,targetTerrain.yPosition,0)
            self.addQuest(src.quests.questMap["GoToTerrain"](targetTerrain=pos))
            return

        if character.container == character.superior.container and self.getSuperiorsTileCoordinate(character) == character.getBigPosition():
            if character.container.getEnemiesOnTile(character):
                self.addQuest(src.quests.questMap["Fight"]())
                return
            character.runCommandString("5.")
            return
        
        self.lastSuperiorPos = self.getSuperiorsTileCoordinate(character)
        if not self.lastSuperiorPos[0] in (0,14,) and not self.lastSuperiorPos[1] in (0,14,):
            self.addQuest(src.quests.questMap["GoToTile"](targetPosition=self.lastSuperiorPos,paranoid=True))
            return

src.quests.addType(ProtectSuperior)
