import src

'''
'''
class GameTestingProducer(src.items.Item):
    type = "GameTestingProducer"

    def __init__(self,xPosition=None,yPosition=None, name="testing producer",creator=None, seed=0, possibleSources=[], possibleResults=[],noId=False):
        self.coolDown = 20
        self.coolDownTimer = -self.coolDown

        super().__init__(src.canvas.displayChars.gameTestingProducer,xPosition,yPosition,name=name,creator=creator)

        self.seed = seed
        self.baseName = name
        self.possibleResults = possibleResults
        self.possibleSources = possibleSources
        #self.change_apply_2(force=True)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])

    def apply(self,character,resultType=None):

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        token = None
        for item in character.inventory:
            if isinstance(item,src.items.Token):
                token = item

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown:
            character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = src.gamestate.gamestate.tick

        if token:
            self.change_apply_1(character,token)
        else:
            self.produce_apply(character)

    def change_apply_1(self,character,token):
        options = [(("yes",character,token),"yes"),(("no",character,token),"no")]
        self.submenue = src.interaction.SelectionMenu("Do you want to reconfigure the machine?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.change_apply_2

    def change_apply_2(self,force=False):
        if not force:
            if self.submenue.selection[0] == "no":
                return
            character = self.submenue.selection[1]
            token = self.submenue.selection[2]
            character.inventory.remove(token)

        seed = self.seed

        self.resource = None
        while not self.resource:
            self.product = self.possibleResults[seed%23%len(self.possibleResults)]
            self.resource = self.possibleSources[seed%len(self.possibleSources)]
            seed += 3+(seed%7)
            if self.product == self.resource:
                self.resource = None

        self.seed += self.seed%107
                    
        self.description = self.baseName + " | " + str(self.resource.type) + " -> " + str(self.product.type) 

    def produce_apply(self,character):

        # gather the resource
        itemFound = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,self.resource):
                   itemFound = item
                   break
        
        # refuse production without resources
        if not itemFound:
            character.addMessage("no "+self.resource.type+" available")
            return

        # remove resources
        self.room.removeItem(item)

        # spawn new item
        new = self.product(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.room.addItems([new])

        super().apply(character,silent=True)

    def getLongInfo(self):
        text = """
item: GameTestingProducer

description:
A game testing producer. It produces things.

Place metalbars to left/west and activate the machine to produce.

"""
        return text

src.items.addType(GameTestingProducer)
