import src


class TerrainMenu(src.subMenu.SubMenu):
    type = "TerrainMenu"

    def __init__(self, functionMap=None, extraText="", cursor=None, applyKey="coordinate", gridSize=15, limits=(1, 13)):
        self.functionMap = functionMap
        self.extraText = extraText
        self.applyKey = applyKey
        self.gridSize = gridSize
        self.limits = limits
        if cursor:
            self.cursor = (
                cursor[0],
                cursor[1],
            )
        else:
            self.cursor = (int(self.gridSize / 2), int(self.gridSize / 2))

        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        closeMenu = False
        mappedFunctions = self.functionMap.get(self.cursor, {})
        if key in mappedFunctions:
            closeMenu = True
            self.callIndirect(mappedFunctions[key]["function"], {self.applyKey: self.cursor})

        # exit the submenu
        if key in ("w", "up") and self.cursor[1] > self.limits[0]:
            self.cursor = (self.cursor[0], self.cursor[1] - 1)
        if key in ("s", "down") and self.cursor[1] < self.limits[1]:
            self.cursor = (self.cursor[0], self.cursor[1] + 1)
        if key in ("a", "left") and self.cursor[0] > self.limits[0]:
            self.cursor = (self.cursor[0] - 1, self.cursor[1])
        if key in ("d", "right") and self.cursor[0] < self.limits[1]:
            self.cursor = (self.cursor[0] + 1, self.cursor[1])

        if closeMenu or key in (
            "esc",
            "enter",
            "space",
            "j",
        ):
            if self.followUp:
                self.followUp()
            return True

        if not noRender:
            mapText = self.renderZoneInfo(character)
            mapText[self.cursor[1]][self.cursor[0]] = "██"
            mapText.append(f"\n press wasd to move cursor {self.cursor}")

            mappedFunctions = self.functionMap.get(self.cursor, {})
            for key, item in mappedFunctions.items():
                mapText.append(
                    "\n press {} to {}".format(
                        key,
                        item["description"],
                    )
                )

            # show info
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "TerrainMenu"))
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), mapText))

        return False

    @staticmethod
    def renderZoneInfo(character):
        rawMap = []
        for y in range(15):
            rawMap.append([])
            for x in range(15):
                if x == 0 or y == 0 or x == 14 or y == 14:
                    rawMap[y].append(src.canvas.displayChars.forceField)
                else:
                    rawMap[y].append("  ")
            rawMap[y].append("\n")

        homeCoordinate = None
        if "HOMETx" in character.registers:
            homeCoordinate = (character.registers["HOMETx"], character.registers["HOMETy"], 0)
        characterCoordinate = character.getTerrainPosition()

        for pos, info in character.terrainInfo.items():
            if info["tag"] == "nothingness":
                rawMap[pos[1]][pos[0]] = (src.interaction.urwid.AttrSpec("#550", "black"), ".`")
            elif info["tag"] == "shrine":
                color = "#999"
                rawMap[pos[1]][pos[0]] = (src.interaction.urwid.AttrSpec(color, "black"), "\\/")
            elif info["tag"] == "ruin":
                color = "#666"
                if info.get("looted"):
                    color = "#550"
                rawMap[pos[1]][pos[0]] = (src.interaction.urwid.AttrSpec(color, "black"), "&%")
            elif info["tag"] == "dungeon":
                ItemID = None
                HaveGlassHeart = False
                for ID in src.gamestate.gamestate.gods:
                    god = src.gamestate.gamestate.gods[ID]
                    if god["home"][0] == pos[0] and god["home"][1] == pos[1]:
                        ItemID = ID
                        if god["lastHeartPos"][0] == pos[0] and god["lastHeartPos"][1] == pos[1]:
                            HaveGlassHeart = True
                color = src.items.itemMap["GlassStatue"].color(ItemID)
                text = "DU" if HaveGlassHeart else "du"
                rawMap[pos[1]][pos[0]] = (src.interaction.urwid.AttrSpec(color, "black"), text)
            else:
                rawMap[pos[1]][pos[0]] = info["tag"][:2]
        if homeCoordinate:
            rawMap[homeCoordinate[1]][homeCoordinate[0]] = "HH"
        rawMap[characterCoordinate[1]][characterCoordinate[0]] = "@@"

        return rawMap
