"""
import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__("src.itemFolder.story." + module[:-3], locals(), globals())
del module
"""

import src.itemFolder.story.autoTutor
import src.itemFolder.story.brokenCityCore
import src.itemFolder.story.portableChallenger
import src.itemFolder.story.reserveCityBuilder
import src.itemFolder.story.specialItem
import src.itemFolder.story.specialItemSlot
import src.itemFolder.story.sunScreen
import src.itemFolder.story.waterCondenser
import src.itemFolder.story.waterPump

