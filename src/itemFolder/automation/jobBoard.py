import src

# bug!: doesn't save todos
class JobBoard(src.items.Item):
    """
    ingame object to hold tasks and distribute tasks to characters
    """

    type = "JobBoard"
    def __init__(self):
        '''
        basic superclass configuration
        '''

        super().__init__(display=src.canvas.displayChars.jobBoard)

        self.name = "job board"
        self.description = "Stores a collection of job orders. Serving as a todo list."

        self.todo = [] #bug: saving is broken

        self.bolted = False
        self.walkable = False

        # set up interaction menu
        self.applyOptions.extend([
                        ("doMaintenance","do a job order"),
                        ("addComand","add comand"),
                        ("addJobOrder","add job order"),
                ])
        self.applyMap = {
                            "doMaintenance":self.doMaintenance,
                            "addComand":self.addComand,
                            "addJobOrder":self.addJobOrder,
                        }

    def addComand(self,character):
        """
        create a job order from a comand
        Paramerters:
            character: the character trying to set the comand
        """
        
        # fetch comand
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
        jobOrder.tasks = [{"task":"run comand","command":comand.command}]
        
        # add to todo list
        self.todo.append(jobOrder)
        character.addMessage("copied comand to job order and added it")

    def addJobOrder(self,character):
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

    def doMaintenance(self,character):
        """
        do a maintenance job by running a job order from the todo list

        Parameters:
            character: the character dooing maintenance
        """

        if not self.todo:
            character.addMessage("no job order on job board")
        else:
            character.addJobOrder(self.todo.pop())
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
"""%(self.todo)
        return text


src.items.addType(JobBoard)
