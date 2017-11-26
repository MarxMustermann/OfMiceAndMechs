def calculatePath(startX,startY,endX,endY,walkingPath):
    path = calculatePathReal(startX,startY,endX,endY,walkingPath)

    index = 0
    lastFoundIndex = index
    for wayPoint in path:
        if wayPoint == (startX,startY):
            lastFoundIndex = index
        index += 1

    return path[lastFoundIndex:]

def calculatePathReal(startX,startY,endX,endY,walkingPath):
    import math
    path = []

    if (startX == endX and startY == endY):
        return []
    if (startX == endX+1 and startY == endY):
        return [(endX,endY)]
    if (startX == endX-1 and startY == endY):
        return [(endX,endY)]
    if (startX == endX and startY == endY+1):
        return [(endX,endY)]
    if (startX == endX and startY == endY-1):
        return [(endX,endY)]

    circlePath = True
    if (startY > 11 and not startX==endX):
        circlePath = True
    elif (startY < 11):
        circlePath = True

    if (startX,startY) in walkingPath and (endX,endY) in walkingPath:
        startIndex = None
        index = 0
        for wayPoint in walkingPath:
            if wayPoint == (startX,startY):
                startIndex = index
            index += 1
        endIndex = None
        index = 0
        for wayPoint in walkingPath:
            if wayPoint == (endX,endY):
                endIndex = index
            index += 1

        distance = startIndex-endIndex
        if distance > 0:
            if circlePath:
                if distance < len(walkingPath)/2:
                    result = []
                    result.extend(reversed(walkingPath[endIndex:startIndex]))
                    return result
                else:
                    result = []
                    result.extend(walkingPath[startIndex:])
                    result.extend(walkingPath[:endIndex+1])
                    return result
            else:
                result = []
                result.extend(reversed(walkingPath[endIndex:startIndex]))
                return result
        else:
            if circlePath:
                if (-distance) <= len(walkingPath)/2:
                    return walkingPath[startIndex+1:endIndex+1]
                else:
                    result = []
                    result.extend(reversed(walkingPath[:startIndex]))
                    result.extend(reversed(walkingPath[endIndex:]))
                    return result
            else:
                return walkingPath[startIndex+1:endIndex+1]

    elif (endX,endY) in walkingPath:
        nearestPoint = None
        lowestDistance = 1234567890
        for waypoint in walkingPath:
            distance = abs(waypoint[0]-startX)+abs(waypoint[1]-startY)
            if lowestDistance > distance:
                lowestDistance = distance
                nearestPoint = waypoint

        if (endX,endY) == nearestPoint:
            pass
        else:
            result = []
            result.extend(calculatePathReal(startX,startY,nearestPoint[0],nearestPoint[1],walkingPath))
            result.extend(calculatePathReal(nearestPoint[0],nearestPoint[1],endX,endY,walkingPath))
            return result

    elif (startX,startY) in walkingPath:
        nearestPoint = None
        lowestDistance = 1234567890
        for waypoint in walkingPath:
            distance = abs(waypoint[0]-endX)+abs(waypoint[1]-endY)
            if lowestDistance > distance:
                lowestDistance = distance
                nearestPoint = waypoint

        if (startX,startY) == nearestPoint:
            pass
        else:
            result = []
            result.extend(calculatePathReal(startX,startY,nearestPoint[0],nearestPoint[1],walkingPath))
            result.extend(calculatePathReal(nearestPoint[0],nearestPoint[1],endX,endY,walkingPath))
            return result
    else:
        path = []
        startPoint = None
        lowestDistance = 1234567890
        for waypoint in walkingPath:
            distance = abs(waypoint[0]-startX)+abs(waypoint[1]-startY)
            if lowestDistance > distance:
                lowestDistance = distance
                startPoint = waypoint

        endPoint = None
        lowestDistance = 1234567890
        for waypoint in walkingPath:
            distance = abs(waypoint[0]-endX)+abs(waypoint[1]-endY)
            if lowestDistance > distance:
                lowestDistance = distance
                endPoint = waypoint

        path.extend(calculatePathReal(startX,startY,startPoint[0],startPoint[1],walkingPath))
        path.extend(calculatePathReal(startPoint[0],startPoint[1],endPoint[0],endPoint[1],walkingPath))
        path.extend(calculatePathReal(endPoint[0],endPoint[1],endX,endY,walkingPath))
        
        return path            

    diffX = startX-endX
    diffY = startY-endY
        
    while (not diffX == 0) or (not diffY == 0):
            if (diffX<0):
                startX += 1
                diffX  += 1
            elif (diffX>0):
                startX -= 1
                diffX  -= 1
            elif (diffY<0):
                startY += 1
                diffY  += 1
            elif (diffY>0):
                startY -= 1
                diffY  -= 1
            path.append((startX,startY))

            """
                if (diffX<1):
                    endX-1
                    diffX+1
                else:
                    endX+1
                    diffX-1
                if (diffY<1):
                    endY-1
                    diffY+1
                else:
                    endY+1
                    diffY-1
                path.append((startX,startY))
            """
    return path
