"""
import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__("src.itemFolder.manager." + module[:-3], locals(), globals())
del module
"""

import src.itemFolder.manager.architectArtwork
import src.itemFolder.manager.cityBuilder
import src.itemFolder.manager.miningManager
import src.itemFolder.manager.productionManager
import src.itemFolder.manager.roadManager
import src.itemFolder.manager.roomManager
import src.itemFolder.manager.stockpileMetaManager

