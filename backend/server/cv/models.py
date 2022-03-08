from django.db import models


class Module():
    def __init__(self, modNumber, parkingLotName, numSpotsFilled, numTotalSpots):
        self.id = modNumber
        self.parkingLot = parkingLotName
        self.ledColour = 0
        self.numSpotsFull = numSpotsFilled
        self.totalSpots = numTotalSpots
        # self.spots
    
    def updateLedColour(self, colour):
        self.ledColour = colour
    
    def updateSpotsOccupied(self, numOccupied):
        self.numSpotsFull = numOccupied
    
    def getTotalSpots(self):
        return self.totalSpots

class Spot():
    def __init__(self, box, spotNum):
        self.botLeftCoord = box[0]
        self.topLeftCoord = box[1]
        self.topRightCoord = box[2]
        self.botRightCoord = box[3]

        # self.y1 = box[0]
        # self.x1 = box[1]
        # self.y2 = box[2]
        # self.x2 = box[3]
        self.spotNum = spotNum
        self.occupied = False

    # Depreciated Nov 21, 2021 - CL
    def getBBox(self):
        return [self.y1, self.x1, self.y2, self.x2]

    def getID(self):
        return self.spotNum

    def updateOccupied(self, status):
        self.occupied = status

    def isOccupied(self):
        return self.occupied

    def getPolygonSpot(self):
        return [
            self.botLeftCoord,
            self.topLeftCoord,
            self.topRightCoord,
            self.botRightCoord,
            self.botLeftCoord
        ]

