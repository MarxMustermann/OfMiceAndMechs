import random

import src


class WaitQuest(src.quests.MetaQuestSequence):
    type = "WaitQuest"

    def __init__(self, description="wait", followUp=None, startCinematics=None, lifetime=None, creator=None, reason=None):
        super().__init__(lifetime=lifetime, creator=creator)
        self.metaDescription = description
        self.reson = reason

        # save initial state and register

    """
    do nothing
    """

    def generateTextDescription(self):
        reason_string = ""
        if self.reason:
            reason_string = f", to {self.reason}"

        text = f"""
Wait{reason_string}."""
        if self.lifetimeEvent:
            text += f"""

This quest will end in {self.lifetimeEvent.tick - src.gamestate.gamestate.tick} ticks"""
        return text

    def isPaused(self):
        if not self.completed and self.active:
            return True
        return False

    def triggerCompletionCheck(self, character=None, dryRun=True):
        if (self.lifetimeEvent.tick - src.gamestate.gamestate.tick) <= 0:
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        self.randomSeed = random.random()
        if self.lifetimeEvent:
            return (None,(str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)+".","wait"))
        return (None,("10.","wait"))

src.quests.addType(WaitQuest)
