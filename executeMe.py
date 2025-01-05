#!/usr/bin/env python3
from multiprocessing import freeze_support
if __name__ == '__main__':
    freeze_support()

    try:

        """
        load environment and start the games main loop
        basically nothing to see here
        if you are a first time visitor, interaction.py, story.py and gamestate.py are probably better files to start with
        """

        import argparse
        import logging

        from src import canvas, characters, interaction, story

        parser = argparse.ArgumentParser()
        parser.add_argument("-p", "--phase", type=str, help="the phase to start in")
        parser.add_argument("--unicode", action="store_true", help="force fallback encoding")
        parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
        parser.add_argument(
            "-t",
            "--tiles",
            action="store_true",
            help="spawn a tile based view of the map (requires pygame)",
        )
        parser.add_argument("--urwid", action="store_true", help="do shell based")
        parser.add_argument("-ts", "--tileSize", type=int, help="the base size of tiles")
        parser.add_argument("-T", "--terrain", type=str, help="select the terrain")
        parser.add_argument("-s", "--seed", type=str, help="select the seed of a new game")
        parser.add_argument("--multiplayer", action="store_true", help="activate multiplayer")
        parser.add_argument("--load", action="store_true", help="load")
        parser.add_argument("--noload", action="store_true", help="do not load saves")
        parser.add_argument("-S", "--speed", type=int, help="set the speed of the game to a fixed speed")
        parser.add_argument("-sc", "--scenario", type=str, help="set the scenario to run")
        parser.add_argument("-notcod", "--notcod", action="store_true", help="do not use tcod renderer")
        parser.add_argument("-df", "--difficulty", type=str, help="set the difficulty for this run")
        parser.add_argument("-nf", "--noFlicker", action="store_true", help="disable flickering (not fully done yet)")
        args = parser.parse_args()

        ################################################################################
        #
        #         switch scenarios
        #
        ################################################################################

        # set rendering mode
        if args.urwid or not args.notcod:
            displayChars = canvas.DisplayMapping("unicode") if args.unicode else canvas.DisplayMapping("pureASCII")
        else:
            displayChars = canvas.TileMapping("testTiles")

        # bad code: common variables with modules
        canvas.displayChars = displayChars

        if args.speed:
            interaction.speed = args.speed

        if args.noFlicker:
            interaction.noFlicker = args.noFlicker

        if args.seed:
            seed = int(args.seed)
        else:
            import random

            seed = random.randint(1, 100000)

        if not args.notcod:
            interaction.setUpTcod()

        story.registerPhases()


        interaction.debug = args.debug
        logging.basicConfig(
            level=logging.DEBUG if interaction.debug else logging.INFO,
            handlers=[logging.StreamHandler()]
            + ([logging.FileHandler("debug.log", "w", "utf-8")] if interaction.debug else []),
        )

        if not args.urwid:
            interaction.nourwid = True

            import src.pseudoUrwid

            interaction.urwid = src.pseudoUrwid
            characters.urwid = src.pseudoUrwid
        else:
            interaction.nourwid = False
            import urwid

            interaction.urwid = urwid
            characters.urwid = urwid
            interaction.setUpUrwid()

        ################################################################################
        #
        #         some stuff that is somehow needed but slated for removal
        #
        ################################################################################

        interaction.setFooter()

        ##########################################
        #
        #  set up the terrain
        #
        ##########################################

        # bad code: common variables with modules

        # set up tile based mode
        if args.tiles:
            # spawn tile based rendered window
            import pygame

            pygame.init()
            pygame.key.set_repeat(200, 20)
            if args.tileSize:
                interaction.tileSize = args.tileSize
            else:
                interaction.tileSize = 10
            pydisplay = pygame.display.set_mode((1200, 700), pygame.RESIZABLE)
            pygame.display.set_caption("Of Mice and Mechs")
            pygame.display.update()
            interaction.pygame = pygame
            interaction.pydisplay = pydisplay
            interaction.useTiles = True
            interaction.tileMapping = canvas.TileMapping("testTiles")
        else:
            interaction.useTiles = False
            interaction.tileMapping = None

        if args.multiplayer:
            interaction.multiplayer = True
            interaction.fixedTicks = 0.1
        else:
            interaction.multiplayer = False
            interaction.fixesTicks = False


        ################################################################################
        #
        #     main loop is started here
        #
        ################################################################################

        # start the interaction loop of the underlying library
        if args.urwid:
            input("game ready. press enter to start")
            interaction.loop.run()

        logger = logging.getLogger(__name__)
        if not args.urwid:
            try:
                interaction.showIntro()
            except src.interaction.EndGame:
                logger.info("ended game")

            while 1:
                try:
                    interaction.showMainMenu(args)
                    try:
                        interaction.gameLoop(None, None)
                    except src.interaction.EndGame:
                        logger.info("ended game")
                except Exception as e:
                    import sys
                    has_trace = hasattr(sys, 'gettrace') and sys.gettrace() is not None
                    has_breakpoint = sys.breakpointhook.__module__ != "sys"
                    is_debug = has_trace or has_breakpoint
                    if is_debug:
                        raise e

                    import time
                    import traceback
                    from datetime import datetime
                    from threading import Thread

                    import tcod


                    interaction.tcodConsole.clear()

                    text = "something happened and the game crashed. Do you consent to uploading the bug report?\n"
                    text+= "press y to accept or press n to deny\n"
                    text+= "(the report doesn't include any personal data)\n"

                    splitted = text.splitlines()
                    width = len(max(splitted, key=len))
                    height = len(splitted)
                    x = int(src.interaction.tcodConsole.width / 2 - width / 2)
                    y = int(src.interaction.tcodConsole.height / 2 - 3 - height)

                    src.helpers.draw_frame_text(src.interaction.tcodConsole ,width, height, text, x, y)

                    src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)


                    exceptionText = ''.join(traceback.format_exception(None, e, e.__traceback__))

                    while 1:
                        events = tcod.event.get()
                        for event in events:
                            if isinstance(event, tcod.event.KeyDown):
                                if event.sym == tcod.event.KeySym.y:
                                    import requests
                                    def send_d():
                                        t = time.time()
                                        res = requests.post(
                                            "http://ofmiceandmechs.com/bugReportDump.php",
                                            {
                                                "bugReport": exceptionText,
                                                "time": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                                            },
                                            files={
                                                "upload_file": open(
                                                    f"gamestate/gamestate_{src.gamestate.gamestate.gameIndex}", "rb"
                                                )
                                            },
                                        )
                                        print(res)
                                        print(res.text)
                                        diff = time.time() - t
                                        if diff < 2:
                                            time.sleep(diff)

                                    t = Thread(target=send_d)
                                    t.start()
                                    interaction.tcodConsole.clear()
                                    text = "thanks a lot, i hope i'll get to fixing the bug soon\n"
                                    text+= "the window will close as soon as the report upload be done"
                                    w = len(max(text.splitlines(), key=len))
                                    x = int(src.interaction.tcodConsole.width / 2 - w / 2 )
                                    src.helpers.draw_frame_text(src.interaction.tcodConsole ,w, 2, text, x, y)
                                    src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)
                                    while t.is_alive():
                                        for _ in tcod.event.get():
                                            if isinstance(event, tcod.event.WindowEvent):
                                                match event.type:
                                                    case "WINDOWCLOSE":
                                                        raise e
                                    raise e
                                elif event.sym == tcod.event.KeySym.n:
                                    t = Thread(target=lambda: time.sleep(1.5))
                                    interaction.tcodConsole.clear()
                                    text = "okay then, here is the trace copied to your clipboard in case you feel better writing me an email"
                                    x = int(src.interaction.tcodConsole.width / 2 - len(text) / 2)
                                    tcod.sdl.sys._set_clipboard(exceptionText)
                                    src.helpers.draw_frame_text(src.interaction.tcodConsole ,len(text), 1, text, x, y)
                                    src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)
                                    t.start()
                                    while t.is_alive():
                                        for _ in tcod.event.get():
                                            if isinstance(event, tcod.event.WindowEvent):
                                                match event.type:
                                                    case "WINDOWCLOSE":
                                                        raise e
                                    raise e
                                src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)
                            if isinstance(event, tcod.event.Quit):
                                raise e
                            if isinstance(event, tcod.event.WindowEvent):
                                match event.type:
                                    case "WINDOWCLOSE":
                                        raise e
                                    case _:
                                        src.interaction.tcodContext.present(src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True)

    except Exception as e:
        if src.interaction.tcodMixer:
            src.interaction.tcodMixer.close()

        raise e
