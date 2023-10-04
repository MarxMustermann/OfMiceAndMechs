import random

import src


class WaitQuest(src.quests.Quest):
    type = "WaitQuest"

    def __init__(
        self, followUp=None, startCinematics=None, lifetime=None, creator=None
    ):
        self.description = "wait"
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

This quest will end in {str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)} ticks"""
        return text

    def isPaused(self):
        if not self.completed and self.active:
            return True
        return False

    def getSolvingCommandString(self, character, dryRun=True):
        if self.lifetimeEvent:
            return str(self.lifetimeEvent.tick - src.gamestate.gamestate.tick)+"."
        return "10."

    def solver(self, character):
        commandString = self.getSolvingCommandString(character,dryRun=False)
        self.randomSeed = random.random()

        if commandString:
            character.runCommandString(commandString)
            return False
        return True

src.quests.addType(WaitQuest)
