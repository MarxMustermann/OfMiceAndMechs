import random

import src

class ConsumePotion(src.quests.MetaQuestSequence):
    type = "ConsumePotion"

    def __init__(self, description="consume potion", creator=None, potionType=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

        self.potionType = potionType
        self.type = "ConsumePotion"

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Cosume a potion of the type {self.potionType} from your inventory{reason}.
"""
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if character.searchInventory(self.potionType):
            return False
        self.postHandler()
        return True

    def droppedItem(self, extraInfo):
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.droppedItem, "dropped")

        super().assignToCharacter(character)

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and not ignoreCommands:
            if not isinstance(character.macroState["submenue"],src.menuFolder.inventoryMenu.InventoryMenu):
                return (None,(["esc"],"close the menu"))

            counter = 0
            for item in character.inventory:
                if item.type == self.potionType:
                    break
                counter += 1

            offset = counter-character.macroState["submenue"].cursor

            return (None,("s"*offset+"w"*(-offset)+"j","drink the potion"))
        return (None,("i","open inventory"))

src.quests.addType(ConsumePotion)
