import src

def test_creation():
    #src.canvas.displayChars = src.canvas.DisplayMapping("pureASCII")
    #src.interaction.urwid = src.pseudoUrwid
    #src.gamestate.gamestate = src.gamestate.GameState(11)

    for (name,questType) in src.quests.questMap.items():
        if name in ("GetEpochReward","GetPromotion","GoToTile","ProduceItem","RunCommand","SecureTile","SetUpMachine","GoToTileStory",):
            continue
        quest = questType()
