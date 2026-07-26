import random

import src


class Flee(src.quests.MetaQuestSequence):
    '''
    quest to flee from enemies
    '''
    type = "Flee"
    lowLevel = True

    def __init__(self, description="Flee", creator=None, command=None, lifetime=None, weaponOnly=False, returnHome=False, reason=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.weaponOnly = weaponOnly

        self.shortCode = "f"
        self.returnHome = returnHome
        self.startTick = None

        self.reason = reason

    def generateTextDescription(self):
        '''
        generate a textual description to show on the UI
        '''
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        return [f"""Flee from your enemies{reasonString}."""]

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and end the quest if completed
        '''
        if not character:
            return False

        if not self.active:
            return False

        try:
            self.returnHome
        except:
            self.returnHome = False

        if not character.getNearbyEnemies():
            bigPos = character.getBigPosition()
            homePos = character.getHomeRoomCord()
            if self.returnHome and bigPos != homePos:
                return False
            if not dryRun:
                self.postHandler()
            return True

        return False

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        '''
        calculate the next step towards solving this quest
        '''

        # wait for subquests to complete
        if self.subQuests:
            return (None,None)

        # run for a random exit after a while
        if src.gamestate.gamestate.tick-self.startTick > 50:
            if not dryRun:
                self.startTick = src.gamestate.gamestate.tick
            exits = []
            if character.container.isRoom:
                for candidate in [(6,0,0),(0,6,0),(12,6,0),(6,12,0)]:
                    if character.container.getPositionWalkable(candidate):
                        exits.append(candidate)
            else:
                exits.extend([(7,1,0),(1,7,0),(13,7,0),(7,13,0)])
            if exits:
                pos = random.choice(exits)
                quest = src.quests.questMap["GoToPosition"](targetPosition=pos,reason="reach escape spot")
                return ([quest],None)

        # return home after initial esscape 
        if not character.getNearbyEnemies():
            bigPos = character.getBigPosition()
            homePos = character.getHomeRoomCord()
            if self.returnHome and bigPos != homePos:
                quest = src.quests.questMap["GoHome"](reason="get back to safety")
                return ([quest],None)
            if not dryRun:
                self.postHandler()
            return (None,("+","end quest"))

        # heal
        if character.health < character.maxHealth//5 and character.canHeal():
            return (None,("JH","heal"))

        # close other menus
        if not ignoreCommands:
            submenue = character.macroState.get("submenue")
            if submenue:
                return (None,(["esc"],"exit the menu"))

        # start collecting possible movements
        commands = []
        command_by_offset = {(-1,0,0):"a",(1,0,0):"d",(0,-1,0):"w",(0,1,0):"s"}

        # get physially possible movement directions
        offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
        character_position = character.getPosition()
        if character.container.isRoom:
            area_size = 11
        else:
            area_size = 13

        terrain = character.getTerrain()
        offset = None
        if character_position[0] < 2:
            offset = (-1,0,0)
        if character_position[0] > area_size-1:
            offset = (1,0,0)
        if character_position[1] < 2:
            offset = (0,-1,0)
        if character_position[1] > area_size-1:
            offset = (0,1,0)
        if offset:
            is_exception = False
            if character.container.isRoom:
                for position in [
                            (6,1,0),(6,0,0),(1,6,0),(0,6,0),
                            (11,6,0),(12,6,0),(6,11,0),(6,12,0),
                        ]:
                    if character_position != position:
                        continue
                    if position in [(6,1,0),(6,0,0)]:
                        rooms = terrain.getRoomByPosition(character.getBigPosition(offset=(0,-1,0)))
                        if rooms:
                            room = rooms[0]
                            if not room.getPositionWalkable((6,12,0)):
                                continue
                    if position in [(6,11,0),(6,12,0)]:
                        rooms = terrain.getRoomByPosition(character.getBigPosition(offset=(0,1,0)))
                        if rooms:
                            room = rooms[0]
                            if not room.getPositionWalkable((6,0,0)):
                                continue
                    if position in [(1,6,0),(0,6,0)]:
                        rooms = terrain.getRoomByPosition(character.getBigPosition(offset=(-1,0,0)))
                        if rooms:
                            room = rooms[0]
                            if not room.getPositionWalkable((12,6,0)):
                                continue
                    if position in [(11,6,0),(12,6,0)]:
                        rooms = terrain.getRoomByPosition(character.getBigPosition(offset=(1,0,0)))
                        if rooms:
                            room = rooms[0]
                            if not room.getPositionWalkable((0,6,0)):
                                continue
                    is_exception = True
            else:
                for position in [(7,1,0),(1,7,0),(13,7,0),(7,13,0)]:
                    if character_position != position:
                        continue
                    if position == (7,1,0):
                        rooms = terrain.getRoomByPosition(character.getBigPosition(offset=(0,-1,0)))
                        if rooms:
                            room = rooms[0]
                            if not room.getPositionWalkable((6,12,0)):
                                continue
                    if position == (7,13,0):
                        rooms = terrain.getRoomByPosition(character.getBigPosition(offset=(0,1,0)))
                        if rooms:
                            room = rooms[0]
                            if not room.getPositionWalkable((6,0,0)):
                                continue
                    if position == (1,7,0):
                        rooms = terrain.getRoomByPosition(character.getBigPosition(offset=(-1,0,0)))
                        if rooms:
                            room = rooms[0]
                            if not room.getPositionWalkable((12,6,0)):
                                continue
                    if position == (13,7,0):
                        rooms = terrain.getRoomByPosition(character.getBigPosition(offset=(1,0,0)))
                        if rooms:
                            room = rooms[0]
                            if not room.getPositionWalkable((0,6,0)):
                                continue
                    is_exception = True
            if not is_exception:
                if offset in offsets:
                    offsets.remove(offset)
            if is_exception:
                commands.extend(command_by_offset[offset]*30)
        basic_offsets = offsets[:]

        # filter movement directions blocked by enemies
        for offset in offsets[:]:
            check_position = character.getPosition(offset=offset)
            characters = character.container.getCharactersOnPosition(check_position,faction=character.faction,enemies=True)
            if characters:
                offsets.remove(offset)
        no_enemy_offsets = offsets[:]

        # filter movement directions blocked by big itens
        for offset in offsets[:]:
            check_position = character.getPosition(offset=offset)
            if not character.container.getPositionWalkable(check_position,character):
                offsets.remove(offset)
        no_items_offsets = offsets[:]

        # select offsets to use as candidate
        if no_items_offsets:
            offsets = no_items_offsets
        elif no_enemy_offsets:
            offsets = no_enemy_offsets
        else:
            offsets = basic_offsets

        # calculate direction ratings
        offset_rating = {(1,0,0):1,(-1,0,0):1,(0,1,0):1,(0,-1,0):1}
        for foundEnemy in character.getNearbyEnemies():
            distance_x = foundEnemy.xPosition-character.xPosition
            if distance_x > 0:
                offset_rating[(-1,0,0)] += 15-abs(distance_x)
            if distance_x < 0:
                offset_rating[(1,0,0)] += 15-abs(distance_x)
            distance_y = foundEnemy.yPosition-character.yPosition
            if distance_y > 0:
                offset_rating[(0,-1,0)] += 15-abs(distance_y)
            if distance_y < 0:
                offset_rating[(0,1,0)] += 15-abs(distance_y)

        # weight escape directions
        for offset in offsets:
            desirability = offset_rating[offset]
            command = command_by_offset[offset]
            commands.extend([command]*desirability)
            
        # fight nearby enemies
        for offset in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,0)]:
            check_position = character.getPosition(offset=offset)
            characters = character.container.getCharactersOnPosition(check_position,faction=character.faction,enemies=True)
            if characters:
                commands.extend(["m"])

        # flee nearby enemies
        for offset in offsets:
            check_position = character.getPosition(offset=offset)
            characters = character.container.getCharactersOnPosition(check_position,faction=character.faction,enemies=True)
            if not characters:
                continue
            flee_offset = (-offset[0],-offset[1],-offset[2])
            command = command_by_offset[flee_offset]
            commands.extend([command]*10)

        # get random escape direction
        command = random.choice(commands)

        # add picking up items to the command
        offset = None
        if command == "d":
            offset = (1,0,0)
        if command == "a":
            offset = (-1,0,0)
        if command == "s":
            offset = (0,1,0)
        if command == "w":
            offset = (0,-1,0)
        if offset:
            pos = character.getPosition(offset=offset)
            if not character.container.getPositionWalkable(pos):
                items = character.container.getItemByPosition(pos)
                if items[0].bolted:
                    command = "C"+command+"b"
                else:
                    command = "K"+command+"l"

        # hang up AI at invalid direction :-P
        if command is None:
            return (None,(".","stand around confused"))

        # run the command
        return (None,(command,"flee"))

    def assignToCharacter(self, character):
        '''
        assign quest to character
        '''
        if self.character:
            return None

        self.startTick = src.gamestate.gamestate.tick

        return super().assignToCharacter(character)

# add the quest type
src.quests.addType(Flee)
