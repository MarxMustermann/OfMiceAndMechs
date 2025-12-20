import src


class ScrapCompactor(src.items.Item):
    '''
    ingame item that converts scrap to metal bars
    '''
    type = "ScrapCompactor"
    def __init__(self):
        super().__init__()
        self.display = src.canvas.displayChars.scrapCompactor
        self.name = "scrap compactor"
        self.description = "This machine converts scrap into metal bars."
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1
        self.commands = {}

    def readyToUse(self):
        '''
        check if the item is ready to use
        '''
        if not self.container:
            return False

        if not self.bolted:
            return False

        if not self.checkCoolDownEnded():
            return False

        (targetFull,itemList) = self.checkTargetFull()
        if targetFull:
            return False

        scrap = self.checkForInputScrap()
        if not scrap:
            return False

        return True

    def render(self):
        '''
        get how the item should be rendered
        '''
        if self.readyToUse():
            return "RC"
        else:
            return self.display

    def checkForInputScrap(self, character = None):
        '''
        check if there is material to process
        '''
        # fetch input scrap
        scrap = None

        for item in self.container.getItemByPosition(
            (self.xPosition - 1, self.yPosition, self.zPosition)
        ):
            if item.type == "Scrap":
                scrap = item
                break
        if self.level > 1 and not scrap:
            for item in self.container.getItemByPosition(
                (self.xPosition, self.yPosition + 1, self.zPosition)
            ):
                if isinstance(item, itemMap["Scrap"]):
                    scrap = item
                    break
        if self.level > 2 and not scrap:
            for item in self.container.getItemByPosition(
                (self.xPosition, self.yPosition - 1, self.zPosition)
            ):
                if isinstance(item, itemMap["Scrap"]):
                    scrap = item
                    break

        if character and not scrap:
            for item in character.inventory:
                if item.type == "Scrap":
                    return item

        return scrap

    def checkCoolDownEnded(self):
        '''
        check if the item is in cooldown
        '''
        tick = self.getTick()
        if (
            tick < self.coolDownTimer + self.coolDown
            and not self.charges
        ):
            return False
        return True

    def checkTargetFull(self):
        '''
        check if the output spots have space
        '''
        targetPos = (self.xPosition + 1, self.yPosition, self.zPosition)
        targetFull = False
        itemList = self.container.getItemByPosition(targetPos)

        #if len(itemList) > 15:
        if len(itemList) > 0:
            targetFull = True
        for item in itemList:
            if item.walkable is False:
                targetFull = True

        return (targetFull,itemList)

    def getTick(self):
        '''
        get the current time
        '''
        tick = src.gamestate.gamestate.tick
        if self.container and isinstance(self.container,src.rooms.Room):
            tick = self.container.timeIndex
        return tick

    def apply(self, character):
        '''
        handle a character trying to use this item to produce a metal bar

        Parameters:
            character: the character trying to use the item
        '''

        if not self.container:
            character.addMessage("this machine has be somewhere to be used")
            return

        character.changed("operated machine",{"character":character,"machine":self})

        if not self.bolted:
            character.addMessage(
                "this machine needs to be bolted down to be used"
            )
            return

        tick = self.getTick()

        if not self.checkCoolDownEnded():
            character.addMessage(
                f"cooldown not reached. Wait {self.coolDown - (tick - self.coolDownTimer)} ticks"
            )
            self.runCommand("cooldown", character)
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
            return

        (targetFull,itemList) = self.checkTargetFull()
        if targetFull:
            character.addMessage(
                "the target area is full, the machine can not produce anything"
            )
            self.runCommand("targetFull", character)
            color = "#740"
            if itemList[0].type != "MetalBars":
                color = "#f00"
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec(color, "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec(color, "black"),"][")})
            return

        scrap = self.checkForInputScrap(character)
        if not scrap:
            character.addMessage("no scraps available")
            self.runCommand("material Scrap", character)
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"[]")})
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = tick

        character.addMessage("you produce a metal bar")

        # remove resources
        if scrap.amount <= 1:
            if scrap in character.inventory:
                character.removeItemFromInventory(scrap)
            else:
                self.container.removeItem(scrap)
        else:
            scrap.amount -= 1
            scrap.setWalkable()
        self.container.addAnimation(scrap.getPosition(),"scrapChange",2,{})

        self.container.addAnimation(self.getPosition(),"charsequence",2,{"chars":[
            (src.interaction.urwid.AttrSpec("#aaa", "black"),"R["),
            (src.interaction.urwid.AttrSpec("#aaa", "black"),"R-"),
            (src.interaction.urwid.AttrSpec("#aaa", "black"),"RK"),
           ]})

        # spawn the metal bar
        new = src.items.itemMap["MetalBars"]()
        self.container.addItem(
            new, (self.xPosition + 1, self.yPosition, self.zPosition)
        )
        self.container.addAnimation(new.getPosition(),"showchar",2,{"char":"++"})
        character.changed("producedItem", {"item":new})

        #HACK: sound effect
        if src.gamestate.gamestate.mainChar in self.container.characters:
            src.interaction.playSound("scrapcompactorUsed","machines")
        self.runCommand("success", character)

    def getConfigurationOptions(self, character):
        '''
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        '''

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def getLongInfo(self):
        '''
        returns a longer than normal description text

        Returns:
           a longer than normal description text
        '''

        text = super().getLongInfo()

        directions = "west"
        if self.level > 1:
            directions += "/south"
        if self.level > 2:
            directions += "/north"
        text += f"""
Place scrap to the {directions} of the machine and activate it

After using this machine you need to wait {self.coolDown} ticks till you can use this machine again.
"""

        tick = src.gamestate.gamestate.tick
        if self.container and isinstance(self.container,src.rooms.Room):
            tick = self.container.timeIndex
        coolDownLeft = self.coolDown - (
            tick - self.coolDownTimer
        )
        if coolDownLeft > 0:
            text += f"""
Currently you need to wait {coolDownLeft} ticks to use this machine again.

"""
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges

""" % (
                self.charges
            )
        else:
            text += """
Currently the machine has no charges

"""

        text += """
this is a level %s item

""" % (
            self.level
        )
        return text

# register the item
src.items.addType(ScrapCompactor)
