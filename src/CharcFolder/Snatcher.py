import src
from src.CharcFolder.Monster import Monster


class Snatcher(Monster):
    def __init__(self,):
        super().__init__(name= "Snatcher")

        self.movementSpeed = 1
        self.solvers = []
        self.specialDisplay = "sn"
        self.baseDamage = 8
        self.maxHealth = 15
        self.health = self.maxHealth

        self.charType = "Snatcher"

src.characters.add_character(Snatcher)
