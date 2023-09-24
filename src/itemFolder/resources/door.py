import src


class Door(src.items.Item):
    """
    a door for opening/closing and locking people in/out
    """

    type = "Door"
    name = "door"
    walkable = False
    description = "Used to enter and leave rooms."

    def __init__(self, bio=False):
        """
        set up initial state

        Parameters:
            bio: whether this item is grown or manmade
        """

        super().__init__()
        self.bio = bio

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted and self.walkable:
            options["x"] = ("block door", self.blockDoor)
        else:
            options["x"] = ("unblock door", self.unblockDoor)
        return options

    def blockDoor(self,character):
        self.walkable = False

    def unblockDoor(self,character):
        self.walkable = True

    def render(self):
        """
        render depending on state

        Returns:
            what the item should look like
        """

        if self.bio:
            if self.walkable:
                displayChar = src.canvas.displayChars.bioDoor_opened
            else:
                displayChar = src.canvas.displayChars.bioDoor_closed
        else:
            if self.walkable:
                displayChar = src.canvas.displayChars.door_opened
            else:
                displayChar = src.canvas.displayChars.door_closed
        return displayChar

    def gatherApplyActions(self, character):
        """
        handle a character trying to use this item, by
        add open or close action depending on state

        Parameters:
            character: the character trying to use this item
        """
        applyActions = super().gatherApplyActions()
        if self.walkable:
            applyActions.append(self.close)
        else:
            applyActions.append(self.open)
        return applyActions

    def open(self, character):
        """
        open door

        Parameters:
            character: the character opening the door
        """

        if not isinstance(self.container, src.rooms.Room):
            if character:
                character.addMessage("you can only use doors within rooms")
            return

        # open the door
        self.walkable = True

    def close(self, character=None):
        """
        close the door

        Parameters:
            character: the character closing the door
        """
        return

        self.walkable = False


src.items.addType(Door)
