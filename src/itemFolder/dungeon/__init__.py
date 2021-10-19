"""
import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__("src.itemFolder.dungeon." + module[:-3], locals(), globals())
del module
"""

import src.itemFolder.dungeon.acidBladder
import src.itemFolder.dungeon.sacrificialCircle
import src.itemFolder.dungeon.sparkPlug
import src.itemFolder.dungeon.staticCrystal
import src.itemFolder.dungeon.staticSpark
import src.itemFolder.dungeon.ripInReality
import src.itemFolder.dungeon.sparcRewardLock
import src.itemFolder.dungeon.spiderNet
import src.itemFolder.dungeon.staticMover
import src.itemFolder.dungeon.staticWall
