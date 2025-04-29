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


def draw_frame_text(con, width, height, t, x, y):
    for cx in range(x - 2, x + width+1):
        for cy in range(y - 2, y + height+1):
            con.rgb[cx, cy] = ord(" "), (0, 0, 0), (0, 0, 0)
    for cx in range(x - 2, x + width+1):
        con.rgb[cx, y - 2] = ord("-"), (255, 255, 255), (0, 0, 0)
        con.rgb[cx, y + height+1] = ord("-"), (255, 255, 255), (0, 0, 0)
    for cy in range(y - 2, y + height+1):
        con.rgb[x - 2, cy] = ord("|"), (255, 255, 255), (0, 0, 0)
        con.rgb[x + width+1, cy] = ord("|"), (255, 255, 255), (0, 0, 0)

    con.rgb[x - 2, y - 2] = ord("+"), (255, 255, 255), (0, 0, 0)
    con.rgb[x - 2, y - 3] = ord("|"), (255, 255, 255), (0, 0, 0)
    con.rgb[x - 3, y - 2] = ord("-"), (255, 255, 255), (0, 0, 0)

    con.rgb[x + width+1, y - 2] = ord("+"), (255, 255, 255), (0, 0, 0)
    con.rgb[x + width+1, y - 3] = ord("|"), (255, 255, 255), (0, 0, 0)
    con.rgb[x + width+2, y - 2] = ord("-"), (255, 255, 255), (0, 0, 0)

    con.rgb[x - 2, y + height + 1] = ord("+"), (255, 255, 255), (0, 0, 0)
    con.rgb[x - 2, y + height + 2] = ord("|"), (255, 255, 255), (0, 0, 0)
    con.rgb[x - 3, y + height + 1] = ord("-"), (255, 255, 255), (0, 0, 0)

    con.rgb[x + width + 1, y + height + 1] = ord("+"), (255, 255, 255), (0, 0, 0)
    con.rgb[x + width + 1, y + height + 2] = ord("|"), (255, 255, 255), (0, 0, 0)
    con.rgb[x + width + 2, y + height+1] = ord("-"), (255, 255, 255), (0, 0, 0)

    con.print_box(x, y, width, height, t, (255, 255, 255), (0, 0, 0), tcod.constants.BKGND_SET, tcod.constants.CENTER)


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
                    src.interaction.tcodContext.present(
                        src.interaction.tcodConsole, integer_scaling=True, keep_aspect=True
                    )
