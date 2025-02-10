import src
import pytest

src.canvas.displayChars = src.canvas.DisplayMapping("pureASCII")
src.interaction.urwid = src.pseudoUrwid
src.gamestate.gamestate = src.gamestate.GameState(11)

def test_dutyhangup_painting_no_painter(character_room):
    (character,room) = character_room

    quest = src.quests.questMap["GoToPosition"](targetPosition=(9,9,0))
    character.assignQuest(quest)

    character.runCommandString("*")

    # let the memory build up a bit first
    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

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

def test_refill_flask_1(character_room):
    (character,room) = character_room

    char_flask = src.items.itemMap["GooFlask"]()
    character.flask = char_flask

    characterPos = character.getPosition()
    itemPos = (characterPos[0],characterPos[1],characterPos[2])

    flask = src.items.itemMap["GooFlask"]()
    flask.uses = 100
    room.addItem(flask,itemPos)

    quest = src.quests.questMap["RefillPersonalFlask"]()
    character.assignQuest(quest)

    assert char_flask.uses == 0

    character.runCommandString("*")

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    assert char_flask.uses > 0

def test_refill_flask_2(character_room):
    (character,room) = character_room

    char_flask = src.items.itemMap["GooFlask"]()
    character.flask = char_flask

    characterPos = character.getPosition()
    itemPos = (characterPos[0]-1,characterPos[1],characterPos[2])

    flask = src.items.itemMap["GooFlask"]()
    flask.uses = 100
    room.addItem(flask,itemPos)

    quest = src.quests.questMap["RefillPersonalFlask"]()
    character.assignQuest(quest)

    assert char_flask.uses == 0

    character.runCommandString("*")

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

def test_placeItem_1(terrain,character):
    bigPos = (4,4,0)
    charPos = (5,5,0)

    terrain.addCharacter(character,bigPos[0]*15+charPos[0],bigPos[1]*15+charPos[1])

    wall = src.items.itemMap["Wall"]()
    character.inventory.append(wall)

    targetPos = (charPos[0],charPos[1]+1,charPos[2])

    quest = src.quests.questMap["PlaceItem"](targetPosition=targetPos,targetPositionBig=character.getBigPosition(),itemType="Wall",tryHard=False,reason="build the outline of the room",clearPath=True)
    character.assignQuest(quest)

    character.runCommandString("*")

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    items = terrain.getItemByPosition((bigPos[0]*15+targetPos[0],bigPos[1]*15+targetPos[1],0))

    assert items == [wall]

def test_placeItem_2(terrain,character):
    bigPos = (4,4,0)
    charPos = (5,5,0)

    terrain.addCharacter(character,bigPos[0]*15+charPos[0],bigPos[1]*15+charPos[1])

    wall = src.items.itemMap["Wall"]()
    character.inventory.append(wall)

    targetPos = (charPos[0],charPos[1]+1,charPos[2])

    mold = src.items.itemMap["Mold"]()
    terrain.addItem(mold,(bigPos[0]*15+targetPos[0],bigPos[1]*15+targetPos[1],0))

    quest = src.quests.questMap["PlaceItem"](targetPosition=targetPos,targetPositionBig=character.getBigPosition(),itemType="Wall",tryHard=False,reason="build the outline of the room",clearPath=True)
    character.assignQuest(quest)

    character.runCommandString("*")

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    items = terrain.getItemByPosition((bigPos[0]*15+targetPos[0],bigPos[1]*15+targetPos[1],0))

    assert items == [wall]

def test_placeItem_3(terrain,character):
    bigPos = (4,4,0)
    charPos = (5,5,0)

    terrain.addCharacter(character,bigPos[0]*15+charPos[0],bigPos[1]*15+charPos[1])

    wall = src.items.itemMap["Wall"]()
    character.inventory.append(wall)

    bloom = src.items.itemMap["Bloom"]()
    character.inventory.append(bloom)
    
    targetPos = (charPos[0],charPos[1]+1,charPos[2])

    mold = src.items.itemMap["Mold"]()
    terrain.addItem(mold,(bigPos[0]*15+targetPos[0],bigPos[1]*15+targetPos[1],0))

    quest = src.quests.questMap["PlaceItem"](targetPosition=targetPos,targetPositionBig=character.getBigPosition(),itemType="Wall",tryHard=False,reason="build the outline of the room",clearPath=True)
    character.assignQuest(quest)

    character.runCommandString("*")

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    items = terrain.getItemByPosition((bigPos[0]*15+targetPos[0],bigPos[1]*15+targetPos[1],0))

    assert items == [wall]

def test_placeItem_4(terrain,character):
    bigPos = (4,4,0)
    charPos = (5,5,0)

    terrain.addCharacter(character,bigPos[0]*15+charPos[0],bigPos[1]*15+charPos[1])

    wall = src.items.itemMap["Wall"]()
    character.inventory.append(wall)

    bloom = src.items.itemMap["Bloom"]()
    character.inventory.append(bloom)
    
    targetPos = (charPos[0],charPos[1]+1,charPos[2])

    wall2 = src.items.itemMap["Wall"]()
    wall2.bolted = True
    terrain.addItem(wall2,(bigPos[0]*15+charPos[0],bigPos[1]*15+charPos[1],0))

    mold = src.items.itemMap["Mold"]()
    terrain.addItem(mold,(bigPos[0]*15+targetPos[0],bigPos[1]*15+targetPos[1],0))

    quest = src.quests.questMap["PlaceItem"](targetPosition=targetPos,targetPositionBig=character.getBigPosition(),itemType="Wall",tryHard=False,reason="build the outline of the room",clearPath=True)
    character.assignQuest(quest)

    character.runCommandString("*")

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    items = terrain.getItemByPosition((bigPos[0]*15+targetPos[0],bigPos[1]*15+targetPos[1],0))

    assert items == [wall]
