import random

import src


class SupportAttack(src.quests.MetaQuestSequence):
    type = "SupportAttack"

    def __init__(self, description="support attack", toProtect=None):
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

        if character.getTerrain() != character.superior.getTerrain():
            return

        if self.lastSuperiorPos != self.getSuperiorsTileCoordinate(character):
            self.clearSubQuests()
            self.lastSuperiorPos = self.getSuperiorsTileCoordinate(character)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append((self.getSuperiorsTileCoordinate(character),"target"))
        return result

    def getSuperiorsTileCoordinate(self,character):
        return character.superior.getBigPosition()

    def solver(self, character):
        character.personality["autoCounterAttack"] = False
        character.personality["autoFlee"] = False

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

        if character.getTerrain() != character.superior.getTerrain():
            targetTerrain = character.superior.getTerrain()
            pos = (targetTerrain.xPosition,targetTerrain.yPosition,0)
            self.addQuest(src.quests.questMap["GoToTerrain"](targetTerrain=pos))
            return None

        if character.container == character.superior.container and self.getSuperiorsTileCoordinate(character) == character.getBigPosition():
            terrain = character.getTerrain()

            if terrain.getEnemiesOnTile(character):
                if character.health < character.maxHealth//5:
                    self.addQuest(src.quests.questMap["Flee"]())
                    return None
                else:
                    self.addQuest(src.quests.questMap["Fight"]())
                    return None

            if character.container.isRoom:
                pos = character.getBigPosition()
                if character.superior.getSpacePosition() == (6,12,0):
                    self.addQuest(src.quests.questMap["SecureTile"](toSecure=(pos[0],pos[1]+1,0),endWhenCleared=True))
                    return None
                if character.superior.getSpacePosition() == (6,11,0) and character.getPosition() != (6, 11, 0):
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=(6,11,0)))
                    return None
                if character.superior.getSpacePosition() == (12,6,0):
                    self.addQuest(src.quests.questMap["SecureTile"](toSecure=(pos[0]+1,pos[1],0),endWhenCleared=True))
                    return None
                if character.superior.getSpacePosition() == (11,6,0) and character.getPosition() != (11, 6, 0):
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=(11,6,0)))
                    return None
                if character.superior.getSpacePosition() == (0,6,0):
                    self.addQuest(src.quests.questMap["SecureTile"](toSecure=(pos[0]-1,pos[1],0),endWhenCleared=True))
                    return None
                if character.superior.getSpacePosition() == (1,6,0) and character.getPosition() != (1, 6, 0):
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=(1,6,0)))
                    return None
                if character.superior.getSpacePosition() == (6,0,0):
                    self.addQuest(src.quests.questMap["SecureTile"](toSecure=(pos[0],pos[1]-1,0),endWhenCleared=True))
                    return None
                if character.superior.getSpacePosition() == (6,1,0) and character.getPosition() != (6, 1, 0):
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=(6,1,0)))
                    return None
            else:
                pos = character.getBigPosition()
                if character.superior.getSpacePosition() == (7,13,0) and character.getPosition() != (7, 13, 0):
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=(7,13,0)))
                    return None
                if character.superior.getSpacePosition() == (13,7,0) and character.getPosition() != (13, 7, 0):
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=(13,7,0)))
                    return None
                if character.superior.getSpacePosition() == (1,7,0) and character.getPosition() != (1, 7, 0):
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=(1,7,0)))
                    return None
                if character.superior.getSpacePosition() == (7,1,0) and character.getPosition() != (7, 1, 0):
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=(7,1,0)))
                    return None

            offsets = [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0)]
            pos = character.getBigPosition()
            for offset in offsets:
                checkPos = (pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2])
                enemiesFound = []
                for otherChar in terrain.charactersByTile.get(checkPos,[]):
                    if otherChar.faction == character.faction:
                        continue
                    if otherChar.dead:
                        continue
                    enemiesFound.append(otherChar)
                for room in terrain.getRoomByPosition(checkPos):
                    for otherChar in room.characters:
                        if otherChar.faction == character.faction:
                            continue
                        if otherChar.dead:
                            continue
                        enemiesFound.append(otherChar)

                if enemiesFound:
                    challengeRating = 0
                    challengeRating -= character.health
                    armorValue = 0
                    if character.armor:
                        armorValue = character.armor.armorValue
                    completeDamage = 0
                    completeHealth = 0
                    for enemyFound in enemiesFound:
                        completeDamage += max(0,enemyFound.baseDamage-armorValue)
                        completeHealth += enemyFound.health
                    ownDamage = character.baseDamage
                    if character.weapon:
                        ownDamage += character.weapon.baseDamage

                    numTurns = completeHealth//ownDamage+1
                    challengeRating += numTurns*completeDamage

                    if challengeRating < 0:
                        self.addQuest(src.quests.questMap["SecureTile"](toSecure=checkPos,endWhenCleared=True))
                        return None

            if character.getFreeInventorySpace() > 2 and character.container.isRoom:
                moldFeeds = character.container.getItemsByType("MoldFeed")
                random.shuffle(moldFeeds)
                for moldFeed in moldFeeds:
                    self.addQuest(src.quests.questMap["CleanSpace"](targetPosition=moldFeed.getPosition(),targetPositionBig=moldFeed.getBigPosition()))
                    return None

            if character.health < character.maxHealth-30 and character.container.isRoom:
                coalBurner = character.container.getItemByType("CoalBurner")
                if coalBurner:
                    if character.getDistance(coalBurner.getPosition()) > 1:
                        self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=coalBurner.getPosition(),ignoreEndBlocked=True))
                        return None
                    if coalBurner.getPosition() == character.getPosition(offset=(-1,0,0)):
                        character.runCommandString("Ja")
                        return None
                    if coalBurner.getPosition() == character.getPosition(offset=(1,0,0)):
                        character.runCommandString("Jd")
                        return None
                    if coalBurner.getPosition() == character.getPosition(offset=(0,-1,0)):
                        character.runCommandString("Jw")
                        return None
                    if coalBurner.getPosition() == character.getPosition(offset=(0,1,0)):
                        character.runCommandString("Js")
                        return None

            character.runCommandString(".....")
            return None

        self.lastSuperiorPos = self.getSuperiorsTileCoordinate(character)
        if self.lastSuperiorPos[0] not in (0,14,) and self.lastSuperiorPos[1] not in (0,14,):
            self.addQuest(src.quests.questMap["GoToTile"](targetPosition=self.lastSuperiorPos,paranoid=True))
            return None
        return None

src.quests.addType(SupportAttack)
