import src
import pytest

def test_creation():
    for (name,questType) in src.quests.questMap.items():
        if name in ("GetEpochReward","GetPromotion","GoToTile","ProduceItem","RunCommand","SecureTile","SetUpMachine","GoToTileStory",):
            continue
        quest = questType()

def test_check_scraphammering_duty_no_anvil(character_room):
    beUsefull = src.quests.questMap["BeUsefull"]()
    (character,room) = character_room
    step = src.quests.questMap["ScrapHammering"].generateDutyQuest(beUsefull,character,room,dryRun=True)
    assert step == (None,None)

def test_check_scraphammering_duty_only_anvil(character_room):
    beUsefull = src.quests.questMap["BeUsefull"]()
    (character,room) = character_room

    anvil = src.items.itemMap["Anvil"]()
    room.addItem(anvil,(6,6,0))
    assert anvil.bolted == True

    step = src.quests.questMap["ScrapHammering"].generateDutyQuest(beUsefull,character,room,dryRun=True)
    assert step == (None,None)

def test_check_scraphammering_duty_anvil_and_scrap(character_room):
    beUsefull = src.quests.questMap["BeUsefull"]()
    (character,room) = character_room

    scrap = src.items.itemMap["Scrap"]()
    character.inventory.append(scrap)

    anvil = src.items.itemMap["Anvil"]()
    room.addItem(anvil,(6,6,0))
    assert anvil.bolted == True

    step = src.quests.questMap["ScrapHammering"].generateDutyQuest(beUsefull,character,room,dryRun=True)
    assert step == (None,None)

def test_check_scraphammering_duty_anvil_and_scrap_and_stockpile(character_room):
    beUsefull = src.quests.questMap["BeUsefull"]()
    (character,room) = character_room

    room.addStorageSlot((8,8,0),None)

    scrap = src.items.itemMap["Scrap"]()
    character.inventory.append(scrap)

    anvil = src.items.itemMap["Anvil"]()
    room.addItem(anvil,(6,6,0))
    assert anvil.bolted == True

    step = src.quests.questMap["ScrapHammering"].generateDutyQuest(beUsefull,character,room,dryRun=True)
    assert step != (None,None)

def test_check_scraphammering_duty_anvil_and_scrap_and_schedule(character_room):
    beUsefull = src.quests.questMap["BeUsefull"]()
    (character,room) = character_room

    scrap = src.items.itemMap["Scrap"]()
    character.inventory.append(scrap)

    anvil = src.items.itemMap["Anvil"]()
    anvil.scheduledAmount = 2
    room.addItem(anvil,(6,6,0))
    assert anvil.bolted == True

    step = src.quests.questMap["ScrapHammering"].generateDutyQuest(beUsefull,character,room,dryRun=True)
    assert step != (None,None)
