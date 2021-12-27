"""
import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__("src.itemFolder.functional." + module[:-3], locals(), globals())
del module
"""

import src.itemFolder.functional.autoScribe
import src.itemFolder.functional.growthTank
import src.itemFolder.functional.map
import src.itemFolder.functional.markerBean
import src.itemFolder.functional.note
import src.itemFolder.functional.roomControls
import src.itemFolder.functional.stasisTank
import src.itemFolder.functional.suicideBooth
import src.itemFolder.functional.corpseAnimator
import src.itemFolder.functional.painter
