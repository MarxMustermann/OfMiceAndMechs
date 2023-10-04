import src


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
            if isinstance(item,src.items.itemMap["LightningRod"]):
                compressorFound = item
                break

        if compressorFound:
            if self.container and isinstance(self.container,src.rooms.Room):
                if hasattr(self.container,"electricalCharges"):
                    if self.container.electricalCharges < self.container.maxElectricalCharges:
                        self.container.electricalCharges += 1
                        character.addMessage(f"you activate the shocker and increase the rooms charges to {self.container.electricalCharges}")
                        character.inventory.remove(compressorFound)

                        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":"~*"})
                        character.changed("charged traproom",(character,self.container))
                    else:
                        character.addMessage("this room is fully charged")
                else:
                    character.addMessage("this room can't be charged")
            else:
                character.addMessage("no room found")
        else:
            character.addMessage("no crystal compressor found in inventory")

    def render(self):
        color = "#000"
        if isinstance(self.container,src.rooms.TrapRoom):
            chargeFaction = self.container.electricalCharges/self.container.maxElectricalCharges
            if self.container.electricalCharges == 0:
                color = "#000"
            elif chargeFaction < 1/15:
                color = "#111"
            elif chargeFaction < 2/15:
                color = "#222"
            elif chargeFaction < 3/15:
                color = "#333"
            elif chargeFaction < 4/15:
                color = "#444"
            elif chargeFaction < 5/15:
                color = "#555"
            elif chargeFaction < 6/15:
                color = "#666"
            elif chargeFaction < 7/15:
                color = "#777"
            elif chargeFaction < 8/15:
                color = "#888"
            elif chargeFaction < 9/15:
                color = "#999"
            elif chargeFaction < 10/15:
                color = "#aaa"
            elif chargeFaction < 11/15:
                color = "#aab"
            elif chargeFaction < 12/15:
                color = "#aac"
            elif chargeFaction < 13/15:
                color = "#aad"
            elif chargeFaction < 14/15:
                color = "#aae"
            else:
                color = "#aaf"
        return (src.interaction.urwid.AttrSpec("#fff", color), "/\\")

src.items.addType(Shocker)
