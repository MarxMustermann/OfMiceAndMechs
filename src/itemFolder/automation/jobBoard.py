import src


class JobBoard(src.items.Item):
    """
    ingame object to hold tasks and distribute tasks to characters
    """

    type = "JobBoard"

    def __init__(self):
        """
        basic superclass configuration
        """

        super().__init__(display=src.canvas.displayChars.jobBoard)

        self.name = "job board"
        self.description = "Stores a collection of job orders. Serving as a todo list."

        self.todo = []  # bug: saving is broken

        self.bolted = False
        self.walkable = False

        self.runsJobOrders = True

        # set up interaction menu
        self.applyOptions.extend(
            [
                ("doMaintenance", "do a job order"),
                ("addComand", "add comand"),
                ("addJobOrder", "add job order"),
                ("spawnNpc", "spawn npc"),
            ]
        )
        self.applyMap = {
            "doMaintenance": self.doMaintenance,
            "addComand": self.addComand,
            "addJobOrder": self.addJobOrder,
            "spawnNpc": self.spawnNpc,
        }

    def getJobOrderTriggers(self):
        """
        register handlers for handling job order tasks

        Returns:
            a dict of lists containing the handlers
        """

        result = super().getJobOrderTriggers()
        self.addTriggerToTriggerMap(result, "add job order", self.jobOrderAddJobOrder)
        return result


    def spawnNpc(self, character):
        npc = src.characters.Character(name="Hooper")
        npc.godMode = True
        self.container.addCharacter(npc,self.xPosition,self.yPosition-1)
        npc.macroState["macros"] = {
            "a": list("Js.j_a")
        }
        npc.runCommandString("_a")

    def addComand(self, character):
        """
        create a job order from a comand
        Parameters:
            character: the character trying to set the comand
        """

        # fetch command
        comands = character.searchInventory("Command")
        if not comands:
            character.addMessage("no comand found")
            return
        comand = comands[0]

        # create new job order
        jobOrder = src.items.itemMap["JobOrder"]()
        jobOrder.taskName = "run comand"

        # add tasks
        comandName = comand.name
        if not comandName:
            comandName = "run comand"
        jobOrder.tasks = [{"task": "run comand", "command": comand.command}]

        # add to todo list
        self.todo.append(jobOrder)
        character.addMessage("copied comand to job order and added it")

    def jobOrderAddJobOrder(self, task, context):
        self.addJobOrder(context["character"])

    def addJobOrder(self, character):
        """
        add a job order
        the intention is for the jobOrder to be run by someone else later

        Paramerters:
            character: the character trying to set the command
        """

        # search the characters inventory for the job order to insert
        foundItems = character.searchInventory("JobOrder")
        if not foundItems:
            character.addMessage("no job order found")
            return
        itemFound = foundItems[0]

        # remove completed job orders
        if itemFound.done:
            character.inventory.remove(itemFound)
            return

        # remove completed job orders
        self.todo.append(itemFound)
        character.removeItemFromInventory(itemFound)
        character.addMessage("job order added")

    def doMaintenance(self, character):
        """
        do a maintenance job by running a job order from the todo list

        Parameters:
            character: the character dooing maintenance
        """

        if not self.todo:
            character.addMessage("no job order on job board")
        else:
            import random
            jobOrder = random.choice(self.todo)
            self.todo.remove(jobOrder)
            character.addJobOrder(jobOrder)
            character.addMessage("you take a job order from the job board")

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the text
        """

        text = super().getLongInfo()
        text += """

todo:
%s
""" % (
            self.todo
        )
        return text

    def getState(self):
        """
        save state and special handle stored job orders

        Returns:
            the state as dictionary
        """
        state = super().getState()

        state["todo"] = []
        for jobOrder in self.todo:
            state["todo"].append(jobOrder.getState())

        return state

    def setState(self, state):
        """
        load state and special handle stored job orders

        Parameters:
            state: the state to load
        """
        super().setState(state)

        if "todo" in state:
            for jobOrderState in state["todo"]:
                jobOrder = src.items.getItemFromState(jobOrderState)
                self.todo.append(jobOrder)


src.items.addType(JobBoard)
