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

        if character.getTerrainPosition() == self.getHomeLocation() and character.getBigPosition() == self.getCityLocation():
            self.postHandler()
            return True
        return False

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return
        self.reroll()

        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.recalcDescription()

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")

        super().assignToCharacter(character)

    def getCityLocation(self):
        return (self.character.registers["HOMEx"],self.character.registers["HOMEy"],0)

    def getHomeLocation(self):
        return (self.character.registers["HOMETx"],self.character.registers["HOMETy"],0)

    def recalcDescription(self):
        if self.character:
            cityLocation = self.getCityLocation()
            terrainLocation = self.getHomeLocation()
            self.metaDescription = self.baseDescription+f" {cityLocation[0]}/{cityLocation[1]} on {terrainLocation[0]}/{terrainLocation[1]}"

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

        if character.getTerrainPosition() != self.getHomeLocation():
            foundShrine = None
            if isinstance(character.container, src.rooms.Room):
                items = character.container.getItemsByType("Shrine")
                if items:
                    for item in items:
                        if character.getDistance(item.getPosition()) <= 1:

                            if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.selectionMenu.SelectionMenu) and not ignoreCommands:
                                submenue = character.macroState["submenue"]

                                targetIndex = None
                                counter = 0
                                for item in submenue.options.values():
                                    counter += 1
                                    if item == "teleport":
                                        targetIndex = counter
                                        break
                                if not targetIndex:
                                    return (None,(["esc"],"close menu"))

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

                            interactionCommand = "J"
                            if "advancedInteraction" in character.interactionState:
                                interactionCommand = ""
                            return (None, (interactionCommand + direction + "sssj", "activate the Shrine"))
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
                quest = src.quests.questMap["GoToTerrain"](targetTerrain=self.getHomeLocation())
                return ([quest], None)

        if character.getBigPosition() != self.getCityLocation():
            quest = src.quests.questMap["GoToTile"](
                paranoid=self.paranoid, targetPosition=self.getCityLocation(), reason="go to the command center"
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
        result.append(((self.getCityLocation()[0],self.getCityLocation()[1]),"target"))
        return result

src.quests.addType(GoHome)
