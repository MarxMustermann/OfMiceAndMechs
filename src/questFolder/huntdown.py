import src

class Huntdown(src.quests.MetaQuestSequence):
    type = "Huntdown"

    def __init__(self, description="huntdown", target=None, lifetime=None):
        questList = []
        super().__init__(questList,lifetime=lifetime)
        self.metaDescription = description
        self.target = target

    def triggerCompletionCheck(self,character=None):
        if self.target and self.target.dead:
            self.postHandler()
            return True
        return False

    def solver(self,character):
        self.triggerCompletionCheck()

        if not self.subQuests:
            if isinstance(character.container, src.rooms.Room):
                charPos = (character.container.xPosition,character.container.yPosition,0)
            else:
                charPos = (character.xPosition//15,character.yPosition//15,0)

            if not self.target.container:
                character.runCommandString("10.")
                return

            if isinstance(self.target.container, src.rooms.Room):
                targetPos = (self.target.container.xPosition,self.target.container.yPosition,0)
            else:
                targetPos = (self.target.xPosition//15,self.target.yPosition//15,0)

            if targetPos == (0,0,0):
                return

            if character.yPosition%15 == 0:
                character.runCommandString("s")
                return
            if character.yPosition%15 == 14:
                character.runCommandString("w")
                return
            if character.xPosition%15 == 0:
                character.runCommandString("d")
                return
            if character.xPosition%15 == 14:
                character.runCommandString("a")
                return

            if not charPos == targetPos:
                if abs(charPos[0]-targetPos[0])+abs(charPos[1]-targetPos[1]) == 1:
                    newPos = targetPos
                else:
                    self.fail()
                    return

                quest = src.quests.questMap["GoToTile"](paranoid=True,targetPosition=newPos)
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                return
            else:
                character.runCommandString("gg")
                return

        super().solver(character)

src.quests.addType(Huntdown)
