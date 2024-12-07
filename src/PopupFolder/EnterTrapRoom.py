import src
import src.popups


class EnterTrapRoom(src.popups.Popup):
    def subscribedEvent(self):
        return "entered room"

    def text(self):
        return "It seems the room has many traps you need to deactivate them\nmaybe try activating it from far away"

    def ConditionMet(self, params) -> bool:
        return self.character.container.tag == "traproom"
src.popups.popupsArray.append(EnterTrapRoom)
