import src

class InstructSubordinatesMenu(src.SubMenu.SubMenu):
    def __init__(self,npcs=None):
        self.type = "InstructSubordinatesMenu"
        self.subMenu = None
        self.instructionType = None
        self.dutyType = None
        self.commandType = None
        self.addFront = True
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

        if not self.instructionType:
            if not self.subMenu:
                options = []
                options.append(("command selection","select from a list of commands"))
                options.append(("createQuest","create and issue quest"))
                self.subMenu = src.menuFolder.SelectionMenu.SelectionMenu("how do you want to give the instruction?", options)
                self.handleKey("~", noRender=noRender, character=character)
                return False
            self.instructionType = self.subMenu.selection
            self.subMenu = None

        if self.instructionType == "createQuest":
            submenue = src.menuFolder.AdvancedQuestMenu.AdvancedQuestMenu()
            submenue.activeChar = character
            submenue.character = self.npc
            submenue.state = "questSelection"
            character.macroState["submenue"] = submenue
            submenue.handleKey("~", noRender=noRender)
        if self.instructionType == "command selection":
            if not self.commandType:
                if not self.subMenu:
                    options = []
                    options.append(("defendTile","defend tile"))
                    options.append(("attackNorth","attack north"))
                    options.append(("attackWest","attack west"))
                    options.append(("attackEast","attack east"))
                    options.append(("attackSouth","attack south"))
                    options.append(("scavengeTile","scavenge tile"))
                    options.append(("clearInventory","clear inventory"))
                    options.append(("equip","equip"))
                    options.append(("abortLast","abort last command"))
                    options.append(("stop","stop what you are doing"))
                    options.append(("continue","continue working"))
                    options.append(("wait","wait until further command"))
                    options.append(("dropAll","drop all your items"))
                    options.append(("goToMyPosition","go to my position"))
                    options.append(("beUseful","be useful"))
                    options.append(("beUsefulHere","be useful here"))
                    options.append(("doDuty","do duty"))
                    options.append(("doDutyHere","do duty here"))
                    self.subMenu = src.menuFolder.SelectionMenu.SelectionMenu("what command do you want to give?", options)
                    self.handleKey("~", noRender=noRender, character=character)
                    return False

                if self.subMenu.origKey == "k":
                    self.addFront = False

                self.commandType = self.subMenu.selection
                self.subMenu = None

            if self.commandType== "stop":
                self.npc.runCommandString("",clear=True)
                self.npc.macroState["loop"] = []
                self.npc.macroState["replay"].clear()
                if "ifCondition" in self.npc.interactionState:
                    self.npc.interactionState["ifCondition"].clear()
                    self.npc.interactionState["ifParam1"].clear()
                    self.npc.interactionState["ifParam2"].clear()
                for quest in self.npc.quests[:]:
                    quest.fail()
                return True
            if self.commandType== "continue":
                self.npc.runCommandString("*",clear=True)
                return True
            if self.commandType == "beUseful":
                for npc in character.subordinates:
                    quest = src.quests.questMap["BeUsefull"]()
                    quest.autoSolve = True
                    npc.assignQuest(quest,active=self.addFront)
                self.subMenu = None
                return True
            if self.commandType == "dropAll":
                self.npc.runCommandString("10l")
                return True
            if self.commandType == "beUsefulHere":
                quest = src.quests.questMap["BeUsefull"](targetPosition=character.getBigPosition())
                quest.autoSolve = True
                self.subMenu = None
                self.npc.assignQuest(quest,active=True)
                return True
            if self.commandType == "goToMyPosition":
                quest = src.quests.questMap["GoToPosition"](targetPosition=character.getSpacePosition())
                quest.autoSolve = True
                self.subMenu = None
                self.npc.assignQuest(quest,active=True)

                if character.container != self.npc.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=character.getBigPosition())
                    quest.autoSolve = True
                    self.subMenu = None
                    self.npc.assignQuest(quest,active=True)
                return True
            if self.commandType in ("defendTile",):
                pos = character.getBigPosition()
                for npc in character.subordinates:
                    quest = src.quests.questMap["SecureTile"](toSecure=pos,endWhenCleared=False)
                    quest.autoSolve = True
                    npc.assignQuest(quest,active=self.addFront)
                self.subMenu = None

            if self.commandType in ("abortLast",):
                for npc in character.subordinates:
                    if npc.quests:
                        npc.quests[0].fail()
                self.subMenu = None

            if self.commandType in ("attackWest","attackEast","attackNorth","attackSouth"):
                pos = character.getBigPosition()
                if self.commandType == "attackWest":
                    pos = (pos[0]-1,pos[1],0)
                if self.commandType == "attackEast":
                    pos = (pos[0]+1,pos[1],0)
                if self.commandType == "attackNorth":
                    pos = (pos[0],pos[1]-1,0)
                if self.commandType == "attackSouth":
                    pos = (pos[0],pos[1]+1,0)

                for npc in character.subordinates:
                    quest = src.quests.questMap["SecureTile"](toSecure=pos,endWhenCleared=True)
                    quest.autoSolve = True
                    npc.assignQuest(quest,active=self.addFront)

                self.subMenu = None
            if self.commandType in ("scavengeTile",):
                pos = character.getBigPosition()

                for npc in character.subordinates:
                    quest = src.quests.questMap["ScavengeTile"](targetPosition=pos)
                    quest.autoSolve = True
                    npc.assignQuest(quest,active=self.addFront)

                self.subMenu = None
            if self.commandType in ("equip",):
                pos = character.getBigPosition()

                for npc in character.subordinates:
                    quest = src.quests.questMap["Equip"]()
                    quest.autoSolve = True
                    npc.assignQuest(quest,active=True)

                self.subMenu = None
            if self.commandType in ("clearInventory",):
                pos = character.getBigPosition()

                for npc in character.subordinates:
                    quest = src.quests.questMap["ClearInventory"]()
                    quest.autoSolve = True
                    npc.assignQuest(quest,active=True)

                self.subMenu = None
            if self.commandType in ("doDutyHere","doDuty"):
                if not self.dutyType:
                    if not self.subMenu:
                        options = []
                        options.append(("resource gathering","resource gathering"))
                        options.append(("machine operation","machine operation"))
                        options.append(("manufacturing","manufacturing"))
                        options.append(("trap setting","trap setting"))
                        options.append(("hauling","hauling"))
                        options.append(("resource fetching","resource fetching"))
                        options.append(("cleaning","cleaning"))
                        options.append(("machine placing","machine placing"))
                        self.subMenu = src.menuFolder.SelectionMenu.SelectionMenu("What duty should be done?", options)
                        self.handleKey("~", noRender=noRender, character=character)
                        return False
                    self.dutyType = self.subMenu.selection
                    self.subMenu = None

                if self.dutyType:
                    self.npc.duties = [self.dutyType]
                    pos = None
                    if self.commandType == "doDutyHere":
                        pos = character.getBigPosition()
                    quest = src.quests.questMap["BeUsefull"](targetPosition=pos,strict=True)
                    quest.autoSolve = True
                    self.subMenu = None
                    self.npc.assignQuest(quest,active=True)
                    return True
        return True
