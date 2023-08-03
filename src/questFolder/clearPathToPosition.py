import src
import random

class ClearPathToPosition(src.quests.MetaQuestSequence):
    type = "ClearPathToPosition"

    def __init__(self, description="clear path to position", creator=None, targetPosition=None, tryHard=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.tryHard = tryHard
        self.reason = reason
        self.path = None

    def triggerCompletionCheck(self,character=None):
        if not character:
            return
        
        pos = character.getPosition()
        pos = (pos[0]%15,pos[1]%15,pos[2]%15)
        if pos == self.targetPosition:
            self.postHandler()
            return True

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
                totalOffset = (0,0,0)
                x = character.xPosition%15
                y = character.yPosition%15

                path = []
                while not (x,y,0) == self.targetPosition:
                    offsets = []
                    if x < self.targetPosition[0]:
                        if character.container.getPositionWalkable(character.getPosition(offset=(totalOffset[0]+1,totalOffset[1],0))):
                            offsets.append(( 1, 0,0))
                    if x > self.targetPosition[0]:
                        if character.container.getPositionWalkable(character.getPosition(offset=(totalOffset[0]-1,totalOffset[1],0))):
                            offsets.append((-1, 0,0))
                    if y < self.targetPosition[1]:
                        if character.container.getPositionWalkable(character.getPosition(offset=(totalOffset[0],totalOffset[1]+1,0))):
                            offsets.append(( 0, 1,0))
                    if y > self.targetPosition[1]:
                        if character.container.getPositionWalkable(character.getPosition(offset=(totalOffset[0],totalOffset[1]-1,0))):
                            offsets.append(( 0,-1,0))

                    if not offsets:
                        if x < self.targetPosition[0]:
                            offsets.append(( 1, 0,0))
                        if x > self.targetPosition[0]:
                            offsets.append((-1, 0,0))
                        if y < self.targetPosition[1]:
                            offsets.append(( 0, 1,0))
                        if y > self.targetPosition[1]:
                            offsets.append(( 0,-1,0))

                    offset = random.choice(offsets)
                    totalOffset = (totalOffset[0]+offset[0],totalOffset[1]+offset[1],0)

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
                    return (None,("l","drop item"))

                if offset == (-1, 0,0):
                    return (None,("Ka","clear next tile"))
                if offset == ( 1, 0,0):
                    return (None,("Kd","clear next tile"))
                if offset == ( 0,-1,0):
                    return (None,("Kw","clear next tile"))
                if offset == ( 0, 1,0):
                    return (None,("Ks","clear next tile"))

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
