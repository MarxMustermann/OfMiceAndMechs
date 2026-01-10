import src

import random

class GoInside(src.quests.MetaQuestSequence):
    '''
    quest to go inside
    '''
    type = "GoInside"
    def __init__(self, description="go inside", creator=None, paranoid=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.baseDescription = description
        # save initial state and register
        self.type = "GoInside"
        self.addedSubQuests = False
        self.paranoid = paranoid
        self.reason = reason

    def generateTextDescription(self):
        '''
        generate a textual description of this quest
        '''
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"

        text = f"""
Go inside{reason}.
"""
        return text

    def triggerCompletionCheck(self, character=None, dryRun=True):
        '''
        check if the quest is completed
        '''
        if not character:
            return False

        if character.container.isRoom:
            if not dryRun:
                self.postHandler()
            return True

        return False

    def wrapedTriggerCompletionCheck(self, extraInfo):
        '''
        indirection to call the actual fuction
        '''
        if not self.active:
            return
        self.reroll()

        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def assignToCharacter(self, character):
        '''
        assign this quest to a character
        '''
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")

        super().assignToCharacter(character)

    def getNextStep(self, character=None, ignoreCommands=False, dryRun=True):
        '''
        get the next step towards solving the quest
        '''

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # navigate menues
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            return (None,(["esc"],"close menu"))

        # enter rooms/tiles properly
        if not character.container.isRoom:
            pos = character.getSpacePosition()
            if pos == (14,7,0):
                return (None,("a","enter room"))
            if pos == (0,7,0):
                return (None,("d","enter room"))
            if pos == (7,14,0):
                return (None,("w","enter room"))
            if pos == (7,0,0):
                return (None,("s","enter room"))
        if character.getBigPosition()[0] == 0:
            return (None, ("d","enter the terrain"))
        if character.getBigPosition()[0] == 14:
            return (None, ("a","enter the terrain"))
        if character.getBigPosition()[1] == 0:
            return (None, ("s","enter the terrain"))
        if character.getBigPosition()[1] == 14:
            return (None, ("w","enter the terrain"))

        # set up helper variables
        currentTerrain = character.getTerrain()

        # workaround missing home rooms
        if not currentTerrain.rooms:
            return self._solver_trigger_fail(dryRun,"no rooms")

        # select room to go to
        target_room = None
        for room in currentTerrain.rooms:
            if room.tag == "entryRoom":
                target_room = room
                break
        if not target_room:
            for room in currentTerrain.rooms:
                if room.tag == "trapRoom":
                    target_room = room
                break
        if not target_room:
            target_room = random.choice(currentTerrain.rooms)

        # make character go into the room
        if character.getBigPosition() != target_room.getPosition():
            quest = src.quests.questMap["GoToTile"](
                paranoid=self.paranoid, targetPosition=target_room.getPosition(), reason="get inside"
            )
            return ([quest], None)

        # enter rooms properly
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

        # soft fail
        return (None, (".","stand around confused"))

    def getQuestMarkersTile(self, character):
        '''
        generate quest markers for this quest
        '''
        result = super().getQuestMarkersTile(character)
        for room in character.getTerrain().rooms:
            result.append((room.getPosition(),"target"))
        return result

    def handleQuestFailure(self,extraParam):
        '''
        handle a subquest failing
        '''

        # set up helper variables
        quest = extraParam.get("quest")
        reason = extraParam.get("reason")

        if reason:
            if reason == "no tile path":
                self.fail(reason)
                return

        super().handleQuestFailure(extraParam)

# register the quest type
src.quests.addType(GoInside)
