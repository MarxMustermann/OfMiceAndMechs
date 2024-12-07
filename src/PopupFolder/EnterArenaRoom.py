import src
import src.popups


class EnterArenaRoom(src.popups.Popup):
    def subscribedEvent(self):
        return "entered room"

    def text(self):
        return "there is some armors and weapon in the room\nyou can equip them using j"

    def ConditionMet(self, params) -> bool:
        return self.character.container.tag == "arena"


src.popups.popupsArray.append(EnterArenaRoom)
