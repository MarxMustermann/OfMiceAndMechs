import src


class PlaceItem(src.quests.MetaQuestSequence):
    type = "PlaceItem"

    def __init__(self, description="place item", creator=None, lifetime=None, targetPosition=None, targetPositionBig=None, itemType=None, tryHard=False, boltDown=False,reason=None, clearPath = False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = f"{description} {itemType} on position {targetPosition} on tile {targetPositionBig}"
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType
        self.tryHard = tryHard
        self.boltDown = boltDown
        self.reason = reason
        self.clearPath = clearPath
    
    def handleQuestFailure(self,extraInfo):
        if extraInfo["reason"] == "no path found":
            if self.tryHard or self.clearPath:
                newQuest = src.quests.questMap["ClearPathToPosition"](targetPosition=self.targetPosition)
                self.addQuest(newQuest)
                self.startWatching(newQuest,self.handleQuestFailure,"failed")
                return
            room = None
            if self.targetPositionBig:
                rooms = self.character.getTerrain().getRoomByPosition(self.targetPositionBig)
                if rooms:
                    room = rooms[0]
            else:
                if self.character.container.isRoom:
                    room = self.character.container
            if room:
                for buildSite in room.buildSites[:]:
                    if buildSite[0] == self.targetPosition:
                        room.buildSites.remove(buildSite)
        self.fail(extraInfo["reason"])

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Place item {self.itemType} on position {self.targetPosition} on tile {self.targetPositionBig}{reason}."""
        if self.boltDown:
            text += """

Bolt down the item after placing it."""

        if not self.character.inventory or self.character.inventory[-1].type != self.itemType:
            text += f"""

You do not have a {self.itemType} in your inventory."""
        else:
            text += f"""

You have a {self.itemType} in your inventory."""

        if self.character.getBigPosition() == self.targetPositionBig:
            text += """

You are on the target tile.
"""
        else:
            direction = ""
            diffXBig = self.targetPositionBig[0] - self.character.getBigPosition()[0]
            if diffXBig < 0:
                direction += f" and {-diffXBig} tiles to the west"
            if diffXBig > 0:
                direction += f" and {diffXBig} tiles to the east"
            diffYBig = self.targetPositionBig[1] - self.character.getBigPosition()[1]
            if diffYBig < 0:
                direction += f" and {-diffYBig} tiles to the north"
            if diffYBig > 0:
                direction += f" and {diffYBig} tiles to the south"
            text += f"""

The target tile is {direction[5:]}
"""

        if self.tryHard:
            text += """

Try as hard as you can to achieve this.
If you don't find the items to place, produce them.
"""
        out = [text]
        if not self.subQuests:
            out.append((src.interaction.urwid.AttrSpec("#f00", "black"),"""
This quest has no subquests. Press r to generate subquests for this quest."""))
        else:
            out.append((src.interaction.urwid.AttrSpec("#080", "black"),"""
This quests has subquests.
Press d to move the cursor and show the subquests description.
"""))

        return out

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.droppedItem, "dropped")
        self.startWatching(character, self.producedItem, "producedItem")
        self.startWatching(character, self.boltedItem, "boltedItem")
        super().assignToCharacter(character)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.targetPositionBig[0],self.targetPositionBig[1]),"target"))
        return result

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if renderForTile:
            result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            if character.getBigPosition() == self.targetPositionBig:
                result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

    def producedItem(self,extraInfo):
        item = extraInfo["item"]
        self.checkPlacedItem(item)

    def droppedItem(self,extraInfo):
        item = extraInfo[1]
        self.checkPlacedItem(item)

    def boltedItem(self,extraInfo):
        item = extraInfo["item"]
        self.checkPlacedItem(item)

    def checkPlacedItem(self,item):
        if item.type == self.itemType:
            if item.container.isRoom:
                if item.container.getPosition() == self.targetPositionBig and item.getPosition() == self.targetPosition:
                    if not self.boltDown or item.bolted:
                        self.postHandler()
            else:
                if item.getPosition() == (self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15,0):
                    if not self.boltDown or item.bolted:
                        self.postHandler()

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if not self.subQuests:
            if not self.tryHard and character.getNearbyEnemies():
                quest = src.quests.questMap["Fight"]()
                return ([quest],None)

            if not ignoreCommands:
                submenue = character.macroState.get("submenue")
                if submenue:
                    return (None,(["esc"],"exit the menu"))

            if character.getBigPosition() != self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,description="go to buildsite",reason=f"be able to place the {self.itemType}")
                return ([quest],None)

            itemFound = None
            itemPlaced = None
            if self.boltDown:
                if self.targetPositionBig:
                    terrain = character.getTerrain()
                    rooms = terrain.getRoomByPosition(self.targetPositionBig)
                    if rooms:
                        container = rooms[0]
                    else:
                        container = terrain
                else:
                    container = character.container

                if character.container.isRoom:
                    items = character.container.getItemByPosition((self.targetPosition[0],self.targetPosition[1],0))
                else:
                    items = character.container.getItemByPosition((self.targetPositionBig[0]*15+self.targetPosition[0],self.targetPositionBig[1]*15+self.targetPosition[1],0))

                if items and items[-1].type == self.itemType:
                    itemFound = items[-1]
                    itemPlaced = items[-1]

            if not itemPlaced:
                itemFound = None
                itemIndex = 0
                for item in reversed(character.inventory):
                    itemIndex += 1
                    if item.type == self.itemType:
                        itemFound = item
                        break

                if not itemFound:
                    quest = src.quests.questMap["FetchItems"](toCollect=self.itemType,amount=1,takeAnyUnbolted=self.tryHard,tryHard=self.tryHard,reason="have an item to place")
                    return ([quest],None)

                if character.getBigPosition() != self.targetPositionBig:
                    quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,description="go to buildsite",reason=f"be able to place the {self.itemType}")
                    return ([quest],None)

                if not itemFound.walkable:
                    if character.container.isRoom:
                        items = character.container.getItemByPosition((self.targetPosition[0],self.targetPosition[1],0))
                    else:
                        items = character.container.getItemByPosition((self.targetPositionBig[0]*15+self.targetPosition[0],self.targetPositionBig[1]*15+self.targetPosition[1],0))
                    if items and items[-1].type != self.itemType:
                        quest = src.quests.questMap["CleanSpace"](targetPosition=self.targetPosition,targetPositionBig=self.targetPositionBig,pickUpBolted=True)
                        return ([quest],None)

                if character.getSpacePosition() != self.targetPosition:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,description="go to placement spot",reason=f"be able to place the {self.itemType}")
                    return ([quest],None)

                if not itemPlaced:
                    if itemIndex > 1:
                        dropCommand = "il"+itemIndex*"w"+"j"
                    else:
                        dropCommand = "l"

                    return (None,(dropCommand,"drop the item"))

            if self.targetPositionBig and self.targetPositionBig != character.getBigPosition():
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,description="go to buildsite",reason=f"be able to place the {self.itemType}")
                return ([quest],None)

            if character.getDistance(itemPlaced.getPosition()) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,description="go to placement spot",reason=f"be able to place the {self.itemType}",ignoreEndBlocked=True)
                return ([quest],None)

            pos = character.getPosition()
            targetPosition = itemPlaced.getPosition()
            if (pos[0],pos[1],pos[2]) == targetPosition:
                return (None,("cb","bolt down item"))
            if (pos[0]-1,pos[1],pos[2]) == targetPosition:
                return (None,("acb","bolt down item"))
            if (pos[0]+1,pos[1],pos[2]) == targetPosition:
                return (None,("dcb","bolt down item"))
            if (pos[0],pos[1]-1,pos[2]) == targetPosition:
                return (None,("wcb","bolt sown item"))
            if (pos[0],pos[1]+1,pos[2]) == targetPosition:
                return (None,("scb","bolt down item"))

            67/0
        return (None,None)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
        if not rooms:
            items = character.getTerrain().getItemByPosition((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15,0))
        else:
            items = rooms[0].getItemByPosition(self.targetPosition)

        if not items:
            return False

        if items[-1].type == self.itemType and (not self.boltDown or items[-1].bolted):
            self.postHandler()
            return True
        return False

src.quests.addType(PlaceItem)
