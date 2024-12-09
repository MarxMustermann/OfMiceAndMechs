import src
import src.popups


class EnterArenaRoom(src.popups.Popup):
    def subscribedEvent(self):
        return "entered room"

    def text(self):
        return """Your implant interrupts:

You made it through the trap room into the base.

There is an enemy (EE) in the base. Be careful.

Use the quest menu to get more information how to beat this enemy.

"""

    def ConditionMet(self, params) -> bool:
        return self.character.container.tag == "arena"


src.popups.popupsArray.append(EnterArenaRoom)
