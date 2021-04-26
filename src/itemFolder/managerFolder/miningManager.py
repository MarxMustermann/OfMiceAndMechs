import src

'''
'''
class MiningManager(src.items.ItemNew):
    type = "MiningManager"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="mining manager",creator=None,noId=False):
        super().__init__("MM",xPosition,yPosition,name=name,creator=creator,runsJobOrders=True)

        self.fittedScrapfields = []

    def apply(self,character):
        action = "10j"
        if not self.fittedScrapfields:
            self.fittedScrapfields.append("")
            item = src.items.itemMap["ItemCollector"]()
            character.addToInventory(item)
            action = "l"

        jobOrder = src.items.itemMap["JobOrder"]()
        jobOrder.tasks = list(reversed([
            {
                "task":"go to room manager",
                "command":self.commands["go to room manager"]
            },
            {
                "task":"do mining",
                "command":"as14a"+action+"13dwd",
            },
            {
                "task":"insert job orderg",
                "command":"scj",
            },
            {
                "task":"relay job order",
                "command":None,
                "type":"Item",
                "ItemType":"StockpileMetaManager",
            },
            {
                "task":"clear inventory",
                "command":None,
            },
            {
                "task":"return from room manager",
                "command":self.commands["return from room manager"]
            },
            ]))
        jobOrder.taskName = "install city builder"

        character.addMessage("running job order to add local room task")
        character.jobOrders.append(jobOrder)
        character.runCommandString("Jj.j")



