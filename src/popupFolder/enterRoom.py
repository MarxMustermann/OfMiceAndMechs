from functools import partial

import src
import src.popups


class EnterRoom(src.popups.Popup):
    def __init__(self, roomType, massage):
        self.roomType = roomType
        self.massage = massage
        super().__init__()

    def subscribedEvent(self):
        return "entered room"

    def text(self):
        if isinstance(self.massage, str):
            return self.massage
        else:
            return self.massage()

    def conditionMet(self, params) -> bool:
        return self.character.container.tag == self.roomType

def arena_massage():
    return [
        """Your implant interrupts:

You made it through the trap room into the base.

There is an enemy (""",
        (src.interaction.urwid.AttrSpec("#f00", "black"), "EE"),
        """) in the base. Be careful.

Use the quest menu by pressing q to get more information how to beat this enemy.

""",
    ]


room_massage = [
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
        arena_massage,
    ),
]

for type, massage in room_massage:
    src.popups.popupsArray.append(partial(EnterRoom, type, massage))
