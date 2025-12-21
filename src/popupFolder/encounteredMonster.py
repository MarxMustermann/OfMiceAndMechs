import src.characters


class EncounteredMonster(src.popups.Popup):
    def __init__(self, monsterType):
        self.monsterType = monsterType

    def subscribedEvent(self):
        return "encountered character"

    def text(self):
        return self.monsterType().description()

    def conditionMet(self, params) -> bool:
        return type(params["other_character"]).__name__ == self.monsterType.__name__

for charType in src.characters.characterMap.values():
    if issubclass(charType,  src.characters.characterMap["Monster"]) and charType != src.characters.characterMap["Monster"]:
        src.popups.popupsArray.append(EncounteredMonster(charType))
