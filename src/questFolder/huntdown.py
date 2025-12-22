import src


class Huntdown(src.quests.MetaQuestSequence):
    type = "Huntdown"

    def __init__(self, description="huntdown", target=None, lifetime=None, alwaysfollow = False, reason=None):
        questList = []
        super().__init__(questList,lifetime=lifetime)
        self.metaDescription = description
        self.target = target
        self.alwaysfollow = alwaysfollow
        self.reason = reason

    def generateTextDescription(self):
        out = []

        reasonText = ""
        if self.reason:
            reasonText += f", to {self.reason}"
        text = f"""
Hunt down enemy{reasonText}."""

        out.append(text)
        return out

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if self.target:
            if self.target.dead:
                if not dryRun:
                    self.postHandler()
                return True
            if self.target.faction == character.faction:
                if not dryRun:
                    self.postHandler()
                return True
        return False

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        # end quest when done
        self.triggerCompletionCheck(dryRun=dryRun)

        # handle weird edge cases
        if self.subQuests:
            return (None,None)

        if not self.target.container:
            return (None,("10.","wait"))

        if isinstance(self.target.container, src.rooms.Room):
            targetPos = (self.target.container.xPosition,self.target.container.yPosition,0)
        else:
            targetPos = (self.target.xPosition//15,self.target.yPosition//15,0)

        if targetPos == (0,0,0):
            return (None,(".","stand around confused"))

        if character.yPosition%15 == 0:
            return (None,("s","move toward target"))
        if character.yPosition%15 == 14:
            return (None,("w","move toward target"))
        if character.xPosition%15 == 0:
            return (None,("d","move toward target"))
        if character.xPosition%15 == 14:
            return (None,("a","move toward target"))

        if isinstance(character.container, src.rooms.Room):
            charPos = (character.container.xPosition,character.container.yPosition,0)
        else:
            charPos = (character.xPosition//15,character.yPosition//15,0)
        if charPos != targetPos:
            if self.alwaysfollow or abs(charPos[0]-targetPos[0])+abs(charPos[1]-targetPos[1]) == 1:
                newPos = targetPos
            else:
                abort_reason = "target escaped"
                if not dryRun:
                    self.fail(abort_reason)                     
                return (None,("+",f"abort quest\n({abort_reason})"))

            if newPos[0] in (0,14,) or newPos[1] in (0,14):
                abort_reason = "target left terrain"
                if not dryRun:
                    self.fail(abort_reason)
                return (None,("+",f"abort quest\n({abort_reason})"))

            quest = src.quests.questMap["GoToTile"](paranoid=True,targetPosition=newPos)
            return ([quest],None)

        quest = src.quests.questMap["Fight"](suicidal=True)
        return ([quest],None)

src.quests.addType(Huntdown)
