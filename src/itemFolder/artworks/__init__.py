"""
import os

for module in os.listdir(os.path.dirname(__file__)):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__("src.itemFolder.artworks." + module[:-3], locals(), globals())
del module
"""

import src.itemFolder.artworks.blueBrintingArtwork
import src.itemFolder.artworks.gooFaucet
import src.itemFolder.artworks.productionArtwork
import src.itemFolder.artworks.questArtwork
import src.itemFolder.artworks.resourceTerminal
import src.itemFolder.artworks.tradingArtwork
