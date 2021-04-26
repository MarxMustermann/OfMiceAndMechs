import src

class TestItem(src.items.Item):
    type = "TestItem"

    '''   
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="test item",creator=None,noId=False):
        super().__init__("ti",xPosition,yPosition,name=name,creator=creator)
