import src

class SwarmIntegrator(src.items.Item):
    type = "SwarmIntegrator"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.floor_node)
        self.name = "swarm integrator"
        self.walkable = False
        self.faction = "swarm"

    def getLongInfo(self):
        return """
item: SwarmIntegrator

description:
You can use it to create paths
"""

    def apply(self,character):
        command = "aopR.$a*13.$w*13.$s*13.$d*13.$=aa$=ww$=ss$=dd"
        convertedCommand = []
        for item in command:
            convertedCommand.append((item,["norecord"]))

        
        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

src.items.addType(SwarmIntegrator)
