import random

import src


class AdventureArtwork(src.items.Item):
    """
    ingame item spawning quests and giving rewards
    used to add more excitement and ressources to the game
    """

    type = "AdventureArtwork"

    def __init__(self):
        """
        call superclass constructor with modified parameters
        """

        super().__init__(display="AA")

        self.name = "adventure artwork"

        self.applyOptions.extend(
                [
                    ("doAdventure", "do adventure"),
                    ("addCoordinate", "add coordinate"),
                ]
            )
        self.applyMap = {
            "doAdventure": self.doAdventure,
        }

    def doAdventure(self,character):
        return

src.items.addType(AdventureArtwork)
