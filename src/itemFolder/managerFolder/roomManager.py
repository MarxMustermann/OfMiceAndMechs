import src

import random

class RoomManager(src.items.ItemNew):
    type = "RoomManager"

    def __init__(self,xPosition=0,yPosition=0,name="RoomManager",creator=None,noId=False):
        super().__init__("##",xPosition,yPosition,name=name,creator=creator)
        self.reset()

    def reset(self):
        self.itemSlotUsage = {}
        self.freeItemSlots = [[2,2],[2,4],[4,2],[4,4],[8,2],[10,2],[8,4],[10,4],[8,8],[10,8],[8,10],[10,10],[2,8],[4,8],[2,10],[4,10]]

        import random
        random.shuffle(self.freeItemSlots)

        self.tasks = [
                {"task":"add CityBuilder"},
                ]

        self.stuck = False
        self.stuckReason = None

        self.machineMachinePos = None
        self.bluePrintingArtworkPos = None
        self.cityBuilderPos = None
        self.resourceTerminalPositions = {}
        self.machinePositions = {}
        self.itemPositions = {}
        self.dependencies = {}
        self.itemPositions = {}
        self.roomName = None
        self.managerName = "comandCenter"

        self.attributesToStore.extend([
               "cityBuilderPos","machineMachinePos","bluePrintingArtworkPos","tasks","managerName","roomName",
               "resourceTerminalPositions","stuck","stuckReason","machinePositions","freeItemSlots",
               ])

        self.tupleDictsToStore.extend([
               "itemSlotUsage","dependencies",
               ])

    def generatePathFromTo(self,start,end):
        path = ""
        path += "a"*(start[0]-6)+"d"*(6-start[0])
        if start[1]>6 and end[1]<6:
            path += "w"*(start[1]-7)
            path += "awwd"
            path += "w"*(5-end[1])
        elif start[1]<6 and end[1]>6:
            path += "s"*(5-(start[1]))
            path += "assd"
            path += "s"*(end[1]-7)
        else:
            path += "w"*(start[1]-end[1])+"s"*(end[1]-start[1])
        path += "a"*(6-end[0])+"d"*(end[0]-6)
        return path

    def characterDropMachine(self,character,itemSlot):
        characterPos = [character.xPosition,character.yPosition]
        itemSlot = itemSlot[:]
        itemSlot[1] -= 1
        command = ""
        command += self.generatePathFromTo(characterPos,itemSlot)
        command += "Ls"
        command += self.generatePathFromTo(itemSlot,characterPos)
        character.runCommandString(command)

    def apply(self,character):
        options = [("doMaintance","do maintanance"),("do action","do action"),("addTask","add task"),("clearTasks","clear tasks")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def addTask(self):
        if self.tasksType == None:
            self.tasksType = self.submenue.selection

            if self.tasksType in ("add machine","add item","add resource terminal"):
                self.submenue = src.interaction.InputMenu("item type")
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.addTask
                return

        typeParameter = None
        if self.tasksType in ("add machine","add item","add resource terminal"):
            typeParameter = self.submenue.text

        if self.tasksType == "add item":
            if not typeParameter in src.items.itemMap:
                self.character.addMessage("item not found")
                return

        newTask = {
                    "task":self.tasksType,
                }

        if not typeParameter == None:
            newTask["type"] = typeParameter

        self.tasks.append(newTask)
        self.stuck = False
        self.stuckReason = None
        self.dependencies = {}

        del self.tasksType 

    def doAction(self):
        if self.submenue.selection == "storeItem":
            jobOrder = src.items.itemMap["JobOrder"]()
            jobOrder.taskName = "add item to storage"

            itemSlot = random.choice(self.itemPositions["StockpileMetaManager"])

            newTasks = [
                    {"task":"go to item","command":self.generatePathFromTo([self.character.xPosition,self.character.yPosition],[itemSlot[0],itemSlot[1]-1])},
                    {"task":"insert job order","command":"scj"},
                    {"task":"store item","command":None},
                    {"task":"go back","command":self.generatePathFromTo([itemSlot[0],itemSlot[1]-1],[self.character.xPosition,self.character.yPosition])},
                ]
            jobOrder.tasks.extend(list(reversed(newTasks)))
            self.character.addJobOrder(jobOrder)

        self.character.addMessage("unkown action")

    def apply2(self):
        if self.submenue.selection == "clearTasks":
            self.tasks = []
        if self.submenue.selection == "addTask":
            options = [("add item","add item"),("add machine","add machine"),("add resource terminal","add resource terminal"),("add machine machine","add machine machine"),("add CityBuilder","add CityBuilder"),("clear all","clear all"),("clear item slot","clear item slot")]
            self.submenue = src.interaction.SelectionMenu("what task do you want to add?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addTask
            self.tasksType = None
        if self.submenue.selection == "do action":
            options = [("storeItem","add item to storage"),]
            self.submenue = src.interaction.SelectionMenu("what action do you want to do?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.doAction
            self.actionType = None
        if self.submenue.selection == "doMaintance":
            character = self.character
            if self.stuck:
                character.addMessage("machine is stuck and doesn't respond. reason: %s"%(self.stuckReason))
                return
            if not self.tasks:
                if self.cityBuilderPos:
                    character.runCommandString("Js.j")
                    command = ""
                    command += self.generatePathFromTo([character.xPosition,character.yPosition],[self.cityBuilderPos[0],self.cityBuilderPos[1]-1])
                    command += "scm"
                    command += self.generatePathFromTo([self.cityBuilderPos[0],self.cityBuilderPos[1]-1],[character.xPosition,character.yPosition])
                    character.runCommandString(command)
                    return
                else:
                    character.addMessage("no tasks")
                    return

            self.character.runCommandString("Js.j")

            task = self.tasks.pop()

            if task["task"] in ("add machine machine","add resource terminal","add machine","add item","add BluePrintingArtwork","add CityBuilder"):
                if not self.freeItemSlots:
                    self.tasks.append(task)
                    character.addMessage("no item slots left")
                    #if self.room.xPosition == 7 and self.room.yPosition == 7 and not self.cityBuilderPos:
                    if not self.cityBuilderPos and 1==0:
                        newTask = {"task":"add CityBuilder task","payload":["setup"]}
                        self.tasks.append(newTask)
                        newTask = {"task":"add CityBuilder"}
                        self.tasks.append(newTask)
                        newTask = {"task":"clear item slot"}
                        self.tasks.append(newTask)
                    elif 1==1:
                        newTask = {"task":"clear item slot"}
                        self.tasks.append(newTask)
                    else:
                        self.stuckReason = "no item slots left"
                        self.stuck = True
                    return
                itemSlot = self.freeItemSlots.pop()

            import random

            character.addMessage(task)
            if task["task"] == "add item":
                if not task["type"] in src.items.itemMap:
                    character.addMessage("item not found")
                    return
                item = src.items.itemMap[task["type"]]()

                character.inventory.append(item)

                jobOrder = src.items.itemMap["JobOrder"]()
                tasks = []
                tasks.extend([
                    {
                        "task":"go to dropoff position",
                        "command":self.generatePathFromTo([character.xPosition,character.yPosition],[itemSlot[0],itemSlot[1]-1]),
                    },
                    {
                        "task":"dropoff machine",
                        "command":"Ls",
                    }])
                if task["type"] in ("MiningManager","StockpileMetaManager","ArchitectArtwork","RoadManager",):
                    commands = {}
                    commands["go to room manager"] = self.generatePathFromTo([itemSlot[0],itemSlot[1]-1],[character.xPosition,character.yPosition])
                    commands["return from room manager"] = self.generatePathFromTo([character.xPosition,character.yPosition],[itemSlot[0],itemSlot[1]-1])

                    configureTask = {
                            "task":"configure machine",
                            "command":None,
                            "commands": commands,
                            "managerName":self.managerName,
                        }

                    tasks.extend([
                        {
                            "task":"insert job order",
                            "command":"scj",
                        },
                        configureTask,
                        ])
                tasks.extend([
                    {
                        "task":"return to start position",
                        "command":self.generatePathFromTo([itemSlot[0],itemSlot[1]-1],[character.xPosition,character.yPosition]),
                    }])
                jobOrder.tasks = list(reversed(tasks))
                jobOrder.taskName = "add item to room"
                character.jobOrders.append(jobOrder)

                character.runCommandString("Jj.j")

                self.itemSlotUsage[tuple(itemSlot)] = task
                if not task["type"] in self.itemPositions:
                    self.itemPositions[task["type"]] = []
                self.itemPositions[task["type"]].append(itemSlot)

            if task["task"] == "clear item slot":
                foundSlot = None
                itemSlots = random.choice(list(self.itemSlotUsage.keys()))
                for itemSlot in itemSlots:
                    itemSlot = list(random.choice(list(self.itemSlotUsage.keys())))
                    originalTask = self.itemSlotUsage[tuple(itemSlot)]
                    if originalTask["task"] == "add machine":
                        foundSlot = itemSlot
                        break

                if not foundSlot:
                    character.addMessage("no slot found")
                    return

                toRemove = [foundSlot]
                while toRemove:
                    removeSlot = toRemove.pop()
                    if tuple(removeSlot) in self.dependencies:
                        toRemove.extend(self.dependencies[tuple(removeSlot)])
                        del self.dependencies[tuple(removeSlot)]

                    for dependencyList in self.dependencies.values():
                        if removeSlot in dependencyList:
                            dependencyList.remove(removeSlot)

                    if not tuple(removeSlot) in self.itemSlotUsage:
                        continue

                    originalTask = self.itemSlotUsage[tuple(removeSlot)]
                    if originalTask["task"] == "add machine":
                        self.machinePositions[originalTask["type"]].remove(removeSlot)
                        if not self.machinePositions[originalTask["type"]]:
                            del self.machinePositions[originalTask["type"]]

                    self.room.clearCoordinate(removeSlot)
                    self.freeItemSlots.append(removeSlot)
                    del self.itemSlotUsage[tuple(removeSlot)]
                return

            if task["task"] == "clear all":
                toRemove = []
                for item in self.room.itemsOnFloor:
                    if item == self:
                        continue
                    if item.xPosition in (0,12):
                        continue
                    if item.yPosition in (0,12):
                        continue
                    toRemove.append(item)
                self.room.removeItems(toRemove)
                self.reset()

            if task["task"] == "add CityBuilder":
                machine = src.items.itemMap["CityBuilder"]()
                if not self.cityBuilderPos:
                    self.cityBuilderPos = itemSlot
                character.inventory.append(machine)
                self.characterDropMachine(character,itemSlot)
                self.itemSlotUsage[tuple(itemSlot)] = task
                if not self.roomName:
                    self.roomName = "CityBuilderRoom_"+self.id

                commands = {}
                commands["go to room manager"] = self.generatePathFromTo([self.cityBuilderPos[0],self.cityBuilderPos[1]-1],[character.xPosition,character.yPosition])
                commands["return from room manager"] = self.generatePathFromTo([character.xPosition,character.yPosition],[self.cityBuilderPos[0],self.cityBuilderPos[1]-1])

                jobOrder = src.items.itemMap["JobOrder"]()
                jobOrder.tasks = list(reversed([
                    {
                        "task":"go to dropoff position",
                        "command":self.generatePathFromTo([character.xPosition,character.yPosition],[self.cityBuilderPos[0],self.cityBuilderPos[1]-1]),
                    },
                    {
                        "task":"dropoff machine",
                        "command":"Ls",
                    },
                    {
                        "task":"insert job order",
                        "command":"scj",
                    },
                    {
                        "task":"configure machine",
                        "command":None,
                        "commands": commands
                    },
                    {
                        "task":"return to start position",
                        "command":self.generatePathFromTo([self.cityBuilderPos[0],self.cityBuilderPos[1]-1],[character.xPosition,character.yPosition]),
                    },
                    ]))
                jobOrder.taskName = "install city builder"

                self.character.addMessage("running job order to install machine")
                self.character.jobOrders.append(jobOrder)
                self.character.runCommandString("Jj.j")

            if task["task"] == "add BluePrintingArtwork":
                machine = src.items.BluePrintingArtwork()
                if not self.bluePrintingArtworkPos:
                    self.bluePrintingArtworkPos = itemSlot
                character.inventory.append(machine)
                self.characterDropMachine(character,itemSlot)
                self.itemSlotUsage[tuple(itemSlot)] = task
            if task["task"] == "add machine machine":
                if not self.bluePrintingArtworkPos:
                    self.tasks.append(task)
                    self.freeItemSlots.append(itemSlot)
                    newTask = {"task":"add BluePrintingArtwork"}
                    self.tasks.append(newTask)
                    return
                if not self.resourceTerminalPositions.get("MetalBars"):
                    self.tasks.append(task)
                    self.freeItemSlots.append(itemSlot)
                    newTask = {"task":"add resource terminal","type":"MetalBars"}
                    self.tasks.append(newTask)
                    return

                machine = src.items.MachineMachine(None,None)
                self.machineMachinePos = itemSlot

                character.inventory.append(machine)
                self.characterDropMachine(character,itemSlot)
                self.itemSlotUsage[tuple(itemSlot)] = task

            if task["task"] == "add resource terminal":
                machine = src.items.ResourceTerminal(itemSlot[0],itemSlot[1])
                machine.balance = 1000
                machine.resource = task["type"]
                if not "MetalBars" in self.resourceTerminalPositions:
                    self.resourceTerminalPositions["MetalBars"] = []
                self.resourceTerminalPositions["MetalBars"].append(itemSlot)

                character.inventory.append(machine)
                self.characterDropMachine(character,itemSlot)
                self.itemSlotUsage[tuple(itemSlot)] = task

            if task["task"] == "add machine":

                if not self.machineMachinePos:
                    self.tasks.append(task)
                    self.freeItemSlots.append(itemSlot)
                    newTask = {"task":"add machine machine"}
                    self.tasks.append(newTask)
                    return

                needResources = src.items.rawMaterialLookup[task["type"]]

                missingResource = None
                needsMetalbars = False
                for resource in needResources:
                    if not resource in self.machinePositions:
                        if resource == "MetalBars":
                            needsMetalbars = True
                            continue
                        missingResource = resource
                        break

                if missingResource:
                    self.tasks.append(task)
                    self.freeItemSlots.append(itemSlot)
                    newTask = {"task":"add machine","type":missingResource}
                    self.tasks.append(newTask)
                    return

                if needsMetalbars and not self.resourceTerminalPositions.get("MetalBars"):
                    self.tasks.append(task)
                    self.freeItemSlots.append(itemSlot)
                    newTask = {"task":"add resource terminal","type":"MetalBars"}
                    self.tasks.append(newTask)
                    return

                for resource in needResources:
                    if resource == "MetalBars":
                        if self.resourceTerminalPositions.get(resource):
                            candidateList = self.resourceTerminalPositions[resource]
                        else:
                            candidateList = []
                    else:
                        if resource in self.machinePositions:
                            candidateList = self.machinePositions[resource]
                        else:
                            candidateList = []

                    for candidate in candidateList:
                        desiredPos = candidate[:]
                        desiredPos[0] += 2

                        if desiredPos in self.freeItemSlots:
                            self.freeItemSlots.append(itemSlot)
                            itemSlot = desiredPos
                            self.freeItemSlots.remove(itemSlot)

                commands ={}
                commands["cooldown"] = "20.Js"

                itemCount = 0
                for resource in needResources:
                    if resource == "MetalBars":
                        if self.resourceTerminalPositions.get("MetalBars"):
                            resourceTerminalPos = random.choice(self.resourceTerminalPositions.get("MetalBars"))
                            command = ""
                            command += self.generatePathFromTo([itemSlot[0],itemSlot[1]-1],[resourceTerminalPos[0],resourceTerminalPos[1]-1])
                            command += "Js.ssj"
                            command += self.generatePathFromTo([resourceTerminalPos[0],resourceTerminalPos[1]-1],[itemSlot[0],itemSlot[1]-1])
                            if itemCount == 0:
                                command += "aLsdJs"
                            else:
                                command += "lJs"
                            commands["material MetalBars"] = command
                            if not tuple(resourceTerminalPos) in self.dependencies:
                                self.dependencies[tuple(resourceTerminalPos)] = []
                            self.dependencies[tuple(resourceTerminalPos)].append(itemSlot)
                    else:
                        if resource in self.machinePositions:
                            targetPos = random.choice(self.machinePositions[resource])
                            command = ""
                            command += self.generatePathFromTo([itemSlot[0],itemSlot[1]-1], [targetPos[0],targetPos[1]-1])
                            command += "JsdKsa"
                            command += self.generatePathFromTo([targetPos[0],targetPos[1]-1],[itemSlot[0],itemSlot[1]-1])
                            if itemCount == 0:
                                command += "aLsdJs"
                            else:
                                command += "lJs"
                            commands["material "+resource] = command

                            if not tuple(targetPos) in self.dependencies:
                                self.dependencies[tuple(targetPos)] = []
                            self.dependencies[tuple(targetPos)].append(itemSlot)
                    itemCount += 1

                character.inventory = []

                resourceTerminalPos = random.choice(self.resourceTerminalPositions.get("MetalBars"))
                jobOrder = src.items.itemMap["JobOrder"]()
                jobOrder.tasks = list(reversed([
                    {
                        "task":"go to blueprinting artwork",
                        "command":self.generatePathFromTo([character.xPosition,character.yPosition], [self.bluePrintingArtworkPos[0],self.bluePrintingArtworkPos[1]-1])
                    },
                    {
                        "task":"produce blueprint",
                        "command":list("Js"+task["type"])+["enter"]+list("dKsa")
                    },
                    {
                        "task":"go to resource terminal",
                        "command":self.generatePathFromTo([self.bluePrintingArtworkPos[0],self.bluePrintingArtworkPos[1]-1],[resourceTerminalPos[0],resourceTerminalPos[1]-1])
                    },
                    {
                        "task":"fetch metal bars",
                        "command":"Js.ssj",
                    },
                    {
                        "task":"go to machine machine",
                        "command":self.generatePathFromTo([resourceTerminalPos[0],resourceTerminalPos[1]-1],[self.machineMachinePos[0],self.machineMachinePos[1]-1]),
                    },
                    {
                        "task":"load blueprint",
                        "command":"aLsdil"+"s"*len(character.inventory)+"jJs.j",
                    },
                    {
                        "task":"run job order",
                        "command":"scj",
                    },
                    {
                        "task":"produce machine",
                        "command":None,
                        "type":task["type"],
                    },
                    {
                        "task":"pick up machine",
                        "command":"dKsa",
                    },
                    {
                        "task":"go to dropoff position",
                        "command":self.generatePathFromTo([self.machineMachinePos[0],self.machineMachinePos[1]-1],[6,5])+self.generatePathFromTo([6,5],[itemSlot[0],itemSlot[1]-1]),
                    },
                    {
                        "task":"dropoff machine",
                        "command":"Ls",
                    },
                    {
                        "task":"insert job order",
                        "command":"scj",
                    },
                    {
                        "task":"configure machine",
                        "command":None,
                        "commands": commands
                    },
                    {
                        "task":"go to resource terminal",
                        "command":self.generatePathFromTo([itemSlot[0],itemSlot[1]-1],[resourceTerminalPos[0],resourceTerminalPos[1]-1])
                    },
                    {
                        "task":"return metal bars",
                        "command":"Js.sj",
                    },
                    {
                        "task":"return to start position",
                        "command":self.generatePathFromTo([resourceTerminalPos[0],resourceTerminalPos[1]-1],[character.xPosition,character.yPosition]),
                    },
                    ]))
                jobOrder.taskName = "drop machine"

                newTask = {"task":"test machine","itemSlot":itemSlot}
                self.tasks.append(newTask)

                self.character.addMessage("running job order to install machine")
                self.character.jobOrders.append(jobOrder)
                self.character.runCommandString("Jj.j")

                if not task["type"] in self.machinePositions:
                    self.machinePositions[task["type"]] = []
                self.machinePositions[task["type"]].append(itemSlot)

                self.itemSlotUsage[tuple(itemSlot)] = task

            if task["task"] == "test machine":
                itemSlot = task["itemSlot"]

                jobOrder = src.items.itemMap["JobOrder"]()
                jobOrder.tasks = list(reversed([
                    {
                        "task":"go to machine",
                        "command":self.generatePathFromTo([character.xPosition,character.yPosition],[itemSlot[0],itemSlot[1]-1])
                    },
                    {
                        "task":"produce item",
                        "command":"JsdKsa",
                    },
                    {
                        "task":"produce item",
                        "command":"JsdKsa",
                    },
                    {
                        "task":"return to start position",
                        "command":self.generatePathFromTo([itemSlot[0],itemSlot[1]-1],[character.xPosition,character.yPosition]),
                    },
                    ]))
                jobOrder.taskName = "test machine"

                self.character.addMessage("running job order to test machine")
                #self.character.jobOrders.append(jobOrder)
                self.character.runCommandString("Jj.j")
            if task["task"] == "produce":
                targetSlot = random.choice(self.machinePositions[task["type"]])
                resourceTerminalPos = random.choice(self.resourceTerminalPositions.get("MetalBars"))
                command = ""
                command += self.generatePathFromTo([character.xPosition,character.yPosition], [targetSlot[0],targetSlot[1]-1])
                command += "JsdKsa"
                command += self.generatePathFromTo([targetSlot[0],targetSlot[1]-1], [character.xPosition,character.yPosition])
                command += self.generatePathFromTo([character.xPosition,character.yPosition],[resourceTerminalPos[0],resourceTerminalPos[1]-1])
                command += "Js.sj"
                command += self.generatePathFromTo([resourceTerminalPos[0],resourceTerminalPos[1]-1],[character.xPosition,character.yPosition])

                character.runCommandString(command)

    def fetchSpecialRegisterInformation(self):
        result = super().fetchSpecialRegisterInformation()

        result["free item slots"] = self.freeItemSlots
        result["num free item slots"] = len(self.freeItemSlots)
        result["stuck"] = self.stuck
        result["stuckReason"] = self.stuckReason
        result["city builder position"] = self.cityBuilderPos
        result["machine machine position"] = self.machineMachinePos
        result["blue printing artwork position"] = self.bluePrintingArtworkPos
        result["resource terminal positions"] = self.resourceTerminalPositions
        result["machine positions"] = self.machinePositions
        
        return result

    def configure(self,character):

        self.lastAction = "configure"

        self.submenue = src.interaction.OneKeystrokeMenu("""
a: addCommand
s: machine settings
j: run job order
r: reset
""")
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        self.lastAction = "configure2"

        if self.submenue.keyPressed == "j":
            if not self.character.jobOrders:
                self.character.addMessage("no job order")
                self.blocked = False
                return
            jobOrder = self.character.jobOrders[-1]
            task = jobOrder.popTask()
            if not task:
                self.character.addMessage("no tasks left")
                return

            if task["task"] == "add Tasks":
                self.tasks.extend(task["tasks"])

            if task["task"] == "relay job order":
                relayedTask = jobOrder.popTask()
                
                if not task["ItemType"] in self.itemPositions and not task["ItemType"] == "CityBuilder":
                    jobOrder.error = {"message":"tried to relay task, but item %s was not found"%task["ItemType"],"itemType":task["ItemType"],"task":task,"type":"item not found"}
                    self.character.addMessage("no such item found")
                    return
                
                if task["ItemType"] == "CityBuilder":
                    itemSlot = self.cityBuilderPos
                else:
                    import random
                    itemSlot = random.choice(self.itemPositions[task["ItemType"]])
                
                newTasks = [
                        {"task":"go to item","command":self.generatePathFromTo([self.character.xPosition,self.character.yPosition],[itemSlot[0],itemSlot[1]-1])},
                        {"task":"insert job order","command":"scj"},
                        relayedTask,
                        {"task":"go back","command":self.generatePathFromTo([itemSlot[0],itemSlot[1]-1],[self.character.xPosition,self.character.yPosition])},
                        ]
                jobOrder.tasks.extend(list(reversed(newTasks)))
            self.blocked = False
            return

        
    def getLongInfo(self):
        text = """

dependencies:
%s

itemSlotUsage:
%s

machines:

"""%(self.dependencies,self.itemSlotUsage,)
        for (key,value) in self.machinePositions.items():
            text += "\n%s: %s"%(key,value,)

        text += """

tasks:
"""

        for task in self.tasks:
            text += "%s \n"%(task,)
        text += """

commands:
%s

"""%(self.commands,)
        return text
