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

        viewChar = src.gamestate.gamestate.mainChar.personality["viewChar"]
        viewColour = src.gamestate.gamestate.mainChar.personality["viewColour"]

        for character in terrain.characters:
            if not (character.yPosition and character.xPosition):
                continue

            if (character.xPosition < coordinateOffset[1] or character.xPosition > coordinateOffset[1]+size[1] or
                  character.yPosition < coordinateOffset[0] or character.yPosition > coordinateOffset[0]+size[0]):
                continue
        
            if not "city" in character.faction or not character.charType in ("Character","Ghul",):
                try:
                    chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]] = character.display
                except:
                    print("failed to show char")
                    print(character.yPosition-coordinateOffset[0],character.xPosition-coordinateOffset[1])
            else:
                if viewChar == "rank":
                    if not isinstance(character,src.characters.Ghul):
                        char = "@"+str(character.rank)
                    else:
                        char = "@x"
                elif viewChar == "health":
                    health = str(character.health//(character.maxHealth//10))
                    if health == "10":
                        health = "|"
                    char = "@"+health
                elif viewChar == "name":
                    if not isinstance(character,src.characters.Ghul):
                        char = character.name[0]+character.name.split(" ")[1][0]
                    else:
                        char = "Gu"
                elif viewChar == "faction":
                    char = "@"+character.faction[-1]
                elif viewChar == "activity":
                    if not isinstance(character,src.characters.Ghul):
                        postfix = " "

                        if character.isStaff:
                            prefix = "S"
                        elif not character.quests:
                            prefix = "I"
                        elif character.quests[0].type == "BeUsefull":
                            prefix = "U"
                        else:
                            prefix = "@"

                        """
                        activeQuest = character.getActiveQuest()
                        if activeQuest:
                            postfix = activeQuest.shortCode
                        """
                        subQuest = None
                        if character.quests and character.quests[0].type == "BeUsefull":
                            if character.quests[0].subQuests:
                                postfix = character.quests[0].subQuests[0].shortCode
                            else:
                                postfix = " "

                        char = prefix+postfix
                    else:
                        char = "G "
                else:
                    char = "@ "

                color = "#fff"
                if viewColour == "activity":
                    if not isinstance(character,src.characters.Ghul):
                        if character.isStaff:
                            color = "#0f0"
                        elif not character.quests:
                            color = "#f00"
                        elif character.quests[0].type == "BeUsefull":
                            color = "#00f"
                        else:
                            color = "#333"
                    else:
                        color = "#fff"
                if viewColour == "rank":
                    color = "#fff"
                    if character.rank == 3:
                        color = "#0f0"
                    if character.rank == 4:
                        color = "#3f0"
                    if character.rank == 5:
                        color = "#480"
                    if character.rank == 6:
                        color = "#662"
                if viewColour == "health":
                    color = "#fff"
                    health = character.health//(character.maxHealth//14)
                    if health == 0:
                        color = "#f00"
                    if health == 1:
                        color = "#e10"
                    if health == 2:
                        color = "#d20"
                    if health == 3:
                        color = "#c30"
                    if health == 4:
                        color = "#b40"
                    if health == 5:
                        color = "#a50"
                    if health == 6:
                        color = "#960"
                    if health == 7:
                        color = "#870"
                    if health == 8:
                        color = "#780"
                    if health == 9:
                        color = "#690"
                    if health == 10:
                        color = "#5a0"
                    if health == 11:
                        color = "#4b0"
                    if health == 12:
                        color = "#3c0"
                    if health == 13:
                        color = "#2d0"
                    if health == 14:
                        color = "#1e0"
                    if health == 15:
                        color = "#0f0"
                if viewColour == "faction":
                    if character.faction.endswith("#1"):
                        color = "#066"
                    elif character.faction.endswith("#2"):
                        color = "#006"
                    elif character.faction.endswith("#3"):
                        color = "#060"
                    elif character.faction.endswith("#4"):
                        color = "#082"
                    elif character.faction.endswith("#5"):
                        color = "#028"
                    elif character.faction.endswith("#6"):
                        color = "#088"
                    elif character.faction.endswith("#7"):
                        color = "#086"
                    elif character.faction.endswith("#8"):
                        color = "#068"
                    elif character.faction.endswith("#9"):
                        color = "#0a0"
                    elif character.faction.endswith("#10"):
                        color = "#00a"
                    elif character.faction.endswith("#11"):
                        color = "#0a6"
                    elif character.faction.endswith("#12"):
                        color = "#06a"
                    elif character.faction.endswith("#13"):
                        color = "#08a"
                    elif character.faction.endswith("#14"):
                        color = "#0a6"
                    elif character.faction.endswith("#15"):
                        color = "#0aa"
                    else:
                        color = "#3f3"
                if viewColour == "name":
                    colormap = {
                            "A":"#aaa",
                            "B":"#3aa",
                            "C":"#00a",
                            "D":"#fa4",
                            "E":"#0af",
                            "F":"#44a",
                            "G":"#dfa",
                            "H":"#0fa",
                            "I":"#0a4",
                            "J":"#4fa",
                            "K":"#08a",
                            "L":"#ea8",
                            "M":"#37a",
                            "N":"#3f8",
                            "O":"#a4f",
                            "P":"#0aa",
                            "Q":"#8aa",
                            "R":"#0a8",
                            "S":"#a2a",
                            "T":"#6af",
                            "U":"#5ea",
                            "V":"#0a5",
                            "W":"#4af",
                            "X":"#daa",
                            "Y":"#1aa",
                            "Z":"#03a",
                            }
                    color = colormap.get(character.name[0])
                    if not color:
                        color = "#3f3"

                chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]] = (src.interaction.urwid.AttrSpec(color, "black"), char)

                if character.showThinking:
                    chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].bg = "#333"
                    character.showThinking = False
                if character.showGotCommand:
                    chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].bg = "#fff"
                    character.showGotCommand = False
                if character.showGaveCommand:
                    chars[character.yPosition-coordinateOffset[0]][character.xPosition-coordinateOffset[1]][0].bg = "#855"
                    character.showGaveCommand = False

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

            try:
                chars[mainChar.yPosition-coordinateOffset[0]][mainChar.xPosition-coordinateOffset[1]] = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@ ")
            except:
                print("failed to show main char")
                print(mainChar.yPosition-coordinateOffset[0],mainChar.xPosition-coordinateOffset[1])
