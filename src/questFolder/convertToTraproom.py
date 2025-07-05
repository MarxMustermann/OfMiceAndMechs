import src


class ConvertToTrapRoom(src.quests.MetaQuestSequence):
    '''
    quest to convert an entry room to a trap room

    Parameters:
        description: the description that should be shown in the UI
        creator: the entity creating this quest (obsolete?)
        roomPosition: the position of the room to convert
    '''
    type = "ConvertToTrapRoom"
    def __init__(self, description="convert to trapRoom", creator=None, roomPosition=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.roomPosition = roomPosition
        self.reason = reason

    def generateTextDescription(self):
        '''
        generate a description of the quest
        '''
        out = []
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
convert an entryRoom to a trapRoom{reason}.

Use a CityPlaner to do this.

"""
        out.append(text)
        return out

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate instructions on what to do next
        uses the city planer to unschedule building a room

        Parameters:
            character: the character that is acting
            ignoreCommands: do not generate commands as output
            dryRum: do not actually change things
        '''

        # do nothing if there are subquests
        if self.subQuests:
            return (None,None)

        # navigate the build-menu and schedule building the room
        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.mapMenu.MapMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            command = ""
            if submenue.cursor[0] > self.roomPosition[0]:
                command += "a"*(submenue.cursor[0]-self.roomPosition[0])
            if submenue.cursor[0] < self.roomPosition[0]:
                command += "d"*(self.roomPosition[0]-submenue.cursor[0])
            if submenue.cursor[1] > self.roomPosition[1]:
                command += "w"*(submenue.cursor[1]-self.roomPosition[1])
            if submenue.cursor[1] < self.roomPosition[1]:
                command += "s"*(self.roomPosition[1]-submenue.cursor[1])
            command += "t"
            return (None,(command,"convert entryRoom to a trapRoom"))

        # select the build menu
        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.selectionMenu.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            rewardIndex = 0
            if rewardIndex == 0:
                counter = 1
                for option in submenue.options.items():
                    if option[1] == "showMap":
                        break
                    counter += 1
                rewardIndex = counter
            offset = rewardIndex-submenue.selectionIndex
            command = ""
            if offset > 0:
                command += "s"*offset
            else:
                command += "w"*(-offset)
            command += "j"
            return (None,(command,"show the map"))

        # close unkown menus
        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"exit submenu"))

        # go to room with city planer
        pos = character.getBigPosition()
        if pos != character.getHomeRoomCord():
            quest = src.quests.questMap["GoHome"](description="go to command centre",reason="go to command centre")
            return ([quest],None)

        # enter room
        if not character.container.isRoom:
            quest = src.quests.questMap["EnterRoom"]()
            return ([quest],None)

        # start using the city planer
        cityPlaner = character.container.getItemsByType("CityPlaner")[0]
        command = None
        if character.getPosition(offset=(1,0,0)) == cityPlaner.getPosition():
            command = "d"
        if character.getPosition(offset=(-1,0,0)) == cityPlaner.getPosition():
            command = "a"
        if character.getPosition(offset=(0,1,0)) == cityPlaner.getPosition():
            command = "s"
        if character.getPosition(offset=(0,-1,0)) == cityPlaner.getPosition():
            command = "w"
        if character.getPosition(offset=(0,0,0)) == cityPlaner.getPosition():
            command = "."
        if command:
            interactionCommand = "J"
            if "advancedInteraction" in character.interactionState:
                interactionCommand = ""
            return (None,(interactionCommand+command,"activate the CityPlaner"))

        # go to the city planer
        quest = src.quests.questMap["GoToPosition"](targetPosition=cityPlaner.getPosition(), description="go to CityPlaner",ignoreEndBlocked=True, reason="go to the CityPlaner")
        return ([quest],None)

    def triggerCompletionCheck(self,character=None):
        '''
        check and end a quest if it is completed

        Parameter:
            character: the character working on the quest
        '''

        # abort on weird states
        if not character:
            return False

        # fetch the city planer
        terrain = character.getTerrain()
        room = terrain.getRoomByPosition(self.roomPosition)[0]

        # continue working if rooms tag is not correct
        if room.tag != "trapRoom":
            return False

        # end quets on completion
        self.postHandler()
        return True

    def handleConvertedRoom(self,extraParams):
        '''
        callback that ends this quest

        Parameter:
            extraParams: context information
        '''
        if self.completed:
            1/0
        if not self.active:
            return
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        '''
        assign the quest to the character
        '''

        # ignore if character was already assigned
        if self.character:
            return None

        # start listening for the event indicating completion
        self.startWatching(character,self.handleConvertedRoom, "assigned floor plan")

        # call superclass
        return super().assignToCharacter(character)

# register quest
src.quests.addType(ConvertToTrapRoom)
