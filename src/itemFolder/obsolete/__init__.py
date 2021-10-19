"""
import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__("src.itemFolder.obsolete." + module[:-3], locals(), globals())
del module
"""

import src.itemFolder.obsolete.acid
import src.itemFolder.obsolete.Chute
import src.itemFolder.obsolete.drill
import src.itemFolder.obsolete.hutch
import src.itemFolder.obsolete.memoryBank
import src.itemFolder.obsolete.objectDispenser
import src.itemFolder.obsolete.spawner
import src.itemFolder.obsolete.transportInNode
import src.itemFolder.obsolete.winch
import src.itemFolder.obsolete.backTracker
import src.itemFolder.obsolete.coalMine
import src.itemFolder.obsolete.engraver
import src.itemFolder.obsolete.memoryDump
import src.itemFolder.obsolete.pile
import src.itemFolder.obsolete.reactionChamber2
import src.itemFolder.obsolete.spray
import src.itemFolder.obsolete.transportOutNode
import src.itemFolder.obsolete.chain
import src.itemFolder.obsolete.commandBook
import src.itemFolder.obsolete.gameTestingProducer
import src.itemFolder.obsolete.lever
import src.itemFolder.obsolete.memoryReset
import src.itemFolder.obsolete.pipe
import src.itemFolder.obsolete.reactionChamber
import src.itemFolder.obsolete.trailHead
import src.itemFolder.obsolete.tumbler
import src.itemFolder.obsolete.chemical
import src.itemFolder.obsolete.commLink
import src.itemFolder.obsolete.globalMacroStorage
import src.itemFolder.obsolete.macroRunner
import src.itemFolder.obsolete.memoryStack
import src.itemFolder.obsolete.positioningDevice
import src.itemFolder.obsolete.simpleRunner
import src.itemFolder.obsolete.transportContainer
import src.itemFolder.obsolete.watch
