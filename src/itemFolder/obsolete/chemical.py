import src

class Chemical(src.items.Item):
    type = "Chemical"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.fireCrystals)

        self.name = "chemical"
        self.composition = b"cccccggggg"

    def apply(self,character):
        import hashlib

        results = []
        counter = 0

        while 1:

            tmp = random.choice(["mix","shift"])

            if tmp == "mix":
                self.mix(character)
            elif tmp == "switch":
                self.mix(character)
            elif tmp == "shift":
                self.shift()

            test = hashlib.sha256(self.composition[0:9])
            character.addMessage(counter)

            result = int(test.digest()[-1])
            result2 = int(test.digest()[-2])
            if result < 15:
                character.addMessage(test.digest())
                character.addMessage(result)
                character.addMessage(result2)
                break

            counter += 1

        #character.addMessage(results)

    def shift(self):
        self.composition = self.composition[1:]+self.composition[0:1]

    def mix(self,character):
        part1 = self.composition[0:5]
        part2 = self.composition[5:10]

        self.composition = part1[0:1]+part2[0:1]+part1[1:2]+part2[1:2]+part1[2:3]+part2[2:3]+part1[3:4]+part2[3:4]+part1[4:5]+part2[4:5]

src.items.addType(Chemical)
