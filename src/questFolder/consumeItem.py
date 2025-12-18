import random

import src

class ConsumeItem(src.quests.MetaQuestSequence):
    type = "ConsumeItem"
    lowLevel = True

    def __init__(self, description="consume item", creator=None, itemType=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

        self.itemType = itemType
        self.type = "ConsumeItem"

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Cosume an item of the type {self.itemType} from your inventory{reason}.
"""
        return text

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if character.searchInventory(self.itemType):
            return False

        if not dryRun:
            self.postHandler()
        return True

    def droppedItem(self, extraInfo):
        self.triggerCompletionCheck(self.character,dryRun=False)

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
                if item.type == self.itemType:
                    break
                counter += 1

            offset = counter-character.macroState["submenue"].cursor

            return (None,("s"*offset+"w"*(-offset)+"j","consume the item"))
        return (None,("i","open inventory"))

src.quests.addType(ConsumeItem)
