import src
import src.popups


class EnterShrineTerrain(src.popups.Popup):
    def subscribedEvent(self):
        return "entered terrain"

    def text(self):
        return """there is a room, that has a loot and a statue, it looks like it is a shrine of some sort, maybe you can prey there"""

    def conditionMet(self, params) -> bool:
        return self.character.getTerrain().tag == "shrine"


src.popups.popupsArray.append(EnterShrineTerrain)
