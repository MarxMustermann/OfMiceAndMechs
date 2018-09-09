'''
remove loops from a path
bad pattern: path should be generated in such a way this is not needed
'''
def removeLoops(path):
    # count the amount of occourances of each position in the path
    found = {}
    for waypoint in path:
        if waypoint in found:
            found[waypoint] += 1
        else:
            found[waypoint] = 1

    # copy path till the first position that's occours more than once
    newPath = []
    brokeAt = None
    for waypoint in path:
        if found[waypoint] == 1:
            newPath.append(waypoint)
        else:
            brokeAt = waypoint
            break

    if brokeAt:
        # get last ocourance of the first duplicate waypoint
        # bad code: non intuitive exception handling
        try:
            lastIndex = 0
            while True:
                lastIndex = path.index(waypoint,lastIndex+1)
        except ValueError as e:
            pass

        # copy the path after the last occourance of the cutoff position
        # bad code: should be using extend or something
        counter = lastIndex
        pathLen = len(path)
        while counter < pathLen:
            newPath.append(path[counter])
            counter += 1

        # recusivly remove remaining loops
        newPath = removeLoops(newPath)

    return newPath

'''
naively calculate a path uses a pracalcated standard path to speed up 
bad code: this assumes no obstacles resulting in bugs and odd workarounds. So this should not be used really.
bad code: Alternative implementations exist but not everywhere yet
'''
def calculatePath(startX,startY,endX,endY,walkingPath):
    # get path with loops
    path = calculatePathReal(startX,startY,endX,endY,walkingPath)

    # remove loops
    return removeLoops(path)

'''
recusively calcualate a unoptimized path
'''
def calculatePathReal(startX,startY,endX,endY,walkingPath):
    path = []

    # bad code: return empty path on broken input
    if None in (startX,startY,endX,endY):
        return []

    # stop recursion at exit condition
    if (startX == endX and startY == endY):
        return []

    # add hardcoded solution to the real easy cases
    if (startX == endX+1 and startY == endY):
        return [(endX,endY)]
    if (startX == endX-1 and startY == endY):
        return [(endX,endY)]
    if (startX == endX and startY == endY+1):
        return [(endX,endY)]
    if (startX == endX and startY == endY-1):
        return [(endX,endY)]

    # bad code: this code doesn't actually do anything
    # bug: this code should select whether or not the path is looped
    circlePath = True
    if (startY > 11 and not startX==endX):
        circlePath = True
    elif (startY < 11):
        circlePath = True

    
    # calculate movement on the default path
    if (startX,startY) in walkingPath and (endX,endY) in walkingPath:
        # get the start/end indices
        # bad code: should use a build in function to find indices
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

        # extract and return the correct part of the default path
        distance = startIndex-endIndex
        if distance > 0:
            if circlePath:
                if distance < len(walkingPath)/2:
                    # use the path between start and end staying within the path
                    result = []
                    result.extend(reversed(walkingPath[endIndex:startIndex]))
                    return result
                else:
                    # use the path between start and end connecting over the ends of the path
                    result = []
                    result.extend(walkingPath[startIndex:])
                    result.extend(walkingPath[:endIndex+1])
                    return result
            else:
                # bad code: impossible to reach
                result = []
                result.extend(reversed(walkingPath[endIndex:startIndex]))
                return result
        else:
            if circlePath:
                if (-distance) <= len(walkingPath)/2:
                    # use the path between start and end staying within the path
                    return walkingPath[startIndex+1:endIndex+1]
                else:
                    # use the path between start and end connecting over the ends of the path
                    result = []
                    result.extend(reversed(walkingPath[:startIndex]))
                    result.extend(reversed(walkingPath[endIndex:]))
                    return result
            else:
                # bad code: impossible to reach
                return walkingPath[startIndex+1:endIndex+1]

    # calculate movement to the default path
    elif (endX,endY) in walkingPath:
        # select the nearest waypoint
        nearestPoint = None
        lowestDistance = 1234567890 # bad code: silly constant
        for waypoint in walkingPath:
            distance = abs(waypoint[0]-startX)+abs(waypoint[1]-startY)
            if lowestDistance > distance:
                lowestDistance = distance
                nearestPoint = waypoint

        if (endX,endY) == nearestPoint:
            # break recursion if this is already shortest path
            pass
        else:
            # stitch path together from recursive calculation
            result = []
            result.extend(calculatePathReal(startX,startY,nearestPoint[0],nearestPoint[1],walkingPath))
            result.extend(calculatePathReal(nearestPoint[0],nearestPoint[1],endX,endY,walkingPath))
            return result

    # calculate movement from the default path 
    elif (startX,startY) in walkingPath:
        # select the nearest waypoint
        nearestPoint = None
        lowestDistance = 1234567890 # bad code: silly constant
        for waypoint in walkingPath:
            distance = abs(waypoint[0]-endX)+abs(waypoint[1]-endY)
            if lowestDistance > distance:
                lowestDistance = distance
                nearestPoint = waypoint

        if (startX,startY) == nearestPoint:
            # break recursion if this is already shortest path
            pass
        else:
            # stitch path together from recursive calculation
            result = []
            result.extend(calculatePathReal(startX,startY,nearestPoint[0],nearestPoint[1],walkingPath))
            result.extend(calculatePathReal(nearestPoint[0],nearestPoint[1],endX,endY,walkingPath))
            return result
    # split calcualtion into to - within - from default path
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

        # stitch path together from recursive calculation
        path.extend(calculatePathReal(startX,startY,startPoint[0],startPoint[1],walkingPath))
        path.extend(calculatePathReal(startPoint[0],startPoint[1],endPoint[0],endPoint[1],walkingPath))
        path.extend(calculatePathReal(endPoint[0],endPoint[1],endX,endY,walkingPath))
        
        return path            

    # get the distance vector
    diffX = startX-endX
    diffY = startY-endY
        
    # walk the distance vector
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

    return path
