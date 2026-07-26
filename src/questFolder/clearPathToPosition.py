import random

import src


class ClearPathToPosition(src.quests.MetaQuestSequence):
    type = "ClearPathToPosition"
    lowLevel = True

    def __init__(self, description="clear path to position", creator=None, targetPosition=None, tryHard=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+f" {targetPosition}"
        self.targetPosition = targetPosition
        self.tryHard = tryHard
        self.reason = reason
        self.path = None
        self.startTime = None

    def generateTextDescription(self):
        reason = (src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),".")
        if self.reason:
            reason = [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),f","),f"\nto {self.reason}."]
        text = [f"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),f"Clear path to position {self.targetPosition}"),reason,f"""

Pick up and unbolt items that are in the way.

""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"""
Clear the path by picking item up by using the k and K keys.
Drop items by using the l and L keys if your inventory has no space.
Unbolt items by using a complex action, if needed.
""")]

        return text

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return None

        pos = character.getPosition()
        pos = (pos[0]%15,pos[1]%15,pos[2]%15)
        if pos[0] == self.targetPosition[0] and pos[1] == self.targetPosition[1]:
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        try:
            self.startTime
        except:
            self.startTime = None
        if not self.startTime:
            if not dryRun:
                self.startTime = src.gamestate.gamestate.tick
            return (None,("+","remember the start time"))

        submenue = character.macroState.get("submenue")
        if submenue:
            if isinstance(submenue,src.menues.menuMap["InventoryMenu"]) and not character.getFreeInventorySpace():
                return (None,("X","destroy item"))
            return (None,(["esc"],"close the menu"))

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
            return self._solver_trigger_fail(dryRun,"no path")

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
            return (None,(".","stand around confused"))

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

                if (src.gamestate.gamestate.tick - self.startTime) > 100:
                    return (None,("iX","destroy item"))
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

        return (None,(".","stand around confused"))

    def handleChangedTile(self, extraInfo = None):
        if not self.active:
            return
        if not self.character:
            return
        if self.completed:
            1/0

        self.fail("left terrain")

    def handleMoved(self, extraInfo):
        if not self.active:
            return
        if not self.character:
            return
        if self.completed:
            1/0

        x = self.character.xPosition%15
        y = self.character.yPosition%15

        if self.path and self.path[0] == (x,y,0):
            self.path.remove((x,y,0))
        else:
            self.path = []

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleChangedTile, "changedTile")
        self.startWatching(character,self.handleMoved, "moved")

        super().assignToCharacter(character)

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        return the quest markers for the normal map
        Parameters:
            character:      the character doing the quest
            renderForTile:  whether or not to show the markers for a room or a tile
        Returns:
            the quest markers to show
        '''

        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if self.path:
            for pos in self.path:
                result.append((pos,"path"))

                if not character.container.isRoom:
                    result.append(((pos[0]+character.getBigPosition()[0]*15,pos[1]%15+character.getBigPosition()[1]*15,0),"path"))
                else:
                    result.append((pos,"path"))
        return result

src.quests.addType(ClearPathToPosition)
