import src


# NIY: not really implemented yet
class SwarmIntegrator(src.items.Item):
    """
    item intended for collecting creatures to add to a mold civilisation
    """

    type = "SwarmIntegrator"
    name = "swarm integrator"
    walkable = False
    faction = "swarm"

    def __init__(self):
        """
        set up initial state
        """

        super().__init__(display=src.canvas.displayChars.floor_node)

    def apply(self, character):
        """
        handle a character trying to use this item

        Parameters:
            character: the character trying to use this item
        """

        command = "aopR.$a*13.$w*13.$s*13.$d*13.$=aa$=ww$=ss$=dd"
        character.runCommandString(command)

src.items.addType(SwarmIntegrator)
