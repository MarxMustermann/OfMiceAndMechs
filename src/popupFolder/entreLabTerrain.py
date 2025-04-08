import src
import src.popups


class EnterLabTerrain(src.popups.Popup):
    def subscribedEvent(self):
        return "entered terrain"

    def text(self):
        return """it looks like there is a lab in the middle but it guarded by a lot of monster, what kind of secrets the lab have, that is up for you to know"""

    def conditionMet(self, params) -> bool:
        return self.character.getTerrain().tag == "lab"


src.popups.popupsArray.append(EnterLabTerrain)
