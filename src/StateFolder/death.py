import math
import time

import tcod
import tcod.constants

import src
import src.gamestate
import src.helpers
import src.interaction
import src.pseudoUrwid
import src.urwidSpecials


def in_dest(source, target, radius):
    return pow(target[0] - source[0], 2) + pow(target[1] - source[1], 2) <= pow(radius, 2)


def Death(extraParam):
    src.interaction.advanceGame()
    src.interaction.renderGameDisplay()

    reason = extraParam["reason"]
    killer = extraParam["killer"]
    # playerpos = (-99999,-9999)
    # for width in range(src.interaction.tcodConsole.width):
    #     for height in range(src.interaction.tcodConsole.height):
    #         if src.interaction.tcodConsole.rgb[width, height]["ch"] == ord("@"):
    #             if width > playerpos[0] and height > playerpos[1]:
    #                 playerpos = (width, height)
    playerpos = (82,28)
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
        for event in tcod.event.get():
            if isinstance(event, tcod.event.Quit):
                raise SystemExit()
            if isinstance(event, tcod.event.WindowEvent) and event.type == "WINDOWCLOSE":
                raise SystemExit()
        time.sleep(0.014)

    text = f"{reason}\n"
    if killer:
        text += f"by {killer.name}\n"
    text += f"press enter to return to main menu"

    width = len(max(text.splitlines(), key=len))
    height = 3
    x = int(playerpos[0]- width / 2)
    y = int(src.interaction.tcodConsole.height / 2 - 7)

    src.helpers.draw_frame_text(src.interaction.tcodConsole ,width, height, text, x, y)

    src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)
    while 1:
        for event in tcod.event.get():
            if isinstance(event, tcod.event.KeyDown) and event.sym == tcod.event.KeySym.RETURN:
                new_console = tcod.console.Console(src.interaction.tcodConsole.width,src.interaction.tcodConsole.height,src.interaction.tcodConsole._order)
                src.interaction.render(src.gamestate.gamestate.mainChar).printTcod(new_console,19, 6, False)
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
                    for event2 in tcod.event.get():
                        pass
                for i in range(total_frames+1):
                    for width in range(src.interaction.tcodConsole.width):
                        for height in range(src.interaction.tcodConsole.height):
                            if (width,height) != playerpos:
                                src.interaction.tcodConsole.rgb[width, height]["fg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["fg"],(0,0,0),i/total_frames)
                                src.interaction.tcodConsole.rgb[width, height]["bg"] = src.pseudoUrwid.AttrSpec.interpolate(src.interaction.tcodConsole.rgb[width, height]["bg"],(0,0,0),i/total_frames)
                    src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)
                    time.sleep(0.01)
                    for event2 in tcod.event.get():
                        pass
                time.sleep(1.0)
                raise src.interaction.EndGame("character died")
            if isinstance(event, tcod.event.Quit):
                raise SystemExit()
            if isinstance(event, tcod.event.WindowEvent) and event.type == "WINDOWCLOSE":
                raise SystemExit()
        src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)
        time.sleep(0.2)
