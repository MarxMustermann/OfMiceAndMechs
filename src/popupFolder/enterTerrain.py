from functools import partial

import src
import src.popups


class EnterTerrain(src.popups.Popup):
    def __init__(self, terrainType, message):
        self.terrainType = terrainType
        self.message = message
        super().__init__()

    def subscribedEvent(self):
        return "entered terrain"

    def text(self):
        return self.message

    def conditionMet(self, params) -> bool:
        return self.character.getTerrain().tag == self.terrainType


terrain_message = [
    (
        "ruin",
        """Everything you see is in ruins. You can't tell what once was here.\n\nYou can clearly see movement between the roublw though.""",
    ),
    (
        "shrine",
        """A small shrine inviting you to pray.\nIt reminds you of home.""",
    ),
    (
        "lab",
        """it looks like there is a lab in the middle but it guarded by a lot of monsters.\n\nBetter not to find out what dark secrets lie here.""",
    ),
]

for type, message in terrain_message:
    src.popups.popupsArray.append(partial(EnterTerrain, type, message))
