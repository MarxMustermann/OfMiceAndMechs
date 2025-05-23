from functools import partial

import src
import src.popups


class EnterTerrain(src.popups.Popup):
    def __init__(self, terrainType, massage):
        self.terrainType = terrainType
        self.massage = massage
        super().__init__()

    def subscribedEvent(self):
        return "entered terrain"

    def text(self):
        return self.massage

    def conditionMet(self, params) -> bool:
        return self.character.getTerrain().tag == self.terrainType


terrain_massage = [
    (
        "ruin",
        """you see the remains of a lost colony and a lot of rogue creatures, which begs the question what has happened to them""",
    ),
    (
        "shrine",
        """there is a room, that has a loot and a statue, it looks like it is a shrine of some sort, maybe you can prey there""",
    ),
    (
        "lab",
        """it looks like there is a lab in the middle but it guarded by a lot of monster, what kind of secrets the lab have, that is up for you to know""",
    ),
]

for type, massage in terrain_massage:
    src.popups.popupsArray.append(partial(EnterTerrain, type, massage))
