import src

class JobBoard(src.items.Item):
    type = "JobBoard"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self):
        super().__init__(display=src.canvas.displayChars.jobBoard)

        self.name = "job board"

        self.todo = []

        self.bolted = False
        self.walkable = False

    def getLongInfo(self):
        text = """
item: JobBoard

description:
Stores a collection of job board. Serving as a todo list.

"""
        return text

    def apply(self,character):
        options = [("addCommand","add command"),("addJobOrder","add job order"),("getSolvableJobOrder","get solvable job order"),("getJobOrder","get job order")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if self.submenue.selection == "addJobOrder":
            itemFound = None
            for item in self.character.inventory:
                if item.type == "JobOrder":
                    itemFound = item
                    break

            if not itemFound:
                self.character.addMessage("no job order found")
                return

            if itemFound.done:
                self.character.inventory.remove(itemFound)
                return

            self.todo.append(itemFound)
            self.character.inventory.remove(itemFound)
            self.character.addMessage("job order added")
        elif self.submenue.selection == "getSolvableJobOrder":

            if len(self.character.inventory) > 9:
                self.character.addMessage("no space in inventory")
                return

            itemFound = None
            for jobOrder in self.todo:
                if jobOrder.macro in self.character.macroState["macros"]:
                   itemFound = jobOrder
                   break

            if not itemFound:
                self.character.addMessage("no fitting job order found")
                return

            self.todo.remove(jobOrder)
            self.character.inventory.append(jobOrder)
            self.character.addMessage("you take a job order")

        elif self.submenue.selection == "getJobOrder":
            if not self.todo:
                self.character.addMessage("no job order on job board")
            elif len(self.character.inventory) > 9:
                self.character.addMessage("inventory not empty")
            else:
                self.character.inventory.append(self.todo.pop())
                self.character.addMessage("you take a job order from the job board")
        else:
            self.character.addMessage("noption not found")

src.items.addType(JobBoard)
