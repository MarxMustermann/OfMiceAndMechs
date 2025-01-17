import src

def test_creation():
    src.canvas.displayChars = src.canvas.DisplayMapping("pureASCII")
    src.interaction.urwid = src.pseudoUrwid
    src.gamestate.gamestate = src.gamestate.GameState(11)

    for characterType in src.characters.characterMap.values():
        character = characterType()
