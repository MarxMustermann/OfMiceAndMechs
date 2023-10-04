import src


class Assimilate(src.quests.MetaQuestSequence):
    type = "Assimilate"

    def __init__(self, description="integrate into the base",preferedDuty=None):
        super().__init__()
        self.metaDescription = description
        self.preferedDuty = preferedDuty

    def triggerCompletionCheck(self,character=None):
        return False

    def generateTextDescription(self):
        if self.character.rank is None:
            return """
When the base grows or clones are dying, replacement personnel are needed.
The base can create new clones, but they need to be integrated into the bases systems.
Every base should have an assimilator for exactly that purpose.

There is an assimilator in the command centre.
Activate the assimilator to get integrated into the base."""
        else:
            return """
Use the assimilator to get further instructions.
The assimilator is in the command centre.
"""

    def generateSubquests(self,character):
        if not self.active:
            return

        while self.subQuests:
            self.subQuests[-1].triggerCompletionCheck(character)
            if not self.subQuests:
                break
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return

        room = character.container

        if not isinstance(character.container, src.rooms.Room):
            quest = src.quests.questMap["GoHome"](description="go to command centre")
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        for item in room.itemsOnFloor:
            if not item.bolted:
                continue
            if item.type != "Assimilator":
                continue

            if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                return
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                return
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                return
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                return
            quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to assimilator ")
            quest.active = True
            quest.assignToCharacter(character)
            self.addQuest(quest)
            return
        self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(7,7,0),description="go to command centre"))
        return

    def getSolvingCommandString(self,character,dryRun=True):
        if not self.subQuests:
            submenue = character.macroState.get("submenue")
            if submenue:
                if isinstance(submenue,src.interaction.SelectionMenu):
                    if self.preferedDuty:
                        foundDuty = False
                        counter = 0
                        for option in submenue.options.items():
                            counter += 1
                            if option[1].startswith(self.preferedDuty):
                                foundDuty = True
                                break

                        if foundDuty:
                            offset = counter-submenue.selectionIndex
                            if offset > 0:
                                return "s"*offset
                            if offset < 0:
                                return "w"*(-offset)
                    return ["enter"]
                return ["esc"]

            room = character.container

            if not isinstance(character.container, src.rooms.Room):
                return super().getSolvingCommandString(character,dryRun=dryRun)

            for item in room.itemsOnFloor:
                if not item.bolted:
                    continue
                if item.type != "Assimilator":
                    continue

                if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                    return list("Ja")
                if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                    return list("Jd")
                if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                    return list("Jw")
                if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                    return list("Js")

        return super().getSolvingCommandString(character,dryRun=dryRun)

    def solver(self,character):
        if not self.subQuests:
            self.generateSubquests(character)

        if not self.subQuests:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                return

        super().solver(character)

    def handleMovement(self, extraInfo):
        if not self.active:
            return

        self.generateSubquests(extraInfo[0])

    def handleTileChange(self):
        if self.completed:
            1/0

        for quest in self.subQuests:
            quest.postHandler()

        self.subQuests = []

    def handleChangedDuties(self,character=None):
        self.postHandler()

    def assignToCharacter(self, character):
        self.startWatching(character,self.handleMovement, "moved")
        self.startWatching(character,self.handleTileChange, "changedTile")
        self.startWatching(character,self.handleChangedDuties, "changed duties")

        super().assignToCharacter(character)

src.quests.addType(Assimilate)
