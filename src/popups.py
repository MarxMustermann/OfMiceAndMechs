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

    def onEvent(self,params = None):
        if self.conditionMet(params):
            self.character.delListener(self.onEvent, self.subscribedEvent())

            submenue = src.menuFolder.textMenu.TextMenu(self.text())
            submenue.tag = "popup"
            self.character.macroState["submenue"] = submenue
            self.character.runCommandString("~",nativeKey=True)

    def addToChar(self, character):
        self.character = character
        character.addListener(self.onEvent, self.subscribedEvent())

popupsArray = []
