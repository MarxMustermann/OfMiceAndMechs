import src

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
                        ("addCommand","add command"),
                        ("addJobOrder","add job order"),
                ])
        self.applyMap = {
                            "doMaintenance":self.doMaintenance,
                            "addCommand":self.addCommand,
                            "addJobOrder":self.addJobOrder,
                        }

    def addCommand(self,character):
        """
        create a job order from a command
        Paramerters:
            character: the character trying to set the command
        """
        pass

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

        Paramerters:
            character: the character dooing maintenance
        """

        if not self.todo:
            character.addMessage("no job order on job board")
        else:
            character.addJobOrder(self.todo.pop())
            character.addMessage("you take a job order from the job board")

src.items.addType(JobBoard)
