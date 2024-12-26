import src
import src.popups


class EnterArenaRoom(src.popups.Popup):
    def subscribedEvent(self):
        return "entered room"

    def text(self):
        text = []
        text.extend(["""Your implant interrupts:

You made it through the trap room into the base.

There is an enemy (""",(src.interaction.urwid.AttrSpec("#f00", "black"),"EE"),""") in the base. Be careful.

Use the quest menu to get more information how to beat this enemy.

"""])
        return text

    def conditionMet(self, params) -> bool:
        return self.character.container.tag == "arena"


src.popups.popupsArray.append(EnterArenaRoom)
