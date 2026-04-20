import random

import src


class WaitQuest(src.quests.MetaQuestSequence):
    type = "WaitQuest"

    def __init__(self, description="wait", followUp=None, startCinematics=None, lifetime=None, creator=None, reason=None, batchWait=False):
        super().__init__(lifetime=lifetime, creator=creator)
        self.metaDescription = description
        self.reason = reason
        self.batchWait = batchWait

    """
    do nothing
    """

    def generateTextDescription(self):
        reason_string = ""
        if self.reason:
            reason_string = f", to {self.reason}"

        text = ["""
Wait{reason_string}.

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"default"),"""You can wait by pressing "." to wait for one tick or by pressing ";" to wait 100 ticks""")]
        if self.lifetimeEvent:
            text.append(f"""

This quest will end in {self.lifetimeEvent.tick - src.gamestate.gamestate.tick} ticks""")
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
        wait_time = 10
        if self.lifetimeEvent:
            wait_time = min(self.lifetimeEvent.tick - src.gamestate.gamestate.tick,10)
        if self.batchWait:
            return (None,(";","wait"))
        return (None,("."*wait_time,"wait"))

src.quests.addType(WaitQuest)
