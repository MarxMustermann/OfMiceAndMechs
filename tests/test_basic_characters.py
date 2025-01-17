import src

def test_creation():
    src.canvas.displayChars = src.canvas.DisplayMapping("pureASCII")
    src.interaction.urwid = src.pseudoUrwid
    src.gamestate.gamestate = src.gamestate.GameState(11)

    for characterType in src.characters.characterMap.values():
        character = characterType()

def test_movement():
    room = src.rooms.EmptyRoom()
    character = src.characters.characterMap["Clone"]()
    room.addCharacter(character,2,2)
    assert character.xPosition == 2
    assert character.yPosition == 2
    character.timeTaken = 0
    character.runCommandString("d")
    character.advance(advanceMacros=True)
    assert character.xPosition == 3
    assert character.yPosition == 2
    character.timeTaken = 0
    character.runCommandString("s")
    character.advance(advanceMacros=True)
    assert character.xPosition == 3
    assert character.yPosition == 3
    character.timeTaken = 0
    character.runCommandString("a")
    character.advance(advanceMacros=True)
    assert character.xPosition == 2
    assert character.yPosition == 3
    character.timeTaken = 0
    character.runCommandString("w")
    character.advance(advanceMacros=True)
    assert character.xPosition == 2
    assert character.yPosition == 2
