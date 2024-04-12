import src


class SpecialItem(src.items.Item):
    """
    ingame item transforming into a rip in reality when using a key
    """

    type = "SpecialItem"

    def __init__(self,epoch=0):
        """
        configure the superclass
        """

        super().__init__(display="!!")
        self.name = "special item"

        self.walkable = True
        self.bolted = False
        self.itemID = None
        self.epoch = epoch

    def getLongInfo(self):
        return f"{self.itemID}"

    def render(self):
        color = "#888"
        if self.itemID == 1:
            color = "#f00"
        elif self.itemID == 2:
            color = "#0f0"
        elif self.itemID == 3:
            color = "#00f"
        elif self.itemID == 4:
            color = "#0ff"
        elif self.itemID == 5:
            color = "#f0f"
        elif self.itemID == 6:
            color = "#ff0"
        elif self.itemID == 7:
            color = "#fff"
        displaychars = "gh"

        display = [
                (src.interaction.urwid.AttrSpec(color, "black"), displaychars),
            ]
        return display

src.items.addType(SpecialItem)
