import urwid

class TileMapping(object):
    def __init__(self,mode):
        self.modes = {"testTiles":"","pseudeUnicode":""}
        self.setRenderingMode(mode)

    def setRenderingMode(self,mode):
        if mode not in self.modes:
            mode = "testTiles"

        if mode == "testTiles":
            import config.tileMap as rawTileMap
        self.mode = mode

        import inspect
        self.indexedMapping = []
        raw = inspect.getmembers(rawTileMap, lambda a:not(inspect.isroutine(a)))
        counter = 0
        for item in raw:
            if item[0].startswith("__"):
                continue

            if isinstance(item[1], list):
                subList = []
                for subItem in item[1]:
                    self.indexedMapping.append(subItem)
                    subList.append(counter)
                    counter += 1
                setattr(self, item[0], subList)
            elif isinstance(item[1], dict):
                subDict = {}
                for k,v in item[1].items():
                    subDict[k] = counter
                    self.indexedMapping.append(v)
                    counter += 1
                setattr(self, item[0], subDict)
            else:
                self.indexedMapping.append(item[1])
                setattr(self, item[0], counter)
                counter += 1

class DisplayMapping(object):
    def __init__(self,mode):
        self.modes = {"unicode":"","pureASCII":""}
        self.setRenderingMode(mode)

    def setRenderingMode(self,mode):
        if mode not in self.modes:
            mode = "pureASCII"

        if mode == "unicode":
            import config.displayChars as rawDisplayChars
        elif mode == "pureASCII":
            import config.displayChars_fallback as rawDisplayChars
        self.mode = mode

        import inspect
        self.indexedMapping = []
        raw = inspect.getmembers(rawDisplayChars, lambda a:not(inspect.isroutine(a)))
        counter = 0
        for item in raw:
            if item[0].startswith("__"):
                continue

            if isinstance(item[1], list):
                subList = []
                for subItem in item[1]:
                    self.indexedMapping.append(subItem)
                    subList.append(counter)
                    counter += 1
                setattr(self, item[0], subList)
            elif isinstance(item[1], dict):
                subDict = {}
                for k,v in item[1].items():
                    subDict[k] = counter
                    self.indexedMapping.append(v)
                    counter += 1
                setattr(self, item[0], subDict)
            else:
                self.indexedMapping.append(item[1])
                setattr(self, item[0], counter)
                counter += 1

class Canvas(object):
    def __init__(self,size=(41,41),chars=None,defaultChar="::",coordinateOffset=(0,0),shift=(0,0),displayChars=None):
        self.size = size
        self.coordinateOffset = coordinateOffset
        # this should be temporary only and be solved by overlaying canvas
        self.shift = shift
        self.defaultChar = defaultChar
        self.displayChars = displayChars
        self.tileMapping = TileMapping("testTiles")

        self.chars = []
        for x in range(0,41):
            line = []
            for y in range(0,41):
                line.append(defaultChar)
            self.chars.append(line)

        for x in range(self.coordinateOffset[0],self.coordinateOffset[0]+self.size[0]):
            for y in range(self.coordinateOffset[1],self.coordinateOffset[1]+self.size[1]):
                self.setPixel(x,y,chars[x][y])

    def setPixel(self,x,y,char):
        x -= self.coordinateOffset[0]
        y -= self.coordinateOffset[1]

        if x < 0 or y < 0 or x > self.size[0] or y > self.size[1]:
            return 
        self.chars[x][y] = char

    def getUrwirdCompatible(self):
        out = []

        if self.shift[0] > 0:
            for x in range(0,self.shift[0]):
                 out.append("\n")
        
        for line in self.chars:
            if self.shift[1] > 0:
                for x in range(0,self.shift[1]):
                    out.append((urwid.AttrSpec("default","default"),"  "))

            for char in line:
                if isinstance(char, int):
                    out.append(self.displayChars.indexedMapping[char])
                else:
                    out.append(char)
            out.append("\n")
        return out

    def setPygameDisplay(self,pydisplay,pygame):
        
        pydisplay.fill((0,0,0))
        counterY = 0
        for line in self.chars:
            counterX = 0
            for char in line:
                if isinstance(char, int):
                    try:
                        image = self.tileMapping.indexedMapping[char]
                        pydisplay.blit(image,(counterX*10, counterY*10))
                    except:
                        pass
                counterX += 1
            counterY += 1

        pygame.display.update()
