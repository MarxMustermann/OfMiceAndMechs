import src

class JobAsMatrixMenu(src.subMenu.SubMenu):
    type = "JobAsMatrixMenu"

    def __init__(self,dutyArtwork):
        super().__init__()
        self.dutyArtwork = dutyArtwork
        self.index = [0,0]

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
        text.append("\ncharacter                 ")
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
                text.append("\n                          ")
                dutyCounter = 0

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

            # add the duties
            rowCounter = 0
            for duty in duties:
                # determine background color
                background_color = "default"
                if rowCounter == self.index[1] or lineCounter == self.index[0]:
                    background_color = "#333"

                # add index indicator in front
                if lineCounter == self.index[0] and rowCounter == self.index[1]:
                    text.append("=>")
                else:
                    text.append((src.interaction.urwid.AttrSpec("default", background_color),"  "))

                # add spacing in front
                distancer = " "
                if duty in npc.duties and npc.dutyPriorities.get(duty,1) > 9:
                    distancer = ""
                text.append((src.interaction.urwid.AttrSpec("default", background_color),distancer))

                # add the actual duty priority
                if duty in npc.duties:
                    text.append(str(npc.dutyPriorities.get(duty,1)))
                else:
                    text.append((src.interaction.urwid.AttrSpec("default", background_color)," "))
                text.append("|")
                rowCounter += 1
            lineCounter += 1

        # show output
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))
        self.persistentText = text
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))
        return False
