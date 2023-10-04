import random

import src


class ClearPathToPosition(src.quests.MetaQuestSequence):
    type = "ClearPathToPosition"

    def __init__(self, description="clear path to position", creator=None, targetPosition=None, tryHard=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+f" {targetPosition}"
        self.targetPosition = targetPosition
        self.tryHard = tryHard
        self.reason = reason
        self.path = None

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Clear path to position {self.targetPosition}{reason}.

Pick up and unbolt items that are in the way.
"""

        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return None

        pos = character.getPosition()
        pos = (pos[0]%15,pos[1]%15,pos[2]%15)
        if pos == self.targetPosition:
            self.postHandler()
            return True
        return None

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            if not self.path:
                x = character.xPosition%15
                y = character.yPosition%15
                path = []

                if character.container.isRoom:
                    generatedPath = character.container.getPathCommandTile(character.getSpacePosition(),self.targetPosition,character=character,clearing=True)[1]
                else:
                    generatedPath = character.container.getPathCommandTile(character.getTilePosition(),character.getSpacePosition(),self.targetPosition,character=character,clearing=True)[1]

                for offset in generatedPath:
                    x += offset[0]
                    y += offset[1]

                    path.append((x,y,0))

                self.path = path

            if not self.path:
                return (None,None)

            x = character.xPosition%15
            y = character.yPosition%15

            if self.path[0] == (x,y,0):
                self.path.remove((x,y,0))

            offset = None
            if (x-1,y  ,0) == self.path[0]:
                offset = (-1, 0,0)
            if (x+1,y  ,0) == self.path[0]:
                offset = ( 1, 0,0)
            if (x  ,y-1,0) == self.path[0]:
                offset = ( 0,-1,0)
            if (x  ,y+1,0) == self.path[0]:
                offset = ( 0, 1,0)

            if not offset:
                self.path = None
                return (None,None)

            if not character.container.getPositionWalkable(character.getPosition(offset=offset)):
                if not character.getFreeInventorySpace():
                    if not character.container.getItemByPosition(character.getPosition()):
                        return (None,("l","drop item"))
                    directions = ["."]
                    if character.xPosition not in (0,1,):
                        directions.append("a")
                    if character.yPosition not in (0,1,):
                        directions.append("w")
                    if not (character.xPosition in (11,12,) and character.container.isRoom):
                        directions.append("d")
                    if not (character.yPosition in (11,12,) and character.container.isRoom):
                        directions.append("s")
                    if not (character.xPosition in (13,14,) and not character.container.isRoom):
                        directions.append("d")
                    if not (character.yPosition in (13,14,) and not character.container.isRoom):
                        directions.append("s")
                    return (None,("L"+random.choice(directions),"drop item"))

                direction = "."
                if offset == (-1, 0,0):
                    direction = "a"
                if offset == ( 1, 0,0):
                    direction = "d"
                if offset == ( 0,-1,0):
                    direction = "w"
                if offset == ( 0, 1,0):
                    direction = "s"

                items = character.container.getItemByPosition(character.getPosition(offset=offset))
                if items and items[0].bolted:
                    return (None,(direction+"cb","make item movable"))
                else:
                    return (None,("K"+direction,"clear next tile"))

            if offset == (-1, 0,0):
                return (None,("a","move to next tile"))
            if offset == ( 1, 0,0):
                return (None,("d","move to next tile"))
            if offset == ( 0,-1,0):
                return (None,("w","move to next tile"))
            if offset == ( 0, 1,0):
                return (None,("s","move to next tile"))

            return (None,None)

        return (None,None)

src.quests.addType(ClearPathToPosition)
