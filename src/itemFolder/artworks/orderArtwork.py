import src
import random


class OrderArtwork(src.items.Item):
    """
    ingame item that allows the player to set duties for npcs of that city
    """

    type = "OrderArtwork"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display="OA")

        self.name = "order artwork"
                
        self.applyOptions.extend(
                                                [
                                                    ("showMap", "show map"),
                                                    ("showQuests", "show what quests the npcs are currently doing"),
                                                    ("assignQuest", "assign quest to group"),
                                                ]
                                )

        self.applyMap = {
                                    "showMap": self.showMap,
                                    "showQuests": self.showQuests,
                                    "assignQuest": self.assignQuestFromMenu,
                                }

    def assignQuestFromMenu(self, character):
        self.assignQuest({"character":character})

    def assignQuest(self, extraInfo):
        
        character = extraInfo["character"]

        if not "groupType" in extraInfo:
            options = []
            options.append(("all","all NPCs"))
            options.append(("staff","staff NPCs"))
            options.append(("non staff","non staff NPCs"))
            options.append(("idle","idle NPCs"))
            options.append(("non idle","non idle NPCs"))
            options.append(("rank 4","rank 4 NPCs"))
            options.append(("rank 5","rank 5 NPCs"))
            options.append(("rank 6","rank 6 NPCs"))
            options.append(("rank 5-6","rank 5-6 NPCs"))
            options.append(("idle rank 6","idle rank 6 NPCs"))
            options.append(("idle non staff","idle non staff NPCs"))
            options.append(("idle non staff rank 6","idle rank 6 non staff NPCs"))
            submenue = src.interaction.SelectionMenu("what group to assign the quest to?",options,targetParamName="groupType")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"assignQuest","params":extraInfo}
            return

        if not "questType" in extraInfo:
            options = []
            if not "coordinate" in extraInfo:
                options.append(("Equip","equip"))
                options.append(("GoHome","go home"))
                options.append(("shelter","shelter"))
            else:
                options.append(("restockRoom","restock"))
            options.append(("BeUsefull","be usefull"))
            options.append(("cancel","cancel quests"))
            submenue = src.interaction.SelectionMenu("what quest to assign?",options,targetParamName="questType")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"assignQuest","params":extraInfo}
            return

        if not "amount" in extraInfo:
            options = []
            submenue = src.interaction.InputMenu("how many NPCs to assign? (0 for all)",targetParamName="amount")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"assignQuest","params":extraInfo}
            return

        targets = []
        cityLeader = self.fetchCityleader()
        mode = extraInfo["groupType"]

        def checkAdd(person):
            if mode == "all":
                targets.append(person)
                return
            if mode == "staff" and person.isStaff == True:
                targets.append(person)
                return
            if mode == "non staff" and person.isStaff == False:
                targets.append(person)
                return
            if mode == "idle" and not person.quests:
                targets.append(person)
                return
            if mode == "non idle" and person.quests:
                targets.append(person)
                return
            if mode == "rank 4" and person.rank == 4:
                targets.append(person)
                return
            if mode == "rank 5" and person.rank == 5:
                targets.append(person)
                return
            if mode == "rank 6" and person.rank == 6:
                targets.append(person)
                return
            if mode == "rank 5-6" and (person.rank == 6 or person.rank == 5):
                targets.append(person)
                return
            if mode == "idle rank 6" and (person.rank == 6 and not person.quests):
                targets.append(person)
                return
            if mode == "idle non staff" and (person.isStaff == False and not person.quests):
                targets.append(person)
                return
            if mode == "idle non staff rank 6" and (person.isStaff == False and person.rank == 6 and not person.quests):
                targets.append(person)
                return

        checkAdd(cityLeader)

        for subleader in cityLeader.subordinates:
            if not subleader or subleader.dead:
                continue

            checkAdd(subleader)

            for subsubleader in subleader.subordinates:
                if not subsubleader or subsubleader.dead:
                    continue

                checkAdd(subsubleader)

                for worker in subsubleader.subordinates:
                    if not worker or worker.dead:
                        continue

                    checkAdd(worker)

        counter = 0
        extraInfo["amount"] = int(extraInfo["amount"])
        for target in targets:
            if not extraInfo["amount"] == 0 and not extraInfo["amount"] > counter:
                break
            if extraInfo["questType"] == "cancel":
                if target.quests:
                    target.quests.remove(target.quests[0])
                continue
            if extraInfo["questType"] == "cancelAll":
                target.quests = []
                continue
            if extraInfo["questType"] == "shelter":
                quest = src.quests.questMap["WaitQuest"](lifetime=100)
                quest.assignToCharacter(target)
                quest.activate()
                target.quests.insert(0,quest)

                quest = src.quests.questMap["GoHome"]()
                quest.activate()
                quest.assignToCharacter(target)
                target.quests.insert(0,quest)
                continue
            if extraInfo["questType"] == "restockRoom":
                quest = src.quests.questMap["RestockRoom"]()
                quest.activate()
                quest.assignToCharacter(target)
                target.quests.insert(0,quest)

                quest = src.quests.questMap["GoToTile"]()
                quest.setParameters({"targetPosition":extraInfo["coordinate"]})
                quest.assignToCharacter(target)
                quest.activate()
                target.quests.insert(0,quest)
                continue
            quest = src.quests.questMap[extraInfo["questType"]]()
            if "coordinate" in extraInfo:
                quest.setParameters({"targetPosition":extraInfo["coordinate"]})
            quest.activate()
            quest.assignToCharacter(target)
            target.quests.insert(0,quest)
            counter += 1

    def showMap(self, character):
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

        for x in range(1,14):
            for y in range(1,14):
                functionMap[(x,y)] = {}
                functionMap[(x,y)]["m"] = {
                        "function": {
                            "container":self,
                            "method":"guardTileFromMap",
                            "params":{"character":character},
                        },
                        "description":"send npcs to guard tile",
                    }
                functionMap[(x,y)]["u"] = {
                        "function": {
                            "container":self,
                            "method":"beusefulFromMap",
                            "params":{"character":character,"amount":0},
                        },
                        "description":"send npcs to work on that tile",
                    }
                functionMap[(x,y)]["U"] = {
                        "function": {
                            "container":self,
                            "method":"beusefulFromMap",
                            "params":{"character":character},
                        },
                        "description":"send npcs to work on that tile (specific number)",
                    }
                functionMap[(x,y)]["q"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"amount":0},
                        },
                        "description":"send npcs to work on that tile",
                    }
                functionMap[(x,y)]["Q"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character},
                        },
                        "description":"send npcs to work on that tile (specific number)",
                    }
                functionMap[(x,y)]["v"] = {
                        "function": {
                            "container":self,
                            "method":"goToFromMap",
                            "params":{"character":character},
                        },
                        "description":"send npcs to that tile",
                    }
                functionMap[(x,y)]["r"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"amount":0},
                        },
                        "description":"send npcs to restock room",
                    }

        plot = (self.container.xPosition,self.container.yPosition)
        mapContent[plot[1]][plot[0]] = "CB"

        extraText = "\n\n"

        self.submenue = src.interaction.MapMenu(mapContent=mapContent,functionMap=functionMap, extraText=extraText)
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

    def showQuests(self, character):
        questsCount = {}
        
        cityLeader = self.fetchCityleader()
        if not cityLeader:
            character.addMessage("no city leader")
            return

        questType = "idle"
        if cityLeader.quests:
            questType = cityLeader.quests[0].type
        if not questType in questsCount:
            questsCount[questType] = 0
        questsCount[questType] += 1

        for subleader in cityLeader.subordinates:
            if not subleader or subleader.dead:
                continue

            questType = "idle"
            if subleader.quests:
                questType = subleader.quests[0].type
            if not questType in questsCount:
                questsCount[questType] = 0
            questsCount[questType] += 1

            for subsubleader in subleader.subordinates:
                if not subsubleader or subsubleader.dead:
                    continue

                questType = "idle"
                if subsubleader.quests:
                    questType = subsubleader.quests[0].type
                if not questType in questsCount:
                    questsCount[questType] = 0
                questsCount[questType] += 1

                for worker in subsubleader.subordinates:
                    if not worker or worker.dead:
                        continue

                    questType = "idle"
                    if worker.quests:
                        questType = worker.quests[0].type
                    if not questType in questsCount:
                        questsCount[questType] = 0
                    questsCount[questType] += 1

        text = "current active quest:\n"
        for (key,value) in questsCount.items():
            text += "%s: %s\n"%(key,value)
        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

    def assignQuestToNumNPCs(self, character, questType, numNPCs, params=None):
        if params == None:
            params = {}

        cityLeader = self.fetchCityleader()
        if not cityLeader:
            character.addMessage("no city leader")
            return

        numQuestsAssigned = 0

        # assign to idle NPCs
        for subleader in cityLeader.subordinates:
            if not subleader or subleader.dead:
                continue
            for subsubleader in subleader.subordinates:
                if not subsubleader or subsubleader.dead:
                    continue
                for worker in subsubleader.subordinates:
                    if not worker or worker.dead:
                        continue

                    if numQuestsAssigned < numNPCs and not worker.quests:
                        numQuestsAssigned += 1
                        quest = src.quests.questMap[questType]()
                        quest.setParameters(params)
                        quest.assignToCharacter(worker)
                        quest.activate()
                        worker.quests.insert(0,quest)

                if numQuestsAssigned < numNPCs and not subsubleader.quests:
                    numQuestsAssigned += 1
                    quest = src.quests.questMap[questType]()
                    quest.setParameters(params)
                    quest.assignToCharacter(subsubleader)
                    quest.activate()
                    subsubleader.quests.insert(0,quest)

            if numQuestsAssigned < numNPCs and not subleader.quests:
                numQuestsAssigned += 1
                quest = src.quests.questMap[questType]()
                quest.setParameters(params)
                quest.assignToCharacter(subleader)
                quest.activate()
                subleader.quests.insert(0,quest)

        if numQuestsAssigned < numNPCs and not cityLeader.quests:
            numQuestsAssigned += 1
            quest = src.quests.questMap[questType]()
            quest.setParameters(params)
            quest.assignToCharacter(cityLeader)
            quest.activate()
            cityLeader.quests.insert(0,quest)

        for subleader in cityLeader.subordinates:
            if not subleader or subleader.dead:
                continue
            for subsubleader in subleader.subordinates:
                if not subsubleader or subsubleader.dead:
                    continue
                for worker in subsubleader.subordinates:
                    if not worker or worker.dead:
                        continue
                    if numQuestsAssigned < numNPCs:
                        numQuestsAssigned += 1
                        quest = src.quests.questMap[questType]()
                        quest.setParameters(params)
                        quest.assignToCharacter(worker)
                        quest.activate()
                        worker.quests.insert(0,quest)

                if numQuestsAssigned < numNPCs:
                    numQuestsAssigned += 1
                    quest = src.quests.questMap[questType]()
                    quest.setParameters(params)
                    quest.assignToCharacter(subsubleader)
                    quest.activate()
                    subsubleader.quests.insert(0,quest)

            if numQuestsAssigned < numNPCs:
                numQuestsAssigned += 1
                quest = src.quests.questMap[questType]()
                quest.setParameters(params)
                quest.assignToCharacter(subleader)
                quest.activate()
                subleader.quests.insert(0,quest)

        if numQuestsAssigned < numNPCs:
            numQuestsAssigned += 1
            quest = src.quests.questMap[questType]()
            quest.setParameters(params)
            quest.assignToCharacter(cityLeader)
            quest.activate()
            cityLeader.quests.insert(0,quest)

    def guardTileFromMap(self, extraInfo):
        print("guardTileFromMap")

    def questFromMap(self, extraInfo):
        print(extraInfo)
        self.assignQuest(extraInfo)

    def beusefulFromMap2(self, extraInfo):
        params = {"targetPosition":extraInfo["coordinate"]}
        character = extraInfo["character"]
        questType = "BeUsefull"

        if "numNPCs" in extraInfo:
            try:
                extraInfo["numNPCs"] = int(extraInfo["numNPCs"])
            except:
                extraInfo["numNPCs"] = None

        if not "numNPCs" in extraInfo:
            submenue = src.interaction.InputMenu("how many NPCs to send?",targetParamName="numNPCs")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"beusefulFromMap","params":extraInfo}
            return

        self.assignQuestToNumNPCs(character, questType, extraInfo["numNPCs"], params)

src.items.addType(OrderArtwork)
