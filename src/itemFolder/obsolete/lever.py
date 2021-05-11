import src

'''
item for letting characters trigger something
'''
class Lever(src.items.Item):
    type = "Lever"

    '''
    straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="lever",activated=False,creator=None,noId=False):
        self.activated = activated
        super().__init__(src.canvas.displayChars.lever_notPulled,xPosition,yPosition,name=name,creator=creator)
        self.activateAction = None
        self.deactivateAction = None
        self.walkable = True
        self.bolted = True

        # set metadata for saving
        self.attributesToStore.extend([
               "activated"])

    '''
    pull the lever!
    bad code: activate/deactive methods would be nice
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        if not self.activated:
            # activate the lever
            self.activated = True

            # run the action
            if self.activateAction:
                self.activateAction(self)
        else:
            # deactivate the lever
            self.activated = False

            # run the action
            if self.deactivateAction:
                self.activateAction(self)

        # notify listeners
        self.changed()

    '''
    render the lever
    '''
    @property
    def display(self):
        if self.activated:
            return src.canvas.displayChars.lever_pulled
        else:
            return src.canvas.displayChars.lever_notPulled

    def getLongInfo(self):
        text = """
item: Lever

description:
A lever. It is not useful.

"""
        return text

src.items.addType(Lever)
