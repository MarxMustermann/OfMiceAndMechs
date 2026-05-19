import src

class ContextListMenu(src.menues.SubMenu):
    type = "ContextListMenu"

    def __init__(self,char):
        super().__init__()
        self.index = char.getSpacePosition()
        self.index_big = char.getBigPosition()
        self.character = char

    def getTitle(self):
        return "CONTEXT MENU"

    def get_map_position(self):
        big_position = self.index_big
        small_position = self.index
        pos = (big_position[0]*15+small_position[0], big_position[1]*15+small_position[1], big_position[2]*15+small_position[2])
        return pos

    def handleKey(self, key, noRender=False, character = None):

        # exit the submenu
        if key in ("esc"," ",):
            return True

        # move small cursor
        if key in ("w","up",):
            self.index = (self.index[0],self.index[1]-1,0)
        if key in ("s","down",):
            self.index = (self.index[0],self.index[1]+1,0)
        if key in ("a","left",):
            self.index = (self.index[0]-1,self.index[1],0)
        if key in ("d","right",):
            self.index = (self.index[0]+1,self.index[1],0)

        # handle out of bounds by small cursor
        if self.index[0] < 0:
            self.index_big = (self.index_big[0]-1,self.index_big[1],0)
            self.index = (13,self.index[1],0)
        if self.index[0] > 13:
            self.index_big = (self.index_big[0]+1,self.index_big[1],0)
            self.index = (0,self.index[1],0)
        if self.index[1] < 0:
            self.index_big = (self.index_big[0],self.index_big[1]-1,0)
            self.index = (self.index[0],13,0)
        if self.index[1] > 13:
            self.index_big = (self.index_big[0],self.index_big[1]+1,0)
            self.index = (self.index[0],0,0)

        # move big cursor
        if key in ("W",):
            self.index_big = (self.index_big[0],self.index_big[1]-1,0)
        if key in ("S",):
            self.index_big = (self.index_big[0],self.index_big[1]+1,0)
        if key in ("A",):
            self.index_big = (self.index_big[0]-1,self.index_big[1],0)
        if key in ("D",):
            self.index_big = (self.index_big[0]+1,self.index_big[1],0)

        # hanldle out of bound by the big cursor
        if self.index_big[0] < 1:
            self.index_big = (13,self.index_big[1],0)
        if self.index_big[0] > 13:
            self.index_big = (1,self.index_big[1],0) 
        if self.index_big[1] < 1:
            self.index_big = (self.index_big[0],13,0)
        if self.index_big[1] > 13:
            self.index_big = (self.index_big[0],1,0)

        if key in ("g",):
            self.trigger_goToPosition()

        if key in ("k",):
            self.trigger_clearSpot()

        # signal menu is still active
        return False

    def render(self):

        # getting some helper variables
        terrain = self.character.getTerrain()
        rooms = terrain.getRoomByPosition(self.index_big)
        container = terrain
        if rooms:
            container = rooms[0]

        # set the besaic text
        text = []

        # show the interaction options
        text.append(src.interaction.ActionMeta(payload=(self.trigger_clearSpot,{}),content="clear spot"))
        text.append("\n")
        text.append(src.interaction.ActionMeta(payload=(self.trigger_goToPosition,{}),content="go to position"))
        text.append("\n")
        text.append(src.interaction.ActionMeta(payload=(self.trigger_restock,{}),content="restock stockpile"))

        # return rendered text
        return text

    def trigger_goToPosition(self,extraParams=None):
        quest = src.quests.questMap["GoToPosition"](targetPositionBig=self.index_big, targetPosition=self.index)
        quest.autoSolve = True
        self.character.assignQuest(quest,active=True)

    def trigger_clearSpot(self,extraParams=None):
        quest = src.quests.questMap["CleanSpace"](targetPositionBig=self.index_big, targetPosition=self.index)
        quest.autoSolve = True
        self.character.assignQuest(quest,active=True)

    def trigger_restock(self,extraParams=None):
        quest = src.quests.questMap["RestockRoom"](targetPositionBig=self.index_big, targetPosition=self.index)
        quest.autoSolve = True
        self.character.assignQuest(quest,active=True)

