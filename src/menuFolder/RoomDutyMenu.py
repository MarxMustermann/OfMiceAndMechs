
from src.menuFolder.SubMenu import SubMenu

import src

class RoomDutyMenu(SubMenu):
    """
    """

    type = "RoomDutyMenu"

    def __init__(self, room):
        """
        initialise inernal state

        Parameters:
            text: the text to show
        """

        super().__init__()
        self.room = room
        self.keyPressed = ""
        self.done = False
        self.index = (0,0)

    def handleKey(self, key, noRender=False, character = None):
        """
        show the text and quit on second keypress

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in ("w",) and self.index[1] > 0:
            self.index = (self.index[0],self.index[1]-1)
        if key in ("s",) and self.index[1] < len(self.room.duties)-1:
            self.index = (self.index[0],self.index[1]+1)
        if key in ("a",) and self.index[0] > 0:
            self.index = (self.index[0]-1,self.index[1])
        if key in ("d",) and self.index[0] < len(self.room.staff)-1:
            self.index = (self.index[0]+1,self.index[1])

        if key in ("j","enter"):
            duty = self.room.duties[self.index[1]]
            staffCharacter = self.room.staff[self.index[0]]
            if duty in staffCharacter.duties:
                staffCharacter.duties.remove(duty)
            else:
                staffCharacter.duties.append(duty)

        # show info
        if not noRender:
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
            self.persistentText = """
move the cursor using w/a/s/d.
press j or enter to select

"""
            self.persistentText = [self.persistentText]
            self.persistentText.append(f"{self.room.objType} - {self.room.name}\n")
            try:
                self.persistentText.append( "electricalCharges: " + str(self.room.electricalCharges)+"\n")
            except:
                pass
            try:
                self.persistentText.append("maxElectricalCharges: " + str(self.room.maxElectricalCharges)+"\n")
            except:
                pass
            self.persistentText.append("\n\n")
            if self.room.staff:
                self.persistentText.append("staff:\n")
                for staffNpc in self.room.staff:
                    deadText = ""
                    if staffNpc.dead:
                        deadText = " (dead)"
                    questText = ""
                    if not staffNpc.dead and staffNpc.quests:
                        questText = staffNpc.quests[0].description.split("\n")[0]
                        try:
                            questText += staffNpc.quests[0].description.split("\n")[1]
                        except:
                            pass
                    self.persistentText.append(f"{staffNpc.name}{deadText} - {questText}\n")
            else:
                    self.persistentText.append("There is no staff assigned assign staff by using the staff artwork (SA)")

            self.persistentText += "\n"

            if self.room.staff:
                rowCounter = 0
                for duty in self.room.duties:
                    self.persistentText.append( duty + " |")
                    colCounter = 0
                    for staffCharacter in self.room.staff:
                        frontColor = "#fff"
                        if duty in staffCharacter.duties:
                            frontColor = "#0e0"
                        backColor = "#000"
                        if (colCounter,rowCounter) == self.index:
                            backColor = "#444"
                        self.persistentText.append((src.interaction.urwid.AttrSpec(frontColor, backColor),staffCharacter.name))
                        self.persistentText.append(" |")
                        colCounter += 1
                    self.persistentText.append("\n")
                    rowCounter += 1
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        # exit the submenu
        if key in ("esc",):
            self.done = True
            return True

        self.firstRun = False

        return False
