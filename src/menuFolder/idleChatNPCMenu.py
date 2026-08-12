import src

class IdleChatNPCMenu(src.menues.SubMenu):
    def __init__(self,npc=None):
        self.npc = npc
        self.type = "IdleChatNPCMenu"
        self.subMenu = None
        self.infoType = None
        super().__init__()

    def getTitle(self):
        return "CHAT"

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
                options.append(("showStats","What have you been doing?"))
                options.append(("exchangeItems","Let us exchange items"))
                options.append(("setDutyPriorities","Let us talk about work priorities"))
                options.append(("reset","You are behaving eratically. Get yourself together!"))
                self.subMenu = src.menues.menuMap["SelectionMenu"]("", options)
                self.handleKey("~", noRender=noRender, character=character)
                return False
            self.instructionType = self.subMenu.selection
            self.subMenu = None

        if self.instructionType == "charInfo":
            submenue = src.menues.menuMap["CharacterInfoMenu"](char=self.npc)
            character.add_submenu(submenue)
            self.subMenu = None
            return True
        if self.instructionType == "showQuests":
            submenue = src.menues.menuMap["QuestMenu"](char=self.npc)
            character.add_submenu(submenue)
            self.subMenu = None
            return True
        if self.instructionType == "showStats":
            submenue = src.menues.menuMap["CharacterStatsMenu"](self.npc)
            character.add_submenu(submenue)
            self.subMenu = None
            return True
        if self.instructionType == "exchangeItems":
            submenue = src.menues.menuMap["ItemExchangeMenu"](character,self.npc)
            character.add_submenu(submenue)
            self.subMenu = None
            return True
        if self.instructionType == "showInventory":
            submenue = src.menues.menuMap["InventoryMenu"](char=self.npc)
            character.add_submenu(submenue)
            self.subMenu = None
            return True
        if self.instructionType == "setDutyPriorities":
            submenue = src.menues.menuMap["DutyPriorityConfigurationMenu"](character,self.npc)
            character.add_submenu(submenue)
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

    def render(self,size=None):
        if self.subMenu:
            return self.subMenu.render(size=size)
        return super().render()

# register the menu type
src.menues.add_menu(IdleChatNPCMenu)
