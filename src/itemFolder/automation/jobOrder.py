import src
import json


class JobOrder(src.items.Item):
    """
    ingame object that stores information about a task to be done and can be run by characters
    this is used to orchestrate running longer tasks
    """

    type = "JobOrder"

    def __init__(self, autoRun=True):
        """
        configuring the super class
        """

        self.tasks = []

        super().__init__(display=src.canvas.displayChars.jobOrder)

        self.name = "job order"
        self.description = "Stores the information that something should be done"

        self.bolted = False
        self.walkable = True
        self.done = False
        self.autoRun = autoRun
        self.information = {}
        self.error = {}
        self.taskName = ""

        self.attributesToStore.extend(
            [
                "done",
                "information",
                "taskName",
                "autoRun",
                "tasks",
            ]
        )

        # set up interaction menu
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

    def getTask(self):
        """
        fetch current task

        Returns:
            the task
        """

        if self.tasks:
            return self.tasks[-1]
        else:
            return None

    def popTask(self):
        """
        fetches and removes current task

        Returns:
            the task
        """

        if self.tasks:
            return self.tasks.pop()
        else:
            return None

    def showInfo(self, character):
        """
        show information about the job orders state
        Parameters:
            character: the character to show the information to
        """

        # format the tasks
        taskStr = ""
        for task in self.tasks:
            taskStr += "%s \n" % (task,)

        # spawn the submenu showing the information
        submenue = src.interaction.TextMenu(
            """
taskName:
%s

information:
%s

error:
%s

tasks:
%s
"""
            % (
                self.taskName,
                self.information,
                self.error,
                taskStr,
            )
        )
        character.macroState["submenue"] = submenue

    def addBreakPoint(self, character):
        """
        add a breakpoint to the job order
        the joborder should stop running when reaching the breakpoint
        this is intended to allow debugging

        Parameters:
            character: the character to set the breakpoint
        """

        options = []

        index = 0
        for task in self.tasks:
            options.append((index, task["task"]))
            index += 1

        self.submenue = src.interaction.SelectionMenu(
            "On what task do you want to set the breakpoint?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doAddBreakPoint
        self.character = character

    def doAddBreakPoint(self):
        if self.submenue.selection is None:
            return
        self.character.addMessage("breakpoint set")
        self.tasks[self.submenue.selection]["breakPoint"] = True

    def runSingleStep(self, character):
        """
        runs a single task from a job order
        Parameters:
            character: the character to run the task on
        """

        self.runJobOrder(character, True)

    def runJobOrder(self, character, singleStep=False):
        """
        runs all or a single task from a job order
        Parameters:
            character: the character to run the task on
            singleStep: flag indicating that only a singestep should be run
        """

        command = ""
        task = self.getTask()
        if not task:
            character.addMessage("no task left")
            return

        if task.get("breakPoint"):
            character.addMessage("triggered breakpoint")
            character.addMessage(character.getCommandString())
            character.clearCommandString()
            del task["breakPoint"]
            return

        if task.get("command"):
            command = self.tasks[-1]["command"]
            self.popTask()

        if self.autoRun and not singleStep:
            nextTask = self.getTask()
            character.runCommandString("Jj.j")
        character.runCommandString(command)

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the text
        """

        text = super().getLongInfo()
        text += """

information:
%s

the order is:

tasks: %s
done: %s

""" % (
            self.information,
            json.dumps(list(reversed(self.tasks)), indent=4),
            self.done,
        )
        return text

    def addTasks(self,tasks):
        self.tasks = list(reversed(tasks))


src.items.addType(JobOrder)
