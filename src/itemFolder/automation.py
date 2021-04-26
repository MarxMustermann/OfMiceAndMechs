import src

class JobOrder(src.items.ItemNew):
    type = "JobOrder"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="job order",creator=None,noId=False,autoRun=True):
        self.tasks = [
                ]

        super().__init__(src.canvas.displayChars.jobOrder,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.done = False
        self.autoRun = autoRun
        self.information = {}
        self.taskName = ""

        self.attributesToStore.extend([
                "done","information","taskName","autoRun"])

    def getLongInfo(self):
        import json
        text = """
item: JobOrder

description:
Stores the information that something should be done, without describing how it should be done.

$s

the order is:

tasks: %s
done: %s

"""%(self.information, json.dumps(list(reversed(self.tasks)),indent=4), self.done)
        return text

    def apply(self,character):
        options = [("runJobOrder","run job order macro"),("runSingleStep","run single step"),("configureJobOrder","configure job order"),("setCommand","set command"),("showInfo","show info")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def getTask(self):
        if self.tasks:
            return self.tasks[-1]
        else:
            return None

    def popTask(self):
        if self.tasks:
            return self.tasks.pop()
        else:
            return None

    def apply2(self):
        if self.submenue.selection == "showInfo":

            taskStr = ""
            for task in self.tasks:
                taskStr += "%s \n"%(task,)
            submenue = src.interaction.TextMenu("""
information:
%s

tasks:
%s
"""%(self.information,taskStr,))
            self.character.macroState["submenue"] = submenue
            return
            
        if self.submenue.selection in ("runJobOrder","runSingleStep"):
            command = ""
            task = self.getTask()
            if not task:
                self.character.addMessage("no task left")
                return

            if task.get("command"):
                command = self.tasks[-1]["command"]
                self.popTask()
            elif task["task"] == "produce":
                if "PRODUCe" in self.character.macroState["macros"]:
                    command = "_PRODUCe"
                else:
                    if not self.tasks[-1]["macro"] in self.character.macroState["macros"]:
                        self.character.addMessage("no solver found - record solver to %s"%(self.tasks[-1]["macro"]))
                        return
                    command = "_"+self.tasks[-1]["macro"]
            elif task["task"] == "place":
                if not "PLACe" in self.character.macroState["macros"]:
                    self.character.addMessage("no solver found - record solver to %s"%("PLACe"))
                    return
                command = "_PLACe"

                if not "PLACE x" in self.character.registers:
                    self.character.registers["PLACE x"] = []
                self.character.registers["PLACE x"][-1] = self.tasks[-1]["placeX"]
                if not "PLACE y" in self.character.registers:
                    self.character.registers["PLACE y"] = []
                self.character.registers["PLACE y"][-1] = self.tasks[-1]["placeY"]
                if not "PLACE BIG x" in self.character.registers:
                    self.character.registers["PLACE BIG x"] = []
                self.character.registers["PLACE BIG x"][-1] = self.tasks[-1]["placeBigX"]
                if not "PLACE BIG y" in self.character.registers:
                    self.character.registers["PLACE BIG y"] = []
                self.character.registers["PLACE BIG y"][-1] = self.tasks[-1]["placeBigY"]
            else:
                self.popTask()
                self.character.addMessage("unknown task")

            if self.autoRun and not self.submenue.selection == "runSingleStep":
                self.character.runCommandString("Jj.j")
            self.character.runCommandString(command)
        elif self.submenue.selection == "configureJobOrder":
            options = []
            for key in src.items.itemMap.keys():
                options.append((key,key))
            self.submenue = src.interaction.SelectionMenu("what should be produced?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.configureJobOrder2
        elif self.submenue.selection == "setCommand":
            if not "a" in self.character.macroState["macros"]:
                return
            self.tasks[-1]["command"] = self.character.macroState["macros"]["a"]
            self.tasks[-1]["macro"] = None

    def configureJobOrder2(self):
        self.tasks[-1]["toProduce"] = self.submenue.selection
        if not self.tasks[-1]["command"]:
            self.tasks[-1]["macro"] = "PRODUCE "+self.tasks[-1]["toProduce"].upper()[:-1]+self.tasks[-1]["toProduce"][-1].lower()

    def fetchSpecialRegisterInformation(self):
        result = {}

        return result

    def getState(self):
        state = super().getState()
        state["tasks"] = self.tasks
        return state

    def setState(self,state):
        super().setState(state)
        if "tasks" in state:
            self.tasks = state["tasks"]

