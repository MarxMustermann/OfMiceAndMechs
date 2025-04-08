import src
import src.popups


class EnterRuinTerrain(src.popups.Popup):
    def subscribedEvent(self):
        return "entered terrain"

    def text(self):
        return """you see the remains of a lost colony and a lot of rogue creatures, which begs the question what has happened to them"""

    def conditionMet(self, params) -> bool:
        return self.character.getTerrain().tag == "ruin"


src.popups.popupsArray.append(EnterRuinTerrain)
