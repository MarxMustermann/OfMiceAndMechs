import random

import src


class MiningManager(src.items.Item):
    """
    ingame item managing the the operation of a mine
    """

    type = "MiningManager"

    def __init__(self):
        """
        call superclass constructor with modified parameters
        """

        super().__init__(display="MM")

        self.name = "mining manager"
        self.runsJobOrders = True

    def apply(self, character):
        """
        handle a character trying to use this item
        by offering a selection of possible actions

        Parameters:
            character: the character trying to use the machine
        """

        options = [
            ("do maintenace", "do maintenace"),
            ("mine", "mine"),
            ("metal bars", "metal bars"),
            ("spawn npc", "spawn npc"),
            ("loop", "start joborder loop"),
        ]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        """
        handle a character having selected a action to do
        by running the action
        """

        character = self.character

        selection = self.submenue.selection
        if selection == "loop":
            self.useJoborderRelayToLocalRoom(
                character,
                [
                    {"task":"add job order"}
                ]
                , "JobBoard"
                )
            targetJobOrder = src.items.itemMap["JobOrder"]()
            tasks = [
                        {
                            "task": "insert job order",
                            "command": "scj",
                        },
                        {
                            "task": "run command",
                            "command": None,
                            "toRun":"go to room manager",
                        },
                        {
                            "task": "insert job order",
                            "command": "scj",
                        },
                        {
                            "task": "go to item",
                            "command": None,
                            "item": "MiningManager",
                        },
                        {
                            "task": "do maintenace",
                            "command": "Js.j",
                        },
                        {
                            "task": "continue loop",
                            "command": "Js.wj",
                        },
                        {
                            "task": "insert job order",
                            "command": "scj",
                        },
                        {
                            "task": "run command",
                            "command": None,
                            "toRun":"go to room manager",
                        },
                        {
                            "task": "insert job order",
                            "command": "scj",
                        },
                        {
                            "task": "go to item",
                            "command": None,
                            "item": "JobBoard",
                        },
                    ]
            targetJobOrder.addTasks(tasks)
            character.addToInventory(targetJobOrder)

        if selection == "spawn npc":
            character = src.characters.Character(name="mining npc")
            character.godMode = True
            character.xPosition = self.xPosition
            character.yPosition = self.yPosition - 1
            self.container.addCharacter(character, self.xPosition, self.yPosition - 1)
            character.macroState["macros"] = {
                "a": ["J", "s", ".", "j", "_", "a"],
            }
            character.runCommandString("_a")
        if selection == "do maintenace":
            selection = random.choice(
                [
                    "metal bars",
                    "mine",
                ]
            )
        if selection == "metal bars":
            jobOrder = src.items.itemMap["JobOrder"]()
            jobOrder.tasks = list(
                reversed(
                    [
                        {
                            "task": "go to room manager",
                            "command": self.commands["go to room manager"],
                        },
                        {
                            "task": "go to mine",
                            "command": self.commands["pathToMine"],
                        },
                        {
                            "task": "go to ore processing",
                            "command": self.commands["pathToOreProcessing"],
                        },
                        {
                            "task": "process ore",
                            "command": "Js.sjj",
                        },
                        {
                            "task": "return from ore proessing",
                            "command": self.commands["pathFromOreProcessing"],
                        },
                        {
                            "task": "return from mine",
                            "command": self.commands["pathFromMine"],
                        },
                        {
                            "task": "return from room manager",
                            "command": self.commands["return from room manager"],
                        },
                    ]
                )
            )
            jobOrder.taskName = "install city builder"

            character.addMessage("running job order to add local room task")
            character.jobOrders.append(jobOrder)
            character.runCommandString("Jj.j")
        if selection == "mine":
            jobOrder = src.items.itemMap["JobOrder"]()
            jobOrder.tasks = list(
                reversed(
                    [
                        {
                            "task": "go to room manager",
                            "command": self.commands["go to room manager"],
                        },
                        {
                            "task": "go to mine",
                            "command": self.commands["pathToMine"],
                        },
                        {
                            "task": "go to mining spot",
                            "command": self.commands["pathToMiningspot"],
                        },
                        {
                            "task": "mine",
                            "command": "11j",
                        },
                        {
                            "task": "return from mining spot",
                            "command": self.commands["pathFromMiningspot"],
                        },
                        {
                            "task": "return from mine",
                            "command": self.commands["pathFromMine"],
                        },
                        {
                            "task": "return from room manager",
                            "command": self.commands["return from room manager"],
                        },
                    ]
                )
            )
            jobOrder.taskName = "install city builder"

            character.addMessage("running job order to add local room task")
            character.jobOrders.append(jobOrder)
            character.runCommandString("Jj.j")

    def getJobOrderTriggers(self):
        """
        register handlers for tasks run via job order
        """

        result = super().getJobOrderTriggers()
        self.addTriggerToTriggerMap(result, "set up", self.doSetUp)
        return result

    def doSetUp(self, task, context):
        """
        handle the task of setting up something

        Parameters:
            task: details about this task
            context: context about this task
        """

        setupInfo = task["setupInfo"]

        jobOrder = context["jobOrder"]
        if not jobOrder.information.get("pathTo"):
            tasks = [
                {
                    "task": "go to room manager",
                    "command": self.commands["go to room manager"],
                },
                {"task": "insert job order", "command": "scj"},
                {
                    "task": "relay job order",
                    "command": None,
                    "ItemType": "RoadManager",
                },
                {
                    "task": "print paths",
                    "command": None,
                    "to": setupInfo["scrapStockPileCoordinate"],
                },
                {
                    "task": "return from room manager",
                    "command": self.commands["return from room manager"],
                },
                {"task": "reactivate", "command": "scj"},
                task,
            ]
            jobOrder.tasks.extend(list(reversed(tasks)))
            context["character"].runCommandString("Jj.j")
            return

        self.commands["pathToMine"] = jobOrder.information.get("pathTo")
        self.commands["pathFromMine"] = jobOrder.information.get("pathFrom")

        terrain = self.getTerrain()

        # mockup for ore processing
        item = src.items.itemMap["ProductionManager"]()

        command = ""
        commandTo = ""
        commandBack = ""
        if setupInfo["scrapStockPileCoordinate"][0] == setupInfo["miningSpot"][0][0]:
            if setupInfo["scrapStockPileCoordinate"][1] < setupInfo["miningSpot"][0][1]:
                commandTo = "dssa12s"
                commandBack = "12wdwwa"
            else:
                commandTo = "12w"
                commandBack = "12s"
        else:
            if setupInfo["scrapStockPileCoordinate"][0] < setupInfo["miningSpot"][0][0]:
                commandTo = "ds12d"
                commandBack = "12awa"
            else:
                commandTo = "as12a"
                commandBack = "12dwd"

        self.commands["pathToMiningspot"] = commandTo
        self.commands["pathFromMiningspot"] = commandBack
        scrapSource = commandTo + "11j" + commandBack + "Js.sj"

        command += commandTo + "Js.sj" * 10 + commandBack
        command += "5w6aslsslsslssslsslsslw3dslwwl7wlwwlw3d5s"
        doStr = "JsdKsa"
        command += (
            "5waa"
            + doStr
            + "3a"
            + doStr
            + "5dssaa"
            + doStr
            + "3a"
            + doStr
            + "5dss5a"
            + doStr
            + "5dsass4a"
            + doStr
            + "5dssaa"
            + doStr
            + "3a"
            + doStr
            + "5dssaa"
            + doStr
            + "3a"
            + doStr
            + "5d4wawwd"
        )

        command = ""
        commandTo = ""
        commandBack = ""
        if setupInfo["oreProcessing"][0] == setupInfo["scrapStockPileCoordinate"][0]:
            if setupInfo["oreProcessing"][1] < setupInfo["scrapStockPileCoordinate"][1]:
                commandTo = "dssa11s"
                commandBack = "11wdwwa"
            else:
                commandTo = "11wdwwa"
                commandBack = "dssa11s"
        else:
            if setupInfo["oreProcessing"][0] < setupInfo["scrapStockPileCoordinate"][0]:
                commandTo = "ds11dwd"
                commandBack = "as11awa"
            else:
                commandTo = "as11awa"
                commandBack = "ds11dwd"

        self.commands["pathToOreProcessing"] = commandBack
        self.commands["pathFromOreProcessing"] = commandTo

        command += commandTo + "Js.sj" * 10 + commandBack
        command += "5w6aslsslsslssslsslsslw3dslwwl7wlwwlw3d5s"
        doStr = "JsdKsaaKsd"
        command += (
            "5waa"
            + doStr
            + "3a"
            + doStr
            + "5dssaa"
            + doStr
            + "3a"
            + doStr
            + "5dss5a"
            + doStr
            + "5dsass4a"
            + doStr
            + "5dssaa"
            + doStr
            + "3a"
            + doStr
            + "5dssaa"
            + doStr
            + "3a"
            + doStr
            + "5d4wawwd"
        )

        commandTo = ""
        commandBack = ""
        if setupInfo["oreProcessing"][0] == setupInfo["metalBarStockPileCoordinate"][0]:
            if (
                setupInfo["oreProcessing"][1]
                < setupInfo["metalBarStockPileCoordinate"][1]
            ):
                commandTo = "dssa11s"
                commandBack = "11wdwwa"
            else:
                commandTo = "11wdwwa"
                commandBack = "dssa11s"
        else:
            if (
                setupInfo["oreProcessing"][0]
                < setupInfo["metalBarStockPileCoordinate"][0]
            ):
                commandTo = "ds11dwd"
                commandBack = "as11awa"
            else:
                commandTo = "as11awa"
                commandBack = "ds11dwd"
        command += commandTo + "Js.j" * 10 + commandBack
        metalBarSource = commandBack + "Js.sjj" + commandTo

        item.commands["MetalBars"] = command
        terrain.addItem(
            item,
            (
                setupInfo["oreProcessing"][0] * 15 + 7,
                setupInfo["oreProcessing"][1] * 15 + 7,
                0,
            ),
        )

        self.useJoborderRelayToLocalRoom(
            context["character"],
            [
                {
                    "task": "connect stockpile",
                    "type": "set wrong item to storage",
                    "stockPile": setupInfo["scrapStockPileName"],
                    "stockPileCoordinate": setupInfo["scrapStockPileCoordinate"],
                    "command": None,
                },
                {
                    "task": "connect stockpile",
                    "type": "set wrong item to storage",
                    "stockPile": setupInfo["metalBarStockPileName"],
                    "stockPileCoordinate": setupInfo["metalBarStockPileCoordinate"],
                    "command": None,
                },
                {
                    "task": "connect stockpile",
                    "type": "set source",
                    "sourceCommand": scrapSource,
                    "stockPile": setupInfo["scrapStockPileName"],
                    "stockPileCoordinate": setupInfo["scrapStockPileCoordinate"],
                },
                {
                    "task": "connect stockpile",
                    "type": "set source",
                    "sourceCommand": metalBarSource,
                    "stockPile": setupInfo["metalBarStockPileName"],
                    "stockPileCoordinate": setupInfo["metalBarStockPileCoordinate"],
                },
            ],
            "ArchitectArtwork",
        )

    def getLongInfo(self):
        """
        get longer than normal description text

        Returns:
            the description text
        """

        text = f"""
commands:
{self.commands}

"""
        return text


src.items.addType(MiningManager)
