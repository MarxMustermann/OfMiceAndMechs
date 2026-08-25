import math
import time

import numpy
import tcod
import tcod.constants
import os

import src
import json

def in_dest(source, target, radius):
    return pow(target[0] - source[0], 2) + pow(target[1] - source[1], 2) <= pow(radius, 2)


def Death(extraParam):

    # delete savestate
    try:
        # register the save
        with open("gamestate/globalInfo.json") as globalInfoFile:
            rawState = json.loads(globalInfoFile.read())
    except:
        rawState = {
            "worlds": [{"savestateId":1,"hasSave":False}],
            "customPrefabs": [],
            "lastGameIndex": 0,
            "wordCounter":0,
        }
    world_info = rawState["worlds"][src.gamestate.gamestate.gameIndex]
    savestate_id = world_info["savestateId"]
    rawState["worlds"].remove(world_info)
    os.remove("gamestate/gamestate_"+str(savestate_id))
    os.remove("gamestate/gamestate_"+str(savestate_id)+"_backup")
    with open("gamestate/globalInfo.json", "w") as globalInfoFile:
        json.dump(rawState, globalInfoFile)

    # unpack parameter
    character = extraParam["character"]
    runStar = False
    for key in character.macroState["commandKeyQueue"]:
        if key[0] == "*":
            runStar = True
    reason = extraParam["reason"]
    killer = extraParam["killer"]

    # chose the successor of the dead player
    pre = False
    chosen_candidate = None
    if "pre" in extraParam:
        homePos = (character.registers["HOMETx"],character.registers["HOMETy"],0)
        homeTerrain = src.gamestate.gamestate.terrainMap[homePos[1]][homePos[0]]

        candidates = homeTerrain.characters[:]
        for room in homeTerrain.rooms:
            candidates.extend(room.characters)

        for candidate in candidates:
            if candidate == character:
                continue
            if candidate.burnedIn:
                continue
            if candidate.faction != character.faction:
                continue
            if isinstance(candidate,src.characters.characterMap["Ghoul"]):
                continue
            if isinstance(candidate,src.characters.characterMap["GroundsKeeper"]):
                continue
            candidate.runCommandString("~",clear=True)
            for quest in candidate.quests[:]:
                quest.autoSolve = False
            chosen_candidate = candidate
            pre = True
            break

    # make sure the old character is shown dead
    character.dead = True
    character.macroState["submenue"] = None
    src.interaction.advanceGame()
    src.interaction.renderGameDisplay()

    # get position of things to draw to
    assumedScreenWidth = src.interaction.tcodConsole.width
    mapWidth = (src.interaction.window_charheight-5)*2
    mapHeight = src.interaction.tcodConsole.height - 1-5
    mapStart  = ((assumedScreenWidth-mapWidth)//2,6)
    playerpos = (mapStart[0] + mapWidth//2 + 1, mapStart[1]+ mapHeight//2 + 1)

    # ensure the character is rendered properly
    src.interaction.tcodConsole.rgb[playerpos[0], playerpos[1]] = ord("@"),(255, 255, 255),(0, 0, 0)
    src.interaction.tcodConsole.rgb[playerpos[0]+1, playerpos[1]]= ord(" "),(0, 0, 0),(0,0,0)

    # show the interaction for respawning a character
    if pre:
        if src.gamestate.gamestate.difficulty == "difficult":
            chosen_candidate.health = int(chosen_candidate.health/2)
            chosen_candidate.maxHealth = int(chosen_candidate.maxHealth/2)
        if src.gamestate.gamestate.difficulty == "easy":
            chosen_candidate.health = int(chosen_candidate.health*2)
            chosen_candidate.maxHealth = int(chosen_candidate.maxHealth*2)
        chosen_candidate.addListener(src.cinematicsFolder.death.Death,"died_pre")
        chosen_candidate.autoExpandQuests = src.gamestate.gamestate.mainChar.autoExpandQuests
        chosen_candidate.autoExpandQuests2 = src.gamestate.gamestate.mainChar.autoExpandQuests2
        chosen_candidate.disableCommandsOnPlus = src.gamestate.gamestate.mainChar.disableCommandsOnPlus
        chosen_candidate.personality = src.gamestate.gamestate.mainChar.personality
        chosen_candidate.duties = src.gamestate.gamestate.mainChar.duties
        chosen_candidate.dutyPriorities = src.gamestate.gamestate.mainChar.dutyPriorities

        src.gamestate.gamestate.mainChar = chosen_candidate

        text = []
        text.append((src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),reason+"\n"))
        if killer:
            name_string = killer.charType
            if isinstance(killer,src.characters.characterMap["Clone"]):
                name_string = killer.name
            text.append((src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),f"by {name_string}\n"))
        text.append("\n")
        text.append("The last bit of your life force left your body and you died.\n")
        text.append("But something else left your body as well.\n")
        text.append("It took over another clone from your base.\n")
        text.append("\n")
        text.append((src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"- press enter to continue -"))
        longestLine = 0
        for line in text:
            line = src.urwidSpecials.flattenToPeseudoString(line)
            if len(line) <= longestLine:
                continue
            longestLine = len(line)

        newText = []
        for line in text:
            newText.append(" "*((longestLine-len(src.urwidSpecials.flattenToPeseudoString(line)))//2))
            newText.append(line)

        chosen_candidate.showTextMenu(newText)

        questMenu = src.menues.menuMap["QuestMenu"](chosen_candidate)
        questMenu.sidebared = True
        chosen_candidate.rememberedMenu.append(questMenu)
        messagesMenu = src.menues.menuMap["MessagesMenu"](chosen_candidate)
        messagesMenu.sidebared = True
        chosen_candidate.rememberedMenu2.append(messagesMenu)
        inventoryMenu = src.menues.menuMap["InventoryMenu"](chosen_candidate)
        inventoryMenu.sidebared = True
        chosen_candidate.rememberedMenu2.append(inventoryMenu)
        combatMenu = src.menues.menuMap["CombatInfoMenu"](chosen_candidate)
        combatMenu.sidebared = True
        chosen_candidate.rememberedMenu.insert(0,combatMenu)
        for quest in chosen_candidate.quests[:]:
            quest.fail("aborted")
        chosen_candidate.quests = []
        src.gamestate.gamestate.story.reachImplant()
        src.gamestate.gamestate.story.activeStory["mainChar"] = chosen_candidate
        chosen_candidate.rank = 6

        if runStar:
            chosen_candidate.runCommandString("*")

        chosen_candidate.addListener(src.gamestate.gamestate.story.enteredRoom,"entered room")
        chosen_candidate.addListener(src.gamestate.gamestate.story.itemPickedUp,"itemPickedUp")
        chosen_candidate.addListener(src.gamestate.gamestate.story.changedTile,"changedTile")
        chosen_candidate.addListener(src.gamestate.gamestate.story.changedTerrain,"changedTerrain")
        chosen_candidate.addListener(src.gamestate.gamestate.story.deliveredSpecialItem,"deliveredSpecialItem")
        chosen_candidate.addListener(src.gamestate.gamestate.story.gotEpochReward,"got epoch reward")

        #  do autosave
        src.gamestate.gamestate.saveAtTheTurnEnd = True
        return

    # draw a darkening cricle around the player
    position_map = {}
    max_dist = -99999
    for width in range(src.interaction.tcodConsole.width):
        for height in range(src.interaction.tcodConsole.height):
            dist = int(math.sqrt(pow(width - playerpos[0], 2) + pow(height - playerpos[1], 2)))
            if dist == 0:
                continue
            if position_map.get(dist) is None:
                position_map[dist] = []
            position_map[dist].append((width,height))
            max_dist = max(dist, max_dist)
    for (index,position_mapping) in enumerate(reversed(sorted(position_map.items()))):
        for position in position_mapping[1]:
            (width,height) = position
            src.interaction.tcodConsole.rgb[width, height]["fg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["fg"],(0,0,0), 1 - index / len(position_map) - 0.01)
            src.interaction.tcodConsole.rgb[width, height]["bg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["bg"],(0,0,0), 1 - index / len(position_map) - 0.01)
        src.interaction.tcodPresent()
        src.helpers.deal_with_window_events()
        time.sleep(0.014)

    # destroy old keystrokes
    tcod.event.get()

    # do post death interaction
    while 1:

        # hande incomming events
        events = list(tcod.event.get())
        while events or runStar:

            # get individual event
            if events:
                event = events.pop(0)
            else:
                event = None

            # show stats menu
            if not pre and isinstance(event, tcod.event.KeyDown) and event.sym == tcod.event.KeySym.s:
                current_content = src.interaction.tcodConsole.rgba.copy()
                show_Stats(original_window_content, character)
                numpy.copyto(src.interaction.tcodConsole.rgba, current_content)

            # end death interaction
            if (isinstance(event, tcod.event.KeyDown) and event.sym == tcod.event.KeySym.RETURN) or runStar:

                # darken screen
                new_console = tcod.console.Console(src.interaction.tcodConsole.width,src.interaction.tcodConsole.height,src.interaction.tcodConsole._order)
                src.interaction.render(src.gamestate.gamestate.mainChar,mapWidth).printTcod(new_console, (assumedScreenWidth-mapWidth)//4, 6, False)
                src.helpers.draw_frame_text(new_console, width, height, text, 0, 0)
                target_console = new_console.rgb
                total_frames = 5
                for i in range(total_frames+1):
                    for width in range(src.interaction.tcodConsole.width):
                        for height in range(src.interaction.tcodConsole.height):
                            if target_console[width,height]["ch"] == ord(" "):
                                src.interaction.tcodConsole.rgb[width, height]["fg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["fg"],(0,0,0),i/total_frames)
                                src.interaction.tcodConsole.rgb[width, height]["bg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["bg"],(0,0,0),i/total_frames)
                    src.interaction.tcodPresent()
                    time.sleep(0.04)
                    src.helpers.deal_with_window_events()
                for i in range(total_frames+1):
                    for width in range(src.interaction.tcodConsole.width):
                        for height in range(src.interaction.tcodConsole.height):
                            if (width,height) != playerpos:
                                src.interaction.tcodConsole.rgb[width, height]["fg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["fg"],(0,0,0),i/total_frames)
                                src.interaction.tcodConsole.rgb[width, height]["bg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["bg"],(0,0,0),i/total_frames)
                    src.interaction.tcodPresent()
                    time.sleep(0.01)
                    src.helpers.deal_with_window_events()
                time.sleep(1.0)

                # actually the run
                raise src.interaction.EndGame("character died")

        # set up text container
        text = []

        # create the text to show to the player
        text.append("")
        text.append((src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),reason))
        if killer:
            killer_description = killer.charType
            if isinstance(killer,src.characters.characterMap["Clone"]):
                killer_description = killer.name
            text.append((src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),f"by {killer_description}"))
        text.append("")
        text.append("press s to see the characters stats")
        text.append("press enter to return to main menu")

        # calculate text width
        longestLine = 0
        numLines = 0
        for line in text:
            numLines += 1
            line = src.urwidSpecials.flattenToPeseudoString(line)
            if len(line) <= longestLine:
                continue
            longestLine = len(line)

        # center text
        newText = []
        for line in text:
            newText.append(" "*((longestLine-len(src.urwidSpecials.flattenToPeseudoString(line)))//2))
            newText.append(line)
            newText.append("\n")

        # show text
        width = longestLine
        height = numLines
        x = int(playerpos[0]- width / 2)
        y = int(src.interaction.tcodConsole.height / 2 - 3 - height)
        original_window_content = src.interaction.tcodConsole.rgba.copy()
        src.interaction.tcodPresent(noPresent=True)
        src.helpers.draw_frame_text(src.interaction.tcodConsole ,width, height, newText, x, y)
        src.interaction.sdl_renderer2.present()

def show_Stats(original_window_content, character):
    numpy.copyto(src.interaction.tcodConsole.rgba, original_window_content)
    text = src.menues.menuMap["CharacterStatsMenu"](character).text(character)
    text += "\npress enter to return"

    splitted = text.splitlines()
    width = len(max(splitted, key=len))
    height = len(splitted)

    if height > src.interaction.tcodConsole.height - 8:
        splits = math.ceil(height / (src.interaction.tcodConsole.height - 8))
        gap = (src.interaction.tcodConsole.width - splits * width) / (splits + 1)
        for i in range(1, splits + 1):
            src.helpers.draw_frame_text(
                src.interaction.tcodConsole,
                width,
                src.interaction.tcodConsole.height - 8,
                "\n".join(splitted[int(((i - 1) / splits) * len(splitted)) : int((i / splits) * len(splitted))]),
                math.floor(gap * i + width * (i - 1)),
                4,
            )
    else:
        x = int(src.interaction.tcodConsole.width / 2 - width / 2)
        y = int(src.interaction.tcodConsole.height / 2 - height / 2)
        src.helpers.draw_frame_text(src.interaction.tcodConsole, width, height, text, x, y)

    while True:
        for event in tcod.event.get():
            if isinstance(event, tcod.event.KeyDown) and event.sym in (
                tcod.event.KeySym.RETURN,
                tcod.event.KeySym.ESCAPE,
                tcod.event.KeySym.j,
            ):
                return

            src.helpers.deal_with_window_events()
            src.interaction.tcodPresent(noPresent=True)

            text = src.menues.menuMap["CharacterStatsMenu"](character).text(character)
            text += "\npress enter to return"

            splitted = text.splitlines()
            width = len(max(splitted, key=len))
            height = len(splitted)

            if height > src.interaction.tcodConsole.height - 8:
                splits = math.ceil(height / (src.interaction.tcodConsole.height - 8))
                gap = (src.interaction.tcodConsole.width - splits * width) / (splits + 1)
                for i in range(1, splits + 1):
                    src.helpers.draw_frame_text(
                        src.interaction.tcodConsole,
                        width,
                        src.interaction.tcodConsole.height - 8,
                        "\n".join(splitted[int(((i - 1) / splits) * len(splitted)) : int((i / splits) * len(splitted))]),
                        math.floor(gap * i + width * (i - 1)),
                        4,
                    )
            else:
                x = int(src.interaction.tcodConsole.width / 2 - width / 2)
                y = int(src.interaction.tcodConsole.height / 2 - height / 2)
                src.helpers.draw_frame_text(src.interaction.tcodConsole, width, height, text, x, y)

            src.interaction.sdl_renderer2.present()
