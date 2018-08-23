import urwid

"""
this maps an abstract representation to tiles.
bad code: indices have to be the same as for DisplayMapping
"""
class TileMapping(object):
    """
    bad code: hardcoded modes for now
    """
    def __init__(self,mode):
        self.modes = {"testTiles":"","pseudeUnicode":""}
        self.setRenderingMode(mode)

    """
    set the rendering mode AND recalculate the tile map
    """
    def setRenderingMode(self,mode):
        # sanatize input
        if mode not in self.modes:
            mode = "testTiles"

        if mode == "testTiles":
            # bad code: reimport the config as library, i don't think this is a good thing to do
            import config.tileMap as rawTileMap

        # set mode flag
        self.mode = mode

        # rebuild the tile mapping
        import inspect
        self.indexedMapping = []
        raw = inspect.getmembers(rawTileMap, lambda a:not(inspect.isroutine(a)))
        counter = 0
        for item in raw:
            if item[0].startswith("__"):
                continue

            if isinstance(item[1], list):
                # convert lists to lists
                subList = []
                for subItem in item[1]:
                    self.indexedMapping.append(subItem)
                    subList.append(counter)
                    counter += 1
                setattr(self, item[0], subList)

            elif isinstance(item[1], dict):
                # convert dicts to dicts
                subDict = {}
                for k,v in item[1].items():
                    subDict[k] = counter
                    self.indexedMapping.append(v)
                    counter += 1
                setattr(self, item[0], subDict)

            else:
                # convert non special entries
                self.indexedMapping.append(item[1])
                setattr(self, item[0], counter)
                counter += 1

"""
this maps an abstract representation to actual chars.
This allows to switch representation during runtime and
is intended to allow for expansions like the tile based 
renderer

bad code: The index used is calculated based on line position
in the config file. This is a bad idea and casuses bugs at the 
time of writing.
"""
class DisplayMapping(object):
    """
    bad code: hardcoded modes for now
    """
    def __init__(self,mode):
        self.modes = {"unicode":"","pureASCII":""}
        self.setRenderingMode(mode)

    """
    set the rendering mode AND recalculate the char map
    """
    def setRenderingMode(self,mode):
        # sanatize input
        if mode not in self.modes:
            mode = "pureASCII"

        # import the appropriate config
        if mode == "unicode":
            import config.displayChars as rawDisplayChars
        elif mode == "pureASCII":
            import config.displayChars_fallback as rawDisplayChars
        self.mode = mode

        # rebuild the tile mapping
        import inspect
        self.indexedMapping = []
        raw = inspect.getmembers(rawDisplayChars, lambda a:not(inspect.isroutine(a)))
        counter = 0
        for item in raw:
            if item[0].startswith("__"):
                continue

            if isinstance(item[1], list):
                # convert lists to lists
                subList = []
                for subItem in item[1]:
                    self.indexedMapping.append(subItem)
                    subList.append(counter)
                    counter += 1
                setattr(self, item[0], subList)

            elif isinstance(item[1], dict):
                # convert dicts to dicts
                subDict = {}
                for k,v in item[1].items():
                    subDict[k] = counter
                    self.indexedMapping.append(v)
                    counter += 1
                setattr(self, item[0], subDict)

            else:
                # convert non special entries
                self.indexedMapping.append(item[1])
                setattr(self, item[0], counter)
                counter += 1

"""
The canvas is supposed to hold the content of a piece drawn things.
It is used to allow for pixel setting and to be able to cache rendered state.
Recursive canvases would be great but are not implemented yet.

bad code: actual rendering beyond the abstracted form is done here
"""
class Canvas(object):
    """
    save basic information AND fill the canvas with the (default) chars
    """
    def __init__(self,size=(41,41),chars=None,defaultChar="::",coordinateOffset=(0,0),shift=(0,0),displayChars=None):
        # set basic information
        self.size = size
        self.coordinateOffset = coordinateOffset
        self.shift = shift # this should be temporary only and be solved by overlaying canvas
        self.defaultChar = defaultChar
        self.displayChars = displayChars
        # bad code: i don't think try should be used like that
        try:
            self.tileMapping = TileMapping("testTiles")
        except:
            pass

        # fill the canvas with the default char
        self.chars = []
        for x in range(0,41):
            line = []
            for y in range(0,41):
                line.append(defaultChar)
            self.chars.append(line)

        # carry the supplied canvas
        for x in range(self.coordinateOffset[0],self.coordinateOffset[0]+self.size[0]):
            for y in range(self.coordinateOffset[1],self.coordinateOffset[1]+self.size[1]):
                self.setPixel(x,y,chars[x][y])

    """
    plain and simple pixel checking 
    """
    def setPixel(self,x,y,char):
        x -= self.coordinateOffset[0]
        y -= self.coordinateOffset[1]

        if x < 0 or y < 0 or x > self.size[0] or y > self.size[1]:
            return 

        self.chars[x][y] = char

    """
    get the Canvas prepared for use with urwid,
    this basically returns urwid.AttrSpecs
    bad code: urwid specific code should be in one place not everywhere
    """
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

    """
    draw the display onto a pygame display
    bad code: pygame specific code should be in one place not everywhere
    bad code: the method should return a rendered result instead of rendering directly
    """
    def setPygameDisplay(self,pydisplay,pygame,tileSize):
        pydisplay.fill((0,0,0))
        counterY = 0
        for line in self.chars:
            counterX = 0
            for char in line:
                if isinstance(char, int):
                    # scale the tile
                    # bad code: rescales each tile individually and on each render
                    try:
                        image = self.tileMapping.indexedMapping[char]
                        if not tileSize == 10:
                            image = pygame.transform.scale(image,(int(tileSize*(image.get_width()/10)),int(tileSize*(image.get_height()/10))))
                        pydisplay.blit(image,(counterX*(tileSize+1), counterY*(tileSize+1)))
                    except:
                        pass
                counterX += 1
            counterY += 1

        pygame.display.update()
