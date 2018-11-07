import os
import json
import random
import math

ROTATE_LEFT = "rotate-left"
ROTATE_RIGHT = "rotate-right"
ADVANCE = "advance"
RETREAT = "retreat"
SHOOT = "shoot"
PASS = "pass"

MOVE_UP =  {"top" : ADVANCE, "bottom" : ROTATE_LEFT, "right" : ROTATE_LEFT ,"left" : ROTATE_RIGHT }
MOVE_DOWN =  {"top" : ROTATE_LEFT, "bottom" : ADVANCE, "right" : ROTATE_RIGHT ,"left" : ROTATE_LEFT }
MOVE_RIGHT = {"top" : ROTATE_RIGHT, "bottom" : ROTATE_LEFT, "right" : ADVANCE ,"left" : ROTATE_LEFT }
MOVE_LEFT = {"top" : ROTATE_LEFT, "bottom" : ROTATE_RIGHT, "right" : ROTATE_RIGHT,"left" : ADVANCE }

def doesCellContainWall(walls, x, y):
    for wall in walls:
        if wall["x"] == x and wall["y"] == y:
            return True
    return False

def wallInFrontOfPenguin(body):
    xValueToCheckForWall = body["you"]["x"]
    yValueToCheckForWall = body["you"]["y"]
    bodyDirection = body["you"]["direction"]

    if bodyDirection == "top":
        yValueToCheckForWall -= 1
    elif bodyDirection == "bottom":
        yValueToCheckForWall += 1
    elif bodyDirection == "left":
        xValueToCheckForWall -= 1
    elif bodyDirection == "right":
        xValueToCheckForWall += 1
    return doesCellContainWall(body["walls"], xValueToCheckForWall, yValueToCheckForWall)

def moveTowardsPoint(body, pointX, pointY):
    penguinPositionX = body["you"]["x"]
    penguinPositionY = body["you"]["y"]
    plannedAction = PASS
    bodyDirection = body["you"]["direction"]

    if penguinPositionX < pointX:
        plannedAction =  MOVE_RIGHT[bodyDirection]
    elif penguinPositionX > pointX:
        plannedAction = MOVE_LEFT[bodyDirection]
    elif penguinPositionY < pointY:
        plannedAction = MOVE_DOWN[bodyDirection]
    elif penguinPositionY > pointY:
        plannedAction = MOVE_UP[bodyDirection]

    if plannedAction == ADVANCE and wallInFrontOfPenguin(body):
        plannedAction = SHOOT
    return plannedAction

def moveTowardsCenterOfMap(body):
    centerPointX = math.floor(body["mapWidth"] / 2)
    centerPointY = math.floor(body["mapHeight"] / 2)
    return moveTowardsPoint(body, centerPointX, centerPointY)

def visibleEnemy(body):
    if "x" in body["enemies"][0]:
        return True
    return False


def lineVertical(body):
    if body["enemies"][0]["x"] < body["you"]["x"]:
        if body["enemies"][0]["direction"] == "right":
            if body["you"]["direction"] == "left":
                return "both see"
            return "he sees"
        if body["you"]["direction"] == "left":
            return "you see"
    else:
        if body["enemies"][0]["direction"] == "left":
            if body["you"]["direction"] == "right":
                return "both see"
            return "he sees"
        if body["you"]["direction"] == "right":
            return "you see"

def lineHorisontal(body):
    if body["enemies"][0]["y"] < body["you"]["y"]:
        if body["enemies"][0]["direction"] == "bottom":
            if body["you"]["direction"] == "top":
                return "both see"
            return "he sees"
        if body["you"]["direction"] == "top":
            return "you see"
    else:
        if body["enemies"][0]["direction"] == "top":
            if body["you"]["direction"] == "bottom":
                return "both see"
            return "he sees"
        if body["you"]["direction"] == "bottom":
            return "you see"
    return "noone sees"

def rotateToEnemy(body):
    if body["enemies"][0]["x"] == body["you"]["x"]:
        if body["enemies"][0]["y"] < body["you"]["y"]:
            if body["you"]["direction"] == "right":
                return ROTATE_LEFT
            return ROTATE_RIGHT
        else:
            if body["you"]["direction"] == "right":
                return ROTATE_RIGHT
            return ROTATE_LEFT
    if body["enemies"][0]["x"] < body["you"]["x"]:
        if body["you"]["direction"] == "top":
            return ROTATE_LEFT
        return ROTATE_RIGHT
    else:
        if body["you"]["direction"] == "top":
            return ROTATE_RIGHT
        return ROTATE_RIGHT

def wallbetween(body):
    hisX = body["enemies"][0]["x"]
    hisY = body["enemies"][0]["y"]
    myX = body["you"]["x"]
    myY = body["you"]["y"]
    if myX == hisX:
        for i in body["walls"]:
            if i["y"] < min(hisY,myY) and i["y"] > max(hisY,myY):
                return i["strength"]
    if myY == hisY:
        for i in body["walls"]:
            if i["x"] < min(hisX,myX) and i["x"] > max(hisX,myX):
                return i["strength"]
    return 0

def moveAway(body):
    return RETREAT

def isEnemyVisible(body):
    if "x" not in body["enemies"][0]:
        return False
    else:
        return True

def getRelativePosition(you, enemy):
    if you["direction"] == "top":
        return enemy["x"] - you["x"], you["y"] - enemy["y"]
    if you["direction"] == "bottom":
        return you["x"] - enemy["x"], enemy["y"]-you["y"]
    if you["direction"] == "right":
        return enemy["y"] - you["y"], enemy["x"]-you["x"]
    if you["direction"] == "left":
        return you["y"] - enemy["y"], you["y"]-enemy["y"]

def ableToAttack(you, enemy):
    x, y = getRelativePosition(you, enemy)
    if y >= 0 and y - you["weaponRange"] and x == 0:
        return True

    return False

def turnsToAttack(body, you, enemy):
    x, y = getRelativePosition(you, enemy)
    min_axis = min(abs(x), abs(y))
    max_axis = max(abs(x), abs(y))
    if y > 0:

        if x > 0:
            return min_axis + 1 + min(0, (max_axis-you["weaponRange"])), moveTowardsPoint(body, enemy["x"], enemy["y"])
        elif x < 0:
            return min_axis + 1 + min(0, (max_axis-you["weaponRange"])), moveTowardsPoint(body, enemy["x"], enemy["y"])
        else:
            if ableToAttack(you, enemy):
                return min_axis + min(0, (max_axis-you["weaponRange"])), SHOOT
            else:
                return min_axis + min(0, (max_axis-you["weaponRange"])), moveTowardsPoint(body, enemy["x"], enemy["y"])
    elif y < 0:
        if x > 0:
            return min_axis + 1 + min(0, (max_axis-you["weaponRange"])), moveTowardsPoint(body, enemy["x"], enemy["y"])
        elif x < 0:
            return min_axis + 1 + min(0, (max_axis-you["weaponRange"])), moveTowardsPoint(body, enemy["x"], enemy["y"])
        else:
            if ableToAttack(you, enemy):
                return min_axis + min(0, (max_axis-you["weaponRange"])), SHOOT
            else:
                return min_axis + min(0, (max_axis-you["weaponRange"])), moveTowardsPoint(body, enemy["x"], enemy["y"])
    else:
        if x > 0:
            return min(0, (max_axis-you["weaponRange"])) + 1, moveTowardsPoint(body, enemy["x"], enemy["y"])
        elif x < 0:
            return min(0, (max_axis-you["weaponRange"])) + 1, moveTowardsPoint(body, enemy["x"], enemy["y"])

    return 11000, PASS

def shouldAttack(body, you, enemy):
    youTurnsToAttack, action = turnsToAttack(body, you, enemy)
    youTurnsToAttack = max(0, youTurnsToAttack)
    enemyTurnsToAttack, th = turnsToAttack(body, enemy, you)
    enemyTurnsToAttack = max(0, enemyTurnsToAttack)
    if (you["strength"] - enemy["weaponDamage"] * min(0, (enemyTurnsToAttack-youTurnsToAttack)))/enemy["weaponDamage"] >= (enemy["strength"] - you["weaponDamage"] * min(0, (youTurnsToAttack-enemyTurnsToAttack)))/you["weaponDamage"]:
        return True, action
    else:
        return False, RETREAT

def getBonuesDistance(body, type):
    result = []
    if not len(body["bonusTiles"]):
        return False
    for bonus in body["bonusTiles"]:
        if bonus["type"] == type:
            result.append([bonus["x"], bonus["y"]])

    return sorted(result, key=sum)


def goToBonus(body):
    bonus_locations = 0
    if body["you"]["strength"] < 300:
        bonus_locations = getBonuesDistance(body, "strength")
    if not bonus_locations:
        bonus_locations = getBonuesDistance(body, "weapon-range")
    if not bonus_locations:
        bonus_locations = getBonuesDistance(body, "weapon-power")
    if not bonus_locations:
        return moveTowardsCenterOfMap(body)
    else:
        return moveTowardsPoint(body, bonus_locations[0][0], bonus_locations[0][1])

def enemyInLine(body):
    if body["enemies"][0]["x"] == body["you"]["x"]:
        return "horisontal"
    elif body["enemies"][0]["y"] == body["you"]["y"]:
        return "vertical"
    elif body["enemies"][0]["x"] == body["you"]["x"]+1:
        return "hori right"
    elif body["enemies"][0]["x"] == body["you"]["x"]-1:
        return "hori left"
    elif body["enemies"][0]["y"] == body["you"]["y"] +1:
        return "vert bottom"
    elif body["enemies"][0]["y"] == body["you"]["y"] +1:
        return "vert top"
    return "none"

def chooseAction(body):
    action = moveTowardsCenterOfMap(body)
    if visibleEnemy(body):
        line = enemyInLine(body)
        if line == "vertical":
            vert = lineVertical(body)
            if vert == "he sees":
                if wallbetween(body) > 0:
                    if wallbetween(body) < body["you"]["strength"]:
                        action = PASS
                    else:
                        action = rotateToEnemy(body)
                else:
                    action = RETREAT
            elif vert == "both see":
                if body["enemies"][0]["strength"]/body["you"]["weaponDamage"] > body["you"]["strength"]/body["enemies"][0]["weaponDamage"]:
                    action = RETREAT
                else:
                    action = SHOOT
            elif vert == "you see":
                action = SHOOT
            else:
                action = rotateToEnemy(body)
        elif line == "horisontal":
            hori = lineHorisontal(body)
            if hori == "he sees":
                if wallbetween(body):
                    if wallbetween(body) < body["you"]["strength"]:
                        action = PASS
                    else:
                        action = rotateToEnemy(body)
                else:
                    action = RETREAT
            elif hori == "both see":
                if body["enemies"][0]["strength"]/body["you"]["weaponDamage"] > body["you"]["strength"]/body["enemies"][0]["weaponDamage"]:
                    action = RETREAT
                else:
                    action = SHOOT
            elif hori == "you see":
                action = SHOOT
            else:
                action = rotateToEnemy(body)
        elif line=="hori right" or line=="hori left":
            if body["you"]["direction"] == "right" and body["enemies"][0]["y"] > body["you"]["y"]:
                action = ROTATE_RIGHT
            elif body["you"]["direction"] == "bottom" and body["enemies"][0]["y"] > body["you"]["y"]:
                action = PASS
            elif body["you"]["direction"] == "top" and body["enemies"][0]["y"] > body["you"]["y"]:
                action = ROTATE_RIGHT
            elif body["you"]["direction"] == "left" and body["enemies"][0]["y"] > body["you"]["y"]:
                action = ROTATE_LEFT
            elif body["you"]["direction"] == "bottom" and body["enemies"][0]["y"] < body["you"]["y"]:
                action = ROTATE_LEFT
            elif body["you"]["direction"] == "right" and body["enemies"][0]["y"] < body["you"]["y"]:
                action = ROTATE_LEFT
            elif body["you"]["direction"] == "top" and body["enemies"][0]["y"] < body["you"]["y"]:
                action = PASS
            elif body["you"]["direction"] == "left" and body["enemies"][0]["y"] < body["you"]["y"]:
                action = ROTATE_RIHT
        elif line=="vert bottom" or line=="vert top":
            if body["you"]["direction"] == "right" and body["enemies"][0]["x"] > body["you"]["x"]:
                action = PASS
            elif body["you"]["direction"] == "bottom" and body["enemies"][0]["x"] > body["you"]["x"]:
                action = ROTATE_LEFT
            elif body["you"]["direction"] == "top" and body["enemies"][0]["x"] > body["you"]["x"]:
                action = ROTATE_RIGHT
            elif body["you"]["direction"] == "left" and body["enemies"][0]["x"] > body["you"]["x"]:
                action = ROTATE_LEFT
            elif body["you"]["direction"] == "bottom" and body["enemies"][0]["x"] < body["you"]["x"]:
                action = ROTATE_RIGHT
            elif body["you"]["direction"] == "right" and body["enemies"][0]["x"] < body["you"]["x"]:
                action = ROTATE_LEFT
            elif body["you"]["direction"] == "top" and body["enemies"][0]["x"] < body["you"]["x"]:
                action = ROTATE_LEFT
            elif body["you"]["direction"] == "left" and body["enemies"][0]["x"] < body["you"]["x"]:
        else:
            action = PASS
    else:
        action = goToBonus(body)
    return action

env = os.environ
req_params_query = env['REQ_PARAMS_QUERY']
responseBody = open(env['res'], 'w')

response = {}
returnObject = {}
if req_params_query == "info":
    returnObject["name"] = "Nils Olav"
    returnObject["team"] = "Det norske forsvaret"
elif req_params_query == "command":
    body = json.loads(open(env["req"], "r").read())
    returnObject["command"] = chooseAction(body)

response["body"] = returnObject
responseBody.write(json.dumps(response))
responseBody.close()
