import math
import time

import numpy
import tcod
import tcod.constants

import src
import src.gamestate
import src.helpers
import src.interaction
import src.menuFolder
import src.menuFolder.characterStatsMenu
import src.pseudoUrwid
import src.story
import src.urwidSpecials


def in_dest(source, target, radius):
    return pow(target[0] - source[0], 2) + pow(target[1] - source[1], 2) <= pow(radius, 2)


def Death(extraParam):
    character = extraParam["character"]
    print(character.macroState)

    runStar = False
    for key in character.macroState["commandKeyQueue"]:
        if key[0] == "*":
            runStar = True
    
    reason = extraParam["reason"]
    killer = extraParam["killer"]
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
            candidate.runCommandString("~",clear=True)
            for quest in candidate.quests[:]:
                quest.autoSolve = False
            chosen_candidate = candidate
            pre = True
            break

    character.dead = True
    character.macroState["submenue"] = None
    src.interaction.advanceGame()
    src.interaction.renderGameDisplay()

    # playerpos = (-99999,-9999)
    # for width in range(src.interaction.tcodConsole.width):
    #     for height in range(src.interaction.tcodConsole.height):
    #         if src.interaction.tcodConsole.rgb[width, height]["ch"] == ord("@"):
    #             if width > playerpos[0] and height > playerpos[1]:
    #                 playerpos = (width, height)
    playerpos = (src.interaction.tcodConsole.width // 2 - 1, src.interaction.tcodConsole.height // 2 - 1)
    src.interaction.tcodConsole.rgb[playerpos[0], playerpos[1]]["ch"] = ord("@")
    p = {}
    max_dist = -99999
    for width in range(src.interaction.tcodConsole.width):
        for height in range(src.interaction.tcodConsole.height):
            dist = int(math.sqrt(pow(width - playerpos[0], 2) + pow(height - playerpos[1], 2)))
            if dist == 0:
                continue
            if p.get(dist) is None:
                p[dist] = []
            p[dist].append((width,height))
            max_dist = max(dist, max_dist)
    for i,d in enumerate(reversed(sorted(p.items()))):
        for po in d[1]:
            (width,height) = po
            src.interaction.tcodConsole.rgb[width, height]["fg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["fg"],(0,0,0), 1 - i / len(p) - 0.01)
            src.interaction.tcodConsole.rgb[width, height]["bg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["bg"],(0,0,0), 1 - i / len(p) - 0.01)
        src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)
        src.helpers.deal_with_window_events()
        time.sleep(0.014)

    text = f"{reason}\n"
    if killer:
        text += f"by {killer.name}\n"

    if not pre:
        text += "press s to see the characters stats\n"
        text += "press enter to return to main menu"
    else:
        text += "The last bit of your life force leaves and you die.\n"
        text += "But something else leaves your implant as well.\n"
        text += "It takes over another clone from your base.\n"
        text += "\n- press enter to respawn -"
    splitted = text.splitlines()
    width = len(max(splitted, key=len))
    height = len(splitted)
    x = int(playerpos[0]- width / 2)
    y = int(src.interaction.tcodConsole.height / 2 - 3 - height)
    original_window_content = src.interaction.tcodConsole.rgba.copy()
    src.helpers.draw_frame_text(src.interaction.tcodConsole ,width, height, text, x, y)

    src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)
    while 1:
        events = list(tcod.event.get())
        while events or runStar:
            if events:
                event = events.pop(0)
            else:
                event = None
            if not pre and isinstance(event, tcod.event.KeyDown) and event.sym == tcod.event.KeySym.s:
                current_content = src.interaction.tcodConsole.rgba.copy()
                show_Stats(original_window_content, character)
                numpy.copyto(src.interaction.tcodConsole.rgba, current_content)
            if (isinstance(event, tcod.event.KeyDown) and event.sym == tcod.event.KeySym.RETURN) or runStar:
                new_console = tcod.console.Console(src.interaction.tcodConsole.width,src.interaction.tcodConsole.height,src.interaction.tcodConsole._order)
                src.interaction.render(src.gamestate.gamestate.mainChar).printTcod(new_console, 34, 6, False)
                src.helpers.draw_frame_text(new_console, width, height, text, x, y)
                target_console = new_console.rgb
                total_frames = 5
                for i in range(total_frames+1):
                    for width in range(src.interaction.tcodConsole.width):
                        for height in range(src.interaction.tcodConsole.height):
                            if target_console[width,height]["ch"] == ord(" "):
                                src.interaction.tcodConsole.rgb[width, height]["fg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["fg"],(0,0,0),i/total_frames)
                                src.interaction.tcodConsole.rgb[width, height]["bg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["bg"],(0,0,0),i/total_frames)
                    src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)
                    time.sleep(0.04)
                    src.helpers.deal_with_window_events()
                for i in range(total_frames+1):
                    for width in range(src.interaction.tcodConsole.width):
                        for height in range(src.interaction.tcodConsole.height):
                            if (width,height) != playerpos:
                                src.interaction.tcodConsole.rgb[width, height]["fg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["fg"],(0,0,0),i/total_frames)
                                src.interaction.tcodConsole.rgb[width, height]["bg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["bg"],(0,0,0),i/total_frames)
                    src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)
                    time.sleep(0.01)
                    src.helpers.deal_with_window_events()
                time.sleep(1.0)
                if not pre:
                    raise src.interaction.EndGame("character died")
                else:
                    if src.gamestate.gamestate.difficulty == "difficult":
                        chosen_candidate.health = int(chosen_candidate.health/2)
                        chosen_candidate.maxHealth = int(chosen_candidate.maxHealth/2)
                    chosen_candidate.addListener(src.cinematicsFolder.death.Death,"died_pre")
                    chosen_candidate.autoExpandQuests = src.gamestate.gamestate.mainChar.autoExpandQuests
                    chosen_candidate.autoExpandQuests2 = src.gamestate.gamestate.mainChar.autoExpandQuests2
                    chosen_candidate.disableCommandsOnPlus = src.gamestate.gamestate.mainChar.disableCommandsOnPlus
                    chosen_candidate.personality = src.gamestate.gamestate.mainChar.personality
                    chosen_candidate.duties = src.gamestate.gamestate.mainChar.duties
                    chosen_candidate.dutyPriorities = src.gamestate.gamestate.mainChar.dutyPriorities

                    src.gamestate.gamestate.mainChar = chosen_candidate

                    questMenu = src.menuFolder.questMenu.QuestMenu(chosen_candidate)
                    questMenu.sidebared = True
                    chosen_candidate.rememberedMenu.append(questMenu)
                    messagesMenu = src.menuFolder.messagesMenu.MessagesMenu(chosen_candidate)
                    chosen_candidate.rememberedMenu2.append(messagesMenu)
                    inventoryMenu = src.menuFolder.inventoryMenu.InventoryMenu(chosen_candidate)
                    inventoryMenu.sidebared = True
                    chosen_candidate.rememberedMenu2.append(inventoryMenu)
                    combatMenu = src.menuFolder.combatInfoMenu.CombatInfoMenu(chosen_candidate)
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
                    chosen_candidate.addListener(src.gamestate.gamestate.story.changedTerrain,"changedTerrain")
                    chosen_candidate.addListener(src.gamestate.gamestate.story.deliveredSpecialItem,"deliveredSpecialItem")
                    chosen_candidate.addListener(src.gamestate.gamestate.story.gotEpochReward,"got epoch reward")

                    #  do autosave
                    src.gamestate.gamestate.save()
                    return
            src.helpers.deal_with_window_events()
            src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)


def show_Stats(original_window_content, character):
    numpy.copyto(src.interaction.tcodConsole.rgba, original_window_content)
    text = src.menuFolder.characterStatsMenu.CharacterStatsMenu().text(character)
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
            src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)
