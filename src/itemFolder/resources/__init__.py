"""
import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__("src.itemFolder.resources." + module[:-3], locals(), globals())
del module
"""

import src.itemFolder.resources.bolt
import src.itemFolder.resources.case
import src.itemFolder.resources.coal
import src.itemFolder.resources.connector
import src.itemFolder.resources.corpse
import src.itemFolder.resources.door
import src.itemFolder.resources.explosive
import src.itemFolder.resources.fireCrystals
import src.itemFolder.resources.floorPlate
import src.itemFolder.resources.frame
import src.itemFolder.resources.heater
import src.itemFolder.resources.memoryCell
import src.itemFolder.resources.metalbars
import src.itemFolder.resources.mount
import src.itemFolder.resources.paving
import src.itemFolder.resources.pocketFrame
import src.itemFolder.resources.puller
import src.itemFolder.resources.pusher
import src.itemFolder.resources.radiator
import src.itemFolder.resources.rod
import src.itemFolder.resources.puller
import src.itemFolder.resources.pusher
import src.itemFolder.resources.radiator
import src.itemFolder.resources.scrap
import src.itemFolder.resources.sheet
import src.itemFolder.resources.stripe
import src.itemFolder.resources.tank
import src.itemFolder.resources.token
import src.itemFolder.resources.wall
import src.itemFolder.resources.crystalCompressor
import src.itemFolder.resources.glassCrystal
