import src

class MeditationPlate(src.items.Item):
    """
    ingame item used to give the player hints to treasure
    """
    type = "MeditationPlate"
    def __init__(self,inscription=None):
        super().__init__(display=(src.interaction.urwid.AttrSpec("#3c3","#000"),"::"))
        self.name = "meditation plate"
        self.description = "a place to find yourself and heal"

        self.bolted = True
        self.walkable = True

    def apply(self, character):
        """
        Parameters:
            character: the character trying to use the item
        """

        self.delayedAction({"action":self.heal,"character":character,"delayTime":100})

    def heal(self, extraParams):
        character = extraParams["character"]

        character.changed("meditated",{"character":character,"item":self})

        if character.health > 50:
            character.addMessage("you don't heal, you already have 50 health")
            return

        heal_amount = max(0,(min(character.adjustedMaxHealth,50)-character.health))
        character.heal(heal_amount,reason="meditation")

src.items.addType(MeditationPlate)
