"""
graphical overlays for decoration on top of renderings
"""

# obsolete: not currently in use and probably broken
class PathsOverlay(object):
    """
    Overlay showing the precalculated paths
    """

    def apply(self, chars, terrain):
        """
        add overlayed information

        Parameters:
            chars: the currently rendered chars
            terrain: the terrain currently rendered
        """

        # do not draw when hidden
        if terrain.hidden:
            return

        # bad code: urwid specific code
        import urwid

        grey = urwid.AttrSpec("#777", "black")
        ltgrey = urwid.AttrSpec("#999", "black")
        yelow = urwid.AttrSpec("#066", "black")
        ltyellow = urwid.AttrSpec("#088", "black")

        # add paths
        for dualPair, path in terrain.foundPaths.items():
            for coordinate in path:
                chars[coordinate[1]][coordinate[0]] = (grey, "::")

        # add intersections
        for coordinate in terrain.watershedStart:
            chars[coordinate[1]][coordinate[0]] = (yellow, "::")

        # add important paths
        for path in terrain.foundSuperPathsComplete.values():
            for coordinate in path:
                chars[coordinate[1]][coordinate[0]] = (ltgrey, "::")
        for dualPair, path in terrain.foundSuperPaths.items():
            for coordinate in path:
                chars[coordinate[1]][coordinate[0]] = (ltyellow, "::")

# obsolete: not currently in use and probably broken
class QuestMarkerOverlay(object):
    """
    Overlay showing quest marker
    """

    def apply(self, chars, mainChar, displayChars):
        """
        add overlayed information

        Parameters:
            chars: the currently rendered chars
            mainChar: the main character
            displayChars: rendering information
        """

        # handle edge case
        if mainChar.room or not mainChar.path:
            return

        # draw path
        for item in mainChar.path:
            # highlight chars on the path
            if chars[item[1]][item[0]] not in (displayChars.pathMarker, "!!", "??"):
                # bad code: urwid specific code
                import urwid

                display = chars[item[1]][item[0]]
                if isinstance(display, int):
                    display = displayChars.indexedMapping[chars[item[1]][item[0]]]
                if isinstance(display, str):
                    display = (urwid.AttrSpec("default", "black"), display)
                chars[item[1]][item[0]] = (
                    urwid.AttrSpec(display[0].foreground, "#333"),
                    display[1],
                )

class NPCsOverlay(object):
    """
    overlay showing npcs
    """

    def apply(self, chars, terrain):
        """
        add overlayed information

        Parameters:
            chars: the currently rendered chars
            terrain: the terrain currently rendered
        """

        for character in terrain.characters:
            if not (character.yPosition and character.xPosition):
                continue
            try:
                chars[character.yPosition][character.xPosition] = character.display
            except:
                pass

class MainCharOverlay(object):
    """
    overly showing the main character
    """

    def apply(self, chars, mainChar):
        """
        add overlayed information

        Parameters:
            chars: the currently rendered chars
            mainChar: the main character
        """

        if not mainChar.dead and not mainChar.room:
            chars[mainChar.yPosition][mainChar.xPosition] = mainChar.display
