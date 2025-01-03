import src


class GoHome(src.quests.MetaQuestSequence):
    type = "GoHome"

    def __init__(self, description="go home", creator=None, paranoid=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.baseDescription = description
        # save initial state and register
        self.type = "GoHome"
        self.addedSubQuests = False
        self.paranoid = paranoid
        self.cityLocation = None
        self.reason = reason

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"

        text = f"""
Go home{reason}.

You consider the command centre of the base your home.
That command centre holds the assimilator and
other important artworks like the quest artwork.

Many activities can be started from the command centre.
Go there and be ready for action.



Quests like this can be pretty boring.
Press c now to use auto move to complete this quest.
Be careful with auto move, while danger is nearby.
Press control-d to stop your character from moving.
"""
        return text

    def triggerCompletionCheck(self, character=None):
        if not character:
            return None
        if not self.cityLocation:
            return None

        if character.getTerrainPosition() == self.terrainLocation and character.getBigPosition() == self.cityLocation:
            self.postHandler()
            return True
        return False

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return
        self.reroll()

        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        self.setHomeLocation(character)

        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")

        super().assignToCharacter(character)

    def setHomeLocation(self,character):
        self.cityLocation = (character.registers["HOMEx"],character.registers["HOMEy"],0)
        self.terrainLocation = (character.registers["HOMETx"],character.registers["HOMETy"],0)
        self.metaDescription = self.baseDescription+f" {self.cityLocation[0]}/{self.cityLocation[1]} on {self.terrainLocation[0]}/{self.terrainLocation[1]}"

    def getNextStep(self, character=None, ignoreCommands=False, dryRun=True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.getBigPosition()[0] == 0:
            return (None, ("d","enter the terrain"))
        if character.getBigPosition()[0] == 14:
            return (None, ("a","enter the terrain"))
        if character.getBigPosition()[1] == 0:
            return (None, ("s","enter the terrain"))
        if character.getBigPosition()[1] == 14:
            return (None, ("w","enter the terrain"))
        
        currentTerrain = character.getTerrain()

        if character.getTerrainPosition() != self.terrainLocation:
            foundShrine = None
            if isinstance(character.container, src.rooms.Room):
                items = character.container.getItemsByType("Shrine")
                if items:
                    for item in items:
                        if character.getDistance(item.getPosition()) <= 1:

                            if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.SelectionMenu.SelectionMenu) and not ignoreCommands:
                                submenue = character.macroState["submenue"]

                                targetIndex = 5

                                offset = targetIndex-submenue.selectionIndex
                                command = ""
                                if offset > 0:
                                    command += "s"*offset
                                else:
                                    command += "w"*(-offset)
                                command += "j"
                                return (None,(command,"teleport home"))

                            direction = "."
                            if character.getPosition(offset=(1, 0, 0)) == item.getPosition():
                                direction = "d"
                            if character.getPosition(offset=(-1, 0, 0)) == item.getPosition():
                                direction = "a"
                            if character.getPosition(offset=(0, 1, 0)) == item.getPosition():
                                direction = "s"
                            if character.getPosition(offset=(0, -1, 0)) == item.getPosition():
                                direction = "w"
                            return (None, ("J" + direction + "wj", "activate the Shrine"))
                    foundShrine = items[0]
                    quest = src.quests.questMap["GoToPosition"](
                        targetPosition=foundShrine.getPosition(), reason="get to a shrine", ignoreEndBlocked=True
                    )
                    return ([quest], None)
                roomsToSearch = character.container.container.rooms
            else:
                roomsToSearch = character.container.rooms

            for room in roomsToSearch:
                items = room.getItemsByType("Shrine")
                if not items:
                    continue
                foundShrine = items[0]

            if foundShrine:
                quest = src.quests.questMap["GoToTile"](
                    paranoid=self.paranoid, targetPosition=foundShrine.container.getPosition(), reason="get to a shrine"
                )
                return ([quest], None)
            else:
                quest = src.quests.questMap["GoToTerrain"](targetTerrain=self.terrainLocation)
                return ([quest], None)

        if character.getBigPosition() != self.cityLocation:
            quest = src.quests.questMap["GoToTile"](
                paranoid=self.paranoid, targetPosition=self.cityLocation, reason="go to the command center"
            )
            return ([quest], None)

        charPos = (character.xPosition % 15, character.yPosition % 15, 0)
        move = ""
        if charPos in ((0, 7, 0), (0, 6, 0)):
            move = "d"
        if charPos in ((7, 14, 0), (6, 12, 0)):
            move = "w"
        if charPos in ((7, 0, 0), (6, 0, 0)):
            move = "s"
        if charPos in ((14, 7, 0), (12, 6, 0)):
            move = "a"
        if move != "":
            return (None, (move, "move into room"))

        return (None, None)

    def getQuestMarkersTile(self, character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.cityLocation[0],self.cityLocation[1]),"target"))
        return result

src.quests.addType(GoHome)
