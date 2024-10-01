import src


class Huntdown(src.quests.MetaQuestSequenceV2):
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

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        self.triggerCompletionCheck()

        if not self.subQuests:
            if isinstance(character.container, src.rooms.Room):
                charPos = (character.container.xPosition,character.container.yPosition,0)
            else:
                charPos = (character.xPosition//15,character.yPosition//15,0)

            if not self.target.container:
                return (None,("10.","wait"))

            if isinstance(self.target.container, src.rooms.Room):
                targetPos = (self.target.container.xPosition,self.target.container.yPosition,0)
            else:
                targetPos = (self.target.xPosition//15,self.target.yPosition//15,0)

            if targetPos == (0,0,0):
                return (None,None)

            if character.yPosition%15 == 0:
                return (None,("s","move toward target"))
            if character.yPosition%15 == 14:
                return (None,("w","move toward target"))
            if character.xPosition%15 == 0:
                return (None,("d","move toward target"))
            if character.xPosition%15 == 14:
                return (None,("a","move toward target"))

            if charPos != targetPos:
                if abs(charPos[0]-targetPos[0])+abs(charPos[1]-targetPos[1]) == 1:
                    newPos = targetPos
                else:
                    if not dryRun:
                        self.fail()                     
                    return (None,None)

                quest = src.quests.questMap["GoToTile"](paranoid=True,targetPosition=newPos)
                return ([quest],None)
            quest = src.quests.questMap["Fight"](suicidal=True)
            return ([quest],None)
        return (None,None)
src.quests.addType(Huntdown)
