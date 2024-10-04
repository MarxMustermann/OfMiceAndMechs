import src


class Map(src.items.Item):
    """
    ingame item for storing, handlind and running paths
    """
    #NIY: kind of works but is not well integrated

    type = "Map"

    def __init__(self):
        """
        configure the super class
        """

        super().__init__(display=src.canvas.displayChars.map)
        self.name = "map"
        self.description = "A map is a collection of routes"
        self.usageInfo = """
You can select the routes and run the stored route.
"""

        self.routes = {}
        self.nodes = []
        self.walkable = True
        self.bolted = False
        self.recording = False
        self.recordingStart = None
        self.macroBackup = None

        self.markers = {}

    def apply(self, character):
        """
        spawn a menue offering a selection of actions to run

        Parameters:
            character: the character that is requesting the list
        """

        options = []
        options.append(("walkRoute", "walk route"))
        options.append(("showRoutes", "show routes"))
        options.append(("showAvailableRoutes", "show available routes"))
        options.append(("addMarker", "add marker"))
        options.append(("addRoute", "add route"))
        options.append(("addNode", "add node"))
        options.append(("abort", "abort"))
        self.character = character
        self.submenue = src.menuFolder.SelectionMenu.SelectionMenu(
            "where do you want to do?", options
        )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.selectActivity
        self.macroBackup = self.character.macroState["macros"].get("a")

    def getReachableNodes(self, node):
        """
        returns the list of reachable pathing nodes on the map

        Parameters:
            node: the start node
        """

        if node not in self.routes:
            return []

        nodes = []
        for exitNode in self.routes:
            if exitNode == node:
                continue
            if exitNode in self.routes and node in self.routes[exitNode]:
                nodes.append(exitNode)
                pass

        return nodes

    # abstraction: should use super class function
    def selectActivity(self):
        """
        handle a character having selected an action and run it
        """

        if self.submenue.selection == "walkRoute":
            self.walkRouteSelect()
        if self.submenue.selection == "showRoutes":
            text = "routes:\n"
            for (startNode, routePart) in self.routes.items():
                for (endNode, route) in routePart.items():
                    text += f"{startNode} => {endNode} ({route})\n"
            self.submenue = src.menuFolder.TextMenu.TextMenu(text)
            self.character.macroState["submenue"] = self.submenue
        elif self.submenue.selection == "addMarker":
            self.addMarker()
        elif self.submenue.selection == "addRoute":
            self.addRoute()
        elif self.submenue.selection == "addNode":
            self.addNode()
        else:
            self.submenue = None
            self.character = None

    def addRoute(self):
        """
        add a new route to the map by recording it
        this is a two step process calling this function at the beginning
        and calling the funtion at the end
        """

        pos = (
            self.character.xPosition,
            self.character.yPosition,
            self.character.zPosition,
        )
        items = self.character.container.getItemByPosition(pos)

        node = None
        for item in items:
            if isinstance(item, src.items.PathingNode):
                node = item.nodeName

        if not self.recording:
            self.character.addMessage(
                "walk the path to the target and activate this menu item again"
            )

            self.character.runCommandString("-a")
            if node:
                self.recordingStart = node
            else:
                self.recordingStart = pos
            self.recording = True
        else:
            self.character.runCommandString("-")
            self.recording = None
            if not self.macroBackup:
                return
            if self.recordingStart not in self.routes:
                self.routes[self.recordingStart] = {}
            if self.xPosition:
                counter = 2
            else:
                counter = 1
                while self.macroBackup[-counter] != "i":
                    counter += 1
            if node:
                recordingEnd = node
            else:
                recordingEnd = pos
            self.routes[self.recordingStart][recordingEnd] = self.macroBackup[:-counter]
            del self.character.macroState["macros"]["a"]
            self.character.addMessage(
                f"added path from {self.recordingStart} to {recordingEnd}"
            )
            self.recordingStart = None

    def addMarker(self):
        """
        add a named position to the map
        """

        items = self.character.container.getItemByPosition(
            (self.character.xPosition, self.character.yPosition)
        )
        for item in items:
            if isinstance(item, src.items.FloorPlate):
                self.markers[
                    (self.character.xPosition, self.character.yPosition)
                ] = item.name
                break

    def walkRouteSelect(self):
        """
        offer a selection of walkable routes from the current position to a character
        """

        charPos = (self.character.xPosition, self.character.yPosition)

        if charPos not in self.routes:
            self.character.addMessage("no routes found for this position")
            return

        options = []
        for target in self.routes[charPos]:
            if target in self.markers:
                target = self.markers[target]
            options.append((target, str(target)))
        options.append(("abort", "abort"))
        self.submenue = src.menuFolder.SelectionMenu.SelectionMenu(
            "where do you want to go?", options
        )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.walkRoute

    def walkRoute(self):
        """
        make character walk a selected route
        """

        if self.submenue.selection == "abort":
            return
        charPos = (self.character.xPosition, self.character.yPosition)
        path = self.routes[charPos][self.submenue.selection]

        self.character.runCommandString(path)
        self.character.addMessage("you walk the path")

src.items.addType(Map)
