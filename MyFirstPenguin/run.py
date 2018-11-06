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

def enemyInLine(body):
    if body["enemies"][0]["x"] == body["you"]["x"]:
        return "horisontal"
    elif body["enemies"][0]["y"] == body["you"]["y"]:
        return "vertical"
    return "none"

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


def chooseAction(body):
    action = moveTowardsCenterOfMap(body)
    if visibleEnemy(body):
        mygain = 0
        line = enemyInLine(body)
        if line == "vertical":
            vert = lineVertical(body)
            if vert == "he sees":
                mygain = -1
            elif vert == "you see":
                mygain = 1
        elif line == "horisontal":
            hori = lineHorisontal(body)
            if hori == "he sees":
                mygain = -1
            elif hori == "you see":
                mygain = 1
        if body["enemies"][0]["strength"]/body["you"]["weaponDamage"] -mygain < body["you"]["strength"]/body["enemies"][0]["weaponDamage"]:
            action = SHOOT
        elif body["enemies"][0]["strength"]/body["you"]["weaponDamage"] -mygain == body["you"]["strength"]/body["enemies"][0]["weaponDamage"]:
            if mygain == 1:
                action = SHOOT
            else:
                #Let etter stuff
                #gå rundt
                action = moveTowardsCenterOfMap(body)
        else: # gå rundt
            action = moveTowardsCenterOfMap(body)
    else:
        if body["enemies"][0]["strength"] <= body["you"]["strength"]: # let etter motstander
            action = moveTowardsCenterOfMap(body)
        else: #let etter powerups og god posisjon
            action = moveTowardsCenterOfMap(body)
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
