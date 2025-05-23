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
        if pos[0] == self.targetPosition[0] and pos[1] == self.targetPosition[1]:
            self.postHandler()
            return True
        return None

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if not self.subQuests:
            path = self.path

            if not path:
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

                if not dryRun:
                    self.path = path

            if not path:
                return (None,None)

            path = path[:]

            x = character.xPosition%15
            y = character.yPosition%15

            if path[0] == (x,y,0):
                path.remove((x,y,0))
                if not dryRun:
                    self.path = path

            offset = None
            if path:
                if (x-1,y  ,0) == path[0]:
                    offset = (-1, 0,0)
                if (x+1,y  ,0) == path[0]:
                    offset = ( 1, 0,0)
                if (x  ,y-1,0) == path[0]:
                    offset = ( 0,-1,0)
                if (x  ,y+1,0) == path[0]:
                    offset = ( 0, 1,0)

            if not offset:
                if not dryRun:
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

                    if character.inventory[-1].walkable:
                        return (None,("L"+random.choice(directions),"drop item"))

                    counter = 0
                    for item in character.inventory:
                        if item.walkable:
                            break
                        counter += 1
                    return (None,("i"+"s"*counter+"L"+random.choice(directions),"drop item"))

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
                    return (None,("K"+direction,"clear next spot"))

            if offset == (-1, 0,0):
                return (None,("a","move to next spot"))
            if offset == ( 1, 0,0):
                return (None,("d","move to next spot"))
            if offset == ( 0,-1,0):
                return (None,("w","move to next spot"))
            if offset == ( 0, 1,0):
                return (None,("s","move to next spot"))

            return (None,None)

        return (None,None)

    def handleChangedTile(self, extraInfo = None):
        self.fail("left terrain")

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleChangedTile, "changedTile")

        super().assignToCharacter(character)

src.quests.addType(ClearPathToPosition)
