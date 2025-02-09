import src
import pytest

src.canvas.displayChars = src.canvas.DisplayMapping("pureASCII")
src.interaction.urwid = src.pseudoUrwid
src.gamestate.gamestate = src.gamestate.GameState(11)

def test_movement_working_GoToPosition(terrain,character):

    bigPos = (6,10,0)

    terrain.addCharacter(character,bigPos[0]*15+3,bigPos[1]*15+7)

    assert character.getBigPosition() == bigPos
    assert character.getSpacePosition() == (3,7,0)

    quest = src.quests.questMap["GoToPosition"](targetPosition=(7,1,0))
    character.assignQuest(quest)

    character.runCommandString("*")

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)
        assert character.getBigPosition() == bigPos

    assert character.getBigPosition() == bigPos
    assert character.getSpacePosition() == (7,1,0)

def test_movement_blocked_GoToPosition(terrain,character):

    bigPos = (6,10,0)
    targetPos = (7,1,0)

    terrain.addCharacter(character,bigPos[0]*15+3,bigPos[1]*15+7)

    for x in range(1,14):
        scrap = src.items.itemMap["Scrap"](amount=7)
        terrain.addItem(scrap,(bigPos[0]*15+x,bigPos[1]*15+2,0))

    quest = src.quests.questMap["GoToPosition"](targetPosition=targetPos)
    character.assignQuest(quest)

    assert character.quests == [quest]

    character.runCommandString("*")

    character.advance(advanceMacros=True)

    assert character.quests == []

def test_movement_working_GoToTile(terrain,character):

    bigPos = (6,10,0)
    targetBigPos = (6,9,0)

    smallPos = (3,7,0)

    terrain.addCharacter(character,bigPos[0]*15+smallPos[0],bigPos[1]*15+smallPos[1])

    assert character.getBigPosition() == bigPos
    assert character.getSpacePosition() == smallPos

    quest = src.quests.questMap["GoToTile"](targetPosition=targetBigPos)
    character.assignQuest(quest)

    character.runCommandString("*")

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    assert character.getBigPosition() == targetBigPos

def test_movement_blocked_GoToTile(terrain,character):

    bigPos = (6,10,0)
    targetBigPos = (6,9,0)

    smallPos = (3,7,0)

    terrain.addCharacter(character,bigPos[0]*15+smallPos[0],bigPos[1]*15+smallPos[1])

    for x in range(1,14):
        scrap = src.items.itemMap["Scrap"](amount=7)
        terrain.addItem(scrap,(bigPos[0]*15+x,bigPos[1]*15+2,0))

    assert character.getBigPosition() == bigPos
    assert character.getSpacePosition() == smallPos

    quest = src.quests.questMap["GoToTile"](targetPosition=targetBigPos)
    character.assignQuest(quest)

    character.runCommandString("*")

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    assert character.getBigPosition() == targetBigPos
