import src
import pytest

src.canvas.displayChars = src.canvas.DisplayMapping("pureASCII")
src.interaction.urwid = src.pseudoUrwid
src.gamestate.gamestate = src.gamestate.GameState(11)

def test_dutyhangup_painting_no_painter(character_room):
    (character,room) = character_room

    beUsefull = src.quests.questMap["BeUsefull"]()
    character.duties.append("painting")
    character.assignQuest(beUsefull)

    character.runCommandString("*")

    # let the memory build up a bit first
    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

