import src
import src.popups


class EnterTrapRoom(src.popups.Popup):
    def subscribedEvent(self):
        return "entered room"

    def text(self):
        return """Your implant iterrupts:

You just entered a trap room.
Be careful and don't step onto the triggerPlates (_~)

press q to get more detailed information.
"""

    def ConditionMet(self, params) -> bool:
        return self.character.container.tag == "traproom"
src.popups.popupsArray.append(EnterTrapRoom)
