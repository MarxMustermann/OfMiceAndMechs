import src

def test_creation():
    #src.canvas.displayChars = src.canvas.DisplayMapping("pureASCII")
    #src.interaction.urwid = src.pseudoUrwid
    #src.gamestate.gamestate = src.gamestate.GameState(11)

    for itemType in src.items.itemMap.values():
        if itemType.isAbstract:
            continue
        item = itemType()
