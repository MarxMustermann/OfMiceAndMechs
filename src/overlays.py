import src
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

    def apply(self, chars, terrain, size=None,coordinateOffset=(0,0)):
        """
        add overlayed information

        Parameters:
            chars: the currently rendered chars
            terrain: the terrain currently rendered
        """

        for character in terrain.characters:
            if not (character.yPosition and character.xPosition):
                continue

            if (character.xPosition < coordinateOffset[1] or character.xPosition > coordinateOffset[1]+size[1] or
                  character.yPosition < coordinateOffset[0] or character.yPosition > coordinateOffset[0]+size[0]):
                continue
        
            if not "city" in character.faction or not character.charType == "Character":
                chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]] = character.display
            else:
                try:
                    chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]] = (src.interaction.urwid.AttrSpec("#3f3", "black"), "@ ")
                    if character.faction.endswith("#1"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#066"
                    if character.faction.endswith("#2"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#006"
                    if character.faction.endswith("#3"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#060"
                    if character.faction.endswith("#4"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#082"
                    if character.faction.endswith("#5"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#028"
                    if character.faction.endswith("#6"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#088"
                    if character.faction.endswith("#7"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#086"
                    if character.faction.endswith("#8"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#068"
                    if character.faction.endswith("#9"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#0a0"
                    if character.faction.endswith("#10"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#00a"
                    if character.faction.endswith("#11"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#0a6"
                    if character.faction.endswith("#12"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#06a"
                    if character.faction.endswith("#13"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#08a"
                    if character.faction.endswith("#14"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#0a6"
                    if character.faction.endswith("#15"):
                        chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].fg = "#0aa"
                except:
                    pass

class MainCharOverlay(object):
    """
    overly showing the main character
    """

    def apply(self, chars, mainChar, size=None,coordinateOffset=(0,0)):
        """
        add overlayed information

        Parameters:
            chars: the currently rendered chars
            mainChar: the main character
        """

        if not mainChar.dead and not mainChar.room and not (
                  mainChar.xPosition < coordinateOffset[1] or mainChar.xPosition > coordinateOffset[1]+size[1] or
                  mainChar.yPosition < coordinateOffset[0] or mainChar.yPosition > coordinateOffset[0]+size[0]):

            chars[mainChar.yPosition-coordinateOffset[0]][mainChar.xPosition-coordinateOffset[1]] = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@ ")
