import src

'''
marker ment to be placed by characters and to control actions with
'''
class MarkerBean(src.items.Item):
    type = "MarkerBean"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="bean",creator=None,noId=False):
        self.activated = False
        super().__init__(src.canvas.displayChars.markerBean_inactive,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False

        # set up meta information for saveing
        self.attributesToStore.extend([
               "activated"])

    '''
    render the marker
    '''
    @property
    def display(self):
        if self.activated:
            return src.canvas.displayChars.markerBean_active
        else:
            return src.canvas.displayChars.markerBean_inactive

    '''
    activate marker
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        character.addMessage(character.name+" activates a marker bean")
        self.activated = True

    def getLongInfo(self):
        text = """
item: MarkerBean

description:
A marker been. It can be used to mark things.

"""
        return text

src.items.addType(MarkerBean)
