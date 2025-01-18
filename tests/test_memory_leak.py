import src
import pytest
import objgraph
import random

src.canvas.displayChars = src.canvas.DisplayMapping("pureASCII")
src.interaction.urwid = src.pseudoUrwid
src.gamestate.gamestate = src.gamestate.GameState(11)

def test_machining_memleak_simple(character_room):
    (character,room) = character_room

    beUsefull = src.quests.questMap["BeUsefull"]()
    character.duties.append("Machining")
    character.assignQuest(beUsefull)

    character.runCommandString("*")

    # let the memory build up a bit first
    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)
    objgraph.show_growth()

    # run for a long time
    for i in range(5000):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    # cancel quests
    for quest in character.quests[:]:
        quest.fail("aborted")

    objgraph.show_growth()

def test_machining_memleak_task(character_room):
    (character,room) = character_room

    room.addBuildSite((5,2,0),"Machine",{"toProduce":"Rod"})

    beUsefull = src.quests.questMap["BeUsefull"]()
    character.duties.append("Machining")
    character.assignQuest(beUsefull)

    character.runCommandString("*")
    # let the memory build up a bit first
    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)
    growth = objgraph.show_growth()

    character.runCommandString("*")

    # run for a long time
    for i in range(50000):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    ## cancel quests
    #for quest in character.quests[:]:
    #    quest.fail("aborted")

    for i in range(50):
        character.timeTaken = 0
        character.advance(advanceMacros=True)

    objgraph.show_growth()

    quests = objgraph.by_type('GoToPosition')
    #quest = random.choice(quests)
    #objgraph.show_backrefs(quest, max_depth=10)

    assert len(quests) < 10
    assert len(character.listeners) < 50
    assert len(beUsefull.listeners) < 50
    assert len(beUsefull.watched) < 50
