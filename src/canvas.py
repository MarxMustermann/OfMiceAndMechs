##########################################################################
###
##    drawing and related code should be here
#     bad code: drawstuff is everywhere
#
##########################################################################

# import basic libs
# bad code: should not be imported when tile based display only
import urwid

class Mapping(object):

    mappedThings = {}
    globalCounter = [0] # non intuitive: list to make counter same object for all instances

    def buildMap(self):

        rawConfig = self.loadMapping()

        # (re)build the tile mapping
        import inspect
        self.indexedMapping = []
        raw = inspect.getmembers(rawConfig, lambda a:not(inspect.isroutine(a)))
        for item in raw:
            if item[0].startswith("__"):
                # ignore internal state
                continue

            if isinstance(item[1], list):
                # convert lists to lists
                subList = []
                counter = 0
                for subItem in item[1]:
                    if not item[0] in self.mappedThings:
                        self.mappedThings[item[0]] = []
                    if len(self.mappedThings[item[0]])-1 < counter: 
                        while len(self.mappedThings[item[0]])-1 < counter: 
                            self.mappedThings[item[0]].append(None)
                        self.mappedThings[item[0]][counter] = self.globalCounter[0]
                        self.globalCounter[0] += 1

                    index = self.mappedThings[item[0]][counter]
                    self.mapToIndex(index,subItem)
                    subList.append(index)
                    counter += 1
                setattr(self, item[0], subList)

            elif isinstance(item[1], dict):
                # convert dicts to dicts
                subDict = {}
                for k,v in item[1].items():
                    if not item[0] in self.mappedThings: 
                        self.mappedThings[item[0]] = {}
                
                    if not k in self.mappedThings:
                        self.mappedThings[item[0]][k] = self.globalCounter[0]
                        self.globalCounter[0] += 1

                    index = self.mappedThings[item[0]][k]
                    subDict[k] = index
                    self.mapToIndex(index,v)

                setattr(self, item[0], subDict)

            else:
                # add non special entries
                if not item[0] in self.mappedThings: 
                    self.mappedThings[item[0]] = self.globalCounter[0]
                    self.globalCounter[0] += 1

                index = self.mappedThings[item[0]]
                self.mapToIndex(index,item[1])
                setattr(self, item[0], index)

    def mapToIndex(self,index,value):
        while len(self.indexedMapping)-1 < index:
            self.indexedMapping.append(None)
        self.indexedMapping[index] = value

"""
this maps an abstract representation to tiles.
"""
class TileMapping(Mapping):
    """
    basic state setting
    bad code: hardcoded modes for now
    """
    def __init__(self,mode):
        super().__init__()
        self.modes = {"testTiles":"","pseudeUnicode":""}
        self.setRenderingMode(mode)

    """
    set the rendering mode AND recalculate the tile map
    """
    def setRenderingMode(self,mode):
        # sanatize input
        # bad code: should raise error
        if mode not in self.modes:
            mode = "testTiles"

        # set mode
        self.mode = mode

        self.buildMap()

    def loadMapping(self):
        # bad pattern: no way to load arbitrary files
        if self.mode == "testTiles":
            # bad code: reimport the config as library, i don't think this is a good thing to do
            import config.tileMap as rawConfig
        return rawConfig

"""
this maps an abstract representation to actual chars.
This allows to switch representation during runtime and
is intended to allow for expansions like the tile based 
renderer
"""
class DisplayMapping(Mapping):
    """
    basic state setting
    bad code: hardcoded modes for now
    """
    def __init__(self,mode):
        super().__init__()
        self.modes = {"unicode":"","pureASCII":""}
        self.setRenderingMode(mode)

    """
    set the rendering mode AND recalculate the char map
    """
    def setRenderingMode(self,mode):
        # sanatize input
        # bad code: should raise exception
        if mode not in self.modes:
            mode = "pureASCII"

        # set mode
        self.mode = mode

        self.buildMap()

    def loadMapping(self):
        if self.mode == "unicode":
            import config.displayChars as rawConfig
        elif self.mode == "pureASCII":
            import config.displayChars_fallback as rawConfig
        return rawConfig


"""
The canvas is supposed to hold the content of a piece screen.
It is used to allow for pixel setting and to be able to cache rendered state.
Recursive canvases would be great but are not implemented yet.

bad code: actual rendering beyond the abstracted form (urwid formatting, tiles) is done here
"""
class Canvas(object):
    """
    set up state AND fill the canvas with the (default) chars
    bad code: should be split into 2 methods
    """
    def __init__(self,size=(41,41),chars=None,defaultChar="::",coordinateOffset=(0,0),shift=(0,0),displayChars=None):
        # set basic information
        self.size = size
        self.coordinateOffset = coordinateOffset
        self.shift = shift # this should be temporary only and be solved by overlaying canvas
        self.defaultChar = defaultChar
        self.displayChars = displayChars

        # bad code: i don't think try should be used like that
        # bad code: this should be somewhere else
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
                self.setPseudoPixel(x,y,chars[x][y])

    """
    plain and simple pseudo pixel setting
    """
    def setPseudoPixel(self,x,y,char):
        # shift coordinates
        x -= self.coordinateOffset[0]
        y -= self.coordinateOffset[1]

        # validate input
        if x < 0 or y < 0 or x > self.size[0] or y > self.size[1]:
            # bad code: should raise an out of bounds error
            return 

        # set pixel
        self.chars[x][y] = char

    """
    get the Canvas prepared for use with urwid,
    this basically returns urwid.AttrSpecs
    bad code: urwid specific code should be in one place not everywhere
    """
    def getUrwirdCompatible(self):
        # the to be result
        out = []

        # add newlines on top
        if self.shift[0] > 0:
            for x in range(0,self.shift[0]):
                 out.append("\n")
        
        # add rendered content
        for line in self.chars:
            # add spaces left of the canvas
            if self.shift[1] > 0:
                for x in range(0,self.shift[1]):
                    out.append((urwid.AttrSpec("default","default"),"  "))

            # add this lines content
            for char in line:
                if isinstance(char, int):
                    if self.displayChars.indexedMapping[char] == None:
                        debugMessages.append("failed render"+str(char)+" "+str(self.displayChars.indexedMapping[char-10])+" "+str(self.displayChars.indexedMapping[char+10]))
                    else:
                        out.append(self.displayChars.indexedMapping[char])
                else:
                    out.append(char)

            # start new line
            out.append("\n")
        return out

    """
    draw the display onto a pygame display
    bad code: pygame specific code should be in one place not everywhere
    bad code: the method should return a rendered result instead of rendering directly
    """
    def setPygameDisplay(self,pydisplay,pygame,tileSize):
        # fill game area
        pydisplay.fill((0,0,0))

        # add rendered content
        # bad pattern: this rendering relies on strict top left to botom right rendering with overlapping tiles to create perspective without having propper mechanism to enforce and control this
        counterY = 0
        for line in self.chars:
            counterX = 0
            for char in line:
                # bad code: only tiles are rendered. special chars and text is not rendered
                # bad code: colour information is lost
                if isinstance(char, int):
                    # scale the tile
                    # bad code: rescales each tile individually and on each render
                    # bad code: exceptions should be prevented/handled not hidden
                    try:
                        image = self.tileMapping.indexedMapping[char]
                        if not tileSize == 10:
                            image = pygame.transform.scale(image,(int(tileSize*(image.get_width()/10)),int(tileSize*(image.get_height()/10))))
                        pydisplay.blit(image,(counterX*(tileSize+1), counterY*(tileSize+1)))
                    except:
                        pass
                counterX += 1
            counterY += 1

        # refresh display
        pygame.display.update()
