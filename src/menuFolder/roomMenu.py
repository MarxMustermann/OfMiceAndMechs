import logging

import src

logger = logging.getLogger(__name__)

class RoomMenu(src.subMenu.SubMenu):
    type = "RoomMenu"

    def __init__(self, room):
        super().__init__()
        self.room = room
        self.submenu = None
        self.firstKey = True

    def handleKey(self, key, noRender=False, character = None):
        self.persistentText = "room menu \n\n"

        self.persistentText = [self.persistentText]
        self.persistentText.append(f"{self.room.objType} - {self.room.tag}\n")
        if hasattr(self.room,"chargeStrength"):
            self.persistentText.append("chargeStrength: " + str(self.room.chargeStrength)+"\n")
        if hasattr(self.room,"electricalCharges"):
            self.persistentText.append("electricalCharges: " + str(self.room.electricalCharges)+"\n")
        if hasattr(self.room,"maxElectricalCharges"):
            self.persistentText.append("maxElectricalCharges: " + str(self.room.maxElectricalCharges)+"\n")
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
                self.persistentText.append("There is no staff assigned.\nassign staff by using the staff artwork (SA)")

        self.persistentText.append(f"\n\nRoompriority: {self.room.priority}")

        if self.room.floorPlan:
            self.persistentText.append("\n\nThis room has a floor plan.")
            if "walkingSpaces" in self.room.floorPlan:
                logger.info("walkingSpaces")
                logger.info(self.room.floorPlan["walkingSpaces"])
            if "buildSites" in self.room.floorPlan:
                logger.info("buildSites")
                logger.info(self.room.floorPlan["buildSites"])
            if "storageSlots" in self.room.floorPlan:
                logger.info("storageSlots")
                logger.info(self.room.floorPlan["storageSlots"])

        try:
            self.room.requiredDuties
        except:
            self.room.requiredDuties = []

        if self.room.requiredDuties:
            self.persistentText.append("\n\nThis room has required duties.\n%s"%self.room.requiredDuties)

        self.persistentText.append("\n\n- q: open staff section\n- r: show resource sources\n- o: issue room orders")

        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        if self.firstKey:
            self.firstKey = False
            return None

        if character and key in ("q",):
            character.macroState["submenue"] = src.menuFolder.RoomDutyMenu.RoomDutyMenu(self.room)

        if character and key in ("r",):
            character.macroState["submenue"] = src.menuFolder.RoomSourceMenu.RoomSourceMenu(self.room)

        if character and key in ("o",):
            homeRoom = character.getHomeRoom()
            items = homeRoom.getItemsByType("OrderArtwork",needsBolted=True)
            if not items:
                character.addMessage("order artwork not found")
                return True
            item = items[0]
            item.showMap(character)
            self.done = True
            return True

        # exit the submenu
        if key in ("esc",):
            self.done = True
            return True
        return None
