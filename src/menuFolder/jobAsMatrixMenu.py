import src

class JobAsMatrixMenu(src.subMenu.SubMenu):
    type = "JobAsMatrixMenu"

    def __init__(self,dutyArtwork):
        super().__init__()
        self.dutyArtwork = dutyArtwork
        self.index = [0,0]
        self.cached_npc_order = []

    def get_duties(self):
        """
        returns what duties can be managed at this item
        Returns:
            a list of duties
        """
        return list(reversed([
                "manufacturing",
                "scavenging",
                "machine operation",
                "cleaning",
                "painting",
                "maggot gathering",
                "machine placing",
                "room building",
                "machining",
                "metal working",
                "hauling",
                "resource fetching",
                "scrap hammering",
                "resource gathering",
                "praying",
                "mold farming"
            ]))

    def get_short_form(self,duty_name):
        match duty_name:
            case "mold farming":
                return "mfarm"
            case "praying":
                return "prayr"
            case "resource gathering":
                return "regat"
            case "scrap hammering":
                return "scrha"
            case "resource fetching":
                return "refet"
            case "hauling":
                return "haulr"
            case "metal working":
                return "metwo"
            case "machining":
                return "machi"
            case "room building":
                return "roomb"
            case "machine placing":
                return "place"
            case "maggot gathering":
                return "magot"
            case "painting":
                return "paint"
            case "cleaning":
                return "clean"
            case "machine operation":
                return "maopr"
            case "scavenging":
                return "scave"
            case "manufacturing":
                return "manuf"
        return duty_name[:4]

    def handleKey(self, key, noRender=False, character = None):
        """
        show the help text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in ("esc"," ",):
            return True

        # gather the npcs to show
        terrain = self.dutyArtwork.getTerrain()
        npcs = []
        for char in terrain.characters:
            if char.burnedIn:
                continue
            if char not in npcs:
                npcs.append(char)
        for room in terrain.rooms:
            for char in room.characters:
                if char.burnedIn:
                    continue
                if char not in npcs:
                    npcs.append(char)
        if src.gamestate.gamestate.mainChar in npcs:
            npcs.remove(src.gamestate.gamestate.mainChar)

        # make sure the order doesn't switch during usage
        for npc in reversed(self.cached_npc_order):
            if npc in npcs:
                npcs.remove(npc)
                npcs.insert(0,npc)
        self.cached_npc_order = npcs[:]

        # set up helper variable
        duties = self.get_duties()

        # handle user interactions
        if key == "C":
            for npc in npcs:
                npc.duties = []
        if key in ("w","up") and not self.index[0] < 0:
            self.index[0] -= 1
        if key in ("s","down"):
            self.index[0] += 1
        if key in ("a","left") and not self.index[1] < 1:
            self.index[1] -= 1
        if key in ("d","right") and not self.index[1] > len(duties)-2:
            self.index[1] += 1
        if key in ("j","k","l","c"):
            rowCounter = 0
            for npc in npcs:
                if npc.faction != character.faction:
                    continue
                if isinstance(npc,src.characters.characterMap["Ghoul"]):
                    continue

                if rowCounter == self.index[0] or self.index[0] == -1:
                    dutyname = duties[self.index[1]]

                    if key == "l":
                        pass
                    elif key == "j":
                        if dutyname not in npc.duties:
                            npc.duties.append(dutyname)
                            npc.dutyPriorities[dutyname] = 1
                        else:
                            if dutyname not in npc.dutyPriorities:
                                npc.dutyPriorities[dutyname] = 1
                            npc.dutyPriorities[dutyname] += 1
                    elif key == "k":
                        if dutyname in npc.duties:
                            if dutyname not in npc.dutyPriorities:
                                npc.dutyPriorities[dutyname] = 1
                            npc.dutyPriorities[dutyname] -= 1
                            if npc.dutyPriorities[dutyname] < 1:
                                del npc.dutyPriorities[dutyname]
                                npc.duties.remove(dutyname)
                    elif key == "c":
                        npc.duties = []
                        npc.dutyPriorities = {}

                rowCounter += 1

        # add instructions to output
        text = "press wasd to move cursor"
        text += "press j to enable/disable"
        text = [text]

        # add matrix head to output
        text.append("\ncharacter                ")
        rowCounter = 0
        dutyCounter = 0
        for duty in duties:
            color = "default"
            if rowCounter == self.index[1]:
                color = "#555"
                if self.index[0] == -1:
                    color = "#888"
            text.append("|")
            text.append((src.interaction.urwid.AttrSpec("default", color)," "+duty+" "))
            rowCounter += 1
            dutyCounter += 1
            if dutyCounter == 6:
                text.append("\n                         ")
                dutyCounter = 0
        text.append("|\n\n                         ")
        rowCounter = 0
        dutyCounter = 0
        for duty in duties:
            color = "default"
            if rowCounter == self.index[1]:
                color = "#555"
                if self.index[0] == -1:
                    color = "#888"
            text.append("|")
            text.append((src.interaction.urwid.AttrSpec("default", color),""+self.get_short_form(duty)[:5]+""))
            rowCounter += 1
            dutyCounter += 1
            if dutyCounter == 6:
                dutyCounter = 0
        text.append("|")

        # add actual matrix to output
        def convertName(name):
            return name.ljust(25," ")[0:24]
        lineCounter = 0
        color = "default"
        rowCounter = 0
        if lineCounter == self.index[0]:
            color = "#333"
        lineCounter = 0
        for npc in npcs:
            
            # filter npcs
            if npc.faction != character.faction:
                continue
            if isinstance(npc,src.characters.characterMap["Ghoul"]):
                continue

            # add name
            text.append("\n")
            if lineCounter == self.index[0]:
                color = "#333"
            else:
                color = "default"
            text.append((src.interaction.urwid.AttrSpec("default", color),f"{convertName(npc.name)}: "))

            # get highest duty
            highest_priority = 1
            second_highest_priority = 1
            multiple_highest = False
            for priority in npc.dutyPriorities.values():
                if priority == highest_priority:
                    multiple_highest = True
                    continue
                if priority > highest_priority:
                    second_highest_priority = highest_priority
                    highest_priority = priority
                    multiple_highest = False
                    continue
                if priority > second_highest_priority:
                    second_highest_priority = priority

            # add the duties
            rowCounter = 0
            for duty in duties:
                # determine colors
                background_color = "default"
                if rowCounter == self.index[1] or lineCounter == self.index[0]:
                    background_color = "#333"
                foreground_color = "default"
                if npc.dutyPriorities.get(duty,1) == second_highest_priority and not multiple_highest:
                    foreground_color = "#f94"
                if npc.dutyPriorities.get(duty,1) == highest_priority:
                    if multiple_highest:
                        foreground_color = "#f83"
                    else:
                        foreground_color = "#ff3"
                color_info = src.interaction.urwid.AttrSpec(foreground_color, background_color)

                # add index indicator in front
                cell_text = ""
                if lineCounter == self.index[0] and rowCounter == self.index[1]:
                    cell_text += "=>"
                else:
                    cell_text += "  "

                # add spacing in front
                distancer = " "
                if duty in npc.duties and npc.dutyPriorities.get(duty,1) > 9:
                    distancer = ""
                cell_text += distancer

                # add the actual duty priority
                if duty in npc.duties:
                    cell_text += str(npc.dutyPriorities.get(duty,1))
                else:
                    cell_text += " "
                cell_text += " "

                # add cell 
                text.append((color_info,cell_text))
                text.append("|")

                rowCounter += 1
            lineCounter += 1

        # show output
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))
        self.persistentText = text
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))
        return False
