from functools import partial

import src
import src.popups


class EnterRoom(src.popups.Popup):
    def __init__(self, roomType, message):
        self.roomType = roomType
        self.message = message
        super().__init__()

    def subscribedEvent(self):
        return "entered room"

    def text(self):
        if isinstance(self.message, str):
            return self.message
        else:
            return self.message()

    def conditionMet(self, params) -> bool:
        return self.character.container.tag == self.roomType

def arena_message():
    return [
        """Your implant interrupts:

You made it through the trap room into the base.

There is an enemy (""",
        (src.interaction.urwid.AttrSpec("#f00", "black"), "EE"),
        """) in the base. Be careful.

Use the quest menu by pressing q to get more information how to beat this enemy.

""",
    ]


room_message = [
    (
        "traproom",
        """Your implant interrupts:

You just entered a trap room.
Be careful and don't step onto the triggerPlates (_~)

press q to get more detailed information.
""",
    ),
    (
        "arena",
        arena_message,
    ),
]

for type, message in room_message:
    src.popups.popupsArray.append(partial(EnterRoom, type, message))
