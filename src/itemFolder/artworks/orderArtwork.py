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
        self.description = """
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This item allows to issue quest to groups of clones in this base."""
        self.usageInfo = """
Activate the item to use it.
Use the map view to assign quests related to a room or tile.
Skip the map view to assign quests that do not relate to a room or tile.

The issued quest will be added at the front of the clones quest queue.
So they will start to run it as soon as their command queue is empty.
That should usually be around 10-20 ticks."""

    def apply(self,character):
        if not character.rank < 4:
            character.addMessage("you need to have rank 3 to use this machine")
            return
        super().apply(character)

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
            options.append(("rank 3","rank 3 NPCs"))
            options.append(("rank 4","rank 4 NPCs"))
            options.append(("rank 5","rank 5 NPCs"))
            options.append(("rank 6","rank 6 NPCs"))
            options.append(("rank 5-6","rank 5-6 NPCs"))
            options.append(("non staff rank 6","non staff rank 6 NPCs"))
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
                options.append(("ClearTerrain","clear terrain"))
            else:
                options.append(("restockRoom","restock"))
            options.append(("BeUsefull","be usefull"))
            options.append(("cancel","cancel current quest"))
            options.append(("cancelAll","cancel all quests"))
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

        mode = extraInfo["groupType"]

        def checkAdd(person):
            if person.faction != character.faction:
                return
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
            if mode == "rank 3" and person.rank == 3:
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
            if mode == "non staff rank 6" and (person.isStaff == False and person.rank == 6):
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

        terrain = self.getTerrain()
        for char in terrain.characters:
            checkAdd(char)
        for room in terrain.rooms:
            for char in room.characters:
                checkAdd(char)

        random.shuffle(targets)

        counter = 0
        extraInfo["amount"] = int(extraInfo["amount"])
        for target in targets:
            if extraInfo["amount"] != 0 and not extraInfo["amount"] > counter:
                break
            if extraInfo["questType"] == "cancel":
                if target.quests:
                    target.quests.remove(target.quests[0])
                continue
            if extraInfo["questType"] == "cancelAll":
                target.quests = []
                continue
            if extraInfo["questType"] == "shelter":
                quest = src.quests.questMap["WaitQuest"]()
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
            target.quests.insert(0,quest)
            quest.assignToCharacter(target)
            quest.activate()
            counter += 1

    def showMap(self, character):
        # render empty map
        mapContent = []
        for x in range(0, 15):
            mapContent.append([])
            for y in range(0, 15):
                if x not in (0, 14) and y not in (0, 14):
                    char = "  "
                elif x != 7 and y != 7:
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

                functionMap[(x,y)]["q"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"amount":0},
                        },
                        "description":"assign quest with that tile as a target",
                    }
                functionMap[(x,y)]["u"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"amount":0,"questType":"BeUsefull"},
                        },
                        "description":"send npcs to work on that tile",
                    }
                functionMap[(x,y)]["m"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"amount":0,"questType":"SecureTile"},
                        },
                        "description":"send npcs to guard tile",
                    }
                functionMap[(x,y)]["v"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"amount":0,"questType":"GoToTile"},
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

                functionMap[(x,y)]["c"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"amount":0,"questType":"ClearTile"},
                        },
                        "description":"send npcs to clear that tile",
                    }

                functionMap[(x,y)]["t"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"amount":0,"questType":"ReloadTraproom"},
                        },
                        "description":"send npcs to reload traps on that tile",
                    }

                functionMap[(x,y)]["Q"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character},
                        },
                        "description":"assign quest with that tile as a target (specific number)",
                    }
                functionMap[(x,y)]["U"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"questType":"BeUsefull"},
                        },
                        "description":"send npcs to work on that tile (specific number)",
                    }
                functionMap[(x,y)]["M"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"questType":"SecureTile"},
                        },
                        "description":"send npcs to guard tile (specific number)",
                    }
                functionMap[(x,y)]["V"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"questType":"GoToTile"},
                        },
                        "description":"send npcs to that tile (specific number)",
                    }
                functionMap[(x,y)]["C"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"questType":"ClearTile"},
                        },
                        "description":"send npcs to clear that tile",
                    }
                functionMap[(x,y)]["T"] = {
                        "function": {
                            "container":self,
                            "method":"questFromMap",
                            "params":{"character":character,"questType":"ReloadTraproom"},
                        },
                        "description":"send npcs to reload traps on that tile",
                    }

        plot = (self.container.xPosition,self.container.yPosition)
        mapContent[plot[1]][plot[0]] = "CB"

        extraText = "\n\n"

        self.submenue = src.interaction.MapMenu(mapContent=mapContent,functionMap=functionMap, extraText=extraText, cursor=character.getBigPosition())
        character.macroState["submenue"] = self.submenue

    def fetchCityleader(self):
        cityBuilder = None
        for item in self.container.itemsOnFloor:
            if item.type != "PersonnelArtwork":
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
            text += f"{key}: {value}\n"
        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

    def assignQuestToNumNPCs(self, character, questType, numNPCs, params=None):
        if params == None:
            params = {}

        numQuestsAssigned = 0

        # assign to idle NPCs
        if numQuestsAssigned < numNPCs:
            numQuestsAssigned += 1
            quest = src.quests.questMap[questType]()
            quest.setParameters(params)
            quest.assignToCharacter(cityLeader)
            quest.activate()
            cityLeader.quests.insert(0,quest)

    def guardTileFromMap(self, extraInfo):
        pass

    def questFromMap(self, extraInfo):
        self.assignQuest(extraInfo)

    def beusefulFromMap(self, extraInfo):
        extraInfo["questType"] = "BeUsefull"
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
