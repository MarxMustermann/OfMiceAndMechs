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
        ["Everything you see ",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"is in ruins.")," You can't tell what once was here.\n\nYou can clearly see movement between the rouble, though.\n\n-- ",(src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"usefull items can be looted from the ruins")],
    ),
    (
        "shrine",
        ["A small shrine inviting you to pray.\nIt reminds you of ",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"home."),"\n\n-- ",(src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"you can use shrines to teleport home""")],
    ),
    (
        "lab",
        ["It looks like there is an old lab guarded by a lot of monsters.\n\nYou can feel ",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"statue"),"something horrible happened here")," and that the place holds dark secrets. Better not to find out what dark secrets lie here.\n\n-- ",(src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"leave this place immediatly and stay away")],
    ),
    (
        "statue room",
        ["A ceremonial ",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"statue")," in a small temple like structure.\n\n-- ",(src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"this place may lead you to a dungeon")],
    ),
    (
        "nothingness",
        ["There is ",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"nothing here")," other than swamp and maybe a bit of Scrap here or there.\n\n-- ",(src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"nothing interesting to be found here"],
    ),
    (
        "cloning lab",
        ["The implant and cloning technology was developed in those labs. Many ",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"interesting"," things should still be left here.\n\n-- ",(src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"best to leave those alone")],
    ),
    (
        "spider pit",
        ["This terrain is overrun with ",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"spiders,")," mostly concerned with themselves\n\n-- ",(src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"best to stay away if you are not looking for a fight")],
    ),
    (
        "dungeon",
        ["This dungeon protects the ",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"heart of a god.")," It is well protected by a series of defences.\n\n-- ",(src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"best to stay away if you are not looking for a fight")],
    ),
    (
        "remote base",
        [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You see a base."),"It is similar to what your base looks like.\n\n-- ",(src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"You may be able to find some useful resorces here"],
    ),
]

for type, message in terrain_message:
    src.popups.popupsArray.append(partial(EnterTerrain, type, message))
