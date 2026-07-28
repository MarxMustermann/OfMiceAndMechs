import math
import random

import tcod

import config
import src


def clamp(n, min, max):
    if n < min:
        return min
    if n > max:
        return max
    return n

def draw_frame_text(removeme, width, height, text, x, y, center=True):

    line_width = 5
    padding = 15

    sdl_renderer2 = src.interaction.sdl_renderer2
    x_pixels = x*src.interaction.tileWidth
    y_pixels = y*src.interaction.tileHeight
    width_pixels = width*src.interaction.tileWidth
    height_pixels = height*src.interaction.tileHeight

    root_console = tcod.console.Console(width, height, order="F")
    src.interaction.printUrwidToTcod(text, (0,0), explecitConsole=root_console)

    atlas = tcod.render.SDLTilesetAtlas(sdl_renderer2,src.interaction.tileset_ui)
    console_render = tcod.render.SDLConsoleRender(atlas)
    renderedToTexture = console_render.render(root_console)
    sdl_renderer2.copy(
                renderedToTexture,
                (0,0,renderedToTexture.width,renderedToTexture.height),
                (x_pixels+padding,y_pixels+padding,renderedToTexture.width,renderedToTexture.height),
            )

    sdl_renderer2.draw_color = (150,150,150,255)
    sdl_renderer2.fill_rect((x_pixels,y_pixels,width_pixels+padding*2,line_width))
    sdl_renderer2.fill_rect((x_pixels,y_pixels,line_width,height_pixels+padding*2))
    sdl_renderer2.fill_rect((x_pixels+width_pixels+2*padding-line_width,y_pixels,line_width,height_pixels+padding*2))
    sdl_renderer2.fill_rect((x_pixels,y_pixels+height_pixels+2*padding-line_width,width_pixels+padding*2,line_width))

def fade_between_consoles_rgb(current, target, t):
    transition_array = ["?", "/", "."]
    for width in range(current.shape[0]):
        for height in range(current.shape[1]):
            transition_state = int(t * 4)
            match transition_state:
                case 0:
                    src.interaction.tcodConsole.rgb[width, height]["ch"] = current[width, height]["ch"]
                case 4:
                    src.interaction.tcodConsole.rgb[width, height]["ch"] = target[width, height]["ch"]
                case _:
                    src.interaction.tcodConsole.rgb[width, height]["ch"] = ord(transition_array[transition_state - 1])
            src.interaction.tcodConsole.rgb[width, height]["fg"] = src.pseudoUrwid.AttrSpec.interpolate(
                current[width, height]["fg"], target[width, height]["fg"], t
            )
            src.interaction.tcodConsole.rgb[width, height]["bg"] = src.pseudoUrwid.AttrSpec.interpolate(
                current[width, height]["bg"], target[width, height]["bg"], t
            )

def distance_between_points(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])


def getRandomName(seed1=0, seed2=None):
    """
    generates a random name

    Parameters:
        seed1: rng seed
        seed2: rng seed

    Returns:
        the generated name
    """

    if seed2 is None:
        seed2 = seed1 + (seed1 // 5)

    firstName = config.names.characterFirstNames[seed1 % len(config.names.characterFirstNames)]
    lastName = config.names.characterLastNames[seed2 % len(config.names.characterLastNames)]

    return f"{firstName} {lastName}"


def drawLine(x1, y1, x2, y2, func):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    length = dx if dx > dy else dy
    for i in range(int(length) + 1):
        t = i / length
        x = x1 + int(t * (x2 - x1))
        y = y1 + int(t * (y2 - y1))
        func(x, y)


def drawCircle(radius):
    text = ""
    points = []
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            if int(math.sqrt(x * x + y * y)) == radius:
                text += "* "
                points.append((x, y))
            else:
                text += "  "
        text += "\n"

    return (points, text)


refvec = [0, +1]


def clockwiseangle_and_distance(origin, point):
    # Vector between point and the origin: v = p - o
    vector = [point[0] - origin[0], point[1] - origin[1]]
    # Length of vector: ||v||
    lenvector = math.hypot(vector[0], vector[1])
    # If length is zero there is no angle
    if lenvector == 0:
        return -math.pi, 0
    # Normalize vector: v/||v||
    normalized = [vector[0] / lenvector, vector[1] / lenvector]
    dotprod = normalized[0] * refvec[0] + normalized[1] * refvec[1]  # x1*x2 + y1*y2
    diffprod = refvec[1] * normalized[0] - refvec[0] * normalized[1]  # x1*y2 - y1*x2
    angle = math.atan2(diffprod, dotprod)
    # Negative angles represent counter-clockwise angles so we need to subtract them
    # from 2*pi (360 degrees)
    if angle < 0:
        return 2 * math.pi + angle, lenvector
    # I return first the angle because that's the primary sorting criterium
    # but if two vectors have the same angle then the shorter distance should come first.
    return angle, lenvector


def percentage_chance(p):
    return random.random() < p


def deal_with_window_events(exception=None):
    for event in tcod.event.get():
        if isinstance(event, tcod.event.Quit):
            raise SystemExit()
        if isinstance(event, tcod.event.WindowEvent):
            match event.type:
                case "WINDOWCLOSE":
                    if exception:
                        raise exception
                    raise SystemExit()
                case "WindowHidden":
                    pass
                case _:
                    src.interaction.tcodPresent()


def power_distribution(low: int | float, high: int | float, power=2.0) -> float:
    """
    return random values between low and high while preferring **lower** values according to skewed curve/distribution
    """
    u = random.random() ** power
    return low + (high - low) * u

def reversed_power_dist(low: int | float, high: int | float, power=2.0) -> float:
    """
    return random values between low and high while preferring **higher** values according to skewed curve/distribution
    """
    u = 1 - random.random() ** power
    return low + (high - low) * u
