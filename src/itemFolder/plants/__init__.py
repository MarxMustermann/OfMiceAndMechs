"""
import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__("src.itemFolder.plants." + module[:-3], locals(), globals())
del module
"""

import src.itemFolder.plants.bloom
import src.itemFolder.plants.commandBloom
import src.itemFolder.plants.encrustedPoisonBush
import src.itemFolder.plants.moldSpore
import src.itemFolder.plants.poisonBush
import src.itemFolder.plants.sickBloom
import src.itemFolder.plants.sprout
import src.itemFolder.plants.tree
import src.itemFolder.plants.bush
import src.itemFolder.plants.encrustedBush
import src.itemFolder.plants.hiveMind
import src.itemFolder.plants.mold
import src.itemFolder.plants.poisonBloom
import src.itemFolder.plants.sprout2
import src.itemFolder.plants.swarmIntegrator
