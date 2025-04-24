from abc import ABC, abstractmethod

import src


class Popup(ABC):
    def __init__(self):
        self.character = None

    @property
    @abstractmethod
    def subscribedEvent(self): ...

    @property
    @abstractmethod
    def text(self): ...

    def conditionMet(self,params) -> bool:
        return True

    def openQuestMenu(self, extraInfo = None):
        extraInfo["character"].macroState["submenue"] = src.menuFolder.questMenu.QuestMenu()

    def onEvent(self,params = None):
        if self.conditionMet(params):
            self.character.delListener(self.onEvent, self.subscribedEvent())

            self.open_Popup(self.character, self.text(), self)

    @staticmethod
    def open_Popup(character, text, container=None):
        submenue = src.menuFolder.textMenu.TextMenu(
            text,
            specialKeys={"q": {"container": container, "method": "openQuestMenu", "params": {"character": character}}},
        )
        submenue.tag = "popup"
        character.macroState["submenue"] = submenue
        character.runCommandString("~", nativeKey=True)

    def addToChar(self, character):
        self.character = character
        character.addListener(self.onEvent, self.subscribedEvent())

popupsArray = []
