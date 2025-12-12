from functools import partial

import src

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
        """Everything you see is in ruins. You can't tell what once was here.\n\nYou can clearly see movement between the rouble though.\n\n-- usefull items can be looted from the ruins""",
    ),
    (
        "shrine",
        """A small shrine inviting you to pray.\nIt reminds you of home.\n\n-- you can use shrines to teleport home""",
    ),
    (
        "lab",
        """it looks like there is an old lab guarded by a lot of monsters.\n\nYou can feel something horrible happened here and that the place holds dark secrets. Better not to find out what dark secrets lie here.\n\n-- leave this place immediatly and stay away""",
    ),
    (
        "statue room",
        """A ceremonial statue in a small dedicated it looks like there is an old lab guarded by a lot of monsters.\n\nYou can feel something horrible happened here and that the place holds dark secrets. Better not to find out what dark secrets lie here.\n\n-- leave this place immediatly and stay away""",
    ),
    (
        "nothingness",
        """There is nothing here than swamp and maybe a bit of scrap here or there.\n\n-- nothing interesting to be found here""",
    ),
    (
        "cloning lab",
        """The implant and cloning technology was developed in those labs. Many interessting things should still be left here.\n\n-- best to leave those alone""",
    ),
    (
        "spider pit",
        """This terrain is overrun with spiders, mostly concerned with themselves\n\n-- best to stay away if you are not looking for a fight""",
    ),
    (
        "dungeon",
        """This dungeon protects the heart of a god. It is well protected by a series of defences.\n\n-- best to stay away if you are not looking for a fight""",
    ),
]

for type, message in terrain_message:
    src.popups.popupsArray.append(partial(EnterTerrain, type, message))
