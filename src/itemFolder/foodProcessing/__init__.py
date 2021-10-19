"""
import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__("src.itemFolder.foodProcessing." + module[:-3], locals(), globals())
del module
"""

import src.itemFolder.foodProcessing.autoFarmer
import src.itemFolder.foodProcessing.bioPress
import src.itemFolder.foodProcessing.bloomShredder
import src.itemFolder.foodProcessing.gooDispenser
import src.itemFolder.foodProcessing.gooProducer
import src.itemFolder.foodProcessing.maggotFermenter
import src.itemFolder.foodProcessing.pressCake
import src.itemFolder.foodProcessing.seededMoldFeed
import src.itemFolder.foodProcessing.vatMaggot
import src.itemFolder.foodProcessing.bioMass
import src.itemFolder.foodProcessing.bloomContainer
import src.itemFolder.foodProcessing.corpseShredder
import src.itemFolder.foodProcessing.gooflask
import src.itemFolder.foodProcessing.moldFeed
import src.itemFolder.foodProcessing.sporeExtractor
