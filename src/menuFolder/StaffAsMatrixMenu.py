
import SubMenu

from src.interaction import header, main, urwid


class StaffAsMatrixMenu(SubMenu):
    type = "StaffAsMatrixMenu"

    def __init__(self,staffArtwork):
        super().__init__()
        self.index = [0,0]
        self.staffArtwork = staffArtwork
        self.roomTypes = ["TrapRoom","WorkshopRoom"]


    def handleKey(self, key, noRender=False, character = None):
        """
        show the help text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in ("esc"," ",):
            return True

        text = ["press wasd to move cursor\npress j to increase\npress k to decrease\n"]

        if key in ("w",) and self.index[1] > 0:
            self.index[1] -= 1
        if key in ("s",) and self.index[1] < len(self.roomTypes)-1:
            self.index[1] += 1
        if key in ("a",) and self.index[0] > 0:
            self.index[0] -= 1
        if key in ("d",):
            self.index[0] += 1

        if key in ("j",):
            roomCounter = 1
            for room in self.staffArtwork.container.container.rooms:
                if room.objType == self.roomTypes[self.index[1]]:
                    if self.index[0] == 0 or self.index[0] == roomCounter:
                        self.staffArtwork.autoFillStaffFromMap({"character":character,"coordinate":(room.xPosition,room.yPosition)},redirect=False)
                    roomCounter += 1
        if key in ("k",):
            roomCounter = 1
            for room in self.staffArtwork.container.container.rooms:
                if room.objType == self.roomTypes[self.index[1]]:
                    if self.index[0] == 0 or self.index[0] == roomCounter:
                        self.staffArtwork.autoRemoveStaffFromMap({"character":character,"coordinate":(room.xPosition,room.yPosition)},redirect=False)
                    roomCounter += 1

        counter = 0
        for roomType in self.roomTypes:
            color = "#fff"
            if counter == self.index[1] and self.index[0] == 0:
                color = "#f00"
            text.append((urwid.AttrSpec(color, "default"),f"{roomType}"))
            roomCounter = 1
            for room in self.staffArtwork.container.container.rooms:
                if room.objType == roomType:
                    color = "#fff"
                    if counter == self.index[1] and roomCounter == self.index[0]:
                        color = "#f00"
                    text.append((urwid.AttrSpec(color, "default")," %s"%(len(room.staff))))
                    roomCounter += 1
            text.append("\n")
            counter += 1

        # show info
        header.set_text((urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))
        self.persistentText = text
        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        return False

    def getQuestMarkersTile(self, character):
        out = []

        roomType = self.roomTypes[self.index[1]]
        roomCounter = 1
        for room in self.staffArtwork.container.container.rooms:
            if room.objType != roomType:
                continue
            if self.index[0] == 0 or self.index[0] == roomCounter:
                out.append((room.getPosition(),"selected"))
            roomCounter += 1
        return out

