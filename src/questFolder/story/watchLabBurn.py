import src


class WatchLabBurn(src.quests.MetaQuestSequence):
    type = "WatchLabBurn"

    def __init__(self, description="watch lab burn", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.explosion_tick = None

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:
            return (None,(["esc",],"close the menu"))

        if not self._get_lab():
            if not self.explosion_tick:
                self.explosion_tick = src.gamestate.gamestate.tick
            if src.gamestate.gamestate.tick > self.explosion_tick:
                if not dryRun:
                    self.postHandler()
                return (None,("+","end quest"))
            return (None,(".","stop watching the explosion"))

        if character.getSpacePosition()[1] > 11:
            return (None,("w","distance yourself from the lab"))
        lab = self._get_lab()
        sterns_contraption = lab.getItemByType("MainContraption")
        num_wait = 1
        if sterns_contraption:
            num_wait = 8-sterns_contraption.meltdownLevel-1
        return (None,("."*num_wait,"watch the lab burn"))

    def generateTextDescription(self):
        door = src.items.itemMap["Door"]()
        door.open = True
        door.walkable = False
        door.blocked = False

        text = []
        text.extend(["""
You reach out to your implant and it answers:


This room is exploding! We need to leave fast.

Look for the door first then move.

Instructions to do that will be shown on the left of the screen as "suggested action"

"""])
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        self.startWatching(character,self.lookedAt, "lookedAt")
        super().assignToCharacter(character)

    def lookedAt(self, extraInfo):
        if extraInfo["index"] == (6,0,0) and extraInfo["index_big"] == (6,10,0):
            if not self.lookedAtDoor:
                self.lookedAtDoor = True
                self.character.addMessage("You found the Door. Close the menu now")

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def _get_lab(self):
        for room in self.character.getTerrain().rooms:
            if room.tag == "the architects lab":
                return room
        return None

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if not self._get_lab():
            if not self.explosion_tick:
                self.explosion_tick = src.gamestate.gamestate.tick
            if src.gamestate.gamestate.tick > self.explosion_tick:
                if not dryRun:
                    self.postHandler()
                return True
        return False

src.quests.addType(WatchLabBurn)
