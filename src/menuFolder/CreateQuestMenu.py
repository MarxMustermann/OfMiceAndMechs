import collections

from src.menuFolder.SubMenu import SubMenu

import src
from src.interaction import header, main, urwid, commandChars
from src.menuFolder.SelectionMenu import SelectionMenu

class CreateQuestMenu(SubMenu):
    type = "CreateQuestMenu"

    def __init__(self, questType=None, assignTo=None, activeChar=None):
        self.requiredParams = None
        self.questParams = {}
        self.questType = questType
        self.quest = None
        self.submenu = None
        self.assignTo = assignTo
        super().__init__()
        self.stealAllKeys = False
        self.parameterName = None
        self.parameterValue = None
        self.activeChar = activeChar

    def handleKey(self, key, noRender=False, character = None):
        # exit submenu
        if key == "esc":
            return True

        if not self.quest:
            self.quest = src.quests.questMap[self.questType]()

        if self.submenu:
            if not self.submenu.handleKey(key, noRender=noRender, character=character):
                return False
            param = self.requiredParams.pop()

            rawParameter = self.submenu.text
            if param["type"] == "int":
                self.questParams[param["name"]] = int(rawParameter)
            elif param["type"] == "string":
                self.questParams[param["name"]] = rawParameter
            elif param["type"] == "coordinate":
                if rawParameter == ".":
                    self.questParams[param["name"]] = character.getBigPosition()
                else:
                    self.questParams[param["name"]] = (int(rawParameter.split(",")[0]),int(rawParameter.split(",")[1]),0)
            self.submenu = None

        if self.requiredParams is None:
            self.requiredParams = self.quest.getRequiredParameters()

        if self.requiredParams and not self.submenu:
            param = self.requiredParams[-1]
            description = "set param: "
            if param["type"] == "coordinate":
                description += str(character.getBigPosition())
            self.submenu = src.interaction.InputMenu(f"{description}{param}")
            self.submenu.handleKey("~", noRender=noRender, character=character)
            self.stealAllKeys = True
            return False

        if not self.requiredParams and key == " ":
            for char in self.assignTo:
                if char is None or char.dead:
                    continue

                quest = src.quests.questMap[self.questType]()
                quest.setParameters(self.questParams)
                foundQuest = None
                for targetQuest in char.quests:
                    if targetQuest.type == "Serve":
                        foundQuest = targetQuest
                        break

                if not foundQuest:
                    char.assignQuest(quest,active=True)
                else:
                    foundQuest.addQuest(quest)
                quest.activate()
                quest.assignToCharacter(char)
                if char == self.activeChar:
                    quest.selfAssigned = True
                char.showGotCommand = True
            self.activeChar.showGaveCommand = True
            return True

        self.optionalParams = self.quest.getOptionalParameters()

        if key not in ("enter","~"):
            self.stealAllKeys = True
            if self.parameterName is None:
                self.parameterName = ""

            if self.parameterValue is None:
                if key == ":":
                    self.parameterValue = ""
                elif key == "backspace":
                    if len(self.parameterName):
                        self.parameterName = self.parameterName[:-1]
                else:
                    self.parameterName += key
            else:
                if key == ";":
                    value = None
                    if self.parameterValue == "None":
                        value = None
                    else:
                        value = int(self.parameterValue)

                    self.questParams[self.parameterName] = value
                    self.parameterName = None
                    self.parameterValue = None
                elif key == "backspace":
                    if len(self.parameterValue):
                        self.parameterValue = self.parameterValue[:-1]
                else:
                    self.parameterValue += key

        # start rendering
        if not noRender:
            header.set_text((urwid.AttrSpec("default", "default"), "\ncreate Quest\n"))
            # show rendered text via urwid
            main.set_text((urwid.AttrSpec("default", "default"), "type: {}\n\nparameters: \n\n{}\n\ncurrent parameter: \n\n{} : {}\n\noptional parameters: \n\n{}\n\npress space to confirm".format(self.questType,self.questParams,self.parameterName,self.parameterValue,self.optionalParams)))
        return False
