import src
import random


class StaffArtwork(src.items.Item):
    """
    ingame item that allows the player to set staff for nps
    """

    type = "StaffArtwork"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display="SA")

        self.name = "staff artwork"
                
        self.applyOptions.extend(
                                                [
                                                    ("showMap", "show map"),
                                                    ("assignByRoomType", "assign staff by room type"),
                                                ]
                                )

        self.applyMap = {
                                    "showMap": self.showMap,
                                    "assignByRoomType": self.assignByRoomType,
                                }

    def showMap(self, character, cursor=None):
        # render empty map
        mapContent = []
        for x in range(0, 15):
            mapContent.append([])
            for y in range(0, 15):
                if x not in (0, 14) and y not in (0, 14):
                    char = "  "
                elif not x == 7 and not y == 7:
                    char = "##"
                else:
                    char = "  "
                mapContent[x].append(char)

        for room in self.container.container.rooms:
            mapContent[room.yPosition][room.xPosition] = room.displayChar

        functionMap = {}

        for room in self.container.container.rooms:
            if not hasattr(room,"duties"):
                continue
            if not hasattr(room,"staff"):
                continue

            x = room.xPosition
            y = room.yPosition

            description = "\n"
            description += "staff: \n"
            for staffCharacter in room.staff:
                try:
                    description += staffCharacter.name+" %s \n"%(staffCharacter.quests[0].subQuests[0],)
                except:
                    description += staffCharacter.name+" \n"
            description += "\n"
            for duty in room.duties:
                description += "%s: "%(duty,)
                for staffCharacter in room.staff:
                    if duty in staffCharacter.duties:
                        description += "%s   "%(staffCharacter.name)
                description += "\n"

            functionMap[(x,y)] = {}
            functionMap[(x,y)]["f"] = {
                    "function": {
                        "container":self,
                        "method":"autoFillStaffFromMap",
                        "params":{"character":character,"amount":1},
                    },
                    "description":"to auto fill staff"
                }
            functionMap[(x,y)]["F"] = {
                    "function": {
                        "container":self,
                        "method":"autoFillStaffFromMap",
                        "params":{"character":character},
                    },
                    "description":"to auto fill staff"
                }
            functionMap[(x,y)]["e"] = {
                    "function": {
                        "container":self,
                        "method":"editStaffFromMap",
                        "params":{"character":character},
                    },
                    "description":description
                }

        plot = (self.container.xPosition,self.container.yPosition)
        mapContent[plot[1]][plot[0]] = "CB"

        extraText = "\n\n"

        self.submenue = src.interaction.MapMenu(mapContent=mapContent,functionMap=functionMap, extraText=extraText, cursor=cursor)
        character.macroState["submenue"] = self.submenue

    def fetchCityleader(self):
        cityBuilder = None
        for item in self.container.itemsOnFloor:
            if not item.type == "CityBuilder2":
                continue
            cityBuilder = item

        if not cityBuilder:
            return None

        return cityBuilder.cityLeader

    def autoFillStaffFromMap(self, extraInfo,redirect=True):
        character = extraInfo["character"]

        cityLeader = self.fetchCityleader()
        if not cityLeader:
            character.addMessage("no city leader")
            return

        foundWorker = None
        for subleader in cityLeader.subordinates:
            if not subleader or subleader.dead:
                continue

            for subsubleader in subleader.subordinates:
                if not subsubleader or subsubleader.dead:
                    continue

                for worker in subsubleader.subordinates:
                    if not worker or worker.dead:
                        continue

                    if worker.isStaff:
                        continue

                    foundWorker = worker
                    break
                if foundWorker:
                    break
            if foundWorker:
                break

        if not foundWorker:
            character.addMessage("no worker found")
            return

        quest = src.quests.BeUsefull(targetPosition=extraInfo["coordinate"])
        quest.activate()
        quest.assignToCharacter(foundWorker)
        foundWorker.quests.insert(0,quest)
        
        room = self.container.container.getRoomByPosition(extraInfo["coordinate"])[0]
        room.staff.append(foundWorker)
        foundWorker.isStaff = True
        foundWorker.duties = room.duties

        numDuties = len(room.duties)//len(room.staff)
        counter = 0
        for staffCharacter in room.staff:
            staffCharacter.duties = room.duties[numDuties*counter:numDuties*(counter+1)]
            counter += 1
        
        cutOff = numDuties*(counter)
        if cutOff < 0:
            cutOff = 0

        counter = 0
        for duty in room.duties[cutOff:]:
            room.staff[counter].duties.append(duty)
            counter += 1

        if redirect:
            self.showMap(character,cursor=extraInfo["coordinate"])

    def autoRemoveStaffFromMap(self, extraInfo,redirect=True):
        character = extraInfo["character"]

        cityLeader = self.fetchCityleader()
        if not cityLeader:
            character.addMessage("no city leader")
            return

        room = self.container.container.getRoomByPosition(extraInfo["coordinate"])[0]
        if not room.staff:
            character.addMessage("no staff")
            return
        worker = room.staff.pop()
        worker.quests.pop()
        worker.isStaff = False

        if not room.staff:
            return

        numDuties = len(room.duties)//len(room.staff)
        counter = 0
        for staffCharacter in room.staff:
            staffCharacter.duties = room.duties[numDuties*counter:numDuties*(counter+1)]
            counter += 1
        
        cutOff = numDuties*(counter)
        if cutOff < 0:
            cutOff = 0

        counter = 0
        for duty in room.duties[cutOff:]:
            room.staff[counter].duties.append(duty)
            counter += 1

        if redirect:
            self.showMap(character,cursor=extraInfo["coordinate"])


    def editStaffFromMap(self, character):
        pass

    def assignByRoomType(self, character):
        self.submenue = src.interaction.StaffAsMatrixMenu(self)
        character.macroState["submenue"] = self.submenue

src.items.addType(StaffArtwork)
