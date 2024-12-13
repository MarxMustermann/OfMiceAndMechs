import src

class IdleChatNPCMenu(src.SubMenu.SubMenu):
    def __init__(self,npc=None):
        self.npc = npc
        self.type = "IdleChatNPCMenu"
        self.subMenu = None
        self.infoType = None
        super().__init__()

    def handleKey(self, key, noRender=False, character = None):
        if self.subMenu:
            subMenuDone = self.subMenu.handleKey(key, noRender=noRender, character=character)
            if not subMenuDone:
                return False
            key = "~"

        # exit the submenu
        if key == "esc":
            return True

        if not self.infoType:
            if not self.subMenu:
                options = []
                options.append(("charInfo","Tell me about yourself."))
                options.append(("showQuests","What are you doing?"))
                options.append(("showInventory","What is in your inventory?"))
                options.append(("showFeelings","How are you feeling?"))
                options.append(("reset","You are behaving eratically. Get yourself together!"))
                self.subMenu = src.menuFolder.SelectionMenu.SelectionMenu("", options)
                self.handleKey("~", noRender=noRender, character=character)
                return False
            self.instructionType = self.subMenu.selection
            self.subMenu = None

        if self.instructionType == "charInfo":
            submenue = src.menuFolder.CharacterInfoMenu.CharacterInfoMenu(char=self.npc)
            character.macroState["submenue"] = submenue
            submenue.handleKey("~", noRender=noRender,character=character)
            self.subMenu = None
            return True
        if self.instructionType == "showQuests":
            submenue = src.menuFolder.QuestMenu.QuestMenu(char=self.npc)
            character.macroState["submenue"] = submenue
            submenue.handleKey("~", noRender=noRender,character=character)
            self.subMenu = None
            return True
        if self.instructionType == "showInventory":
            submenue = src.menuFolder.InventoryMenu.InventoryMenu(char=self.npc)
            character.macroState["submenue"] = submenue
            submenue.handleKey("~", noRender=noRender,character=character)
            self.subMenu = None
            return True
        if self.instructionType == "showFeelings":
            submenue = src.menuFolder.InventoryMenu.InventoryMenu(char=self.npc)
            character.macroState["submenue"] = submenue
            submenue.handleKey("~", noRender=noRender,character=character)
            self.subMenu = None
            return True
        if self.instructionType == "reset":
            for quest in self.npc.quests:
                quest.fail()

            containerQuest = src.quests.questMap["BeUsefull"]()
            self.npc.quests.append(containerQuest)
            containerQuest.assignToCharacter(self.npc)
            containerQuest.activate()
            containerQuest.autoSolve = True

            self.npc.timeTaken = 0
        return True
