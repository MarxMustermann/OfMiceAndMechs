import src
import pytest

src.canvas.displayChars = src.canvas.DisplayMapping("pureASCII")
src.interaction.urwid = src.pseudoUrwid
src.gamestate.gamestate = src.gamestate.GameState(11)

def test_gotoPosition_bounds(character_room):
    src.quests.questMap["GoToPosition"](targetPosition=(9,9,0))

    with pytest.raises(ValueError):
        src.quests.questMap["GoToPosition"](targetPosition=(9,-1,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToPosition"](targetPosition=(-1,9,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToPosition"](targetPosition=(14,9,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToPosition"](targetPosition=(9,14,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToPosition"](targetPosition=(9,5000,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToPosition"](targetPosition=(5000,14,0))

def test_gotoTile(character_room):
    src.quests.questMap["GoToTile"](targetPosition=(9,9,0))

    with pytest.raises(ValueError):
        src.quests.questMap["GoToTile"](targetPosition=(9,0,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToTile"](targetPosition=(0,9,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToTile"](targetPosition=(14,9,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToTile"](targetPosition=(9,14,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToTile"](targetPosition=(9,5000,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToTile"](targetPosition=(5000,14,0))

def test_gotoTerrain(character_room):
    src.quests.questMap["GoToTerrain"](targetTerrain=(9,9,0))

    with pytest.raises(ValueError):
        src.quests.questMap["GoToTerrain"](targetTerrain=(9,0,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToTerrain"](targetTerrain=(0,9,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToTerrain"](targetTerrain=(14,9,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToTerrain"](targetTerrain=(9,14,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToTerrain"](targetTerrain=(9,5000,0))
    with pytest.raises(ValueError):
        src.quests.questMap["GoToTerrain"](targetTerrain=(5000,14,0))

