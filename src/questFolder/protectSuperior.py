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
        if not self.lastSuperiorPos == self.getSuperiorsTileCoordinate(character):
            self.clearSubQuests()

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append((self.getSuperiorsTileCoordinate(character),"target"))
        return result

    def getSuperiorsTileCoordinate(self,character):
        return character.superior.getBigPosition()

    def solver(self, character):
        if not (character.superior or character.superior.dead):
            self.fail()
            return True
        
        if self.delegatedTask == False and character.rank < 6:
            command = ".QSNProtectSuperior\n ."
            character.runCommandString(command)
            self.delegatedTask = True
            return

        self.checkDoRecalc(character)

        if self.subQuests:
            return super().solver(character)

        if character.container == character.superior.container and self.getSuperiorsTileCoordinate(character) == character.getBigPosition():
            if character.container.getEnemiesOnTile(character):
                character.runCommandString("gg")
                return
            character.runCommandString("5.")
            return
        
        self.lastSuperiorPos = self.getSuperiorsTileCoordinate(character)
        self.addQuest(src.quests.questMap["GoToTile"](targetPosition=self.lastSuperiorPos,paranoid=True))
        return

src.quests.addType(ProtectSuperior)
