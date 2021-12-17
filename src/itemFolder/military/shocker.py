import src
import random

class Shocker(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    should have the habit to explode at inconvienent times
    """

    type = "Shocker"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="/\\")

    def apply(self, character):
        """

        Parameters:
            character: the character trying to use the item
        """

        compressorFound = None
        for item in character.inventory:
            if isinstance(item,src.items.itemMap["CrystalCompressor"]):
                compressorFound = item
                break

        if compressorFound:
            if self.container and isinstance(self.container,src.rooms.Room):
                if hasattr(self.container,"electricalCharges"):
                    self.container.electricalCharges += 1
                    character.addMessage("you activate the shocker and increase the rooms charges to %s"%(self.container.electricalCharges,))
            character.inventory.remove(compressorFound)
        else:
            character.addMessage("no crystal compressor found in inventory")

src.items.addType(Shocker)
