import src

class EnterRoom(src.quests.MetaQuestSequence):
    '''
    enter a room fully
    '''
    type = "EnterRoom"
    lowLevel = True
    def __init__(self, description="enter room", creator=None, command=None, lifetime=None):
        super().__init__([], creator=creator, lifetime=lifetime)
        self.metaDescription = description

    def generateTextDescription(self):
        '''
        generate a text description for the quest
        '''
        return """
Enter the room.

This quest is a workaround quest.
This means it is needed for other quests to work,
but has no purpose on its own.

So just complete the quest and don't think about it too much."""

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        never complete
        '''
        return False

    def enteredRoom(self,character=None):
        '''
        end quest when entering a room
        '''
        self.postHandler()

    def getNextStep(self, character=None, ignoreCommands=False, dryRun = True): 
        '''
        get next step towards solving the quest
        '''

        # enter the room
        if character.xPosition%15 == 0:
            return (None,("d","enter room"))
        if character.xPosition%15 == 14:
            return (None,("a","enter room"))
        if character.yPosition%15 == 0:
            return (None,("s","enter room"))
        if character.yPosition%15 == 14:
            return (None,("w","enter room"))
        
        # fail
        if not dryRun:
            self.fail("unexpected position")
        return (None,("+","abort quest"))

    def assignToCharacter(self, character):
        '''
        make character listen to events
        '''
        if self.character:
            return
        self.startWatching(character,self.enteredRoom, "entered room")
        super().assignToCharacter(character)

# register quest type
src.quests.addType(EnterRoom)
