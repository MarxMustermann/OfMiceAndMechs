import src

'''
steam sprayer used as a prop in the vat
'''
class Spray(src.items.Item):
    type = "Spray"

    '''
    call superclass constructor with modified parameters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="spray",direction=None,creator=None,noId=False):
        # skin acording to spray direction
        if direction == None:
            direction = "left"

        self.direction = direction

        super().__init__(src.canvas.displayChars.spray_left_inactive,xPosition,yPosition,name=name,creator=creator)

        # set up meta information for saveing
        self.attributesToStore.extend([
               "direction"])

    '''
    set appearance depending on energy supply
    bad code: energy supply is directly taken from the machine room
    '''
    @property
    def display(self):
        if self.direction == "left":
            if self.terrain.tutorialMachineRoom.steamGeneration == 0:
                return src.canvas.displayChars.spray_left_inactive
            elif self.terrain.tutorialMachineRoom.steamGeneration == 1:
                return src.canvas.displayChars.spray_left_stage1
            elif self.terrain.tutorialMachineRoom.steamGeneration == 2:
                return src.canvas.displayChars.spray_left_stage2
            elif self.terrain.tutorialMachineRoom.steamGeneration == 3:
                return src.canvas.displayChars.spray_left_stage3
        else:
            if self.terrain.tutorialMachineRoom.steamGeneration == 0:
                return src.canvas.displayChars.spray_right_inactive
            elif self.terrain.tutorialMachineRoom.steamGeneration == 1:
                return src.canvas.displayChars.spray_right_stage1
            elif self.terrain.tutorialMachineRoom.steamGeneration == 2:
                return src.canvas.displayChars.spray_right_stage2
            elif self.terrain.tutorialMachineRoom.steamGeneration == 3:
                return src.canvas.displayChars.spray_right_stage3

    def getLongInfo(self):
        text = """
item: Boiler

description:
a boiler can be heated by a furnace to produce steam. Steam is the basis for energy generation.

"""
        return text

src.items.addType(Spray)
