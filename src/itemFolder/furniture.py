import src

'''
a door for opening/closing and locking people in/out
# bad code: should use a rendering method
'''
class Door(src.items.ItemNew):
    type = "Door"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Door",creator=None,noId=False,bio=False):
        if bio:
            displayChar = src.canvas.displayChars.bioDoor_closed
        else:
            displayChar = src.canvas.displayChars.door_closed

        super().__init__(displayChar,xPosition,yPosition,name=name,creator=creator)
        self.walkable = False
        self.bio = bio

        # bad code: set metadata for saving
        self.attributesToStore.extend([
               "bio","walkable","type"])
        self.description = "Used to enter and leave rooms."

    '''
    set state from dict
    bad code: should have a open attribute
    '''
    def setState(self,state):
        super().setState(state)
        if self.walkable:
            self.open(None)

    def gatherApplyActions(self,character):
        applyActions = super().gatherApplyActions()
        if self.walkable:
            applyActions.append(self.close)
        else:
            applyActions.append(self.open)
        return applyActions

    '''
    open door
    '''
    def open(self,character):
        if not isinstance(self.container,src.rooms.Room):
            if character:
                character.addMessage("you can only use doors within rooms")
            return

        # open the door
        self.walkable = True
        if self.bio:
            self.display = src.canvas.displayChars.bioDoor_opened
        else:
            self.display = src.canvas.displayChars.door_opened
        self.room.open = True

    '''
    close the door
    '''
    def close(self,character=None):
        self.walkable = False
        if self.bio:
            self.display = src.canvas.displayChars.bioDoor_closed
        else:
            self.display = src.canvas.displayChars.door_closed
        if self.room:
            self.room.open = False
            self.room.forceRedraw()

'''
basic item with different appearance
'''
class Wall(src.items.ItemNew):
    type = "Wall"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Wall",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.wall,xPosition,yPosition,name=name,creator=creator)
        self.description = "Used to build rooms."

