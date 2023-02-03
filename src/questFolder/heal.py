import src

class Heal(src.quests.MetaQuestSequence):
    type = "Heal"

    def __init__(self, description="heal"):
        super().__init__()
        self.metaDescription = description

    def generateTextDescription(self):
        text = """
You are hurt. Heal yourself.

You can heal yourself using vials.
Use vials to heal yourself.

Press JH to auto heal.
"""
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        foundVial = None
        for item in character.inventory:
            if item.type == "Vial" and item.uses > 0:
                foundVial = item

        if not foundVial:
            self.postHandler()
            return True

        if character.health < character.maxHealth:
            return False

        self.postHandler()
        return True

    def getSolvingCommandString(self,character,dryRun=True):
        if not dryRun:
            self.triggerCompletionCheck(character)
        return "JH"

    def solver(self,character):
        command = self.getSolvingCommandString(character,dryRun=False)
        if command:
            character.runCommandString(command)
            return
        if self.triggerCompletionCheck(character):
            return
        return super().solver(character)
    
src.quests.addType(Heal)
