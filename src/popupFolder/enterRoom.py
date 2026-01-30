from functools import partial

import src

class EnterRoom(src.popups.Popup):
    def __init__(self, roomType, message):
        self.roomType = roomType
        self.message = message
        super().__init__()

    def subscribedEvent(self):
        return "entered room"

    def text(self):
        self.character.clear_quests()
        src.gamestate.gamestate.stern["reached_base"] = True
        return self.message

    def conditionMet(self, params) -> bool:
        return self.character.container.tag == self.roomType


room_message = [
    (
        "trapRoom",
        """Your implant interrupts:

You just entered a trap room.
Be careful and don't step onto the triggerPlates (_~)

press q to get more detailed information.
""",
    ),
    (
        "arena",
        ["""Your implant interrupts:

You made it through the trap room into the base.

There is an enemy (""",(src.pseudoUrwid.AttrSpec("#f00", "black"), "EE"),""") in the base. Be careful.

Use the quest menu by pressing q to get more information how to beat this enemy.

"""],
    ),
]

for type, message in room_message:
    src.popups.popupsArray.append(partial(EnterRoom, type, message))
