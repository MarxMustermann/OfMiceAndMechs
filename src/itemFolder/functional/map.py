import src

'''
'''
class Map(Item):
    type = "Map"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Map",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.map,xPosition,yPosition,name=name,creator=creator)

        self.routes = {
                      }
        self.nodes = []
        self.walkable = True
        self.bolted = False
        self.recording = False
        self.recordingStart = None
        self.macroBackup = None

        self.markers = {}

        self.attributesToStore.extend([
                "text","recording","nodes","routes",])

    def apply(self,character):
        super().apply(character,silent=True)

        options = []
        options.append(("walkRoute","walk route"))
        options.append(("showRoutes","show routes"))
        options.append(("showAvailableRoutes","show available routes"))
        options.append(("addMarker","add marker"))
        options.append(("addRoute","add route"))
        options.append(("addNode","add node"))
        options.append(("abort","abort"))
        self.character = character
        self.submenue = src.interaction.SelectionMenu("where do you want to do?",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.selectActivity
        self.macroBackup = self.character.macroState["macros"].get("auto")

    def getReachableNodes(self,node):
        if not node in self.routes:
            return []

        nodes = []
        for exitNode in self.routes.keys():
            if exitNode == node:
                continue
            if exitNode in self.routes and node in self.routes[exitNode]:
                nodes.append(exitNode)
                pass

        return nodes

    def selectActivity(self):
        if self.submenue.selection == "walkRoute":
            self.walkRouteSelect()
        if self.submenue.selection == "showRoutes":
            text = "routes:\n"
            for (startNode,routePart) in self.routes.items():
                for (endNode,route) in routePart.items():
                    text += "%s => %s (%s)\n"%(startNode,endNode,route,)
            self.submenue = src.interaction.TextMenu(text)
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
        pos = (self.character.xPosition,self.character.yPosition,self.character.zPosition)
        items = self.character.container.getItemByPosition(pos)

        node = None
        for item in items:
            if isinstance(item,src.items.PathingNode):
                node = item.nodeName

        if not self.recording:
            self.character.addMessage("walk the path to the target and activate this menu item again")
            self.character.macroState["commandKeyQueue"] = [("-",["norecord"]),("auto",["norecord"])]+self.character.macroState["commandKeyQueue"] 
            if node:
                self.recordingStart = node
            else:
                self.recordingStart = pos
            self.recording = True
        else:
            self.character.macroState["commandKeyQueue"] = [("-",["norecord"])]+self.character.macroState["commandKeyQueue"] 
            self.recording = None
            if not self.macroBackup:
                return
            if not self.recordingStart in self.routes:
                self.routes[self.recordingStart] = {}
            if self.xPosition:
                counter = 2
            else:
                counter = 1
                while not self.macroBackup[-counter] == "i":
                    counter += 1
            if node:
                recordingEnd = node
            else:
                recordingEnd = pos
            self.routes[self.recordingStart][recordingEnd] = self.macroBackup[:-counter]
            del self.character.macroState["macros"]["auto"]
            self.character.addMessage("added path from %s to %s"%(self.recordingStart,recordingEnd))
            self.recordingStart = None

    def addMarker(self):
        items = self.character.container.getItemByPosition((self.character.xPosition,self.character.yPosition))
        for item in items:
            if isinstance(item,src.items.FloorPlate):
                self.markers[(self.character.xPosition,self.character.yPosition)] = item.name
                break

    def walkRouteSelect(self):
        charPos = (self.character.xPosition,self.character.yPosition)

        if not charPos in self.routes:
            self.character.addMessage("no routes found for this position")
            return

        options = []
        for target in self.routes[charPos].keys():
            if target in self.markers:
                target = self.markers[target]
            options.append((target,str(target)))
        options.append(("abort","abort"))
        self.submenue = src.interaction.SelectionMenu("where do you want to go?",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.walkRoute

    def walkRoute(self):
        if self.submenue.selection == "abort":
            return
        charPos = (self.character.xPosition,self.character.yPosition)
        path = self.routes[charPos][self.submenue.selection]
        convertedPath = []
        for step in path:
            convertedPath.append((step,["norecord"]))
        self.character.macroState["commandKeyQueue"] = convertedPath + self.character.macroState["commandKeyQueue"]
        self.character.addMessage("you walk the path")

    def getLongInfo(self):

        text = """
item: Map

description:
A map is a collection of routes.

You can select the routes and run the stored route.

"""
        return text

src.items.addType(Map)
