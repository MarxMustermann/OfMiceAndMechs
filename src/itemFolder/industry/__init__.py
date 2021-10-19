"""
import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__("src.itemFolder.industry." + module[:-3], locals(), globals())
del module
"""

import src.itemFolder.industry.bluePrinter
import src.itemFolder.industry.boiler
import src.itemFolder.industry.itemDowngrader
import src.itemFolder.industry.machineMachine
import src.itemFolder.industry.pavingGenerator
import src.itemFolder.industry.roomBuilder
import src.itemFolder.industry.scraper
import src.itemFolder.industry.bluePrint
import src.itemFolder.industry.furnace
import src.itemFolder.industry.itemCollector
import src.itemFolder.industry.itemUpgrader
import src.itemFolder.industry.machine
import src.itemFolder.industry.scrapCompactor

