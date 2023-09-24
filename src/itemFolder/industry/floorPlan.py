import src
import json
import copy

class FloorPlan(src.items.Item):
    """
    """

    type = "FloorPlan"

    def __init__(self, autoRun=True):
        """
        configuring the super class
        """

        super().__init__(display="fp")

        self.name = "floor plan"
        self.description = "stores the information about a room layout"
        self.bolted = False
        self.walkable = True

        """
        self.applyOptions.extend(
                [
                    ("runJobOrder", "run job order macro"),
                    ("runSingleStep", "run single step"),
                    ("showInfo", "show info"),
                    ("addBreakPoint", "add break point"),
                ]
            )
        self.applyMap = {
            "runJobOrder": self.runJobOrder,
            "runSingleStep": self.runSingleStep,
            "showInfo": self.showInfo,
            "addBreakPoint": self.addBreakPoint,
        }
        """
    
    def readFloorPlanFromRoom(self):
        room = self.container

        #print(room.walkingSpace)
        self.walkingSpace = copy.copy(room.walkingSpace)
        #print(room.inputSlots)
        self.inputSlots = copy.copy(room.inputSlots)
        #print(room.outputSlots)
        self.outputSlots = copy.copy(room.outputSlots)

        self.buildSites = []
        for item in room.itemsOnFloor:
            if (not item.bolted) or item.xPosition in (0,12) or item.yPosition in (0,12):
                continue
            extra = {}
            if item.type == "Machine":
                extra = {"toProduce":item.toProduce}
            if item.type == "DutyBell":
                extra = {"duty":item.duty}
            self.buildSites.append((item.getPosition(),item.type,extra))
        print(self.buildSites)

        for walkingSpace in self.walkingSpace:
            self.container.addAnimation(walkingSpace,"showchar",3,{"char":"::"})
        for slot in self.inputSlots:
            self.container.addAnimation(slot[0],"showchar",3,{"char":"::"})
        for slot in self.outputSlots:
            self.container.addAnimation(slot[0],"showchar",3,{"char":"::"})
        for slot in self.buildSites:
            self.container.addAnimation(slot[0],"showchar",3,{"char":"XX"})

    def apply(self,character):
        room = self.container

        floorPlan = {
                "walkingSpace": list(self.walkingSpace),
                "inputSlots": copy.copy(self.inputSlots),
                "outputSlots": copy.copy(self.outputSlots),
                "buildSites": copy.copy(self.buildSites)
             }

        room.floorPlan = floorPlan

        character.addMessage("you transfer the floor plan to the room you are in")

        for walkingSpace in self.walkingSpace:
            self.container.addAnimation(walkingSpace,"showchar",3,{"char":"::"})
        for slot in self.inputSlots:
            self.container.addAnimation(slot[0],"showchar",3,{"char":"::"})
        for slot in self.outputSlots:
            self.container.addAnimation(slot[0],"showchar",3,{"char":"::"})
        for slot in self.buildSites:
            self.container.addAnimation(slot[0],"showchar",3,{"char":"XX"})

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the text
        """

        text = super().getLongInfo()
        text += f"""

information:

buildSites:
{self.buildSites}

walkingspace:
{self.walkingSpace}

inputSlots:
{self.inputSlots}

outputSlots:
{self.outputSlots}

"""
        print(self.buildSites)
        return text

src.items.addType(FloorPlan)
