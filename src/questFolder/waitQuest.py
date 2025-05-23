import random

import src


class WaitQuest(src.quests.MetaQuestSequence):
    type = "WaitQuest"

    def __init__(
        self, followUp=None, startCinematics=None, lifetime=None, creator=None
    ):
        self.metaDescription = "wait"
        super().__init__(lifetime=lifetime, creator=creator)

        # save initial state and register

    """
    do nothing
    """

    def generateTextDescription(self):
        text = """
Wait."""
        if self.lifetimeEvent:
            text += f"""

This quest will end in {self.lifetimeEvent.tick - src.gamestate.gamestate.tick} ticks"""
        return text

    def isPaused(self):
        if not self.completed and self.active:
            return True
        return False

    def triggerCompletionCheck(self, character=None):
        if (self.lifetimeEvent.tick - src.gamestate.gamestate.tick) <= 0:
            self.postHandler()
            return True
        return None

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        self.randomSeed = random.random()
        if self.lifetimeEvent:
            return (None,(str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)+".","wait"))
        return (None,("10.","wait"))

src.quests.addType(WaitQuest)
